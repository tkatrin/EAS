# EAS 0.1 Compliance Matrix

| Level | Command | Deterministic result | Explicit limitation |
|---|---|---|---|
| Schema | `eas validate` | selected JSON shape | no cross-field or behavioral claim |
| Structural | `eas validate` | 19 active requirement rules over the record | no proof that source claims are authentic |
| Scenario | `eas assess` | one locked scenario projection and artifact integrity | no universal conformance |

## Active requirement coverage

| Metric | Count |
|---|---:|
| Active requirements | 19 |
| Fully machine-checkable | 19 |
| Partially machine-checkable | 0 |
| Unobservable | 0 |
| Requirements with validator rules | 19 |
| Executable scenarios | 8 |
| Definition-only scenarios | 0 |

The registry rejects more than 20 active requirements and rejects an active
requirement whose checkability is not `full`. Every validator rule names its
implementation and automated tests.

## Observable boundary

The tool checks record shape, task-class vocabulary, lifecycle transitions,
outcome consistency, materiality derivation, material-action decision shape,
evidence identity and references, passed-claim support, report shape,
applicability dimensions, assessment-record consistency, scenario
expectations, and artifact bytes.

It does not independently establish source-trace completeness, authority
authenticity, external effects, adequacy of engineering judgment, or
real-world task quality.
