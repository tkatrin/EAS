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


if __name__ == "__main__":
    unittest.main()
