# EAS-005: Material Decisions and Authority

The six recorded materiality dimensions are project-state change, external
effect, significant resource consumption, authority expansion, security or
privacy posture change, and difficulty of reversal.

## Requirements

- **EAS-005-R02**: A decision referenced by a material action MUST contain the
  complete decision, impact, reversibility, rollback, authorization-scope, and
  authority-evidence fields required by the run schema.
- **EAS-005-R04**: A performed material action MUST record `authorized`
  authority and reference an existing decision.
- **EAS-005-R14**: An action MUST set `material` to the logical OR of its six
  recorded materiality dimensions.

These checks establish internal record consistency. They do not independently
prove that a source trace disclosed every real-world effect or that an
authority statement is authentic.
