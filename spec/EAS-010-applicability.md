# EAS-010: Applicability and Task Classification

## Status

EAS 0.1 Working Draft; pre-consensus.

## Purpose

This document defines how an assessor determines which EAS requirements apply
to a run. It also defines the boundaries of the six core task classes and the
rules for selecting primary and secondary classes.

Applicability is determined from the requested outcome, acceptance criteria,
observable actions, effects, claims, and assessment target. A class label in a
run record is evidence about applicability, but it is not the sole source of
applicability.

## Terms used by this document

**Requested task outcome** — the result whose delivery would satisfy the
task's acceptance criteria. When acceptance criteria are absent, it is the
bounded result supported by the task text and applicable constraints.

**Outcome-bearing class** — a task class whose class-defining outcome is
necessary for the requested task outcome.

**Supporting activity** — an activity performed only to produce or check
another class's outcome and which does not itself create a separately requested
outcome, material external effect, or material report claim.

**Material report claim** — a claim whose truth could change the reported
outcome, an acceptance decision, an authority decision, or a conformance
result.

**Task-target project-state change** — an observable creation, modification,
or deletion of an artifact, configuration, or data item in the task's target.
The run record and the final report are not task-target changes merely because
they record or transport the result. A report delivered as a project artifact
is a task-target change when changing that artifact is itself part of the
requested outcome.

**External-state change** — an observable effect outside the task-target
project artifacts, including a change to a service, deployment, account,
permission, external data store, or stakeholder-visible external system.

**Applicability trigger** — an observable condition that makes a conditional
requirement applicable. A trigger can be a selected or inferred task class, an
action, a state change, a risk condition, a claim, an assessment type, or
another event named by the requirement.

## Task-class selection

- **EAS-010-R01**: A run MUST identify exactly one primary task class before
  its first class-defining activity or evidence collection, or before
  `REPORTING` when neither occurs.
- **EAS-010-R02**: The primary task class MUST be the class that corresponds to
  the requested task outcome under the boundaries in Table 1.
- **EAS-010-R03**: When exactly one class is outcome-bearing, the agent MUST
  select that class as primary.
- **EAS-010-R04**: When multiple classes are outcome-bearing and the task does
  not designate a primary class, the agent MUST record the candidate classes,
  the selected primary class, and the observable task or acceptance-criterion
  basis for the selection.
- **EAS-010-R05**: A run MUST identify every remaining outcome-bearing class as
  a secondary class and exclude the primary class from that list.
- **EAS-010-R06**: An assessor MUST apply a class's requirements when the task,
  observable behavior, external effect, or material report claim meets that
  class's boundary, even when the run record omits or mislabels the class.
- **EAS-010-R07**: A supporting activity MUST NOT by itself cause the activity's
  class to be selected as a secondary class, except that a material
  external-state change invokes the `operate` obligations and a task-target
  project-state change invokes the state-change obligations in this document.
- **EAS-010-R08**: When an observed scope change or evidence item changes the
  set of outcome-bearing classes, the run MUST record a revised classification
  before the next action whose authority or evidence obligation depends on it.
- **EAS-010-R09**: Task classification MUST NOT create authority, reduce risk,
  or remove an obligation invoked by an actual action, effect, claim, or state
  change.

### Table 1 — Core task-class boundaries

The primary and inferred-class criteria in this table are incorporated by
EAS-010-R02 and EAS-010-R06. The examples in the final column are informative.

| Class | Primary boundary | Secondary or inferred-class trigger | Does not trigger the class by itself |
|---|---|---|---|
| `change` | Completion requires a task-target project-state change as an engineering outcome, rather than only as the representation or delivery of another class's outcome. | Such a change is a separately requested outcome in a multi-outcome run, or the report claims such a change as completed. | Creating the EAS record; a delivery-only report; temporary diagnostic artifacts removed before completion. |
| `diagnose` | Completion requires a supported explanation of an observed condition, symptom, or failure, without requiring a remedy to be implemented. | A causal or explanatory conclusion is a separately requested outcome or is presented as a material supported conclusion in the report. | Observing a symptom or testing a hypothesis solely to complete another class's outcome. |
| `review` | Completion requires findings from evaluating an existing or proposed artifact against stated or identified criteria. | A distinct set of evaluative findings is requested or reported in addition to another outcome. | Reviewing the agent's own work to satisfy a quality gate; inspecting files to understand the task. |
| `research` | Completion requires selecting, comparing, or synthesizing sources or experiments to reduce an open factual uncertainty. | A research synthesis is a separately requested outcome or a material evidentiary result reported alongside another outcome. | Reading project files, applicable instructions, or known documentation only to understand or execute another task. |
| `operate` | Completion requires an external-state change or other material effect in an environment or external system. | A material action intended to create an external-state change is attempted or performed in support of another outcome. | Read-only inspection; an isolated local check with no material external effect. |
| `advise` | Completion requires an answer, recommendation, or choice guidance and does not require the recommended action to be performed. | A recommendation or trade-off decision is separately requested or presented as a material outcome alongside another outcome. | A routine final summary, limitation, or next-step note after completing another class's outcome. |

The storage form of a deliverable does not determine its class. For example, a
research report saved in a file remains primarily `research` when the requested
outcome is the synthesis and the file is only its delivery form; the file write
independently invokes applicable state-change obligations.

## Applicability dimensions

An individual run assessment uses four independent dimensions:

1. **Base** — requirements that apply to every run, irrespective of class.
2. **Class** — requirements invoked by every selected or assessor-inferred
   class.
3. **Action and state change** — requirements invoked by actual or claimed
   material actions, task-target changes, and external effects.
4. **Risk and event** — requirements invoked by impact, reversibility,
   uncertainty, failure, escalation, redaction, or another named condition.

- **EAS-010-R10**: An assessor MUST apply the union of the obligations obtained
  from all four applicability dimensions.
- **EAS-010-R11**: The base requirement families in Table 2 MUST be evaluated
  for every run and remain applicable regardless of its primary or secondary
  task classes.
- **EAS-010-R12**: The class-specific evidence requirement for every selected
  or assessor-inferred class in Table 3 MUST be applied to the run.
- **EAS-010-R13**: Material-action requirements MUST be applied according to
  the candidate or performed action, regardless of the task class.
- **EAS-010-R14**: State-change requirements MUST be applied when a
  task-target project-state change or external-state change occurs, or when a
  report claim or `task_result` states that a required change occurred.
- **EAS-010-R15**: Absence of a state change MUST NOT make a state-change
  requirement `not_applicable` when the run claims completion of an acceptance
  criterion that required that change.
- **EAS-010-R16**: The applicability record for risk-triggered requirements MUST
  be independent of task class and revised when observed impact,
  reversibility, authority, or material uncertainty changes.
- **EAS-010-R17**: A terminal outcome of `escalated` or `blocked` MUST NOT make
  requirements governing behavior before that terminal state
  `not_applicable`.

### Table 2 — Base run requirement families

`Base` means that class selection cannot make the family inapplicable. A
requirement whose text quantifies over records, references, actions, or claims
is evaluated against the observed set; an empty set can satisfy a prohibition
or universal invariant without producing `not_applicable`.

| Obligation family | Existing requirements | Applicability basis |
|---|---|---|
| Run and task model | EAS-002-R01, EAS-002-R02, EAS-002-R04, EAS-002-R06–R10; EAS-003-R02, EAS-003-R03, EAS-003-R06, EAS-003-R07 | Every run. |
| Lifecycle integrity | EAS-004-R01–R03, EAS-004-R06, EAS-004-R08 | Every run. Event-specific lifecycle duties remain subject to Table 4. |
| Constraint-first decision discipline | EAS-005-R08 | Every run. |
| Truthful communication | EAS-006-R03, EAS-006-R08; EAS-007-R01, EAS-007-R03, EAS-007-R05–R07 | Every run; prohibitions are satisfied, rather than made inapplicable, when the prohibited claim is absent. |
| Evidence, record integrity, and privacy | EAS-008-R01–R04, EAS-008-R06–R08, EAS-008-R15–R18, EAS-008-R20, EAS-008-R23 | Every run; collection depth remains proportional and claim-relative. Prohibitions are satisfied when the prohibited representation is absent. |
| Applicability and classification | EAS-010-R01–R26 | Every run assessment, subject to each requirement's stated event condition. |

### Table 3 — Class applicability matrix

Symbols: `B` = base for every class; `K` = invoked when that class is selected
or inferred; `C` = invoked when the stated condition occurs; `—` = the class
alone does not invoke that row. A `—` does not override an action, state,
risk, or event trigger.

| Requirement or obligation | Change | Diagnose | Review | Research | Operate | Advise | Trigger outside class selection |
|---|:---:|:---:|:---:|:---:|:---:|:---:|---|
| Base run families in Table 2 | B | B | B | B | B | B | None; always evaluated. |
| Change evidence, EAS-008-R09 | K | — | — | — | — | — | Assessor-inferred `change` class. |
| Diagnosis evidence, EAS-008-R10 | — | K | — | — | — | — | Assessor-inferred `diagnose` class. |
| Review/research evidence, EAS-008-R11 | — | — | K | K | — | — | Assessor-inferred `review` or `research` class. |
| Operation evidence, EAS-008-R12 | — | — | — | — | K | — | Any material external-state change. |
| Advice evidence, EAS-008-R13 | — | — | — | — | — | K | Assessor-inferred `advise` class. |
| Combined-class evidence, EAS-004-R09 and EAS-008-R14 | C | C | C | C | C | C | More than one selected or inferred class. |
| Material-action authority and decision record, EAS-003-R01 and EAS-005-R01–R04 | C | C | C | C | C | C | A candidate or performed material action. |
| State-change verification and review, EAS-006-R01, EAS-006-R02, EAS-006-R05 | C | C | C | C | C | C | An actual or completed claim of task-target or external-state change. |
| High-impact or irreversible gate, EAS-005-R10 | C | C | C | C | C | C | `impact_level` is `high` or `critical`, or reversibility level is `none`. |
| Limitation and negative-result reporting, EAS-006-R04, EAS-006-R06, EAS-007-R05 | C | C | C | C | C | C | A relevant check is unavailable, or a material negative result or limitation exists. |
| Data-science and machine-learning profile, EAS-011 | C | C | C | C | C | C | A run creates, selects, evaluates, or makes an evaluation claim about an artifact or result named by EAS-011. |

### Table 4 — Event and subject applicability schedule

This table makes the conditional requirements in EAS-000 through EAS-011
assessor-usable. Requirements listed in Table 2 remain base requirements.
Permission-level statements do not receive a pass or fail result merely because
the permitted behavior was not used. EAS-000-R04 is an unconditional design
permission and is not scored as a run obligation.

| Requirement | Applicability trigger | `not_applicable` basis |
|---|---|---|
| EAS-000-R01 | A conformance claim is made. | No conformance claim is in the assessed scope. |
| EAS-000-R02 | An implementation's description of what EAS requires is assessed. | No such implementation claim is in the assessed scope. |
| EAS-000-R03 | A conformance assessment is performed. | No conformance assessment is being assessed. |
| EAS-000-R05 | Tailoring accompanies an unqualified conformance claim. | No tailoring, or no unqualified claim, is in the assessed scope. |
| EAS-001-R01 | An EAS specification or conformance report is assessed. | Neither artifact is in the assessed scope. |
| EAS-001-R02 | A local terminology specialization is used. | No local specialization is used. |
| EAS-002-R03 | New information invalidates the working task or project model. | No invalidating information is observed. |
| EAS-002-R05 | The run relies on the permission to conclude that no project-state change is appropriate. | The run does not rely on that permission. |
| EAS-003-R01 | A candidate or performed material action exists. | No material action is proposed or performed. |
| EAS-003-R04 | The agent makes an inference from absence of observed evidence. | No such inference is made. |
| EAS-003-R05 | Required information is unavailable and a wrong assumption has material cost. | At least one element of that conjunction is observably absent. |
| EAS-003-R08 | Distinguishing uncertainty type affects the next action. | The uncertainty type does not affect the next action. |
| EAS-004-R04 | Discovery invalidates understanding or planning. | No invalidating discovery is observed. |
| EAS-004-R05 | Verification fails. | No verification failure is observed. |
| EAS-004-R07 | A successor run resumes escalated or blocked work. | The run is not such a successor. |
| EAS-004-R09 | More than one task class applies. | Fewer than two classes apply. |
| EAS-005-R01 | A candidate or performed material action exists. | No material action is proposed or performed. |
| EAS-005-R02 | A material decision exists. | No material decision is observed. |
| EAS-005-R03 | An action has a listed escalation condition. | No candidate action has a listed condition. |
| EAS-005-R04 | A candidate action has `escalated` or `prohibited` authority. | No candidate action has either authority outcome. |
| EAS-005-R05 | Multiple authorized alternatives satisfy the acceptance criteria and have materially different trade-offs. | No such alternative set is observed. |
| EAS-005-R06 | The agent relies on a documented assumption to take a reversible, low-impact action. | No such reliance is observed. |
| EAS-005-R07 | The agent escalates. | No escalation occurs. |
| EAS-005-R09 | Information is missing and safe, authorized, proportionate inspection could obtain it. | At least one element of that conjunction is observably absent. |
| EAS-005-R10 | A candidate action is high impact or irreversible. | No candidate action meets either condition. |
| EAS-005-R11 | A capability required for the outcome is unavailable. | No required capability is unavailable. |
| EAS-005-R12 | The request conflicts with an applicable binding constraint. | No conflict is observed. |
| EAS-005-R13 | New information materially changes a decision input. | No such change is observed. |
| EAS-005-R14 | A candidate or performed action is assessed. | No candidate or performed action is in the assessed scope. |
| EAS-005-R15 | A decision governs a material action. | No decision governs a material action. |
| EAS-005-R16 | Reversibility is assessed for a material action. | No material action is in the assessed scope. |
| EAS-005-R17 | A decision governing a material action has an `authorized` authority result. | No authorized material-action decision is in the assessed scope. |
| EAS-005-R18 | An authority determination is made. | No authority determination is in the assessed scope. |
| EAS-005-R19 | An adapter cannot reconstruct a required decision property. | The subject is not an adapter mapping, or every required property is reconstructed. |
| EAS-005-R20 | An applicable result depends on an unmapped decision property. | The subject is not an assessment process, or no applicable result has that dependency. |
| EAS-006-R01 | A report claim or `task_result` states that required work or a state change was completed. | The run does not make such a claim. |
| EAS-006-R02 | Verification is required, performed, or reported. | No verification is required, performed, or reported for the bounded outcome. |
| EAS-006-R04 | A relevant check cannot be run. | No relevant check is unavailable. |
| EAS-006-R05 | Review is required or performed, including review of an actual or claimed state change. | No review or state-change review is required or performed. |
| EAS-006-R06 | A material negative result or degraded metric exists. | No such result or metric is observed. |
| EAS-006-R07 | A data-science or machine-learning evaluation claim is made. | No such evaluation claim is made. |
| EAS-007-R02 | A question or approval request is made. | No question or approval request is made. |
| EAS-007-R04 | A newly discovered material risk exists and a candidate action depends on accepting it. | At least one element of that conjunction is observably absent. |
| EAS-008-R05 | Evidence is redacted. | No evidence is redacted. |
| EAS-008-R09 | `change` is selected or inferred. | `change` is neither selected nor inferred. |
| EAS-008-R10 | `diagnose` is selected or inferred. | `diagnose` is neither selected nor inferred. |
| EAS-008-R11 | `review` or `research` is selected or inferred. | Neither class is selected or inferred. |
| EAS-008-R12 | `operate` is selected or inferred, or a material external-state change occurs. | Neither condition occurs. |
| EAS-008-R13 | `advise` is selected or inferred. | `advise` is neither selected nor inferred. |
| EAS-008-R14 | More than one class is selected or inferred. | Fewer than two classes apply. |
| EAS-008-R15 | A run record is assessed. | The assessment subject is not a run record. |
| EAS-008-R16 | A run record is assessed. | The assessment subject is not a run record. |
| EAS-008-R17 | A run record contains time-bearing evidence or metadata. | The assessment subject is not a run record. |
| EAS-008-R18 | A run record contains timestamps. | The assessment subject is not a run record. |
| EAS-008-R19 | A run resumes a predecessor. | The run does not resume prior work. |
| EAS-008-R20 | A run record contains or could contain implementation extensions. | The assessment subject is not a run record. |
| EAS-008-R21 | An adapter mapping is assessed. | The assessment subject is not an adapter mapping. |
| EAS-008-R22 | An adapter mapping is assessed. | The assessment subject is not an adapter mapping. |
| EAS-008-R23 | A claim depends on self-reported evidence. | No dependent claim uses self-reported evidence. |
| EAS-009-R01 | A conformance report is produced. | No conformance report is in the assessed scope. |
| EAS-009-R02 | A structural assessment is performed. | The assessment is not structural. |
| EAS-009-R03 | A behavioral assessment is performed. | The assessment is not behavioral. |
| EAS-009-R04 | An assessment result is aggregated. | Never; an empty failed set satisfies the invariant. |
| EAS-009-R05 | An assessment result is aggregated. | Never; an empty indeterminate set satisfies the invariant. |
| EAS-009-R06 | A conformance result is produced. | No conformance result is in the assessed scope. |
| EAS-009-R07 | Tooling reports a structural pass. | No tooling output reports a structural pass. |
| EAS-009-R08 | A behavioral scenario is specified. | No behavioral scenario is in the assessed scope. |
| EAS-009-R09 | A scenario assessment is performed. | No scenario assessment is performed. |
| EAS-009-R10 | A finite scenario result is represented. | No finite scenario result is represented. |
| EAS-009-R11 | An assessment record is produced. | No assessment record is in the assessed scope. |
| EAS-009-R12 | An assessment contains `not_applicable` or `indeterminate`. | Neither result occurs. |
| EAS-009-R13 | An assessment is performed. | The assessment process is not the declared subject. |
| EAS-009-R14 | A human-readable conformance report is produced. | No human-readable report is in the assessed scope. |

### Table 5 — Risk and state-change cross-check

This cross-check exposes requirements whose applicability or assessment
criterion depends on risk or state change even when no task-class row invokes
them.

| Dimension | Requirements | Trigger or assessment effect |
|---|---|---|
| Proportional inspection | EAS-003-R03 | Complexity, impact, and uncertainty determine the required inspection depth; class does not remove the obligation. |
| Costly wrong assumption | EAS-003-R05 | Missing required information combines with material cost from a wrong assumption. |
| Assumption-based action | EAS-005-R06 | The permission is relevant only to a reversible, low-impact action under a documented assumption. |
| High-impact or irreversible action | EAS-005-R10 | Either condition invokes the explicit-authorization gate. |
| Changed decision risk | EAS-005-R13 | New information changes risk, reversibility, authority, uncertainty, or evidence availability. |
| Risk-based verification | EAS-006-R01 | Verification scope includes material risks introduced by claimed or completed work. |
| Newly discovered risk | EAS-007-R04 | Communication precedes an action that depends on accepting the risk. |
| No-change conclusion | EAS-002-R05 | The recorded basis supports the decision not to change project state. |
| Preservation of unrelated state | EAS-002-R04 | This remains a base invariant, including when an intended change occurs. |
| Task-target state change | EAS-006-R01, EAS-006-R02, EAS-006-R05 | An actual change or completed change claim invokes verification and review duties independently of class. |
| Change-class state evidence | EAS-008-R09 | The evidence duty is additionally invoked when `change` is selected or inferred. |
| External-state change | EAS-005-R01–R04, EAS-006-R01, EAS-006-R02, EAS-006-R05, EAS-008-R12 | A candidate or actual material external effect invokes authority, verification, review, and operation-evidence duties. |

## Applicability decision procedure

- **EAS-010-R18**: For each assessed requirement, the assessor MUST record the
  subject match and the applicability result for the base, class, action and
  state-change, risk and event, and selected-profile dimensions.
- **EAS-010-R19**: When any independent applicability path invokes a
  requirement, the assessor MUST evaluate that requirement even when another
  path does not invoke it.
- **EAS-010-R20**: The assessor MUST base inferred classes and applicability
  triggers on observable assessment inputs without requiring private
  chain-of-thought.
- **EAS-010-R21**: When available evidence is insufficient to determine
  whether an applicability trigger occurred, the assessor MUST report
  `indeterminate` rather than `not_applicable`.

The decision procedure can be represented as:

```text
classes = {declared primary}
        union {declared secondary classes}
        union {classes inferred from observable task and behavior}

applicable(requirement) =
    subject_is_in_scope(requirement)
    and (
      is_base(requirement)
      or class_trigger(requirement, classes)
      or action_or_state_trigger(requirement, observations)
      or risk_or_event_trigger(requirement, observations)
      or profile_trigger(requirement, observations)
    )
```

The expression defines applicability, not the conformance result. An
applicable requirement can evaluate to `pass`, `fail`, or `indeterminate`.

## `not_applicable` rules and burden of justification

- **EAS-010-R22**: An assessor MUST use `not_applicable` only for a conditional
  requirement whose subject or applicability trigger is observably absent.
- **EAS-010-R23**: A base requirement MUST NOT be marked `not_applicable` because
  of missing evidence, omission of a required action, or failure to satisfy the
  requirement.
- **EAS-010-R24**: The party making a conformance claim MUST provide the
  justification for every `not_applicable` result, including the requirement
  identifier, the absent subject or trigger, the observable basis for that
  conclusion, and any supporting evidence references.
- **EAS-010-R25**: The assessor MUST reject a `not_applicable` justification
  when validation against the task, acceptance criteria, actions, effects,
  report claims, and available evidence shows that any input invokes the
  requirement.
- **EAS-010-R26**: An assessor MUST apply EAS-011 when a run creates, selects,
  evaluates, or makes an evaluation claim about a statistical or
  machine-learning model, dataset, split, metric, threshold, or experimental
  result.

An implementation may propose applicability classifications, but the assessor
remains responsible for the reported assessment result. A missing or
unsupported non-applicability justification is not evidence that a requirement
does not apply.

## Informative examples

### Diagnose, then fix

A task requests identification and repair of a defect. Repair is necessary for
completion, so `change` is primary. If the task also requires a supported root
cause, `diagnose` is secondary. Both EAS-008-R09 and EAS-008-R10 apply. If the
root-cause work is only transient reasoning used to select the edit and no
diagnosis is requested or claimed as an outcome, it is a supporting activity
and does not by itself select `diagnose`.

### Research-backed advice

A task requests a recommendation based on a comparison of current primary
sources. `advise` is primary because the recommendation is the terminal
outcome; `research` is secondary because source selection and synthesis are a
separate required outcome. EAS-008-R11 and EAS-008-R13 both apply.

### Authorized deployment

A task requests a deployment. `operate` is primary. The task label does not
prove authority: the material-action, high-impact or irreversible, and
operation-evidence requirements apply from the actual candidate action and its
risk. If deployment never occurs because capability is unavailable,
EAS-005-R11 and truthful blocked reporting still apply.

### Review with no findings

A review that finds no actionable defect remains a `review` run. The absence
of findings does not make EAS-008-R11 inapplicable; evidence still describes
the inspected scope, criteria, and coverage limitations.

### Completed change with no observed diff

If a run claims completion of a requested code change but no state difference
can be observed, the state-change requirements are not `not_applicable`.
Depending on the evidence, the result is `fail` or `indeterminate`. A justified
no-change conclusion may be a valid outcome, but the report must not claim the
requested change occurred.
