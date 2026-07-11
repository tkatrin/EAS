# EAS Project Charter

## 1. Purpose

The Engineering Agent Standard (EAS) defines a portable and testable model for
the process by which an engineering agent transforms project state.

An engineering agent is a system that accepts a task and an initial project
state, performs engineering work under applicable constraints, and produces a
new project state and a truthful report.

## 2. Problem

Outcome-only evaluation cannot distinguish a disciplined solution from a lucky
or unsafe success. Existing projects cover repository instructions, workflow
authoring, agent runtimes, or benchmark outcomes, but these concerns do not by
themselves define a complete normative engineering process.

EAS addresses that gap by specifying required states, decisions, evidence,
quality gates, escalation behavior, and reporting obligations.

## 3. Scope

EAS covers:

- construction of a task and project-state model;
- lifecycle states and permitted transitions;
- planning and scope control proportionate to the task;
- autonomy, risk, reversibility, and escalation decisions;
- implementation or other authorized project-state changes;
- verification, review, and negative-result handling;
- evidence required to support claims;
- truthful communication and final reporting;
- structural and behavioral conformance.

## 4. Non-goals

EAS does not standardize:

- model providers, prompts, or reasoning internals;
- tool-calling protocols or agent APIs;
- repository-instruction file formats;
- a workflow programming language;
- a sandbox, runtime, user interface, or hosting platform;
- a required programming language or development methodology;
- which technical design is correct for a particular task;
- claims that cannot be checked without exposing private chain-of-thought.

## 5. Confirmed direction

The following direction is treated as project input from the founding
discussion:

1. EAS is a standard, not a prompt.
2. EAS applies to engineering agents regardless of model or implementation.
3. EAS standardizes engineering decision process rather than interfaces.
4. The architecture and formal model precede mature normative prose.
5. Specifications are independently identifiable as `EAS-NNN`.
6. The normative language is English.
7. Conformance must eventually be testable.

## 6. Working hypotheses

The following are working-draft choices, not irreversible project decisions:

- the core is decomposed into Understanding, Lifecycle, Decision and Autonomy,
  Quality, Communication, and Evidence concerns;
- a run is represented as an event-and-evidence record;
- EAS 0.1 has one experimental conformance target rather than multiple maturity
  levels;
- a small JSON format is used for the first reference validator.

## 7. Open governance decisions

- standards governance and change-approval process;
- ownership of the EAS name and marks;
- publication venue and versioning after 0.1;
- whether conformance profiles are needed;
- whether certification may ever be claimed and by whom.

Until these decisions are resolved, this repository is a working draft and
must not claim formal certification authority.

The project uses CC BY 4.0 for specifications and documentation and Apache-2.0
for software and machine-readable artifacts. See `LICENSE.md` for the boundary.

## 8. Success criteria for EAS 0.1

EAS 0.1 is ready for external design review when:

- the formal model is internally consistent;
- every normative requirement has a stable identifier;
- each machine-checkable requirement maps to a validator rule;
- examples include successful, escalated, blocked, and invalid runs;
- prior art and original contributions are clearly separated;
- at least two distinct agent implementations can emit comparable run records;
- known limitations and unobservable requirements are explicit.
