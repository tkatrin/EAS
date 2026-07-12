from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from eas_validator.artifacts import validate_artifact_files
from eas_validator.schema import validate_instance


ROOT = Path(__file__).resolve().parents[1]
BUNDLE_DIRECTORY = ROOT / "examples" / "artifacts" / "SCN-001"


def load(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


class ArtifactBundleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = load(BUNDLE_DIRECTORY / "manifest.json")
        cls.schema = load(ROOT / "schemas" / "eas-artifact-bundle.schema.json")

    def test_reference_bundle_matches_schema_files_and_scenario_coverage(self) -> None:
        self.assertEqual(validate_instance(self.bundle, self.schema), [])
        self.assertEqual(
            validate_artifact_files(
                self.bundle,
                BUNDLE_DIRECTORY,
                expected_run_id="run-example-001",
                required_kinds=("project_diff", "test_or_inspection_result"),
            ),
            [],
        )

    def test_wrong_hash_run_and_missing_kind_are_reported(self) -> None:
        bundle = copy.deepcopy(self.bundle)
        bundle["run_id"] = "another-run"
        bundle["artifacts"][0]["sha256"] = "0" * 64

        issues = validate_artifact_files(
            bundle,
            BUNDLE_DIRECTORY,
            expected_run_id="run-example-001",
            required_kinds=("project_diff", "authority_source"),
        )
        paths = {issue.path for issue in issues}

        self.assertIn("$artifacts.run_id", paths)
        self.assertIn("$artifacts.artifacts[0].sha256", paths)
        self.assertTrue(any("authority_source" in issue.message for issue in issues))

    def test_path_escape_is_rejected(self) -> None:
        bundle = copy.deepcopy(self.bundle)
        bundle["artifacts"][0]["path"] = "../manifest.json"

        issues = validate_artifact_files(bundle, BUNDLE_DIRECTORY)

        self.assertTrue(any("inside bundle" in issue.message for issue in issues))


if __name__ == "__main__":
    unittest.main()
