# Engineering Agent Standard (EAS)

EAS is a vendor-independent working draft for specifying how engineering
agents understand work, classify tasks, make authorized decisions, change
project state, verify results, and report observable evidence.

EAS standardizes the **engineering process**, not a model, prompt, API, tool,
runtime, adapter transport, or predetermined technical outcome.

## Status

- Version: EAS 0.1 Working Draft
- Maturity: pre-consensus and experimental
- Language: English
- License: CC BY 4.0 for specifications and documentation; Apache-2.0 for
  software and machine-readable artifacts

Nothing in this repository should be represented as an adopted industry
standard, a certification program, or proof that an implementation is
universally conforming. Normative requirements are drafts for review and
experimentation.

## Start here

- [Project charter](CHARTER.md)
- [Current status](STATUS.md)
- [Specification index, EAS-000 through EAS-011](spec/README.md)
- [Architecture](architecture/README.md)
- [Applicability and task classification](spec/EAS-010-applicability.md)
- [Materiality, authority, and reversibility](architecture/materiality-model.md)
- [Versioned record model](architecture/record-model.md)
- [Behavioral scenario catalog](compliance/scenarios.md)
- [Requirement coverage report](reports/requirement-coverage.md)
- [Editorial and normative review](research/editorial-review-0.1.md)
- [Adapter interoperability pilot](research/adapter-interoperability-pilot.md)
- [Machine-readable adapter-pilot result](reports/adapter-pilot.json)
- [Validation-study protocol](research/validation-study-protocol.md)
- [Roadmap](ROADMAP.md)
- [Licensing](LICENSE.md)

## What the repository contains

```text
.github/        CI for tests, traceability, coverage, and documented commands
architecture/   conceptual, formal, materiality, decision, and record models
compliance/     executable scenario manifests and core/ML behavior corpora
examples/       run records, neutral/scripted traces, and external artifacts
registry/       requirement and validator-rule registries plus coverage baseline
reports/        generated requirement-coverage and adapter-pilot results
research/       prior art, editorial review, and validation-study materials
schemas/        run, scenario, assessment, artifact, corpus, and trace schemas
spec/           normative EAS-000 through EAS-011 working drafts
src/            dependency-free validator, assessor, adapters, and report tools
tests/          schema, structural, behavioral, traceability, and CLI tests
```

The reference toolchain separates three levels:

1. schema validation of the machine record;
2. structural semantic validation of references and invariants;
3. behavioral assessment against a declared scenario and optional external
   artifact bundle.

A run record separates terminal control status (`outcome`) from whether the
requested result was achieved (`task_result`). A normally completed run can
truthfully report `not_satisfied`; a negative experimental finding may still
satisfy a research task.

A behavioral result is bounded by the selected scenario, observable inputs,
registry versions, and artifact limitations. Artifact checks establish file
presence, size, and digest, not semantic authenticity.

## Use the reference toolchain

Python 3.10 or newer is required. The reference implementation has no
third-party runtime dependencies. From a source checkout, set `PYTHONPATH=src`.

Validate a run record at schema and structural levels:

```bash
PYTHONPATH=src python3 -m eas_validator validate examples/minimal-run.json
```

Run a bounded behavioral assessment and save its versioned assessment record:

```bash
PYTHONPATH=src python3 -m eas_validator assess examples/minimal-run.json \
  --scenario compliance/scenarios/SCN-001-focused-edit.json \
  --artifacts examples/artifacts/SCN-001 \
  --format json \
  --output /tmp/eas-assessment.json
```

Render the saved assessment as a human-readable report:

```bash
PYTHONPATH=src python3 -m eas_validator report /tmp/eas-assessment.json \
  --format markdown
```

Run all checks, including registries, coverage, adapters, and CLI behavior:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m eas_validator.coverage \
  --check reports/requirement-coverage.md \
  --baseline registry/coverage-baseline.json
PYTHONPATH=src python3 -m eas_validator.pilot \
  --check reports/adapter-pilot.json
```

The neutral JSONL trace schema and two reference adapters demonstrate a
portable mapping boundary. They do not define an agent runtime and their
fixture-based interoperability pilot is not real-world agent validation.

## Design principle

> EAS specifies the required discipline and evidence of engineering work, not
> the technical answer an agent must choose.
