from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from eas_validator.study_lock import build_study_lock, validate_study_lock


ROOT = Path(__file__).resolve().parents[1]
LOCK_PATH = ROOT / "research" / "study-lock-0.1.json"


class StudyLockTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.committed = json.loads(LOCK_PATH.read_text(encoding="utf-8"))

    def test_committed_lock_matches_its_historical_inputs(self) -> None:
        self.assertEqual(validate_study_lock(self.committed, ROOT), [])
        self.assertEqual(
            self.committed["scenario_set"]["scenario_ids"],
            [
                "SCN-001",
                "SCN-002",
                "SCN-003",
                "SCN-007",
                "SCN-008",
                "SCN-010",
                "SCN-011",
                "SCN-012",
            ],
        )

    def test_completed_lock_does_not_follow_later_worktree_changes(self) -> None:
        current = build_study_lock(ROOT, self.committed["source_revision"])

        self.assertNotEqual(self.committed, current)
        self.assertEqual(validate_study_lock(self.committed, ROOT), [])

    def test_changed_digest_is_rejected(self) -> None:
        changed = copy.deepcopy(self.committed)
        changed["groups"][0]["files"][0]["sha256"] = "0" * 64

        issues = validate_study_lock(changed, ROOT)

        self.assertTrue(any("locked digest changed" in issue for issue in issues))

    def test_changed_path_set_is_rejected(self) -> None:
        changed = copy.deepcopy(self.committed)
        changed["groups"][1]["files"].pop()

        issues = validate_study_lock(changed, ROOT)

        self.assertTrue(any("locked path set" in issue for issue in issues))

    def test_invalid_source_revision_is_rejected(self) -> None:
        changed = copy.deepcopy(self.committed)
        changed["source_revision"] = "main"

        self.assertEqual(
            validate_study_lock(changed, ROOT),
            ["source_revision must be a 40-character lowercase Git SHA"],
        )


if __name__ == "__main__":
    unittest.main()
