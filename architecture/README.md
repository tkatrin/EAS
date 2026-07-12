# EAS Architecture

EAS models engineering work as a constrained transformation:

```text
(Task, ProjectState, Context)
              |
              v
      Engineering Agent
              |
              v
(ProjectState', Outcome, TaskResult, Report, Evidence)
```

The architecture describes observable responsibilities and records. It does
not prescribe runtime modules, an LLM, a tool protocol, or a fixed execution
pipeline.

## Logical concerns

| Concern | Governing question | Primary observable output |
|---|---|---|
| Understanding | What is requested, constrained, known, and uncertain? | Task and project-state model |
| Applicability | Which primary, secondary, action, state, and risk obligations apply? | Classification basis and applicable requirement set |
| Lifecycle | What state is the run in, and what transition is justified? | State history and terminal outcome |
| Decision and autonomy | May the agent proceed, or must it escalate, block, or refuse? | Decision and authority record |
| Quality | What checks and review support the result? | Verification and review evidence |
| Communication | What must be communicated, when, and with what limits? | Messages and final report |
| Evidence | Which observable facts support each material claim? | Evidence and external artifact references |

The concerns interact at gates rather than forming a fixed linear sequence.
New evidence can invalidate understanding; a failed check can return a run to
planning or execution; and a changed materiality, authority, or risk field can
force a new autonomy decision from any active state.

## Cross-cutting models

- The [task model](task-model.md) defines six outcome-based classes and the
  distinction between primary, secondary, candidate, and supporting activity.
- [EAS-010](../spec/EAS-010-applicability.md) applies the union of base, class,
  action/state, and risk/event triggers. A label cannot suppress an obligation
  triggered by observable behavior.
- The [decision model](decision-model.md) defines the constraint-first
  proceed/inspect/escalate/block/refuse boundary.
- The [materiality model](materiality-model.md) defines six materiality
  dimensions, structured reversibility, and bounded authority evidence.
- The [evidence model](evidence-model.md) limits claims to observable support
  without requiring private chain-of-thought.
- The [record model](record-model.md) separates versioned run records,
  assessment records, and human report renderings.

## Machine-artifact flow

```text
agent/runtime trajectory
        |
        | adapter (unmapped events and uncertainty preserved)
        v
versioned EAS run record ---- optional external artifact bundle
        |                                      |
        +--------------+-----------------------+
                       v
        schema -> structural -> behavioral assessment
                       |
                       v
             versioned assessment record
                       |
                       v
             terminal/JSON/Markdown report
```

The neutral JSONL trace format is one portable adapter input, not a normative
runtime interface. A run record describes observed or explicitly supplied
facts. An adapter does not infer a decision, authority, or successful check
from an action or transport-level success alone.

An assessment subject answers *what* is being assessed: a run, adapter
mapping, assessment process, conformance report, implementation claim, or the
specification. The assessment level answers *how deeply* that subject was
checked: schema, structural, or behavioral. Keeping those axes separate avoids
attributing an adapter or assessor defect to agent behavior.

Run completion and task satisfaction are separate. `outcome` records whether
control terminated as `completed`, `escalated`, or `blocked`; `task_result`
records `satisfied`, `partially_satisfied`, `not_satisfied`, or
`indeterminate`. A negative experiment can complete successfully as a run
without satisfying a requested implementation outcome.

## Architectural constraints

1. **Runtime independence:** no EAS concept requires a particular model,
   vendor, tool, or transport.
2. **Observable conformance:** assessment uses records and project evidence,
   not private chain-of-thought.
3. **Proportionality:** low-risk work may use compact plans and evidence while
   preserving the same invariants.
4. **Truthful reporting:** claims cannot exceed recorded evidence.
5. **Controlled state change:** every material action is attributable to the
   task and governed by explicit authority.
6. **Independent applicability:** actual action, state, claim, and risk
   triggers cannot be disabled by a task-class label.
7. **Explicit uncertainty:** missing source signals remain unmapped or
   indeterminate rather than becoming invented facts.
8. **Re-entry:** discovery and failed verification may revisit earlier states.

See the [formal model](formal-model.md), [lifecycle diagram](lifecycle.mmd), and
the [architecture decision record](decisions/0001-logical-concerns-not-runtime-modules.md)
for the underlying state and responsibility boundaries.
