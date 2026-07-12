from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from eas_validator import validate_record


ROOT = Path(__file__).resolve().parents[1]


def example_record() -> dict:
    with (ROOT / "examples" / "minimal-run.json").open(encoding="utf-8") as handle:
        return json.load(handle)


class ValidatorTests(unittest.TestCase):
    def test_minimal_example_passes(self) -> None:
        self.assertEqual(validate_record(example_record()), [])

    def test_missing_required_field_fails(self) -> None:
        record = example_record()
        del record["report"]

        issues = validate_record(record)

        self.assertTrue(any(issue.path == "$.report" for issue in issues))

    def test_invalid_transition_fails(self) -> None:
        record = example_record()
        record["state_history"] = ["RECEIVED", "EXECUTING", "COMPLETED"]

        issues = validate_record(record)

        self.assertTrue(any(issue.requirement == "EAS-004-R02" for issue in issues))

    def test_outcome_must_match_terminal_state(self) -> None:
        record = example_record()
        record["outcome"] = "blocked"

        issues = validate_record(record)

        self.assertTrue(any(issue.requirement == "EAS-004-R06" for issue in issues))

    def test_task_result_is_distinct_from_terminal_outcome(self) -> None:
        record = example_record()
        record["state_history"][-1] = "BLOCKED"
        record["outcome"] = "blocked"
        record["task_result"] = "satisfied"

        issues = validate_record(record)

        self.assertTrue(
            any(
                issue.requirement == "EAS-002-R10"
                and issue.path == "$.task_result"
                for issue in issues
            )
        )

    def test_evidence_references_must_resolve(self) -> None:
        record = example_record()
        record["actions"][0]["evidence_refs"] = ["missing"]

        issues = validate_record(record)

        self.assertTrue(any(issue.requirement == "EAS-008-R02" for issue in issues))

    def test_material_action_requires_authorized_decision(self) -> None:
        record = example_record()
        record["actions"][0]["authority"] = "escalated"
        record["actions"][0]["decision_id"] = "missing"

        issues = validate_record(record)

        requirements = {issue.requirement for issue in issues}
        self.assertIn("EAS-005-R04", requirements)
        self.assertIn("EAS-005-R02", requirements)

    def test_passed_claim_requires_passed_evidence(self) -> None:
        record = example_record()
        next(
            item for item in record["evidence"] if item["id"] == "evidence-1"
        )["result"] = "failed"

        issues = validate_record(record)

        self.assertTrue(any(issue.requirement == "EAS-006-R03" for issue in issues))

    def test_passed_claim_may_also_reference_observations(self) -> None:
        record = example_record()
        record["evidence"].append(
            {
                "id": "evidence-2",
                "kind": "inspection",
                "description": "Observed the target artifact before the passing check.",
                "result": "observed",
                "source": "artifact inspection",
                "origin": "environment",
                "capture": "direct",
                "observed_at": "2026-07-11T00:01:00Z",
                "recorded_at": "2026-07-11T00:02:00Z",
            }
        )
        record["report"]["verification"][0]["evidence_refs"].append("evidence-2")

        self.assertEqual(validate_record(record), [])

    def test_duplicate_ids_fail(self) -> None:
        record = example_record()
        record["evidence"].append(copy.deepcopy(record["evidence"][0]))

        issues = validate_record(record)

        self.assertTrue(any("duplicate id" in issue.message for issue in issues))

    def test_all_conforming_examples_pass(self) -> None:
        for name in ("minimal-run.json", "escalated-run.json", "blocked-run.json"):
            with self.subTest(name=name):
                with (ROOT / "examples" / name).open(encoding="utf-8") as handle:
                    record = json.load(handle)
                self.assertEqual(validate_record(record), [])

    def test_documented_invalid_fixture_fails(self) -> None:
        path = ROOT / "examples" / "invalid" / "invalid-transition.json"
        with path.open(encoding="utf-8") as handle:
            record = json.load(handle)

        issues = validate_record(record)

        self.assertTrue(any(issue.requirement == "EAS-004-R02" for issue in issues))

    def test_nested_required_fields_are_checked(self) -> None:
        record = example_record()
        record["task"] = {"acceptance_criteria": []}
        record["final_state"]["revision"] = ""

        issues = validate_record(record)

        paths = {issue.path for issue in issues}
        self.assertIn("$.task.description", paths)
        self.assertIn("$.final_state.revision", paths)

    def test_task_class_and_disposition_are_checked(self) -> None:
        record = example_record()
        record["task"]["primary_class"] = "feature"
        record["decisions"][0]["disposition"] = "guess"

        issues = validate_record(record)

        requirements = {issue.requirement for issue in issues}
        self.assertIn("EAS-002-R07", requirements)
        self.assertIn("EAS-005-R02", requirements)


if __name__ == "__main__":
    unittest.main()
