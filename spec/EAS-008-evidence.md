# EAS-008: Evidence and Run Records

## Evidence model

Evidence kinds are `inspection`, `test`, `analysis`, `user`, `tool`, and
`artifact`. Results are `passed`, `failed`, `observed`, `not_run`, and
`inconclusive`.

## Requirements

- **EAS-008-R01**: Every evidence record MUST have a unique identifier, kind,
  description, result, and source.
- **EAS-008-R02**: Every evidence reference MUST resolve within the run record.
- **EAS-008-R03**: Evidence MUST preserve every negative or inconclusive result
  that changes a decision, verification status, task result, comparison, or
  reported limitation.
- **EAS-008-R04**: A run record MUST NOT contain secrets or private data unless
  the content is required evidence, its retention is authorized, and no
  privacy-safe reference can satisfy the same evidence obligation.
- **EAS-008-R05**: When redaction is used, the redacted evidence record MUST
  preserve the evidence type and explain the effect of redaction on assessment.
- **EAS-008-R06**: The run record MUST distinguish evidence captured during the
  run from evidence supplied by the user or another system.
- **EAS-008-R07**: Evidence SHOULD be reproducible when reproduction is safe,
  authorized, and practical.
- **EAS-008-R08**: A run MUST identify how its evidence addresses the primary
  task class and every materially applicable secondary task class.
- **EAS-008-R09**: A `change` run MUST preserve evidence of the intended state
  difference, applicable acceptance checks, and review for unintended changes.
- **EAS-008-R10**: A `diagnose` run MUST preserve material observations or
  reproduction, evaluated candidate explanations and their results, the
  supported explanation when one was established, and remaining uncertainty.
- **EAS-008-R11**: A `review` or `research` run MUST preserve, respectively,
  inspected scope, criteria, findings, and coverage limitations; or source
  provenance, selection method, synthesis, and unresolved uncertainty.
- **EAS-008-R12**: An `operate` run MUST preserve action authority, pre-action
  state, whether the action was attempted, whether its effect was observed,
  absent, or indeterminate, post-action status, and rollback evidence when
  rollback is required or performed.
- **EAS-008-R13**: An `advise` run MUST distinguish supporting facts,
  assumptions, inference, alternatives or trade-offs, and limitations.
- **EAS-008-R14**: When multiple task classes apply, the evidence set MUST
  satisfy the union of their applicable obligations.
- **EAS-008-R15**: A run record MUST identify both the normative EAS version and
  the machine schema version.
- **EAS-008-R16**: A run record MUST identify the agent implementation, adapter,
  their versions, and the execution-environment revision used for the run.
- **EAS-008-R17**: A run record MUST store observation time, evidence recording
  time, and run-record creation time in distinct fields without substituting one
  for another.
- **EAS-008-R18**: Timestamps MUST use RFC 3339 date-time values with an
  explicit UTC offset.
- **EAS-008-R19**: A resumed run MUST use a new run identifier, reference its
  immediate predecessor, and leave the predecessor's terminal history
  unchanged.
- **EAS-008-R20**: Implementation-specific fields MUST be contained within a
  namespaced `extensions` object without redefining core field semantics.
- **EAS-008-R21**: An adapter MUST preserve unmapped source events, mapping
  assumptions, and required properties that cannot be reconstructed.
- **EAS-008-R22**: An adapter MUST NOT create a decision, authority fact,
  evidence item, or successful check that is not supported by the source trace
  or supplied context.
- **EAS-008-R23**: Self-reported evidence MUST NOT by itself establish that a
  material action, check, external effect, or rollback occurred; the dependent
  claim requires direct or imported observable evidence.
