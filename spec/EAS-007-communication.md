# EAS-007: Communication

## Communication artifacts

The final run record exposes terminal `outcome` and `task_result` as separate
top-level fields. Its embedded report communicates observed work, evidence, and
limitations without duplicating those fields. It is distinct from a
human-readable conformance report, which is rendered from a versioned
assessment record and identifies one assessment subject and assessment level.

Communication records concise observable bases and references. It does not
require private chain-of-thought and does not convert self-reported claims into
independent evidence.

## Requirements

- **EAS-007-R01**: Communication MUST distinguish the current control status or
  terminal `outcome` from `task_result` and distinguish performed work,
  unperformed work, and proposed future work.
- **EAS-007-R02**: A question or approval request MUST identify the decision it
  blocks, the smallest authorization or observation needed, and the material
  consequence of proceeding without an answer, including the recorded
  `impact_level`, affected `authorization_scope`, and reversibility limitation
  when applicable.
- **EAS-007-R03**: The agent SHOULD avoid interrupting the user for information
  that can be obtained safely from the authorized project context.
- **EAS-007-R04**: The agent MUST communicate the observable basis and
  consequence of a newly discovered material risk before taking an action that
  depends on accepting it, including any changed `impact_level`, authority
  result, `authorization_scope`, or reversibility assessment.
- **EAS-007-R05**: A final run record MUST expose `outcome` and `task_result`
  separately and include an embedded report summarizing material changes or
  justified no-change, verification claims with their evidence references,
  known limitations, and unresolved issues.
- **EAS-007-R06**: A final report MUST NOT imply that an action, check, commit,
  publication, external effect, or external communication occurred unless the
  claim is supported by direct or imported observable evidence; self-reported
  evidence alone is insufficient.
- **EAS-007-R07**: Communication SHOULD be proportionate to `impact_level` and
  make decision bases, authority evidence, verification evidence, limitations,
  and the assessment subject and level when reporting an assessment easy to
  locate.
