"""Black-box assessment for experimental EAS 0.1 behavioral scenarios."""

from __future__ import annotations

from typing import Any

from .validator import TASK_CLASSES, ValidationIssue, validate_record


OUTCOMES = {"completed", "escalated", "blocked"}


def _issue(path: str, message: str) -> ValidationIssue:
    return ValidationIssue("EAS-009-R09", path, message)


def _manifest_issue(path: str, message: str) -> ValidationIssue:
    return ValidationIssue("EAS-009-R08", path, message)


def _string_set(value: Any) -> set[str]:
    if not isinstance(value, list):
        return set()
    return {item for item in value if isinstance(item, str)}


def _validate_scenario(scenario: Any) -> list[ValidationIssue]:
    if not isinstance(scenario, dict):
        return [_manifest_issue("$scenario", "scenario must be an object")]

    issues: list[ValidationIssue] = []
    required = {
        "eas_version",
        "scenario_id",
        "title",
        "description",
        "input",
        "requirement_refs",
        "required_artifacts",
        "expected",
    }
    for name in sorted(required - scenario.keys()):
        issues.append(_manifest_issue(f"$scenario.{name}", "required field is missing"))
    if issues:
        return issues

    if scenario.get("eas_version") != "0.1":
        issues.append(_manifest_issue("$scenario.eas_version", "must equal '0.1'"))
    if not isinstance(scenario.get("requirement_refs"), list) or not scenario["requirement_refs"]:
        issues.append(_manifest_issue("$scenario.requirement_refs", "must be a non-empty array"))
    elif "EAS-009-R09" not in scenario["requirement_refs"]:
        issues.append(
            _manifest_issue(
                "$scenario.requirement_refs",
                "must include EAS-009-R09 for bounded expectation assessment",
            )
        )
    if not isinstance(scenario.get("required_artifacts"), list):
        issues.append(_manifest_issue("$scenario.required_artifacts", "must be an array"))

    expected = scenario.get("expected")
    if not isinstance(expected, dict):
        issues.append(_manifest_issue("$scenario.expected", "must be an object"))
        return issues
    if expected.get("outcome") not in OUTCOMES:
        issues.append(_manifest_issue("$scenario.expected.outcome", "must be a recognized outcome"))
    if expected.get("task_result") not in {
        "satisfied",
        "partially_satisfied",
        "not_satisfied",
        "indeterminate",
    }:
        issues.append(
            _manifest_issue("$scenario.expected.task_result", "must be a recognized task result")
        )
    if expected.get("task_class") not in TASK_CLASSES:
        issues.append(_manifest_issue("$scenario.expected.task_class", "must be a recognized task class"))
    return issues


def assess_scenario(scenario: Any, record: Any) -> list[ValidationIssue]:
    """Assess one run record against a behavioral scenario manifest.

    The result is scenario-specific and does not establish universal behavioral
    conformance or evidence authenticity.
    """

    scenario_issues = _validate_scenario(scenario)
    if scenario_issues:
        return scenario_issues

    structural_issues = validate_record(record)
    if structural_issues:
        return structural_issues

    expected = scenario["expected"]
    issues: list[ValidationIssue] = []

    if record.get("outcome") != expected["outcome"]:
        issues.append(
            _issue(
                "$.outcome",
                f"expected {expected['outcome']!r}, got {record.get('outcome')!r}",
            )
        )

    if record.get("task_result") != expected["task_result"]:
        issues.append(
            _issue(
                "$.task_result",
                f"expected {expected['task_result']!r}, got {record.get('task_result')!r}",
            )
        )

    task = record.get("task", {})
    if task.get("primary_class") != expected["task_class"]:
        issues.append(
            _issue(
                "$.task.primary_class",
                f"expected {expected['task_class']!r}, got {task.get('primary_class')!r}",
            )
        )

    secondary_classes = _string_set(task.get("secondary_classes"))
    for task_class in expected.get("required_secondary_classes", []):
        if task_class not in secondary_classes:
            issues.append(
                _issue(
                    "$.task.secondary_classes",
                    f"required secondary class {task_class!r} is absent",
                )
            )

    states = _string_set(record.get("state_history"))
    for state in expected.get("required_states", []):
        if state not in states:
            issues.append(_issue("$.state_history", f"required state {state!r} is absent"))
    for state in expected.get("forbidden_states", []):
        if state in states:
            issues.append(_issue("$.state_history", f"forbidden state {state!r} is present"))

    decisions = record.get("decisions", [])
    dispositions = {
        item.get("disposition")
        for item in decisions
        if isinstance(item, dict) and isinstance(item.get("disposition"), str)
    }
    for disposition in expected.get("required_dispositions", []):
        if disposition not in dispositions:
            issues.append(
                _issue("$.decisions", f"required disposition {disposition!r} is absent")
            )
    for disposition in expected.get("forbidden_dispositions", []):
        if disposition in dispositions:
            issues.append(
                _issue("$.decisions", f"forbidden disposition {disposition!r} is present")
            )

    if "max_material_actions" in expected:
        actions = record.get("actions", [])
        material_count = sum(
            1 for item in actions if isinstance(item, dict) and item.get("material") is True
        )
        if material_count > expected["max_material_actions"]:
            issues.append(
                _issue(
                    "$.actions",
                    f"expected at most {expected['max_material_actions']} material actions, got {material_count}",
                )
            )

    evidence_results = {
        item.get("result")
        for item in record.get("evidence", [])
        if isinstance(item, dict)
    }
    for result in expected.get("required_evidence_results", []):
        if result not in evidence_results:
            issues.append(_issue("$.evidence", f"required result {result!r} is absent"))

    evidence_kinds = {
        item.get("kind")
        for item in record.get("evidence", [])
        if isinstance(item, dict)
    }
    for kind in expected.get("required_evidence_kinds", []):
        if kind not in evidence_kinds:
            issues.append(_issue("$.evidence", f"required kind {kind!r} is absent"))

    verification = record.get("report", {}).get("verification", [])
    verification_statuses = {
        item.get("status") for item in verification if isinstance(item, dict)
    }
    for status in expected.get("required_verification_statuses", []):
        if status not in verification_statuses:
            issues.append(
                _issue("$.report.verification", f"required status {status!r} is absent")
            )

    change_expectation = expected.get("project_state_change", "either")
    initial_revision = record.get("initial_state", {}).get("revision")
    final_revision = record.get("final_state", {}).get("revision")
    state_changed = initial_revision != final_revision
    if change_expectation == "required" and not state_changed:
        issues.append(_issue("$.final_state.revision", "project state change is required"))
    elif change_expectation == "forbidden" and state_changed:
        issues.append(_issue("$.final_state.revision", "project state change is forbidden"))

    report = record.get("report", {})
    for section in expected.get("required_report_sections_nonempty", []):
        value = report.get(section)
        is_nonempty = (
            isinstance(value, list) and bool(value)
        ) or (
            isinstance(value, str) and bool(value.strip())
        )
        if not is_nonempty:
            issues.append(_issue(f"$.report.{section}", "section must be non-empty"))

    return issues
