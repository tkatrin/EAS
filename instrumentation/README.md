# Reference Instrumented-Run Contract

## Scope

This directory defines a small non-normative event contract for the EAS 0.1
instrumented-run pilot. It is a reference collection format, not a required
runtime architecture, vendor integration, or additional conformance profile.

The objective is to determine whether an agent or runtime can state
agent-owned run semantics during execution and later compile them without
guessing. The canonical event schema is
[`schemas/eas-run-event.schema.json`](../schemas/eas-run-event.schema.json).

## Event stream

The transport is UTF-8 JSONL. Each non-empty line is one event object. The
physical line order is the append order.

Every event contains:

- `event_schema_version`;
- `event_id`;
- `event_type`;
- `run_id`;
- `recorded_at`;
- `source`;
- `payload`;
- `native_event_refs`; and
- `observer_evidence_refs`.

`native_event_refs` bind a statement to preserved runtime events.
`observer_evidence_refs` bind it to separately captured external facts. Empty
arrays are allowed and remain visible as absence of corroboration.

## Event types

| Event type | Run-record contribution |
|---|---|
| `run_started` | implementation, environment, start time, initial state, constraints, optional lineage and assumptions |
| `task_model_recorded` | complete task model |
| `state_entered` | one lifecycle state in append order |
| `decision_recorded` | one explicit decision record |
| `action_recorded` | one explicit action record |
| `evidence_recorded` | one explicit evidence record |
| `report_finalized` | task result and final report |
| `run_finished` | completion time, final state, and outcome |

The nested task, action, decision, evidence, report, implementation,
environment, and project-state objects are run-record fragments. The
deterministic compiler validates the completed object against the core run
schema; an event schema pass alone does not establish that the fragment is
complete or semantically valid.

## Source boundary

An event source has kind `agent` or `runtime`. Both kinds represent an
agent-side declaration for compilation. They do not represent an independent
observation.

Observer overlays remain separate and contain harness-known facts such as tool
results, file changes, artifact digests, exit codes, timestamps, and project
state. An adapter may preserve and link both layers but cannot convert one into
the other.

## Reference commands

The dependency-free reference implementation provides two commands:

```bash
PYTHONPATH=src python3 -m eas_validator record event.json \
  --stream run-events.jsonl

PYTHONPATH=src python3 -m eas_validator compile-run run-events.jsonl \
  --output run.json
```

`record` accepts one event JSON object from a file, or from standard input when
the input path is `-`. It validates the object against the event schema and
appends one compact canonical JSON line. Invalid events are not appended. The
parent directory must already exist, and an existing non-empty stream must end
with a newline.

The recorder assumes one writer per stream. It does not provide cross-process
locking, event transport, or runtime lifecycle hooks. Those are runtime
integration concerns, not parts of the reference file format.

`compile-run` writes the complete run only after every event, stream invariant,
core run-schema rule, and structural rule passes. When compilation fails, an
existing output file is left unchanged.

## Deterministic compilation rules

The `eas compile-run` reference command:

1. preserve physical event order;
2. require one run ID and unique event IDs;
3. require non-decreasing `recorded_at` timestamps;
4. require exactly one start, task model, finalized report, and finish event;
5. preserve every state, decision, action, and evidence event in append order;
6. reject duplicate entity IDs and unresolved run-record references;
7. reject missing or conflicting run fields;
8. validate the result against the run schema and structural validator; and
9. emit no run record when any required agent-owned domain is absent.

The first event must be `run_started`, the last must be `run_finished`, and the
task model must precede the finalized report. The compiler rejects a semantic
start or completion time later than its containing event's `recorded_at`, and
rejects completion before start.

`native_event_refs` and `observer_evidence_refs` refer to separately preserved
sources, so the compiler cannot resolve them inside the agent event stream. It
retains them as provenance. References between run entities, such as
`decision_id` and `evidence_refs`, must resolve inside the compiled run.

The compiler does not repair or reinterpret payload content. In particular, it
does not
choose `task_result`, infer authority from tool access, turn a successful exit
code into verification evidence, or use assessor judgment to fill a gap.

`record_created_at` is the `recorded_at` value of the sole `run_finished`
event. That is the first append time at which the stream can represent a
complete run. Using this recorded source value keeps repeated compilation
byte-deterministic and avoids inventing a later wall-clock timestamp.

## Field provenance

The compiler will store field provenance under the run extension
`org.eas.instrumentation-provenance`. Keys are run-record JSON pointers and
values retain the instrumentation and observer references:

```json
{
  "extensions": {
    "org.eas.instrumentation-provenance": {
      "/task_result": {
        "source_event_refs": ["evt-041"],
        "native_event_refs": ["native-report-007"],
        "observer_evidence_refs": ["obs-019"]
      }
    }
  }
}
```

The core field remains `"task_result": "satisfied"`. The extension records
where that value came from; it does not change or validate the value.

A complete runnable stream is provided at
[`examples/instrumentation/minimal-run-events.jsonl`](../examples/instrumentation/minimal-run-events.jsonl).

## Time semantics

`recorded_at` is when the event was appended. A later statement may reference
an earlier native or observer event, but its recording time remains later. The
compiler must not reorder events by referenced source time or represent a late
statement as contemporaneous with the referenced event.
