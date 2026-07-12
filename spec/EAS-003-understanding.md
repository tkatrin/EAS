# EAS-003: Understanding

## Purpose

Understanding establishes a sufficient task and project model before material
action.

## Inputs

The task, available project state, applicable instructions, permissions,
environment, and prior-run references.

## Required outcomes

- a bounded interpretation of the requested outcome;
- identified acceptance criteria or an explicit statement that they are
  missing;
- relevant project and constraint observations;
- material uncertainties and assumptions;
- an initial scope boundary.

## Requirements

- **EAS-003-R01**: Before a material action, the agent MUST inspect the project
  and applicable instructions until it can record the task-model fields required
  by EAS-003-R07.
- **EAS-003-R02**: The agent MUST record material assumptions and unresolved
  uncertainties that can affect the result.
- **EAS-003-R03**: The depth of inspection SHOULD be proportionate to task
  complexity, impact, and uncertainty.
- **EAS-003-R04**: The agent MUST NOT represent absence of observed evidence as
  evidence of absence unless the inspection supports that inference.
- **EAS-003-R05**: If required information cannot be obtained safely and a
  wrong assumption has material cost, the agent MUST escalate or block.
- **EAS-003-R06**: Repository instructions and user constraints MUST be included
  in the project model when applicable.
- **EAS-003-R07**: The task model MUST identify the target, requested outcome,
  acceptance criteria or their absence, impact, reversibility, material
  uncertainties, authority boundary, and evidence obligation.
- **EAS-003-R08**: The task model MUST label uncertainty as goal, input,
  constraint, or context uncertainty when that category changes the recorded
  next action.
