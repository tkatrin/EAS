# Engineering Task Model

## 1. Why task classes are needed

A single linear `understand -> plan -> implement -> verify` workflow describes
change tasks reasonably well but misrepresents diagnosis, review, research,
operations, and advice. EAS therefore defines common obligations and allows
different lifecycle paths based on the requested state transformation.

Task class is descriptive. It does not authorize work and does not replace the
task's actual acceptance criteria.

## 2. Task classes

| Class | Intended transformation | Typical terminal evidence |
|---|---|---|
| `change` | Modify project artifacts or configuration | Diff/artifact inspection and relevant checks |
| `diagnose` | Produce a supported explanation without an implied fix | Reproduction, observations, ruled-out alternatives |
| `review` | Assess an existing artifact or proposed change | Findings linked to locations, risks, and criteria |
| `research` | Reduce uncertainty through structured investigation | Sources, method, synthesis, and unresolved uncertainty |
| `operate` | Change an environment or external system | Authorization, observed effect, and rollback/status evidence |
| `advise` | Produce a recommendation or answer | Stated basis, assumptions, alternatives, and limitations |

A run may have one primary class and multiple secondary classes. For example, a
`diagnose` run may lead to a successor `change` run. Combining classes must not
silently broaden authority.

## 3. Common task dimensions

Each task model includes the following independent dimensions:

- **target**: the project or external state in scope;
- **requested outcome**: the observable result sought by the user;
- **acceptance criteria**: the conditions used to assess success;
- **impact**: `low`, `medium`, `high`, or `critical`;
- **reversibility**: `reversible`, `partially_reversible`, or `irreversible`;
- **uncertainty**: known gaps in goal, input, constraints, or context;
- **authority boundary**: actions allowed without additional approval;
- **evidence obligation**: evidence needed to support the final claims.

Impact and uncertainty are not the same. A well-understood production deletion
can be high impact; a harmless wording preference can be uncertain but low
impact.

## 4. Lifecycle obligations by class

All classes require Understanding, Decision/Autonomy evaluation, Evidence, and
Reporting. Planning, Executing, Verifying, and Reviewing are included when the
task needs their outcomes.

| Class | Execution meaning | Minimum quality gate |
|---|---|---|
| `change` | Apply an authorized project-state modification | Verify acceptance criteria and unintended changes |
| `diagnose` | Perform observations or safe experiments | Test the explanation against available evidence |
| `review` | Inspect and evaluate | Check coverage, specificity, and false-positive risk |
| `research` | Search, select, compare, and synthesize evidence | Check source quality, attribution, and uncertainty |
| `operate` | Perform an external-state action | Confirm authority immediately before action and observe result |
| `advise` | Analyze and formulate a recommendation | Separate facts, inference, preference, and uncertainty |

## 5. Success and no-change

Success does not always require a changed repository. A diagnosis, review,
research result, or justified no-change decision can be a successful state
transformation because the report and project knowledge are part of project
state.

No-change is conforming only when the agent records why a change was not
required, not supported by evidence, not authorized, or not safely possible.
