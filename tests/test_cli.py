from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest

from eas_validator.__main__ import main
from eas_validator.assessment import validate_assessment_record


ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "examples" / "minimal-run.json"
SCENARIO = ROOT / "compliance" / "scenarios" / "SCN-001-focused-edit.json"
ARTIFACTS = ROOT / "examples" / "artifacts" / "SCN-001"


class CommandLineTests(unittest.TestCase):
    def test_validate_names_all_three_levels_without_overclaiming(self) -> None:
        output = StringIO()

        with redirect_stdout(output):
            result = main(["validate", str(RECORD)])

        rendered = output.getvalue()
        self.assertEqual(result, 0)
        self.assertIn("Level 1 — schema: PASS", rendered)
        self.assertIn("Level 2 — structural semantics: PASS", rendered)
        self.assertIn("Level 3 — behavioral assessment: NOT ASSESSED", rendered)
        self.assertIn("STRUCTURAL PASS ONLY", rendered)

    def test_assess_writes_versioned_json_when_artifacts_pass(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "assessment.json"
            output = StringIO()
            with redirect_stdout(output):
                result = main(
                    [
                        "assess",
                        str(RECORD),
                        "--scenario",
                        str(SCENARIO),
                        "--artifacts",
                        str(ARTIFACTS),
                        "--format",
                        "json",
                        "--output",
                        str(destination),
                        "--assessment-id",
                        "assessment-cli-test",
                    ]
                )

            with destination.open(encoding="utf-8") as handle:
                assessment = json.load(handle)
            self.assertEqual(result, 0)
            self.assertEqual(assessment["summary"]["result"], "pass")
            self.assertEqual(validate_assessment_record(assessment), [])

    def test_missing_required_artifacts_is_indeterminate(self) -> None:
        output = StringIO()

        with redirect_stdout(output):
            result = main(
                ["assess", str(RECORD), "--scenario", str(SCENARIO)]
            )

        self.assertEqual(result, 1)
        self.assertIn("Result: INDETERMINATE", output.getvalue())
        self.assertIn("required bundle missing", output.getvalue())

    def test_failed_scenario_is_attributed_to_bounded_requirement(self) -> None:
        with RECORD.open(encoding="utf-8") as handle:
            record = json.load(handle)
        record["task"]["primary_class"] = "review"
        record["task"]["candidate_classes"] = ["review"]
        record["task"]["classification_basis"] = "Deliberately wrong for the scenario."

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "wrong-class.json"
            path.write_text(json.dumps(record), encoding="utf-8")
            output = StringIO()
            with redirect_stdout(output):
                result = main(
                    [
                        "assess",
                        str(path),
                        "--scenario",
                        str(SCENARIO),
                        "--artifacts",
                        str(ARTIFACTS),
                    ]
                )

        rendered = output.getvalue()
        self.assertEqual(result, 1)
        self.assertIn("EAS-009-R09", rendered)
        self.assertIn("Result: FAIL", rendered)
        self.assertNotIn("Result: INDETERMINATE", rendered)

    def test_report_renders_saved_assessment_as_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "assessment.json"
            self.assertEqual(
                main(
                    [
                        "assess",
                        str(RECORD),
                        "--scenario",
                        str(SCENARIO),
                        "--artifacts",
                        str(ARTIFACTS),
                        "--format",
                        "json",
                        "--output",
                        str(destination),
                        "--assessment-id",
                        "assessment-report-test",
                    ]
                ),
                0,
            )
            output = StringIO()
            with redirect_stdout(output):
                result = main(
                    ["report", str(destination), "--format", "markdown"]
                )

        self.assertEqual(result, 0)
        self.assertIn("# EAS assessment report", output.getvalue())
        self.assertIn("**PASS**", output.getvalue())


if __name__ == "__main__":
    unittest.main()
