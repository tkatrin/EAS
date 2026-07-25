# EAS-008: Evidence and Versions

Evidence kinds are `inspection`, `test`, `analysis`, `user`, `tool`, and
`artifact`. Results are `passed`, `failed`, `observed`, `not_run`, and
`inconclusive`.

## Requirements

- **EAS-008-R01**: Every evidence record MUST have a unique identifier, kind,
  description, result, source, origin, capture mode, observation time, and
  recording time in the shapes required by the run schema.
- **EAS-008-R02**: Every evidence reference MUST resolve within the run record.
- **EAS-008-R15**: A run record MUST identify both the normative EAS version and
  the machine schema version.

These requirements establish record integrity, not real-world authenticity.
Adapter fidelity and external provenance remain explicit limitations.
