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
