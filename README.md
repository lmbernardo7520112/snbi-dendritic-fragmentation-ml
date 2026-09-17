# Sn Bi Dendritic Fragmentation ML

Governed scientific-computing repository for space-time analysis of dendritic
fragmentation in in situ X-ray radiographies of Sn-39.5 wt.% Bi solidification.
The work is a computer-vision continuation of the diffusive and convective
solidification studies developed in Leonardo Maximino Bernardo's doctoral
research and presented at COBEM.

## Current authorization

**TI-0 — Governed Technical Bootstrap** and **TI-1 — Deterministic Audit** are
formally complete. G1 and G2-TEMP were approved by the author. The real local
Codex sandbox passed its single read-only smoke test, closing LB0 local
acceptance; local Codex writes still require a separate author decision. The
executive plan for **TI-2 — Registration and Calibration** is approved, but its
execution and TI-3 through TI-8 remain blocked. This repository does not
extract frames, create annotations or datasets, define splits, execute
baselines, or train models.

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

## Clean-checkout verification

Python 3.12 is required. CI runs the complete legacy regression suite only in
a clean checkout known not to contain experimental data. The suite has no
third-party runtime dependency.

```bash
make test
make validate-manifest
PYTHONPATH=src python scripts/check_ti1_scope.py
```

These full-suite commands are not part of the local agent bootstrap task.

The following source-verification command documents the now-closed TI-1
workflow. **It is not authorized in the current bootstrap and must not be run
without a new explicit authorization:**

```bash
PYTHONPATH=src python -m snbi_fragmentation.custody \
  verify configs/sources/source_manifest.json \
  --data-root /path/to/authorized/source/directory
```

The raw videos and documents are deliberately absent from Git. See
[`data/README.md`](data/README.md) for the custody policy.

The following audit command is likewise retained only as historical TI-1
documentation and is not currently authorized:

```bash
PYTHONPATH=src python scripts/run_ti1_audit.py \
  --data-root /path/to/authorized/source/directory
```

This command reads the MP4 members directly from the ZIP and writes metadata
and gate evidence only; it does not extract frames.

## Governed local VS Code bootstrap

Local agent work is governed by [`AGENTS.md`](AGENTS.md). Before any local
task, run:

```bash
/usr/bin/python3 -B scripts/check_repository_data.py
/usr/bin/python3 -B scripts/check_local_bootstrap.py
/usr/bin/python3 -B scripts/check_local_environment.py
```

The environment diagnostic is read-only and does not run the optional
`bwrap` capability probe unless `--probe-bwrap` is supplied explicitly. That
probe does not test the complete Codex/seccomp sandbox and cannot authorize
writes. A real sandboxed Codex command subsequently passed under the governed
SDR-2-A remediation, but workspace writes remain blocked until the author
separately authorizes a bounded work scope. A sandbox failure must never be
retried outside the sandbox.

## Governance

The approved scientific protocol controls the technical implementation. Any
change to the task, label semantics, physical-time rule, split policy,
endpoints, or scientific claims requires formal change control. See
[`docs/protocols/TI1_EXECUTION_SPEC.md`](docs/protocols/TI1_EXECUTION_SPEC.md).
The approved but not executable TI-2 plan is documented in
[`docs/protocols/TI2_EXECUTION_PLAN.md`](docs/protocols/TI2_EXECUTION_PLAN.md).
The bootstrap decision is separated into static conformance and local sandbox
readiness in [`docs/gates/LOCAL_BOOTSTRAP.md`](docs/gates/LOCAL_BOOTSTRAP.md).
