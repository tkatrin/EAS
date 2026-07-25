# EAS-000: Overview and Conventions

## Status

EAS 0.1 Working Draft; pre-consensus.

## Purpose

EAS 0.1 is a small, executable protocol for recording and assessing observable
engineering-agent runs. It deliberately standardizes neither an agent runtime
nor a private reasoning process.

Only clauses carrying an `EAS-nnn-Rnn` identifier are normative requirements.
All other prose, architecture documents, and research notes are informative.

## Normative language

The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** in
identified requirements are interpreted as described in BCP 14, RFC 2119 and
RFC 8174.

## EAS 0.1 inclusion rule

An active EAS 0.1 requirement has:

- deterministic observable inputs;
- at least one implemented validator rule;
- at least one automated test of that rule; and
- a bounded result vocabulary of `pass`, `fail`, `indeterminate`, and
  `not_applicable`.

Ideas that do not meet this bar are research topics, not EAS 0.1 requirements.
The reference tool does not require disclosure of private chain-of-thought and
does not establish certification, standards consensus, or universal agent
quality.
