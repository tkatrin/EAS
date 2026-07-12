# EAS-004: Lifecycle

## States

`RECEIVED`, `UNDERSTANDING`, `PLANNING`, `EXECUTING`, `VERIFYING`, `REVIEWING`,
`REPORTING`, `ESCALATED`, `BLOCKED`, and `COMPLETED`.

The permitted transition relation is defined in
`architecture/formal-model.md`.

The terminal run outcome describes control flow, not task success. A run can
reach `COMPLETED` after truthfully reporting a `partially_satisfied`,
`not_satisfied`, or `indeterminate` task result. `ESCALATED` and `BLOCKED`
indicate why the run stopped; they do not erase work already performed.

## Requirements

- **EAS-004-R01**: A run MUST start in `RECEIVED` and record an ordered state
  history.
- **EAS-004-R02**: Every state transition MUST belong to the permitted
  transition relation.
- **EAS-004-R03**: Lifecycle depth and artifact size SHOULD be proportionate to
  the task; proportionality does not waive required outcomes.
- **EAS-004-R04**: When recorded evidence contradicts understanding or planning,
  the state history MUST return to `UNDERSTANDING` or `PLANNING` before the next
  action that depends on the contradicted field.
- **EAS-004-R05**: Failed verification MUST be followed by correction,
  replanning, escalation, blocking, or truthful reporting that preserves the
  failure.
- **EAS-004-R06**: A run MUST end in `COMPLETED` when `outcome` is `completed`
  and in the corresponding `ESCALATED` or `BLOCKED` state when `outcome` is
  `escalated` or `blocked`.
- **EAS-004-R07**: A successor run that resumes escalated or blocked work SHOULD
  reference the preceding run.
- **EAS-004-R08**: The lifecycle MUST NOT require `EXECUTING` when the task's
  required outcome can be produced without a material state-changing action.
- **EAS-004-R09**: A run containing more than one task class MUST preserve the
  evidence and authority obligations of every applicable class.
