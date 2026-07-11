# EAS Architecture

EAS models engineering work as a constrained transformation:

```text
(Task, ProjectState, Context)
              |
              v
      Engineering Agent
              |
              v
(ProjectState', Report, Evidence)
```

The architecture separates six concerns. They are logical responsibilities,
not required runtime components.

| Concern | Governing question | Primary output |
|---|---|---|
| Understanding | What is the task and project state? | Task/project model |
| Lifecycle | What phase is the run in, and what is next? | State transition |
| Decision and Autonomy | May the agent proceed, or must it escalate? | Decision record |
| Quality | Is the work adequately verified and reviewed? | Assessment |
| Communication | What must be communicated, when, and with what precision? | Messages/report |
| Evidence | What observable facts support the run's claims? | Evidence records |

These concerns interact at gates rather than forming a fixed linear pipeline.
For example, new evidence can invalidate understanding and return the run to
`UNDERSTANDING`; a failed verification can return it to `PLANNING` or
`EXECUTING`; and an autonomy decision can move it to `ESCALATED` from any
active state.

## Architectural constraints

1. Runtime independence: no EAS concept requires an LLM or a particular tool.
2. Observable conformance: assessment uses records and project evidence, not
   private chain-of-thought.
3. Proportionality: small, low-risk work may use compact plans and evidence.
4. Truthful reporting: claims cannot exceed the evidence recorded.
5. Controlled state change: every material action must be authorized and
   attributable to the task.
6. Re-entrance: discovery and failed verification may revisit earlier states.

See the [formal model](formal-model.md), [task model](task-model.md),
[decision model](decision-model.md), [evidence model](evidence-model.md), and
the Mermaid diagrams in this directory.
