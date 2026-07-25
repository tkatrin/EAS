# EAS 0.1 Real-Agent Validation Study Protocol

## Claim boundary

This is a prospective protocol. No real-agent validation study has yet been
completed. Repository fixtures and the shared reference adapters do not count
as independent implementations.

## Locked inputs

Use the eight executable EAS 0.1 scenarios without changing requirements,
manifests, adapters, or assessment logic after evaluation starts. Record the
exact repository revision.

The prospective study inputs are byte-locked in
[`study-lock-0.1.json`](study-lock-0.1.json). The lock records the source
revision, scenario-set identity, byte length, and SHA-256 digest of every
scenario manifest, registry, schema, adapter, and assessment-toolchain file.
Verify it before collection and again before assessment:

```bash
PYTHONPATH=src python3 -m eas_validator.study_lock \
  --check research/study-lock-0.1.json
```

Any lock failure means the study input changed. Stop the affected study run,
record the deviation, and either restore the locked bytes or create a new
prospective study version before collecting more trajectories.

Select two independently developed agent runtimes with different native trace
formats. Implement one adapter per format. Adapters must preserve unmapped
events and must not invent decisions, authority, evidence, or lifecycle states.

## Observation preflight

Before the study series, repeat the focused-edit and material-ambiguity
calibration tasks once. If the runtime does not expose enough information for a
valid run record, serialize the available source events as an incomplete
observation. The observation must conform to
`schemas/eas-incomplete-observation.schema.json`, list every missing target
field, and report `indeterminate`. It must not contain a partial run record.

The preflight succeeds when both calibration trajectories are preserved
without invented fields and each output is either a valid run record or a
valid incomplete observation. The preflight result is a collection check, not
behavioral conformance evidence. Only then begin the 16-run series for that
runtime. A second independent runtime is still required for the complete
32-trajectory study.

## Runs

Execute every scenario twice on each runtime in isolated initial states:

```text
8 scenarios × 2 runtimes × 2 repetitions = 32 trajectories
```

Record runtime, model, adapter, environment and repository revisions; the full
task and constraints; observable tool events; before/after project state;
artifacts; final report; timestamps; and random seed when supported. Do not
collect private chain-of-thought.

## Assessment

Blind runtime and adapter identity. Two assessors independently rate every
trajectory using only the locked scenario, normalized record, referenced raw
events, and artifacts.

For every active requirement in scope, record `pass`, `fail`,
`indeterminate`, or `not_applicable`, evidence references, and a reason for
every non-pass result. Freeze both rating sets before adjudication.

## Required metrics

- schema and structural pass rate;
- scenario pass rate;
- fraction of unmapped source events;
- fraction of active requirements rated indeterminate;
- raw assessor agreement and Cohen's kappa;
- disagreements by requirement and runtime;
- structural passes followed by scenario failures;
- adapter-specific information loss; and
- repeated-run disagreement within each runtime.

Report negative results and all protocol deviations. Synthetic trajectories
must be reported separately and cannot support claims about real-world
reliability.

## Decision rule

Do not add normative requirements from intuition. After the study, remove or
rewrite requirements with systematic disagreement or unverifiable inputs.
Add a new requirement only with a portable deterministic rule, a failing
fixture, and evidence that the rule addresses an observed study failure.
