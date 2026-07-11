# Prior-art Landscape

This review separates neighboring work from the proposed EAS contribution. It
is a design input, not a novelty or legal opinion. Sources were checked on
2026-07-11.

| Project or standard | Primary concern | Reuse or align | Keep outside EAS |
|---|---|---|---|
| AGENTS.md | Repository-specific instructions | Instruction precedence and interoperability | A competing repository-instruction format |
| GitHub Spec Kit | Spec-driven feature workflow | Artifact separation and spec-before-implementation practice | Its feature-development lifecycle as a universal agent lifecycle |
| AgentSPEX | Workflow specification and execution language | Explicit state, typed steps, branching, checkpointing, visualization | A workflow language or execution harness |
| AgentLens (Lucky Pass) | Process-level trajectory evaluation | Outcome/process separation, waste and missing-verification signals | Its benchmark-specific scoring as normative truth |
| AgentLens (production review) | Whole-trajectory product evaluation | Readable reviews and regression-oriented assessment | LLM-as-judge as the only compliance mechanism |
| OpenHands | Agent runtime and SDK | Reference adapter target; observable tool/action traces | Sandbox, runtime, tools, UI, model routing |
| SWE-Explore | Repository-exploration evaluation | Independent assessment of Understanding | A required retrieval algorithm |
| SWE-Cycle | End-to-end issue-resolution evaluation | Isolated and end-to-end compliance scenarios | Assuming isolated phase success proves full-run quality |
| Ask or Assume? | Clarification under underspecification | Uncertainty-aware escalation scenarios | Requiring a multi-agent implementation |
| ISO/IEC/IEEE 12207:2026 | Software lifecycle processes | Process/activity/outcome framing; methodology independence | Copying protected wording or claiming ISO alignment without a crosswalk |
| NIST AI RMF 1.0 | Voluntary AI risk management | Risk framing and continuous governance concepts | Treating EAS as a general AI-risk framework |
| BCP 14 | Normative requirement keywords | `MUST`, `SHOULD`, `MAY` semantics | IETF status or process claims |

## Proposed original integration

EAS aims to integrate the following into one runtime-independent conformance
model:

1. required engineering lifecycle states with re-entry and no-change paths;
2. explicit authority, risk, reversibility, and escalation decisions;
3. evidence-linked verification and reporting requirements;
4. structural run records plus behavioral conformance scenarios;
5. proportional requirements applicable beyond code generation.

No individual item is claimed to be novel. The project hypothesis is that the
combined normative and testable model fills a useful gap.

## Research constraints

- Recent 2026 papers are preprints unless a venue is explicitly identified.
- Benchmark results are empirical evidence for specific setups, not universal
  requirements.
- ISO full text was not used; only the public abstract and bibliographic page
  informed this mapping.
- EAS text must remain original and must cite rather than reproduce protected
  standards material.
