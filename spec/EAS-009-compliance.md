# EAS-009: Compliance

## Assessment levels

EAS 0.1 defines three assessment levels:

- **Schema**: the machine record satisfies its selected versioned JSON Schema.
- **Structural**: the run record satisfies the schema and machine-checkable
  invariants.
- **Behavioral**: the observable run behavior satisfies all applicable EAS 0.1
  normative requirements.

A schema pass is not proof of structural conformance, and structural
conformance is not proof of behavioral conformance.

## Assessment subjects

Assessment level and assessment subject are independent. The level states how
the evidence is checked; the subject states whose obligations are being
aggregated. A run assessment does not assign an adapter, assessor, reporting
tool, implementation claim, or specification defect to the agent run. Those
subjects require separate assessment records.

## Requirements

- **EAS-009-R01**: A conformance report MUST identify `schema`, `structural`,
  or `behavioral` assessment, the assessment subject, and the exact EAS
  version.
- **EAS-009-R02**: Structural assessment MUST validate required fields,
  lifecycle transitions, terminal outcome, unique identifiers, and reference
  integrity.
- **EAS-009-R03**: Behavioral assessment MUST identify the task, applicable
  constraints, observed project context, evidence, and assessor.
- **EAS-009-R04**: An aggregate assessment result MUST be `fail` when any
  applicable mandatory requirement for the declared subject fails.
- **EAS-009-R05**: An aggregate assessment result MUST be `indeterminate` when
  no applicable mandatory requirement fails and at least one is indeterminate.
- **EAS-009-R06**: A conformance result MUST report failed and indeterminate
  requirement identifiers and use `pass` only when neither category contains
  an applicable mandatory requirement.
- **EAS-009-R07**: Tooling MUST NOT label a merely structural pass as an
  unqualified EAS-compliant run.
- **EAS-009-R08**: A behavioral scenario MUST identify its EAS version, input
  task and constraints, applicable requirement identifiers, and observable
  expected properties.
- **EAS-009-R09**: A scenario assessment MUST establish structural conformance
  before evaluating every declared observable expectation.
- **EAS-009-R10**: Passing a finite scenario set MUST NOT be represented as
  universal behavioral conformance beyond the assessed scenarios and version.
- **EAS-009-R11**: An assessment record MUST identify its schema version,
  assessment subject, assessor and version, assessment level, immutable source
  artifact, assessment time, scenario set when used, and requirement and
  validator-rule registry versions.
- **EAS-009-R12**: Every `not_applicable` or `indeterminate` requirement result
  MUST include a non-empty reason.
- **EAS-009-R13**: Every assessment of a run MUST produce a separate assessment
  record without modifying the source run record.
- **EAS-009-R14**: A human-readable report MUST be generated from a versioned
  assessment record while preserving failed, indeterminate, and not-applicable
  requirement results.

## Experimental status

The EAS project has not established a certification authority. Implementations
may report experimental assessment results but must not imply official
certification.
