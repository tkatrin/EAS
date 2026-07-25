from __future__ import annotations

import json
import unittest
from pathlib import Path

from eas_validator.assessment import build_assessment_record
from eas_validator.registry import resolve_requirement_subjects
from eas_validator.report import render_json, render_markdown, render_report, render_terminal


ROOT = Path(__file__).resolve().parents[1]


def applicability(*, applicable: bool = True) -> dict:
    return {
        "subject_match": "matched",
        "base": "invoked" if applicable else "not_invoked",
        "task_class": "not_invoked",
        "action_or_state": "not_invoked",
        "risk_or_event": "not_invoked",
        "selected_profile": "not_invoked",
        "applicable": applicable,
        "basis": "Synthetic report fixture applicability.",
    }


class HumanReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with (ROOT / "examples" / "minimal-run.json").open(encoding="utf-8") as handle:
            source = json.load(handle)
        with (ROOT / "registry" / "requirements.json").open(encoding="utf-8") as handle:
            requirement_subjects = resolve_requirement_subjects(json.load(handle))
        cls.assessment = build_assessment_record(
            assessment_id="assessment-report-fixture",
            assessment_level="behavioral",
            assessor_name="reference-assessor",
            assessor_version="0.1.0",
            source_record=source,
            requirement_results=[
                {
                    "requirement_id": "EAS-006-R03",
                    "applicability": applicability(),
                    "title": "Evidence-backed success claim",
                    "level": "MUST",
                    "result": "fail",
                    "reason": "The success claim has no matching direct evidence.",
                    "evidence_refs": [],
                    "validator_rule_refs": ["VAL-PASSED-CLAIM-EVIDENCE"],
                    "scenario_refs": ["SCN-001"],
                },
                {
                    "requirement_id": "EAS-008-R02",
                    "applicability": applicability(),
                    "title": "Resolvable evidence references",
                    "level": "MUST",
                    "result": "indeterminate",
                    "reason": "The referenced external evidence was unavailable.",
                    "evidence_refs": [],
                    "validator_rule_refs": ["VAL-EVIDENCE-REFERENCE-INTEGRITY"],
                    "scenario_refs": ["SCN-001"],
                },
                {
                    "requirement_id": "EAS-005-R14",
                    "applicability": applicability(applicable=False),
                    "title": "Deterministic materiality classification",
                    "level": "MUST",
                    "result": "not_applicable",
                    "reason": "The fixture contains no performed action.",
                    "evidence_refs": [],
                    "validator_rule_refs": ["VAL-MATERIALITY-CLASSIFICATION"],
                    "scenario_refs": ["SCN-001"],
                },
            ],
            requirement_subjects=requirement_subjects,
            requirements_registry_version="0.1.1",
            validator_rules_registry_version="0.1.1",
            started_at="2026-07-12T00:00:00Z",
            completed_at="2026-07-12T00:00:01Z",
            scenario_set={
                "id": "core-0.1",
                "version": "0.1.0",
                "scenario_ids": ["SCN-001"],
            },
        )

    def test_terminal_report_preserves_all_non_pass_categories(self) -> None:
        rendered = render_terminal(self.assessment)

        self.assertIn("Result: FAIL", rendered)
        self.assertIn("Failed requirements: 1", rendered)
        self.assertIn("Indeterminate requirements: 1", rendered)
        self.assertIn("Not applicable: 1", rendered)
        self.assertIn("EAS-006-R03", rendered)

    def test_markdown_and_json_renderers_are_complete(self) -> None:
        markdown = render_markdown(self.assessment)
        document = json.loads(render_json(self.assessment))

        self.assertIn("# EAS assessment report", markdown)
        self.assertIn("## Scope and limitations", markdown)
        self.assertEqual(document["summary"]["result"], "fail")
        self.assertEqual(render_report(self.assessment, "markdown"), markdown)

    def test_invalid_assessment_is_not_rendered(self) -> None:
        invalid = dict(self.assessment)
        invalid["summary"] = {"result": "pass", "counts": {}}

        with self.assertRaisesRegex(ValueError, "cannot render invalid"):
            render_terminal(invalid)


if __name__ == "__main__":
    unittest.main()
