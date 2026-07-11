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
            ROOT / "compliance" / "scenarios" / "SCN-002-material-ambiguity.json"
        )
        record = load(ROOT / "examples" / "scenarios" / "material-ambiguity-run.json")
        record = copy.deepcopy(record)
        record["actions"] = [
            {
                "id": "action-1",
                "description": "Publish without destination confirmation.",
                "material": True,
                "authority": "authorized",
                "decision_id": "decision-1",
                "evidence_refs": ["evidence-1"],
            }
        ]

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
