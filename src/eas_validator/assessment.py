"""Versioned assessment records for experimental EAS 0.1 checks.

The source run record and its assessment are deliberately separate artifacts.
This module builds an immutable reference to a source record, derives aggregate
counts, and checks cross-field invariants that JSON Schema cannot express.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
import re
from typing import Any


ASSESSMENT_LEVELS = frozenset({"schema", "structural", "behavioral"})
ASSESSMENT_SUBJECTS = frozenset(
    {
        "run",
        "adapter_mapping",
        "assessment_process",
        "conformance_report",
        "implementation_claim",
        "specification",
    }
)
REQUIREMENT_LEVELS = frozenset({"MUST", "SHOULD", "MAY"})
REQUIREMENT_RESULTS = (
    "pass",
    "fail",
    "indeterminate",
    "not_applicable",
)
APPLICABILITY_DIMENSIONS = (
    "base",
    "task_class",
    "action_or_state",
    "risk_or_event",
    "selected_profile",
)
APPLICABILITY_STATES = frozenset({"invoked", "not_invoked", "indeterminate"})
SUBJECT_MATCH_STATES = frozenset({"matched", "not_matched", "indeterminate"})

SCHEMA_SCOPE_LIMITATION = (
    "Schema validation covers record shape only; it does not establish "
    "structural or behavioral conformance."
)
STRUCTURAL_SCOPE_LIMITATION = (
    "Structural assessment does not establish behavioral conformance."
)
BEHAVIORAL_SCOPE_LIMITATION = (
    "Behavioral assessment is limited to the declared requirements and "
    "observable inputs."
)
SCENARIO_SCOPE_LIMITATION = (
    "Passing the declared scenario set does not establish universal behavioral "
    "conformance beyond that set and EAS version."
)

_REQUIREMENT_ID = re.compile(r"^EAS-[0-9]{3}-R[0-9]{2}$")
_SHA256 = re.compile(r"^[a-f0-9]{64}$")


@dataclass(frozen=True)
class AssessmentIssue:
    """One invalid assessment-record property or cross-field invariant."""

    requirement: str
    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.requirement} at {self.path}: {self.message}"


def _issue(requirement: str, path: str, message: str) -> AssessmentIssue:
    return AssessmentIssue(requirement, path, message)


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    if not (value.endswith("Z") or value[-6:-5] in {"+", "-"}):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def canonical_record_sha256(record: Any) -> str:
    """Return a stable SHA-256 digest of JSON-serializable *record*.

    The digest identifies the exact source content assessed. It is not a
    signature and makes no claim about who produced the source record.
    """

    encoded = json.dumps(
        record,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def aggregate_requirement_results(
    requirement_results: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Derive deterministic counts and the overall assessment result.

    A failed applicable ``MUST`` makes the assessment fail. If no ``MUST``
    fails but an applicable ``MUST`` is indeterminate, the aggregate is
    indeterminate. ``SHOULD`` and ``MAY`` results remain visible in the counts
    but do not independently establish nonconformance.
    """

    counts = {name: 0 for name in REQUIREMENT_RESULTS}
    must_failed = False
    must_indeterminate = False

    for index, item in enumerate(requirement_results):
        if not isinstance(item, Mapping):
            raise ValueError(f"requirement_results[{index}] must be an object")
        result = item.get("result")
        level = item.get("level")
        if result not in counts:
            raise ValueError(
                f"requirement_results[{index}].result is not recognized: {result!r}"
            )
        if level not in REQUIREMENT_LEVELS:
            raise ValueError(
                f"requirement_results[{index}].level is not recognized: {level!r}"
            )
        counts[result] += 1
        if level == "MUST" and result == "fail":
            must_failed = True
        if level == "MUST" and result == "indeterminate":
            must_indeterminate = True

    if must_failed:
        overall = "fail"
    elif must_indeterminate:
        overall = "indeterminate"
    else:
        overall = "pass"

    counts["total"] = len(requirement_results)
    return {"result": overall, "counts": counts}


def _scope_limitation(level: str, scenario_set: Mapping[str, Any] | None) -> str:
    if level == "schema":
        return SCHEMA_SCOPE_LIMITATION
    if level == "structural":
        return STRUCTURAL_SCOPE_LIMITATION
    if scenario_set is not None:
        return SCENARIO_SCOPE_LIMITATION
    return BEHAVIORAL_SCOPE_LIMITATION


def build_assessment_record(
    *,
    assessment_id: str,
    assessment_level: str,
    assessment_subject_type: str = "run",
    assessment_subject_id: str | None = None,
    assessor_name: str,
    assessor_version: str,
    source_record: Mapping[str, Any],
    requirement_results: Iterable[Mapping[str, Any]],
    requirement_subjects: Mapping[str, Iterable[str]],
    requirements_registry_version: str,
    validator_rules_registry_version: str,
    started_at: str,
    completed_at: str,
    record_created_at: str | None = None,
    scenario_set: Mapping[str, Any] | None = None,
    source_artifact_ref: str | None = None,
    limitations: Iterable[str] = (),
    extensions: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a standalone assessment without modifying *source_record*.

    Callers provide explicit per-requirement results. The builder does not
    infer that an unmentioned requirement passed and does not turn a scenario
    pass into a broader behavioral claim.
    """

    if assessment_subject_type not in ASSESSMENT_SUBJECTS:
        raise ValueError(
            f"assessment_subject_type is not recognized: {assessment_subject_type!r}"
        )

    copied_results: list[dict[str, Any]] = []
    for index, item in enumerate(requirement_results):
        if not isinstance(item, Mapping):
            raise ValueError(f"requirement_results[{index}] must be an object")
        copied = deepcopy(dict(item))
        requirement_id = copied.get("requirement_id")
        allowed_subjects = requirement_subjects.get(str(requirement_id))
        if allowed_subjects is None:
            raise ValueError(
                f"requirement_results[{index}] references an unknown requirement: "
                f"{requirement_id!r}"
            )
        if assessment_subject_type not in set(allowed_subjects):
            raise ValueError(
                f"requirement_results[{index}] {requirement_id!r} does not apply "
                f"to assessment subject {assessment_subject_type!r}"
            )
        copied["assessment_subject"] = assessment_subject_type
        if not isinstance(copied.get("applicability"), Mapping):
            raise ValueError(
                f"requirement_results[{index}].applicability must be an object"
            )
        copied["applicability"] = deepcopy(dict(copied["applicability"]))
        for field in ("evidence_refs", "validator_rule_refs", "scenario_refs"):
            copied[field] = list(copied.get(field, []))
        copied_results.append(copied)

    copied_scenario_set: dict[str, Any] | None = None
    if scenario_set is not None:
        if not isinstance(scenario_set, Mapping):
            raise ValueError("scenario_set must be an object or None")
        copied_scenario_set = deepcopy(dict(scenario_set))
        copied_scenario_set["scenario_ids"] = list(
            copied_scenario_set.get("scenario_ids", [])
        )

    copied_limitations = list(limitations)
    required_limitation = _scope_limitation(assessment_level, copied_scenario_set)
    if required_limitation not in copied_limitations:
        copied_limitations.append(required_limitation)

    source_id = assessment_subject_id
    if source_id is None:
        for candidate in ("run_id", "assessment_id", "id"):
            value = source_record.get(candidate)
            if _is_non_empty_string(value):
                source_id = str(value)
                break
    if source_id is None and _is_non_empty_string(source_artifact_ref):
        source_id = str(source_artifact_ref)
    if not _is_non_empty_string(source_id):
        raise ValueError(
            "assessment_subject_id or a stable source-record identifier is required"
        )

    source_reference: dict[str, Any] = {
        "type": assessment_subject_type,
        "id": source_id,
        "sha256": canonical_record_sha256(source_record),
    }
    if _is_non_empty_string(source_record.get("schema_version")):
        source_reference["schema_version"] = source_record["schema_version"]
    if _is_non_empty_string(source_record.get("record_created_at")):
        source_reference["record_created_at"] = source_record["record_created_at"]
    if source_artifact_ref is not None:
        source_reference["artifact_ref"] = source_artifact_ref

    assessment: dict[str, Any] = {
        "eas_version": "0.1",
        "schema_version": "0.1.0",
        "assessment_id": assessment_id,
        "assessment_subject": {
            "type": assessment_subject_type,
            "id": source_id,
        },
        "assessment_level": assessment_level,
        "assessor": {"name": assessor_name, "version": assessor_version},
        "started_at": started_at,
        "completed_at": completed_at,
        "record_created_at": record_created_at or completed_at,
        "source_record": source_reference,
        "registries": {
            "requirements": requirements_registry_version,
            "validator_rules": validator_rules_registry_version,
        },
        "scenario_set": copied_scenario_set,
        "requirement_results": copied_results,
        "summary": aggregate_requirement_results(copied_results),
        "limitations": copied_limitations,
    }
    if extensions is not None:
        assessment["extensions"] = deepcopy(dict(extensions))

    issues = validate_assessment_record(assessment, requirement_subjects)
    if issues:
        rendered = "; ".join(str(issue) for issue in issues)
        raise ValueError(f"invalid assessment record: {rendered}")
    return assessment


def requirement_results_from_issues(
    evaluated_requirements: Mapping[str, str],
    issues: Iterable[Any],
    *,
    assessment_subject: str = "run",
) -> list[dict[str, Any]]:
    """Convert validator issues for explicitly evaluated rules into results.

    ``evaluated_requirements`` must contain only requirements whose checks were
    actually executed. An absent issue is treated as pass only within that
    caller-declared set; this helper must not be used to mark unobserved
    requirements as passing.
    """

    grouped: dict[str, list[str]] = {key: [] for key in evaluated_requirements}
    for issue in issues:
        requirement_id = getattr(issue, "requirement", None)
        if requirement_id not in grouped:
            raise ValueError(
                f"issue references undeclared evaluated requirement: {requirement_id!r}"
            )
        path = getattr(issue, "path", "$")
        message = getattr(issue, "message", str(issue))
        grouped[requirement_id].append(f"{path}: {message}")

    results: list[dict[str, Any]] = []
    for requirement_id in sorted(evaluated_requirements):
        failures = grouped[requirement_id]
        result: dict[str, Any] = {
            "requirement_id": requirement_id,
            "assessment_subject": assessment_subject,
            "applicability": {
                "subject_match": "matched",
                "base": "invoked",
                "task_class": "not_invoked",
                "action_or_state": "not_invoked",
                "risk_or_event": "not_invoked",
                "selected_profile": "not_invoked",
                "applicable": True,
                "basis": "The caller declared this requirement evaluated by an executed rule.",
            },
            "level": evaluated_requirements[requirement_id],
            "result": "fail" if failures else "pass",
            "evidence_refs": [],
            "validator_rule_refs": [],
            "scenario_refs": [],
        }
        if failures:
            result["reason"] = "; ".join(failures)
        results.append(result)
    return results


def validate_assessment_record(
    record: Any,
    requirement_subjects: Mapping[str, Iterable[str]] | None = None,
) -> list[AssessmentIssue]:
    """Check assessment metadata and cross-field semantic invariants.

    JSON Schema remains the authoritative shape definition. These checks are a
    dependency-free complement for aggregate consistency, time ordering,
    scenario references, and scope limitations.
    """

    if not isinstance(record, dict):
        return [_issue("EAS-009-R11", "$", "assessment record must be an object")]

    issues: list[AssessmentIssue] = []
    required = {
        "eas_version",
        "schema_version",
        "assessment_id",
        "assessment_subject",
        "assessment_level",
        "assessor",
        "started_at",
        "completed_at",
        "record_created_at",
        "source_record",
        "registries",
        "scenario_set",
        "requirement_results",
        "summary",
        "limitations",
    }
    for name in sorted(required - record.keys()):
        issues.append(_issue("EAS-009-R11", f"$.{name}", "required field is missing"))

    if record.get("eas_version") != "0.1":
        issues.append(_issue("EAS-009-R11", "$.eas_version", "must equal '0.1'"))
    if record.get("schema_version") != "0.1.0":
        issues.append(
            _issue("EAS-009-R11", "$.schema_version", "must equal '0.1.0'")
        )
    if not _is_non_empty_string(record.get("assessment_id")):
        issues.append(
            _issue("EAS-009-R11", "$.assessment_id", "must be a non-empty string")
        )

    subject = record.get("assessment_subject")
    if not isinstance(subject, dict):
        issues.append(
            _issue("EAS-009-R11", "$.assessment_subject", "must be an object")
        )
    else:
        if subject.get("type") not in ASSESSMENT_SUBJECTS:
            issues.append(
                _issue(
                    "EAS-009-R11",
                    "$.assessment_subject.type",
                    f"must be one of {sorted(ASSESSMENT_SUBJECTS)!r}",
                )
            )
        if not _is_non_empty_string(subject.get("id")):
            issues.append(
                _issue(
                    "EAS-009-R11",
                    "$.assessment_subject.id",
                    "must be a non-empty string",
                )
            )

    level = record.get("assessment_level")
    if level not in ASSESSMENT_LEVELS:
        issues.append(
            _issue(
                "EAS-009-R11",
                "$.assessment_level",
                f"must be one of {sorted(ASSESSMENT_LEVELS)!r}",
            )
        )

    assessor = record.get("assessor")
    if not isinstance(assessor, dict):
        issues.append(_issue("EAS-009-R11", "$.assessor", "must be an object"))
    else:
        for name in ("name", "version"):
            if not _is_non_empty_string(assessor.get(name)):
                issues.append(
                    _issue(
                        "EAS-009-R11",
                        f"$.assessor.{name}",
                        "must be a non-empty string",
                    )
                )

    parsed_times: dict[str, datetime] = {}
    for name in ("started_at", "completed_at", "record_created_at"):
        parsed = _parse_timestamp(record.get(name))
        if parsed is None:
            issues.append(
                _issue(
                    "EAS-009-R11",
                    f"$.{name}",
                    "must be an RFC 3339 date-time with an explicit offset",
                )
            )
        else:
            parsed_times[name] = parsed
    if len(parsed_times) == 3:
        if parsed_times["started_at"] > parsed_times["completed_at"]:
            issues.append(
                _issue(
                    "EAS-009-R11",
                    "$.completed_at",
                    "must not precede started_at",
                )
            )
        if parsed_times["completed_at"] > parsed_times["record_created_at"]:
            issues.append(
                _issue(
                    "EAS-009-R11",
                    "$.record_created_at",
                    "must not precede completed_at",
                )
            )

    source = record.get("source_record")
    if not isinstance(source, dict):
        issues.append(_issue("EAS-009-R11", "$.source_record", "must be an object"))
    else:
        for name in ("type", "id"):
            if not _is_non_empty_string(source.get(name)):
                issues.append(
                    _issue(
                        "EAS-009-R11",
                        f"$.source_record.{name}",
                        "must be a non-empty string",
                    )
                )
        if source.get("type") not in ASSESSMENT_SUBJECTS:
            issues.append(
                _issue(
                    "EAS-009-R11",
                    "$.source_record.type",
                    f"must be one of {sorted(ASSESSMENT_SUBJECTS)!r}",
                )
            )
        elif isinstance(subject, dict) and source.get("type") != subject.get("type"):
            issues.append(
                _issue(
                    "EAS-009-R11",
                    "$.source_record.type",
                    "must match assessment_subject.type",
                )
            )
        if isinstance(subject, dict) and source.get("id") != subject.get("id"):
            issues.append(
                _issue(
                    "EAS-009-R11",
                    "$.source_record.id",
                    "must match assessment_subject.id",
                )
            )
        if "schema_version" in source and not _is_non_empty_string(
            source.get("schema_version")
        ):
            issues.append(
                _issue(
                    "EAS-009-R11",
                    "$.source_record.schema_version",
                    "must be a non-empty string when present",
                )
            )
        if "record_created_at" in source and _parse_timestamp(
            source.get("record_created_at")
        ) is None:
            issues.append(
                _issue(
                    "EAS-009-R11",
                    "$.source_record.record_created_at",
                    "must be an RFC 3339 date-time with an explicit offset when present",
                )
            )
        if not isinstance(source.get("sha256"), str) or not _SHA256.fullmatch(
            source["sha256"]
        ):
            issues.append(
                _issue(
                    "EAS-009-R11",
                    "$.source_record.sha256",
                    "must be a lowercase SHA-256 digest",
                )
            )

    registries = record.get("registries")
    if not isinstance(registries, dict):
        issues.append(_issue("EAS-009-R11", "$.registries", "must be an object"))
    else:
        for name in ("requirements", "validator_rules"):
            if not _is_non_empty_string(registries.get(name)):
                issues.append(
                    _issue(
                        "EAS-009-R11",
                        f"$.registries.{name}",
                        "must be a non-empty version string",
                    )
                )

    scenario_set = record.get("scenario_set")
    scenario_ids: set[str] = set()
    if scenario_set is not None:
        if not isinstance(scenario_set, dict):
            issues.append(
                _issue("EAS-009-R11", "$.scenario_set", "must be an object or null")
            )
        else:
            for name in ("id", "version"):
                if not _is_non_empty_string(scenario_set.get(name)):
                    issues.append(
                        _issue(
                            "EAS-009-R11",
                            f"$.scenario_set.{name}",
                            "must be a non-empty string",
                        )
                    )
            values = scenario_set.get("scenario_ids")
            if not isinstance(values, list) or not values:
                issues.append(
                    _issue(
                        "EAS-009-R11",
                        "$.scenario_set.scenario_ids",
                        "must contain at least one scenario identifier",
                    )
                )
            else:
                for index, scenario_id in enumerate(values):
                    if not _is_non_empty_string(scenario_id):
                        issues.append(
                            _issue(
                                "EAS-009-R11",
                                f"$.scenario_set.scenario_ids[{index}]",
                                "must be a non-empty string",
                            )
                        )
                    else:
                        if scenario_id in scenario_ids:
                            issues.append(
                                _issue(
                                    "EAS-009-R11",
                                    f"$.scenario_set.scenario_ids[{index}]",
                                    f"duplicate scenario identifier {scenario_id!r}",
                                )
                            )
                        scenario_ids.add(scenario_id)
        if level != "behavioral":
            issues.append(
                _issue(
                    "EAS-009-R11",
                    "$.scenario_set",
                    "a scenario set is valid only for behavioral assessment",
                )
            )

    results = record.get("requirement_results")
    result_ids: set[str] = set()
    aggregate_input: list[Mapping[str, Any]] = []
    if not isinstance(results, list) or not results:
        issues.append(
            _issue(
                "EAS-009-R11",
                "$.requirement_results",
                "must contain at least one requirement result",
            )
        )
    else:
        for index, result in enumerate(results):
            path = f"$.requirement_results[{index}]"
            if not isinstance(result, dict):
                issues.append(_issue("EAS-009-R11", path, "must be an object"))
                continue
            requirement_id = result.get("requirement_id")
            if not isinstance(requirement_id, str) or not _REQUIREMENT_ID.fullmatch(
                requirement_id
            ):
                issues.append(
                    _issue(
                        "EAS-009-R11",
                        f"{path}.requirement_id",
                        "must be an EAS requirement identifier",
                    )
                )
            elif requirement_id in result_ids:
                issues.append(
                    _issue(
                        "EAS-009-R11",
                        f"{path}.requirement_id",
                        f"duplicate requirement result {requirement_id}",
                    )
                )
            else:
                result_ids.add(requirement_id)

            result_subject = result.get("assessment_subject")
            declared_subject = subject.get("type") if isinstance(subject, dict) else None
            if result_subject != declared_subject:
                issues.append(
                    _issue(
                        "EAS-009-R11",
                        f"{path}.assessment_subject",
                        "must match the assessment record subject",
                    )
                )
            if (
                requirement_subjects is not None
                and isinstance(requirement_id, str)
            ):
                allowed_subjects = requirement_subjects.get(requirement_id)
                if allowed_subjects is None:
                    issues.append(
                        _issue(
                            "EAS-009-R11",
                            f"{path}.requirement_id",
                            "is absent from the selected requirement registry",
                        )
                    )
                elif declared_subject not in set(allowed_subjects):
                    issues.append(
                        _issue(
                            "EAS-009-R11",
                            f"{path}.assessment_subject",
                            "requirement does not belong to the declared subject",
                        )
                    )

            applicability = result.get("applicability")
            if not isinstance(applicability, dict):
                issues.append(
                    _issue(
                        "EAS-010-R18",
                        f"{path}.applicability",
                        "must be an object",
                    )
                )
            else:
                if applicability.get("subject_match") not in SUBJECT_MATCH_STATES:
                    issues.append(
                        _issue(
                            "EAS-010-R18",
                            f"{path}.applicability.subject_match",
                            "must be matched, not_matched, or indeterminate",
                        )
                    )
                for dimension in APPLICABILITY_DIMENSIONS:
                    if applicability.get(dimension) not in APPLICABILITY_STATES:
                        issues.append(
                            _issue(
                                "EAS-010-R18",
                                f"{path}.applicability.{dimension}",
                                "must be invoked, not_invoked, or indeterminate",
                            )
                        )
                if not isinstance(applicability.get("applicable"), bool):
                    issues.append(
                        _issue(
                            "EAS-010-R18",
                            f"{path}.applicability.applicable",
                            "must be boolean",
                        )
                    )
                if not _is_non_empty_string(applicability.get("basis")):
                    issues.append(
                        _issue(
                            "EAS-010-R18",
                            f"{path}.applicability.basis",
                            "must be a non-empty string",
                        )
                    )
                if applicability.get("subject_match") != "matched":
                    issues.append(
                        _issue(
                            "EAS-009-R11",
                            f"{path}.applicability.subject_match",
                            "a result in this record must match its declared subject",
                        )
                    )

            result_value = result.get("result")
            result_level = result.get("level")
            if result_value not in REQUIREMENT_RESULTS:
                issues.append(
                    _issue(
                        "EAS-009-R11",
                        f"{path}.result",
                        "must be pass, fail, indeterminate, or not_applicable",
                    )
                )
            if result_level not in REQUIREMENT_LEVELS:
                issues.append(
                    _issue(
                        "EAS-009-R11",
                        f"{path}.level",
                        "must be MUST, SHOULD, or MAY",
                    )
                )
            if isinstance(applicability, dict):
                expected_applicable = result_value != "not_applicable"
                if applicability.get("applicable") is not expected_applicable:
                    issues.append(
                        _issue(
                            "EAS-010-R18",
                            f"{path}.applicability.applicable",
                            "must be false exactly for a not_applicable result",
                        )
                    )
                dimension_values = [
                    applicability.get(name) for name in APPLICABILITY_DIMENSIONS
                ]
                if result_value in {"pass", "fail"} and "invoked" not in dimension_values:
                    issues.append(
                        _issue(
                            "EAS-010-R18",
                            f"{path}.applicability",
                            "pass or fail requires at least one invoked applicability dimension",
                        )
                    )
            if result_value in {"indeterminate", "not_applicable"} and not _is_non_empty_string(
                result.get("reason")
            ):
                issues.append(
                    _issue(
                        "EAS-009-R12",
                        f"{path}.reason",
                        f"{result_value} requires a non-empty reason",
                    )
                )
            if "reason" in result and not _is_non_empty_string(result.get("reason")):
                issues.append(
                    _issue(
                        "EAS-009-R12",
                        f"{path}.reason",
                        "when present, reason must be a non-empty string",
                    )
                )

            refs = result.get("scenario_refs", [])
            if isinstance(refs, list):
                for ref_index, scenario_id in enumerate(refs):
                    if scenario_set is None or scenario_id not in scenario_ids:
                        issues.append(
                            _issue(
                                "EAS-009-R11",
                                f"{path}.scenario_refs[{ref_index}]",
                                "must reference a scenario in the declared scenario set",
                            )
                        )
            if result_value in REQUIREMENT_RESULTS and result_level in REQUIREMENT_LEVELS:
                aggregate_input.append(result)

    limitations = record.get("limitations")
    if not isinstance(limitations, list):
        issues.append(_issue("EAS-009-R11", "$.limitations", "must be an array"))
    else:
        for index, limitation in enumerate(limitations):
            if not _is_non_empty_string(limitation):
                issues.append(
                    _issue(
                        "EAS-009-R11",
                        f"$.limitations[{index}]",
                        "must be a non-empty string",
                    )
                )
        if scenario_set is not None and SCENARIO_SCOPE_LIMITATION not in limitations:
            issues.append(
                _issue(
                    "EAS-009-R11",
                    "$.limitations",
                    "must state that scenario-set results are bounded",
                )
            )

    summary = record.get("summary")
    if not isinstance(summary, dict):
        issues.append(_issue("EAS-009-R11", "$.summary", "must be an object"))
    elif isinstance(results, list) and len(aggregate_input) == len(results):
        expected = aggregate_requirement_results(aggregate_input)
        if summary.get("result") != expected["result"]:
            issues.append(
                _issue(
                    "EAS-009-R11",
                    "$.summary.result",
                    f"must equal derived result {expected['result']!r}",
                )
            )
        counts = summary.get("counts")
        if counts != expected["counts"]:
            issues.append(
                _issue(
                    "EAS-009-R11",
                    "$.summary.counts",
                    "must equal counts derived from requirement_results",
                )
            )

    return issues
