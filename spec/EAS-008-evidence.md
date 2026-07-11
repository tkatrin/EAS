# EAS-008: Evidence and Run Records

## Evidence model

Evidence kinds are `inspection`, `test`, `analysis`, `user`, `tool`, and
`artifact`. Results are `passed`, `failed`, `observed`, `not_run`, and
`inconclusive`.

## Requirements

- **EAS-008-R01**: Every evidence record MUST have a unique identifier, kind,
  description, result, and source.
- **EAS-008-R02**: Every evidence reference MUST resolve within the run record.
- **EAS-008-R03**: Evidence MUST preserve negative and inconclusive results
  needed to understand the run.
- **EAS-008-R04**: A run record MUST NOT contain secrets or private data merely
  to improve audit detail.
- **EAS-008-R05**: Redaction MAY be used, but it MUST preserve enough metadata
  to explain the evidence type and effect on assessment.
- **EAS-008-R06**: The run record MUST distinguish evidence captured during the
  run from evidence supplied by the user or another system.
- **EAS-008-R07**: Evidence SHOULD be reproducible when reproduction is safe,
  authorized, and practical.
- **EAS-008-R08**: A run MUST identify how its evidence addresses the primary
  task class and every materially applicable secondary task class.
- **EAS-008-R09**: A `change` run MUST preserve evidence of the intended state
  difference, applicable acceptance checks, and review for unintended changes.
- **EAS-008-R10**: A `diagnose` run MUST preserve the material observations or
  reproduction, tests of the selected explanation, and remaining uncertainty.
- **EAS-008-R11**: A `review` or `research` run MUST preserve inspected scope or
  source provenance, evaluation criteria or selection method, supported
  findings, and material coverage limitations.
- **EAS-008-R12**: An `operate` run MUST preserve the action authority,
  relevant pre-action state, observed external effect, and post-action status;
  it MUST include rollback evidence when rollback is required or performed.
- **EAS-008-R13**: An `advise` run MUST distinguish supporting facts,
  assumptions, inference, alternatives or trade-offs, and limitations.
- **EAS-008-R14**: When multiple task classes apply, the evidence set MUST
  satisfy the union of their applicable obligations.
