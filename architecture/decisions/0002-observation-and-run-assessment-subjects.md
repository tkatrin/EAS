# ADR-0002: Separate observation and run assessment subjects

## Status

Accepted for the 0.1 working draft.

## Context

Native agent-runtime traces expose commands, tool activity, file changes,
exit codes, artifacts, external effects, harness timestamps, and project state
with varying completeness. They generally do not expose the agent-owned
semantics required by an EAS run record: outcome, task result, lifecycle,
actions, decisions, evidence collection, and final report.

Treating a native trace as a defective run attributes a collection limitation
to the agent. Filling the missing fields in an adapter or assessor invents
semantics and makes the result irreproducible. Restricting EAS to complete run
records, however, would make it usable only by instrumented runtimes.

## Decision

EAS distinguishes five assessment subjects: `observation`, `run`, `adapter`,
`assessor`, and `report`.

An `observation` contains facts recorded directly by a collection harness. It
is assessed only against scenario expectations explicitly classified as
observable. Its result never establishes full EAS run conformance.

A `run` is a complete, versioned EAS run record produced by an agent or
instrumented runtime. Full lifecycle, decision-discipline, authority,
task-result, evidence, reporting, structural, and scenario claims are
available only for this subject.

Adapters preserve native events and uncertainty. They do not synthesize
agent-owned outcome, task result, lifecycle, actions, decisions, report,
authority, or verification claims. An observer overlay may add only facts
known directly to the harness.

Each normative requirement declares its applicable subjects explicitly.
Applicability to `run` does not imply applicability to `observation`.

## Consequences

- Missing agent-owned data in a native trace is an observability limitation,
  not an agent failure.
- Observation and run results have separate aggregates and claims.
- Scenario manifests separate observable expectations from run-semantic
  expectations.
- Complete run conformance requires runtime instrumentation or an equivalent
  explicit run record.
- EAS retains lifecycle, autonomy, authority, evidence, and reporting
  requirements without fabricating them for uninstrumented systems.
