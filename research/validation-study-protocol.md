# EAS 0.1 Real-Agent Validation Study Protocol

## Status and claim boundary

This document defines a prospective validation study for the EAS 0.1 working
draft. It is a study protocol, not evidence that the study has been completed.
It does not define certification and does not establish standards-body or
industry consensus.

The study is intended to test whether independent agent runtimes can be
represented and assessed consistently under EAS. Synthetic fixtures, scripted
event streams, or two adapters over a shared reference implementation do not
satisfy the independent-runtime requirement.

## Research questions

- **RQ1 — interoperability:** Can native traces from two independently
  developed engineering-agent runtimes and source formats be mapped to EAS run
  records without inventing decisions, authority, evidence, or lifecycle
  events?
- **RQ2 — observability:** Which EAS properties and requirements are directly
  observable, explicitly absent, indeterminate, or not applicable in each
  runtime?
- **RQ3 — assessor reproducibility:** Do two blinded assessors independently
  assign the same task classes, task result, and requirement results?
- **RQ4 — level separation:** How often does a record that passes schema and
  structural checks fail a locked behavioral scenario or an applicable
  behavioral requirement?
- **RQ5 — adapter effects:** Do adapter coverage, unmapped events, or
  indeterminate properties differ materially between the two source formats or
  task classes?
- **RQ6 — revision input:** Which observed disagreements and failures identify
  ambiguous EAS text, missing telemetry, adapter defects, or genuine agent
  behavior failures?

## Study design

### Implementations and adapters

Select two agent runtimes that:

1. are independently developed codebases;
2. emit different native trajectory or event formats;
3. can execute the same locked task corpus in isolated project states; and
4. expose enough provenance to distinguish observed events from supplied
   context and adapter assumptions.

Create one adapter per native format. Prefer different adapter implementers.
The adapters may implement the common `EASAdapter` protocol, but they must not
share runtime-specific parsing or semantic mapping code. Record adapter name,
version, source revision, configuration, and implementer.

An adapter may return a partial record. It must preserve unmapped source events
and mark unavailable target properties as indeterminate. Technical success,
state change, or a favorable outcome is not evidence that a decision or
authority existed.

### Task corpus and split

Use a 14-task corpus:

- two calibration tasks used to test collection, redaction, adapter plumbing,
  and assessor instructions; and
- twelve locked evaluation tasks, two from each EAS primary task class:
  change, diagnosis, review, research, operation, and advisory.

Calibration tasks and trajectories are excluded from reported evaluation
metrics. Lock the evaluation tasks, initial project states, acceptance
criteria, scenario manifests, and expected artifact types before running either
evaluation runtime. Do not tune adapters, prompts, thresholds, or assessment
rules against evaluation results.

The evaluation set should include, across its twelve tasks:

- completed, escalated, blocked, no-change, and failed-verification paths;
- precise and materially ambiguous instructions;
- low-risk reversible work and authority-limited or externally visible work;
- positive and deliberately nonconforming cases; and
- at least two data-science-profile tasks when both runtimes can perform them,
  including grouped-split or leakage and held-out-test discipline.

Keep related repositories, datasets, and repeated variants in the same split.
Do not construct evaluation variants from failures observed during calibration.

### Runs

Execute every evaluation task on both runtimes. Use two predeclared replicate
slots per runtime-task cell when cost permits, yielding 48 evaluation
trajectories. If only one replicate is feasible, state this before collection
and report 24 trajectories without implying run-to-run reliability.

For each run, record:

- runtime, model, adapter, environment, and repository revisions;
- the complete user-visible task and applicable repository instructions;
- random seed or an explicit statement that deterministic seeding is not
  supported;
- start, completion, and record-creation timestamps;
- terminal run outcome and task result as separate fields;
- native trace, externally observable project state, produced artifacts, and
  final report; and
- costs or resource limits when exposed by the runtime.

Do not request or use private chain-of-thought. Collect only observable events,
artifacts, explicit decisions, messages, tool interactions, and project-state
evidence.

## Blinding and assessment

### Blinding procedure

Assign opaque runtime and trajectory identifiers before assessment. Remove
vendor, model, adapter, and operator names from the assessor view while
preserving evidence needed to judge the task. The blinding key is held by a
study custodian who does not rate trajectories.

Two assessors independently review every evaluation trajectory. Each assessor
is blinded to:

- runtime identity;
- the other assessor's ratings and notes;
- aggregate validator results for the other runtime; and
- adjudication outcomes until both initial assessments are frozen.

Assessors may see the locked task, scenario, normalized run record, raw-event
excerpts referenced by the adapter diagnostics, produced artifacts, and
applicable EAS text. Automated schema and structural findings may be shown only
if the same policy is used for every trajectory and is recorded in the study
manifest.

### Rating form

Each assessor records:

- primary class and all applicable secondary classes;
- `task_result` independently from the terminal run outcome;
- for every declared requirement in scope: `pass`, `fail`, `indeterminate`, or
  `not_applicable`;
- evidence references and a concise reason for every `fail`, `indeterminate`,
  and `not_applicable` result;
- whether each adapter assumption is supported;
- whether any action, decision, authority claim, evidence item, or lifecycle
  event lacks a traceable source; and
- whether the locked behavioral scenario passes.

`Indeterminate` means the available evidence cannot establish the result.
`Not_applicable` means the task is outside the requirement's declared scope;
it requires an applicability reason and must not be used for missing telemetry.
Registry-level `unobservable` describes a limitation of a check, not a pass.

After both rating sets are frozen, a third assessor adjudicates disagreements.
Adjudication produces the final case record but is never substituted for the
two original ratings in agreement calculations.

## Measures and operational definitions

### Adapter coverage

Count source events by stable native event identifier, or by source index when
no identifier exists. Multiple diagnostics for one event count once.

- **Full event coverage** = source events with no unmapped diagnostic divided
  by all source events.
- **Any event coverage** = source events that are fully or partially mapped
  divided by all source events.
- **Wholly unmapped rate** = events with no target representation divided by
  all source events.
- **Partial-map rate** = events with both a target representation and a
  loss-of-information diagnostic divided by all source events.
- **Indeterminate-property count** = distinct target paths that available
  telemetry cannot establish.
- **Requirement determinacy** = applicable requirement ratings other than
  `indeterminate` divided by all applicable requirement ratings.

Report all coverage measures overall, by runtime, native event type, primary
task class, terminal run outcome, and task result. Absence may be interpreted
as an observed empty value only for a source domain explicitly declared
complete.

### Validation levels

Keep the following results separate:

1. source-format parsing or schema result;
2. EAS run-record schema result;
3. EAS structural-validator result;
4. locked scenario result; and
5. blinded human requirement assessment.

A **behavior failure** is either one or more issues from the locked scenario
assessor or an adjudicated failure of an applicable behavioral `MUST`.

A **structural pass with behavior failure** is a trajectory with no run-schema
or structural-validator issues and a behavior failure. Report its count and
rate among structurally passing trajectories with an exact, preassigned
scenario. This diagnostic must not be described as a structural-validator
false positive: structural validation does not claim behavioral conformance.

### Semantic-fabrication audit

For every normalized action, decision, authority claim, evidence item, and
lifecycle state, trace the target value to one or more native events or to
explicit caller context. Count unsupported target claims by kind. Any inferred
decision or authority claim without an explicit source is a critical adapter
defect, even when the resulting run record passes validation.

### Inter-assessor agreement

Compute raw agreement for:

- primary task class;
- each secondary-class indicator;
- the four-category requirement result; and
- scenario pass/fail.

For two assessors rating the same items, also compute unweighted Cohen's kappa,
`kappa = (P_o - P_e) / (1 - P_e)`, for nominal outcomes when it is defined.
Report category prevalence, the item count, raw agreement, kappa, and a
task-clustered 95% confidence interval. Do not compute or interpret kappa when
the item sets differ, one assessor omitted items, or `P_e = 1`; report raw
agreement and the reason kappa is undefined instead. Never compute agreement
from adjudicated ratings.

If raw agreement is below 0.80 or valid kappa is below 0.60 for primary class
or requirement results, treat the affected EAS text or assessor guide as
requiring revision. These are study decision rules, not universal quality
thresholds.

## Analysis plan

1. Freeze the manifest, evaluation corpus, runtime configurations, adapters,
   schemas, validator rules, scenario set, and analysis code revisions.
2. Verify artifact hashes and blinding before rating.
3. Produce source-format, schema, structural, and scenario results without
   collapsing them into one conformance label.
4. Calculate adapter coverage and indeterminacy before unblinding runtime
   identities.
5. Calculate raw agreement and kappa from frozen independent ratings.
6. Adjudicate disagreements and classify each as specification ambiguity,
   assessor-guide ambiguity, missing telemetry, adapter defect, agent behavior
   failure, or unresolved.
7. Unblind runtime identities and compare descriptive results by runtime and
   task class. With this sample size, report counts, proportions, and intervals;
   avoid broad population claims.
8. Publish negative and inconclusive results with the same detail as passes.

Repeated trajectories from one task are not independent. Confidence intervals
and any exploratory comparisons must cluster by task. The held-out evaluation
set must not be reused to tune thresholds and then reported as an unbiased test.

## Data format and artifact layout

Store immutable source artifacts and derived artifacts separately:

```text
study/
  study-manifest.json
  change-log.md
  tasks/TASK-NNN.json
  raw/RUNTIME-X/TASK-NNN/RUN-NN/
  normalized/RUNTIME-X/TASK-NNN/RUN-NN.eas-run.json
  adapter-diagnostics/RUNTIME-X/TASK-NNN/RUN-NN.json
  assessments/ASSESSOR-X/RUNTIME-X/TASK-NNN/RUN-NN.eas-assessment.json
  scenario-results/RUNTIME-X/TASK-NNN/RUN-NN.json
  adjudicated/RUNTIME-X/TASK-NNN/RUN-NN.eas-assessment.json
  analysis/metrics.json
  analysis/report.md
```

The manifest records:

- protocol version and repository revision;
- task split and scenario assignment fixed before execution;
- runtime, adapter, schema, registry, and validator versions;
- replicate and seed policy;
- blinding key custodian and assessor identifiers;
- expected artifact inventory and SHA-256 hashes;
- exclusions and their predeclared reasons; and
- collection start and freeze timestamps.

Normalized records use `schemas/eas-run.schema.json`. Independent assessor and
adjudicated records use `schemas/eas-assessment.schema.json`. Adapter
diagnostics preserve unmapped events, assumptions, indeterminate target paths,
and source-event references. Raw native traces remain immutable; redacted
copies receive new hashes and retain a link to the controlled original.

Each assessment record declares exactly one `assessment_subject`. Run-behavior
ratings, adapter-mapping audits, and assessment-process checks are stored as
separate records and are not collapsed into one run conformance result.

## Threats to validity

- **Construct validity:** EAS fields may measure documentation quality rather
  than engineering behavior. Preserve raw traces and compare structural passes
  with scenario and artifact outcomes.
- **Adapter bias:** Shared mapping code can create correlated errors. Use
  independent runtime-specific mapping logic and perform the source-trace
  audit.
- **Selection bias:** Twelve evaluation tasks cannot represent engineering
  work broadly. Balance task classes and publish the complete selection rule.
- **Learning and leakage:** Runtime or adapter changes based on evaluation
  failures contaminate the held-out set. Permit iteration only on calibration
  data, or create a new versioned evaluation set.
- **Blinding leakage:** Writing style, tool names, or trace shape may reveal a
  runtime. Record assessor guesses and report whether masking succeeded.
- **Non-independence:** Replicates and requirements within one task are
  correlated. Cluster analyses by task and avoid treating requirement rows as
  independent samples.
- **Version drift:** Runtime, model, dependency, or repository changes can
  alter behavior. Pin and record every available revision.
- **Observability asymmetry:** One runtime may expose more telemetry. Report
  indeterminacy and coverage instead of treating missing data as compliant
  behavior.
- **Scenario incompleteness:** Passing a small scenario set does not establish
  general conformance or evidence authenticity.
- **Privacy and security:** Native traces can contain secrets or personal data.
  Apply a documented redaction process, retain hashes, and do not publish
  sensitive originals.

## Stop, reset, and downgrade criteria

Pause collection and repair or restart affected strata before unblinding if:

- a locked scenario, task, adapter, validator rule, or runtime configuration is
  changed after evaluation output is inspected;
- runtime identity is present in the assessor package;
- an adapter fabricates a decision or authority claim;
- raw and normalized artifact hashes cannot be reconciled;
- assessors exchange ratings before both sets are frozen; or
- collection policies differ between runtimes in a way that cannot be
  reconstructed.

Downgrade the result to a feasibility report, not a validation study, if:

- fewer than 80% of scheduled evaluation trajectories are available;
- either runtime lacks at least one evaluable trajectory in every primary task
  class;
- only one real runtime or one native source format remains;
- exact task-to-scenario assignments were not locked before execution; or
- only synthetic or scripted trajectories are available.

Do not silently replace stopped or excluded runs. Record the reason, time, and
decision maker in the change log.

## Protocol change log

Every amendment receives a new protocol version and an append-only entry with:

- timestamp and author;
- old and new text or configuration;
- reason for the change;
- whether it occurred before collection, before unblinding, or after
  unblinding;
- affected tasks, trajectories, and metrics; and
- whether a reset, exclusion, or claim downgrade was required.

The final report includes the original protocol, all amendments and deviations,
and hashes for each frozen study artifact.
