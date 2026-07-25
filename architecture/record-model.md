# Versioned Run and Assessment Record Model

## 1. Separation of records

EAS distinguishes four artifacts:

1. **incomplete observation** — preserved source events plus an explicit list
   of target run fields that cannot be established;
2. **run record** — an adapter's observable representation of one engineering
   run;
3. **assessment record** — an assessor's versioned result for a run under a
   requirement set or scenario corpus;
4. **human report** — a rendering of an assessment record.

An assessment does not rewrite the source run record. Multiple assessors can
independently assess the same immutable run record.

An incomplete observation is not a run record and cannot receive a structural
or behavioral pass. Its result is always `indeterminate`. It preserves each
available source event and a non-empty list of missing target paths with
reasons. Once the adapter can establish every required target field, it must
produce a run record instead.
Only externally observable events belong in this envelope; private
chain-of-thought is outside the EAS record model.

## 2. Version identifiers

`eas_version` selects the normative specification series. `schema_version`
selects the machine-record contract. Schema versions use semantic versioning:

- patch: editorial or validation clarification with no accepted-record break;
- minor: backward-compatible fields or enum values;
- major: incompatible record semantics or required-field changes.

Every JSON Schema has a versioned `$id`. The unversioned repository path is a
development convenience and is not a stable schema identifier.

## 3. Run metadata

A run record identifies:

```json
{
  "eas_version": "0.1",
  "schema_version": "0.1.0",
  "run_id": "...",
  "implementation": {
    "name": "...",
    "version": "...",
    "adapter": "...",
    "adapter_version": "..."
  },
  "environment": {
    "name": "...",
    "revision": "..."
  }
}
```

The adapter identity is separate from the agent implementation because mapping
choices can change assessment results without changing the underlying agent.

The run record also separates terminal control status from task satisfaction:

```json
{
  "outcome": "completed",
  "task_result": "not_satisfied"
}
```

This means the run reached truthful reporting and terminated normally, while
the requested outcome was not achieved. `satisfied` requires `completed`, but
`completed` does not imply `satisfied`.

## 4. Time semantics

EAS records three distinct time concepts:

- `observed_at`: when the underlying event or state was observed;
- `recorded_at`: when an evidence item was written into the run record;
- `record_created_at`: when the complete run record was serialized.

Run start and completion times describe the observed execution interval. They
must not be replaced by adapter processing time. All timestamps use RFC 3339
date-time strings with an explicit UTC offset.

## 5. Resumption and lineage

A resumed run has a new `run_id` and references its immediate predecessor with
`predecessor_run_id`. A chain preserves escalation and blocking history rather
than editing an earlier terminal record into a completed record.

## 6. Extensions

Implementation-specific data is permitted only inside `extensions`. Extension
keys use a reverse-domain namespace controlled by the implementation, for
example `org.example.runtime`. Core assessors ignore unknown extension content
unless an explicitly selected profile defines it.

Extensions must not redefine core fields, weaken normative requirements, or be
required to interpret an unqualified EAS core conformance claim.

## 7. Assessment metadata

An assessment record identifies one assessment subject, assessor name and
version, assessment level, scenario set, immutable source artifact, assessment
time, artifact roots or fingerprints, and the exact registry versions used. A
source descriptor records the subject type, stable identifier, and content
digest; schema version and record time are included when the source exposes
them. Every
`not_applicable` or `indeterminate` requirement result includes a non-empty
reason and observable basis when one exists.

Requirement results in one record belong to its declared subject. For example,
a run assessment does not mix failures of the adapter or assessor into the
run's aggregate result; those require assessment records whose subject is
`adapter_mapping` or `assessment_process`.

## 8. Adapter uncertainty

Adapters preserve:

- unmapped source events;
- assumptions introduced by the mapping;
- properties that cannot be reconstructed.

An absent source signal is not converted into a negative fact. Required but
unreconstructable properties result in `indeterminate`, not fabricated
evidence.

## 9. Observer overlay

A collection harness may add neutral events for facts it observed directly,
such as the supplied task, runtime metadata, timestamps, and before/after
project-state digests. Those events remain in the incomplete observation
beside every native event and identify their source.

An observer overlay does not speak for the agent. It cannot declare an agent
decision, verification claim, final report, task result, or complete internal
lifecycle. If those signals are absent from the runtime output, the
corresponding target fields remain `indeterminate`.
