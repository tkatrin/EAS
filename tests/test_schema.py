from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from eas_validator.schema import validate_instance


ROOT = Path(__file__).resolve().parents[1]


def load(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


class SchemaValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.run_schema = load(ROOT / "schemas" / "eas-run.schema.json")
        cls.record = load(ROOT / "examples" / "minimal-run.json")

    def test_reference_record_matches_schema(self) -> None:
        self.assertEqual(validate_instance(self.record, self.run_schema), [])

    def test_all_run_examples_match_schema(self) -> None:
        for path in sorted((ROOT / "examples").rglob("*.json")):
            if {"traces", "artifacts", "assessments"} & set(path.parts):
                continue
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertEqual(validate_instance(load(path), self.run_schema), [])

    def test_scenario_manifests_match_schema(self) -> None:
        schema = load(ROOT / "schemas" / "eas-scenario.schema.json")
        for path in sorted((ROOT / "compliance" / "scenarios").glob("*.json")):
            with self.subTest(path=path.name):
                self.assertEqual(validate_instance(load(path), schema), [])

    def test_corpora_match_schema(self) -> None:
        schema = load(ROOT / "schemas" / "eas-corpus.schema.json")
        for path in sorted((ROOT / "compliance" / "corpus").glob("*.json")):
            with self.subTest(path=path.name):
                self.assertEqual(validate_instance(load(path), schema), [])

    def test_missing_required_and_extra_property_fail(self) -> None:
        record = copy.deepcopy(self.record)
        del record["schema_version"]
        record["unexpected"] = True

        issues = validate_instance(record, self.run_schema)
        paths = {issue.path for issue in issues}

        self.assertIn("$.schema_version", paths)
        self.assertIn("$.unexpected", paths)

    def test_enum_timestamp_and_materiality_shape_fail(self) -> None:
        record = copy.deepcopy(self.record)
        record["task"]["primary_class"] = "feature"
        record["record_created_at"] = "not-a-time"
        record["actions"][0]["materiality"]["unknown"] = False

        issues = validate_instance(record, self.run_schema)
        paths = {issue.path for issue in issues}

        self.assertIn("$.task.primary_class", paths)
        self.assertIn("$.record_created_at", paths)
        self.assertIn("$.actions[0].materiality.unknown", paths)

    def test_conditional_trace_payload_is_validated(self) -> None:
        schema = load(
            ROOT / "schemas" / "eas-neutral-trace-event-0.1.0.schema.json"
        )
        event = {
            "trace_schema_version": "0.1.0",
            "event_id": "event-1",
            "type": "trace_start",
            "payload": {},
        }

        paths = {issue.path for issue in validate_instance(event, schema)}

        self.assertIn("$.payload.run_id", paths)

    def test_numeric_minimum_and_unsupported_keywords_fail_closed(self) -> None:
        issues = validate_instance(-1, {"type": "integer", "minimum": 0})

        self.assertTrue(issues)
        with self.assertRaisesRegex(ValueError, "unsupported JSON Schema keyword"):
            validate_instance("value", {"type": "string", "maxLength": 3})

    def test_irreversible_action_may_have_no_rollback_mechanism(self) -> None:
        record = copy.deepcopy(self.record)
        record["decisions"][0]["reversibility"] = {
            "level": "none",
            "limitations": ["The external effect cannot be restored."],
        }
        record["decisions"][0]["rollback_available"] = False
        record["decisions"][0]["rollback_verified"] = False

        self.assertEqual(validate_instance(record, self.run_schema), [])


if __name__ == "__main__":
    unittest.main()
