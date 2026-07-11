# Formal Model

## 1. Run

An EAS run is the tuple:

```text
Run = (id, T, P0, C, S, A, D, E, P1, R)
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
- `R` is the final report.

The abstract transformation is:

```text
F(T, P0, C) -> (P1, R, E)
```

EAS constrains `F`; it does not prescribe its internal implementation.

The transformation is decomposed conceptually as:

```text
U(T, P0, C, E)        -> M                 task/project model
D(a, M, C, H)         -> (d, b, Oe)        disposition, basis, evidence obligation
L(q, M, H)            -> q'                permitted lifecycle transition
Q(M, P0, P1, E)       -> assessment        quality assessment
C(M, H, E, assessment)-> report/message    communication artifact
```

These functions are responsibilities, not required runtime modules. `D` is
evaluated for candidate material actions rather than only once per run.

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

## 4. Decisions

A material decision is:

```text
Decision = (id, question, options, choice, disposition, basis, risk,
            reversibility, authority, evidenceRefs)
```

`authority` is one of:

- `authorized`: within known user/project authority;
- `escalated`: requires external direction or approval;
- `prohibited`: conflicts with an applicable constraint.

The decision disposition is one of `inspect`, `proceed`, `escalate`, `block`,
or `refuse`. Authority and disposition are distinct: an authorized action may
still be blocked by unavailable capability, while a prohibited action must be
refused regardless of confidence.

## 5. Evidence

Evidence is an observable record:

```text
Evidence = (id, kind, description, result, source, observedAt)
```

EAS 0.1 evidence kinds are `inspection`, `test`, `analysis`, `user`, `tool`,
and `artifact`. An evidence record may describe a negative result. Evidence is
not required to contain private reasoning or hidden model state.

## 6. Invariants

For every structurally conforming run:

1. `S[0] = RECEIVED`.
2. Every adjacent pair in `S` belongs to `delta`.
3. A run with outcome `completed` ends in `COMPLETED`.
4. A run with outcome `escalated` ends in `ESCALATED`.
5. A run with outcome `blocked` ends in `BLOCKED`.
6. All evidence references resolve to members of `E`.
7. A report never claims a check passed unless matching evidence records that
   result.
8. A material action has a task/scope basis and applicable authority.
9. A destructive, irreversible, externally visible, or authority-expanding
   action is not performed under `escalated` or `prohibited` authority.
10. `P1` may equal `P0`; no-change is a valid engineering result when justified.

## 7. Conformance boundary

Structural conformance can be checked from a run record. Behavioral conformance
may additionally require inspection of the project, task, permissions, and
external effects. EAS 0.1 explicitly does not claim that a JSON record alone
proves behavioral conformance.
