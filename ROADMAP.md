# Roadmap

## Observation boundary milestone

- [x] Freeze the 19 active requirements, eight calibration scenarios, current
  run schema, first-study results, and ADR-0002.
- [x] Record that native observations and instrumented runs are independent
  assessment subjects.
- [x] Reclassify the existing scenario set as calibration rather than holdout
  evaluation.

## Instrumented-run validation — next

- [x] Define a non-normative reference instrumentation event contract.
- [ ] Implement a recorder and deterministic run compiler.
- [ ] Run an 8-trajectory instrumentation pilot: two runtimes, two tasks, two
  repetitions.
- [ ] Assess run/observation consistency separately from run conformance.
- [ ] Revisit the 19 requirements only after pilot data exist.
- [ ] Prepare a new locked eight-task holdout set for a 32-trajectory study.

## EAS 0.1 minimal core

- [x] Reduce the normative set to 19 active requirements.
- [x] Require full machine checkability, implemented rules, and tests.
- [x] Enforce a maximum of 20 active requirements in registry validation.
- [x] Retire removed working-draft identifiers without reusing them.
- [x] Keep only executable corpus cases.
- [x] Separate schema, structural, and bounded scenario results.
- [x] Preserve immutable source digests and explicit applicability results.
- [x] Provide terminal, JSON, and Markdown reports.

## Reference boundary

- [x] Define a neutral JSONL trace format and adapter protocol.
- [x] Implement two controlled reference adapters.
- [x] Preserve unmapped events and assumptions.
- [x] Record the fixture pilot separately from real-world evidence.
- [ ] Move at least one adapter outside the reference implementation.
- [ ] Add independent artifact observation or signed provenance.

## Empirical validation — next

- [x] Define a prospective real-agent study protocol.
- [x] Lock the eight current scenarios and their source revisions.
- [x] Preserve incomplete runtime observations without fabricating a valid run.
- [x] Repeat the two-run observation preflight.
- [x] Complete the first 16-run single-runtime series after a successful
  preflight.
- [x] Complete the two-run observation preflight on a second independently
  developed runtime.
- [x] Complete the 16-run series for the second runtime.
- [x] Collect consented trajectories from at least two independent runtimes.
- [x] Run at least two repetitions per runtime and scenario.
- [x] Obtain independent blinded ratings from two assessors.
- [x] Report adapter loss, indeterminate rate, assessor agreement, scenario
  failures, and false structural passes.
- [x] Preserve the five independent disagreements without consensus
  rescoring.
- [x] Clarify `EAS-006-R03` applicability and remove the under-specified
  SCN-010 exact-location boundary.
- [x] Define an out-of-project location for required observable artifacts in
  scenarios that forbid project-state changes.
- [x] Add a provenance-preserving observer overlay for caller-known run
  metadata and project state.
- [x] Reprocess one preserved trajectory per runtime with the observer overlay.
- [x] Keep complete run conformance for instrumented runtimes and define a
  smaller native-observation scenario projection over external facts.
- [x] Separate observable and run-semantic expectations in every scenario.
- [x] Assign every active requirement to explicit assessment subjects.
- [x] Recheck the two preserved SCN-001 trajectories with that projection.
- [x] Close the native-observation study at the observation-boundary milestone.
- [ ] Revise, merge, or remove criteria based on observed results.

## Deferred

- ML, security, and privacy profiles until they have executable datasets and
  independent observations;
- nested tasks, concurrency, and delegation;
- certification, conformance marks, and public registries;
- standards-body or industry-consensus claims.
