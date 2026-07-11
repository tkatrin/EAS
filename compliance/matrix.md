# EAS 0.1 Compliance Matrix

This matrix records what the initial reference validator can and cannot assess.
`Structural` means directly checked from the JSON record; `scenario` means it
requires an external behavioral fixture or human assessment.

| Area | Structural checks | Scenario or assessor checks |
|---|---|---|
| Version and claim | Version and class fields | Misleading public claims |
| Agent model | Required top-level record fields | Scope control and preservation of unrelated state |
| Understanding | Evidence/reference structure | Inspection sufficiency and assumption quality |
| Lifecycle | Initial state, transitions, terminal outcome | Appropriate re-entry after discovery |
| Autonomy | Decision references and action authority | Actual permission, risk, and escalation timing |
| Quality | Passed claims point to passed evidence | Adequacy of tests and review |
| Communication | Report container and verification list | Accuracy, clarity, and material omissions |
| Evidence | Unique evidence IDs and reference integrity | Authenticity, privacy, and reproducibility |

## Machine-checked requirement mapping

| Requirement | Validator behavior |
|---|---|
| EAS-000-R01 | Requires version `0.1` |
| EAS-002-R01 | Requires top-level fields and a non-empty run ID |
| EAS-004-R01 | Requires `RECEIVED` and at least two states |
| EAS-004-R02 | Checks state names and transition relation |
| EAS-004-R06 | Checks outcome/terminal-state correspondence |
| EAS-005-R02 | Requires material actions to reference a known decision |
| EAS-005-R04 | Rejects performed material actions without authorized status |
| EAS-006-R03 | Requires passed evidence for passed verification claims |
| EAS-007-R05 | Requires a report object and verification list |
| EAS-008-R01 | Checks unique, non-empty evidence IDs |
| EAS-008-R02 | Resolves evidence references |
| EAS-009-R01 | Requires structural class in the structural record format |
| EAS-009-R02 | Aggregates structural invariants |

Behavioral scenario assessment additionally checks declared task class,
outcome, lifecycle states, decision dispositions, material-action bounds,
evidence results, and report verification statuses. These checks establish only
scenario-specific behavioral results as constrained by EAS-009-R10.

## Result vocabulary

- `pass`: all assessed applicable requirements passed;
- `fail`: at least one assessed applicable `MUST` failed;
- `indeterminate`: evidence was insufficient for at least one applicable `MUST`;
- `not_applicable`: the assessor documented why the requirement does not apply.

The current CLI reports only the experimental structural pass/fail subset.
