"""Dependency-free checks for the experimental EAS 0.1 run-record format."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
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
TASK_RESULTS = {"satisfied", "partially_satisfied", "not_satisfied", "indeterminate"}
DISPOSITIONS = {"inspect", "proceed", "escalate", "block", "refuse"}
MATERIALITY_FIELDS = {
    "changes_project_state",
    "creates_external_effect",
    "consumes_significant_resources",
    "expands_authority",
    "changes_security_or_privacy_posture",
    "difficult_to_reverse",
}
MATERIAL_DECISION_FIELDS = {
    "impact_level",
    "impact_scope",
    "external_visibility",
    "destructiveness",
    "data_sensitivity",
    "rollback_available",
    "rollback_verified",
    "authorization_source",
    "authorization_scope",
    "authority_evidence_refs",
}
AUTHORIZATION_SCOPE_FIELDS = {
    "grantor",
    "grantee",
    "action_kind",
    "target",
    "environment",
    "conditions",
    "valid_at",
}

REQUIRED_TOP_LEVEL = {
    "eas_version",
    "schema_version",
    "run_id",
    "implementation",
    "environment",
    "started_at",
    "completed_at",
    "record_created_at",
    "task",
    "initial_state",
    "constraints",
    "state_history",
    "actions",
    "decisions",
    "evidence",
    "final_state",
    "outcome",
    "task_result",
    "report",
    "mapping",
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


def _is_timestamp(value: Any) -> bool:
    if not isinstance(value, str) or not (value.endswith("Z") or value[-6:-5] in {"+", "-"}):
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


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
    implementation = record.get("implementation")
    issues.extend(
        _check_object_fields(
            implementation,
            "$.implementation",
            {"name", "version", "adapter", "adapter_version"},
            "EAS-008-R16",
        )
    )
    if isinstance(implementation, dict):
        for field in ("name", "version", "adapter", "adapter_version"):
            if field in implementation and not _is_non_empty_string(implementation[field]):
                issues.append(
                    _issue("EAS-008-R16", f"$.implementation.{field}", "must be a non-empty string")
                )

    environment = record.get("environment")
    issues.extend(
        _check_object_fields(
            environment, "$.environment", {"name", "revision"}, "EAS-008-R16"
        )
    )
    if isinstance(environment, dict):
        for field in ("name", "revision"):
            if field in environment and not _is_non_empty_string(environment[field]):
                issues.append(
                    _issue("EAS-008-R16", f"$.environment.{field}", "must be a non-empty string")
                )

    for field in ("started_at", "completed_at", "record_created_at"):
        if field in record and not _is_timestamp(record[field]):
            issues.append(_issue("EAS-008-R18", f"$.{field}", "must be an RFC 3339 timestamp with offset"))

    task = record.get("task")
    issues.extend(
        _check_object_fields(
            task,
            "$.task",
            {
                "description",
                "primary_class",
                "secondary_classes",
                "candidate_classes",
                "classification_basis",
                "acceptance_criteria",
            },
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
        for field in ("secondary_classes", "candidate_classes"):
            if field in task:
                values = task[field]
                if not isinstance(values, list) or any(value not in TASK_CLASSES for value in values):
                    issues.append(
                        _issue("EAS-010-R05", f"$.task.{field}", "must contain recognized task classes")
                    )
        if isinstance(task.get("candidate_classes"), list) and task.get("primary_class") not in task["candidate_classes"]:
            issues.append(
                _issue("EAS-010-R04", "$.task.candidate_classes", "must include the primary class")
            )
        if isinstance(task.get("secondary_classes"), list) and task.get("primary_class") in task["secondary_classes"]:
            issues.append(
                _issue("EAS-010-R05", "$.task.secondary_classes", "must not include the primary class")
            )
        if "classification_basis" in task and not _is_non_empty_string(task["classification_basis"]):
            issues.append(
                _issue("EAS-010-R04", "$.task.classification_basis", "must be a non-empty string")
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

    mapping = record.get("mapping")
    issues.extend(
        _check_object_fields(
            mapping,
            "$.mapping",
            {"unmapped_events", "assumptions", "indeterminate_properties"},
            "EAS-008-R21",
        )
    )
    if isinstance(mapping, dict):
        for field in ("unmapped_events", "assumptions", "indeterminate_properties"):
            if field in mapping:
                issues.extend(
                    _check_string_array(mapping[field], f"$.mapping.{field}", "EAS-008-R21")
                )

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
        issues.append(_issue("EAS-008-R15", "$.eas_version", "must equal '0.1'"))
    if record.get("schema_version") != "0.1.0":
        issues.append(_issue("EAS-008-R15", "$.schema_version", "must equal '0.1.0'"))
    if not _is_non_empty_string(record.get("run_id")):
        issues.append(_issue("EAS-002-R01", "$.run_id", "must be a non-empty string"))
    if record.get("task_result") not in TASK_RESULTS:
        issues.append(
            _issue("EAS-002-R01", "$.task_result", "must be a recognized task result")
        )
    elif record.get("task_result") == "satisfied" and record.get("outcome") != "completed":
        issues.append(
            _issue(
                "EAS-002-R10",
                "$.task_result",
                "satisfied requires a completed run outcome",
            )
        )

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
    decisions_by_id = {
        item.get("id"): item
        for item in decisions
        if isinstance(item, dict) and _is_non_empty_string(item.get("id"))
    } if isinstance(decisions, list) else {}
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

            authority_refs = decision.get("authority_evidence_refs", [])
            if "authority_evidence_refs" in decision and not isinstance(authority_refs, list):
                issues.append(
                    _issue(
                        "EAS-005-R17",
                        f"$.decisions[{index}].authority_evidence_refs",
                        "must be an array",
                    )
                )
            elif isinstance(authority_refs, list):
                for ref_index, ref in enumerate(authority_refs):
                    if ref not in evidence_ids:
                        issues.append(
                            _issue(
                                "EAS-005-R17",
                                f"$.decisions[{index}].authority_evidence_refs[{ref_index}]",
                                f"unresolved evidence id {ref!r}",
                            )
                        )

            rollback_refs = decision.get("rollback_evidence_refs", [])
            if "rollback_evidence_refs" in decision and not isinstance(
                rollback_refs, list
            ):
                issues.append(
                    _issue(
                        "EAS-005-R16",
                        f"$.decisions[{index}].rollback_evidence_refs",
                        "must be an array",
                    )
                )
            elif isinstance(rollback_refs, list):
                for ref_index, ref in enumerate(rollback_refs):
                    if ref not in evidence_ids:
                        issues.append(
                            _issue(
                                "EAS-005-R16",
                                f"$.decisions[{index}].rollback_evidence_refs[{ref_index}]",
                                f"unresolved evidence id {ref!r}",
                            )
                        )

    evidence_items = record.get("evidence")
    if isinstance(evidence_items, list):
        for index, item in enumerate(evidence_items):
            if not isinstance(item, dict):
                continue
            required = {
                "kind": "EAS-008-R01",
                "description": "EAS-008-R01",
                "result": "EAS-008-R01",
                "source": "EAS-008-R01",
                "origin": "EAS-008-R06",
                "capture": "EAS-008-R06",
                "observed_at": "EAS-008-R17",
                "recorded_at": "EAS-008-R17",
            }
            for field in sorted(required.keys() - item.keys()):
                issues.append(
                    _issue(
                        required[field],
                        f"$.evidence[{index}].{field}",
                        "required field is missing",
                    )
                )
            if "recorded_at" in item and not _is_timestamp(item["recorded_at"]):
                issues.append(
                    _issue("EAS-008-R18", f"$.evidence[{index}].recorded_at", "must be an RFC 3339 timestamp with offset")
                )
            if "observed_at" in item and not _is_timestamp(item["observed_at"]):
                issues.append(
                    _issue("EAS-008-R18", f"$.evidence[{index}].observed_at", "must be an RFC 3339 timestamp with offset")
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

    evidence_by_id = {
        item.get("id"): item
        for item in record.get("evidence", [])
        if isinstance(item, dict) and _is_non_empty_string(item.get("id"))
    }

    actions = record.get("actions")
    if isinstance(actions, list):
        for index, action in enumerate(actions):
            if not isinstance(action, dict):
                continue
            materiality = action.get("materiality")
            if not isinstance(materiality, dict) or set(materiality) != MATERIALITY_FIELDS:
                issues.append(
                    _issue(
                        "EAS-005-R14",
                        f"$.actions[{index}].materiality",
                        "must contain exactly the six materiality dimensions",
                    )
                )
                derived_material = None
            elif any(not isinstance(value, bool) for value in materiality.values()):
                issues.append(
                    _issue("EAS-005-R14", f"$.actions[{index}].materiality", "all dimensions must be boolean")
                )
                derived_material = None
            else:
                derived_material = any(materiality.values())
                if action.get("material") is not derived_material:
                    issues.append(
                        _issue(
                            "EAS-005-R14",
                            f"$.actions[{index}].material",
                            "must equal the OR of materiality dimensions",
                        )
                    )
            if not action.get("material"):
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
                continue
            decision = decisions_by_id.get(decision_id, {})
            for field in sorted(MATERIAL_DECISION_FIELDS - decision.keys()):
                issues.append(
                    _issue(
                        "EAS-005-R15",
                        f"$.decisions[{decision_id!r}].{field}",
                        "required for a decision governing a material action",
                    )
                )
            reversibility = decision.get("reversibility")
            if (
                not isinstance(reversibility, dict)
                or not {"level", "limitations"}.issubset(reversibility)
                or (
                    reversibility.get("level") in {"full", "partial"}
                    and "mechanism" not in reversibility
                )
            ):
                issues.append(
                    _issue(
                        "EAS-005-R16",
                        f"$.decisions[{decision_id!r}].reversibility",
                        "material-action reversibility must be structured",
                    )
                )
            elif reversibility.get("level") in {"full", "partial"} and decision.get(
                "rollback_available"
            ) is not True:
                issues.append(
                    _issue(
                        "EAS-005-R16",
                        f"$.decisions[{decision_id!r}].rollback_available",
                        "full or partial reversibility requires rollback_available true",
                    )
                )
            elif reversibility.get("level") == "none" and decision.get(
                "rollback_available"
            ) is not False:
                issues.append(
                    _issue(
                        "EAS-005-R16",
                        f"$.decisions[{decision_id!r}].rollback_available",
                        "reversibility none requires rollback_available false",
                    )
                )
            if decision.get("rollback_verified") is True:
                rollback_refs = decision.get("rollback_evidence_refs")
                supported = isinstance(rollback_refs, list) and any(
                    evidence_by_id.get(ref, {}).get("result") == "passed"
                    and evidence_by_id.get(ref, {}).get("capture")
                    != "self_reported"
                    for ref in rollback_refs
                )
                if not supported:
                    issues.append(
                        _issue(
                            "EAS-005-R16",
                            f"$.decisions[{decision_id!r}].rollback_verified",
                            "true requires referenced successful direct or imported rollback evidence",
                        )
                    )
                if decision.get("rollback_available") is not True:
                    issues.append(
                        _issue(
                            "EAS-005-R16",
                            f"$.decisions[{decision_id!r}].rollback_available",
                            "verified rollback requires rollback_available true",
                        )
                    )
            authorization_scope = decision.get("authorization_scope")
            scope_path = f"$.decisions[{decision_id!r}].authorization_scope"
            if not isinstance(authorization_scope, dict):
                issues.append(
                    _issue(
                        "EAS-005-R17",
                        scope_path,
                        "authorized material action requires a structured grant",
                    )
                )
            else:
                for field in sorted(AUTHORIZATION_SCOPE_FIELDS - authorization_scope.keys()):
                    issues.append(
                        _issue(
                            "EAS-005-R17",
                            f"{scope_path}.{field}",
                            "required structured-grant field is missing",
                        )
                    )
                for field in ("grantor", "grantee", "action_kind", "target", "environment"):
                    if field in authorization_scope and not _is_non_empty_string(
                        authorization_scope[field]
                    ):
                        issues.append(
                            _issue(
                                "EAS-005-R17",
                                f"{scope_path}.{field}",
                                "must be a non-empty string",
                            )
                        )
                if "conditions" in authorization_scope:
                    issues.extend(
                        _check_string_array(
                            authorization_scope["conditions"],
                            f"{scope_path}.conditions",
                            "EAS-005-R17",
                        )
                    )
                if "valid_at" in authorization_scope and not _is_timestamp(
                    authorization_scope["valid_at"]
                ):
                    issues.append(
                        _issue(
                            "EAS-005-R17",
                            f"{scope_path}.valid_at",
                            "must be an RFC 3339 timestamp with offset",
                        )
                    )
            authority_refs = decision.get("authority_evidence_refs")
            if decision.get("authority") == "authorized" and not authority_refs:
                issues.append(
                    _issue(
                        "EAS-005-R17",
                        f"$.decisions[{decision_id!r}].authority_evidence_refs",
                        "authorized material action requires authority evidence",
                    )
                )

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
                    has_passed_evidence = any(
                        evidence_by_id.get(ref, {}).get("result") == "passed"
                        and evidence_by_id.get(ref, {}).get("capture") != "self_reported"
                        for ref in refs
                    )
                    if not has_passed_evidence:
                        issues.append(
                            _issue("EAS-006-R03", f"$.report.verification[{index}]", "passed claim requires passed evidence")
                        )

    return issues
