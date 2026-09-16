# ADR 0001 Governed bootstrap and phase boundary

- Status: Accepted
- Date: 2026-09-16
- Decision owner: Leonardo Maximino Bernardo
- Authorized phase: TI-0

## Context

The scientific protocol requires source custody, explicit contracts, evidence,
and deterministic checks before acquisition or machine-learning work begins.

## Decision

Use a small standard-library Python package. Store no experimental binaries in
Git. Identify all sources by canonical ID, size, and SHA-256. Run deterministic
tests in CI. Keep all TI-1 and later modules absent until separately authorized.

## Consequences

The repository can prove source identity and manifest integrity. It cannot yet
make claims about frame counts, timing, synchronization, events, or model
performance.

