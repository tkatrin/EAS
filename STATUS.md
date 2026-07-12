# EAS Project Status

## Current working-draft scope

EAS 0.1 now has an end-to-end experimental slice from normative text to
machine-readable assessment:

- twelve draft documents, EAS-000 through EAS-011, with 149 stable normative
  requirement identifiers;
- six primary task classes, secondary-class rules, an applicability matrix,
  and an assessor burden for every `not_applicable` result;
- formal lifecycle and decision models plus operational definitions of
  materiality, authority evidence, and reversibility;
- distinct terminal `outcome` and task-satisfaction `task_result` fields, so a
  completed run does not imply that its requested result was achieved;
- separate, versioned run, assessment, and human-report artifacts;
- JSON Schemas for run records, scenarios, assessments, external artifact
  bundles, behavior corpora, and neutral trace events;
- machine-readable requirement and validator-rule registries, a generated
  coverage report, and a checked non-regression baseline;
- a dependency-free Python toolchain with explicit `validate`, `assess`, and
  `report` commands;
- a neutral JSONL adapter contract and two reference adapter implementations
  that preserve unmapped events, mapping assumptions, and indeterminate
  properties rather than inventing missing decisions or authority;
- a 26-case core behavior corpus and a 7-case ML/data-science corpus;
- nine executable scenario manifests covering all six primary classes,
  including a combined research-and-advice case;
- external artifact-bundle integrity checks and human-readable terminal and
  Markdown assessment reports;
- CI checks across two Python versions for tests, traceability, coverage
  baseline, reproducibility of the controlled adapter pilot, and the three
  documented CLI paths.

This is enough to test EAS as a coherent draft and reference-tool boundary. It
is not evidence of standards consensus, certification readiness, universal
conformance, or real-world agent quality.

## Assessment boundary

The reference toolchain reports three distinct levels:

1. **Schema** — whether an artifact has the declared machine shape.
2. **Structural** — whether record references and cross-field invariants hold.
3. **Behavioral** — whether one run satisfies the observable expectations of
   one declared scenario.

Assessment records identify the assessment subject separately from the
assessment level and preserve the source-record digest, assessor and registry
versions, per-requirement `pass`, `fail`, `indeterminate`, or
`not_applicable` results, and explicit limitations. External artifact checks
verify local path confinement, size, and digest; they do not prove that an
artifact is authentic or semantically sufficient.

The current [coverage report](reports/requirement-coverage.md) counts declared
reference-tool traceability. It does not convert currently unobservable
requirements into machine-checkable ones and does not establish empirical
validity.

## Editorial and pilot status

Automated editorial checks currently cover duplicate identifiers, missing or
compound BCP 14 obligations, and a bounded list of terms requiring operational
criteria. The separate read-only reviewer record is
[research/editorial-review-0.1.md](research/editorial-review-0.1.md). This is a
draft-quality review, not standards-body review or consensus.

The review found 149 unique requirements and no automated editorial findings.
Its identified cross-model blockers were corrected in this revision; it also
records judgment-dependent and empirical risks that remain open. No external
human editor has yet reviewed the draft.

The [adapter interoperability pilot](research/adapter-interoperability-pilot.md)
uses repository-controlled neutral and scripted fixtures with two reference
adapter classes that share a base class and package. It tests the mapping
contract, explicit uncertainty, and resulting record validity. It does **not**
evaluate two independent agent runtimes, production trajectories,
nondeterminism, or real-world task quality.

Its reproducible machine result is `reports/adapter-pilot.json`; it records zero
real-agent trajectories. Across 50 controlled source events, the two normalized
records agree on all 16 compared semantic fields and both pass the run schema,
structural checks, and SCN-001 projection. The neutral adapter still preserves
one partial and one wholly unmapped event rather than hiding information loss.

The protocol for that later work is documented in
[research/validation-study-protocol.md](research/validation-study-protocol.md).

## Central project hypothesis

An engineering agent is defined by a constrained transformation of project
state, not by code generation alone:

```text
(Task, Initial Project State, Context)
    -> Engineering Agent
    -> (Final Project State, Report, Evidence)
```

EAS specifies the observable discipline of that transformation: what must be
understood, which task classes and conditional requirements apply, which
decisions require authority, what evidence supports quality claims, and when
an agent must escalate or stop.

## What EAS must still demonstrate

1. Independent agent runtimes can emit or be mapped to comparable records
   without adapter-specific semantic invention.
2. The decision, applicability, and materiality rules produce comparable
   proceed/ask/block/refuse outcomes on ambiguous and high-impact cases.
3. Run-record and external-artifact claims correlate with observed behavior
   and resist fabrication, omission, and evaluator gaming.
4. Requirements remain proportional on small tasks while constraining
   externally visible, destructive, sensitive, and data-science work.
5. Definition-only corpus cases can be made executable without embedding a
   vendor runtime or a single prescribed implementation path.

## Immediate development focus

The next content work is to execute the validation-study protocol on real,
consented trajectories from at least two independent agents; add adversarial
and repeated runs; promote high-value definition-only cases to executable
manifests; and revise normative text from observed disagreements. Security and
privacy profiles also remain to be developed.

Governance, certification marks, public registries, and release commitments
beyond the 0.1 working draft remain deliberately deferred.
