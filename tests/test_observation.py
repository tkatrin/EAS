from __future__ import annotations

import copy
from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest

from eas_validator.adapters import NeutralJSONLAdapter
from eas_validator.observation import (
    build_incomplete_observation,
    main,
    validate_incomplete_observation,
)
from eas_validator.schema import validate_instance


ROOT = Path(__file__).resolve().parents[1]
TRACE = ROOT / "examples" / "traces" / "neutral-incomplete.jsonl"
SCHEMA = ROOT / "schemas" / "eas-incomplete-observation.schema.json"
TRACE_SCHEMA = ROOT / "schemas" / "eas-neutral-trace-event-0.1.0.schema.json"


def load_events() -> list[dict]:
    with TRACE.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def build_example() -> dict:
    events = load_events()
    adapter = NeutralJSONLAdapter()
    adapter.ingest(events)
    return build_incomplete_observation(
        observation_id="observation-incomplete-example-001",
        record_created_at="2026-07-25T20:00:00Z",
        source_format="eas-neutral-jsonl/0.1.0",
        source_events=events,
        adapter=adapter,
    )


class IncompleteObservationTests(unittest.TestCase):
    def test_incomplete_observation_is_valid_and_indeterminate(self) -> None:
        observation = build_example()
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        trace_schema = json.loads(TRACE_SCHEMA.read_text(encoding="utf-8"))

        self.assertEqual(validate_instance(observation, schema), [])
        self.assertEqual(validate_incomplete_observation(observation), [])
        for event in load_events():
            self.assertEqual(validate_instance(event, trace_schema), [])
        self.assertEqual(observation["result"], "indeterminate")
        self.assertEqual(len(observation["events"]), len(load_events()))
        self.assertEqual(
            [item["content"] for item in observation["events"]],
            load_events(),
        )
        self.assertTrue(observation["missing_fields"])
        self.assertNotIn("partial_run_record", observation)
        self.assertNotIn("outcome", observation)

    def test_builder_refuses_a_complete_mapping(self) -> None:
        complete = ROOT / "examples" / "traces" / "neutral-complete.jsonl"
        adapter = NeutralJSONLAdapter()
        adapter.ingest(complete)

        with self.assertRaisesRegex(ValueError, "no missing target fields"):
            build_incomplete_observation(
                observation_id="not-incomplete",
                record_created_at="2026-07-25T20:00:00Z",
                source_format="eas-neutral-jsonl/0.1.0",
                source_events=[],
                adapter=adapter,
            )

    def test_cross_references_and_duplicates_are_checked(self) -> None:
        observation = build_example()
        changed = copy.deepcopy(observation)
        changed["events"][1]["index"] = 0
        changed["missing_fields"][0]["source_event_ids"] = ["unknown-event"]

        messages = [str(issue) for issue in validate_incomplete_observation(changed)]

        self.assertTrue(any("indexes must be unique" in item for item in messages))
        self.assertTrue(any("unknown source event identifier" in item for item in messages))

    def test_cli_writes_indeterminate_observation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "observation.json"
            output = StringIO()
            with redirect_stdout(output):
                result = main(
                    [
                        str(TRACE),
                        "--observation-id",
                        "cli-observation-001",
                        "--record-created-at",
                        "2026-07-25T20:00:00Z",
                        "--output",
                        str(output_path),
                    ]
                )
            observation = json.loads(output_path.read_text(encoding="utf-8"))

        self.assertEqual(result, 1)
        self.assertEqual(observation["result"], "indeterminate")
        self.assertIn("Result: INDETERMINATE", output.getvalue())

    def test_observer_overlay_reduces_missing_fields_without_inventing_agent_output(
        self,
    ) -> None:
        native_lines = [
            '{"type":"session.started","session_id":"native-1"}',
            "native banner",
        ]
        observer_events = [
            {
                "trace_schema_version": "0.1.0",
                "event_id": "observer-start",
                "type": "trace_start",
                "source": {"name": "controlled collection harness"},
                "payload": {
                    "run_id": "overlay-run-001",
                    "started_at": "2026-07-25T20:00:00Z",
                    "completed_at": "2026-07-25T20:01:00Z",
                    "record_created_at": "2026-07-25T20:02:00Z",
                    "task": {
                        "description": "Correct one identified typo.",
                        "primary_class": "change",
                        "secondary_classes": [],
                        "candidate_classes": ["change"],
                        "classification_basis": "The locked scenario requires one edit.",
                        "acceptance_criteria": ["Only the identified word changes."],
                    },
                    "initial_state": {
                        "summary": "The target typo is present.",
                        "revision": "tree-before",
                    },
                    "constraints": ["Change only the identified word."],
                    "implementation": {
                        "name": "independent-runtime",
                        "version": "1.0",
                    },
                    "environment": {
                        "name": "isolated workspace",
                        "revision": "tree-before",
                    },
                },
            },
            {
                "trace_schema_version": "0.1.0",
                "event_id": "observer-final-state",
                "type": "project_state",
                "source": {"name": "workspace tree digest"},
                "payload": {
                    "phase": "final",
                    "state": {
                        "summary": "The observed workspace after the run.",
                        "revision": "tree-after",
                    },
                },
            },
        ]

        with tempfile.TemporaryDirectory() as directory:
            native_path = Path(directory) / "native.jsonl"
            native_path.write_text("\n".join(native_lines) + "\n", encoding="utf-8")
            observer_path = Path(directory) / "observer.jsonl"
            observer_path.write_text(
                "\n".join(json.dumps(item) for item in observer_events) + "\n",
                encoding="utf-8",
            )
            output_path = Path(directory) / "observation.json"
            with redirect_stdout(StringIO()):
                result = main(
                    [
                        str(native_path),
                        "--observation-id",
                        "overlay-observation-001",
                        "--record-created-at",
                        "2026-07-25T20:02:00Z",
                        "--source-format",
                        "independent-runtime-jsonl/1.0",
                        "--native-extension-type",
                        "x-independent.runtime-event",
                        "--observer-events",
                        str(observer_path),
                        "--output",
                        str(output_path),
                    ]
                )
            observation = json.loads(output_path.read_text(encoding="utf-8"))

        missing_paths = {item["path"] for item in observation["missing_fields"]}
        self.assertEqual(result, 1)
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(validate_instance(observation, schema), [])
        self.assertEqual(validate_incomplete_observation(observation), [])
        self.assertEqual(
            observation["extensions"]["org.eas.observer-overlay"],
            {
                "native_event_count": 2,
                "observer_event_count": 2,
                "native_extension_type": "x-independent.runtime-event",
            },
        )
        self.assertEqual(len(observation["events"]), 4)
        self.assertEqual(
            observation["events"][1]["content"]["payload"]["native_event"],
            {"type": "session.started", "session_id": "native-1"},
        )
        self.assertEqual(
            observation["events"][2]["content"]["payload"]["native_event"],
            "native banner",
        )
        self.assertNotIn("$.run_id", missing_paths)
        self.assertNotIn("$.task", missing_paths)
        self.assertNotIn("$.environment", missing_paths)
        self.assertNotIn("$.final_state", missing_paths)
        self.assertNotIn("$.implementation.name", missing_paths)
        self.assertIn("$.outcome", missing_paths)
        self.assertIn("$.task_result", missing_paths)
        self.assertIn("$.report", missing_paths)
        self.assertIn("$.decisions", missing_paths)

    def test_observer_overlay_rejects_agent_decisions(self) -> None:
        decision = {
            "trace_schema_version": "0.1.0",
            "event_id": "observer-decision",
            "type": "decision",
            "source": {"name": "collection harness"},
            "payload": {
                "decision": {
                    "id": "invented",
                    "question": "Proceed?",
                    "options": ["yes"],
                    "choice": "yes",
                    "disposition": "proceed",
                    "basis": "Not observable.",
                    "risk": "low",
                    "reversibility": {"level": "none", "limitations": []},
                    "authority": "authorized",
                    "evidence_refs": [],
                }
            },
        }
        with tempfile.TemporaryDirectory() as directory:
            native_path = Path(directory) / "native.jsonl"
            native_path.write_text('{"type":"session.started"}\n', encoding="utf-8")
            observer_path = Path(directory) / "observer.jsonl"
            observer_path.write_text(json.dumps(decision) + "\n", encoding="utf-8")
            output_path = Path(directory) / "observation.json"
            output = StringIO()
            with redirect_stdout(output):
                result = main(
                    [
                        str(native_path),
                        "--observation-id",
                        "invalid-overlay",
                        "--native-extension-type",
                        "x-independent.runtime-event",
                        "--observer-events",
                        str(observer_path),
                        "--output",
                        str(output_path),
                    ]
                )

        self.assertEqual(result, 2)
        self.assertIn("not an externally observable overlay type", output.getvalue())
        self.assertFalse(output_path.exists())


if __name__ == "__main__":
    unittest.main()
