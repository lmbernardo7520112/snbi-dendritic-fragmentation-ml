# Contributing

## Branch and review policy

- `main` must remain green.
- Work is developed in a phase-specific branch.
- A failing RED test is retained as development evidence, not merged into
  `main`.
- Every merge requires passing deterministic tests and an explicit gate record.
- Scientific rules belong in versioned contracts, not only in notebooks.

## Commit policy

Commits must be small, causal, and descriptive. Prefer separate commits for a
test, its minimal implementation, documentation, and generated evidence when
that separation improves reviewability.

## Data and secrets

Never commit raw videos, extracted frames, PDFs under third-party copyright,
credentials, tokens, local absolute paths, or personally identifying data.
Sources are referenced by canonical identifier, size, and SHA-256 digest.

## Scope control

TI-1 through TI-8 are blocked until separately authorized. A pull request that
introduces acquisition, temporal mapping, synchronization, annotation,
dataset, model, or evaluation behavior during TI-0 must be rejected.

