"""Public adapter contract for converting trajectories into EAS run records.

Adapters are intentionally separate from assessment.  An adapter may produce a
partial run record when its source trajectory does not expose enough
information; callers must inspect its unmapped events and indeterminate fields
before attempting conformance assessment.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol, runtime_checkable


@dataclass(frozen=True)
class AdapterContext:
    """Explicit caller-supplied context for one adapter ingestion.

    ``record_fields`` is copied into the partial run record before events are
    mapped. ``complete_for`` names source domains whose absence may safely be
    interpreted as an observed empty value rather than missing telemetry.
    """

    record_fields: Mapping[str, Any] = field(default_factory=dict)
    assumptions: tuple[str, ...] = ()
    complete_for: frozenset[str] = frozenset()


@dataclass(frozen=True)
class UnmappedEvent:
    """A source event that could not be represented completely."""

    index: int
    reason: str
    event: Any
    event_id: str | None = None
    partially_mapped: bool = False


@dataclass(frozen=True)
class AdapterAssumption:
    """An assumption explicitly supplied by the source or caller."""

    statement: str
    source: str
    source_event_id: str | None = None


@dataclass(frozen=True)
class IndeterminateField:
    """A target property that the available trajectory cannot establish."""

    path: str
    reason: str
    source_event_ids: tuple[str, ...] = ()


@runtime_checkable
class EASAdapter(Protocol):
    """Protocol implemented by trajectory-to-EAS adapters.

    Implementations reset their state on every ``ingest`` call.  They must not
    infer an agent decision merely from an action or successful result.
    """

    def ingest(
        self,
        trajectory: Any,
        context: AdapterContext | Mapping[str, Any] | None = None,
    ) -> None:
        """Consume one source trajectory and its explicit context."""

    def build_run_record(self) -> dict[str, Any]:
        """Return a defensive copy of the mapped, possibly partial record."""

    def get_unmapped_events(self) -> tuple[UnmappedEvent, ...]:
        """Return source events that were not represented completely."""

    def get_assumptions(self) -> tuple[AdapterAssumption, ...]:
        """Return assumptions explicitly present in the source or context."""

    def get_indeterminate_fields(self) -> tuple[IndeterminateField, ...]:
        """Return target properties that cannot be established from the source."""
