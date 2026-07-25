# EAS Project Status

## Current result

EAS 0.1 is now a minimal reproducible core:

- 19 active `MUST` requirements;
- every requirement is marked `full`, has an implemented validator rule, and
  has at least one referenced automated test;
- registry policy rejects more than 20 active requirements or any active
  `partial`/`none` requirement;
- 130 earlier working-draft identifiers are retired;
- 8 executable scenarios cover all six recorded primary task classes;
- schema, structural, scenario, assessment-record, artifact, adapter, report,
  and traceability checks run without third-party runtime dependencies.

The earlier 24 definition-only cases, unexecutable ML profile, and synthetic
dual-assessor study fixture were removed. They created apparent coverage
without validating agent behavior.

## What a pass means

- **Schema pass**: the artifact matches its selected JSON Schema.
- **Structural pass**: deterministic cross-field invariants hold.
- **Scenario pass**: the supplied run record and artifact bundle satisfy one
  declared bounded projection.

None of these proves that self-reported events are authentic. Artifact checks
verify bytes and digests, not authorship or semantic truth. The fixture-based
adapter pilot contains zero real-agent trajectories.

## What remains unproven

1. Two independently developed agent runtimes can be mapped without semantic
   invention.
2. Two blinded assessors produce comparable results on the same real
   trajectories.
3. Recorded authority, effects, and verification evidence correlate with
   independently observed reality.
4. The 19 requirements are sufficient to distinguish meaningful engineering
   behavior without overfitting the included fixtures.

## Immediate focus

Do not add new normative requirements yet. First repeat the two-run observation
preflight and verify that incomplete runtime data is preserved as
`indeterminate` without fabricated run fields. After a successful preflight,
execute the first 16-run series; the complete study still requires the eight
locked scenarios, at least two independent runtimes, and two assessors. Revise
or remove requirements based on observed disagreement, false passes, and
missing observables. Add a requirement only when it has a portable
deterministic rule and a failing test.
