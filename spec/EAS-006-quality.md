# EAS-006: Quality

## Dimensions

Quality includes outcome correctness, process discipline, scope control,
regression safety, maintainability where applicable, and report accuracy.

## Requirements

- **EAS-006-R01**: A verification record MUST link each applicable acceptance
  criterion and introduced material risk to a verification claim, evidence
  references, or a recorded reason the check was not run.
- **EAS-006-R02**: Verification evidence MUST identify what was checked and its
  actual result.
- **EAS-006-R03**: The agent MUST NOT claim a check passed unless evidence
  records a successful result for that check.
- **EAS-006-R04**: When a check required by an acceptance criterion or material
  risk cannot be run, the report MUST state that fact, the reason, and the
  resulting limitation.
- **EAS-006-R05**: A review record MUST identify its inspected scope, observed
  unintended changes, and comparison with the task and applicable constraints.
- **EAS-006-R06**: Evidence and the final report MUST preserve each negative
  result or degraded metric that changes a decision, verification status, task
  result, comparison, or limitation.
- **EAS-006-R07**: For data-science or machine-learning work, an evaluation
  claim MUST identify its evaluation protocol and demonstrate compliance with
  the partition rules in EAS-011.
- **EAS-006-R08**: A successful isolated phase MUST NOT by itself be represented
  as proof of successful end-to-end behavior.

Data-science and machine-learning runs are additionally governed by EAS-011.
