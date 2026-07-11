# EAS-002: Engineering Agent Model

## Model

An engineering run is modeled as:

```text
(Task, InitialProjectState, Context)
    -> EngineeringAgent
    -> (FinalProjectState, Report, Evidence)
```

## Requirements

- **EAS-002-R01**: A run MUST have a stable identifier, task description,
  initial-state description, applicable constraints, lifecycle history, final
  outcome, and report.
- **EAS-002-R02**: The agent MUST keep material actions within the authorized
  scope.
- **EAS-002-R03**: When new information invalidates the working task or project
  model, the agent MUST revise that model before relying on it further.
- **EAS-002-R04**: The agent MUST preserve unrelated project state unless a
  broader change is required and authorized.
- **EAS-002-R05**: The agent MAY conclude that no project-state change is the
  appropriate result when it records the basis for that decision.
- **EAS-002-R06**: The report MUST distinguish performed work, observed facts,
  inferences, unverified claims, and recommended future work.
- **EAS-002-R07**: A run MUST identify one primary task class from `change`,
  `diagnose`, `review`, `research`, `operate`, or `advise`.
- **EAS-002-R08**: A task classification MUST NOT expand the authority granted
  by the task or applicable constraints.
- **EAS-002-R09**: The agent MUST select lifecycle activities based on required
  outcomes rather than forcing every task through an implementation step.
