# Engineering Agent Standard (EAS)

EAS is a vendor-independent working draft for recording and assessing
observable engineering-agent runs. EAS standardizes neither a model, prompt,
runtime, private reasoning process, nor a predetermined technical answer.

## EAS 0.1 scope

EAS 0.1 is intentionally small:

- **19 active normative requirements**;
- **19 fully machine-checkable requirements**;
- **0 partial requirements**;
- **0 unobservable requirements**;
- **8 executable scenarios** and no definition-only corpus entries; and
- a CI-enforced maximum of 20 active requirements for the 0.1 series.

The 130 requirement identifiers removed in the pre-release scope reset are
retired, not active criteria. See the [specification index](spec/README.md) and
[generated coverage report](reports/requirement-coverage.md).

This repository is pre-consensus and experimental. It is not a certification
program and does not establish universal agent quality.

## Reference toolchain

The dependency-free Python toolchain separates:

1. JSON Schema validation;
2. structural invariants; and
3. a bounded assessment against one executable scenario.

```bash
PYTHONPATH=src python3 -m eas_validator validate examples/minimal-run.json

PYTHONPATH=src python3 -m eas_validator assess examples/minimal-run.json \
  --scenario compliance/scenarios/SCN-001-focused-edit.json \
  --artifacts examples/artifacts/SCN-001

PYTHONPATH=src python3 -m unittest discover -s tests -v

PYTHONPATH=src python3 -m eas_validator.coverage \
  --check reports/requirement-coverage.md \
  --baseline registry/coverage-baseline.json

PYTHONPATH=src python3 -m eas_validator.pilot \
  --check reports/adapter-pilot.json
```

Scenario checks are deterministic over the supplied run record and artifact
bundle. Artifact checks establish presence, size, and digest, not semantic
authenticity. The two included adapters and their pilot use controlled
repository fixtures; they are not two independent agent implementations.

## Repository guide

- [Current status](STATUS.md)
- [Normative specification](spec/README.md)
- [Executable scenarios](compliance/scenarios.md)
- [Compliance matrix](compliance/matrix.md)
- [Real-agent study protocol](research/validation-study-protocol.md)
- [Roadmap](ROADMAP.md)
- [Licensing](LICENSE.md)
