from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from eas_validator.assessment import (
    SCENARIO_SCOPE_LIMITATION,
    aggregate_requirement_results,
    build_assessment_record,
    canonical_record_sha256,
    requirement_results_from_issues,
    validate_assessment_record,
)
from eas_validator.schema import validate_instance
from eas_validator.registry import resolve_requirement_subjects
from eas_validator.validator import ValidationIssue


ROOT = Path(__file__).resolve().parents[1]


def load(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def result(
    requirement_id: str,
    level: str,
    outcome: str,
    *,
    reason: str | None = None,
    scenario_refs: tuple[str, ...] = (),
) -> dict:
    item = {
        "requirement_id": requirement_id,
        "assessment_subject": "run",
        "applicability": {
            "subject_match": "matched",
            "base": "not_invoked" if outcome == "not_applicable" else "invoked",
            "task_class": "not_invoked",
            "action_or_state": "not_invoked",
            "risk_or_event": "not_invoked",
            "selected_profile": "not_invoked",
            "applicable": outcome != "not_applicable",
            "basis": "Synthetic assessment fixture applicability.",
        },
        "level": level,
        "result": outcome,
        "evidence_refs": [],
        "validator_rule_refs": [],
        "scenario_refs": list(scenario_refs),
    }
    if reason is not None:
        item["reason"] = reason
    return item


class AssessmentRecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = load(ROOT / "examples" / "minimal-run.json")
        cls.schema = load(ROOT / "schemas" / "eas-assessment.schema.json")
        cls.requirement_subjects = resolve_requirement_subjects(
            load(ROOT / "registry" / "requirements.json")
        )

    def build(self, **overrides: object) -> dict:
        arguments = {
            "assessment_id": "assessment-001",
            "assessment_level": "behavioral",
            "assessor_name": "reference-assessor",
            "assessor_version": "0.1.0",
            "source_record": self.source,
            "requirement_results": [
                result("EAS-006-R03", "MUST", "pass", scenario_refs=("SCN-003",)),
                result(
                    "EAS-005-R04",
                    "MUST",
                    "fail",
                    reason="The material action was not authorized.",
                    scenario_refs=("SCN-008",),
                ),
                result(
                    "EAS-008-R02",
                    "MUST",
                    "indeterminate",
                    reason="The referenced external evidence was unavailable.",
                ),
                result(
                    "EAS-005-R14",
                    "MUST",
                    "not_applicable",
                    reason="The run contains no performed action.",
                ),
            ],
            "requirement_subjects": self.requirement_subjects,
            "requirements_registry_version": "0.1.1",
            "validator_rules_registry_version": "0.1.1",
            "started_at": "2026-07-11T18:00:00Z",
            "completed_at": "2026-07-11T18:00:02Z",
            "record_created_at": "2026-07-11T18:00:03Z",
            "scenario_set": {
                "id": "core-0.1",
                "version": "0.1.0",
                "scenario_ids": ["SCN-001", "SCN-003", "SCN-008"],
            },
            "source_artifact_ref": "examples/minimal-run.json",
        }
        arguments.update(overrides)
        return build_assessment_record(**arguments)

    def test_builder_produces_schema_valid_assessment_with_aggregate_counts(self) -> None:
        assessment = self.build()

        self.assertEqual(validate_instance(assessment, self.schema), [])
        self.assertEqual(validate_assessment_record(assessment), [])
        self.assertEqual(
            assessment["summary"],
            {
                "result": "fail",
                "counts": {
                    "pass": 1,
                    "fail": 1,
                    "indeterminate": 1,
                    "not_applicable": 1,
                    "total": 4,
                },
            },
        )
        self.assertIn(SCENARIO_SCOPE_LIMITATION, assessment["limitations"])

    def test_builder_does_not_modify_source_record(self) -> None:
        original = copy.deepcopy(self.source)

        assessment = self.build()

        self.assertEqual(self.source, original)
        self.assertEqual(
            assessment["source_record"]["sha256"],
            canonical_record_sha256(original),
        )
        reordered = dict(reversed(list(original.items())))
        self.assertEqual(
            canonical_record_sha256(original), canonical_record_sha256(reordered)
        )

    def test_missing_reasons_are_rejected_by_schema_and_semantic_validator(self) -> None:
        assessment = self.build()
        del assessment["requirement_results"][2]["reason"]

        schema_issues = validate_instance(assessment, self.schema)
        semantic_issues = validate_assessment_record(assessment)

        self.assertTrue(
            any(issue.path == "$.requirement_results[2]" for issue in schema_issues)
        )
        self.assertTrue(
            any(
                issue.requirement == "EAS-009-R12"
                and issue.path == "$.requirement_results[2].reason"
                for issue in semantic_issues
            )
        )

    def test_must_failure_takes_priority_over_indeterminate(self) -> None:
        summary = aggregate_requirement_results(
            [
                result("EAS-008-R02", "MUST", "indeterminate", reason="Not observable."),
                result("EAS-006-R03", "MUST", "fail", reason="Contradicted."),
                result("EAS-999-R01", "SHOULD", "fail", reason="Missing."),
            ]
        )

        self.assertEqual(summary["result"], "fail")
        self.assertEqual(summary["counts"]["fail"], 2)

    def test_should_failure_remains_visible_without_forcing_nonconformance(self) -> None:
        summary = aggregate_requirement_results(
            [result("EAS-999-R01", "SHOULD", "fail", reason="Missing.")]
        )

        self.assertEqual(summary["result"], "pass")
        self.assertEqual(summary["counts"]["fail"], 1)

    def test_duplicate_results_and_inconsistent_summary_are_rejected(self) -> None:
        assessment = self.build()
        assessment["requirement_results"].append(
            copy.deepcopy(assessment["requirement_results"][0])
        )
        assessment["summary"]["counts"]["total"] += 1

        issues = validate_assessment_record(assessment)

        self.assertTrue(any("duplicate requirement result" in issue.message for issue in issues))
        self.assertTrue(any(issue.path == "$.summary.counts" for issue in issues))

    def test_time_order_and_scenario_level_are_cross_checked(self) -> None:
        assessment = self.build()
        assessment["completed_at"] = "2026-07-11T17:59:59Z"
        assessment["assessment_level"] = "structural"

        issues = validate_assessment_record(assessment)

        self.assertTrue(any(issue.path == "$.completed_at" for issue in issues))
        self.assertTrue(any(issue.path == "$.scenario_set" for issue in issues))

    def test_assessment_subject_is_explicit_and_validated(self) -> None:
        assessment = self.build()
        assessment["assessment_subject"]["type"] = "agent"

        schema_issues = validate_instance(assessment, self.schema)
        semantic_issues = validate_assessment_record(assessment)

        self.assertTrue(
            any(issue.path == "$.assessment_subject.type" for issue in schema_issues)
        )
        self.assertTrue(
            any(issue.path == "$.assessment_subject.type" for issue in semantic_issues)
        )

        assessment = self.build()
        assessment["assessment_level"] = "unqualified"

        schema_issues = validate_instance(assessment, self.schema)
        semantic_issues = validate_assessment_record(assessment)

        self.assertTrue(any(issue.path == "$.assessment_level" for issue in schema_issues))
        self.assertTrue(
            any(issue.path == "$.assessment_level" for issue in semantic_issues)
        )

        assessment = self.build()
        assessment["requirement_results"][0]["assessment_subject"] = (
            "assessor"
        )

        semantic_issues = validate_assessment_record(
            assessment, self.requirement_subjects
        )

        self.assertTrue(
            any(
                issue.path.endswith(".assessment_subject")
                for issue in semantic_issues
            )
        )

        with self.assertRaisesRegex(ValueError, "does not apply"):
            self.build(
                requirement_results=[
                    result("EAS-009-R08", "MUST", "pass")
                ]
            )

    def test_issue_conversion_is_limited_to_explicitly_evaluated_requirements(self) -> None:
        issues = [
            ValidationIssue(
                "EAS-004-R02",
                "$.state_history[1]",
                "transition is not permitted",
            )
        ]

        results = requirement_results_from_issues(
            {"EAS-004-R01": "MUST", "EAS-004-R02": "MUST"}, issues
        )

        self.assertEqual(results[0]["result"], "pass")
        self.assertEqual(results[1]["result"], "fail")
        self.assertIn("transition is not permitted", results[1]["reason"])

    def test_applicability_dimensions_are_required(self) -> None:
        assessment = self.build()
        del assessment["requirement_results"][0]["applicability"]["base"]

        schema_issues = validate_instance(assessment, self.schema)
        semantic_issues = validate_assessment_record(
            assessment, self.requirement_subjects
        )

        self.assertTrue(
            any(issue.path == "$.requirement_results[0]" for issue in schema_issues)
        )
        self.assertTrue(
            any(
                issue.requirement == "EAS-010-R18"
                and issue.path.endswith(".applicability.base")
                for issue in semantic_issues
            )
        )

    def test_non_run_subject_uses_general_source_descriptor(self) -> None:
        assessment = self.build(
            assessment_level="schema",
            assessment_subject_type="assessor",
            source_record={"id": "EAS-009", "content_revision": "draft-0.1"},
            requirement_results=[result("EAS-009-R08", "MUST", "pass")],
            scenario_set=None,
            source_artifact_ref="spec/EAS-009-compliance.md",
        )

        self.assertEqual(assessment["source_record"]["type"], "assessor")
        self.assertEqual(assessment["source_record"]["id"], "EAS-009")
        self.assertNotIn("run_id", assessment["source_record"])
        self.assertEqual(validate_instance(assessment, self.schema), [])
        self.assertEqual(
            validate_assessment_record(assessment, self.requirement_subjects),
            [],
        )

    def test_subject_limits_assessment_levels(self) -> None:
        with self.assertRaisesRegex(ValueError, "is not valid for subject"):
            self.build(
                assessment_level="structural",
                assessment_subject_type="observation",
            )

        assessment = self.build()
        assessment["assessment_subject"]["type"] = "observation"
        assessment["source_record"]["type"] = "observation"

        issues = validate_assessment_record(
            assessment,
            self.requirement_subjects,
        )

        self.assertTrue(
            any(
                issue.path.endswith(".assessment_subject")
                for issue in issues
            )
        )

    def test_committed_assessment_examples_are_valid_and_bound_to_source(self) -> None:
        for path in sorted((ROOT / "examples" / "assessments").glob("*.json")):
            with self.subTest(path=path.name):
                assessment = load(path)
                self.assertEqual(validate_instance(assessment, self.schema), [])
                self.assertEqual(
                    validate_assessment_record(
                        assessment, self.requirement_subjects
                    ),
                    [],
                )
                self.assertEqual(
                    assessment["source_record"]["sha256"],
                    canonical_record_sha256(self.source),
                )


if __name__ == "__main__":
    unittest.main()
