"""Reference adapter for a compact scripted-event baseline format."""

from __future__ import annotations

import copy
from collections.abc import Iterable, Mapping
from typing import Any

from ._base import ConservativeAdapterBase
from .protocol import AdapterContext


_SET_FIELDS = {
    "run_id",
    "predecessor_run_id",
    "task",
    "initial_state",
    "constraints",
    "final_state",
    "outcome",
    "task_result",
    "report",
    "environment",
    "started_at",
    "completed_at",
    "record_created_at",
}

_APPEND_FIELDS = {"state_history", "actions", "decisions", "evidence"}

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


class ScriptedEventAdapter(ConservativeAdapterBase):
    """Map an explicit operation script into a partial EAS run record.

    This format is intentionally different from the neutral JSONL event model.
    Each script item is an operation (``set``, ``append``, ``assume``, or
    ``declare_complete``), making it useful as an independent deterministic
    baseline.  Values are copied verbatim and semantic fields are never filled
    from neighboring operations.
    """

    adapter_name = "scripted-events"
    adapter_version = "0.1.0"

    def ingest(
        self,
        trajectory: Any,
        context: AdapterContext | Mapping[str, Any] | None = None,
    ) -> None:
        self._reset(context)
        if isinstance(trajectory, Mapping):
            items: Iterable[Any] = (trajectory,)
        elif isinstance(trajectory, Iterable) and not isinstance(
            trajectory, (str, bytes)
        ):
            items = trajectory
        else:
            raise TypeError("scripted trajectory must be an iterable of operation objects")

        for index, raw_event in enumerate(items):
            if not isinstance(raw_event, Mapping):
                self._add_unmapped(index, "script event must be an object", raw_event)
                continue
            event = copy.deepcopy(dict(raw_event))
            event_id_value = event.get("event_id", f"script-{index + 1:04d}")
            event_id = event_id_value if isinstance(event_id_value, str) else None
            operation = event.get("op")
            if not isinstance(operation, str):
                self._add_unmapped(
                    index,
                    "script event op must be a string",
                    event,
                    event_id=event_id,
                )
                continue

            if operation == "set":
                self._map_set(event, index, event_id)
            elif operation == "append":
                self._map_append(event, index, event_id)
            elif operation == "assume":
                self._map_assume(event, index, event_id)
            elif operation == "declare_complete":
                self._map_declare_complete(event, index, event_id)
            else:
                self._add_unmapped(
                    index,
                    "unsupported scripted operation",
                    event,
                    event_id=event_id,
                )

        self._finalize_indeterminate()

    def _map_set(
        self,
        event: dict[str, Any],
        index: int,
        event_id: str | None,
    ) -> None:
        field = event.get("field")
        if field == "implementation":
            self._merge_implementation(
                event.get("value"),
                index=index,
                event=event,
                event_id=event_id,
            )
            return
        if field not in _SET_FIELDS:
            self._add_unmapped(
                index,
                "set field is not supported by the scripted adapter",
                event,
                event_id=event_id,
            )
            return
        if "value" not in event:
            self._add_unmapped(index, "set value is missing", event, event_id=event_id)
            return
        self._set_top_level(
            field,
            event["value"],
            index=index,
            event=event,
            event_id=event_id,
        )

    def _map_append(
        self,
        event: dict[str, Any],
        index: int,
        event_id: str | None,
    ) -> None:
        collection = event.get("collection")
        if collection not in _APPEND_FIELDS:
            self._add_unmapped(
                index,
                "append collection is not supported by the scripted adapter",
                event,
                event_id=event_id,
            )
            return
        if "value" not in event:
            self._add_unmapped(index, "append value is missing", event, event_id=event_id)
            return
        value = copy.deepcopy(event["value"])
        if collection != "state_history":
            if not isinstance(value, Mapping):
                self._add_unmapped(
                    index,
                    f"{collection} value must be an object",
                    event,
                    event_id=event_id,
                )
                return
            value = dict(value)
            if event_id is not None:
                value["_source_event_id"] = event_id
        self._append_collection(
            collection,
            value,
            index=index,
            event=event,
            event_id=event_id,
        )

    def _map_assume(
        self,
        event: dict[str, Any],
        index: int,
        event_id: str | None,
    ) -> None:
        if not self._append_assumption(
            event.get("statement"),
            source="scripted assumption",
            source_event_id=event_id,
        ):
            self._add_unmapped(
                index,
                "assume statement must be a non-empty string",
                event,
                event_id=event_id,
            )

    def _map_declare_complete(
        self,
        event: dict[str, Any],
        index: int,
        event_id: str | None,
    ) -> None:
        fields = event.get("fields")
        if not isinstance(fields, list) or not all(isinstance(item, str) for item in fields):
            self._add_unmapped(
                index,
                "declare_complete fields must be an array of strings",
                event,
                event_id=event_id,
            )
            return
        recognized = set(fields) & _COMPLETE_DOMAINS
        self._complete_for.update(recognized)
        unknown = sorted(set(fields) - _COMPLETE_DOMAINS)
        if unknown:
            self._add_unmapped(
                index,
                f"unknown completeness domains: {', '.join(unknown)}",
                event,
                event_id=event_id,
                partially_mapped=True,
            )
