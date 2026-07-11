"""Dependency-free checks for the experimental EAS 0.1 run-record format."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


STATES = {
    "RECEIVED",
    "UNDERSTANDING",
    "PLANNING",
    "EXECUTING",
    "VERIFYING",
    "REVIEWING",
    "REPORTING",
    "ESCALATED",
    "BLOCKED",
    "COMPLETED",
}

TRANSITIONS = {
    "RECEIVED": {"UNDERSTANDING", "ESCALATED", "BLOCKED"},
    "UNDERSTANDING": {"PLANNING", "REPORTING", "ESCALATED", "BLOCKED"},
    "PLANNING": {
        "EXECUTING",
        "VERIFYING",
        "REPORTING",
        "ESCALATED",
        "BLOCKED",
    },
    "EXECUTING": {
        "UNDERSTANDING",
        "PLANNING",
        "VERIFYING",
        "ESCALATED",
        "BLOCKED",
    },
    "VERIFYING": {
        "UNDERSTANDING",
        "PLANNING",
        "EXECUTING",
        "REVIEWING",
        "ESCALATED",
        "BLOCKED",
    },
    "REVIEWING": {
        "PLANNING",
        "EXECUTING",
        "VERIFYING",
        "REPORTING",
        "ESCALATED",
        "BLOCKED",
    },
    "REPORTING": {"COMPLETED"},
    "ESCALATED": set(),
    "BLOCKED": set(),
    "COMPLETED": set(),
}

TERMINAL_BY_OUTCOME = {
    "completed": "COMPLETED",
    "escalated": "ESCALATED",
    "blocked": "BLOCKED",
}

TASK_CLASSES = {"change", "diagnose", "review", "research", "operate", "advise"}
DISPOSITIONS = {"inspect", "proceed", "escalate", "block", "refuse"}

REQUIRED_TOP_LEVEL = {
    "eas_version",
    "conformance_class",
    "run_id",
    "task",
    "initial_state",
    "constraints",
    "state_history",
    "actions",
    "decisions",
    "evidence",
    "final_state",
    "outcome",
    "report",
}


@dataclass(frozen=True)
class ValidationIssue:
    """One structural conformance failure."""

    requirement: str
    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.requirement} at {self.path}: {self.message}"


def _issue(requirement: str, path: str, message: str) -> ValidationIssue:
    return ValidationIssue(requirement, path, message)


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _check_required(record: dict[str, Any]) -> list[ValidationIssue]:
    return [
        _issue("EAS-002-R01", f"$.{name}", "required field is missing")
        for name in sorted(REQUIRED_TOP_LEVEL - record.keys())
    ]


def _check_string_array(value: Any, path: str, requirement: str) -> list[ValidationIssue]:
    if not isinstance(value, list):
        return [_issue(requirement, path, "must be an array")]
    return [
        _issue(requirement, f"{path}[{index}]", "must be a non-empty string")
        for index, item in enumerate(value)
        if not _is_non_empty_string(item)
    ]


def _check_object_fields(
    value: Any,
    path: str,
    required: set[str],
    requirement: str,
) -> list[ValidationIssue]:
    if not isinstance(value, dict):
        return [_issue(requirement, path, "must be an object")]
    return [
        _issue(requirement, f"{path}.{name}", "required field is missing")
        for name in sorted(required - value.keys())
    ]


def _check_record_shape(record: dict[str, Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    task = record.get("task")
    issues.extend(
        _check_object_fields(
            task,
            "$.task",
            {"description", "primary_class", "acceptance_criteria"},
            "EAS-002-R01",
        )
    )
    if isinstance(task, dict):
        if "description" in task and not _is_non_empty_string(task.get("description")):
            issues.append(_issue("EAS-002-R01", "$.task.description", "must be a non-empty string"))
        if "primary_class" in task and task.get("primary_class") not in TASK_CLASSES:
            issues.append(
                _issue("EAS-002-R07", "$.task.primary_class", "must be a recognized task class")
            )
        if "acceptance_criteria" in task:
            issues.extend(
                _check_string_array(
                    task.get("acceptance_criteria"),
                    "$.task.acceptance_criteria",
                    "EAS-002-R01",
                )
            )

    for name in ("initial_state", "final_state"):
        state = record.get(name)
        path = f"$.{name}"
        issues.extend(
            _check_object_fields(state, path, {"summary", "revision"}, "EAS-002-R01")
        )
        if isinstance(state, dict):
            for field in ("summary", "revision"):
                if field in state and not _is_non_empty_string(state.get(field)):
                    issues.append(
                        _issue("EAS-002-R01", f"{path}.{field}", "must be a non-empty string")
                    )

    issues.extend(_check_string_array(record.get("constraints"), "$.constraints", "EAS-002-R01"))
    if "assumptions" in record:
        issues.extend(_check_string_array(record.get("assumptions"), "$.assumptions", "EAS-003-R02"))

    report = record.get("report")
    issues.extend(
        _check_object_fields(
            report,
            "$.report",
            {"summary", "changes", "verification", "limitations", "unresolved"},
            "EAS-007-R05",
        )
    )
    if isinstance(report, dict):
        if "summary" in report and not _is_non_empty_string(report.get("summary")):
            issues.append(_issue("EAS-007-R05", "$.report.summary", "must be a non-empty string"))
        for field in ("changes", "limitations", "unresolved"):
            if field in report:
                issues.extend(
                    _check_string_array(report.get(field), f"$.report.{field}", "EAS-007-R05")
                )

    return issues


def _ids(items: Any, path: str, requirement: str) -> tuple[set[str], list[ValidationIssue]]:
    if not isinstance(items, list):
        return set(), [_issue(requirement, path, "must be an array")]
    found: set[str] = set()
    issues: list[ValidationIssue] = []
    for index, item in enumerate(items):
        item_path = f"{path}[{index}]"
        if not isinstance(item, dict) or not _is_non_empty_string(item.get("id")):
            issues.append(_issue(requirement, f"{item_path}.id", "must be a non-empty string"))
            continue
        item_id = item["id"]
        if item_id in found:
            issues.append(_issue(requirement, f"{item_path}.id", f"duplicate id {item_id!r}"))
        found.add(item_id)
    return found, issues


def validate_record(record: Any) -> list[ValidationIssue]:
    """Return all detectable EAS 0.1 structural issues in *record*.

    A clean result demonstrates only experimental structural conformance. It
    does not establish behavioral conformance.
    """

    if not isinstance(record, dict):
        return [_issue("EAS-009-R02", "$", "run record must be an object")]

    issues = _check_required(record)
    if issues:
        return issues
    issues.extend(_check_record_shape(record))

    if record.get("eas_version") != "0.1":
        issues.append(_issue("EAS-000-R01", "$.eas_version", "must equal '0.1'"))
    if record.get("conformance_class") != "structural":
        issues.append(
            _issue("EAS-009-R01", "$.conformance_class", "must equal 'structural'")
        )
    if not _is_non_empty_string(record.get("run_id")):
        issues.append(_issue("EAS-002-R01", "$.run_id", "must be a non-empty string"))

    history = record.get("state_history")
    if not isinstance(history, list) or len(history) < 2:
        issues.append(_issue("EAS-004-R01", "$.state_history", "must contain at least two states"))
    else:
        unknown = [(index, state) for index, state in enumerate(history) if state not in STATES]
        for index, state in unknown:
            issues.append(_issue("EAS-004-R02", f"$.state_history[{index}]", f"unknown state {state!r}"))
        if history[0] != "RECEIVED":
            issues.append(_issue("EAS-004-R01", "$.state_history[0]", "must be RECEIVED"))
        for index, (source, target) in enumerate(zip(history, history[1:])):
            if source in STATES and target in STATES and target not in TRANSITIONS[source]:
                issues.append(
                    _issue(
                        "EAS-004-R02",
                        f"$.state_history[{index + 1}]",
                        f"transition {source} -> {target} is not permitted",
                    )
                )
        expected = TERMINAL_BY_OUTCOME.get(record.get("outcome"))
        if expected is None:
            issues.append(_issue("EAS-004-R06", "$.outcome", "unknown outcome"))
        elif history[-1] != expected:
            issues.append(
                _issue("EAS-004-R06", "$.state_history", f"outcome requires terminal state {expected}")
            )

    evidence_ids, id_issues = _ids(record.get("evidence"), "$.evidence", "EAS-008-R01")
    issues.extend(id_issues)
    decision_ids, id_issues = _ids(record.get("decisions"), "$.decisions", "EAS-005-R02")
    issues.extend(id_issues)
    _, id_issues = _ids(record.get("actions"), "$.actions", "EAS-002-R01")
    issues.extend(id_issues)

    decisions = record.get("decisions")
    if isinstance(decisions, list):
        for index, decision in enumerate(decisions):
            if not isinstance(decision, dict):
                continue
            if decision.get("disposition") not in DISPOSITIONS:
                issues.append(
                    _issue(
                        "EAS-005-R02",
                        f"$.decisions[{index}].disposition",
                        "must be inspect, proceed, escalate, block, or refuse",
                    )
                )

    for collection in ("evidence", "decisions", "actions"):
        items = record.get(collection)
        if not isinstance(items, list):
            continue
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                issues.append(_issue("EAS-009-R02", f"$.{collection}[{index}]", "must be an object"))
                continue
            refs = item.get("evidence_refs", [])
            if not isinstance(refs, list):
                issues.append(_issue("EAS-008-R02", f"$.{collection}[{index}].evidence_refs", "must be an array"))
                continue
            for ref_index, ref in enumerate(refs):
                if ref not in evidence_ids:
                    issues.append(
                        _issue(
                            "EAS-008-R02",
                            f"$.{collection}[{index}].evidence_refs[{ref_index}]",
                            f"unresolved evidence id {ref!r}",
                        )
                    )

    actions = record.get("actions")
    if isinstance(actions, list):
        for index, action in enumerate(actions):
            if not isinstance(action, dict) or not action.get("material"):
                continue
            if action.get("authority") != "authorized":
                issues.append(
                    _issue("EAS-005-R04", f"$.actions[{index}].authority", "a performed material action must be authorized")
                )
            decision_id = action.get("decision_id")
            if decision_id not in decision_ids:
                issues.append(
                    _issue("EAS-005-R02", f"$.actions[{index}].decision_id", "material action must reference a decision")
                )

    evidence_by_id = {
        item.get("id"): item
        for item in record.get("evidence", [])
        if isinstance(item, dict) and _is_non_empty_string(item.get("id"))
    }
    report = record.get("report")
    if not isinstance(report, dict):
        issues.append(_issue("EAS-007-R05", "$.report", "must be an object"))
    else:
        verification = report.get("verification")
        if not isinstance(verification, list):
            issues.append(_issue("EAS-007-R05", "$.report.verification", "must be an array"))
        else:
            for index, claim in enumerate(verification):
                if not isinstance(claim, dict):
                    issues.append(_issue("EAS-006-R02", f"$.report.verification[{index}]", "must be an object"))
                    continue
                refs = claim.get("evidence_refs", [])
                if not isinstance(refs, list):
                    issues.append(_issue("EAS-008-R02", f"$.report.verification[{index}].evidence_refs", "must be an array"))
                    continue
                for ref_index, ref in enumerate(refs):
                    if ref not in evidence_ids:
                        issues.append(
                            _issue("EAS-008-R02", f"$.report.verification[{index}].evidence_refs[{ref_index}]", f"unresolved evidence id {ref!r}")
                        )
                if claim.get("status") == "passed":
                    if not refs or any(evidence_by_id.get(ref, {}).get("result") != "passed" for ref in refs):
                        issues.append(
                            _issue("EAS-006-R03", f"$.report.verification[{index}]", "passed claim requires passed evidence")
                        )

    return issues
