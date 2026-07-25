from __future__ import annotations

import copy
from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest

from eas_validator.__main__ import main
from eas_validator.instrumentation import (
    append_event,
    compile_events,
    read_event_stream,
    render_run,
)
from eas_validator.validator import validate_record


ROOT = Path(__file__).resolve().parents[1]
STREAM = ROOT / "examples" / "instrumentation" / "minimal-run-events.jsonl"


class InstrumentationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.event_schema = json.loads(
            (ROOT / "schemas" / "eas-run-event.schema.json").read_text(
                encoding="utf-8"
            )
        )
        cls.run_schema = json.loads(
            (ROOT / "schemas" / "eas-run.schema.json").read_text(encoding="utf-8")
        )
        cls.events, issues = read_event_stream(STREAM)
        if issues:
            raise AssertionError(issues)

    def compile(self, events: list[dict] | None = None):
        return compile_events(
            copy.deepcopy(events if events is not None else self.events),
            self.event_schema,
            self.run_schema,
        )

    def test_reference_stream_compiles_without_inventing_agent_fields(self) -> None:
        record, issues = self.compile()

        self.assertEqual(issues, [])
        self.assertIsNotNone(record)
        assert record is not None
        self.assertEqual(validate_record(record), [])
        self.assertEqual(record["run_id"], "instrumented-example-001")
        self.assertEqual(
            record["state_history"],
            [
                "RECEIVED",
                "UNDERSTANDING",
                "PLANNING",
                "EXECUTING",
                "VERIFYING",
                "REVIEWING",
                "REPORTING",
                "COMPLETED",
            ],
        )
        self.assertEqual(record["record_created_at"], "2026-07-26T01:01:10Z")
        provenance = record["extensions"]["org.eas.instrumentation-provenance"]
        self.assertEqual(provenance["/evidence/0"]["source_event_refs"], ["evt-010"])
        self.assertEqual(
            provenance["/evidence/0"]["native_event_refs"],
            ["native-tool-result-1"],
        )
        self.assertEqual(
            provenance["/evidence/0"]["observer_evidence_refs"],
            ["observer-state-1"],
        )

    def test_rendered_run_is_byte_deterministic(self) -> None:
        first, first_issues = self.compile()
        second, second_issues = self.compile()

        self.assertEqual(first_issues, [])
        self.assertEqual(second_issues, [])
        assert first is not None and second is not None
        self.assertEqual(render_run(first), render_run(second))

    def test_missing_singleton_emits_no_record(self) -> None:
        events = [
            event
            for event in copy.deepcopy(self.events)
            if event["event_type"] != "report_finalized"
        ]

        record, issues = self.compile(events)

        self.assertIsNone(record)
        self.assertTrue(
            any("report_finalized" in issue.message for issue in issues)
        )

    def test_schema_valid_but_incomplete_fragment_fails_run_compilation(self) -> None:
        events = copy.deepcopy(self.events)
        task_event = next(
            event for event in events if event["event_type"] == "task_model_recorded"
        )
        task_event["payload"]["task"] = {"description": "Incomplete task model."}

        record, issues = self.compile(events)

        self.assertIsNone(record)
        self.assertTrue(
            any(issue.path == "$.task.primary_class" for issue in issues)
        )

    def test_mixed_run_ids_duplicate_events_and_time_regression_fail(self) -> None:
        events = copy.deepcopy(self.events)
        events[3]["run_id"] = "other-run"
        events[4]["event_id"] = events[3]["event_id"]
        events[5]["recorded_at"] = "2026-07-26T01:00:01Z"

        record, issues = self.compile(events)
        rendered = "\n".join(str(issue) for issue in issues)

        self.assertIsNone(record)
        self.assertIn("exactly one run_id", rendered)
        self.assertIn("duplicate event id", rendered)
        self.assertIn("non-decreasing", rendered)

    def test_future_semantic_time_is_rejected(self) -> None:
        events = copy.deepcopy(self.events)
        events[-1]["payload"]["completed_at"] = "2026-07-26T01:02:00Z"

        record, issues = self.compile(events)

        self.assertIsNone(record)
        self.assertTrue(
            any("later than the event recording time" in issue.message for issue in issues)
        )

    def test_duplicate_entity_ids_are_global(self) -> None:
        events = copy.deepcopy(self.events)
        action = next(
            event for event in events if event["event_type"] == "action_recorded"
        )
        action["payload"]["action"]["id"] = "decision-1"

        record, issues = self.compile(events)

        self.assertIsNone(record)
        self.assertTrue(any("duplicate entity id" in issue.message for issue in issues))

    def test_unresolved_run_reference_fails_closed(self) -> None:
        events = copy.deepcopy(self.events)
        report = next(
            event for event in events if event["event_type"] == "report_finalized"
        )
        report["payload"]["report"]["verification"][0]["evidence_refs"] = [
            "missing-evidence"
        ]

        record, issues = self.compile(events)

        self.assertIsNone(record)
        self.assertTrue(any("unresolved evidence id" in issue.message for issue in issues))

    def test_nonmaterial_action_still_requires_a_resolved_decision(self) -> None:
        events = copy.deepcopy(self.events)
        action = next(
            event for event in events if event["event_type"] == "action_recorded"
        )
        action["payload"]["action"]["decision_id"] = "missing-decision"

        record, issues = self.compile(events)

        self.assertIsNone(record)
        self.assertTrue(any("unresolved decision id" in issue.message for issue in issues))

    def test_recorder_does_not_create_stream_for_invalid_event(self) -> None:
        invalid = copy.deepcopy(self.events[0])
        del invalid["source"]
        with tempfile.TemporaryDirectory() as directory:
            stream = Path(directory) / "events.jsonl"

            issues = append_event(stream, invalid, self.event_schema)

            self.assertTrue(issues)
            self.assertFalse(stream.exists())

    def test_recorder_appends_canonical_events(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            stream = Path(directory) / "events.jsonl"

            self.assertEqual(
                append_event(stream, self.events[0], self.event_schema),
                [],
            )
            self.assertEqual(
                append_event(stream, self.events[1], self.event_schema),
                [],
            )
            loaded, issues = read_event_stream(stream)

            self.assertEqual(issues, [])
            self.assertEqual(loaded, self.events[:2])
            self.assertTrue(stream.read_bytes().endswith(b"\n"))
            self.assertEqual(len(stream.read_text(encoding="utf-8").splitlines()), 2)

    def test_recorder_refuses_an_unterminated_existing_stream(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            stream = Path(directory) / "events.jsonl"
            stream.write_text('{"preserved":true}', encoding="utf-8")

            issues = append_event(stream, self.events[0], self.event_schema)

            self.assertTrue(
                any("does not end with a newline" in issue.message for issue in issues)
            )
            self.assertEqual(stream.read_text(encoding="utf-8"), '{"preserved":true}')

    def test_compile_cli_writes_a_structurally_valid_run(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "run.json"

            result = main(
                ["compile-run", str(STREAM), "--output", str(output)]
            )

            self.assertEqual(result, 0)
            record = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(validate_record(record), [])

    def test_compile_cli_preserves_existing_output_on_failure(self) -> None:
        events = [
            event
            for event in self.events
            if event["event_type"] != "run_finished"
        ]
        with tempfile.TemporaryDirectory() as directory:
            stream = Path(directory) / "incomplete.jsonl"
            output = Path(directory) / "run.json"
            stream.write_text(
                "".join(json.dumps(event) + "\n" for event in events),
                encoding="utf-8",
            )
            output.write_text("preserve me\n", encoding="utf-8")

            with redirect_stdout(StringIO()):
                result = main(
                    ["compile-run", str(stream), "--output", str(output)]
                )

            self.assertEqual(result, 1)
            self.assertEqual(output.read_text(encoding="utf-8"), "preserve me\n")

    def test_record_cli_appends_one_event(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            event_path = Path(directory) / "event.json"
            stream = Path(directory) / "events.jsonl"
            event_path.write_text(
                json.dumps(self.events[0]),
                encoding="utf-8",
            )

            with redirect_stdout(StringIO()):
                result = main(
                    ["record", str(event_path), "--stream", str(stream)]
                )
            loaded, issues = read_event_stream(stream)

            self.assertEqual(result, 0)
            self.assertEqual(issues, [])
            self.assertEqual(loaded, [self.events[0]])


if __name__ == "__main__":
    unittest.main()
