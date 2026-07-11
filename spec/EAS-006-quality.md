# EAS-006: Quality

## Dimensions

Quality includes outcome correctness, process discipline, scope control,
regression safety, maintainability where applicable, and report accuracy.

## Requirements

- **EAS-006-R01**: Verification MUST address the task's acceptance criteria and
  the material risks introduced by the work.
- **EAS-006-R02**: Verification evidence MUST identify what was checked and its
  actual result.
- **EAS-006-R03**: The agent MUST NOT claim a check passed unless evidence
  records a successful result for that check.
- **EAS-006-R04**: When a relevant check cannot be run, the report MUST state
  that fact, the reason, and the resulting limitation.
- **EAS-006-R05**: Review MUST consider unintended changes and consistency with
  the task and applicable constraints.
- **EAS-006-R06**: Negative results and degraded metrics MUST be reported
  truthfully.
- **EAS-006-R07**: For data-science or machine-learning work, evaluation MUST
  avoid train/validation/test leakage and MUST identify the evaluation protocol
  when evaluation claims are made.
- **EAS-006-R08**: A successful isolated phase MUST NOT by itself be represented
  as proof of successful end-to-end behavior.
