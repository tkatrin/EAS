from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "codex-pilot-calibration-0.1.json"


class CodexCalibrationReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT.read_text(encoding="utf-8"))

    def test_calibration_is_not_presented_as_validation(self) -> None:
        self.assertFalse(
            self.report["included_in_planned_16_trajectory_analysis"]
        )
        self.assertEqual(
            self.report["planned_trajectory_count_after_calibration"],
            0,
        )
        self.assertFalse(
            self.report["decision"]["continue_remaining_14_runs"]
        )
        self.assertIn(
            "not an EAS behavioral assessment",
            self.report["claim_boundary"],
        )

    def test_both_slots_preserve_negative_adapter_results(self) -> None:
        self.assertEqual(len(self.report["slots"]), 2)
        for slot in self.report["slots"]:
            self.assertEqual(slot["event_schema_issue_count"], 0)
            self.assertTrue(slot["tool_call_result_pairs_complete"])
            self.assertGreater(slot["run_schema_issue_count"], 0)
            self.assertGreater(slot["run_structural_issue_count"], 0)
            self.assertFalse(slot["behavioral_assessment_executed"])
            self.assertEqual(
                slot["capture_file_changes_misclassified_as_project_changes"],
                1,
            )

    def test_observed_workspace_effects_are_bounded(self) -> None:
        slots = {
            slot["slot_id"]: slot
            for slot in self.report["slots"]
        }

        self.assertEqual(
            slots["CDX-SCN-001-R1"]["changed_workspace_paths"],
            ["README.md"],
        )
        self.assertEqual(
            slots["CDX-SCN-002-R1"]["changed_workspace_paths"],
            [],
        )
        self.assertEqual(
            slots["CDX-SCN-002-R1"]["baseline_tree_sha256"],
            slots["CDX-SCN-002-R1"]["final_tree_sha256"],
        )


if __name__ == "__main__":
    unittest.main()
