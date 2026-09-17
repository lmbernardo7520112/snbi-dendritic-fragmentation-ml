# Sn Bi Dendritic Fragmentation ML

Governed scientific-computing repository for space-time analysis of dendritic
fragmentation in in situ X-ray radiographies of Sn-39.5 wt.% Bi solidification.
The work is a computer-vision continuation of the diffusive and convective
solidification studies developed in Leonardo Maximino Bernardo's doctoral
research and presented at COBEM.

## Current authorization

**TI-0 — Governed Technical Bootstrap** and **TI-1 — Deterministic Audit** are
formally complete. G1 and G2-TEMP were approved by the author. The executive
plan for **TI-2 — Registration and Calibration** is approved, but its execution
and TI-3 through TI-8 remain blocked. A governed local VS Code bootstrap is
authorized independently of TI-2 execution. This repository does not extract frames,
create annotations or datasets, define splits, execute baselines, or train
models.

## Implemented outcomes

- canonical vocabulary and source identifiers;
- immutable source manifest and SHA-256 verification;
- reproducible, dependency-free Python bootstrap;
- deterministic unit and integration tests;
- minimal continuous integration;
- decision and gate records;
- evidence bundle for Gate G0.
- read-only streamed metadata audit for ESM1–ESM6;
- explicit physical-time rule independent of MP4 playback FPS;
- metadata-level correspondence checks for both three-modality groups;
- evidence bundles for the proposed G1 and G2-TEMP decisions.

## Local verification

Python 3.12 is required. The test suite has no third-party runtime dependency.

```bash
make test
make validate-manifest
PYTHONPATH=src python scripts/check_ti1_scope.py
```

To verify locally held source files without copying or extracting them:

```bash
PYTHONPATH=src python -m snbi_fragmentation.custody \
  verify configs/sources/source_manifest.json \
  --data-root /path/to/authorized/source/directory
```

The raw videos and documents are deliberately absent from Git. See
[`data/README.md`](data/README.md) for the custody policy.

An authorized local TI-1 audit can be executed with:

```bash
PYTHONPATH=src python scripts/run_ti1_audit.py \
  --data-root /path/to/authorized/source/directory
```

This command reads the MP4 members directly from the ZIP and writes metadata
and gate evidence only; it does not extract frames.

## Governance

The approved scientific protocol controls the technical implementation. Any
change to the task, label semantics, physical-time rule, split policy,
endpoints, or scientific claims requires formal change control. See
[`docs/protocols/TI1_EXECUTION_SPEC.md`](docs/protocols/TI1_EXECUTION_SPEC.md).
