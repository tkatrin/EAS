"""Loss-preserving incomplete observations for conservative EAS adapters."""

from __future__ import annotations

import argparse
from collections.abc import Mapping, Sequence
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from .adapters import EASAdapter, NeutralJSONLAdapter
from .schema import validate_instance


OBSERVATION_SCHEMA_VERSION = "0.1.0"
TARGET_RUN_SCHEMA_VERSION = "0.1.0"


@dataclass(frozen=True)
class ObservationIssue:
    """One cross-field problem in an incomplete-observation envelope."""

    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.path}: {self.message}"


def _non_empty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _event_id(value: Any) -> str | None:
    if not isinstance(value, Mapping):
        return None
    candidate = value.get("event_id")
    return candidate if _non_empty(candidate) else None


def build_incomplete_observation(
    *,
    observation_id: str,
    record_created_at: str,
    source_format: str,
    source_events: Sequence[Any],
    adapter: EASAdapter,
) -> dict[str, Any]:
    """Build an indeterminate envelope without serializing a partial run record."""

    missing = adapter.get_indeterminate_fields()
    if not missing:
        raise ValueError(
            "the adapter reports no missing target fields; an incomplete "
            "observation would misrepresent a complete mapping"
        )

    partial_record = adapter.build_run_record()
    implementation = partial_record.get("implementation")
    if not isinstance(implementation, Mapping):
        raise ValueError("adapter output does not identify its implementation")
    adapter_name = implementation.get("adapter")
    adapter_version = implementation.get("adapter_version")
    if not _non_empty(adapter_name) or not _non_empty(adapter_version):
        raise ValueError("adapter output does not identify its name and version")

    events: list[dict[str, Any]] = []
    for index, source_event in enumerate(source_events):
        item: dict[str, Any] = {
            "index": index,
            "content": deepcopy(source_event),
        }
        source_event_id = _event_id(source_event)
        if source_event_id is not None:
            item["event_id"] = source_event_id
        events.append(item)

    missing_fields: list[dict[str, Any]] = []
    missing_by_path: dict[str, dict[str, Any]] = {}
    for missing_field in missing:
        existing = missing_by_path.get(missing_field.path)
        if existing is None:
            existing = {
                "path": missing_field.path,
                "reason": missing_field.reason,
                "source_event_ids": list(missing_field.source_event_ids),
            }
            missing_by_path[missing_field.path] = existing
            missing_fields.append(existing)
            continue
        if missing_field.reason not in existing["reason"].split("; "):
            existing["reason"] += f"; {missing_field.reason}"
        for source_event_id in missing_field.source_event_ids:
            if source_event_id not in existing["source_event_ids"]:
                existing["source_event_ids"].append(source_event_id)

    observation: dict[str, Any] = {
        "eas_version": "0.1",
        "observation_schema_version": OBSERVATION_SCHEMA_VERSION,
        "observation_id": observation_id,
        "record_created_at": record_created_at,
        "target_run_schema_version": TARGET_RUN_SCHEMA_VERSION,
        "source": {
            "format": source_format,
            "adapter": adapter_name,
            "adapter_version": adapter_version,
        },
        "events": events,
        "missing_fields": missing_fields,
        "result": "indeterminate",
    }
    run_id = partial_record.get("run_id")
    if _non_empty(run_id):
        observation["observed_run_id"] = run_id
    return observation


def validate_incomplete_observation(
    observation: Any,
) -> list[ObservationIssue]:
    """Check invariants not expressed by the observation JSON Schema."""

    if not isinstance(observation, Mapping):
        return [ObservationIssue("$", "incomplete observation must be an object")]

    issues: list[ObservationIssue] = []
    if observation.get("result") != "indeterminate":
        issues.append(
            ObservationIssue(
                "$.result",
                "an incomplete observation must remain indeterminate",
            )
        )

    events = observation.get("events")
    event_indices: set[int] = set()
    event_ids: set[str] = set()
    if isinstance(events, list):
        for position, event in enumerate(events):
            if not isinstance(event, Mapping):
                continue
            index = event.get("index")
            if isinstance(index, int) and not isinstance(index, bool):
                if index in event_indices:
                    issues.append(
                        ObservationIssue(
                            f"$.events[{position}].index",
                            "source event indexes must be unique",
                        )
                    )
                event_indices.add(index)
                if index != position:
                    issues.append(
                        ObservationIssue(
                            f"$.events[{position}].index",
                            "source event indexes must preserve sequence order",
                        )
                    )
            event_id = event.get("event_id")
            if _non_empty(event_id):
                if event_id in event_ids:
                    issues.append(
                        ObservationIssue(
                            f"$.events[{position}].event_id",
                            "source event identifiers must be unique",
                        )
                    )
                event_ids.add(event_id)

    missing_fields = observation.get("missing_fields")
    missing_paths: set[str] = set()
    if isinstance(missing_fields, list):
        if not missing_fields:
            issues.append(
                ObservationIssue(
                    "$.missing_fields",
                    "at least one target field must be missing",
                )
            )
        for position, field in enumerate(missing_fields):
            if not isinstance(field, Mapping):
                continue
            path = field.get("path")
            if _non_empty(path):
                if path in missing_paths:
                    issues.append(
                        ObservationIssue(
                            f"$.missing_fields[{position}].path",
                            "missing target paths must be unique",
                        )
                    )
                missing_paths.add(path)
            refs = field.get("source_event_ids")
            if isinstance(refs, list):
                for source_event_id in refs:
                    if _non_empty(source_event_id) and source_event_id not in event_ids:
                        issues.append(
                            ObservationIssue(
                                f"$.missing_fields[{position}].source_event_ids",
                                f"unknown source event identifier: {source_event_id}",
                            )
                        )

    return issues


def _repository_root() -> Path:
    candidates = (Path.cwd(), Path(__file__).resolve().parents[2])
    for candidate in candidates:
        if (candidate / "schemas" / "eas-incomplete-observation.schema.json").is_file():
            return candidate
    raise RuntimeError("cannot locate the incomplete-observation schema")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def main(argv: Sequence[str] | None = None) -> int:
    """Preserve one incomplete neutral JSONL trace as an observation envelope."""

    parser = argparse.ArgumentParser(
        description=(
            "Preserve an incomplete neutral JSONL trace without creating an "
            "EAS run record."
        )
    )
    parser.add_argument("trace", type=Path)
    parser.add_argument("--observation-id", required=True)
    parser.add_argument(
        "--record-created-at",
        help="RFC 3339 serialization time; defaults to the current UTC time",
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    try:
        lines = [
            line
            for line in args.trace.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    except OSError as error:
        print(f"INVALID INPUT: cannot read source trace {args.trace}: {error}")
        return 2

    events: list[Any] = []
    for line in lines:
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            events.append(line)

    adapter = NeutralJSONLAdapter()
    adapter.ingest(events)
    try:
        observation = build_incomplete_observation(
            observation_id=args.observation_id,
            record_created_at=args.record_created_at or _now(),
            source_format="eas-neutral-jsonl/0.1.0",
            source_events=events,
            adapter=adapter,
        )
    except ValueError as error:
        print(f"INVALID INCOMPLETE OBSERVATION: {error}")
        return 2

    root = _repository_root()
    schema = json.loads(
        (root / "schemas" / "eas-incomplete-observation.schema.json").read_text(
            encoding="utf-8"
        )
    )
    issues = [
        *validate_instance(observation, schema),
        *validate_incomplete_observation(observation),
    ]
    if issues:
        print("INVALID INCOMPLETE OBSERVATION")
        for issue in issues:
            print(f"- {issue}")
        return 2

    rendered = json.dumps(observation, indent=2, sort_keys=True) + "\n"
    args.output.write_text(rendered, encoding="utf-8")
    print(f"WROTE: {args.output}")
    print("Result: INDETERMINATE")
    print(f"Preserved source events: {len(observation['events'])}")
    print(f"Missing target fields: {len(observation['missing_fields'])}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
