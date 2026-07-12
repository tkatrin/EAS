# EAS 0.1 Compliance Matrix

This matrix describes the observable boundary of the experimental reference
toolchain. It separates declared specification requirements, schema checks,
structural semantic checks, scenario projections, and evidence that still
requires an independent observer or human judgment.

## Assessment levels

| Level | Reference command | What it establishes | What it does not establish |
|---|---|---|---|
| 1 — Schema | `eas validate` | The run record conforms to the versioned JSON shape | Reference integrity, behavioral quality, or evidence truth |
| 2 — Structural | `eas validate` | Cross-field invariants, transition rules, identifiers, and declared evidence links hold | Whether authority was real, checks were adequate, or claims match external reality |
| 3 — Behavioral | `eas assess` | One run satisfies one executable scenario's observable projection and declared artifact conditions | Universal EAS conformance, certification, or performance outside the scenario |

`eas report` validates and renders an existing versioned assessment record. It
does not perform or strengthen an assessment.

Assessment level is distinct from assessment subject. The subject vocabulary
is `run`, `adapter_mapping`, `assessment_process`, `conformance_report`,
`implementation_claim`, and `specification`; a result must not move a failure
from one subject to another.

## Concern coverage

| Area | Schema and structural checks | Scenario, external, or human checks |
|---|---|---|
| Version and identity | EAS/schema versions, run ID, implementation, environment, timestamps, and source digest | Identity provenance and whether the observed runtime matches the declaration |
| Task and applicability | Primary/secondary/candidate fields, classification basis, task-result vocabulary, and scenario-required values | Correct inferred classes and task satisfaction from the task, actions, effects, claims, and acceptance criteria |
| Lifecycle | State vocabulary, permitted transitions, terminal outcome correspondence, and the satisfied/completed invariant | Whether re-entry, stopping, or escalation was appropriate in context |
| Materiality and authority | Six materiality dimensions, material predicate consistency, decision references, structured reversibility, authority fields, and evidence-reference resolution | Whether authority source and scope were genuine and sufficient; actual external consequences |
| Quality | Verification status/evidence consistency and rejection of unsupported passed claims | Adequacy, relevance, independence, and coverage of tests or review |
| Communication | Report and verification structure plus scenario-required non-empty sections | Clarity, omission risk, and whether the report truthfully captures external reality |
| Evidence | Unique IDs, provenance/capture metadata, timestamps, reference integrity, and non-self-reported support for passed claims | Artifact authenticity, privacy compliance, reproducibility, and semantic support |
| External artifacts | Bundle schema, path confinement, run binding, kind coverage, byte length, and SHA-256 digest | Authorship, chain of custody, truth, or semantic sufficiency |
| Data science/ML | Profile requirements are registered and represented by definition-only scenarios | Leakage, split protocol, test-set isolation, reproducibility, slice quality, and real-world validity require experiment evidence and assessment |

## Machine-readable traceability

The source of truth is:

- `registry/requirements.json` for all 149 EAS-000 through EAS-011
  requirements, their applicability notes, observable inputs, result
  vocabulary, validator rules, and scenario references;
- `registry/validator-rules.json` for 39 schema, structural, and behavioral
  rules with implementation and test references; and
- `reports/requirement-coverage.md` for the generated coverage snapshot.

The current snapshot reports:

| Metric | Count |
|---|---:|
| Total requirements | 149 |
| Mandatory (`MUST`) | 136 |
| Advisory (`SHOULD`) | 10 |
| Permissions (`MAY`) | 3 |
| Fully machine-checkable | 20 |
| Partially machine-checkable | 36 |
| Currently unobservable by the reference tool | 93 |
| Requirements with validator rules | 56 |
| Structurally machine-checkable requirements | 39 |
| Behaviorally assessable requirements | 20 |
| Requirements referenced by at least one scenario | 61 |

These counts measure declared and tested traceability. They are not a quality
score, empirical validation result, or claim that unobservable requirements
have passed. CI validates every registry reference, checks that the generated
report is current, and rejects coverage regression below the committed
baseline.

## Scenario projection

The reference assessor can compare a structurally valid run with portable
expectations for:

- terminal outcome, task-result satisfaction, and project-state change;
- primary and required secondary task classes;
- required and forbidden lifecycle states;
- required and forbidden decision dispositions;
- maximum material-action count;
- evidence kinds and results;
- verification statuses; and
- non-empty report sections.

Nine executable manifests cover all six primary task classes. The two corpora
also contain 24 definition-only cases, including all seven EAS-011 cases. A
definition-only case contributes design and requirement traceability, not an
executed result.

## Result vocabulary

- `pass`: the assessed applicable requirement passed within the declared
  observable scope;
- `fail`: at least one observed condition violates the requirement;
- `indeterminate`: available evidence cannot establish pass or fail; and
- `not_applicable`: a conditional subject or trigger is observably absent and
  the assessment records a non-empty reason.

A failed applicable `MUST` makes the aggregate assessment fail. If no `MUST`
fails but an applicable `MUST` is indeterminate, the aggregate is
indeterminate. `SHOULD` and `MAY` outcomes remain visible without independently
creating a mandatory nonconformance result.

## Adapter boundary

The neutral JSONL and scripted-event adapters are tested against repository
fixtures. They preserve unmapped source events, explicit mapping assumptions,
and indeterminate target properties. Successful transport or tool completion
is not automatically promoted to passed engineering evidence, and an observed
action is not used to fabricate a decision or authority record.

The reproducible fixture-based interoperability pilot maps two controlled
encodings of SCN-001 to the same 16-field semantic projection and records
schema, structural, and scenario agreement. It contains zero real-agent
trajectories. Repeated trials, independent implementations, and adversarial
evidence tests remain part of the planned validation study.
