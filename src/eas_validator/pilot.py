"""Reproducible controlled interoperability pilot for the two reference adapters."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Sequence

from .adapters import NeutralJSONLAdapter, ScriptedEventAdapter
from .scenario import assess_scenario
from .schema import validate_instance
from .validator import validate_record


PROJECTION_FIELDS = (
    "task",
    "environment",
    "started_at",
    "completed_at",
    "record_created_at",
    "initial_state",
    "constraints",
    "state_history",
    "actions",
    "decisions",
    "evidence",
    "assumptions",
    "report",
    "final_state",
    "outcome",
    "task_result",
)


def _load(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _adapter_metrics(
    *,
    name: str,
    source_format: str,
    source_event_count: int,
    adapter: Any,
    record: dict[str, Any],
    run_schema: dict[str, Any],
    scenario: dict[str, Any],
) -> dict[str, Any]:
    unmapped = adapter.get_unmapped_events()
    wholly_unmapped = sum(not item.partially_mapped for item in unmapped)
    partial = sum(item.partially_mapped for item in unmapped)
    lossless = source_event_count - len(unmapped)
    represented = source_event_count - wholly_unmapped
    return {
        "adapter": name,
        "source_format": source_format,
        "source_event_count": source_event_count,
        "mapped_record_counts": {
            "lifecycle_states": len(record["state_history"]),
            "actions": len(record["actions"]),
            "decisions": len(record["decisions"]),
            "evidence": len(record["evidence"]),
        },
        "unmapped_event_count": len(unmapped),
        "partially_mapped_event_count": partial,
        "wholly_unmapped_event_count": wholly_unmapped,
        "unmapped_source_event_ids": [item.event_id for item in unmapped],
        "lossless_event_rate": round(lossless / source_event_count, 4),
        "represented_event_rate": round(represented / source_event_count, 4),
        "explicit_assumption_count": len(adapter.get_assumptions()),
        "indeterminate_property_count": len(adapter.get_indeterminate_fields()),
        "schema_issue_count": len(validate_instance(record, run_schema)),
        "structural_issue_count": len(validate_record(record)),
        "scenario_issue_count": len(assess_scenario(scenario, record)),
    }


def build_pilot_report(root: Path) -> dict[str, Any]:
    """Run the paired controlled fixture through both adapters."""

    neutral_path = root / "examples" / "traces" / "neutral-complete.jsonl"
    with neutral_path.open(encoding="utf-8") as handle:
        neutral_events = [json.loads(line) for line in handle if line.strip()]
    scripted_path = root / "examples" / "traces" / "scripted-focused-edit.json"
    scripted_events = _load(scripted_path)

    neutral = NeutralJSONLAdapter()
    neutral.ingest(neutral_path)
    scripted = ScriptedEventAdapter()
    scripted.ingest(scripted_events)
    neutral_record = neutral.build_run_record()
    scripted_record = scripted.build_run_record()

    run_schema = _load(root / "schemas" / "eas-run.schema.json")
    scenario = _load(
        root / "compliance" / "scenarios" / "SCN-001-focused-edit.json"
    )
    neutral_projection = {
        field: neutral_record[field] for field in PROJECTION_FIELDS
    }
    scripted_projection = {
        field: scripted_record[field] for field in PROJECTION_FIELDS
    }
    agreeing_fields = [
        field
        for field in PROJECTION_FIELDS
        if neutral_record[field] == scripted_record[field]
    ]

    implementations = [
        _adapter_metrics(
            name="neutral-jsonl",
            source_format="versioned neutral JSONL events",
            source_event_count=len(neutral_events),
            adapter=neutral,
            record=neutral_record,
            run_schema=run_schema,
            scenario=scenario,
        ),
        _adapter_metrics(
            name="scripted-events",
            source_format="explicit set/append operation list",
            source_event_count=len(scripted_events),
            adapter=scripted,
            record=scripted_record,
            run_schema=run_schema,
            scenario=scenario,
        ),
    ]
    return {
        "pilot_id": "adapter-interoperability-0.1",
        "eas_version": "0.1",
        "fixture_type": "controlled_synthetic",
        "real_agent_trajectory_count": 0,
        "task_count": 1,
        "scenario_ids": ["SCN-001"],
        "source_format_count": 2,
        "adapter_count": 2,
        "implementations": implementations,
        "comparison": {
            "projection_fields": list(PROJECTION_FIELDS),
            "agreeing_projection_field_count": len(agreeing_fields),
            "total_projection_field_count": len(PROJECTION_FIELDS),
            "exact_semantic_projection_agreement": (
                neutral_projection == scripted_projection
            ),
            "neutral_projection_sha256": _digest(neutral_projection),
            "scripted_projection_sha256": _digest(scripted_projection),
            "structural_result_agreement": (
                implementations[0]["structural_issue_count"]
                == implementations[1]["structural_issue_count"]
            ),
            "scenario_result_agreement": (
                implementations[0]["scenario_issue_count"]
                == implementations[1]["scenario_issue_count"]
            ),
        },
        "limitations": [
            "Both trajectories are controlled fixtures, not observations from independent agent runtimes.",
            "Both adapters are maintained in the same reference codebase, so implementation independence is not established.",
            "The pilot uses one task and cannot estimate inter-rater agreement, false-positive rates, or real-world adapter coverage.",
            "Scenario projection does not include the external artifact bundle used by the full CLI behavioral assessment.",
        ],
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the controlled adapter pilot.")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--check", type=Path, help="require this JSON report to be current")
    args = parser.parse_args(argv)
    report = build_pilot_report(args.root)
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.check is None:
        print(rendered, end="")
        return 0
    try:
        committed = args.check.read_text(encoding="utf-8")
    except OSError as error:
        print(f"pilot report cannot be read: {error}")
        return 1
    if committed != rendered:
        print(f"pilot report is stale: {args.check}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
