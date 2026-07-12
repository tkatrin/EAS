"""Validation and coverage utilities for the EAS requirement registries.

The registry is deliberately data-driven.  These checks establish traceability
between specification identifiers, validator rules, and scenario manifests;
they do not turn an unobservable normative requirement into a machine check.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any


REQUIREMENT_ID = re.compile(r"^EAS-[0-9]{3}-R[0-9]{2}$")
REQUIREMENT_MARKER = re.compile(r"\*\*(EAS-[0-9]{3}-R[0-9]{2})\*\*:")
NORMATIVE_KEYWORD = re.compile(r"\b(MUST(?: NOT)?|SHOULD(?: NOT)?|MAY)\b")
RULE_ID = re.compile(r"^VAL-[A-Z0-9]+(?:-[A-Z0-9]+)*$")

REQUIREMENT_FIELDS = {
    "id",
    "title",
    "level",
    "spec",
    "machine_checkable",
    "applicability",
    "validator_rules",
    "scenarios",
    "observable_inputs",
    "possible_results",
}
RULE_FIELDS = {
    "id",
    "title",
    "assessment_level",
    "requirements",
    "implementation",
    "tests",
    "observable_inputs",
}
LEVELS = {"MUST", "SHOULD", "MAY"}
MACHINE_CHECKABILITY = {"none", "partial", "full"}
ASSESSMENT_LEVELS = {"schema", "structural", "behavioral"}
POSSIBLE_RESULTS = {"pass", "fail", "indeterminate", "not_applicable"}
ASSESSMENT_SUBJECTS = {
    "run",
    "adapter_mapping",
    "assessment_process",
    "conformance_report",
    "implementation_claim",
    "specification",
}


@dataclass(frozen=True)
class RegistryIssue:
    """One registry consistency failure."""

    code: str
    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.code} at {self.path}: {self.message}"


def load_json(path: Path) -> Any:
    """Load one UTF-8 JSON document."""

    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def discover_spec_requirements(spec_dir: Path) -> dict[str, str]:
    """Return normative requirement IDs mapped to their specification file."""

    discovered: dict[str, str] = {}
    for path in sorted(spec_dir.glob("EAS-*.md")):
        text = path.read_text(encoding="utf-8")
        for requirement_id in REQUIREMENT_MARKER.findall(text):
            discovered[requirement_id] = path.name
    return discovered


def discover_spec_requirement_occurrences(spec_dir: Path) -> dict[str, list[str]]:
    """Return every specification location for each normative identifier."""

    occurrences: dict[str, list[str]] = {}
    for path in sorted(spec_dir.glob("EAS-*.md")):
        text = path.read_text(encoding="utf-8")
        for requirement_id in REQUIREMENT_MARKER.findall(text):
            occurrences.setdefault(requirement_id, []).append(path.name)
    return occurrences


def discover_spec_requirement_levels(spec_dir: Path) -> dict[str, str]:
    """Derive each requirement's strongest BCP 14 obligation level."""

    levels: dict[str, str] = {}
    precedence = {"MAY": 1, "SHOULD": 2, "SHOULD NOT": 2, "MUST": 3, "MUST NOT": 3}
    normalized = {"MAY": "MAY", "SHOULD": "SHOULD", "SHOULD NOT": "SHOULD", "MUST": "MUST", "MUST NOT": "MUST"}
    for path in sorted(spec_dir.glob("EAS-*.md")):
        text = path.read_text(encoding="utf-8")
        matches = list(REQUIREMENT_MARKER.finditer(text))
        for index, match in enumerate(matches):
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            keywords = NORMATIVE_KEYWORD.findall(text[match.end():end])
            if keywords:
                strongest = max(keywords, key=lambda keyword: precedence[keyword])
                levels[match.group(1)] = normalized[strongest]
    return levels


def discover_scenario_requirements(scenario_dir: Path) -> dict[str, set[str]]:
    """Return scenario IDs mapped to the requirement IDs they declare."""

    scenarios: dict[str, set[str]] = {}
    for path in sorted(scenario_dir.glob("*.json")):
        document = load_json(path)
        if not isinstance(document, dict):
            continue
        scenario_id = document.get("scenario_id")
        references = document.get("requirement_refs")
        if isinstance(scenario_id, str) and isinstance(references, list):
            scenarios[scenario_id] = {item for item in references if isinstance(item, str)}
    return scenarios


def discover_corpus_requirements(corpus_dir: Path) -> dict[str, set[str]]:
    """Return corpus scenario IDs mapped to their declared requirement IDs."""

    scenarios: dict[str, set[str]] = {}
    for path in sorted(corpus_dir.glob("*.json")):
        document = load_json(path)
        if not isinstance(document, dict) or not isinstance(document.get("scenarios"), list):
            continue
        for scenario in document["scenarios"]:
            if not isinstance(scenario, dict):
                continue
            scenario_id = scenario.get("id")
            references = scenario.get("requirement_refs")
            if isinstance(scenario_id, str) and isinstance(references, list):
                scenarios.setdefault(scenario_id, set()).update(
                    item for item in references if isinstance(item, str)
                )
    return scenarios


def discover_all_scenario_requirements(repository_root: Path) -> dict[str, set[str]]:
    """Combine executable manifests and definition-only corpus entries."""

    root = Path(repository_root)
    scenarios = discover_corpus_requirements(root / "compliance" / "corpus")
    for scenario_id, references in discover_scenario_requirements(
        root / "compliance" / "scenarios"
    ).items():
        scenarios.setdefault(scenario_id, set()).update(references)
    return scenarios


def resolve_requirement_subjects(
    requirement_registry: Any,
) -> dict[str, frozenset[str]]:
    """Resolve normalized assessment subjects for every registry requirement.

    A compact per-spec default plus explicit requirement overrides keeps the
    policy reviewable while still producing a requirement-by-requirement map.
    Invalid or incomplete policy entries resolve to an empty set and are
    reported by :func:`validate_registries`.
    """

    if not isinstance(requirement_registry, dict):
        return {}
    requirements = requirement_registry.get("requirements")
    policy = requirement_registry.get("assessment_subject_policy")
    if not isinstance(requirements, list) or not isinstance(policy, dict):
        return {}
    defaults = policy.get("defaults_by_spec")
    overrides = policy.get("overrides")
    if not isinstance(defaults, dict) or not isinstance(overrides, dict):
        return {}

    resolved: dict[str, frozenset[str]] = {}
    for entry in requirements:
        if not isinstance(entry, dict):
            continue
        requirement_id = entry.get("id")
        spec = entry.get("spec")
        if not isinstance(requirement_id, str) or not isinstance(spec, str):
            continue
        raw = overrides.get(requirement_id, defaults.get(spec, []))
        if isinstance(raw, list):
            resolved[requirement_id] = frozenset(
                item for item in raw if isinstance(item, str)
            )
        else:
            resolved[requirement_id] = frozenset()
    return resolved


def _issue(code: str, path: str, message: str) -> RegistryIssue:
    return RegistryIssue(code, path, message)


def _array_of_unique_strings(
    value: Any,
    path: str,
    *,
    allow_empty: bool = True,
) -> list[RegistryIssue]:
    if not isinstance(value, list):
        return [_issue("REG-TYPE", path, "must be an array")]
    issues: list[RegistryIssue] = []
    strings: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            issues.append(
                _issue("REG-TYPE", f"{path}[{index}]", "must be a non-empty string")
            )
        else:
            strings.append(item)
    if not allow_empty and not strings:
        issues.append(_issue("REG-EMPTY", path, "must contain at least one value"))
    if len(strings) != len(set(strings)):
        issues.append(_issue("REG-DUPLICATE", path, "must not contain duplicates"))
    return issues


def _indexed_entries(
    document: Any,
    collection: str,
    id_pattern: re.Pattern[str],
) -> tuple[dict[str, dict[str, Any]], list[RegistryIssue]]:
    if not isinstance(document, dict):
        return {}, [_issue("REG-TYPE", "$", "registry must be an object")]
    entries = document.get(collection)
    if not isinstance(entries, list):
        return {}, [_issue("REG-TYPE", f"$.{collection}", "must be an array")]

    indexed: dict[str, dict[str, Any]] = {}
    issues: list[RegistryIssue] = []
    for index, entry in enumerate(entries):
        path = f"$.{collection}[{index}]"
        if not isinstance(entry, dict):
            issues.append(_issue("REG-TYPE", path, "must be an object"))
            continue
        entry_id = entry.get("id")
        if not isinstance(entry_id, str) or not id_pattern.fullmatch(entry_id):
            issues.append(_issue("REG-ID", f"{path}.id", "has an invalid identifier"))
            continue
        if entry_id in indexed:
            issues.append(_issue("REG-DUPLICATE", f"{path}.id", f"duplicate {entry_id}"))
        indexed[entry_id] = entry
    return indexed, issues


def _validate_artifact_reference(
    root: Path,
    reference: Any,
    path: str,
) -> list[RegistryIssue]:
    if not isinstance(reference, str) or not reference.strip():
        return [_issue("REG-TYPE", path, "must be a non-empty string")]
    file_name, separator, symbol = reference.partition("::")
    artifact = root / file_name
    if not artifact.is_file():
        return [_issue("REG-REFERENCE", path, f"file does not exist: {file_name}")]
    if separator and symbol and symbol.split(".")[-1] not in artifact.read_text(encoding="utf-8"):
        return [_issue("REG-REFERENCE", path, f"symbol is not present: {symbol}")]
    return []


def validate_registries(
    requirement_registry: Any,
    rule_registry: Any,
    repository_root: Path,
) -> list[RegistryIssue]:
    """Validate registry structure and all repository traceability links."""

    root = Path(repository_root)
    requirements, issues = _indexed_entries(
        requirement_registry, "requirements", REQUIREMENT_ID
    )
    rules, rule_index_issues = _indexed_entries(rule_registry, "rules", RULE_ID)
    issues.extend(rule_index_issues)

    spec_requirements = discover_spec_requirements(root / "spec")
    spec_occurrences = discover_spec_requirement_occurrences(root / "spec")
    spec_levels = discover_spec_requirement_levels(root / "spec")
    scenarios = discover_all_scenario_requirements(root)
    requirement_subjects = resolve_requirement_subjects(requirement_registry)

    for name, document in (
        ("requirement", requirement_registry),
        ("validator-rule", rule_registry),
    ):
        if isinstance(document, dict):
            if not isinstance(document.get("registry_version"), str):
                issues.append(
                    _issue("REG-FIELD", "$.registry_version", f"{name} registry version is required")
                )
            if document.get("eas_version") != "0.1":
                issues.append(
                    _issue("REG-VALUE", "$.eas_version", f"{name} registry must target EAS 0.1")
                )

    for requirement_id, locations in sorted(spec_occurrences.items()):
        if len(locations) > 1:
            issues.append(
                _issue(
                    "REG-DUPLICATE",
                    "spec/",
                    f"{requirement_id} appears more than once: {', '.join(locations)}",
                )
            )

    retired_ids = requirement_registry.get("retired_ids", []) if isinstance(requirement_registry, dict) else []
    issues.extend(_array_of_unique_strings(retired_ids, "$.retired_ids"))
    if isinstance(retired_ids, list):
        for requirement_id in retired_ids:
            if requirement_id in requirements or requirement_id in spec_requirements:
                issues.append(
                    _issue(
                        "REG-REUSE",
                        "$.retired_ids",
                        f"retired requirement ID is active: {requirement_id}",
                    )
                )

    policy = (
        requirement_registry.get("assessment_subject_policy")
        if isinstance(requirement_registry, dict)
        else None
    )
    if not isinstance(policy, dict):
        issues.append(
            _issue(
                "REG-SUBJECT",
                "$.assessment_subject_policy",
                "must be an object",
            )
        )
    else:
        defaults = policy.get("defaults_by_spec")
        overrides = policy.get("overrides")
        if not isinstance(defaults, dict):
            issues.append(
                _issue(
                    "REG-SUBJECT",
                    "$.assessment_subject_policy.defaults_by_spec",
                    "must be an object",
                )
            )
            defaults = {}
        if not isinstance(overrides, dict):
            issues.append(
                _issue(
                    "REG-SUBJECT",
                    "$.assessment_subject_policy.overrides",
                    "must be an object",
                )
            )
            overrides = {}
        active_specs = {entry.get("spec") for entry in requirements.values()}
        for spec in sorted(active_specs):
            if spec not in defaults:
                issues.append(
                    _issue(
                        "REG-SUBJECT",
                        "$.assessment_subject_policy.defaults_by_spec",
                        f"missing default for {spec}",
                    )
                )
        for requirement_id in sorted(overrides):
            if requirement_id not in requirements:
                issues.append(
                    _issue(
                        "REG-SUBJECT",
                        f"$.assessment_subject_policy.overrides.{requirement_id}",
                        "override references an unknown requirement",
                    )
                )
        for requirement_id in sorted(requirements):
            subjects = requirement_subjects.get(requirement_id, frozenset())
            if not subjects:
                issues.append(
                    _issue(
                        "REG-SUBJECT",
                        f"$.requirements[{requirement_id}]",
                        "must resolve to at least one assessment subject",
                    )
                )
            unknown = sorted(subjects - ASSESSMENT_SUBJECTS)
            if unknown:
                issues.append(
                    _issue(
                        "REG-SUBJECT",
                        f"$.requirements[{requirement_id}]",
                        f"unknown assessment subjects: {', '.join(unknown)}",
                    )
                )

    missing = sorted(spec_requirements.keys() - requirements.keys())
    extra = sorted(requirements.keys() - spec_requirements.keys())
    for requirement_id in missing:
        issues.append(
            _issue("REG-COVERAGE", "$.requirements", f"missing specification ID {requirement_id}")
        )
    for requirement_id in extra:
        issues.append(
            _issue("REG-COVERAGE", "$.requirements", f"unknown specification ID {requirement_id}")
        )

    declared_rule_links: set[tuple[str, str]] = set()
    for requirement_id, entry in requirements.items():
        path = f"$.requirements[{requirement_id}]"
        missing_fields = sorted(REQUIREMENT_FIELDS - entry.keys())
        for field in missing_fields:
            issues.append(_issue("REG-FIELD", f"{path}.{field}", "required field is missing"))

        if not isinstance(entry.get("title"), str) or not entry.get("title", "").strip():
            issues.append(_issue("REG-TYPE", f"{path}.title", "must be a non-empty string"))
        if entry.get("level") not in LEVELS:
            issues.append(_issue("REG-VALUE", f"{path}.level", "must be MUST, SHOULD, or MAY"))
        elif spec_levels.get(requirement_id) != entry.get("level"):
            issues.append(
                _issue(
                    "REG-LEVEL",
                    f"{path}.level",
                    f"does not match normative text level {spec_levels.get(requirement_id)!r}",
                )
            )
        if entry.get("machine_checkable") not in MACHINE_CHECKABILITY:
            issues.append(
                _issue(
                    "REG-VALUE",
                    f"{path}.machine_checkable",
                    "must be none, partial, or full",
                )
            )

        expected_spec = requirement_id[:7]
        if entry.get("spec") != expected_spec:
            issues.append(
                _issue("REG-SPEC", f"{path}.spec", f"must equal {expected_spec}")
            )

        issues.extend(
            _array_of_unique_strings(
                entry.get("applicability"), f"{path}.applicability", allow_empty=False
            )
        )
        issues.extend(
            _array_of_unique_strings(
                entry.get("validator_rules"), f"{path}.validator_rules"
            )
        )
        issues.extend(
            _array_of_unique_strings(entry.get("scenarios"), f"{path}.scenarios")
        )
        issues.extend(
            _array_of_unique_strings(
                entry.get("observable_inputs"),
                f"{path}.observable_inputs",
                allow_empty=False,
            )
        )
        issues.extend(
            _array_of_unique_strings(
                entry.get("possible_results"),
                f"{path}.possible_results",
                allow_empty=False,
            )
        )

        possible_results = entry.get("possible_results")
        if isinstance(possible_results, list) and set(possible_results) != POSSIBLE_RESULTS:
            issues.append(
                _issue(
                    "REG-RESULTS",
                    f"{path}.possible_results",
                    "must contain the complete EAS assessment result vocabulary",
                )
            )

        rule_ids = entry.get("validator_rules")
        if isinstance(rule_ids, list):
            if entry.get("machine_checkable") in {"partial", "full"} and not rule_ids:
                issues.append(
                    _issue(
                        "REG-CHECKABILITY",
                        f"{path}.validator_rules",
                        "machine-checkable requirement must have a validator rule",
                    )
                )
            if entry.get("machine_checkable") == "none" and rule_ids:
                issues.append(
                    _issue(
                        "REG-CHECKABILITY",
                        f"{path}.validator_rules",
                        "unobservable requirement must not claim a validator rule",
                    )
                )
            for rule_id in rule_ids:
                if isinstance(rule_id, str):
                    declared_rule_links.add((requirement_id, rule_id))
                    if rule_id not in rules:
                        issues.append(
                            _issue(
                                "REG-REFERENCE",
                                f"{path}.validator_rules",
                                f"unknown validator rule {rule_id}",
                            )
                        )

        scenario_ids = entry.get("scenarios")
        if isinstance(scenario_ids, list):
            for scenario_id in scenario_ids:
                if scenario_id not in scenarios:
                    issues.append(
                        _issue(
                            "REG-REFERENCE",
                            f"{path}.scenarios",
                            f"unknown scenario {scenario_id}",
                        )
                    )
                elif requirement_id not in scenarios[scenario_id]:
                    issues.append(
                        _issue(
                            "REG-TRACEABILITY",
                            f"{path}.scenarios",
                            f"{scenario_id} does not reference {requirement_id}",
                        )
                    )

    reverse_rule_links: set[tuple[str, str]] = set()
    for rule_id, entry in rules.items():
        path = f"$.rules[{rule_id}]"
        missing_fields = sorted(RULE_FIELDS - entry.keys())
        for field in missing_fields:
            issues.append(_issue("REG-FIELD", f"{path}.{field}", "required field is missing"))
        if not isinstance(entry.get("title"), str) or not entry.get("title", "").strip():
            issues.append(_issue("REG-TYPE", f"{path}.title", "must be a non-empty string"))
        if entry.get("assessment_level") not in ASSESSMENT_LEVELS:
            issues.append(
                _issue(
                    "REG-VALUE",
                    f"{path}.assessment_level",
                    "must be schema, structural, or behavioral",
                )
            )
        for field, allow_empty in (
            ("requirements", False),
            ("implementation", False),
            ("tests", False),
            ("observable_inputs", False),
        ):
            issues.extend(
                _array_of_unique_strings(
                    entry.get(field), f"{path}.{field}", allow_empty=allow_empty
                )
            )
        requirement_ids = entry.get("requirements")
        if isinstance(requirement_ids, list):
            for requirement_id in requirement_ids:
                if not isinstance(requirement_id, str):
                    continue
                reverse_rule_links.add((requirement_id, rule_id))
                if requirement_id not in requirements:
                    issues.append(
                        _issue(
                            "REG-REFERENCE",
                            f"{path}.requirements",
                            f"unknown requirement {requirement_id}",
                        )
                    )
        for field in ("implementation", "tests"):
            references = entry.get(field)
            if isinstance(references, list):
                for index, reference in enumerate(references):
                    issues.extend(
                        _validate_artifact_reference(
                            root, reference, f"{path}.{field}[{index}]"
                        )
                    )

    for link in sorted(declared_rule_links - reverse_rule_links):
        issues.append(
            _issue(
                "REG-TRACEABILITY",
                "$.requirements",
                f"validator rule {link[1]} does not link back to {link[0]}",
            )
        )
    for link in sorted(reverse_rule_links - declared_rule_links):
        issues.append(
            _issue(
                "REG-TRACEABILITY",
                "$.rules",
                f"requirement {link[0]} does not link back to {link[1]}",
            )
        )

    for scenario_id, references in scenarios.items():
        for requirement_id in sorted(references):
            if requirement_id not in requirements:
                issues.append(
                    _issue(
                        "REG-REFERENCE",
                        f"$scenario[{scenario_id}].requirement_refs",
                        f"unknown requirement {requirement_id}",
                    )
                )
            elif scenario_id not in requirements[requirement_id].get("scenarios", []):
                issues.append(
                    _issue(
                        "REG-TRACEABILITY",
                        f"$scenario[{scenario_id}].requirement_refs",
                        f"registry does not link {requirement_id} back to {scenario_id}",
                    )
                )

    return issues


def build_coverage(requirement_registry: Any, rule_registry: Any) -> dict[str, Any]:
    """Build a deterministic coverage data structure from valid registries."""

    requirements = requirement_registry.get("requirements", [])
    rules = rule_registry.get("rules", [])
    rule_levels = {
        rule["id"]: rule["assessment_level"]
        for rule in rules
        if isinstance(rule, dict)
        and isinstance(rule.get("id"), str)
        and isinstance(rule.get("assessment_level"), str)
    }

    level_counts = {level: 0 for level in sorted(LEVELS)}
    checkability_counts = {value: 0 for value in sorted(MACHINE_CHECKABILITY)}
    by_spec: dict[str, int] = {}
    structurally_checked: list[str] = []
    behaviorally_checked: list[str] = []
    covered_by_scenarios: list[str] = []
    details: list[dict[str, Any]] = []
    requirement_subjects = resolve_requirement_subjects(requirement_registry)

    for requirement in sorted(requirements, key=lambda item: item.get("id", "")):
        requirement_id = requirement.get("id")
        if not isinstance(requirement_id, str):
            continue
        level = requirement.get("level")
        if level in level_counts:
            level_counts[level] += 1
        checkability = requirement.get("machine_checkable")
        if checkability in checkability_counts:
            checkability_counts[checkability] += 1
        spec = requirement.get("spec")
        if isinstance(spec, str):
            by_spec[spec] = by_spec.get(spec, 0) + 1

        validator_rules = requirement.get("validator_rules", [])
        assessment_levels = sorted(
            {
                rule_levels[rule_id]
                for rule_id in validator_rules
                if rule_id in rule_levels
            }
        )
        if any(level_name in {"schema", "structural"} for level_name in assessment_levels):
            structurally_checked.append(requirement_id)
        if "behavioral" in assessment_levels:
            behaviorally_checked.append(requirement_id)
        scenarios = requirement.get("scenarios", [])
        if scenarios:
            covered_by_scenarios.append(requirement_id)
        details.append(
            {
                "id": requirement_id,
                "assessment_subjects": sorted(
                    requirement_subjects.get(requirement_id, frozenset())
                ),
                "machine_checkable": checkability,
                "assessment_levels": assessment_levels,
                "validator_rules": list(validator_rules),
                "scenarios": list(scenarios),
            }
        )

    all_ids = [item["id"] for item in details]
    rule_covered = sorted(item["id"] for item in details if item["validator_rules"])
    scenario_covered = sorted(covered_by_scenarios)
    return {
        "eas_version": requirement_registry.get("eas_version"),
        "registry_version": requirement_registry.get("registry_version"),
        "summary": {
            "total_requirements": len(details),
            "by_level": level_counts,
            "by_spec": dict(sorted(by_spec.items())),
            "machine_checkable": checkability_counts,
            "with_validator_rules": len(rule_covered),
            "structurally_machine_checkable": len(structurally_checked),
            "behaviorally_assessable": len(behaviorally_checked),
            "currently_unobservable": checkability_counts["none"],
            "covered_by_scenarios": len(scenario_covered),
        },
        "requirements": details,
        "uncovered": {
            "validator_rules": sorted(set(all_ids) - set(rule_covered)),
            "scenarios": sorted(set(all_ids) - set(scenario_covered)),
        },
    }
