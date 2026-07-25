from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from eas_validator.registry import (
    build_coverage,
    discover_all_scenario_requirements,
    discover_spec_requirements,
    validate_registries,
)
from eas_validator.scenario import assess_scenario
from eas_validator.schema import validate_instance
from eas_validator.validator import validate_record


ROOT = Path(__file__).resolve().parents[1]


def load(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


class RegistryConsistencyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.requirements = load(ROOT / "registry" / "requirements.json")
        self.rules = load(ROOT / "registry" / "validator-rules.json")

    def test_current_registries_are_consistent(self) -> None:
        self.assertEqual(validate_registries(self.requirements, self.rules, ROOT), [])

    def test_registry_covers_every_current_specification_id(self) -> None:
        specification_ids = set(discover_spec_requirements(ROOT / "spec"))
        registry_ids = {item["id"] for item in self.requirements["requirements"]}

        self.assertEqual(registry_ids, specification_ids)
        self.assertEqual(len(registry_ids), 19)
        self.assertLessEqual(
            len(registry_ids),
            self.requirements["scope_policy"]["maximum_active_requirements"],
        )
        self.assertTrue(
            all(
                item["machine_checkable"] == "full"
                for item in self.requirements["requirements"]
            )
        )

    def test_manifest_and_corpus_scenario_links_are_reciprocal(self) -> None:
        scenario_references = discover_all_scenario_requirements(ROOT)
        requirement_scenarios = {
            item["id"]: set(item["scenarios"])
            for item in self.requirements["requirements"]
        }

        for scenario_id, requirement_ids in scenario_references.items():
            for requirement_id in requirement_ids:
                self.assertIn(scenario_id, requirement_scenarios[requirement_id])
        self.assertIn("SCN-001", requirement_scenarios["EAS-009-R09"])

    def test_machine_checkable_requirement_requires_a_rule(self) -> None:
        mutated = copy.deepcopy(self.requirements)
        target = next(
            item for item in mutated["requirements"] if item["id"] == "EAS-004-R02"
        )
        target["validator_rules"] = []

        issues = validate_registries(mutated, self.rules, ROOT)

        self.assertTrue(any(issue.code == "REG-CHECKABILITY" for issue in issues))

    def test_scope_policy_rejects_expansion_and_partial_requirements(self) -> None:
        expanded = copy.deepcopy(self.requirements)
        template = copy.deepcopy(expanded["requirements"][0])
        template["id"] = "EAS-099-R01"
        template["spec"] = "EAS-099"
        expanded["requirements"].append(template)
        template = copy.deepcopy(template)
        template["id"] = "EAS-099-R02"
        expanded["requirements"].append(template)

        issues = validate_registries(expanded, self.rules, ROOT)

        self.assertTrue(
            any(
                issue.code == "REG-SCOPE"
                and "maximum is 20" in issue.message
                for issue in issues
            )
        )

        partial = copy.deepcopy(self.requirements)
        partial["requirements"][0]["machine_checkable"] = "partial"

        issues = validate_registries(partial, self.rules, ROOT)

        self.assertTrue(
            any(
                issue.code == "REG-SCOPE"
                and issue.path.endswith(".machine_checkable")
                for issue in issues
            )
        )

    def test_unknown_scenario_reference_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.requirements)
        target = next(
            item for item in mutated["requirements"] if item["id"] == "EAS-002-R01"
        )
        target["scenarios"] = ["SCN-999"]

        issues = validate_registries(mutated, self.rules, ROOT)

        self.assertTrue(any("unknown scenario SCN-999" in issue.message for issue in issues))

    def test_rule_links_are_bidirectional(self) -> None:
        mutated = copy.deepcopy(self.rules)
        target = next(
            item for item in mutated["rules"] if item["id"] == "VAL-RUN-VERSION"
        )
        target["requirements"] = ["EAS-002-R01", "EAS-008-R15"]

        issues = validate_registries(self.requirements, mutated, ROOT)

        self.assertTrue(any(issue.code == "REG-TRACEABILITY" for issue in issues))

    def test_registry_level_matches_normative_text(self) -> None:
        mutated = copy.deepcopy(self.requirements)
        target = next(
            item for item in mutated["requirements"] if item["id"] == "EAS-005-R14"
        )
        target["level"] = "SHOULD"

        issues = validate_registries(mutated, self.rules, ROOT)

        self.assertTrue(any(issue.code == "REG-LEVEL" for issue in issues))

    def test_subject_policy_covers_requirements(self) -> None:
        mutated = copy.deepcopy(self.requirements)
        del mutated["assessment_subject_policy"]["defaults_by_spec"]["EAS-002"]

        issues = validate_registries(mutated, self.rules, ROOT)

        self.assertTrue(any(issue.code == "REG-SUBJECT" for issue in issues))

    def test_coverage_report_is_deterministic_and_explicit(self) -> None:
        coverage = build_coverage(self.requirements, self.rules)
        summary = coverage["summary"]

        self.assertEqual(summary["total_requirements"], 19)
        self.assertEqual(summary["by_level"], {"MAY": 0, "MUST": 19, "SHOULD": 0})
        self.assertEqual(summary["machine_checkable"], {"full": 19, "none": 0, "partial": 0})
        self.assertEqual(summary["currently_unobservable"], 0)
        self.assertGreater(summary["structurally_machine_checkable"], 0)
        self.assertGreater(summary["behaviorally_assessable"], 0)
        self.assertEqual(coverage["uncovered"]["validator_rules"], [])


class RegistryReferenceRuleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.record = load(ROOT / "examples" / "minimal-run.json")
        self.run_schema = load(ROOT / "schemas" / "eas-run.schema.json")
        self.scenario = load(
            ROOT / "compliance" / "scenarios" / "SCN-001-focused-edit.json"
        )

    def test_run_version_rule(self) -> None:
        record = copy.deepcopy(self.record)
        record["eas_version"] = "0.2"

        issues = validate_record(record)

        self.assertTrue(any(issue.requirement == "EAS-008-R15" for issue in issues))

    def test_lifecycle_start_rule(self) -> None:
        record = copy.deepcopy(self.record)
        record["state_history"][0] = "UNDERSTANDING"

        issues = validate_record(record)

        self.assertTrue(any(issue.requirement == "EAS-004-R01" for issue in issues))

    def test_verification_shape_rule(self) -> None:
        record = copy.deepcopy(self.record)
        record["report"]["verification"] = "passed"

        issues = validate_record(record)

        self.assertTrue(any(issue.path == "$.report.verification" for issue in issues))

    def test_evidence_shape_rule(self) -> None:
        record = copy.deepcopy(self.record)
        del record["evidence"][0]["source"]

        schema_issues = validate_instance(record, self.run_schema)
        semantic_issues = validate_record(record)

        self.assertTrue(any(issue.path == "$.evidence[0].source" for issue in schema_issues))
        self.assertTrue(any(issue.requirement == "EAS-008-R01" for issue in semantic_issues))

    def test_evidence_origin_rule(self) -> None:
        record = copy.deepcopy(self.record)
        del record["evidence"][0]["origin"]

        issues = validate_record(record)

        self.assertTrue(
            any(
                issue.requirement == "EAS-008-R01"
                and issue.path == "$.evidence[0].origin"
                for issue in issues
            )
        )

    def test_schema_version_rule(self) -> None:
        record = copy.deepcopy(self.record)
        record["schema_version"] = "0.2.0"

        issues = validate_record(record)

        self.assertTrue(any(issue.requirement == "EAS-008-R15" for issue in issues))

    def test_provenance_metadata_rule(self) -> None:
        record = copy.deepcopy(self.record)
        del record["implementation"]["adapter_version"]

        issues = validate_record(record)

        self.assertTrue(any(issue.requirement == "EAS-002-R01" for issue in issues))

    def test_timestamp_rule(self) -> None:
        record = copy.deepcopy(self.record)
        record["record_created_at"] = "2026-07-11 00:00:00"

        issues = validate_record(record)

        self.assertTrue(any(issue.requirement == "EAS-002-R01" for issue in issues))

        record = copy.deepcopy(self.record)
        del record["evidence"][0]["observed_at"]

        issues = validate_record(record)

        self.assertTrue(
            any(
                issue.requirement == "EAS-008-R01"
                and issue.path.endswith(".observed_at")
                for issue in issues
            )
        )

    def test_materiality_rule(self) -> None:
        record = copy.deepcopy(self.record)
        record["actions"][0]["material"] = False

        issues = validate_record(record)

        self.assertTrue(any(issue.requirement == "EAS-005-R14" for issue in issues))

    def test_material_decision_fields_rule(self) -> None:
        record = copy.deepcopy(self.record)
        del record["decisions"][0]["impact_level"]

        issues = validate_record(record)

        self.assertTrue(any(issue.requirement == "EAS-005-R02" for issue in issues))

    def test_reversibility_shape_rule(self) -> None:
        record = copy.deepcopy(self.record)
        record["decisions"][0]["reversibility"] = "reversible"

        issues = validate_record(record)

        self.assertTrue(any(issue.requirement == "EAS-005-R02" for issue in issues))

    def test_rollback_verified_requires_successful_evidence(self) -> None:
        record = copy.deepcopy(self.record)
        record["decisions"][0]["rollback_verified"] = True
        record["decisions"][0].pop("rollback_evidence_refs", None)

        issues = validate_record(record)

        self.assertTrue(
            any(
                issue.requirement == "EAS-005-R02"
                and issue.path.endswith(".rollback_verified")
                for issue in issues
            )
        )

        record = copy.deepcopy(self.record)
        record["decisions"][0]["rollback_available"] = False

        issues = validate_record(record)

        self.assertTrue(
            any(
                issue.requirement == "EAS-005-R02"
                and issue.path.endswith(".rollback_available")
                for issue in issues
            )
        )

    def test_authority_evidence_rule(self) -> None:
        record = copy.deepcopy(self.record)
        record["decisions"][0]["authority_evidence_refs"] = []

        issues = validate_record(record)

        self.assertTrue(any(issue.requirement == "EAS-005-R02" for issue in issues))

    def test_structured_authority_scope_rule(self) -> None:
        record = copy.deepcopy(self.record)
        del record["decisions"][0]["authorization_scope"]["target"]

        issues = validate_record(record)

        self.assertTrue(
            any(
                issue.requirement == "EAS-005-R02"
                and issue.path.endswith("authorization_scope.target")
                for issue in issues
            )
        )

    def test_self_reported_evidence_rule(self) -> None:
        record = copy.deepcopy(self.record)
        passed = next(item for item in record["evidence"] if item["result"] == "passed")
        passed["capture"] = "self_reported"

        issues = validate_record(record)

        self.assertTrue(any(issue.requirement == "EAS-006-R03" for issue in issues))

    def test_task_classification_details_rule(self) -> None:
        record = copy.deepcopy(self.record)
        record["task"]["candidate_classes"] = ["diagnose"]
        record["task"]["secondary_classes"] = [record["task"]["primary_class"]]

        issues = validate_record(record)
        requirements = {issue.requirement for issue in issues}

        self.assertEqual(requirements, {"EAS-002-R07"})

    def test_extension_namespace_rule(self) -> None:
        record = copy.deepcopy(self.record)
        record["extensions"] = {"invalid": {"value": 1}}

        issues = validate_instance(record, self.run_schema)

        self.assertTrue(any("property:invalid" in issue.path for issue in issues))

    def test_scenario_manifest_rule(self) -> None:
        scenario = copy.deepcopy(self.scenario)
        del scenario["input"]

        issues = assess_scenario(scenario, self.record)

        self.assertTrue(any(issue.path == "$scenario.input" for issue in issues))

    def test_scenario_expectations_rule(self) -> None:
        mutations = (
            ("outcome", "blocked", "$.outcome"),
            ("task_result", "not_satisfied", "$.task_result"),
            ("task_class", "advise", "$.task.primary_class"),
            ("required_states", ["BLOCKED"], "$.state_history"),
            ("required_dispositions", ["block"], "$.decisions"),
            ("required_evidence_results", ["inconclusive"], "$.evidence"),
            ("required_evidence_kinds", ["tool"], "$.evidence"),
            ("required_verification_statuses", ["failed"], "$.report.verification"),
            ("project_state_change", "forbidden", "$.final_state.revision"),
            ("required_report_sections_nonempty", ["limitations"], "$.report.limitations"),
        )
        for field, value, expected_path in mutations:
            with self.subTest(field=field):
                scenario = copy.deepcopy(self.scenario)
                scenario["expected"][field] = value
                issues = assess_scenario(scenario, self.record)
                self.assertTrue(any(issue.path == expected_path for issue in issues))


if __name__ == "__main__":
    unittest.main()
