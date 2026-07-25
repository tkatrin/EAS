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

## Deterministic compilation rules

The planned `eas compile-run` reference command will:

1. preserve physical event order;
2. require one run ID and unique event IDs;
3. require non-decreasing `recorded_at` timestamps;
4. require exactly one start, task model, finalized report, and finish event;
5. preserve every state, decision, action, and evidence event in append order;
6. reject duplicate entity IDs and unresolved references;
7. reject missing or conflicting run fields;
8. validate the result against the run schema and structural validator; and
9. emit no run record when any required agent-owned domain is absent.

It will not repair or reinterpret payload content. In particular, it will not
choose `task_result`, infer authority from tool access, turn a successful exit
code into verification evidence, or use assessor judgment to fill a gap.

The planned `eas record` command will append one independently schema-valid
event. These command names describe the next reference-tool block; they are not
implemented by this contract commit.

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
        "observer_evidence_refs": ["obs-019"]
      }
    }
  }
}
```

The core field remains `"task_result": "satisfied"`. The extension records
where that value came from; it does not change or validate the value.

## Time semantics

`recorded_at` is when the event was appended. A later statement may reference
an earlier native or observer event, but its recording time remains later. The
compiler must not reorder events by referenced source time or represent a late
statement as contemporaneous with the referenced event.
