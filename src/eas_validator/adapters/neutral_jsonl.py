"""Reference adapter for the EAS neutral JSONL trajectory format."""

from __future__ import annotations

import copy
import json
from collections.abc import Iterable, Mapping
from os import PathLike
from pathlib import Path
from typing import Any

from ._base import ConservativeAdapterBase
from .protocol import AdapterContext


TRACE_SCHEMA_VERSION = "0.1.0"

_COMPLETE_DOMAINS = {
    "task",
    "initial_state",
    "constraints",
    "lifecycle",
    "actions",
    "decisions",
    "evidence",
    "final_state",
    "outcome",
    "task_result",
    "report",
}

_BUILT_IN_TYPES = {
    "trace_start",
    "user_message",
    "agent_message",
    "lifecycle_state",
    "decision",
    "tool_call",
    "tool_result",
    "file_change",
    "evidence",
    "project_state",
    "verification_claim",
    "report",
    "run_outcome",
    "assumption",
}

_TOP_LEVEL_KEYS = {
    "trace_schema_version",
    "event_id",
    "type",
    "observed_at",
    "source",
    "payload",
    "extensions",
}

_PAYLOAD_KEYS = {
    "trace_start": {
        "run_id",
        "predecessor_run_id",
        "task",
        "initial_state",
        "constraints",
        "assumptions",
        "implementation",
        "environment",
        "started_at",
        "completed_at",
        "record_created_at",
        "observability",
    },
    "user_message": {"message_id", "text"},
    "agent_message": {"message_id", "channel", "text"},
    "lifecycle_state": {"state"},
    "decision": {"decision"},
    "tool_call": {
        "call_id",
        "tool",
        "operation",
        "description",
        "action_id",
        "material",
        "materiality",
        "authority",
        "authority_evidence_refs",
        "decision_id",
        "evidence_refs",
    },
    "tool_result": {
        "call_id",
        "status",
        "description",
        "output_summary",
        "evidence_id",
        "evidence_kind",
        "evidence_result",
        "source",
        "recorded_at",
    },
    "file_change": {
        "path",
        "change",
        "description",
        "action_id",
        "authority",
        "authority_evidence_refs",
        "decision_id",
        "evidence_id",
        "evidence_refs",
        "before_revision",
        "after_revision",
        "materiality",
        "recorded_at",
    },
    "evidence": {"evidence"},
    "project_state": {"phase", "state"},
    "verification_claim": {"claim"},
    "report": {"report"},
    "run_outcome": {"outcome", "task_result"},
    "assumption": {"statement"},
}


def _contains_extensions(value: Any) -> bool:
    if isinstance(value, Mapping):
        return "extensions" in value or any(_contains_extensions(item) for item in value.values())
    if isinstance(value, list):
        return any(_contains_extensions(item) for item in value)
    return False


def _strip_extensions(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            key: _strip_extensions(item)
            for key, item in value.items()
            if key != "extensions"
        }
    if isinstance(value, list):
        return [_strip_extensions(item) for item in value]
    return copy.deepcopy(value)


class NeutralJSONLAdapter(ConservativeAdapterBase):
    """Map explicit neutral JSONL events without reconstructing hidden intent."""

    adapter_name = "neutral-jsonl"
    adapter_version = TRACE_SCHEMA_VERSION

    def __init__(self) -> None:
        self._seen_event_ids: set[str] = set()
        self._tool_calls: dict[str, dict[str, Any]] = {}
        self._pending_claims: list[dict[str, Any]] = []
        super().__init__()

    def ingest(
        self,
        trajectory: Any,
        context: AdapterContext | Mapping[str, Any] | None = None,
    ) -> None:
        self._reset(context)
        self._seen_event_ids = set()
        self._tool_calls = {}
        self._pending_claims = []

        for index, item in enumerate(self._iter_items(trajectory)):
            event = self._decode_item(item, index)
            if event is None:
                continue
            self._ingest_event(event, index)

        if self._pending_claims:
            report = self._record.get("report")
            if report is None:
                self._record["report"] = {"verification": copy.deepcopy(self._pending_claims)}
            elif isinstance(report, dict):
                verification = report.setdefault("verification", [])
                if isinstance(verification, list):
                    for claim in self._pending_claims:
                        if claim not in verification:
                            verification.append(copy.deepcopy(claim))
                else:
                    self._add_indeterminate(
                        "$.report.verification",
                        "explicit verification claims could not be appended to a non-array field",
                    )
            else:
                self._add_indeterminate(
                    "$.report",
                    "explicit verification claims could not be appended to a non-object report",
                )

        self._finalize_indeterminate()

    @staticmethod
    def _iter_items(trajectory: Any) -> Iterable[Any]:
        if isinstance(trajectory, PathLike):
            with Path(trajectory).open(encoding="utf-8") as handle:
                yield from handle
            return
        if isinstance(trajectory, Mapping):
            yield trajectory
            return
        if isinstance(trajectory, bytes):
            yield trajectory
            return
        if isinstance(trajectory, str):
            yield from trajectory.splitlines() or (trajectory,)
            return
        if not isinstance(trajectory, Iterable):
            raise TypeError("trajectory must be JSONL text, a path, or an iterable of events")
        yield from trajectory

    def _decode_item(self, item: Any, index: int) -> dict[str, Any] | None:
        if isinstance(item, Mapping):
            return copy.deepcopy(dict(item))
        if isinstance(item, bytes):
            try:
                item = item.decode("utf-8")
            except UnicodeDecodeError:
                self._add_unmapped(index, "event bytes are not UTF-8", item)
                return None
        if not isinstance(item, str):
            self._add_unmapped(index, "event is neither an object nor JSON text", item)
            return None
        if not item.strip():
            return None
        try:
            decoded = json.loads(item)
        except json.JSONDecodeError as error:
            self._add_unmapped(
                index,
                f"invalid JSON at column {error.colno}",
                {"raw": item.rstrip("\r\n")},
            )
            return None
        if not isinstance(decoded, dict):
            self._add_unmapped(index, "JSONL event must be an object", decoded)
            return None
        return decoded

    def _ingest_event(self, event: dict[str, Any], index: int) -> None:
        event_id = event.get("event_id")
        if not isinstance(event_id, str) or not event_id.strip():
            self._add_unmapped(index, "event_id must be a non-empty string", event)
            return
        if event_id in self._seen_event_ids:
            self._add_unmapped(index, "duplicate event_id is ambiguous", event, event_id=event_id)
            return
        self._seen_event_ids.add(event_id)

        if event.get("trace_schema_version") != TRACE_SCHEMA_VERSION:
            self._add_unmapped(
                index,
                f"unsupported trace_schema_version; expected {TRACE_SCHEMA_VERSION}",
                event,
                event_id=event_id,
            )
            return

        event_type = event.get("type")
        payload = event.get("payload")
        if not isinstance(event_type, str) or not event_type.strip():
            self._add_unmapped(index, "type must be a non-empty string", event, event_id=event_id)
            return
        if not isinstance(payload, Mapping):
            self._add_unmapped(index, "payload must be an object", event, event_id=event_id)
            return
        payload = dict(payload)

        if event_type not in _BUILT_IN_TYPES:
            reason = (
                "extension event type is not interpreted by the reference adapter"
                if event_type.startswith("x-")
                else "unknown event type is not part of the neutral format"
            )
            self._add_unmapped(index, reason, event, event_id=event_id)
            return

        mapper = getattr(self, f"_map_{event_type}")
        mapper(payload, event, index, event_id)

        extra_top_level = sorted(set(event) - _TOP_LEVEL_KEYS)
        extra_payload = sorted(set(payload) - _PAYLOAD_KEYS[event_type])
        reasons: list[str] = []
        if extra_top_level:
            reasons.append(f"unrecognized top-level fields: {', '.join(extra_top_level)}")
        if extra_payload:
            reasons.append(f"unrecognized payload fields: {', '.join(extra_payload)}")
        if "extensions" in event:
            reasons.append("implementation-specific extensions were not interpreted")
        if _contains_extensions(payload) or _contains_extensions(event.get("source")):
            reasons.append("nested implementation-specific extensions were not interpreted")
        if "observed_at" in event and event_type not in {
            "tool_result",
            "file_change",
            "evidence",
        }:
            reasons.append("event observation time has no lossless target field")
        if "source" in event and event_type not in {"tool_result", "file_change"}:
            reasons.append("event source metadata has no lossless target field")
        if reasons:
            self._add_unmapped(
                index,
                "; ".join(reasons),
                event,
                event_id=event_id,
                partially_mapped=True,
            )

    def _map_trace_start(
        self,
        payload: dict[str, Any],
        event: dict[str, Any],
        index: int,
        event_id: str,
    ) -> None:
        for field in (
            "run_id",
            "predecessor_run_id",
            "task",
            "initial_state",
            "constraints",
            "environment",
            "started_at",
            "completed_at",
            "record_created_at",
        ):
            if field in payload:
                self._set_top_level(
                    field,
                    _strip_extensions(payload[field]),
                    index=index,
                    event=event,
                    event_id=event_id,
                )
        if "implementation" in payload:
            self._merge_implementation(
                _strip_extensions(payload["implementation"]),
                index=index,
                event=event,
                event_id=event_id,
            )
        assumptions = payload.get("assumptions", [])
        if isinstance(assumptions, list):
            for statement in assumptions:
                if not self._append_assumption(
                    statement,
                    source="trace_start",
                    source_event_id=event_id,
                ):
                    self._add_unmapped(
                        index,
                        "trace_start contains a non-string assumption",
                        event,
                        event_id=event_id,
                        partially_mapped=True,
                    )
        elif "assumptions" in payload:
            self._add_unmapped(
                index,
                "trace_start assumptions must be an array",
                event,
                event_id=event_id,
                partially_mapped=True,
            )

        observability = payload.get("observability")
        if observability is not None:
            complete_for = (
                observability.get("complete_for")
                if isinstance(observability, Mapping)
                else None
            )
            if isinstance(complete_for, list) and all(
                isinstance(value, str) for value in complete_for
            ):
                recognized = set(complete_for) & _COMPLETE_DOMAINS
                self._complete_for.update(recognized)
                unknown = sorted(set(complete_for) - _COMPLETE_DOMAINS)
                if unknown:
                    self._add_unmapped(
                        index,
                        f"unknown observability domains: {', '.join(unknown)}",
                        event,
                        event_id=event_id,
                        partially_mapped=True,
                    )
            else:
                self._add_unmapped(
                    index,
                    "observability.complete_for must be an array of strings",
                    event,
                    event_id=event_id,
                    partially_mapped=True,
                )

    def _map_user_message(
        self,
        payload: dict[str, Any],
        event: dict[str, Any],
        index: int,
        event_id: str,
    ) -> None:
        self._add_unmapped(
            index,
            "a general user message has no unambiguous run-record mapping",
            event,
            event_id=event_id,
        )

    def _map_agent_message(
        self,
        payload: dict[str, Any],
        event: dict[str, Any],
        index: int,
        event_id: str,
    ) -> None:
        self._add_unmapped(
            index,
            "an agent message is not treated as a structured report or decision",
            event,
            event_id=event_id,
        )

    def _map_lifecycle_state(
        self,
        payload: dict[str, Any],
        event: dict[str, Any],
        index: int,
        event_id: str,
    ) -> None:
        if "state" not in payload:
            self._add_unmapped(index, "state is missing", event, event_id=event_id)
            return
        self._append_collection(
            "state_history",
            payload["state"],
            index=index,
            event=event,
            event_id=event_id,
        )

    def _map_decision(
        self,
        payload: dict[str, Any],
        event: dict[str, Any],
        index: int,
        event_id: str,
    ) -> None:
        decision = payload.get("decision")
        if not isinstance(decision, Mapping):
            self._add_unmapped(index, "decision must be an object", event, event_id=event_id)
            return
        mapped = _strip_extensions(decision)
        mapped["_source_event_id"] = event_id
        self._append_collection(
            "decisions", mapped, index=index, event=event, event_id=event_id
        )

    def _map_tool_call(
        self,
        payload: dict[str, Any],
        event: dict[str, Any],
        index: int,
        event_id: str,
    ) -> None:
        tool = payload.get("tool")
        operation = payload.get("operation")
        if not isinstance(tool, str) or not isinstance(operation, str):
            self._add_unmapped(
                index,
                "tool and operation must be strings",
                event,
                event_id=event_id,
            )
            return
        call_id = payload.get("call_id", event_id)
        if not isinstance(call_id, str) or not call_id:
            self._add_unmapped(index, "call_id must be a string", event, event_id=event_id)
            return
        action: dict[str, Any] = {
            "id": payload.get("action_id", event_id),
            "description": payload.get("description", f"{tool}: {operation}"),
            "evidence_refs": copy.deepcopy(payload.get("evidence_refs", [])),
            "_source_event_id": event_id,
        }
        for field in (
            "material",
            "materiality",
            "authority",
            "decision_id",
        ):
            if field in payload:
                action[field] = _strip_extensions(payload[field])
        if self._append_collection(
            "actions", action, index=index, event=event, event_id=event_id
        ):
            self._tool_calls[call_id] = {
                "tool": tool,
                "operation": operation,
                "event_id": event_id,
            }
        if "authority_evidence_refs" in payload:
            self._add_unmapped(
                index,
                "action-level authority evidence has no target action field; attach it to the explicit decision",
                event,
                event_id=event_id,
                partially_mapped=True,
            )

    def _map_tool_result(
        self,
        payload: dict[str, Any],
        event: dict[str, Any],
        index: int,
        event_id: str,
    ) -> None:
        call_id = payload.get("call_id")
        status = payload.get("status")
        if not isinstance(call_id, str) or not isinstance(status, str):
            self._add_unmapped(
                index,
                "call_id and status must be strings",
                event,
                event_id=event_id,
            )
            return
        call = self._tool_calls.get(call_id)
        source = payload.get("source")
        if not isinstance(source, str) or not source:
            event_source = event.get("source")
            if isinstance(event_source, Mapping) and isinstance(event_source.get("name"), str):
                source = event_source["name"]
            elif call is not None:
                source = f"neutral trace tool call {call_id} ({call['tool']})"
            else:
                source = f"neutral trace event {event_id}"
        description = payload.get("description") or payload.get("output_summary")
        if not isinstance(description, str) or not description:
            description = f"Tool call {call_id} reported status {status}"
        evidence: dict[str, Any] = {
            "id": payload.get("evidence_id", event_id),
            "kind": payload.get("evidence_kind", "tool"),
            "description": description,
            # A transport-level success is only observed. It is not promoted to
            # a passing verification result unless the source says so.
            "result": payload.get("evidence_result", "observed"),
            "source": source,
            "_source_event_id": event_id,
        }
        if isinstance(event.get("observed_at"), str):
            evidence["observed_at"] = event["observed_at"]
        evidence["origin"] = "tool"
        evidence["capture"] = "imported"
        if isinstance(payload.get("recorded_at"), str):
            evidence["recorded_at"] = payload["recorded_at"]
        self._append_collection(
            "evidence", evidence, index=index, event=event, event_id=event_id
        )

    def _map_file_change(
        self,
        payload: dict[str, Any],
        event: dict[str, Any],
        index: int,
        event_id: str,
    ) -> None:
        path = payload.get("path")
        change = payload.get("change")
        if not isinstance(path, str) or not isinstance(change, str):
            self._add_unmapped(
                index,
                "path and change must be strings",
                event,
                event_id=event_id,
            )
            return
        description = payload.get("description", f"{change} {path}")
        evidence_id = payload.get("evidence_id", f"{event_id}-artifact")
        refs = copy.deepcopy(payload.get("evidence_refs", []))
        if not isinstance(refs, list):
            refs = []
            self._add_unmapped(
                index,
                "evidence_refs is not an array",
                event,
                event_id=event_id,
                partially_mapped=True,
            )
        if evidence_id not in refs:
            refs.append(evidence_id)
        action: dict[str, Any] = {
            "id": payload.get("action_id", event_id),
            "description": description,
            "material": True,
            "materiality": copy.deepcopy(
                _strip_extensions(
                    payload.get("materiality", {"changes_project_state": True})
                )
            ),
            "evidence_refs": refs,
            "_source_event_id": event_id,
        }
        for field in ("authority", "decision_id"):
            if field in payload:
                action[field] = _strip_extensions(payload[field])
        self._append_collection(
            "actions", action, index=index, event=event, event_id=event_id
        )

        evidence: dict[str, Any] = {
            "id": evidence_id,
            "kind": "artifact",
            "description": f"Trace observed file change: {description}",
            "result": "observed",
            "source": (
                event["source"]["name"]
                if isinstance(event.get("source"), Mapping)
                and isinstance(event["source"].get("name"), str)
                else f"neutral trace event {event_id}"
            ),
            "origin": "environment",
            "capture": "imported",
            "artifact_ref": path,
            "_source_event_id": event_id,
        }
        if isinstance(event.get("observed_at"), str):
            evidence["observed_at"] = event["observed_at"]
        if isinstance(payload.get("recorded_at"), str):
            evidence["recorded_at"] = payload["recorded_at"]
        self._append_collection(
            "evidence", evidence, index=index, event=event, event_id=event_id
        )
        if "before_revision" in payload or "after_revision" in payload:
            self._add_unmapped(
                index,
                "file revision details have no lossless action field in the target record",
                event,
                event_id=event_id,
                partially_mapped=True,
            )
        if "authority_evidence_refs" in payload:
            self._add_unmapped(
                index,
                "action-level authority evidence has no target action field; attach it to the explicit decision",
                event,
                event_id=event_id,
                partially_mapped=True,
            )

    def _map_evidence(
        self,
        payload: dict[str, Any],
        event: dict[str, Any],
        index: int,
        event_id: str,
    ) -> None:
        evidence = payload.get("evidence")
        if not isinstance(evidence, Mapping):
            self._add_unmapped(index, "evidence must be an object", event, event_id=event_id)
            return
        mapped = _strip_extensions(evidence)
        if "observed_at" not in mapped and isinstance(event.get("observed_at"), str):
            mapped["observed_at"] = event["observed_at"]
        mapped["_source_event_id"] = event_id
        self._append_collection(
            "evidence", mapped, index=index, event=event, event_id=event_id
        )

    def _map_project_state(
        self,
        payload: dict[str, Any],
        event: dict[str, Any],
        index: int,
        event_id: str,
    ) -> None:
        phase = payload.get("phase")
        state = payload.get("state")
        field = {"initial": "initial_state", "final": "final_state"}.get(phase)
        if field is None or not isinstance(state, Mapping):
            self._add_unmapped(
                index,
                "project_state requires phase initial/final and an object state",
                event,
                event_id=event_id,
            )
            return
        self._set_top_level(
            field,
            _strip_extensions(state),
            index=index,
            event=event,
            event_id=event_id,
        )

    def _map_verification_claim(
        self,
        payload: dict[str, Any],
        event: dict[str, Any],
        index: int,
        event_id: str,
    ) -> None:
        claim = payload.get("claim")
        if not isinstance(claim, Mapping):
            self._add_unmapped(index, "claim must be an object", event, event_id=event_id)
            return
        self._pending_claims.append(_strip_extensions(claim))

    def _map_report(
        self,
        payload: dict[str, Any],
        event: dict[str, Any],
        index: int,
        event_id: str,
    ) -> None:
        report = payload.get("report")
        if not isinstance(report, Mapping):
            self._add_unmapped(index, "report must be an object", event, event_id=event_id)
            return
        self._set_top_level(
            "report",
            _strip_extensions(report),
            index=index,
            event=event,
            event_id=event_id,
        )

    def _map_run_outcome(
        self,
        payload: dict[str, Any],
        event: dict[str, Any],
        index: int,
        event_id: str,
    ) -> None:
        if "outcome" not in payload or "task_result" not in payload:
            self._add_unmapped(
                index,
                "outcome and task_result are required",
                event,
                event_id=event_id,
            )
            return
        for field in ("outcome", "task_result"):
            self._set_top_level(
                field,
                payload[field],
                index=index,
                event=event,
                event_id=event_id,
            )

    def _map_assumption(
        self,
        payload: dict[str, Any],
        event: dict[str, Any],
        index: int,
        event_id: str,
    ) -> None:
        if not self._append_assumption(
            payload.get("statement"),
            source="assumption event",
            source_event_id=event_id,
        ):
            self._add_unmapped(
                index,
                "assumption statement must be a non-empty string",
                event,
                event_id=event_id,
            )
