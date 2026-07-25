# EAS 0.1 Real-Agent Validation Study Protocol

## Claim boundary

This is a prospective protocol. No real-agent validation study has yet been
completed. Repository fixtures and the shared reference adapters do not count
as independent implementations.

## Locked inputs

Use the eight executable EAS 0.1 scenarios without changing requirements,
manifests, adapters, or assessment logic after evaluation starts. Record the
exact repository revision.

Select two independently developed agent runtimes with different native trace
formats. Implement one adapter per format. Adapters must preserve unmapped
events and must not invent decisions, authority, evidence, or lifecycle states.

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
