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

PYTHONPATH=src python3 -m eas_validator.observation \
  examples/traces/neutral-incomplete.jsonl \
  --observation-id incomplete-example-001 \
  --record-created-at 2026-07-25T20:00:00Z \
  --output /tmp/incomplete-observation.json
```

For a native trace, the same command can preserve every native line inside a
neutral extension event and merge separately recorded observer facts:

```bash
PYTHONPATH=src python3 -m eas_validator.observation native.jsonl \
  --observation-id native-observation-001 \
  --source-format example-runtime-jsonl/1.0 \
  --native-extension-type x-example.runtime-event \
  --observer-events observer-events.jsonl \
  --output /tmp/native-observation.json
```

Observer events may add only externally recorded start metadata, tool results,
file changes, evidence, and project states. They cannot supply agent decisions,
claims, reports, outcomes, or lifecycle completeness.

Scenario checks are deterministic over the supplied run record and artifact
bundle. Artifact checks establish presence, size, and digest, not semantic
authenticity. The two included adapters and their pilot use controlled
repository fixtures; they are not two independent agent implementations.
The observation command intentionally returns a non-zero status together with
`INDETERMINATE`; successful serialization is not a conformance pass.

An incomplete observation can then receive a smaller, external-only scenario
projection:

```bash
PYTHONPATH=src python3 -m eas_validator.native_observation \
  /tmp/native-observation.json \
  --scenario compliance/scenarios/SCN-001-focused-edit.json \
  --projection-id native-scn-001-001 \
  --output /tmp/native-scn-001-projection.json
```

This compares only the scenario's `observable_expectations`: observed
before/after project revisions and observer-captured evidence result/kind.
The result begins by stating that its subject is an external observation and
that it is not a full run-conformance assessment. It fixes
`conformance_claim` to `false`; even a projection pass is not a structural,
behavioral, or universal EAS run-conformance pass.

## Repository guide

- [Current status](STATUS.md)
- [Normative specification](spec/README.md)
- [Executable scenarios](compliance/scenarios.md)
- [Compliance matrix](compliance/matrix.md)
- [Real-agent study protocol](research/validation-study-protocol.md)
- [Observation-boundary conclusion](research/observation-boundary-conclusion.md)
- [Reference instrumentation contract](instrumentation/README.md)
- [Instrumented-run pilot protocol](research/instrumented-run-pilot-protocol.md)
- [Roadmap](ROADMAP.md)
- [Licensing](LICENSE.md)
