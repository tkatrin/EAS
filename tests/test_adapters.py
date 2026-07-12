from __future__ import annotations

import json
import unittest
from pathlib import Path

from eas_validator import validate_record
from eas_validator.adapters import (
    AdapterContext,
    EASAdapter,
    NeutralJSONLAdapter,
    ScriptedEventAdapter,
)
from eas_validator.schema import validate_instance


ROOT = Path(__file__).resolve().parents[1]
NEUTRAL_EXAMPLE = ROOT / "examples" / "traces" / "neutral-complete.jsonl"
SCRIPTED_EXAMPLE = ROOT / "examples" / "traces" / "scripted-complete.json"
TRACE_SCHEMA = ROOT / "schemas" / "eas-neutral-trace-event-0.1.0.schema.json"


def event(event_id: str, event_type: str, payload: dict) -> dict:
    return {
        "trace_schema_version": "0.1.0",
        "event_id": event_id,
        "type": event_type,
        "payload": payload,
    }


class NeutralJSONLAdapterTests(unittest.TestCase):
    def test_adapter_implements_protocol(self) -> None:
        self.assertIsInstance(NeutralJSONLAdapter(), EASAdapter)
        self.assertIsInstance(ScriptedEventAdapter(), EASAdapter)

    def test_versioned_schema_and_example_are_json_objects(self) -> None:
        with TRACE_SCHEMA.open(encoding="utf-8") as handle:
            schema = json.load(handle)

        self.assertTrue(schema["$id"].endswith("eas-neutral-trace-event-0.1.0.schema.json"))
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(schema["properties"]["trace_schema_version"]["const"], "0.1.0")

        with NEUTRAL_EXAMPLE.open(encoding="utf-8") as handle:
            lines = [json.loads(line) for line in handle if line.strip()]
        self.assertGreater(len(lines), 1)
        self.assertTrue(all(item["trace_schema_version"] == "0.1.0" for item in lines))
        self.assertEqual(len({item["event_id"] for item in lines}), len(lines))
        for item in lines:
            self.assertEqual(validate_instance(item, schema), [])

        invalid = dict(lines[0])
        invalid["trace_schema_version"] = "9.9.9"
        self.assertTrue(validate_instance(invalid, schema))

    def test_complete_example_maps_explicit_content(self) -> None:
        adapter = NeutralJSONLAdapter()
        adapter.ingest(NEUTRAL_EXAMPLE)

        record = adapter.build_run_record()

        self.assertEqual(record["schema_version"], "0.1.0")
        self.assertEqual(record["implementation"]["adapter"], "neutral-jsonl")
        self.assertEqual(record["implementation"]["name"], "example-neutral-agent")
        self.assertEqual(record["run_id"], "neutral-example-001")
        self.assertEqual(record["task_result"], "satisfied")
        self.assertEqual(len(record["decisions"]), 1)
        self.assertEqual(record["decisions"][0]["id"], "decision-1")
        self.assertEqual(len(record["actions"]), 2)
        evidence_by_id = {item["id"]: item for item in record["evidence"]}
        self.assertEqual(evidence_by_id["evidence-tests"]["result"], "passed")
        self.assertEqual(record["report"]["verification"][0]["status"], "passed")
        self.assertNotIn("_source_event_id", record["actions"][0])
        self.assertEqual(adapter.get_indeterminate_fields(), ())

        unmapped = adapter.get_unmapped_events()
        self.assertTrue(any(item.partially_mapped for item in unmapped))
        self.assertTrue(any(item.event_id == "evt-018" for item in unmapped))
        self.assertEqual(
            [item.statement for item in adapter.get_assumptions()],
            ["Repository instructions are authoritative."],
        )
        with (ROOT / "schemas" / "eas-run.schema.json").open(encoding="utf-8") as handle:
            run_schema = json.load(handle)
        self.assertEqual(validate_instance(record, run_schema), [])
        self.assertEqual(validate_record(record), [])

    def test_transport_success_is_not_promoted_to_passed_evidence(self) -> None:
        adapter = NeutralJSONLAdapter()
        adapter.ingest(
            [
                event(
                    "call-event",
                    "tool_call",
                    {"call_id": "call-1", "tool": "shell", "operation": "run"},
                ),
                event(
                    "result-event",
                    "tool_result",
                    {"call_id": "call-1", "status": "success"},
                ),
            ]
        )

        record = adapter.build_run_record()

        self.assertEqual(record["evidence"][0]["result"], "observed")
        self.assertNotIn("recorded_at", record["evidence"][0])
        self.assertEqual(record["decisions"], [])
        self.assertIn(
            "$.evidence[0].recorded_at",
            {item.path for item in adapter.get_indeterminate_fields()},
        )
        self.assertIn(
            "$.evidence[0].observed_at",
            {item.path for item in adapter.get_indeterminate_fields()},
        )

    def test_action_does_not_fabricate_decision_or_authority(self) -> None:
        adapter = NeutralJSONLAdapter()
        adapter.ingest(
            [event("edit-1", "file_change", {"path": "a.txt", "change": "modified"})]
        )

        record = adapter.build_run_record()
        indeterminate_paths = {item.path for item in adapter.get_indeterminate_fields()}

        self.assertEqual(record["decisions"], [])
        self.assertNotIn("decision_id", record["actions"][0])
        self.assertNotIn("authority", record["actions"][0])
        self.assertEqual(
            record["actions"][0]["materiality"],
            {"changes_project_state": True},
        )
        self.assertIn("$.actions[0].decision_id", indeterminate_paths)
        self.assertIn("$.actions[0].authority", indeterminate_paths)
        self.assertIn(
            "$.actions[0].materiality.creates_external_effect",
            indeterminate_paths,
        )
        self.assertIn("$.decisions", indeterminate_paths)
        self.assertTrue(record["mapping"]["indeterminate_properties"])

    def test_incomplete_collection_remains_indeterminate_with_mapped_entries(self) -> None:
        adapter = NeutralJSONLAdapter()
        adapter.ingest(
            [
                event(
                    "explicit-decision",
                    "decision",
                    {"decision": {"id": "decision-1"}},
                )
            ]
        )

        paths = {item.path for item in adapter.get_indeterminate_fields()}

        self.assertEqual(len(adapter.build_run_record()["decisions"]), 1)
        self.assertIn("$.decisions", paths)
        self.assertIn("$.decisions[0].choice", paths)

    def test_extension_and_invalid_json_are_preserved_unmapped(self) -> None:
        extension = event("vendor-1", "x-acme.metric", {"score": 0.8})
        adapter = NeutralJSONLAdapter()
        adapter.ingest([json.dumps(extension), "{not-json"])

        unmapped = adapter.get_unmapped_events()

        self.assertEqual(unmapped[0].event, extension)
        self.assertEqual(unmapped[0].event_id, "vendor-1")
        self.assertEqual(unmapped[1].event, {"raw": "{not-json"})

    def test_duplicate_event_is_preserved_and_not_mapped_twice(self) -> None:
        state = event("same", "lifecycle_state", {"state": "RECEIVED"})
        adapter = NeutralJSONLAdapter()
        adapter.ingest([state, state])

        self.assertEqual(adapter.build_run_record()["state_history"], ["RECEIVED"])
        self.assertIn("duplicate event_id", adapter.get_unmapped_events()[0].reason)

    def test_explicit_context_assumptions_are_preserved(self) -> None:
        adapter = NeutralJSONLAdapter()
        adapter.ingest(
            [],
            AdapterContext(
                record_fields={"run_id": "context-run"},
                assumptions=("The supplied revision is stable.",),
            ),
        )

        self.assertEqual(
            adapter.build_run_record()["assumptions"],
            ["The supplied revision is stable."],
        )
        self.assertEqual(adapter.get_assumptions()[0].source, "context.assumptions")

    def test_ingest_resets_previous_state(self) -> None:
        adapter = NeutralJSONLAdapter()
        adapter.ingest([event("one", "assumption", {"statement": "First run."})])
        adapter.ingest([event("two", "assumption", {"statement": "Second run."})])

        self.assertEqual(adapter.build_run_record()["assumptions"], ["Second run."])


class ScriptedEventAdapterTests(unittest.TestCase):
    def test_scripted_example_maps_without_semantic_inference(self) -> None:
        with SCRIPTED_EXAMPLE.open(encoding="utf-8") as handle:
            script = json.load(handle)
        adapter = ScriptedEventAdapter()
        adapter.ingest(script)

        record = adapter.build_run_record()

        self.assertEqual(record["implementation"]["adapter"], "scripted-events")
        self.assertEqual(record["task"]["primary_class"], "review")
        self.assertEqual(record["actions"], [])
        self.assertEqual(record["decisions"], [])
        self.assertEqual(record["final_state"]["revision"], "rev-1")
        self.assertEqual(record["task_result"], "satisfied")
        self.assertEqual(adapter.get_indeterminate_fields(), ())
        self.assertEqual(adapter.get_unmapped_events(), ())
        with (ROOT / "schemas" / "eas-run.schema.json").open(encoding="utf-8") as handle:
            run_schema = json.load(handle)
        self.assertEqual(validate_instance(record, run_schema), [])
        self.assertEqual(validate_record(record), [])

    def test_unknown_script_operation_is_preserved(self) -> None:
        source = {"event_id": "custom-1", "op": "think", "value": "hidden"}
        adapter = ScriptedEventAdapter()
        adapter.ingest([source])

        self.assertEqual(adapter.build_run_record()["decisions"], [])
        self.assertEqual(adapter.get_unmapped_events()[0].event, source)

    def test_built_record_is_a_defensive_copy(self) -> None:
        adapter = ScriptedEventAdapter()
        adapter.ingest([{"op": "set", "field": "run_id", "value": "run-1"}])
        first = adapter.build_run_record()
        first["run_id"] = "mutated"

        self.assertEqual(adapter.build_run_record()["run_id"], "run-1")


if __name__ == "__main__":
    unittest.main()
