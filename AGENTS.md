# EAS repository instructions

## Project intent

EAS is a vendor-independent working draft for engineering-agent process and
conformance. Do not turn it into an agent runtime, prompt collection, tool API,
or vendor-specific integration.

## Editing rules

- Write normative specifications in English.
- Use uppercase BCP 14 keywords only for normative requirements.
- Give each normative requirement a stable identifier such as `EAS-004-R03`.
- Keep conceptual claims, normative requirements, and validator behavior
  distinct.
- Do not claim certification, consensus, uniqueness, or standards-body status.
- Preserve the license boundary in `LICENSE.md`: documentation and
  specifications use CC BY 4.0; software and machine-readable artifacts use
  Apache-2.0.
- Prefer the Python standard library for the reference validator.

## Verification

Run:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m eas_validator validate examples/minimal-run.json
PYTHONPATH=src python3 -m eas_validator assess examples/minimal-run.json \
  --scenario compliance/scenarios/SCN-001-focused-edit.json \
  --artifacts examples/artifacts/SCN-001
PYTHONPATH=src python3 -m eas_validator.coverage \
  --check reports/requirement-coverage.md \
  --baseline registry/coverage-baseline.json
PYTHONPATH=src python3 -m eas_validator.pilot \
  --check reports/adapter-pilot.json
```

When a requirement changes, update its specification, schema/validator mapping,
examples, and tests together.

## Repository-owner authorization

The repository owner has explicitly authorized agents to commit finished,
tested logical blocks, push their working branches to `tkatrin/EAS`, and
fast-forward those blocks into `main` without requesting the same permission
again. Before doing so, inspect the final diff, run the relevant checks, and
keep each commit logically focused.

This standing authorization does not permit force-pushing, rewriting published
history, discarding user changes, deleting data, using destructive commands,
or resolving a divergent `main` with a non-fast-forward merge. Stop and ask the
owner if publication would require any of those actions.
