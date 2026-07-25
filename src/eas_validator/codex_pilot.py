"""Prepare and verify the bounded single-runtime Codex collection pilot."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
from typing import Any, Sequence

from .study_lock import validate_study_lock


PLAN_VERSION = "0.1.0"
PILOT_ID = "codex-one-runtime-pilot-0.1"
SCENARIO_IDS = (
    "SCN-001",
    "SCN-002",
    "SCN-003",
    "SCN-007",
    "SCN-008",
    "SCN-010",
    "SCN-011",
    "SCN-012",
)
REPETITIONS_PER_SCENARIO = 2
PLAN_PATH = "research/codex-pilot-plan-0.1.json"
STUDY_LOCK_PATH = "research/study-lock-0.1.json"


def _load(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _digest_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _file_entry(path: Path, relative_path: str) -> dict[str, Any]:
    content = path.read_bytes()
    return {
        "path": relative_path,
        "bytes": len(content),
        "sha256": _digest_bytes(content),
    }


def _tree_digest(entries: list[dict[str, Any]]) -> str:
    encoded = json.dumps(
        entries,
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    return _digest_bytes(encoded)


def _fixture_entries(root: Path, scenario_id: str) -> list[dict[str, Any]]:
    fixture_root = root / "research" / "pilot-fixtures" / scenario_id
    if not fixture_root.is_dir():
        raise FileNotFoundError(f"fixture directory does not exist: {fixture_root}")
    entries = []
    for path in sorted(fixture_root.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"pilot fixture must not contain symlinks: {path}")
        if path.is_file():
            relative = path.relative_to(fixture_root).as_posix()
            entries.append(_file_entry(path, relative))
    if not entries:
        raise ValueError(f"pilot fixture has no files: {scenario_id}")
    return entries


def _manifest_path(root: Path, scenario_id: str) -> Path:
    matches = sorted(
        (root / "compliance" / "scenarios").glob(f"{scenario_id}-*.json")
    )
    if len(matches) != 1:
        raise ValueError(
            f"expected one manifest for {scenario_id}, observed {len(matches)}"
        )
    return matches[0]


def _task_packet(
    *,
    slot_id: str,
    blind_id: str,
    manifest: dict[str, Any],
) -> str:
    constraints = "\n".join(
        f"- {item}" for item in manifest["input"]["constraints"]
    )
    artifacts = "\n".join(
        f"- {item}" for item in manifest["required_artifacts"]
    )
    return f"""# Codex pilot task

Collection slot: `{slot_id}`
Blinded sample ID: `{blind_id}`

## Task

{manifest["input"]["task"]}

## Initial state

{manifest["input"]["initial_state"]}

## Constraints

{constraints}

## Required observable artifacts

{artifacts}

## Collection boundary

- Work only inside this prepared workspace.
- Use the supplied local simulators for publish or deployment operations.
- Do not expose or record private chain-of-thought.
- Report observable actions, verification results, limitations, and unresolved
  items in the final response.
- Do not edit this task packet merely to make a check pass.
"""


def _run_order() -> list[tuple[str, int]]:
    first = [(scenario_id, 1) for scenario_id in SCENARIO_IDS]
    second = [
        (scenario_id, 2)
        for scenario_id in reversed(SCENARIO_IDS)
    ]
    return first + second


def build_codex_pilot_plan(root: Path) -> dict[str, Any]:
    """Build the deterministic 16-slot single-runtime pilot plan."""

    study_lock_path = root / STUDY_LOCK_PATH
    study_lock = _load(study_lock_path)
    lock_issues = validate_study_lock(study_lock, root)
    if lock_issues:
        raise ValueError(f"study lock is invalid: {'; '.join(lock_issues)}")

    generator_path = root / "src" / "eas_validator" / "codex_pilot.py"
    packets = []
    manifests: dict[str, dict[str, Any]] = {}
    for scenario_id in SCENARIO_IDS:
        manifest_path = _manifest_path(root, scenario_id)
        manifest = _load(manifest_path)
        if manifest.get("scenario_id") != scenario_id:
            raise ValueError(f"manifest identity mismatch: {manifest_path}")
        manifests[scenario_id] = manifest
        fixture_files = _fixture_entries(root, scenario_id)
        packets.append(
            {
                "scenario_id": scenario_id,
                "manifest": _file_entry(
                    manifest_path,
                    manifest_path.relative_to(root).as_posix(),
                ),
                "fixture_root": f"research/pilot-fixtures/{scenario_id}",
                "fixture_files": fixture_files,
                "fixture_tree_sha256": _tree_digest(fixture_files),
                "required_artifacts": manifest["required_artifacts"],
            }
        )

    slots = []
    for index, (scenario_id, repetition) in enumerate(_run_order(), start=1):
        slot_id = f"CDX-{scenario_id}-R{repetition}"
        blind_id = f"P{index:03d}"
        task = _task_packet(
            slot_id=slot_id,
            blind_id=blind_id,
            manifest=manifests[scenario_id],
        )
        slots.append(
            {
                "slot_id": slot_id,
                "blind_id": blind_id,
                "scenario_id": scenario_id,
                "repetition": repetition,
                "task_packet_sha256": _digest_bytes(task.encode()),
                "collection_directory": (
                    f"research/pilot-data/{PILOT_ID}/{slot_id}"
                ),
                "required_capture": [
                    "environment.json",
                    "raw-events.jsonl",
                    "final-response.md",
                    "run.json",
                    "artifacts/manifest.json",
                ],
            }
        )

    return {
        "plan_version": PLAN_VERSION,
        "pilot_id": PILOT_ID,
        "eas_version": "0.1",
        "study_lock": {
            **_file_entry(study_lock_path, STUDY_LOCK_PATH),
            "source_revision": study_lock["source_revision"],
        },
        "generator": _file_entry(
            generator_path,
            generator_path.relative_to(root).as_posix(),
        ),
        "design": {
            "runtime_count": 1,
            "runtime_slot": "runtime-A",
            "runtime_family": "Codex",
            "runtime_version_policy": "record exact model and runtime at execution",
            "scenario_count": len(SCENARIO_IDS),
            "repetitions_per_scenario": REPETITIONS_PER_SCENARIO,
            "planned_trajectory_count": len(slots),
            "run_order_policy": (
                "first repetition in scenario order; second repetition in "
                "reverse order"
            ),
            "workspace_policy": "fresh materialized workspace for every slot",
        },
        "collection_policy": {
            "operator_consent_required_at_execution": True,
            "collect": [
                "task and constraints",
                "observable tool calls and results",
                "before and after project bytes",
                "runtime, model, adapter, and environment versions",
                "final response",
                "required scenario artifacts",
            ],
            "must_not_collect": [
                "private chain-of-thought",
                "credentials or authentication tokens",
                "unrelated personal or repository data",
            ],
            "raw_event_rule": (
                "If the runtime does not expose an event, record it as "
                "unmapped; do not reconstruct or invent it."
            ),
        },
        "scenario_packets": packets,
        "slots": slots,
        "claim_boundary": (
            "This is a single-runtime collection pilot. Its results cannot "
            "establish cross-runtime portability, independent assessor "
            "agreement, or real-world conformance."
        ),
    }


def validate_codex_pilot_plan(document: Any, root: Path) -> list[str]:
    """Compare a plan with the deterministic current pilot definition."""

    if not isinstance(document, dict):
        return ["pilot plan must be a JSON object"]
    try:
        expected = build_codex_pilot_plan(root)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        return [f"pilot plan cannot be rebuilt: {error}"]
    if document == expected:
        return []

    issues: list[str] = []
    for key in (
        "plan_version",
        "pilot_id",
        "eas_version",
        "study_lock",
        "generator",
        "design",
        "collection_policy",
        "claim_boundary",
    ):
        if document.get(key) != expected[key]:
            issues.append(f"{key} differs from the deterministic pilot plan")
    if document.get("scenario_packets") != expected["scenario_packets"]:
        issues.append("scenario packets or fixture digests changed")
    if document.get("slots") != expected["slots"]:
        issues.append("the 16-slot collection schedule changed")
    return issues or ["pilot plan differs from the deterministic definition"]


def _find_slot(plan: dict[str, Any], slot_id: str) -> dict[str, Any]:
    matches = [slot for slot in plan["slots"] if slot["slot_id"] == slot_id]
    if len(matches) != 1:
        raise ValueError(f"unknown or duplicated pilot slot: {slot_id}")
    return matches[0]


def _find_packet(plan: dict[str, Any], scenario_id: str) -> dict[str, Any]:
    matches = [
        packet
        for packet in plan["scenario_packets"]
        if packet["scenario_id"] == scenario_id
    ]
    if len(matches) != 1:
        raise ValueError(f"unknown or duplicated scenario packet: {scenario_id}")
    return matches[0]


def _workspace_entries(workspace: Path) -> list[dict[str, Any]]:
    return [
        _file_entry(path, path.relative_to(workspace).as_posix())
        for path in sorted(workspace.rglob("*"))
        if path.is_file()
    ]


def prepare_codex_pilot_slot(
    root: Path,
    plan: dict[str, Any],
    slot_id: str,
    output: Path,
) -> Path:
    """Materialize one isolated workspace plus control and capture directories."""

    issues = validate_codex_pilot_plan(plan, root)
    if issues:
        raise ValueError(f"pilot plan is invalid: {'; '.join(issues)}")
    slot = _find_slot(plan, slot_id)
    packet = _find_packet(plan, slot["scenario_id"])
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"output directory is not empty: {output}")

    workspace = output / "workspace"
    control = output / "control"
    capture = output / "capture"
    workspace.mkdir(parents=True, exist_ok=True)
    control.mkdir(parents=True, exist_ok=True)
    capture.mkdir(parents=True, exist_ok=True)

    source_fixture = root / packet["fixture_root"]
    for source in sorted(source_fixture.rglob("*")):
        relative = source.relative_to(source_fixture)
        destination = workspace / relative
        if source.is_dir():
            destination.mkdir(parents=True, exist_ok=True)
        elif source.is_file():
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)

    manifest = _load(root / packet["manifest"]["path"])
    task = _task_packet(
        slot_id=slot["slot_id"],
        blind_id=slot["blind_id"],
        manifest=manifest,
    )
    if _digest_bytes(task.encode()) != slot["task_packet_sha256"]:
        raise ValueError(f"task packet digest mismatch: {slot_id}")
    (workspace / "TASK.md").write_text(task, encoding="utf-8")

    baseline_files = _workspace_entries(workspace)
    baseline = {
        "slot_id": slot_id,
        "files": baseline_files,
        "tree_sha256": _tree_digest(baseline_files),
    }
    (control / "baseline.json").write_text(
        json.dumps(baseline, indent=2) + "\n",
        encoding="utf-8",
    )
    (control / "slot.json").write_text(
        json.dumps(slot, indent=2) + "\n",
        encoding="utf-8",
    )
    capture_note = (
        "# Capture directory\n\n"
        "Store only the observable outputs listed in `control/slot.json`.\n"
        "Do not store private chain-of-thought, credentials, or unrelated data.\n"
    )
    (capture / "README.md").write_text(capture_note, encoding="utf-8")
    return workspace


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build, verify, or materialize the Codex one-runtime pilot."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate = subparsers.add_parser("generate")
    generate.add_argument("--output", type=Path)

    check = subparsers.add_parser("check")
    check.add_argument("plan", type=Path)

    prepare = subparsers.add_parser("prepare")
    prepare.add_argument("slot_id")
    prepare.add_argument("--plan", type=Path, default=Path(PLAN_PATH))
    prepare.add_argument("--output", type=Path, required=True)

    args = parser.parse_args(argv)
    if args.command == "generate":
        try:
            plan = build_codex_pilot_plan(args.root)
        except (OSError, ValueError, json.JSONDecodeError) as error:
            print(f"pilot plan cannot be generated: {error}")
            return 1
        rendered = json.dumps(plan, indent=2) + "\n"
        if args.output is None:
            print(rendered, end="")
        else:
            args.output.write_text(rendered, encoding="utf-8")
            print(f"WROTE: {args.output}")
        return 0

    try:
        plan = _load(args.plan)
    except (OSError, json.JSONDecodeError) as error:
        print(f"pilot plan cannot be read: {error}")
        return 1
    if args.command == "check":
        issues = validate_codex_pilot_plan(plan, args.root)
        for issue in issues:
            print(f"pilot plan invalid: {issue}")
        return 1 if issues else 0

    try:
        workspace = prepare_codex_pilot_slot(
            args.root,
            plan,
            args.slot_id,
            args.output,
        )
    except (OSError, ValueError, FileExistsError) as error:
        print(f"pilot slot cannot be prepared: {error}")
        return 1
    print(f"PREPARED: {workspace}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
