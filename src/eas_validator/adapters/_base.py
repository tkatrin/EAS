"""Shared conservative accumulation behavior for reference adapters."""

from __future__ import annotations

import copy
from collections.abc import Mapping
from typing import Any

from .protocol import (
    AdapterAssumption,
    AdapterContext,
    IndeterminateField,
    UnmappedEvent,
)


_COLLECTION_COMPLETENESS = {
    "state_history": "lifecycle",
    "actions": "actions",
    "decisions": "decisions",
    "evidence": "evidence",
}

_REQUIRED_TOP_LEVEL = (
    "run_id",
    "environment",
    "started_at",
    "completed_at",
    "record_created_at",
    "task",
    "initial_state",
    "constraints",
    "final_state",
    "outcome",
    "task_result",
    "report",
)


class ConservativeAdapterBase:
    """Base class that records uncertainty instead of filling semantic gaps."""

    adapter_name = "base"
    adapter_version = "0.1.0"
    target_eas_version = "0.1"
    target_schema_version = "0.1.0"

    def __init__(self) -> None:
        self._record: dict[str, Any] = {}
        self._unmapped: list[UnmappedEvent] = []
        self._assumptions: list[AdapterAssumption] = []
        self._indeterminate: list[IndeterminateField] = []
        self._complete_for: set[str] = set()
        self._finalized = False
        self._reset(None)

    def _reset(
        self,
        context: AdapterContext | Mapping[str, Any] | None,
    ) -> None:
        if context is None:
            normalized = AdapterContext()
        elif isinstance(context, AdapterContext):
            normalized = context
        elif isinstance(context, Mapping):
            normalized = AdapterContext(record_fields=context)
        else:
            raise TypeError("context must be AdapterContext, a mapping, or None")

        self._record = copy.deepcopy(dict(normalized.record_fields))
        self._unmapped = []
        self._assumptions = []
        self._indeterminate = []
        self._complete_for = set(normalized.complete_for)
        self._finalized = False

        self._record.setdefault("eas_version", self.target_eas_version)
        self._record.setdefault("schema_version", self.target_schema_version)
        for collection in ("state_history", "actions", "decisions", "evidence"):
            self._record.setdefault(collection, [])
        self._record.setdefault("assumptions", [])

        implementation = self._record.get("implementation")
        if implementation is None:
            implementation = {}
            self._record["implementation"] = implementation
        if isinstance(implementation, dict):
            implementation["adapter"] = self.adapter_name
            implementation["adapter_version"] = self.adapter_version
        else:
            self._add_indeterminate(
                "$.implementation",
                "caller context did not provide an object, so adapter metadata could not be recorded",
            )

        supplied_assumptions = self._record.get("assumptions")
        if isinstance(supplied_assumptions, list):
            for statement in supplied_assumptions:
                if isinstance(statement, str) and statement.strip():
                    self._assumptions.append(
                        AdapterAssumption(statement=statement, source="context.record_fields")
                    )
        else:
            self._add_indeterminate(
                "$.assumptions",
                "caller context supplied assumptions in an unsupported shape",
            )

        for statement in normalized.assumptions:
            self._append_assumption(statement, source="context.assumptions")

    def _append_assumption(
        self,
        statement: Any,
        *,
        source: str,
        source_event_id: str | None = None,
    ) -> bool:
        if not isinstance(statement, str) or not statement.strip():
            return False
        assumption = AdapterAssumption(
            statement=statement,
            source=source,
            source_event_id=source_event_id,
        )
        if assumption not in self._assumptions:
            self._assumptions.append(assumption)
        values = self._record.setdefault("assumptions", [])
        if isinstance(values, list) and statement not in values:
            values.append(statement)
        self._finalized = False
        return True

    def _add_unmapped(
        self,
        index: int,
        reason: str,
        event: Any,
        *,
        event_id: str | None = None,
        partially_mapped: bool = False,
    ) -> None:
        self._unmapped.append(
            UnmappedEvent(
                index=index,
                reason=reason,
                event=copy.deepcopy(event),
                event_id=event_id,
                partially_mapped=partially_mapped,
            )
        )

    def _add_indeterminate(
        self,
        path: str,
        reason: str,
        source_event_ids: tuple[str, ...] = (),
    ) -> None:
        field = IndeterminateField(path, reason, source_event_ids)
        if field not in self._indeterminate:
            self._indeterminate.append(field)

    def _set_top_level(
        self,
        field: str,
        value: Any,
        *,
        index: int,
        event: Any,
        event_id: str | None,
    ) -> bool:
        if field not in self._record:
            self._record[field] = copy.deepcopy(value)
            self._finalized = False
            return True
        if self._record[field] == value:
            return True
        self._add_unmapped(
            index,
            f"conflicts with the previously mapped $.{field} value",
            event,
            event_id=event_id,
            partially_mapped=True,
        )
        return False

    def _append_collection(
        self,
        collection: str,
        value: Any,
        *,
        index: int,
        event: Any,
        event_id: str | None,
    ) -> bool:
        target = self._record.get(collection)
        if not isinstance(target, list):
            self._add_unmapped(
                index,
                f"$.{collection} is not an array in the caller context",
                event,
                event_id=event_id,
            )
            return False
        target.append(copy.deepcopy(value))
        self._finalized = False
        return True

    def _merge_implementation(
        self,
        observed: Any,
        *,
        index: int,
        event: Any,
        event_id: str | None,
    ) -> None:
        target = self._record.get("implementation")
        if not isinstance(observed, Mapping) or not isinstance(target, dict):
            self._add_unmapped(
                index,
                "implementation metadata is not an object",
                event,
                event_id=event_id,
                partially_mapped=True,
            )
            return
        for key, value in observed.items():
            if key in {"adapter", "adapter_version"}:
                if target.get(key) != value:
                    self._add_unmapped(
                        index,
                        f"source implementation.{key} conflicts with the active adapter",
                        event,
                        event_id=event_id,
                        partially_mapped=True,
                    )
                continue
            if key in target and target[key] != value:
                self._add_unmapped(
                    index,
                    f"conflicting implementation.{key} value",
                    event,
                    event_id=event_id,
                    partially_mapped=True,
                )
                continue
            target[key] = copy.deepcopy(value)

    def _finalize_indeterminate(self) -> None:
        if self._finalized:
            return

        for field in _REQUIRED_TOP_LEVEL:
            if field not in self._record:
                self._add_indeterminate(
                    f"$.{field}",
                    "the source trajectory and caller context do not expose this property",
                )

        for collection, coverage_name in _COLLECTION_COMPLETENESS.items():
            if coverage_name not in self._complete_for:
                self._add_indeterminate(
                    f"$.{collection}",
                    f"the source does not declare {coverage_name!r} coverage complete; mapped entries may be partial",
                )

        self._mark_missing_object_fields(
            "task",
            (
                "description",
                "primary_class",
                "secondary_classes",
                "candidate_classes",
                "classification_basis",
                "acceptance_criteria",
            ),
        )
        self._mark_missing_object_fields("environment", ("name", "revision"))
        self._mark_missing_object_fields("initial_state", ("summary", "revision"))
        self._mark_missing_object_fields("final_state", ("summary", "revision"))
        self._mark_missing_object_fields(
            "report", ("summary", "changes", "verification", "limitations", "unresolved")
        )

        implementation = self._record.get("implementation")
        if isinstance(implementation, Mapping):
            for field in ("name", "version"):
                if field not in implementation:
                    self._add_indeterminate(
                        f"$.implementation.{field}",
                        "the adapter identifies itself but the source does not identify the agent implementation",
                    )

        required_by_collection = {
            "actions": (
                "id",
                "description",
                "material",
                "materiality",
                "authority",
                "evidence_refs",
            ),
            "decisions": (
                "id",
                "question",
                "options",
                "choice",
                "disposition",
                "basis",
                "risk",
                "reversibility",
                "authority",
                "evidence_refs",
            ),
            "evidence": (
                "id",
                "kind",
                "description",
                "result",
                "source",
                "origin",
                "capture",
                "observed_at",
                "recorded_at",
            ),
        }
        for collection, required_fields in required_by_collection.items():
            values = self._record.get(collection)
            if not isinstance(values, list):
                continue
            for index, value in enumerate(values):
                if not isinstance(value, Mapping):
                    self._add_indeterminate(
                        f"$.{collection}[{index}]",
                        "the mapped value is not an object",
                    )
                    continue
                source_ids = ()
                source_event_id = value.get("_source_event_id")
                if isinstance(source_event_id, str):
                    source_ids = (source_event_id,)
                for field in required_fields:
                    if field not in value:
                        self._add_indeterminate(
                            f"$.{collection}[{index}].{field}",
                            "the source event does not expose this property",
                            source_ids,
                        )
                if collection == "actions" and value.get("material") is True:
                    if "decision_id" not in value:
                        self._add_indeterminate(
                            f"$.actions[{index}].decision_id",
                            "no explicit decision reference was observed for the material action",
                            source_ids,
                        )
                if collection == "actions":
                    materiality = value.get("materiality")
                    dimensions = (
                        "changes_project_state",
                        "creates_external_effect",
                        "consumes_significant_resources",
                        "expands_authority",
                        "changes_security_or_privacy_posture",
                        "difficult_to_reverse",
                    )
                    if isinstance(materiality, Mapping):
                        for dimension in dimensions:
                            if dimension not in materiality:
                                self._add_indeterminate(
                                    f"$.actions[{index}].materiality.{dimension}",
                                    "the source event does not expose this materiality dimension",
                                    source_ids,
                                )

        decisions = self._record.get("decisions")
        decisions_by_id = {
            item.get("id"): (index, item)
            for index, item in enumerate(decisions)
            if isinstance(item, Mapping) and isinstance(item.get("id"), str)
        } if isinstance(decisions, list) else {}
        actions = self._record.get("actions")
        if isinstance(actions, list):
            material_decision_fields = (
                "impact_level",
                "impact_scope",
                "external_visibility",
                "destructiveness",
                "data_sensitivity",
                "rollback_available",
                "rollback_verified",
                "authorization_source",
                "authorization_scope",
                "authority_evidence_refs",
            )
            for action in actions:
                if not isinstance(action, Mapping) or action.get("material") is not True:
                    continue
                decision_match = decisions_by_id.get(action.get("decision_id"))
                if decision_match is None:
                    continue
                decision_index, decision = decision_match
                source_event_id = decision.get("_source_event_id")
                source_ids = (source_event_id,) if isinstance(source_event_id, str) else ()
                for field in material_decision_fields:
                    if field not in decision:
                        self._add_indeterminate(
                            f"$.decisions[{decision_index}].{field}",
                            "the explicit decision does not expose this material-action property",
                            source_ids,
                        )
                reversibility = decision.get("reversibility")
                if isinstance(reversibility, Mapping):
                    required_reversibility_fields = ["level", "limitations"]
                    if reversibility.get("level") in {"full", "partial"}:
                        required_reversibility_fields.append("mechanism")
                    for field in required_reversibility_fields:
                        if field not in reversibility:
                            self._add_indeterminate(
                                f"$.decisions[{decision_index}].reversibility.{field}",
                                "the explicit decision does not expose this reversibility property",
                                source_ids,
                            )
                authorization_scope = decision.get("authorization_scope")
                if isinstance(authorization_scope, Mapping):
                    for field in (
                        "grantor",
                        "grantee",
                        "action_kind",
                        "target",
                        "environment",
                        "conditions",
                        "valid_at",
                    ):
                        if field not in authorization_scope:
                            self._add_indeterminate(
                                f"$.decisions[{decision_index}].authorization_scope.{field}",
                                "the explicit decision does not expose this authority-grant property",
                                source_ids,
                            )

        self._finalized = True

    def _mark_missing_object_fields(self, name: str, fields: tuple[str, ...]) -> None:
        value = self._record.get(name)
        if value is None:
            return
        if not isinstance(value, Mapping):
            self._add_indeterminate(f"$.{name}", "the mapped value is not an object")
            return
        for field in fields:
            if field not in value:
                self._add_indeterminate(
                    f"$.{name}.{field}",
                    "the source trajectory and caller context do not expose this property",
                )

    def build_run_record(self) -> dict[str, Any]:
        """Return the mapped partial record without embedding adapter diagnostics."""

        self._finalize_indeterminate()
        record = copy.deepcopy(self._record)
        for collection in ("actions", "decisions", "evidence"):
            values = record.get(collection)
            if isinstance(values, list):
                for value in values:
                    if isinstance(value, dict):
                        value.pop("_source_event_id", None)
        record["mapping"] = {
            "unmapped_events": [
                f"{item.event_id or f'event[{item.index}]'}: {item.reason}"
                for item in self._unmapped
            ],
            "assumptions": [item.statement for item in self._assumptions],
            "indeterminate_properties": [
                f"{item.path}: {item.reason}" for item in self._indeterminate
            ],
        }
        return record

    def get_unmapped_events(self) -> tuple[UnmappedEvent, ...]:
        return tuple(copy.deepcopy(self._unmapped))

    def get_assumptions(self) -> tuple[AdapterAssumption, ...]:
        return tuple(self._assumptions)

    def get_indeterminate_fields(self) -> tuple[IndeterminateField, ...]:
        self._finalize_indeterminate()
        return tuple(self._indeterminate)
