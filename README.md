# Sn Bi Dendritic Fragmentation ML

Governed scientific-computing repository for space-time analysis of dendritic
fragmentation in in situ X-ray radiographies of Sn-39.5 wt.% Bi solidification.
The work is a computer-vision continuation of the diffusive and convective
solidification studies developed in Leonardo Maximino Bernardo's doctoral
research and presented at COBEM.

## Current authorization

Only **TI-0 — Governed Technical Bootstrap** is implemented. TI-1 through TI-8
remain blocked. In particular, this repository currently performs no video
metadata audit, physical-time calculation, modality synchronization, frame
extraction, annotation, split generation, baseline execution, or model
training.

## TI-0 outcomes

- canonical vocabulary and source identifiers;
- immutable source manifest and SHA-256 verification;
- reproducible, dependency-free Python bootstrap;
- deterministic unit and integration tests;
- minimal continuous integration;
- decision and gate records;
- evidence bundle for Gate G0.

## Local verification

Python 3.12 is required. The test suite has no third-party runtime dependency.

```bash
make test
make validate-manifest
```

To verify locally held source files without copying or extracting them:

```bash
PYTHONPATH=src python -m snbi_fragmentation.custody \
  verify configs/sources/source_manifest.json \
  --data-root /path/to/authorized/source/directory
```

The raw videos and documents are deliberately absent from Git. See
[`data/README.md`](data/README.md) for the custody policy.

## Governance

The approved scientific protocol controls the technical implementation. Any
change to the task, label semantics, physical-time rule, split policy,
endpoints, or scientific claims requires formal change control. See
[`docs/protocols/TI0_SCOPE.md`](docs/protocols/TI0_SCOPE.md).

