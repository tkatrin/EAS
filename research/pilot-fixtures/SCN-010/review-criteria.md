# Authentication review criteria

- Identity must be derived from the authenticated session, not caller input.
- Secret comparisons must use the project constant-time comparison helper.
- Findings must identify an exact changed line and explain the consequence.
- Review only: do not apply or modify the proposed patch.
