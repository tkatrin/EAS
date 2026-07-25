"""Loss-preserving incomplete observations for conservative EAS adapters."""

from __future__ import annotations

import argparse
from collections.abc import Mapping, Sequence
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Any

from .adapters import EASAdapter, NeutralJSONLAdapter, TRACE_SCHEMA_VERSION
from .schema import validate_instance


OBSERVATION_SCHEMA_VERSION = "0.1.0"
TARGET_RUN_SCHEMA_VERSION = "0.1.0"
NATIVE_EXTENSION_PATTERN = re.compile(r"^x-[a-z0-9][a-z0-9._-]*$")
OBSERVER_EVENT_TYPES = frozenset(
    {
        "trace_start",
        "tool_result",
        "file_change",
        "evidence",
        "project_state",
    }
)


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


def _read_jsonl(path: Path) -> list[Any]:
    lines = [
        line
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    events: list[Any] = []
    for line in lines:
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            events.append(line)
    return events


def _wrap_native_events(
    source_events: Sequence[Any],
    *,
    extension_type: str,
    source_format: str,
) -> list[dict[str, Any]]:
    return [
        {
            "trace_schema_version": TRACE_SCHEMA_VERSION,
            "event_id": f"native-{index:06d}",
            "type": extension_type,
            "source": {"name": source_format},
            "payload": {"native_event": deepcopy(event)},
        }
        for index, event in enumerate(source_events)
    ]


def _validate_observer_events(
    events: Sequence[Any],
    trace_schema: dict[str, Any],
) -> list[str]:
    issues: list[str] = []
    trace_start_positions: list[int] = []
    for index, event in enumerate(events):
        if not isinstance(event, Mapping):
            issues.append(f"observer event[{index}] must be a JSON object")
            continue
        for issue in validate_instance(event, trace_schema):
            issues.append(f"observer event[{index}] {issue}")
        event_type = event.get("type")
        if event_type not in OBSERVER_EVENT_TYPES:
            issues.append(
                f"observer event[{index}] type {event_type!r} is not an "
                "externally observable overlay type"
            )
        if event_type == "trace_start":
            trace_start_positions.append(index)
            payload = event.get("payload")
            if isinstance(payload, Mapping) and "observability" in payload:
                issues.append(
                    f"observer event[{index}] must not declare agent-stream "
                    "observability completeness"
                )
        source = event.get("source")
        if not isinstance(source, Mapping) or not _non_empty(source.get("name")):
            issues.append(
                f"observer event[{index}] must identify its observation source"
            )
    if len(trace_start_positions) > 1:
        issues.append("observer events may contain at most one trace_start")
    elif trace_start_positions and trace_start_positions[0] != 0:
        issues.append("observer trace_start must be the first observer event")
    return issues


def main(argv: Sequence[str] | None = None) -> int:
    """Preserve one incomplete neutral or wrapped-native trace."""

    parser = argparse.ArgumentParser(
        description=(
            "Preserve an incomplete neutral or wrapped-native JSONL trace "
            "without creating an EAS run record."
        )
    )
    parser.add_argument("trace", type=Path)
    parser.add_argument("--observation-id", required=True)
    parser.add_argument(
        "--record-created-at",
        help="RFC 3339 serialization time; defaults to the current UTC time",
    )
    parser.add_argument(
        "--source-format",
        default="eas-neutral-jsonl/0.1.0",
        help="name and version of the preserved native source format",
    )
    parser.add_argument(
        "--native-extension-type",
        help=(
            "wrap every native line losslessly in this x-* neutral extension "
            "event type before mapping"
        ),
    )
    parser.add_argument(
        "--observer-events",
        type=Path,
        help=(
            "neutral JSONL facts recorded by the observation harness; a first "
            "trace_start is placed before native events and remaining facts after"
        ),
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    try:
        native_events = _read_jsonl(args.trace)
    except OSError as error:
        print(f"INVALID INPUT: cannot read source trace {args.trace}: {error}")
        return 2

    if (
        args.native_extension_type is not None
        and not NATIVE_EXTENSION_PATTERN.fullmatch(args.native_extension_type)
    ):
        print(
            "INVALID INPUT: --native-extension-type must match "
            "^x-[a-z0-9][a-z0-9._-]*$"
        )
        return 2

    root = _repository_root()
    trace_schema = json.loads(
        (root / "schemas" / "eas-neutral-trace-event-0.1.0.schema.json").read_text(
            encoding="utf-8"
        )
    )
    observer_events: list[Any] = []
    if args.observer_events is not None:
        try:
            observer_events = _read_jsonl(args.observer_events)
        except OSError as error:
            print(
                "INVALID INPUT: cannot read observer events "
                f"{args.observer_events}: {error}"
            )
            return 2
        observer_issues = _validate_observer_events(
            observer_events,
            trace_schema,
        )
        if observer_issues:
            print("INVALID OBSERVER EVENTS")
            for issue in observer_issues:
                print(f"- {issue}")
            return 2

    if args.native_extension_type is None:
        mapped_native_events = native_events
    else:
        mapped_native_events = _wrap_native_events(
            native_events,
            extension_type=args.native_extension_type,
            source_format=args.source_format,
        )

    if observer_events and observer_events[0].get("type") == "trace_start":
        events = [
            observer_events[0],
            *mapped_native_events,
            *observer_events[1:],
        ]
    else:
        events = [*mapped_native_events, *observer_events]

    adapter = NeutralJSONLAdapter()
    adapter.ingest(events)
    try:
        observation = build_incomplete_observation(
            observation_id=args.observation_id,
            record_created_at=args.record_created_at or _now(),
            source_format=args.source_format,
            source_events=events,
            adapter=adapter,
        )
    except ValueError as error:
        print(f"INVALID INCOMPLETE OBSERVATION: {error}")
        return 2

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

    if args.native_extension_type is not None or observer_events:
        observation["extensions"] = {
            "org.eas.observer-overlay": {
                "native_event_count": len(native_events),
                "observer_event_count": len(observer_events),
                "native_extension_type": args.native_extension_type,
            }
        }
    rendered = json.dumps(observation, indent=2, sort_keys=True) + "\n"
    args.output.write_text(rendered, encoding="utf-8")
    print(f"WROTE: {args.output}")
    print("Result: INDETERMINATE")
    print(f"Preserved source events: {len(observation['events'])}")
    if args.native_extension_type is not None or observer_events:
        print(f"Native events preserved: {len(native_events)}")
        print(f"Observer events preserved: {len(observer_events)}")
    print(f"Missing target fields: {len(observation['missing_fields'])}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
