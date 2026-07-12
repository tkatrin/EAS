from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from eas_validator.coverage import check_coverage_baseline, render_coverage_markdown
from eas_validator.registry import build_coverage


ROOT = Path(__file__).resolve().parents[1]


def load(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


class CoverageReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.coverage = build_coverage(
            load(ROOT / "registry" / "requirements.json"),
            load(ROOT / "registry" / "validator-rules.json"),
        )
        cls.baseline = load(ROOT / "registry" / "coverage-baseline.json")

    def test_committed_report_is_current_and_baseline_passes(self) -> None:
        rendered = render_coverage_markdown(self.coverage)

        self.assertEqual(
            (ROOT / "reports" / "requirement-coverage.md").read_text(encoding="utf-8"),
            rendered,
        )
        self.assertEqual(check_coverage_baseline(self.coverage, self.baseline), [])

    def test_regression_is_detected(self) -> None:
        regressed = copy.deepcopy(self.coverage)
        regressed["summary"]["with_validator_rules"] = 0
        regressed["summary"]["currently_unobservable"] = 999

        issues = check_coverage_baseline(regressed, self.baseline)

        self.assertTrue(any("with_validator_rules regressed" in issue for issue in issues))
        self.assertTrue(any("currently_unobservable regressed" in issue for issue in issues))


if __name__ == "__main__":
    unittest.main()
