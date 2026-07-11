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
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -m eas_validator examples/minimal-run.json
PYTHONPATH=src python -m eas_validator examples/minimal-run.json \
  --scenario compliance/scenarios/SCN-001-focused-edit.json
```

When a requirement changes, update its specification, schema/validator mapping,
examples, and tests together.
