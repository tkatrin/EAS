# Executable Scenario Format

Each scenario supplies a task, initial state, constraints, requirement
references, required artifact kinds, artifact handling, and two disjoint sets
of deterministic expected properties. The manifest conforms to
`schemas/eas-scenario.schema.json` and includes EAS-009-R09.

`observable_expectations` contains only properties a collection harness can
establish without reconstructing agent semantics: project-state change and
observer-captured evidence result and kind.

`run_semantic_expectations` contains outcome, task result, task class,
lifecycle, dispositions, material-action bounds, verification claims, and
report content. These properties are assessed only for a complete run.

Required scenario artifacts are observation inputs, not additional work
assigned to the agent. The observation harness produces the artifact bundle
outside the project under assessment. Bundle creation is excluded from the
scenario's project-state comparison. An agent-created file inside the project
remains a project-state change even when its content could satisfy a required
artifact kind.

The assessor checks, in order:

1. run and scenario schemas;
2. run structural invariants;
3. declared observable and run-semantic expectations; and
4. required external artifact presence, path confinement, byte length, and
   SHA-256.

If schema or structural validation fails, dependent scenario checks do not
run. If required artifacts are absent, EAS-009-R09 is `indeterminate`. If an
expectation or artifact check fails, EAS-009-R09 is `fail`.

Artifact integrity does not establish authenticity or semantic sufficiency.

## Incomplete native observations

A native observation that cannot form a structurally valid run does not enter
the assessment sequence above. The reference tool may instead compare
`observable_expectations` only:

- `project_state_change`;
- `required_evidence_results`; and
- `required_evidence_kinds`.

The result is an observed scenario projection, not EAS-009-R09 conformance.
Missing observer facts are `indeterminate`, not failures or inferred values.
Native extension payloads remain preserved source material and cannot satisfy
an observer-fact check.
