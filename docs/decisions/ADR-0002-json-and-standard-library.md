# ADR 0002 JSON contracts and standard library implementation

- Status: Accepted
- Date: 2026-09-16

## Decision

Use JSON for the TI-0 manifest and evidence records and Python 3.12 standard
library code for validation and hashing.

## Rationale

This removes package-resolution variability from Gate G0. JSON Schema remains
the human- and tool-readable normative contract, while deterministic runtime
checks enforce the subset required by TI-0 without downloading dependencies.

