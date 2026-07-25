# EAS-010: Applicability

Applicability is an assessment property, not a way to inflate the number of
agent obligations. EAS 0.1 records independent applicability dimensions so a
class label cannot silently turn a failed or unobserved check into a pass.

## Requirement

- **EAS-010-R18**: Every requirement result MUST record assessment-subject
  match, base, task-class, action-or-state, risk-or-event, and selected-profile
  applicability as independent dimensions.

`not_applicable` and `indeterminate` results also require a reason under
EAS-009-R12. The requirement registry is the source of applicability tags.
