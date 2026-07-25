# EAS 0.1 Executable Scenarios

EAS 0.1 contains eight executable scenarios and no definition-only cases.
Every case has a manifest, a reference run, deterministic assertions, and
machine-readable requirement links.

| ID | Primary class | Controlled focus |
|---|---|---|
| [SCN-001](scenarios/SCN-001-focused-edit.json) | `change` | focused state change and report |
| [SCN-002](scenarios/SCN-002-material-ambiguity.json) | `operate` | escalation without material action |
| [SCN-003](scenarios/SCN-003-failed-verification.json) | `change` | failed evidence cannot support a passed claim |
| [SCN-007](scenarios/SCN-007-diagnosis-without-fix.json) | `diagnose` | bounded no-change diagnosis |
| [SCN-008](scenarios/SCN-008-authorized-operation.json) | `operate` | complete authorized material decision |
| [SCN-010](scenarios/SCN-010-scoped-review.json) | `review` | bounded review projection |
| [SCN-011](scenarios/SCN-011-sourced-research.json) | `research` | bounded research projection |
| [SCN-012](scenarios/SCN-012-bounded-advice.json) | `advise` | bounded advice projection |

All scenario-specific assertions are attributed to EAS-009-R09. Structural
requirements referenced by a manifest are assessed by their own rules. A
failed scenario assertion now produces `fail` for EAS-009-R09; it is no longer
spread as an `indeterminate` result across every referenced requirement.

Passing a fixture proves only that the fixture and reference assessor agree on
that projection. It does not prove real-world evidence authenticity,
certification, or behavior outside the scenario.
