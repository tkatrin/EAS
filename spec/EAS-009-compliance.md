# EAS-009: Bounded Assessment

EAS 0.1 keeps schema, structural, and behavioral assessment separate. A
structural pass is not a behavioral result, and a finite scenario pass is not
universal conformance.

## Requirements

- **EAS-009-R08**: A behavioral scenario MUST identify its EAS version, input
  task and constraints, applicable requirement identifiers, and observable
  expected properties.
- **EAS-009-R09**: A run assessed under an executable scenario MUST pass schema
  and structural validation before satisfying every declared observable
  expectation and required artifact-integrity check.
- **EAS-009-R11**: An assessment record MUST identify its schema version,
  assessment subject, assessor and version, assessment level, immutable source
  artifact, assessment time, scenario set when used, and requirement and
  validator-rule registry versions.
- **EAS-009-R12**: Every `not_applicable` or `indeterminate` requirement result
  MUST include a non-empty reason.

The deterministic aggregate and report-rendering rules are reference-tool
protocol checks, not additional EAS requirements.

## Native observation boundary

This non-normative boundary keeps two assessment subjects distinct:

- a complete EAS run may receive schema, structural, and bounded behavioral
  assessment under EAS-009-R09;
- an incomplete native observation may receive only an observed scenario
  projection over project-state revisions and observer-captured evidence.

An observed projection pass is not a pass for EAS-009-R09. It does not supply
or infer outcome, task result, lifecycle, actions, decisions, report, or
verification claims. Missing external facts produce `indeterminate`; a direct
project-state contradiction may produce `fail`. The projection record binds
the exact observation and scenario bytes by SHA-256 and fixes
`conformance_claim` to `false`.
