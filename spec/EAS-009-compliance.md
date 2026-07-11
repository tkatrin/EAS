# EAS-009: Compliance

## Conformance classes

EAS 0.1 defines two assessment classes:

- **Structural**: the run record satisfies the schema and machine-checkable
  invariants.
- **Behavioral**: the observable run behavior satisfies all applicable EAS 0.1
  normative requirements.

Structural conformance is not proof of behavioral conformance.

## Requirements

- **EAS-009-R01**: A conformance report MUST identify `structural` or
  `behavioral` assessment and the exact EAS version.
- **EAS-009-R02**: Structural assessment MUST validate required fields,
  lifecycle transitions, terminal outcome, unique identifiers, and reference
  integrity.
- **EAS-009-R03**: Behavioral assessment MUST identify the task, applicable
  constraints, observed project context, evidence, and assessor.
- **EAS-009-R04**: A failed applicable `MUST` requirement means the assessed run
  is nonconforming.
- **EAS-009-R05**: An unobservable applicable `MUST` requirement means
  conformance is `indeterminate`, not `pass`.
- **EAS-009-R06**: A conformance result MUST report failed and indeterminate
  requirement identifiers.
- **EAS-009-R07**: Tooling MUST NOT label a merely structural pass as an
  unqualified EAS-compliant run.
- **EAS-009-R08**: A behavioral scenario MUST identify its EAS version, input
  task and constraints, applicable requirement identifiers, and observable
  expected properties.
- **EAS-009-R09**: A scenario assessment MUST first establish structural
  conformance and MUST then evaluate every declared observable expectation.
- **EAS-009-R10**: Passing a finite scenario set MUST NOT be represented as
  universal behavioral conformance beyond the assessed scenarios and version.

## Experimental status

The EAS project has not established a certification authority. Implementations
may report experimental assessment results but must not imply official
certification.
