"""Build and verify the immutable input set for the EAS 0.1 study."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Sequence


LOCK_VERSION = "0.1.0"
REVISION_PATTERN = re.compile(r"^[0-9a-f]{40}$")
LOCKED_PATH_GROUPS = {
    "corpus": (
        "compliance/corpus/core-0.1.json",
    ),
    "scenario_manifests": (
        "compliance/scenarios/SCN-001-focused-edit.json",
        "compliance/scenarios/SCN-002-material-ambiguity.json",
        "compliance/scenarios/SCN-003-failed-verification.json",
        "compliance/scenarios/SCN-007-diagnosis-without-fix.json",
        "compliance/scenarios/SCN-008-authorized-operation.json",
        "compliance/scenarios/SCN-010-scoped-review.json",
        "compliance/scenarios/SCN-011-sourced-research.json",
        "compliance/scenarios/SCN-012-bounded-advice.json",
    ),
    "registries": (
        "registry/requirements.json",
        "registry/validator-rules.json",
    ),
    "schemas": (
        "schemas/eas-artifact-bundle.schema.json",
        "schemas/eas-assessment.schema.json",
        "schemas/eas-corpus.schema.json",
        "schemas/eas-neutral-trace-event-0.1.0.schema.json",
        "schemas/eas-run.schema.json",
        "schemas/eas-scenario.schema.json",
    ),
    "adapters": (
        "src/eas_validator/adapters/__init__.py",
        "src/eas_validator/adapters/_base.py",
        "src/eas_validator/adapters/neutral_jsonl.py",
        "src/eas_validator/adapters/protocol.py",
        "src/eas_validator/adapters/scripted_events.py",
    ),
    "assessment_toolchain": (
        "src/eas_validator/__main__.py",
        "src/eas_validator/artifacts.py",
        "src/eas_validator/assessment.py",
        "src/eas_validator/registry.py",
        "src/eas_validator/report.py",
        "src/eas_validator/scenario.py",
        "src/eas_validator/schema.py",
        "src/eas_validator/validator.py",
    ),
}


def _digest(path: Path) -> tuple[int, str]:
    content = path.read_bytes()
    return len(content), hashlib.sha256(content).hexdigest()


def build_study_lock(root: Path, source_revision: str) -> dict[str, Any]:
    """Return the deterministic lock document for the selected source revision."""

    if not REVISION_PATTERN.fullmatch(source_revision):
        raise ValueError("source revision must be a 40-character lowercase Git SHA")
    groups = []
    for group_name, paths in LOCKED_PATH_GROUPS.items():
        files = []
        for relative_path in paths:
            byte_count, digest = _digest(root / relative_path)
            files.append(
                {
                    "path": relative_path,
                    "bytes": byte_count,
                    "sha256": digest,
                }
            )
        groups.append({"name": group_name, "files": files})
    return {
        "lock_version": LOCK_VERSION,
        "eas_version": "0.1",
        "study_id": "real-agent-validation-0.1",
        "source_revision": source_revision,
        "scenario_set": {
            "id": "core-0.1",
            "version": "0.1.1",
            "scenario_ids": [
                "SCN-001",
                "SCN-002",
                "SCN-003",
                "SCN-007",
                "SCN-008",
                "SCN-010",
                "SCN-011",
                "SCN-012",
            ],
        },
        "groups": groups,
        "claim_boundary": (
            "This lock establishes byte identity of prospective study inputs; "
            "it does not establish empirical validity or evidence authenticity."
        ),
    }


def validate_study_lock(document: Any, root: Path) -> list[str]:
    """Return all lock-format, path-set, byte-count, and digest issues."""

    if not isinstance(document, dict):
        return ["study lock must be a JSON object"]
    revision = document.get("source_revision")
    if not isinstance(revision, str) or not REVISION_PATTERN.fullmatch(revision):
        return ["source_revision must be a 40-character lowercase Git SHA"]
    try:
        expected = build_study_lock(root, revision)
    except OSError as error:
        return [f"locked input cannot be read: {error}"]
    if document == expected:
        return []

    issues: list[str] = []
    for key in (
        "lock_version",
        "eas_version",
        "study_id",
        "scenario_set",
        "claim_boundary",
    ):
        if document.get(key) != expected[key]:
            issues.append(f"{key} does not match the EAS 0.1 study definition")

    observed_groups = document.get("groups")
    if not isinstance(observed_groups, list):
        issues.append("groups must be an array")
        return issues
    observed_by_name = {
        group.get("name"): group
        for group in observed_groups
        if isinstance(group, dict) and isinstance(group.get("name"), str)
    }
    expected_names = [group["name"] for group in expected["groups"]]
    observed_names = [
        group.get("name")
        for group in observed_groups
        if isinstance(group, dict)
    ]
    if observed_names != expected_names:
        issues.append("locked group names or order changed")

    for expected_group in expected["groups"]:
        name = expected_group["name"]
        observed_group = observed_by_name.get(name)
        if not isinstance(observed_group, dict):
            issues.append(f"locked group missing: {name}")
            continue
        observed_files = observed_group.get("files")
        if not isinstance(observed_files, list):
            issues.append(f"locked group files must be an array: {name}")
            continue
        expected_files = expected_group["files"]
        expected_paths = [item["path"] for item in expected_files]
        observed_paths = [
            item.get("path")
            for item in observed_files
            if isinstance(item, dict)
        ]
        if observed_paths != expected_paths:
            issues.append(f"locked path set or order changed: {name}")
            continue
        for observed, expected_file in zip(observed_files, expected_files):
            if not isinstance(observed, dict):
                issues.append(f"locked file entry must be an object: {name}")
                continue
            path = expected_file["path"]
            if observed.get("bytes") != expected_file["bytes"]:
                issues.append(f"locked byte count changed: {path}")
            if observed.get("sha256") != expected_file["sha256"]:
                issues.append(f"locked digest changed: {path}")
    return issues or ["study lock differs from the deterministic lock document"]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build or verify the immutable EAS 0.1 study input lock."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--check", type=Path, help="verify this committed lock file")
    parser.add_argument(
        "--source-revision",
        help="40-character Git SHA used when generating a lock",
    )
    parser.add_argument("--output", type=Path, help="write a generated lock here")
    args = parser.parse_args(argv)

    if args.check is not None:
        try:
            document = json.loads(args.check.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            print(f"study lock cannot be read: {error}")
            return 1
        issues = validate_study_lock(document, args.root)
        for issue in issues:
            print(f"study lock invalid: {issue}")
        return 1 if issues else 0

    if args.source_revision is None:
        parser.error("--source-revision is required when generating a lock")
    try:
        document = build_study_lock(args.root, args.source_revision)
    except (OSError, ValueError) as error:
        print(f"study lock cannot be generated: {error}")
        return 1
    rendered = json.dumps(document, indent=2) + "\n"
    if args.output is None:
        print(rendered, end="")
    else:
        args.output.write_text(rendered, encoding="utf-8")
        print(f"WROTE: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
