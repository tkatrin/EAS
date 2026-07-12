# EAS-000: Overview and Conventions

## Status

EAS 0.1 Working Draft; pre-consensus.

## Purpose

This document defines the scope and interpretation rules for the Engineering
Agent Standard.

## Normative language

The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** in
EAS specifications are to be interpreted as described in BCP 14, RFC 2119 and
RFC 8174, when and only when they appear in uppercase.

## Requirements

- **EAS-000-R01**: A conformance claim MUST identify the EAS version,
  assessment level, and assessment subject.
- **EAS-000-R02**: An implementation MUST NOT claim that EAS requires a
  particular model, prompt, API, tool, runtime, programming language, or
  engineering methodology.
- **EAS-000-R03**: Conformance assessment MUST use observable behavior and
  evidence without requiring disclosure of private chain-of-thought.
- **EAS-000-R04**: An implementation MAY use any internal architecture that
  satisfies the observable requirements.
- **EAS-000-R05**: Tailoring MUST preserve every mandatory requirement in any
  unqualified conformance claim.

## Out of scope

Repository-specific instructions, protocol interoperability, model selection,
and runtime security implementation remain outside the core standard, though
their constraints may form part of a run's context.
