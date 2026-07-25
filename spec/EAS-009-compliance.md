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

## Assessment subjects

For EAS-009-R11, `assessment_subject` is exactly one of `observation`, `run`,
`adapter`, `assessor`, or `report`. A subject identifies whose properties are
being assessed; it is not a quality grade.

| Subject | Allowed levels | Active requirements | Permitted claim | Required limitation |
|---|---|---|---|---|
| `observation` | schema, behavioral | none in EAS 0.1; only declared observable scenario expectations | externally recorded facts match or contradict a bounded scenario projection | not a full EAS run-conformance assessment |
| `run` | schema, structural, behavioral | explicitly marked run requirements, including EAS-009-R09 | complete record, structural, and bounded scenario results at the levels actually executed | finite scenario results are not universal conformance |
| `adapter` | schema, structural, behavioral | only requirements explicitly marked for adapters | mapping fidelity, preservation, and declared loss | no claim about agent behavior |
| `assessor` | schema, behavioral | EAS-009-R08 and EAS-010-R18 | scenario and applicability process properties | no run aggregate |
| `report` | schema, structural | EAS-009-R11, EAS-009-R12, and EAS-010-R18 | assessment-record integrity and faithful rendering | no broader claim than the source assessment |

The requirement registry is authoritative for subject applicability. A
requirement applicable to `run` is not thereby applicable to `observation`.

An observed projection pass is not a pass for EAS-009-R09. It does not supply
or infer outcome, task result, lifecycle, actions, decisions, report, or
verification claims. Missing external facts produce `indeterminate`; a direct
project-state contradiction may produce `fail`. The projection record binds
the exact observation and scenario bytes by SHA-256 and fixes
`conformance_claim` to `false`.
