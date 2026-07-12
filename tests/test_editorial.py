from __future__ import annotations

import unittest
from pathlib import Path

from eas_validator.editorial import RequirementText, extract_requirements, review_requirements


ROOT = Path(__file__).resolve().parents[1]


class EditorialTests(unittest.TestCase):
    def test_extracts_unique_repository_requirements(self) -> None:
        requirements = extract_requirements(sorted((ROOT / "spec").glob("EAS-*.md")))
        identifiers = [item.identifier for item in requirements]

        self.assertGreater(len(identifiers), 100)
        self.assertEqual(len(identifiers), len(set(identifiers)))
        self.assertEqual(review_requirements(requirements), [])

    def test_flags_compound_and_vague_obligation(self) -> None:
        requirement = RequirementText(
            "EAS-999-R01",
            "An agent MUST act appropriately and MUST report it.",
            Path("example.md"),
            1,
        )

        kinds = {issue.kind for issue in review_requirements([requirement])}

        self.assertIn("compound-obligation", kinds)
        self.assertIn("operational-definition", kinds)


if __name__ == "__main__":
    unittest.main()
