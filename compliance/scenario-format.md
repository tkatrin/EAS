# Executable Behavioral Scenario Format

An EAS behavioral scenario is a bounded black-box test definition. It supplies
a task, an initial-state description, constraints, requirement references, and
portable observable expectations. An implementation adapter returns an EAS run
record; the reference assessor evaluates that record and, when declared,
external artifacts.

The manifest deliberately avoids expected private reasoning, exact model
output, vendor-specific tool calls, or a single required implementation path.

## Corpus definitions and executable manifests

The machine-readable corpora in `compliance/corpus/` contain both:

- `executable` cases with a linked manifest in `compliance/scenarios/`; and
- `definition_only` cases that identify a controlled failure mode, applicable
  requirements, and needed artifacts but do not yet have an executable
  projection.

Both corpus files conform to `schemas/eas-corpus.schema.json`. A definition-only
case is design coverage, not an executed assessment result.

## Assessment flow

```text
Scenario input -> Agent/runtime -> Adapter -> EAS run record
                                            |
External artifact bundle ------------------+
                                            v
                               Level 1: schema validation
                                            |
                                            v
                           Level 2: structural semantics
                                            |
                                            v
                       Level 3: scenario expectation checks
                                            |
                                            v
                              Versioned assessment record
                                            |
                                            v
                             Human-readable report rendering
```

Schema and structural failures stop dependent behavioral checks. When a
required artifact bundle is absent, dependent results are `indeterminate`, not
silently passed or treated as not applicable.

## Scenario manifest fields

Each executable manifest declares:

- `eas_version`, `scenario_id`, `title`, and `description`;
- `input.task`, `input.initial_state`, and `input.constraints`;
- `requirement_refs`, the normative requirements projected by the case;
- `required_artifacts`, the portable artifact kinds needed by assessment; and
- `expected`, the observable behavioral projection.

The manifest schema is `schemas/eas-scenario.schema.json`.

## Observable expectation fields

- `outcome`: required terminal outcome;
- `task_result`: required task-satisfaction result, independently of terminal
  outcome;
- `task_class`: required primary task classification;
- `required_secondary_classes`: required outcome-bearing secondary classes;
- `required_states` and `forbidden_states`;
- `required_dispositions` and `forbidden_dispositions`;
- `max_material_actions`;
- `required_evidence_results`;
- `required_evidence_kinds`;
- `required_verification_statuses`;
- `project_state_change`: whether initial and final project revisions must
  differ, must remain equal, or may do either; and
- `required_report_sections_nonempty`.

New assertion types should be added only when they are portable across agent
runtimes and cannot be represented by an existing observable property plus a
normative requirement.

## External artifact bundles

An executable scenario may require artifact kinds such as `project_diff`,
`test_or_inspection_result`, or `authority_source`. The optional bundle follows
`schemas/eas-artifact-bundle.schema.json` and binds artifacts to a run ID with
relative paths, byte lengths, SHA-256 digests, capture modes, sources, and
evidence references.

The reference checker establishes that the declared bytes exist inside the
bundle directory and match their recorded size and digest. It does not
establish authorship, semantic authenticity, truth, or sufficiency. Those
limitations remain explicit in the assessment record.

## Assessment and report records

Behavioral assessment emits a separate record conforming to
`schemas/eas-assessment.schema.json`. It identifies the immutable source record
by digest, the assessment subject and level, the assessor and registry
versions, the scenario set, each assessed requirement result, aggregate
counts, and limitations. It never rewrites the source run record. Subject and
level are independent axes: for example, `adapter_mapping` is a subject while
`structural` is a level.

The `report` command renders that assessment record as terminal text, JSON, or
Markdown. A rendering is not a new assessment and cannot strengthen its scope.

## Result interpretation

- `pass`: the assessed applicable requirement passed within the declared
  inputs and scenario projection;
- `fail`: the assessor observed a violation;
- `indeterminate`: available inputs could not establish a result; and
- `not_applicable`: the conditional subject or trigger was observably absent
  and the assessment records a reason.

A passing scenario means that one run record satisfied one declared set of
observable properties. It does not prove artifact authenticity, universal task
quality, certification, or conformance outside that scenario. Repeated,
adversarial, and real-world runs are required to characterize nondeterministic
implementations.
