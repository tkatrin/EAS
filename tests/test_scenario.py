from __future__ import annotations

import copy
import json
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from eas_validator import assess_scenario
from eas_validator.__main__ import main


ROOT = Path(__file__).resolve().parents[1]


def load(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


CASES = (
    ("SCN-001-focused-edit.json", ROOT / "examples" / "minimal-run.json"),
    (
        "SCN-002-material-ambiguity.json",
        ROOT / "examples" / "scenarios" / "material-ambiguity-run.json",
    ),
    (
        "SCN-003-failed-verification.json",
        ROOT / "examples" / "scenarios" / "failed-verification-run.json",
    ),
    (
        "SCN-007-diagnosis-without-fix.json",
        ROOT / "examples" / "scenarios" / "diagnosis-without-fix-run.json",
    ),
    (
        "SCN-008-authorized-operation.json",
        ROOT / "examples" / "scenarios" / "authorized-operation-run.json",
    ),
    (
        "SCN-010-scoped-review.json",
        ROOT / "examples" / "scenarios" / "scoped-review-run.json",
    ),
    (
        "SCN-011-sourced-research.json",
        ROOT / "examples" / "scenarios" / "sourced-research-run.json",
    ),
    (
        "SCN-012-bounded-advice.json",
        ROOT / "examples" / "scenarios" / "bounded-advice-run.json",
    ),
)


class ScenarioAssessmentTests(unittest.TestCase):
    def test_reference_runs_pass_their_scenarios(self) -> None:
        for scenario_name, record_path in CASES:
            with self.subTest(scenario=scenario_name):
                scenario = load(ROOT / "compliance" / "scenarios" / scenario_name)
                record = load(record_path)
                self.assertEqual(assess_scenario(scenario, record), [])

    def test_wrong_outcome_and_forbidden_action_fail(self) -> None:
        scenario = load(
            ROOT / "compliance" / "scenarios" / "SCN-008-authorized-operation.json"
        )
        record = load(ROOT / "examples" / "scenarios" / "authorized-operation-run.json")
        record = copy.deepcopy(record)
        second_action = copy.deepcopy(record["actions"][0])
        second_action["id"] = "action-2"
        second_action["description"] = "Perform an additional unrequested production action."
        record["actions"].append(second_action)

        issues = assess_scenario(scenario, record)

        self.assertTrue(any("material actions" in issue.message for issue in issues))

    def test_structural_failure_is_reported_before_expectations(self) -> None:
        scenario = load(
            ROOT / "compliance" / "scenarios" / "SCN-001-focused-edit.json"
        )
        record = load(ROOT / "examples" / "minimal-run.json")
        record["state_history"] = ["RECEIVED", "EXECUTING", "COMPLETED"]

        issues = assess_scenario(scenario, record)

        self.assertTrue(any(issue.requirement == "EAS-004-R02" for issue in issues))

    def test_evidence_kind_state_change_and_report_sections_are_checked(self) -> None:
        scenario = load(
            ROOT / "compliance" / "scenarios" / "SCN-008-authorized-operation.json"
        )
        record = load(ROOT / "examples" / "scenarios" / "authorized-operation-run.json")
        record = copy.deepcopy(record)
        record["evidence"][0]["kind"] = "inspection"
        record["final_state"]["revision"] = record["initial_state"]["revision"]
        record["report"]["changes"] = []

        issues = assess_scenario(scenario, record)

        messages = {issue.message for issue in issues}
        self.assertIn("required kind 'user' is absent", messages)
        self.assertIn("project state change is required", messages)
        self.assertIn("section must be non-empty", messages)

    def test_cli_scenario_mode(self) -> None:
        scenario_path = (
            ROOT / "compliance" / "scenarios" / "SCN-001-focused-edit.json"
        )
        record_path = ROOT / "examples" / "minimal-run.json"
        output = StringIO()

        with redirect_stdout(output):
            result = main([str(record_path), "--scenario", str(scenario_path)])

        self.assertEqual(result, 0)
        self.assertIn("SCN-001", output.getvalue())


if __name__ == "__main__":
    unittest.main()
