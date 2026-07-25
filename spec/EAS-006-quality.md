# EAS-006: Verification Claims

## Requirement

- **EAS-006-R03**: A verification claim with status `passed` MUST reference at
  least one evidence record whose result is `passed` and whose capture mode is
  not `self_reported`.

This requirement applies only when the run contains at least one verification
claim whose status is `passed`. A run with no such claim is
`not_applicable`, not a vacuous pass.

Broader quality judgments remain research questions until they have portable,
tested observables.
