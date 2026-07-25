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

1. Native runtime traces can be mapped into complete EAS run records without
   semantic invention.
2. Recorded authority, effects, and verification evidence correlate with
   independently observed reality.
3. The 19 requirements distinguish meaningful engineering behavior rather
   than mainly detecting incomplete records.
4. The results generalize across model-provider families.

## Real-agent study result

The independent assessment phase completed on 2026-07-25. Two assessors each
rated 32 blinded trajectories and 480 run-level requirement decisions without
missing rows. Requirement agreement was 476/480 (99.17%, Cohen's kappa
0.987); scenario agreement was 31/32 (96.88%, kappa 0.904).

This high agreement is not evidence that the requirements discriminate agent
quality. All 3,552 native events were preserved, but all 32 captures remained
incomplete observations with 18 missing run fields. No capture could be mapped
to a complete EAS run, so run-schema and structural pass rates were both 0%.
Each assessor rated 160/480 requirements (33.33%) `indeterminate`. Requirement
profiles were identical between repeated runs even when scenario outcomes
changed.

The scenario layer produced 25 unanimous passes and six unanimous failures.
Five unanimous failures expose an artifact-location ambiguity in SCN-002,
SCN-007, and SCN-012: those packets require observable artifacts while also
forbidding project-state changes. SCN-010 produced one unanimous failure and
the only scenario disagreement because exact finding location is
under-specified.

Four requirement disagreements all concern `EAS-006-R03`: one assessor used
`not_applicable` when no passed verification claim existed, while the other
used `pass`. The independent results are recorded in
[`reports/real-agent-validation-0.1.json`](reports/real-agent-validation-0.1.json).
The independent ratings remain unchanged and are not consensus-rescored.

The active post-study revision now makes `EAS-006-R03` `not_applicable` when
no passed verification claim exists. It removes the under-specified
`finding_location` artifact from SCN-010. All scenario manifests now declare
that the observation harness produces required artifacts outside the project,
so those files cannot silently violate a no-change task.

Do not add normative requirements yet. Repair the observation-to-run mapping,
then repeat a newly locked study before deciding which requirements to revise,
merge, or remove.
