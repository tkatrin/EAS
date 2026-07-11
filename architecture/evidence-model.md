# Evidence Model

## 1. Purpose

Evidence makes EAS conformance reviewable without requiring private
chain-of-thought. It supports claims about what the agent observed, changed,
checked, decided, and could not establish.

Evidence is not a transcript dump. A conforming run records the smallest set of
observable facts needed to support or limit its material claims.

## 2. Evidence dimensions

Every evidence item has:

- **provenance** — where the observation came from;
- **kind** — inspection, test, analysis, user statement, tool result, or
  artifact;
- **result** — passed, failed, observed, not run, or inconclusive;
- **scope** — which claim, action, state, or acceptance criterion it addresses;
- **freshness** — whether it was observed in this run or supplied earlier;
- **reproducibility** — how another assessor can repeat or inspect it when safe.

Evidence strength is claim-relative. A passing unit test may strongly support a
local behavior claim but provide no evidence for production safety or user
intent.

## 3. Evidence obligations by task class

| Task class | Required evidence coverage |
|---|---|
| `change` | Initial and final relevant state, intended diff/artifact, acceptance checks, unintended-change review |
| `diagnose` | Observations or reproduction, hypothesis tests, relevant alternatives, remaining uncertainty |
| `review` | Inspected scope, criteria used, findings linked to evidence, coverage limitations |
| `research` | Source provenance, selection method, synthesis basis, conflicts and unresolved uncertainty |
| `operate` | Authority, pre-action state, observed external effect, post-action status, rollback evidence when applicable |
| `advise` | Material facts, assumptions, alternatives or trade-offs, inference boundary, limitations |

When a run has multiple task classes, its evidence set satisfies the union of
their applicable obligations. Task classification cannot be used to avoid an
evidence obligation created by the actual work.

## 4. Claim-evidence relation

Let `supports(e, c)` mean evidence item `e` materially supports claim `c`. A
report claim is admissible when:

```text
admissible(c) iff
  exists e in E: supports(e, c)
  or c is explicitly marked as assumption, inference, limitation, or unknown
```

A `passed` claim requires at least one `passed` item addressing the same check.
A negative or inconclusive item must not be removed merely because later work
succeeds when the earlier result is material to understanding risk or process.

## 5. Authenticity boundary

The EAS 0.1 structural validator checks record consistency, not evidence
authenticity. Behavioral assessment may inspect referenced artifacts, logs,
repository state, or external systems. A self-authored record alone cannot
prove that an action or check occurred.

## 6. Privacy and minimization

Evidence collection must remain within authority and applicable privacy and
security constraints. Secrets, personal data, private reasoning, and unrelated
project content are not collected merely to increase audit detail. Redacted
evidence records preserve kind, result, scope, and the effect of redaction on
confidence.
