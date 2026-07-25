# EAS 0.1 Minimal-Core Review

## Finding

The preceding working draft contained 149 active requirements while only 20
were fully machine-checkable. Ninety-three were unobservable and 36 were
partial. The corpus also counted 24 definition-only cases as design coverage.
This mixed future research ideas with reproducible EAS 0.1 criteria.

## Resolution

- Retained 19 requirements that have deterministic inputs, implemented rules,
  and automated tests.
- Reworded retained requirements to match exactly what the rule establishes.
- Retired 130 identifiers without reusing them.
- Removed the definition-only corpus, unexecutable ML profile, and synthetic
  dual-assessor analysis fixture.
- Added a registry maximum of 20 active requirements and required every active
  requirement to be `full`.
- Made scenario failures produce a direct EAS-009-R09 failure rather than
  ambiguous indeterminate results for unrelated requirements.

## Remaining review risks

The reference tool still evaluates declared records. It cannot prove that a
runtime disclosed all actions, that authority evidence is genuine, or that an
artifact semantically supports a claim. These questions require independent
real trajectories and observers.

This is an internal draft-quality review, not external consensus.
