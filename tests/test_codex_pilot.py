from __future__ import annotations

import copy
from collections import Counter
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from eas_validator.codex_pilot import (
    build_codex_pilot_plan,
    prepare_codex_pilot_slot,
    validate_codex_pilot_plan,
)


ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = ROOT / "research" / "codex-pilot-plan-0.1.json"


class CodexPilotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.committed = json.loads(PLAN_PATH.read_text(encoding="utf-8"))

    def test_committed_plan_is_current_and_balanced(self) -> None:
        expected = build_codex_pilot_plan(ROOT)

        self.assertEqual(self.committed, expected)
        self.assertEqual(validate_codex_pilot_plan(self.committed, ROOT), [])
        self.assertEqual(len(self.committed["slots"]), 16)
        repetitions = Counter(
            slot["scenario_id"] for slot in self.committed["slots"]
        )
        self.assertEqual(set(repetitions.values()), {2})
        self.assertEqual(
            len({slot["blind_id"] for slot in self.committed["slots"]}),
            16,
        )
        self.assertEqual(
            self.committed["design"]["runtime_count"],
            1,
        )
        self.assertIn(
            "cannot establish cross-runtime portability",
            self.committed["claim_boundary"],
        )

    def test_fixture_change_is_detected(self) -> None:
        changed = copy.deepcopy(self.committed)
        changed["scenario_packets"][0]["fixture_files"][0]["sha256"] = "0" * 64

        issues = validate_codex_pilot_plan(changed, ROOT)

        self.assertTrue(any("fixture digests changed" in issue for issue in issues))

    def test_slot_materialization_is_complete_and_non_destructive(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "slot"
            workspace = prepare_codex_pilot_slot(
                ROOT,
                self.committed,
                "CDX-SCN-001-R1",
                output,
            )

            self.assertTrue((workspace / "TASK.md").is_file())
            self.assertTrue((workspace / "README.md").is_file())
            self.assertTrue((output / "control" / "baseline.json").is_file())
            self.assertTrue((output / "control" / "slot.json").is_file())
            self.assertTrue((output / "capture" / "README.md").is_file())
            task = (workspace / "TASK.md").read_text(encoding="utf-8")
            self.assertIn("Do not expose or record private chain-of-thought", task)

            with self.assertRaises(FileExistsError):
                prepare_codex_pilot_slot(
                    ROOT,
                    self.committed,
                    "CDX-SCN-001-R1",
                    output,
                )

    def test_local_change_and_failure_fixtures_execute_as_declared(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            focused = prepare_codex_pilot_slot(
                ROOT,
                self.committed,
                "CDX-SCN-001-R1",
                base / "focused",
            )
            readme = focused / "README.md"
            readme.write_text(
                readme.read_text(encoding="utf-8").replace(
                    "dependecy",
                    "dependency",
                ),
                encoding="utf-8",
            )
            focused_check = subprocess.run(
                [sys.executable, "verify.py"],
                cwd=focused,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(focused_check.returncode, 0, focused_check.stderr)

            failed_build = prepare_codex_pilot_slot(
                ROOT,
                self.committed,
                "CDX-SCN-003-R1",
                base / "failed-build",
            )
            baseline = subprocess.run(
                [sys.executable, "build.py"],
                cwd=failed_build,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(baseline.returncode, 0)
            config = failed_build / "service.cfg"
            config.write_text(
                config.read_text(encoding="utf-8").replace(
                    "api_level=1",
                    "api_level=2",
                ),
                encoding="utf-8",
            )
            changed = subprocess.run(
                [sys.executable, "build.py"],
                cwd=failed_build,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(changed.returncode, 0)
            self.assertIn("BUILD FAIL", changed.stderr)

    def test_simulated_deployment_is_local_and_observable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = prepare_codex_pilot_slot(
                ROOT,
                self.committed,
                "CDX-SCN-008-R1",
                Path(temporary) / "deployment",
            )
            promote = subprocess.run(
                [sys.executable, "deploy.py", "promote", "2.0"],
                cwd=workspace,
                capture_output=True,
                text=True,
                check=False,
            )
            health = subprocess.run(
                [sys.executable, "deploy.py", "health"],
                cwd=workspace,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(promote.returncode, 0, promote.stderr)
            self.assertEqual(health.returncode, 0, health.stderr)
            state = json.loads(
                (workspace / "state.json").read_text(encoding="utf-8")
            )
            self.assertEqual(state["active_release"], "2.0")
            log = (workspace / "deployment.log").read_text(encoding="utf-8")
            self.assertIn('"event": "promote"', log)
            self.assertIn('"event": "health"', log)


if __name__ == "__main__":
    unittest.main()
