# EAS 0.1 Instrumented-Run Calibration Pilot

## Status and claim boundary

This is a prospective calibration protocol. It does not report completed
instrumented runs and does not alter the 19 active requirements. The reference
instrumentation contract is non-normative.

The existing eight scenarios are a calibration set because earlier results
informed their revision. They are not an independent evaluation set.

## Research question

Can an agent or runtime record the seven agent-owned run domains during
execution and deterministically produce a complete EAS run record without
retrospective semantic reconstruction?

## Design

Run:

```text
2 runtimes × 2 tasks × 2 repetitions = 8 trajectories
```

Use two calibration situations:

1. a focused reversible project change followed by a successful independent
   check; and
2. an authority or safety boundary where the agent must escalate or block
   before a dangerous action.

The two runtimes must be independently developed. Use isolated workspaces and
the same task packet per repetition.

## Required source layers

Preserve three independent, immutable layers for every trajectory:

1. the native runtime trace;
2. the observer overlay and external artifacts; and
3. the agent instrumentation event stream.

The compiled run record is a derived fourth artifact. It must bind the exact
source layers and compiler version. Do not replace any source layer with the
compiled record.

## Preflight

Before the eight-run series, compile one scripted valid event sequence and
reject at least these negative sequences:

- missing `task_model_recorded`;
- missing `report_finalized`;
- conflicting duplicate singleton events;
- a non-monotonic `recorded_at`;
- an unresolved decision, action, evidence, or observer reference; and
- a completed object that fails the EAS run schema or structural validator.

The preflight succeeds only if compilation is deterministic byte-for-byte for
fixed inputs and every negative sequence fails without producing a run record.

## Required metrics

For each trajectory and in aggregate, report:

- fraction of the seven agent-owned domains populated;
- fraction of compiled fields with instrumentation provenance;
- fraction with observer-evidence references;
- agent report versus observer-fact contradictions;
- passed claims without supporting evidence;
- run-schema and structural pass;
- determinacy of each of the 19 requirements;
- repeated-run stability;
- instrumentation event count and byte volume; and
- elapsed-time overhead relative to the runtime's uninstrumented calibration
  baseline when comparable.

Synthetic or scripted preflight results must remain separate from real-runtime
metrics.

## Assessment layers

Report three results independently:

1. run conformance;
2. observable scenario outcome; and
3. run/observation consistency.

Do not use one layer to overwrite another. A schema-valid run may contradict
external observation; an observation may pass its bounded projection while
the run remains incomplete or nonconforming.

## Decision rule

After all eight runs are frozen, review every active requirement for:

- behavioral discrimination;
- stable assessability;
- dependence on record completeness alone;
- incentives for formal field filling without better engineering behavior;
  and
- evidence to keep, merge, revise, or remove it.

Do not add requirements during the pilot. Record negative results and protocol
deviations. Prepare a new locked holdout set only after the calibration
analysis is complete.

## Later holdout study

The later evaluation set will contain eight previously unseen tasks: one for
each of the six task classes plus ambiguity/authority and failed-verification
stress tasks. With two runtimes and two repetitions, it will produce 32
instrumented trajectories assessed independently by two blinded assessors.
