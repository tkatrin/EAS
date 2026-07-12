# Formal Model

## 1. Run

An EAS run is the tuple:

```text
Run = (id, T, P0, C, S, A, D, E, P1, O, TR, R)
```

where:

- `id` is a stable run identifier;
- `T` is the engineering task;
- `P0` is the observed initial project state;
- `C` is the applicable context and constraint set;
- `S` is the ordered lifecycle-state history;
- `A` is the ordered action history;
- `D` is the decision history;
- `E` is the evidence set;
- `P1` is the observed final project state, which may equal `P0`;
- `O` is the terminal control outcome: `completed`, `escalated`, or `blocked`;
- `TR` is the task result: `satisfied`, `partially_satisfied`,
  `not_satisfied`, or `indeterminate`;
- `R` is the final report.

`O` and `TR` are independent axes. `completed` means that the run reached
truthful reporting and terminated normally; it does not mean that the requested
result was satisfied.

The abstract transformation is:

```text
F(T, P0, C) -> (P1, O, TR, R, E)
```

EAS constrains `F`; it does not prescribe its internal implementation.

The transformation is decomposed conceptually as:

```text
U(T, P0, C, E)       -> M               task/project model
D(a, M, C, H)        -> (d, b, Oe)      disposition, basis, evidence obligation
L(q, M, H)           -> q'              permitted lifecycle transition
V(M, P0, P1, E)      -> VC              verification claims
C(M, H, E, VC, O, TR)-> R               final run report
Assess(subject, level, Run, X) -> AR     separate assessment record
Render(AR)            -> CR              human-readable conformance report
```

These functions are responsibilities, not required runtime modules. `D` is
evaluated for candidate material actions rather than only once per run. `X`
denotes assessor-visible project or external evidence. `AR` does not modify the
source `Run`, and `CR` is distinct from the agent's final run report `R`.

## 2. Lifecycle states

```text
Q = {
  RECEIVED, UNDERSTANDING, PLANNING, EXECUTING,
  VERIFYING, REVIEWING, REPORTING,
  ESCALATED, BLOCKED, COMPLETED
}
```

`COMPLETED` is terminal for a run record. `ESCALATED` and `BLOCKED` are
terminal in EAS 0.1; a response or changed external condition starts a
successor run that references the prior run.

## 3. Transition relation

The permitted relation `delta` is:

```text
RECEIVED      -> UNDERSTANDING | ESCALATED | BLOCKED
UNDERSTANDING -> PLANNING | REPORTING | ESCALATED | BLOCKED
PLANNING      -> EXECUTING | VERIFYING | REPORTING | ESCALATED | BLOCKED
EXECUTING     -> UNDERSTANDING | PLANNING | VERIFYING | ESCALATED | BLOCKED
VERIFYING     -> UNDERSTANDING | PLANNING | EXECUTING | REVIEWING | ESCALATED | BLOCKED
REVIEWING     -> PLANNING | EXECUTING | VERIFYING | REPORTING | ESCALATED | BLOCKED
REPORTING     -> COMPLETED
```

The direct paths to `REPORTING` allow a conforming decision to make no change,
or to answer/report without implementation. They do not waive applicable
verification or evidence requirements.

## 4. Actions and materiality

An action record is:

```text
Action = (id, description, material, materiality, authority,
          decisionId?, evidenceRefs)
```

The structured materiality value contains six Boolean dimensions:

```text
Materiality = (
  changesProjectState,
  createsExternalEffect,
  consumesSignificantResources,
  expandsAuthority,
  changesSecurityOrPrivacyPosture,
  difficultToReverse
)

material(a) = OR(Materiality(a))
```

The predicate is based on observable effect and applicable bounds. Tool-call
count and implementation confidence do not determine materiality.

## 5. Decisions

A material decision is:

```text
Decision = (id, question, options, choice, disposition, basis, risk,
            impactLevel, impactScope, externalVisibility, destructiveness,
            dataSensitivity, rollbackAvailable, rollbackVerified,
            rollbackEvidenceRefs,
            reversibility, authority, authorizationSource,
            authorizationScope, authorityEvidenceRefs, evidenceRefs)
```

`risk` and `impactLevel` use `low`, `medium`, `high`, or `critical`, but they
are not interchangeable: `impactLevel` is the escalation trigger defined by
EAS-005-R10. The other classification axes preserve scope, visibility,
destructiveness, and data sensitivity rather than collapsing them into one
score.

Reversibility is structured as:

```text
Reversibility = (level, mechanism?, limitations)
level in {full, partial, none}
```

`mechanism` is required for `full` and `partial`. `rollbackAvailable` and
`rollbackVerified` remain separate because naming a mechanism does not prove
that it works. A true `rollbackVerified` value has at least one successful
direct or imported item in `rollbackEvidenceRefs`.

Authorization scope is a bounded grant:

```text
AuthorizationScope = (grantor, grantee, actionKind, target,
                      environment, conditions, validAt)
```

`authority` is one of:

- `authorized`: within known user/project authority;
- `escalated`: requires external direction or approval;
- `prohibited`: conflicts with an applicable constraint.

The decision disposition is one of `inspect`, `proceed`, `escalate`, `block`,
or `refuse`. Authority and disposition are distinct: an authorized action may
still be blocked by unavailable capability, while a prohibited action must be
refused regardless of confidence. An `authorized` result is supported by
`authorityEvidenceRefs`; technical capability or access alone is not authority.

## 6. Evidence

Evidence is an observable record:

```text
Evidence = (id, kind, description, result, source, origin, capture,
            observedAt, recordedAt, artifactRef?)
```

EAS 0.1 evidence kinds are `inspection`, `test`, `analysis`, `user`, `tool`,
and `artifact`. Results are `passed`, `failed`, `observed`, `not_run`, and
`inconclusive`. `origin` is `agent`, `user`, `tool`, `environment`, or
`assessor`; `capture` is `direct`, `imported`, or `self_reported`.

`observedAt` records when the underlying fact was observed, while `recordedAt`
records when the evidence item was written into the run record. Self-reported
evidence alone does not establish that a material action, check, external
effect, or rollback occurred. Evidence is not required to contain private
reasoning or hidden model state.

## 7. Assessments

An assessment record is separate from its source run:

```text
Assessment = (id, subject, level, assessor, sourceRun, time,
              registries, scenarioSet?, requirementResults,
              aggregate, limitations)
```

`subject` is exactly one of `run`, `adapter_mapping`, `assessment_process`,
`conformance_report`, `implementation_claim`, or `specification`. `level` is
`schema`, `structural`, or `behavioral`. Subject determines whose obligations
are aggregated; level determines how those obligations were checked.

Each requirement result is `pass`, `fail`, `indeterminate`, or
`not_applicable`. Failures of an adapter or assessor are not added to a run's
aggregate; they belong to assessment records with the corresponding subject.
A human-readable conformance report is rendered from the versioned assessment
record and preserves its subject, level, failures, indeterminate results, and
limitations.

## 8. Invariants

For every structurally conforming run:

1. `S[0] = RECEIVED`.
2. Every adjacent pair in `S` belongs to `delta`.
3. A run with outcome `completed` ends in `COMPLETED`.
4. A run with outcome `escalated` ends in `ESCALATED`.
5. A run with outcome `blocked` ends in `BLOCKED`.
6. `TR = satisfied` implies `O = completed`; `O = completed` does not imply
   `TR = satisfied`.
7. All evidence references, including authority evidence references, resolve
   to members of `E`.
8. A report never claims a check passed unless matching direct or imported
   observable evidence records that result.
9. For every action, `material` equals the disjunction of its six materiality
   dimensions.
10. A material action has a task/scope basis, a governing decision, and
    applicable authority supported by a bounded authorization scope.
11. A destructive, reversibility-`none`, externally visible, or
    authority-expanding action is not performed under `escalated` or
    `prohibited` authority.
12. A high- or critical-impact action, or an action with reversibility `none`,
    is not performed without explicit authorization of its material
    consequences.
13. `P1` may equal `P0`; no-change is a valid engineering result when justified.
14. The run exposes `O` and `TR` separately, and `R` does not represent normal
    run completion as task satisfaction.

## 9. Conformance boundary

Structural conformance can be checked from a run record. Behavioral conformance
may additionally require inspection of the project, task, permissions, and
external effects. Adapter mapping and assessment-process correctness are
separate assessment subjects. EAS 0.1 explicitly does not claim that a JSON
record alone proves behavioral conformance or evidence authenticity.
