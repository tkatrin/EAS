# Engineering Agent Standard (EAS)

EAS is a vendor-independent working draft for specifying how engineering
agents understand work, make decisions, change project state, verify results,
and report evidence.

EAS standardizes the **engineering process**, not a model, prompt, API, tool,
runtime, or predetermined technical outcome.

## Status

- Version: EAS 0.1 Working Draft
- Maturity: pre-consensus
- Language: English
- License: CC BY 4.0 for specifications and documentation; Apache-2.0 for
  software and machine-readable artifacts

Nothing in this repository should yet be represented as an adopted industry
standard. Normative requirements are draft requirements for review and
experimentation.

## Start here

- [Project charter](CHARTER.md)
- [Architecture](architecture/README.md)
- [Formal model](architecture/formal-model.md)
- [Specification index](spec/README.md)
- [Research landscape](research/landscape.md)
- [Roadmap](ROADMAP.md)
- [Licensing](LICENSE.md)

## Repository layout

```text
architecture/   conceptual and formal models
examples/       example EAS run records
research/       prior-art analysis and source register
schemas/        machine-readable run-record schema
spec/           normative EAS specifications
src/            dependency-free reference validator
tests/          validator and conformance-fixture tests
```

## Validate an example

Python 3.11 or newer is recommended. The validator has no third-party runtime
dependencies.

```bash
python -m eas_validator examples/minimal-run.json
python -m eas_validator examples/minimal-run.json \
  --scenario compliance/scenarios/SCN-001-focused-edit.json
python -m unittest discover -s tests -v
```

When running directly from a source checkout, either install the package in a
virtual environment or set `PYTHONPATH=src`.

## Design principle

> EAS specifies the required discipline and evidence of engineering work, not
> the technical answer an agent must choose.
