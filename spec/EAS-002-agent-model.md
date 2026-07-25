# EAS-002: Engineering Agent Run Record

An engineering run is represented as:

```text
(Task, Initial Project State, Context)
    -> Engineering Agent
    -> (Final Project State, Outcome, Task Result, Report, Evidence)
```

## Requirements

- **EAS-002-R01**: A run record MUST conform to the selected EAS run schema,
  including run identity, implementation and environment identity, timestamps,
  task and state descriptions, constraints, lifecycle history, actions,
  decisions, evidence, outcome, task result, report, and adapter mapping.
- **EAS-002-R07**: A run MUST identify exactly one recognized primary task
  class and only recognized, distinct candidate and secondary task classes.
- **EAS-002-R10**: A run whose `task_result` is `satisfied` MUST have a
  `completed` outcome.

Task-class selection guidance is informative in EAS 0.1. The validator checks
the recorded classification; it does not infer it from private reasoning.
