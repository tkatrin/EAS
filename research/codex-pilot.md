# Codex Single-Runtime Collection Pilot

## Purpose and claim boundary

This pilot prepares real observable runs from one runtime family before the
two-runtime validation study. It tests collection mechanics, workspace reset,
adapter loss, and scenario execution. It cannot establish cross-runtime
portability, independent assessor agreement, or EAS conformance.

The plan contains 16 collection slots:

```text
8 locked scenarios × 1 runtime × 2 repetitions = 16 trajectories
```

No trajectory has been collected yet.

## Reproducible inputs

[`codex-pilot-plan-0.1.json`](codex-pilot-plan-0.1.json) records:

- the locked EAS source revision;
- SHA-256 and byte length for every scenario manifest and fixture file;
- a fixed interleaved run order;
- unique run and blinded sample identifiers;
- the required capture files; and
- the data-minimization and claim boundaries.

The fixture workspaces are local simulations. A publish action writes only a
local log, and a deployment changes only a local JSON state file. They do not
contact a public channel or production environment.

Verify the plan:

```bash
PYTHONPATH=src python3 -m eas_validator.codex_pilot \
  check research/codex-pilot-plan-0.1.json
```

Prepare one fresh slot:

```bash
PYTHONPATH=src python3 -m eas_validator.codex_pilot \
  prepare CDX-SCN-001-R1 \
  --plan research/codex-pilot-plan-0.1.json \
  --output /tmp/eas-codex-pilot/CDX-SCN-001-R1
```

Run Codex in the generated `workspace/` directory and give it only the
instruction to follow `TASK.md`. Store observable exports in `capture/`.
`control/baseline.json` preserves the initial workspace bytes.

## Collection rules

- Use a fresh materialized workspace for every slot.
- Record the exact runtime, model, environment, and adapter versions.
- Capture observable tool calls, tool results, final response, and before/after
  project bytes when the runtime exposes them.
- Do not collect private chain-of-thought, credentials, tokens, or unrelated
  user data.
- If Codex does not expose an event, mark it unmapped. Do not reconstruct or
  invent it.
- Do not commit raw pilot data. The `research/pilot-data/` path is ignored.

Completing these 16 slots will provide a collection pilot for runtime A only.
The full validation protocol still requires a second independently developed
runtime and two blinded assessors.
