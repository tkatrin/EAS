# EAS 0.1 controlled adapter interoperability pilot

## Claim boundary

This is a reproducible controlled-fixture pilot of two source formats and two
reference adapters. It is not a real-agent validation study: the trajectory
count from real agent runtimes is zero, both adapters live in the same
codebase, and only one task is paired.

The authoritative machine result is
`reports/adapter-pilot.json`. CI reconstructs that file with:

```bash
PYTHONPATH=src python3 -m eas_validator.pilot \
  --check reports/adapter-pilot.json
```

## Paired sources

Both fixtures explicitly represent the same focused-edit task and expected
SCN-001 behavior:

| Source | Format | Adapter | Events |
|---|---|---|---:|
| `examples/traces/neutral-complete.jsonl` | Versioned typed JSONL events | `NeutralJSONLAdapter` | 20 |
| `examples/traces/scripted-focused-edit.json` | Explicit `set`, `append`, `assume`, and completeness operations | `ScriptedEventAdapter` | 30 |

The comparison excludes adapter identity, run identifier, and mapping
diagnostics. It compares 16 semantic fields: task, environment, three run
timestamps, initial state, constraints, lifecycle, actions, decisions,
evidence, assumptions, report, final state, run outcome, and task result.

## Reproducible result

| Measure | Neutral JSONL | Scripted operations | Combined |
|---|---:|---:|---:|
| Source events | 20 | 30 | 50 |
| Events with no unmapped diagnostic | 18 (90%) | 30 (100%) | 48 (96%) |
| Partially mapped events | 1 (5%) | 0 | 1 (2%) |
| Wholly unmapped events | 1 (5%) | 0 | 1 (2%) |
| Events with at least a partial representation | 19 (95%) | 30 (100%) | 49 (98%) |
| Explicit assumptions | 1 | 1 | 2 |
| Indeterminate target properties | 0 | 0 | 0 |
| Run-schema issues | 0 | 0 | 0 |
| Structural issues | 0 | 0 | 0 |
| SCN-001 scenario issues | 0 | 0 | 0 |

The normalized semantic projections agree on all 16 fields and have the same
SHA-256 digest:
`7f14d0d08fed4170e2b961b8fd095d86bec187ff666199688c71e169bc24081b`.

Both records contain eight lifecycle states, two actions, one decision, and
four evidence items. Both distinguish a `completed` run outcome from the
`satisfied` task result and use the same structured materiality,
reversibility, and authority grant.

## Preserved information loss

The neutral adapter reports two source events rather than hiding their loss:

- `evt-007` is partially mapped because source revision details have no
  lossless action field in the target record;
- `evt-018` is wholly unmapped because a free-form final message is not
  promoted to a structured report or decision.

The scripted format has no unmapped event in this fixture because its
operations explicitly name target EAS fields. Its higher mapping rate is a
property of this purpose-built source format, not evidence that it captures
real runtime behavior better.

## Interpretation

This pilot establishes that:

- both adapter implementations satisfy the common protocol on the paired
  fixture;
- two materially different source encodings can produce the same normalized
  semantic projection;
- unmapped and partially mapped events remain observable;
- neither adapter must fabricate a decision or authority result to produce a
  structurally valid record; and
- schema, structural, and bounded scenario outcomes remain separately
  reproducible.

It does not establish:

- compatibility between independent agent runtimes;
- real-world event coverage or evidence authenticity;
- inter-assessor agreement;
- false-positive or false-negative rates;
- generalization beyond SCN-001; or
- full behavioral conformance, because the pilot comparison does not include
  the external artifact bundle used by `eas assess`.

## Verification

The paired pilot and adapter tests cover source parsing, conservative handling
of transport success, no fabricated decisions or authority, incomplete-domain
indeterminacy, invalid and duplicate events, assumptions, defensive copies,
schema/structural/scenario separation, and exact report reproduction.

The next evidence-producing step is the prospective protocol in
`research/validation-study-protocol.md`: two independently developed real
runtimes, a locked 14-task corpus with 12 evaluation tasks, two blinded
assessors, source audits, and preregistered analysis. Until that study is run,
the project must describe this result only as a controlled synthetic adapter
pilot.
