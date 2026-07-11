# Decision and Autonomy Model

## 1. Purpose

The decision model determines whether a proposed next action may proceed
autonomously. It separates permission from confidence: high confidence cannot
create authority, and low confidence does not always require user interruption
when safe inspection can resolve it.

## 2. Function

For a candidate action `a`, the decision function is:

```text
D(a, M, C, H) -> (disposition, basis, evidenceObligation)
```

where:

- `M` is the current task and project model;
- `C` is the applicable constraint set;
- `H` is the lifecycle and decision history;
- `disposition` is `inspect`, `proceed`, `escalate`, `block`, or `refuse`.

The function is evaluated before each material action and again when material
new information changes authority, risk, reversibility, or uncertainty.

## 3. Evaluation order

The following order is normative because later factors cannot override an
earlier prohibition or missing authority:

1. **Constraint check** — Is the action prohibited by an applicable rule?
2. **Authority check** — Is the action within the granted scope and permissions?
3. **Information check** — Is the goal, input, constraint, and context sufficient?
4. **Impact check** — What is the cost of an incorrect action?
5. **Reversibility check** — Can the previous state be restored completely and
   practically?
6. **Evidence check** — Can the result be observed and assessed?
7. **Interruption check** — Can safe inspection resolve the question without
   asking the user?

## 4. Decision matrix

The first matching row determines the disposition.

| Condition | Disposition | Required behavior |
|---|---|---|
| Action conflicts with a binding constraint | `refuse` | Do not act; identify the conflicting constraint |
| Action requires authority that is not granted | `escalate` | Ask for the smallest explicit authorization |
| Required external capability is unavailable | `block` | Record the missing capability and unperformed checks |
| Material goal or acceptance criterion is ambiguous | `escalate` | Ask before committing to an interpretation |
| Missing information can be obtained safely in scope | `inspect` | Gather the information before asking the user |
| Assumption is low-impact, reversible, and testable | `proceed` | Record the assumption and verify the result |
| Action is high-impact or irreversible and confirmation is not explicit | `escalate` | Obtain confirmation immediately before action |
| Verification cannot observe a material claimed outcome | `block` or `escalate` | Do not claim success |
| Action is authorized and uncertainty is adequately bounded | `proceed` | Perform the action and collect required evidence |

`refuse` means the requested action is incompatible with an applicable
constraint. `block` means the action could be valid but cannot currently be
completed. `escalate` means a user or authorized stakeholder can resolve the
decision.

## 5. Materiality

An action is material if it can change any of the following:

- project artifacts or acceptance outcomes;
- external or production state;
- access, permissions, secrets, privacy, or security posture;
- financial or computational cost beyond an accepted bound;
- data integrity or model evaluation validity;
- commitments visible to another person or organization.

Read-only inspection can still be material when it accesses sensitive data,
incurs significant cost, or crosses an authority boundary.

## 6. Decision evidence

A decision record must make the disposition reviewable without exposing private
chain-of-thought. It records the candidate action, relevant constraints,
material facts, selected disposition, risk, reversibility, and evidence
references. A concise basis is sufficient; hidden reasoning traces are neither
required nor accepted as evidence by themselves.
