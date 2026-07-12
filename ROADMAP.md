# Roadmap

## Phase 1 — Architecture and applicability

- [x] Define scope and non-goals.
- [x] Define core entities, concerns, lifecycle, and invariants.
- [x] Define six task classes and primary/secondary classification rules.
- [x] Define requirement applicability across base, class, action/state, and
  risk/event triggers.
- [x] Operationalize materiality, authority evidence, and reversibility.
- [x] Separate terminal run outcome from task-result satisfaction.
- [x] Separate versioned run, assessment, and report artifacts.
- [ ] Obtain external design review and resolve recorded architecture
  questions.
- [ ] Model nested tasks, concurrency, and delegation.

## Phase 2 — Normative specifications

- [x] Publish the EAS-000 through EAS-010 core working-draft set.
- [x] Add EAS-011 as the ML/data-science profile.
- [x] Assign stable identifiers to all normative requirements.
- [x] Add automated checks for identifiers, BCP 14 clauses, and selected vague
  terms.
- [x] Record a separate read-only 0.1 editorial review.
- [ ] Resolve review findings that require normative policy decisions.
- [ ] Add security and privacy profiles.

## Phase 3 — Machine-readable records and traceability

- [x] Define versioned schemas for run and behavioral scenario records.
- [x] Define a separate versioned assessment-record schema.
- [x] Define an external artifact-bundle schema and integrity checks.
- [x] Define behavior-corpus and neutral trace-event schemas.
- [x] Create requirement and validator-rule registries.
- [x] Generate a human-readable coverage report from the registries.
- [x] Enforce registry consistency and a coverage non-regression baseline in
  CI.
- [ ] Publish a schema compatibility and migration policy beyond 0.1.0.

## Phase 4 — Reference assessment toolchain

- [x] Implement dependency-free schema and structural validators.
- [x] Implement executable behavioral scenario assessment.
- [x] Expose distinct `validate`, `assess`, and `report` commands.
- [x] Emit immutable-source assessment records with per-requirement results.
- [x] Separate the assessed subject from the schema/structural/behavioral
  assessment level.
- [x] Render terminal, JSON, and Markdown assessment reports.
- [x] Distinguish `pass`, `fail`, `indeterminate`, and `not_applicable`.
- [x] Check external artifact path confinement, byte length, and digest without
  claiming semantic authenticity.
- [ ] Add cryptographic provenance or independent artifact-observation support.

## Phase 5 — Adapters and behavior corpus

- [x] Define a trajectory-to-EAS adapter protocol.
- [x] Define a vendor-neutral JSONL trace format.
- [x] Implement neutral-JSONL and scripted-event reference adapters.
- [x] Preserve unmapped events, explicit assumptions, and indeterminate fields.
- [x] Run a repository-fixture interoperability pilot across both adapters.
- [x] Create a 26-case core corpus across scope, ambiguity, verification,
  authority, applicability, research, and advice failures.
- [x] Create a 7-case ML/data-science failure corpus.
- [x] Cover all six primary task classes with nine executable scenario
  manifests, including one combined-class scenario.
- [ ] Promote high-value definition-only cases to executable manifests.
- [ ] Establish an inter-implementation suite using adapters maintained outside
  the reference implementation.

## Phase 6 — Empirical validation

- [x] Define a reproducible validation-study protocol.
- [x] Record the fixture-based adapter pilot separately from real-world
  evidence.
- [ ] Collect consented trajectories from at least two independent agent
  runtimes.
- [ ] Run repeated and adversarial cases to characterize nondeterminism.
- [ ] Measure adapter agreement, assessor agreement, indeterminate rates,
  false-pass risks, and requirement ambiguity.
- [ ] Revise the specification and coverage baseline from observed failures and
  publish negative results.

## Deferred until governance and evidence support them

- certification marks or certification claims;
- a public registry of conforming implementations;
- standards-body or industry-consensus claims;
- release commitments beyond the EAS 0.1 working draft.

## Governance decisions completed

- [x] Dual licensing: CC BY 4.0 for specifications/documentation and
  Apache-2.0 for software/machine-readable artifacts.
