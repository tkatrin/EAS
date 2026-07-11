# Roadmap

## Phase 1 — Architecture

- [x] Define scope and non-goals.
- [x] Identify core entities and concerns.
- [x] Define the high-level control flow.
- [ ] Obtain design review and resolve architecture questions.

## Phase 2 — Formal model

- [x] Define inputs, outputs, states, transitions, decisions, and evidence.
- [x] State core invariants.
- [ ] Model nested tasks, concurrency, and delegation.
- [ ] Validate the model against real agent trajectories.
- [x] Define task classes and class-specific lifecycle obligations.
- [x] Define the first formal decision/autonomy matrix.

## Phase 3 — Specifications

- [x] Create the initial EAS-000 through EAS-009 set.
- [x] Assign requirement identifiers.
- [ ] Perform editorial and normative-language review.
- [ ] Add security, privacy, ML, and data-science profiles.

## Phase 4 — Compliance

- [x] Define an experimental run-record schema.
- [x] Implement a dependency-free structural validator.
- [x] Add initial conformance fixtures and tests.
- [ ] Add behavioral scenario tests and implementation adapters.
- [x] Define an executable behavioral scenario manifest and reference assessor.
- [ ] Establish an inter-implementation test suite.

## Phase 5 — Reference implementation

- [x] Provide a minimal record validator.
- [ ] Build a trajectory-to-EAS adapter API.
- [ ] Add a human-readable conformance report.
- [ ] Evaluate at least two independent agent runtimes.

## Deferred until governance decisions

- certification marks;
- a public registry of conforming implementations;
- release commitments beyond the 0.1 working draft.

## Governance decisions completed

- [x] Dual licensing: CC BY 4.0 for specifications/documentation and
  Apache-2.0 for software/machine-readable artifacts.
