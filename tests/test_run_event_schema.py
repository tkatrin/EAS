from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from eas_validator.schema import validate_instance


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "eas-run-event.schema.json"


PAYLOADS = {
    "run_started": {
        "implementation": {"name": "instrumented-agent", "version": "1.0"},
        "environment": {"name": "isolated fixture", "revision": "tree-before"},
        "started_at": "2026-07-26T00:00:00Z",
        "initial_state": {"summary": "Initial fixture.", "revision": "tree-before"},
        "constraints": ["Do not change unrelated files."],
    },
    "task_model_recorded": {
        "task": {
            "description": "Correct one typo.",
            "primary_class": "change",
        }
    },
    "state_entered": {"state": "RECEIVED"},
    "decision_recorded": {
        "decision": {
            "id": "decision-1",
            "disposition": "proceed",
        }
    },
    "action_recorded": {
        "action": {
            "id": "action-1",
            "description": "Correct the identified typo.",
        }
    },
    "evidence_recorded": {
        "evidence": {
            "id": "evidence-1",
            "result": "passed",
        }
    },
    "report_finalized": {
        "task_result": "satisfied",
        "report": {
            "summary": "The typo was corrected.",
        },
    },
    "run_finished": {
        "completed_at": "2026-07-26T00:01:00Z",
        "final_state": {"summary": "Corrected fixture.", "revision": "tree-after"},
        "outcome": "completed",
    },
}


def event(event_type: str) -> dict:
    return {
        "event_schema_version": "0.1.0",
        "event_id": f"event-{event_type}",
        "event_type": event_type,
        "run_id": "instrumented-run-001",
        "recorded_at": "2026-07-26T00:00:30Z",
        "source": {
            "kind": "agent",
            "name": "instrumented-agent",
            "version": "1.0",
        },
        "payload": copy.deepcopy(PAYLOADS[event_type]),
        "native_event_refs": [],
        "observer_evidence_refs": [],
    }


class RunEventSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    def test_all_eight_event_types_are_schema_valid(self) -> None:
        self.assertEqual(set(PAYLOADS), {
            "run_started",
            "task_model_recorded",
            "state_entered",
            "decision_recorded",
            "action_recorded",
            "evidence_recorded",
            "report_finalized",
            "run_finished",
        })
        for event_type in PAYLOADS:
            with self.subTest(event_type=event_type):
                self.assertEqual(
                    validate_instance(event(event_type), self.schema),
                    [],
                )

    def test_payload_shape_is_selected_by_event_type(self) -> None:
        changed = event("report_finalized")
        changed["payload"] = {"outcome": "completed"}

        issues = validate_instance(changed, self.schema)

        self.assertTrue(
            any(issue.path == "$.payload.task_result" for issue in issues)
        )
        self.assertTrue(any(issue.path == "$.payload.report" for issue in issues))
        self.assertTrue(any(issue.path == "$.payload.outcome" for issue in issues))

    def test_source_references_and_recording_time_are_required(self) -> None:
        changed = event("state_entered")
        del changed["native_event_refs"]
        changed["recorded_at"] = "yesterday"
        changed["source"]["kind"] = "observer"

        issues = validate_instance(changed, self.schema)

        self.assertTrue(
            any(issue.path == "$.native_event_refs" for issue in issues)
        )
        self.assertTrue(any(issue.path == "$.recorded_at" for issue in issues))
        self.assertTrue(any(issue.path == "$.source.kind" for issue in issues))

    def test_event_cannot_claim_a_backdated_observation_field(self) -> None:
        changed = event("decision_recorded")
        changed["observed_at"] = "2026-07-25T23:59:00Z"

        issues = validate_instance(changed, self.schema)

        self.assertTrue(any(issue.path == "$.observed_at" for issue in issues))


if __name__ == "__main__":
    unittest.main()
