from __future__ import annotations

import copy
from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest

from eas_validator.adapters import NeutralJSONLAdapter
from eas_validator.native_observation import (
    build_native_observation_projection,
    main,
)
from eas_validator.observation import build_incomplete_observation
from eas_validator.schema import validate_instance


ROOT = Path(__file__).resolve().parents[1]
SCENARIO = ROOT / "compliance" / "scenarios" / "SCN-001-focused-edit.json"
PROJECTION_SCHEMA = (
    ROOT / "schemas" / "eas-native-observation-assessment.schema.json"
)


def observer_events(*, final_revision: str = "tree-after", evidence: bool = True) -> list[dict]:
    events = [
        {
            "trace_schema_version": "0.1.0",
            "event_id": "observer-start",
            "type": "trace_start",
            "source": {"name": "controlled harness"},
            "payload": {
                "run_id": "native-run-001",
                "task": {"description": "Correct one identified typo."},
                "initial_state": {
                    "summary": "Known typo present.",
                    "revision": "tree-before",
                },
                "implementation": {"name": "runtime", "version": "1"},
                "environment": {"name": "fixture", "revision": "tree-before"},
            },
        },
        {
            "trace_schema_version": "0.1.0",
            "event_id": "native-000001",
            "type": "x-runtime.event",
            "source": {"name": "runtime-jsonl/1"},
            "payload": {"native_event": {"message": "unchanged native event"}},
        },
        {
            "trace_schema_version": "0.1.0",
            "event_id": "observer-final",
            "type": "project_state",
            "source": {"name": "workspace digest"},
            "payload": {
                "phase": "final",
                "state": {
                    "summary": "Observed final tree.",
                    "revision": final_revision,
                },
            },
        },
    ]
    if evidence:
        events.append(
            {
                "trace_schema_version": "0.1.0",
                "event_id": "observer-inspection",
                "type": "evidence",
                "source": {"name": "fixture checker"},
                "payload": {
                    "evidence": {
                        "id": "inspection-result",
                        "kind": "inspection",
                        "description": "Only the intended word changed.",
                        "result": "passed",
                        "source": "fixture checker",
                        "origin": "assessor",
                        "capture": "direct",
                    }
                },
            }
        )
    return events


def incomplete_observation(**kwargs) -> dict:
    events = observer_events(**kwargs)
    adapter = NeutralJSONLAdapter()
    adapter.ingest(events)
    observation = build_incomplete_observation(
        observation_id="native-observation-001",
        record_created_at="2026-07-25T22:00:00Z",
        source_format="runtime-jsonl/1",
        source_events=events,
        adapter=adapter,
    )
    observation["extensions"] = {
        "org.eas.observer-overlay": {
            "native_event_count": 1,
            "observer_event_count": len(events) - 1,
            "native_extension_type": "x-runtime.event",
        }
    }
    return observation


def projection(observation: dict) -> dict:
    scenario = json.loads(SCENARIO.read_text(encoding="utf-8"))
    return build_native_observation_projection(
        observation=observation,
        observation_sha256="a" * 64,
        scenario=scenario,
        scenario_sha256="b" * 64,
        projection_id="projection-001",
        created_at="2026-07-25T22:01:00Z",
    )


class NativeObservationProjectionTests(unittest.TestCase):
    def test_external_projection_passes_without_claiming_conformance(self) -> None:
        result = projection(incomplete_observation())
        schema = json.loads(PROJECTION_SCHEMA.read_text(encoding="utf-8"))

        self.assertEqual(validate_instance(result, schema), [])
        self.assertEqual(result["schema_result"], "pass")
        self.assertEqual(result["observable_scenario_result"], "pass")
        self.assertEqual(result["agent_decision_properties"], "indeterminate")
        self.assertEqual(result["assessment_subject"]["type"], "observation")
        self.assertFalse(result["conformance_claim"])
        self.assertEqual(
            {item["name"] for item in result["dimensions"]},
            {"project_state_change", "evidence_results", "evidence_kinds"},
        )
        rendered = json.dumps(result)
        self.assertNotIn('"outcome"', rendered)
        self.assertNotIn('"task_result"', rendered)

    def test_observed_state_contradiction_is_a_failure(self) -> None:
        result = projection(incomplete_observation(final_revision="tree-before"))

        self.assertEqual(result["observable_scenario_result"], "fail")
        state = next(
            item
            for item in result["dimensions"]
            if item["name"] == "project_state_change"
        )
        self.assertEqual(state["result"], "fail")
        self.assertEqual(state["observed"], "unchanged")

    def test_missing_external_evidence_is_indeterminate_not_failure(self) -> None:
        result = projection(incomplete_observation(evidence=False))

        self.assertEqual(result["observable_scenario_result"], "indeterminate")
        evidence = [
            item
            for item in result["dimensions"]
            if item["name"].startswith("evidence_")
        ]
        self.assertTrue(all(item["result"] == "indeterminate" for item in evidence))

    def test_native_extension_payload_cannot_supply_observer_evidence(self) -> None:
        observation = incomplete_observation(evidence=False)
        native = copy.deepcopy(observation["events"][1]["content"])
        native["payload"]["native_event"] = {
            "type": "evidence",
            "evidence": {"kind": "inspection", "result": "passed"},
        }
        observation["events"][1]["content"] = native

        result = projection(observation)

        self.assertEqual(result["observable_scenario_result"], "indeterminate")

    def test_unmarked_events_cannot_supply_observer_facts(self) -> None:
        observation = incomplete_observation()
        del observation["extensions"]

        result = projection(observation)

        self.assertEqual(result["observable_scenario_result"], "indeterminate")
        self.assertTrue(
            all(item["source_event_ids"] == [] for item in result["dimensions"])
        )

    def test_cli_writes_digest_bound_projection(self) -> None:
        observation = incomplete_observation()
        with tempfile.TemporaryDirectory() as directory:
            observation_path = Path(directory) / "observation.json"
            output_path = Path(directory) / "projection.json"
            observation_path.write_text(
                json.dumps(observation) + "\n", encoding="utf-8"
            )
            output = StringIO()
            with redirect_stdout(output):
                status = main(
                    [
                        str(observation_path),
                        "--scenario",
                        str(SCENARIO),
                        "--projection-id",
                        "cli-projection-001",
                        "--created-at",
                        "2026-07-25T22:01:00Z",
                        "--output",
                        str(output_path),
                    ]
                )
            result = json.loads(output_path.read_text(encoding="utf-8"))

        self.assertEqual(status, 0)
        self.assertEqual(result["observable_scenario_result"], "pass")
        lines = output.getvalue().splitlines()
        self.assertEqual(
            lines[:2],
            [
                "This assessment concerns an external observation.",
                "It is not a full EAS run-conformance assessment.",
            ],
        )
        self.assertIn("EAS conformance: NOT ASSESSED", output.getvalue())


if __name__ == "__main__":
    unittest.main()
