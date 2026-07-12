# EAS Specification Index

Status of every document below: **EAS 0.1 Working Draft**.

| ID | Title | Role |
|---|---|---|
| [EAS-000](EAS-000-overview.md) | Overview and Conventions | Scope and normative language |
| [EAS-001](EAS-001-terminology.md) | Terminology | Shared vocabulary |
| [EAS-002](EAS-002-agent-model.md) | Engineering Agent Model | Inputs, outputs, and invariants |
| [EAS-003](EAS-003-understanding.md) | Understanding | Task and project-state model |
| [EAS-004](EAS-004-lifecycle.md) | Lifecycle | States and transitions |
| [EAS-005](EAS-005-decision-autonomy.md) | Decision and Autonomy | Authority and escalation |
| [EAS-006](EAS-006-quality.md) | Quality | Verification and review |
| [EAS-007](EAS-007-communication.md) | Communication | Questions, updates, and reports |
| [EAS-008](EAS-008-evidence.md) | Evidence and Run Records | Observable evidence format |
| [EAS-009](EAS-009-compliance.md) | Compliance | Conformance claims and assessment |
| [EAS-010](EAS-010-applicability.md) | Applicability and Task Classification | Primary/secondary classes, applicability triggers, and non-applicability burden |
| [EAS-011](EAS-011-data-science.md) | Data Science and Machine-Learning Profile | Leakage prevention, reproducibility, evaluation, and reporting |

Requirement identifiers are stable within the 0.1 series. Deleted identifiers
must not be reused for unrelated requirements.

EAS-000 through EAS-010 define the current core. EAS-011 is a conditional
profile that supplements the core when a run creates, selects, evaluates, or
reports a statistical or machine-learning artifact or result; EAS-010-R26 is
the normative activation rule.

The architecture also defines the cross-specification [task
model](../architecture/task-model.md), [decision/autonomy
model](../architecture/decision-model.md), [materiality and reversibility
model](../architecture/materiality-model.md), and [versioned record
model](../architecture/record-model.md).

Machine-readable traceability is maintained in the [requirement
registry](../registry/requirements.json) and [validator-rule
registry](../registry/validator-rules.json). The generated [coverage
report](../reports/requirement-coverage.md) describes declared reference-tool
coverage; it is not an empirical-validity or certification report.
