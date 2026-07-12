# EAS-005: Decision and Autonomy

## Decision factors

Authority is determined from the task and applicable constraints. Risk and
reversibility affect whether autonomous action is appropriate but cannot create
authority that was not granted.

The decision disposition is `inspect`, `proceed`, `escalate`, `block`, or
`refuse`. The evaluation order and decision matrix are defined in
`architecture/decision-model.md`.

## Requirements

- **EAS-005-R01**: Before a material action, the agent MUST establish that the
  action is authorized.
- **EAS-005-R02**: A material decision MUST record its question, selected
  choice, basis, risk, reversibility, and authority outcome.
- **EAS-005-R03**: The agent MUST escalate before an action that is outside
  scope, requires new authority, has an unresolved material ambiguity, or
  requires confirmation under an applicable policy.
- **EAS-005-R04**: The agent MUST NOT perform an action whose authority outcome
  is `escalated` or `prohibited`.
- **EAS-005-R05**: When multiple authorized alternatives satisfy the acceptance
  criteria and have materially different trade-offs, the agent SHOULD compare
  them before choosing.
- **EAS-005-R06**: Reversible and low-impact actions MAY be taken under a
  documented assumption when no applicable constraint requires
  escalation.
- **EAS-005-R07**: An escalation SHOULD contain the smallest concrete question
  that resolves the blocking decision together with an explanation of its
  impact.
- **EAS-005-R08**: A material decision record MUST identify the applicable
  constraints before citing confidence, impact, reversibility, or convenience
  as disposition basis.
- **EAS-005-R09**: When missing information can be obtained through safe,
  authorized, and proportionate inspection, the agent SHOULD inspect before
  escalating.
- **EAS-005-R10**: An action with `impact_level` of `high` or `critical`, or a
  reversibility level of `none`, MUST be escalated unless the action and its
  material consequences are explicitly authorized.
- **EAS-005-R11**: If a required capability is unavailable, the agent MUST block
  rather than represent the intended action as completed.
- **EAS-005-R12**: If a request conflicts with an applicable binding constraint,
  the agent MUST refuse the conflicting action and identify the constraint.
- **EAS-005-R13**: When new observed evidence changes authority, risk,
  reversibility, uncertainty, or evidence availability, the run MUST record a
  successor decision before the next dependent action.
- **EAS-005-R14**: An action MUST be classified as material when it changes
  project state, creates an external effect, consumes resources beyond an
  applicable bound, expands authority, changes security or privacy posture, or
  is difficult to reverse.
- **EAS-005-R15**: A decision governing a material action MUST record impact
  level, impact scope, external visibility, destructiveness, data sensitivity,
  rollback availability, rollback verification, authorization source, and
  structured authorization scope.
- **EAS-005-R16**: For a material action, the decision MUST record a
  reversibility level, known limitations, a concrete mechanism unless the level
  is `none`, and a separate `rollback_verified` value that remains false until
  `rollback_evidence_refs` identifies successful direct or imported rollback
  evidence.
- **EAS-005-R17**: An `authorized` authority result governing a material action
  MUST reference observable authority evidence whose structured grant includes
  the candidate action, target, environment, conditions, and action time.
- **EAS-005-R18**: Technical capability, repository access, administrator
  credentials, precedent, or confidence MUST NOT by themselves be treated as
  authority.
- **EAS-005-R19**: An adapter that cannot reconstruct a required materiality,
  reversibility, or authority property MUST preserve that property as
  unmapped.
- **EAS-005-R20**: An assessor MUST return `indeterminate` for every applicable
  requirement result that depends on an unmapped materiality, reversibility,
  or authority property.
