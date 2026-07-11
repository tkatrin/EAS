# ADR-0001: Treat EAS engines as logical concerns

## Status

Accepted for the 0.1 working draft.

## Context

The founding discussion described Understanding, Lifecycle, Decision, Quality,
and Communication engines. Requiring five concrete runtime modules would make
EAS an implementation architecture and would conflict with runtime and vendor
independence.

## Decision

EAS defines logical concerns and observable responsibilities. An implementation
may combine, split, rename, or distribute internal components while preserving
the specified behavior and evidence.

Evidence is modeled as a sixth cross-cutting concern because conformance cannot
be assessed reliably without observable support for claims.

## Consequences

- Existing agents can adopt EAS without architectural rewrites.
- Conformance tests target records and behavior, not component names.
- Diagrams must not imply that the concerns are required deployable services.
