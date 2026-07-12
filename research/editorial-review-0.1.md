# EAS 0.1 editorial and normative review

Date: 2026-07-12
Scope: EAS-000 through EAS-011 and the incorporated task, decision,
materiality, applicability, record, schema, and assessor models.

## Review method

The review used two passes:

1. a deterministic editorial check over every identified normative clause;
2. a separate read-only reviewer pass focused on assessment subjects,
   observability, terminology, negative outcomes, and reproducibility between
   assessors.

The automated check enforces unique requirement identifiers, one uppercase
BCP 14 keyword per numbered clause, and a blocklist of undefined qualifiers.
It currently finds 149 unique requirements and zero automated editorial
findings. That result is necessary but not evidence that every requirement is
empirically assessable.

The separate reviewer was another agent operating read-only on the same
repository. This reduces authoring bias but is not an external standards-body
or independent-human review.

## Blocking findings and dispositions

| Finding | Disposition in this revision |
|---|---|
| Assessment requirements mixed agent, adapter, assessor, tooling, report, and specification defects into one run result. | Added an explicit single `assessment_subject`, separated it from `assessment_level`, and prohibited mixing subjects in one aggregate assessment record. |
| The EAS-010 applicability schedule omitted later EAS-005, EAS-008, EAS-009, and EAS-011 requirements. | Extended the subject/event schedule, added record requirements to the base matrix, corrected non-applicability conditions, and added EAS-010-R26 for normative EAS-011 activation. |
| Impact and reversibility used incompatible vocabularies and did not expose a deterministic high-impact trigger. | Standardized reversibility on `full`, `partial`, and `none`; added `impact_level`; defined the EAS-005-R10 trigger; allowed no rollback mechanism when level is `none`; kept `rollback_verified` as a separate canonical decision field. |
| Free-text authority scope could not be compared with a candidate action. | Replaced it for material decisions with a structured grant containing grantor, grantee, action kind, target, environment, conditions, and validity time. Observable authority evidence remains separately referenced. |
| `completed` could be misread as successful task completion. | Kept `outcome` as terminal control status and added `task_result` with `satisfied`, `partially_satisfied`, `not_satisfied`, and `indeterminate`. A completed run may truthfully have any task result. |
| Diagnosis and operation evidence clauses assumed a positive explanation or observed effect. | Reworded them to preserve evaluated candidates, absent or indeterminate effects, and remaining uncertainty. |
| ML rules omitted fitted preprocessing leakage and auditable final-test ordering. | Expanded EAS-011-R02 and added EAS-011-R15 through R17 for fit isolation, immutable pre-test selection, and bounded post-test changes. |
| The decision matrix returned `block or escalate` and used an undefined final gate. | Split stakeholder-resolvable and technically unavailable observations into deterministic rows and made the architecture matrix explicitly informative. |
| Aggregate conformance priority was implicit. | EAS-009-R04 through R06 now define `fail` before `indeterminate`, with `pass` only when no applicable mandatory result is failed or indeterminate. |

## Additional corrections

- Primary class selection now precedes the first class-defining activity or
  evidence collection, not only a material action.
- Multi-class non-applicability uses “fewer than two classes,” covering the
  unclassified case without treating missing classification as success.
- EAS-008-R11 now gives distinct evidence branches for review and research.
- EAS-011-R12 retains the declared search path unless a predeclared pruning
  policy removes an attempt.
- EAS-011-R14 limits component attribution rather than demanding ablation for
  every multi-component result.
- Architecture text no longer claims independent normative force for the
  decision matrix.

## Remaining editorial and empirical risks

The following are explicit open issues rather than silently accepted claims:

- Applicability inference, proportional inspection, material-risk thresholds,
  and grantor authority still require domain evidence and assessor judgment.
  The registry marks requirements that cannot yet be reproduced by the
  reference tooling as unobservable.
- Several behavioral duties depend on the ordering of observable events. The
  neutral trace can represent that ordering, but real runtime adapters and
  inter-rater testing are still required.
- A structured authority grant makes comparison possible; it does not prove
  that the named grantor had legal or organizational authority. Missing proof
  must yield `indeterminate`.
- Terms such as “proportionate” remain intentionally risk-relative. A profile
  or scenario must provide the bound; an agent-selected threshold alone is not
  sufficient assessor evidence.
- The automated compound-clause detector counts BCP 14 keywords. It cannot
  detect every clause that contains several semantic duties under one keyword.
- No external human editor or real-agent trajectory study has yet reviewed
  this draft.

## Review outcome

The identified cross-model blockers were corrected in the working draft. The
text is ready for controlled implementation experiments, but not for a claim
of consensus, certification, or real-world validation. The next editorial
revision must use evidence from the validation-study protocol and record every
requirement changed because two independent assessors interpreted it
differently.
