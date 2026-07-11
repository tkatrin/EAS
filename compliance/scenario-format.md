# Executable Behavioral Scenario Format

An EAS behavioral scenario is a black-box test definition. It supplies a task,
initial-state description, and constraints to an agent adapter. The adapter
returns an EAS run record. The reference assessor first applies structural
validation and then compares observable run properties with the scenario's
expectations.

## Assessment flow

```text
Scenario input -> Agent adapter -> EAS run record
                                      |
                                      v
                           Structural validator
                                      |
                                      v
                           Scenario expectations
                                      |
                                      v
                        Scenario-specific result
```

The manifest deliberately avoids expected private reasoning, exact tool calls,
or a single required implementation path.

## Observable expectation fields

- `outcome`: required terminal outcome;
- `task_class`: required primary task classification;
- `required_states` and `forbidden_states`;
- `required_dispositions` and `forbidden_dispositions`;
- `max_material_actions`;
- `required_evidence_results`;
- `required_evidence_kinds`;
- `required_verification_statuses`.
- `project_state_change`: whether initial and final project revisions must
  differ, must remain equal, or may do either;
- `required_report_sections_nonempty`.

Expectations are intentionally small in EAS 0.1. New assertion types should be
added only when they are portable across agent runtimes and cannot be expressed
as a normative requirement plus existing observable property.

## Result interpretation

A passing scenario means that one run record satisfied the declared observable
properties. It does not prove evidence authenticity, universal task quality, or
conformance outside that scenario. Repeated and adversarial runs are needed to
characterize nondeterministic implementations.
