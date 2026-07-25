"""Command-line interface for the experimental EAS 0.1 toolchain."""

from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from typing import Any, Iterable, Sequence

from .artifacts import ArtifactIssue, validate_artifact_files
from .assessment import build_assessment_record, validate_assessment_record
from .report import render_report
from .registry import resolve_requirement_subjects
from .scenario import assess_scenario
from .schema import SchemaIssue, validate_instance
from .validator import ValidationIssue, validate_record


COMMANDS = {"validate", "assess", "report"}
TASK_CLASSES = {"change", "diagnose", "review", "research", "operate", "advise"}
ARTIFACT_LIMITATION = (
    "Artifact integrity checks establish presence and digest only; they do not "
    "establish semantic authenticity."
)
MISSING_ARTIFACT_LIMITATION = (
    "The required external artifact bundle was not provided; dependent "
    "behavioral results are indeterminate."
)


def _repository_root() -> Path:
    candidates = (Path.cwd(), Path(__file__).resolve().parents[2])
    for candidate in candidates:
        if (candidate / "schemas" / "eas-run.schema.json").is_file():
            return candidate
    raise RuntimeError(
        "cannot locate EAS schemas; run from a source checkout or provide a checkout"
    )


def _load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _read_json(path: Path, label: str) -> tuple[Any | None, str | None]:
    try:
        return _load_json(path), None
    except (OSError, json.JSONDecodeError) as error:
        return None, f"cannot read {label} {path}: {error}"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _render_issues(issues: Iterable[Any], *, prefix: str = "- ") -> list[str]:
    return [f"{prefix}{issue}" for issue in issues]


def _write_or_print(text: str, output: Path | None) -> None:
    if output is None:
        print(text, end="")
        return
    output.write_text(text, encoding="utf-8")
    print(f"WROTE: {output}")


def _validate_command(args: argparse.Namespace) -> int:
    record, error = _read_json(args.record, "run record")
    if error:
        print(f"INVALID INPUT: {error}")
        return 2

    root = _repository_root()
    schema = _load_json(root / "schemas" / "eas-run.schema.json")
    schema_issues = validate_instance(record, schema)
    structural_issues: list[ValidationIssue] = []
    if not schema_issues:
        structural_issues = validate_record(record)

    print("EAS validation: structural")
    print("Version: EAS 0.1 Working Draft")
    print(f"Level 1 — schema: {'FAIL' if schema_issues else 'PASS'}")
    if schema_issues:
        print("Level 2 — structural semantics: NOT RUN (schema prerequisite failed)")
    else:
        print(
            f"Level 2 — structural semantics: "
            f"{'FAIL' if structural_issues else 'PASS'}"
        )
    print("Level 3 — behavioral assessment: NOT ASSESSED")

    issues: list[Any] = [*schema_issues, *structural_issues]
    if issues:
        print("Result: NONCONFORMING AT AN ASSESSED LEVEL")
        print("Issues:")
        print("\n".join(_render_issues(issues)))
        return 1
    print("Result: STRUCTURAL PASS ONLY (not a behavioral conformance claim)")
    return 0


def _load_requirement_registry(
    root: Path,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, frozenset[str]]]:
    document = _load_json(root / "registry" / "requirements.json")
    entries = {item["id"]: item for item in document["requirements"]}
    return document, entries, resolve_requirement_subjects(document)


def _run_applicability(
    metadata: dict[str, Any],
    *,
    task_classes: set[str],
    scenario_id: str | None,
    applicable: bool,
) -> dict[str, Any]:
    tags = {item for item in metadata.get("applicability", []) if isinstance(item, str)}
    base = applicable and "all_runs" in tags
    class_invoked = applicable and bool(tags & task_classes & TASK_CLASSES)
    profile = False
    action_or_state = applicable and any(
        fragment in tag
        for tag in tags
        for fragment in ("action", "state", "change", "operate", "verification")
    )
    risk_or_event = applicable and any(
        fragment in tag
        for tag in tags
        for fragment in (
            "risk", "failure", "failed", "ambiguity", "uncertainty",
            "escalation", "redact", "unavailable", "result", "claim",
        )
    )
    if applicable and not any((base, class_invoked, profile, action_or_state, risk_or_event)):
        risk_or_event = True
    state = lambda invoked: "invoked" if invoked else "not_invoked"
    basis = (
        f"Scenario {scenario_id} declares the requirement in scope and the "
        "registry applicability tags were evaluated across all dimensions."
        if scenario_id
        else "The executed validator rule and registry applicability tags place the requirement in scope."
    )
    if not applicable:
        basis = "The declared subject or every independent applicability trigger is observably absent."
    return {
        "subject_match": "matched",
        "base": state(base),
        "task_class": state(class_invoked),
        "action_or_state": state(action_or_state),
        "risk_or_event": state(risk_or_event),
        "selected_profile": state(profile),
        "applicable": applicable,
        "basis": basis,
    }


def _run_requirement_is_applicable(
    metadata: dict[str, Any],
    record: dict[str, Any],
) -> bool:
    """Evaluate the observable run-level triggers declared by the registry."""

    tags = {
        item
        for item in metadata.get("applicability", [])
        if isinstance(item, str)
    }
    unconditional = {"all_runs", "behavioral_scenario", "scenario_assessment"}
    if tags & unconditional:
        return True

    actions = record.get("actions", [])
    if not isinstance(actions, list):
        actions = []
    if "material_action" in tags and any(
        isinstance(item, dict) and item.get("material") is True
        for item in actions
    ):
        return True
    if "performed_action" in tags and any(
        isinstance(item, dict) for item in actions
    ):
        return True

    verification = record.get("report", {}).get("verification", [])
    if not isinstance(verification, list):
        verification = []
    if "passed_verification_claim" in tags and any(
        isinstance(item, dict) and item.get("status") == "passed"
        for item in verification
    ):
        return True

    task = record.get("task", {})
    task_classes = {
        item
        for item in [
            task.get("primary_class") if isinstance(task, dict) else None,
            *(task.get("secondary_classes", []) if isinstance(task, dict) else []),
        ]
        if isinstance(item, str)
    }
    if tags & task_classes & TASK_CLASSES:
        return True

    supported = unconditional | {
        "material_action",
        "performed_action",
        "passed_verification_claim",
    } | TASK_CLASSES
    if tags - supported:
        return True
    return False


def _requirement_result(
    requirement_id: str,
    result: str,
    registry: dict[str, Any],
    *,
    reason: str | None = None,
    scenario_id: str | None = None,
    task_classes: set[str] | None = None,
) -> dict[str, Any]:
    metadata = registry[requirement_id]
    item: dict[str, Any] = {
        "requirement_id": requirement_id,
        "assessment_subject": "run",
        "applicability": _run_applicability(
            metadata,
            task_classes=task_classes or set(),
            scenario_id=scenario_id,
            applicable=result != "not_applicable",
        ),
        "title": metadata["title"],
        "level": metadata["level"],
        "result": result,
        "evidence_refs": [],
        "validator_rule_refs": list(metadata["validator_rules"]),
        "scenario_refs": [scenario_id] if scenario_id is not None else [],
    }
    if reason:
        item["reason"] = reason
    return item


def _join_issue_reasons(issues: Iterable[Any]) -> str:
    return "; ".join(str(issue) for issue in issues)


def _build_behavioral_results(
    *,
    scenario: dict[str, Any],
    registry: dict[str, Any],
    requirement_subjects: dict[str, frozenset[str]],
    record: dict[str, Any],
    record_schema_issues: list[SchemaIssue],
    scenario_schema_issues: list[SchemaIssue],
    structural_issues: list[ValidationIssue],
    behavioral_issues: list[ValidationIssue],
    artifact_issues: list[Any],
    artifacts_missing: bool,
) -> list[dict[str, Any]]:
    scenario_id = scenario.get("scenario_id")
    task = record.get("task", {})
    task_classes = {
        item
        for item in [
            task.get("primary_class") if isinstance(task, dict) else None,
            *(task.get("secondary_classes", []) if isinstance(task, dict) else []),
        ]
        if isinstance(item, str)
    }
    declared = {
        item
        for item in scenario.get("requirement_refs", [])
        if isinstance(item, str)
        and item in registry
        and "run" in requirement_subjects.get(item, frozenset())
    }
    results: dict[str, dict[str, Any]] = {}

    grouped: dict[str, list[ValidationIssue]] = defaultdict(list)
    for issue in structural_issues:
        if (
            issue.requirement in registry
            and "run" in requirement_subjects.get(issue.requirement, frozenset())
        ):
            grouped[issue.requirement].append(issue)
    for requirement_id, issues in grouped.items():
        results[requirement_id] = _requirement_result(
            requirement_id,
            "fail",
            registry,
            reason=_join_issue_reasons(issues),
            scenario_id=scenario_id,
            task_classes=task_classes,
        )

    prerequisites_failed = bool(
        record_schema_issues or scenario_schema_issues or structural_issues
    )
    if prerequisites_failed:
        reason = "Schema or structural prerequisites failed before behavioral assessment."
        for requirement_id in declared - results.keys():
            results[requirement_id] = _requirement_result(
                requirement_id,
                "indeterminate",
                registry,
                reason=reason,
                scenario_id=scenario_id,
                task_classes=task_classes,
            )
        return sorted(results.values(), key=lambda item: item["requirement_id"])

    bounded_requirement = "EAS-009-R09"
    if behavioral_issues or artifact_issues:
        results[bounded_requirement] = _requirement_result(
            bounded_requirement,
            "fail",
            registry,
            reason=_join_issue_reasons([*behavioral_issues, *artifact_issues]),
            scenario_id=scenario_id,
            task_classes=task_classes,
        )
    elif artifacts_missing:
        results[bounded_requirement] = _requirement_result(
            bounded_requirement,
            "indeterminate",
            registry,
            reason=MISSING_ARTIFACT_LIMITATION,
            scenario_id=scenario_id,
            task_classes=task_classes,
        )

    for requirement_id in declared - results.keys():
        if not _run_requirement_is_applicable(
            registry[requirement_id],
            record,
        ):
            results[requirement_id] = _requirement_result(
                requirement_id,
                "not_applicable",
                registry,
                reason=(
                    "The run contains none of the observable applicability "
                    "triggers declared by the requirement registry."
                ),
                scenario_id=scenario_id,
                task_classes=task_classes,
            )
            continue
        results[requirement_id] = _requirement_result(
            requirement_id,
            "pass",
            registry,
            reason="The executed deterministic checks for this requirement passed.",
            scenario_id=scenario_id,
            task_classes=task_classes,
        )
    return sorted(results.values(), key=lambda item: item["requirement_id"])


def _read_artifact_bundle(path: Path) -> tuple[Any | None, Path, str | None]:
    manifest = path / "manifest.json" if path.is_dir() else path
    bundle, error = _read_json(manifest, "artifact manifest")
    return bundle, manifest.parent, error


def _assess_command(args: argparse.Namespace) -> int:
    started_at = _now()
    record, record_error = _read_json(args.record, "run record")
    scenario, scenario_error = _read_json(args.scenario, "scenario")
    if record_error or scenario_error:
        print(f"INVALID INPUT: {record_error or scenario_error}")
        return 2
    if not isinstance(record, dict) or not isinstance(scenario, dict):
        print("INVALID INPUT: run record and scenario must be JSON objects")
        return 2

    root = _repository_root()
    run_schema = _load_json(root / "schemas" / "eas-run.schema.json")
    scenario_schema = _load_json(root / "schemas" / "eas-scenario.schema.json")
    artifact_schema = _load_json(root / "schemas" / "eas-artifact-bundle.schema.json")
    (
        requirement_document,
        requirement_registry,
        requirement_subjects,
    ) = _load_requirement_registry(root)
    rule_document = _load_json(root / "registry" / "validator-rules.json")

    record_schema_issues = validate_instance(record, run_schema)
    scenario_schema_issues = validate_instance(scenario, scenario_schema)
    if record_schema_issues or scenario_schema_issues:
        print("EAS assessment pipeline: behavioral")
        print("Version: EAS 0.1 Working Draft")
        print("Level 1 — schema: FAIL")
        print("Level 2 — structural semantics: NOT RUN")
        print("Level 3 — behavioral scenario: NOT RUN")
        print("Result: INVALID ASSESSMENT INPUT")
        print("Issues:")
        print(
            "\n".join(
                _render_issues([*record_schema_issues, *scenario_schema_issues])
            )
        )
        return 1
    structural_issues = validate_record(record) if not record_schema_issues else []
    behavioral_issues = (
        assess_scenario(scenario, record)
        if not record_schema_issues and not scenario_schema_issues and not structural_issues
        else []
    )

    required_artifacts = [
        item for item in scenario.get("required_artifacts", []) if isinstance(item, str)
    ]
    artifacts_missing = bool(required_artifacts) and args.artifacts is None
    artifact_issues: list[SchemaIssue | ArtifactIssue] = []
    if args.artifacts is not None:
        bundle, bundle_directory, bundle_error = _read_artifact_bundle(args.artifacts)
        if bundle_error:
            print(f"INVALID INPUT: {bundle_error}")
            return 2
        artifact_issues.extend(validate_instance(bundle, artifact_schema))
        if not artifact_issues:
            artifact_issues.extend(
                validate_artifact_files(
                    bundle,
                    bundle_directory,
                    expected_run_id=record.get("run_id"),
                    required_kinds=required_artifacts,
                )
            )

    results = _build_behavioral_results(
        scenario=scenario,
        registry=requirement_registry,
        requirement_subjects=requirement_subjects,
        record=record,
        record_schema_issues=record_schema_issues,
        scenario_schema_issues=scenario_schema_issues,
        structural_issues=structural_issues,
        behavioral_issues=behavioral_issues,
        artifact_issues=artifact_issues,
        artifacts_missing=artifacts_missing,
    )
    completed_at = _now()
    limitations = [ARTIFACT_LIMITATION]
    if artifacts_missing:
        limitations.append(MISSING_ARTIFACT_LIMITATION)
    assessment_id = args.assessment_id or (
        f"assessment-{record.get('run_id', 'unknown')}-"
        f"{scenario.get('scenario_id', 'unknown')}-{completed_at.replace(':', '')}"
    )
    assessment = build_assessment_record(
        assessment_id=assessment_id,
        assessment_level="behavioral",
        assessor_name="eas-reference-assessor",
        assessor_version="0.1.0.dev0",
        source_record=record,
        requirement_results=results,
        requirement_subjects=requirement_subjects,
        requirements_registry_version=requirement_document["registry_version"],
        validator_rules_registry_version=rule_document["registry_version"],
        started_at=started_at,
        completed_at=completed_at,
        scenario_set={
            "id": args.scenario_set,
            "version": args.scenario_set_version,
            "scenario_ids": [scenario["scenario_id"]],
        },
        source_artifact_ref=str(args.record),
        limitations=limitations,
    )

    if args.format == "terminal" and args.output is None:
        print("EAS assessment pipeline: behavioral")
        print("Version: EAS 0.1 Working Draft")
        print(
            f"Level 1 — schema: "
            f"{'FAIL' if record_schema_issues or scenario_schema_issues else 'PASS'}"
        )
        if record_schema_issues or scenario_schema_issues:
            print("Level 2 — structural semantics: NOT RUN")
            print("Level 3 — behavioral scenario: NOT RUN")
        else:
            print(
                f"Level 2 — structural semantics: "
                f"{'FAIL' if structural_issues else 'PASS'}"
            )
            if structural_issues:
                print("Level 3 — behavioral scenario: NOT RUN")
            else:
                behavior_status = "FAIL" if behavioral_issues else "PASS"
                print(f"Level 3 — behavioral scenario: {behavior_status}")
        if artifacts_missing:
            print("External artifacts: NOT ASSESSED (required bundle missing)")
        else:
            print(f"External artifacts: {'FAIL' if artifact_issues else 'PASS'}")
        print("")

    rendered = render_report(assessment, args.format)
    _write_or_print(rendered, args.output)
    return 0 if assessment["summary"]["result"] == "pass" else 1


def _report_command(args: argparse.Namespace) -> int:
    record, error = _read_json(args.assessment, "assessment record")
    if error:
        print(f"INVALID INPUT: {error}")
        return 2
    root = _repository_root()
    schema = _load_json(root / "schemas" / "eas-assessment.schema.json")
    requirement_document = _load_json(root / "registry" / "requirements.json")
    requirement_subjects = resolve_requirement_subjects(requirement_document)
    schema_issues = validate_instance(record, schema)
    semantic_issues = validate_assessment_record(record, requirement_subjects)
    if schema_issues or semantic_issues:
        print("INVALID ASSESSMENT RECORD")
        print("\n".join(_render_issues([*schema_issues, *semantic_issues])))
        return 1
    _write_or_print(render_report(record, args.format), args.output)
    return 0


def _legacy_main(argv: Sequence[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Legacy EAS source-checkout invocation; prefer explicit subcommands."
    )
    parser.add_argument("record", type=Path)
    parser.add_argument("--scenario", type=Path)
    args = parser.parse_args(argv)
    record, error = _read_json(args.record, "run record")
    if error:
        print(f"INVALID INPUT: {error}")
        return 2
    if args.scenario is None:
        issues = validate_record(record)
        label = "Level 2 structural semantics"
    else:
        scenario, scenario_error = _read_json(args.scenario, "scenario")
        if scenario_error:
            print(f"INVALID INPUT: {scenario_error}")
            return 2
        issues = assess_scenario(scenario, record)
        label = (
            f"Level 3 scenario projection {scenario.get('scenario_id', 'unknown')} "
            "(external artifacts not assessed)"
        )
    if issues:
        print(f"NONCONFORMING ({label})")
        print("\n".join(_render_issues(issues)))
        return 1
    print(f"PASS ({label}; bounded result, not universal EAS conformance)")
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="eas",
        description="Experimental EAS 0.1 validation and reporting toolchain.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser(
        "validate", help="run Level 1 schema and Level 2 structural checks"
    )
    validate_parser.add_argument("record", type=Path)
    validate_parser.set_defaults(handler=_validate_command)

    assess_parser = subparsers.add_parser(
        "assess", help="run a bounded Level 3 behavioral scenario assessment"
    )
    assess_parser.add_argument("record", type=Path)
    assess_parser.add_argument("--scenario", type=Path, required=True)
    assess_parser.add_argument(
        "--artifacts",
        type=Path,
        help="artifact bundle directory or manifest.json; omission may be indeterminate",
    )
    assess_parser.add_argument("--scenario-set", default="ad-hoc")
    assess_parser.add_argument("--scenario-set-version", default="0.1.0")
    assess_parser.add_argument("--assessment-id")
    assess_parser.add_argument(
        "--format", choices=("terminal", "json", "markdown"), default="terminal"
    )
    assess_parser.add_argument("--output", type=Path)
    assess_parser.set_defaults(handler=_assess_command)

    report_parser = subparsers.add_parser(
        "report", help="render a versioned assessment record"
    )
    report_parser.add_argument("assessment", type=Path)
    report_parser.add_argument(
        "--format", choices=("terminal", "json", "markdown"), default="terminal"
    )
    report_parser.add_argument("--output", type=Path)
    report_parser.set_defaults(handler=_report_command)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    values = list(argv) if argv is not None else sys.argv[1:]
    if values and values[0] not in COMMANDS and not values[0].startswith("-"):
        return _legacy_main(values)
    args = _parser().parse_args(values)
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
