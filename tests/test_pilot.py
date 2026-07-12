from __future__ import annotations

import json
import unittest
from pathlib import Path

from eas_validator.pilot import build_pilot_report


ROOT = Path(__file__).resolve().parents[1]


class AdapterPilotTests(unittest.TestCase):
    def test_paired_controlled_sources_agree_without_real_world_overclaim(self) -> None:
        report = build_pilot_report(ROOT)

        self.assertEqual(report["fixture_type"], "controlled_synthetic")
        self.assertEqual(report["real_agent_trajectory_count"], 0)
        self.assertTrue(report["comparison"]["exact_semantic_projection_agreement"])
        self.assertTrue(report["comparison"]["structural_result_agreement"])
        self.assertTrue(report["comparison"]["scenario_result_agreement"])
        for implementation in report["implementations"]:
            self.assertEqual(implementation["schema_issue_count"], 0)
            self.assertEqual(implementation["structural_issue_count"], 0)
            self.assertEqual(implementation["scenario_issue_count"], 0)

    def test_committed_pilot_report_is_reproducible(self) -> None:
        expected = json.dumps(build_pilot_report(ROOT), indent=2, sort_keys=True) + "\n"

        observed = (ROOT / "reports" / "adapter-pilot.json").read_text(
            encoding="utf-8"
        )

        self.assertEqual(observed, expected)


if __name__ == "__main__":
    unittest.main()
