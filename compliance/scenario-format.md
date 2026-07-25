# Executable Scenario Format

Each scenario supplies a task, initial state, constraints, requirement
references, required artifact kinds, and deterministic expected properties.
The manifest conforms to `schemas/eas-scenario.schema.json` and includes
EAS-009-R09.

The assessor checks, in order:

1. run and scenario schemas;
2. run structural invariants;
3. declared outcome, task result, task class, lifecycle, disposition, action,
   evidence, project-state, and report expectations; and
4. required artifact presence, path confinement, byte length, and SHA-256.

If schema or structural validation fails, dependent scenario checks do not
run. If required artifacts are absent, EAS-009-R09 is `indeterminate`. If an
expectation or artifact check fails, EAS-009-R09 is `fail`.

Artifact integrity does not establish authenticity or semantic sufficiency.
