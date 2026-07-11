# EAS Project Status

## What exists now

EAS 0.1 has a complete first vertical slice:

- a project charter with scope and non-goals;
- a runtime-independent engineering-agent model;
- a lifecycle state machine with re-entry, escalation, blocking, and no-change
  paths;
- ten draft specifications with stable requirement identifiers;
- a model for observable evidence and truthful reporting;
- an experimental JSON run-record schema;
- a structural validator, conforming examples, an invalid fixture, and tests;
- a prior-art map distinguishing EAS from repository instructions, workflow
  languages, runtimes, and outcome-only benchmarks.

This is enough to discuss EAS as a coherent design. It is not yet enough to
claim that the design is complete, empirically validated, or ready for
certification.

## Central project hypothesis

An engineering agent is not defined by code generation. It is defined by a
constrained transformation of project state:

```text
(Task, Initial Project State, Context)
    -> Engineering Agent
    -> (Final Project State, Report, Evidence)
```

EAS specifies the observable discipline of that transformation: what must be
understood, which decisions require authority, what evidence supports quality
claims, and when an agent must escalate or stop.

## What EAS must still prove

1. The same core model can describe change, diagnosis, review, research,
   operation, and advisory work without forcing every task through an
   implementation pipeline.
2. Autonomy decisions can be expressed precisely enough that independent
   implementations make comparable proceed/ask/block/refuse choices.
3. Evidence requirements can be verified without requesting private
   chain-of-thought.
4. Structural run records correlate with actual behavioral quality rather than
   becoming paperwork that a poor agent can fabricate.
5. Requirements remain proportional for small tasks while still constraining
   high-impact work.

## Current development focus

The immediate focus is the content of the standard:

1. validate the task model and lifecycle paths;
2. formalize the decision and autonomy function;
3. define evidence obligations per task and decision type;
4. convert behavioral requirements into executable scenarios;
5. test the model against trajectories from at least two independent agents;
6. revise the normative text from observed failures and ambiguities.

Governance, certification marks, and public launch mechanics are deliberately
secondary until the model survives this validation.
