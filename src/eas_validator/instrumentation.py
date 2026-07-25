"""Append-only recording and deterministic compilation for instrumented runs."""

from __future__ import annotations

import copy
from dataclasses import dataclass
from datetime import datetime
import json
import os
from pathlib import Path
from typing import Any, Iterable

from .schema import SchemaIssue, validate_instance
from .validator import ValidationIssue, validate_record


SINGLETON_EVENT_TYPES = (
    "run_started",
    "task_model_recorded",
    "report_finalized",
    "run_finished",
)


@dataclass(frozen=True)
class InstrumentationIssue:
    """One recorder or compiler failure."""

    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.path}: {self.message}"


def _timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _schema_issue(
    issue: SchemaIssue,
    *,
    prefix: str,
) -> InstrumentationIssue:
    suffix = issue.path[1:] if issue.path.startswith("$") else f".{issue.path}"
    return InstrumentationIssue(f"{prefix}{suffix}", issue.message)


def read_event_stream(
    path: Path,
) -> tuple[list[Any], list[InstrumentationIssue]]:
    """Read non-empty JSONL entries in physical order."""

    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        return [], [InstrumentationIssue("$", f"cannot read event stream {path}: {error}")]

    events: list[Any] = []
    issues: list[InstrumentationIssue] = []
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        if not raw_line.strip():
            continue
        try:
            events.append(json.loads(raw_line))
        except json.JSONDecodeError as error:
            issues.append(
                InstrumentationIssue(
                    f"$[line {line_number}]",
                    f"invalid JSON: {error.msg}",
                )
            )
    return events, issues


def append_event(
    stream: Path,
    event: Any,
    event_schema: dict[str, Any],
) -> list[InstrumentationIssue]:
    """Validate and append one canonical JSON event.

    The function creates the stream file when needed, but never creates parent
    directories or modifies the stream when validation fails.
    """

    issues = [
        _schema_issue(issue, prefix="$")
        for issue in validate_instance(event, event_schema)
    ]
    if issues:
        return issues

    if not stream.parent.is_dir():
        return [
            InstrumentationIssue(
                "$",
                f"event stream parent directory does not exist: {stream.parent}",
            )
        ]

    encoded = (
        json.dumps(
            event,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")

    try:
        with stream.open("a+b") as handle:
            handle.seek(0, os.SEEK_END)
            size = handle.tell()
            if size:
                handle.seek(-1, os.SEEK_END)
                if handle.read(1) != b"\n":
                    return [
                        InstrumentationIssue(
                            "$",
                            "existing event stream does not end with a newline",
                        )
                    ]
                handle.seek(0, os.SEEK_END)
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
    except OSError as error:
        return [
            InstrumentationIssue("$", f"cannot append event stream {stream}: {error}")
        ]
    return []


def _provenance(events: Iterable[dict[str, Any]]) -> dict[str, list[str]]:
    source_event_refs: list[str] = []
    native_event_refs: list[str] = []
    observer_evidence_refs: list[str] = []
    for event in events:
        source_event_refs.append(event["event_id"])
        for name, destination in (
            ("native_event_refs", native_event_refs),
            ("observer_evidence_refs", observer_evidence_refs),
        ):
            for reference in event[name]:
                if reference not in destination:
                    destination.append(reference)
    return {
        "source_event_refs": source_event_refs,
        "native_event_refs": native_event_refs,
        "observer_evidence_refs": observer_evidence_refs,
    }


def _collection_duplicate_issues(
    record: dict[str, Any],
) -> list[InstrumentationIssue]:
    seen: dict[str, str] = {}
    issues: list[InstrumentationIssue] = []
    for collection in ("decisions", "actions", "evidence"):
        for index, item in enumerate(record[collection]):
            if not isinstance(item, dict) or not isinstance(item.get("id"), str):
                continue
            entity_id = item["id"]
            path = f"$.{collection}[{index}].id"
            if entity_id in seen:
                issues.append(
                    InstrumentationIssue(
                        path,
                        f"duplicate entity id {entity_id!r}; first declared at {seen[entity_id]}",
                    )
                )
            else:
                seen[entity_id] = path
    return issues


def _unresolved_reference_issues(
    record: dict[str, Any],
) -> list[InstrumentationIssue]:
    decision_ids = {
        item.get("id")
        for item in record["decisions"]
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    evidence_ids = {
        item.get("id")
        for item in record["evidence"]
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    issues: list[InstrumentationIssue] = []

    for index, action in enumerate(record["actions"]):
        if not isinstance(action, dict):
            continue
        decision_id = action.get("decision_id")
        if decision_id is not None and decision_id not in decision_ids:
            issues.append(
                InstrumentationIssue(
                    f"$.actions[{index}].decision_id",
                    f"unresolved decision id {decision_id!r}",
                )
            )

    for collection in ("actions", "decisions"):
        for index, item in enumerate(record[collection]):
            if not isinstance(item, dict):
                continue
            for field in (
                "evidence_refs",
                "authority_evidence_refs",
                "rollback_evidence_refs",
            ):
                references = item.get(field, [])
                if not isinstance(references, list):
                    continue
                for reference_index, reference in enumerate(references):
                    if reference not in evidence_ids:
                        issues.append(
                            InstrumentationIssue(
                                f"$.{collection}[{index}].{field}[{reference_index}]",
                                f"unresolved evidence id {reference!r}",
                            )
                        )

    report = record.get("report")
    if isinstance(report, dict):
        verification = report.get("verification", [])
        if isinstance(verification, list):
            for index, claim in enumerate(verification):
                if not isinstance(claim, dict):
                    continue
                references = claim.get("evidence_refs", [])
                if not isinstance(references, list):
                    continue
                for reference_index, reference in enumerate(references):
                    if reference not in evidence_ids:
                        issues.append(
                            InstrumentationIssue(
                                (
                                    f"$.report.verification[{index}]."
                                    f"evidence_refs[{reference_index}]"
                                ),
                                f"unresolved evidence id {reference!r}",
                            )
                        )
    return issues


def _compiled_record(
    events: list[dict[str, Any]],
    by_type: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    started = by_type["run_started"][0]
    task = by_type["task_model_recorded"][0]
    report = by_type["report_finalized"][0]
    finished = by_type["run_finished"][0]
    started_payload = started["payload"]
    finished_payload = finished["payload"]

    state_events = by_type.get("state_entered", [])
    decision_events = by_type.get("decision_recorded", [])
    action_events = by_type.get("action_recorded", [])
    evidence_events = by_type.get("evidence_recorded", [])

    record: dict[str, Any] = {
        "eas_version": "0.1",
        "schema_version": "0.1.0",
        "run_id": started["run_id"],
        "implementation": copy.deepcopy(started_payload["implementation"]),
        "environment": copy.deepcopy(started_payload["environment"]),
        "started_at": started_payload["started_at"],
        "completed_at": finished_payload["completed_at"],
        "record_created_at": finished["recorded_at"],
        "task": copy.deepcopy(task["payload"]["task"]),
        "initial_state": copy.deepcopy(started_payload["initial_state"]),
        "constraints": copy.deepcopy(started_payload["constraints"]),
        "state_history": [
            event["payload"]["state"] for event in state_events
        ],
        "actions": [
            copy.deepcopy(event["payload"]["action"]) for event in action_events
        ],
        "decisions": [
            copy.deepcopy(event["payload"]["decision"]) for event in decision_events
        ],
        "evidence": [
            copy.deepcopy(event["payload"]["evidence"]) for event in evidence_events
        ],
        "final_state": copy.deepcopy(finished_payload["final_state"]),
        "outcome": finished_payload["outcome"],
        "task_result": report["payload"]["task_result"],
        "report": copy.deepcopy(report["payload"]["report"]),
        "mapping": {
            "unmapped_events": [],
            "assumptions": [],
            "indeterminate_properties": [],
        },
    }
    if "predecessor_run_id" in started_payload:
        record["predecessor_run_id"] = started_payload["predecessor_run_id"]
    if "assumptions" in started_payload:
        record["assumptions"] = copy.deepcopy(started_payload["assumptions"])

    field_events: dict[str, list[dict[str, Any]]] = {
        "/run_id": events,
        "/implementation": [started],
        "/environment": [started],
        "/started_at": [started],
        "/initial_state": [started],
        "/constraints": [started],
        "/task": [task],
        "/task_result": [report],
        "/report": [report],
        "/completed_at": [finished],
        "/record_created_at": [finished],
        "/final_state": [finished],
        "/outcome": [finished],
    }
    if "predecessor_run_id" in started_payload:
        field_events["/predecessor_run_id"] = [started]
    if "assumptions" in started_payload:
        field_events["/assumptions"] = [started]
    for index, event in enumerate(state_events):
        field_events[f"/state_history/{index}"] = [event]
    for name, collection in (
        ("decisions", decision_events),
        ("actions", action_events),
        ("evidence", evidence_events),
    ):
        for index, event in enumerate(collection):
            field_events[f"/{name}/{index}"] = [event]

    record["extensions"] = {
        "org.eas.instrumentation-provenance": {
            path: _provenance(source_events)
            for path, source_events in field_events.items()
        }
    }
    return record


def compile_events(
    events: list[Any],
    event_schema: dict[str, Any],
    run_schema: dict[str, Any],
) -> tuple[dict[str, Any] | None, list[InstrumentationIssue]]:
    """Compile validated events into one complete EAS run record."""

    if not events:
        return None, [
            InstrumentationIssue("$", "event stream must contain at least one event")
        ]

    issues: list[InstrumentationIssue] = []
    for index, event in enumerate(events):
        issues.extend(
            _schema_issue(issue, prefix=f"$[{index}]")
            for issue in validate_instance(event, event_schema)
        )
    if issues:
        return None, issues

    typed_events: list[dict[str, Any]] = events
    by_type: dict[str, list[dict[str, Any]]] = {}
    for event in typed_events:
        by_type.setdefault(event["event_type"], []).append(event)

    run_ids = {event["run_id"] for event in typed_events}
    if len(run_ids) != 1:
        issues.append(
            InstrumentationIssue(
                "$",
                f"event stream must contain exactly one run_id; found {sorted(run_ids)!r}",
            )
        )

    seen_event_ids: dict[str, int] = {}
    for index, event in enumerate(typed_events):
        event_id = event["event_id"]
        if event_id in seen_event_ids:
            issues.append(
                InstrumentationIssue(
                    f"$[{index}].event_id",
                    (
                        f"duplicate event id {event_id!r}; first declared at "
                        f"$[{seen_event_ids[event_id]}]"
                    ),
                )
            )
        else:
            seen_event_ids[event_id] = index

    previous_time: datetime | None = None
    for index, event in enumerate(typed_events):
        recorded_at = _timestamp(event["recorded_at"])
        if previous_time is not None and recorded_at < previous_time:
            issues.append(
                InstrumentationIssue(
                    f"$[{index}].recorded_at",
                    "recording timestamps must be non-decreasing in physical append order",
                )
            )
        previous_time = recorded_at

    for event_type in SINGLETON_EVENT_TYPES:
        count = len(by_type.get(event_type, []))
        if count != 1:
            issues.append(
                InstrumentationIssue(
                    "$",
                    f"event type {event_type!r} must appear exactly once; found {count}",
                )
            )

    if typed_events[0]["event_type"] != "run_started":
        issues.append(
            InstrumentationIssue("$[0].event_type", "first event must be run_started")
        )
    if typed_events[-1]["event_type"] != "run_finished":
        issues.append(
            InstrumentationIssue(
                f"$[{len(typed_events) - 1}].event_type",
                "last event must be run_finished",
            )
        )

    if all(len(by_type.get(name, [])) == 1 for name in SINGLETON_EVENT_TYPES):
        positions = {
            name: typed_events.index(by_type[name][0])
            for name in SINGLETON_EVENT_TYPES
        }
        if positions["task_model_recorded"] > positions["report_finalized"]:
            issues.append(
                InstrumentationIssue(
                    f"$[{positions['report_finalized']}].event_type",
                    "report_finalized cannot precede task_model_recorded",
                )
            )

        started_event = by_type["run_started"][0]
        finished_event = by_type["run_finished"][0]
        started_at = _timestamp(started_event["payload"]["started_at"])
        completed_at = _timestamp(finished_event["payload"]["completed_at"])
        if completed_at < started_at:
            issues.append(
                InstrumentationIssue(
                    f"$[{positions['run_finished']}].payload.completed_at",
                    "completed_at cannot precede started_at",
                )
            )
        if started_at > _timestamp(started_event["recorded_at"]):
            issues.append(
                InstrumentationIssue(
                    f"$[{positions['run_started']}].payload.started_at",
                    "started_at cannot be later than the event recording time",
                )
            )
        if completed_at > _timestamp(finished_event["recorded_at"]):
            issues.append(
                InstrumentationIssue(
                    f"$[{positions['run_finished']}].payload.completed_at",
                    "completed_at cannot be later than the event recording time",
                )
            )

    if issues:
        return None, issues

    record = _compiled_record(typed_events, by_type)
    issues.extend(_collection_duplicate_issues(record))
    issues.extend(_unresolved_reference_issues(record))
    issues.extend(
        InstrumentationIssue(issue.path, issue.message)
        for issue in validate_instance(record, run_schema)
    )
    if not issues:
        issues.extend(
            InstrumentationIssue(
                issue.path,
                f"{issue.requirement}: {issue.message}",
            )
            for issue in validate_record(record)
        )
    if issues:
        return None, issues
    return record, []


def render_run(record: dict[str, Any]) -> str:
    """Return canonical, reproducible JSON for a compiled run."""

    return json.dumps(
        record,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n"
