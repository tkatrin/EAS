# EAS-001: Terminology

## Terms

**Action** — an observable operation performed by an agent or delegated actor.

**Applicable constraint** — a user instruction, project rule, policy,
permission boundary, or environmental limit governing a run.

**Assessment subject** — the single kind of entity whose requirements are
aggregated in one assessment record: `run`, `adapter_mapping`,
`assessment_process`, `conformance_report`, `implementation_claim`, or
`specification`.

**Decision** — a selection among proceeding, choosing an alternative,
escalating, stopping, or making no change.

**Engineering agent** — a system that transforms project state in response to
an engineering task and produces a report of the work.

**Evidence** — an observable record supporting or contradicting a claim.

**Material action** — an action for which at least one of the six materiality
dimensions in `architecture/materiality-model.md` is true.

**Indeterminate** — an assessment result used when an applicable requirement
cannot be decided from the available observable evidence.

**Not applicable** — an assessment result used when a documented applicability
rule establishes that a requirement does not govern the declared assessment
subject.

**Project state** — the relevant state of artifacts, configuration, data,
tests, documentation, metrics, issues, environment, and known constraints.

**Run** — one bounded execution of an engineering task, represented by a run
record.

**Run outcome** — the terminal control status of a run: `completed`,
`escalated`, or `blocked`. It does not by itself state whether the requested
task result was achieved.

**Scope** — the set of outcomes and state changes authorized by the task and
applicable constraints.

**Task result** — the observed relationship between the delivered result and
the requested outcome: `satisfied`, `partially_satisfied`, `not_satisfied`, or
`indeterminate`.

**Verification** — the collection and evaluation of evidence that work meets
specified acceptance criteria.

## Requirements

- **EAS-001-R01**: Specifications and conformance reports MUST use these terms
  consistently or explicitly define a local specialization.
- **EAS-001-R02**: A local specialization MUST NOT weaken a normative
  requirement by changing the meaning of its terms.
