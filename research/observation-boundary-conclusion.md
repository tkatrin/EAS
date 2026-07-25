# EAS 0.1 Observation Boundary Milestone

## Status

Completed on 2026-07-26.

## Result

The first real-agent study established a record-boundary result, not evidence
of full run conformance. Native traces from two independently developed
runtimes preserved 3,552 source events, but none established a complete EAS
run record without semantic invention.

Observer overlays reduced collection loss by adding harness-known task,
runtime, time, evidence, and project-state facts. They did not establish the
seven complete agent-owned domains shared by both runtime captures:

- `outcome`;
- `task_result`;
- `report`;
- `state_history`;
- `actions`;
- `decisions`; and
- the complete `evidence` collection.

ADR-0002 therefore separates external `observation` from instrumented `run`.
Missing agent-owned data in an observation is an observability limitation, not
an agent failure. Observation projections and run-conformance results are not
interchangeable.

## Frozen calibration baseline

Until the prospective instrumented-run pilot is complete, the following form
the EAS 0.1 observation-boundary baseline:

- 19 active requirements;
- the eight existing executable scenarios;
- the current EAS run-record schema;
- the recorded first-study results and independent ratings; and
- ADR-0002.

The eight existing scenarios are a calibration set. They are not an
independent evaluation set because their results informed requirement,
scenario, artifact-handling, and record-boundary revisions.

Changes to this baseline before the pilot require an explicit replacement
milestone and rationale. New requirements, task classes, profiles, or
observation obligations are outside the next pilot.

## Next research question

The next question is whether an agent or runtime can record the seven
agent-owned domains during execution and deterministically compile them into a
complete EAS run record without retrospective reconstruction. A reference
instrumentation contract and small eight-run calibration pilot address that
question.
