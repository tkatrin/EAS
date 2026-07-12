"""Small dependency-free JSON Schema evaluator for EAS-owned schemas.

This is intentionally not a general JSON Schema implementation. It supports
the Draft 2020-12 keywords used by the versioned schemas in this repository and
fails closed when an EAS schema introduces an unsupported assertion keyword.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
import re
from typing import Any


@dataclass(frozen=True)
class SchemaIssue:
    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.path}: {self.message}"


_TYPE_MAP: dict[str, type | tuple[type, ...]] = {
    "object": dict,
    "array": list,
    "string": str,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
    "null": type(None),
}

_SUPPORTED_KEYWORDS = {
    "$schema",
    "$id",
    "$defs",
    "$ref",
    "title",
    "description",
    "type",
    "const",
    "enum",
    "oneOf",
    "allOf",
    "if",
    "then",
    "else",
    "format",
    "pattern",
    "minLength",
    "minimum",
    "required",
    "properties",
    "propertyNames",
    "additionalProperties",
    "minItems",
    "uniqueItems",
    "items",
}


def _json_equal(left: Any, right: Any) -> bool:
    return type(left) is type(right) and left == right


def _resolve_ref(root: dict[str, Any], reference: str) -> dict[str, Any]:
    if not reference.startswith("#/"):
        raise ValueError(f"unsupported non-local schema reference: {reference}")
    value: Any = root
    for raw_part in reference[2:].split("/"):
        part = raw_part.replace("~1", "/").replace("~0", "~")
        value = value[part]
    if not isinstance(value, dict):
        raise ValueError(f"schema reference does not resolve to an object: {reference}")
    return value


def _type_matches(instance: Any, expected: str) -> bool:
    if expected == "integer":
        return isinstance(instance, int) and not isinstance(instance, bool)
    if expected == "number":
        return isinstance(instance, (int, float)) and not isinstance(instance, bool)
    return isinstance(instance, _TYPE_MAP[expected])


def _validate_timestamp(value: str) -> bool:
    if not (value.endswith("Z") or value[-6:-5] in {"+", "-"}):
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def validate_instance(instance: Any, schema: dict[str, Any]) -> list[SchemaIssue]:
    """Validate *instance* against the supported subset of *schema*."""

    issues: list[SchemaIssue] = []

    def visit(value: Any, node: dict[str, Any], path: str) -> None:
        unsupported = set(node) - _SUPPORTED_KEYWORDS
        if unsupported:
            names = ", ".join(sorted(unsupported))
            raise ValueError(f"unsupported JSON Schema keyword(s): {names}")

        if "$ref" in node:
            visit(value, _resolve_ref(schema, node["$ref"]), path)
            return

        if "allOf" in node:
            for branch in node["allOf"]:
                visit(value, branch, path)

        def branch_matches(branch: dict[str, Any]) -> bool:
            before = len(issues)
            visit(value, branch, path)
            produced = len(issues) > before
            del issues[before:]
            return not produced

        if "if" in node:
            selected = node.get("then") if branch_matches(node["if"]) else node.get("else")
            if isinstance(selected, dict):
                visit(value, selected, path)

        if "oneOf" in node:
            matches = 0
            for branch in node["oneOf"]:
                if branch_matches(branch):
                    matches += 1
            if matches != 1:
                issues.append(SchemaIssue(path, f"must match exactly one oneOf branch; matched {matches}"))
            return

        expected_type = node.get("type")
        if expected_type is not None:
            expected_types = [expected_type] if isinstance(expected_type, str) else expected_type
            if not any(_type_matches(value, item) for item in expected_types):
                issues.append(
                    SchemaIssue(path, f"expected type {expected_type!r}, got {type(value).__name__}")
                )
                return

        if "const" in node and not _json_equal(value, node["const"]):
            issues.append(SchemaIssue(path, f"must equal {node['const']!r}"))
        if "enum" in node and not any(_json_equal(value, item) for item in node["enum"]):
            issues.append(SchemaIssue(path, f"must be one of {node['enum']!r}"))

        if (
            "minimum" in node
            and isinstance(value, (int, float))
            and not isinstance(value, bool)
            and value < node["minimum"]
        ):
            issues.append(SchemaIssue(path, f"must be greater than or equal to {node['minimum']}"))

        if isinstance(value, str):
            if len(value) < node.get("minLength", 0):
                issues.append(SchemaIssue(path, f"must contain at least {node['minLength']} characters"))
            pattern = node.get("pattern")
            if pattern is not None and re.search(pattern, value) is None:
                issues.append(SchemaIssue(path, f"must match pattern {pattern!r}"))
            if node.get("format") == "date-time" and not _validate_timestamp(value):
                issues.append(SchemaIssue(path, "must be an RFC 3339 date-time with offset"))

        if isinstance(value, list):
            if len(value) < node.get("minItems", 0):
                issues.append(SchemaIssue(path, f"must contain at least {node['minItems']} items"))
            if node.get("uniqueItems"):
                encoded = [json.dumps(item, sort_keys=True, separators=(",", ":")) for item in value]
                if len(encoded) != len(set(encoded)):
                    issues.append(SchemaIssue(path, "items must be unique"))
            item_schema = node.get("items")
            if isinstance(item_schema, dict):
                for index, item in enumerate(value):
                    visit(item, item_schema, f"{path}[{index}]")

        if isinstance(value, dict):
            required = node.get("required", [])
            for name in required:
                if name not in value:
                    issues.append(SchemaIssue(f"{path}.{name}", "required property is missing"))

            properties = node.get("properties", {})
            for name, child_schema in properties.items():
                if name in value:
                    visit(value[name], child_schema, f"{path}.{name}")

            property_names = node.get("propertyNames")
            if isinstance(property_names, dict):
                for name in value:
                    visit(name, property_names, f"{path}.<property:{name}>")

            if node.get("additionalProperties") is False:
                extras = set(value) - set(properties)
                for name in sorted(extras):
                    issues.append(SchemaIssue(f"{path}.{name}", "additional property is not allowed"))

    visit(instance, schema, "$")
    return issues
