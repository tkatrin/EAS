# EAS Specification Index

Status: **EAS 0.1 Working Draft**.

EAS 0.1 contains **19 active normative requirements**. Every active
requirement is deterministically exercised by the reference toolchain and an
automated test. The 130 identifiers removed during the pre-release scope reset
are retired and are not active criteria.

| ID | Title | Active requirements |
|---|---|---:|
| [EAS-000](EAS-000-overview.md) | Overview and inclusion rule | 0 |
| [EAS-001](EAS-001-terminology.md) | Informative terminology | 0 |
| [EAS-002](EAS-002-agent-model.md) | Run record and task classification | 3 |
| [EAS-004](EAS-004-lifecycle.md) | Lifecycle | 3 |
| [EAS-005](EAS-005-decision-autonomy.md) | Material decisions and authority | 3 |
| [EAS-006](EAS-006-quality.md) | Evidence-backed verification claims | 1 |
| [EAS-007](EAS-007-communication.md) | Final run report | 1 |
| [EAS-008](EAS-008-evidence.md) | Evidence and versions | 3 |
| [EAS-009](EAS-009-compliance.md) | Bounded assessment protocol | 4 |
| [EAS-010](EAS-010-applicability.md) | Applicability record | 1 |

The architecture directory is informative. Machine-readable traceability is
maintained in the [requirement registry](../registry/requirements.json) and
[validator-rule registry](../registry/validator-rules.json). The generated
[coverage report](../reports/requirement-coverage.md) is the authoritative
check that every active criterion is reproducible; it is not empirical
validation or certification.
