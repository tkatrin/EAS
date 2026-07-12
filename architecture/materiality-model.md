# Materiality, Authority, and Reversibility Model

## 1. Material action

An action is material when at least one materiality dimension is true:

```text
material(a) =
    changes_project_state(a)
    OR creates_external_effect(a)
    OR consumes_significant_resources(a)
    OR expands_authority(a)
    OR changes_security_or_privacy_posture(a)
    OR difficult_to_reverse(a)
```

Materiality is evaluated from observable effects and authorized limits, not
from the implementation's confidence or the number of tool calls. A read-only
action can be material when it accesses sensitive data, incurs significant
cost, or crosses an authority boundary.

`significant` means that the action exceeds a limit stated by the task,
project, environment, or assessor scenario. When no explicit limit exists, the
agent records the limit it applied and why that limit is proportionate. An
agent-selected limit is a claim, not independent assessor evidence; without a
scenario, policy, or observable baseline supporting it, the dependent
materiality result is `indeterminate`.

## 2. Decision classification fields

Every decision governing a material action records:

- `impact_level`: `low`, `medium`, `high`, or `critical`;
- `impact_scope`: `local`, `project`, or `external`;
- `external_visibility`: `none`, `internal`, or `public`;
- `destructiveness`: `none`, `modifying`, or `destructive`;
- `data_sensitivity`: `none`, `internal`, `confidential`, or `restricted`;
- `rollback_available`: whether a concrete rollback mechanism exists;
- `rollback_verified`: whether that mechanism was checked for this action;
- `rollback_evidence_refs`: successful direct or imported evidence supporting
  `rollback_verified` when it is true;
- `authorization_source`: the instruction, role, policy, or approval granting
  authority;
- `authorization_scope`: a structured grant containing `grantor`, `grantee`,
  `action_kind`, `target`, `environment`, `conditions`, and `valid_at`;
- `authority_evidence_refs`: observable evidence supporting the authority
  classification.

These fields describe different axes. For example, a public announcement may
be non-destructive but externally visible and only partially reversible.
`impact_level` is the trigger used by EAS-005-R10; `impact_scope` does not
substitute for it.

## 3. Reversibility

Reversibility is a structured assessment:

```json
{
  "level": "partial",
  "mechanism": "git revert",
  "limitations": ["External notifications cannot be recalled"]
}
```

The level is:

- `full`: the relevant prior state can be restored within the authorized
  environment and accepted cost;
- `partial`: some relevant effects cannot be restored;
- `none`: no practical authorized restoration mechanism is known.

The adjectives *reversible*, *partially reversible*, and *irreversible* in
normative prose correspond to `full`, `partial`, and `none`, respectively.

The existence of a nominal mechanism is not proof that rollback works.
`rollback_verified` is a separate decision field and can be true only when
`rollback_evidence_refs` resolves to successful direct or imported evidence.
An irreversible or unverified rollback increases escalation obligations but
does not by itself grant or remove authority.

## 4. Authority evidence

Authority is an observable relationship between a source, scope, actor, target,
and action. A statement such as "the user authorized it" is insufficient when
the evidence does not identify what was authorized.

Authority evidence records the source and supports the bounded
`authorization_scope`. If the evidence does not establish that the grantor can
authorize the recorded action and target, the authority result is
`indeterminate`. Authority cannot be inferred from technical ability,
repository write access, administrator credentials, precedent, or model
confidence alone.

## 5. Classification procedure

Before a material action, the agent or adapter:

1. evaluates all six materiality dimensions;
2. identifies the impact level, scope, visibility, destructiveness, and
   sensitivity axes;
3. records the rollback mechanism, limitations, and verification status;
4. resolves authority evidence and its exact scope;
5. applies the decision matrix in `decision-model.md`;
6. re-evaluates when any material field changes.

When the trace cannot establish a field, an adapter marks the property
unmapped and the assessor returns `indeterminate`; it does not invent a
classification.
