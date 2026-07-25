# ADR-0003: Bound reference instrumentation to explicit run events

## Status

Accepted for the EAS 0.1 instrumented-run calibration pilot.

## Context

ADR-0002 separates external observation from a complete EAS run. The first
real-agent study showed that ordinary native traces do not establish outcome,
task result, lifecycle, actions, decisions, report, or a complete evidence
collection without retrospective semantic reconstruction.

The next research question is whether an agent or runtime can record those
properties during execution. A reference mechanism is needed for the pilot,
but making it normative would prematurely require one transport or runtime
architecture.

## Decision

The reference instrumentation contract is a non-normative, append-only JSONL
sequence of eight event types:

1. `run_started`;
2. `task_model_recorded`;
3. `state_entered`;
4. `decision_recorded`;
5. `action_recorded`;
6. `evidence_recorded`;
7. `report_finalized`; and
8. `run_finished`.

Every event identifies its run, event ID, event type, recording time, source,
payload, native-event references, and observer-evidence references.

Agent instrumentation events are declarations by the agent or runtime. They
do not become observer facts merely because they are structured. Observer
events remain a separate source layer and may corroborate or contradict those
declarations.

An adapter preserves events and uncertainty. It does not repair decisions,
choose a task result, infer authority from access, promote an exit code to
successful evidence, or fill absent semantics from assessor judgment.

Compilation is deterministic and fail-closed. A compiler either produces a
complete run record from explicit events or refuses with missing/conflicting
field diagnostics. Field provenance is stored in a namespaced run extension so
the EAS 0.1 core run schema does not change for the pilot.

`recorded_at` is the append time of the instrumentation statement. A late
statement retains its late timestamp. The contract provides no field with
which a later writer can backdate the statement as an earlier recorded event.

## Consequences

- The reference contract is not a new EAS requirement, runtime, or tool API.
- Runtimes may emit equivalent information through another transport.
- A schema-valid event sequence is not automatically a valid run.
- Full run validation still uses `schemas/eas-run.schema.json` and the
  structural validator.
- Run conformance and run/observation consistency remain separate results.
- The current requirements, calibration scenarios, run schema, study results,
  and ADR-0002 stay frozen during the pilot.
