# EAS-004: Lifecycle

The states are `RECEIVED`, `UNDERSTANDING`, `PLANNING`, `EXECUTING`,
`VERIFYING`, `REVIEWING`, `REPORTING`, `ESCALATED`, `BLOCKED`, and `COMPLETED`.
The transition relation is defined in `architecture/formal-model.md`.

## Requirements

- **EAS-004-R01**: A run MUST start in `RECEIVED` and record an ordered state
  history.
- **EAS-004-R02**: Every state transition MUST belong to the permitted
  transition relation.
- **EAS-004-R06**: A run MUST end in `COMPLETED` when `outcome` is `completed`
  and in the corresponding `ESCALATED` or `BLOCKED` state when `outcome` is
  `escalated` or `blocked`.
