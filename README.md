# Sn Bi Dendritic Fragmentation ML

Governed scientific-computing repository for space-time analysis of dendritic
fragmentation in in situ X-ray radiographies of Sn-39.5 wt.% Bi solidification.
The work is a computer-vision continuation of the diffusive and convective
solidification studies developed in Leonardo Maximino Bernardo's doctoral
research and presented at COBEM.

## Current authorization

**TI-0 — Governed Technical Bootstrap** and **TI-1 — Deterministic Audit** are
formally complete. G1 and G2-TEMP were approved by the author. LB0 is **PASS**
and SDR-2-A is **RESOLVED** after the successful real Codex sandbox smoke test.
The author separately authorized **TI-2 — Registration and Calibration**, E0–E7,
and repository writes in the default sandbox on
`feat/ti2-registration-calibration` in the
[execution decision](docs/decisions/AUTHORIZATION-LB0-SDR2A-CLOSURE-PR5-MERGE-TI2-EXECUTION-2026-09-17.md).

Only the 30 frozen pilot images may be decoded from the exact source supplied
by the operator, read-only. Local derived binaries remain ignored. TI-3 through
TI-8, labels, ledger, ML datasets, splits, baselines and training remain blocked.
The [targeted Git approval decision](docs/decisions/AUTHORIZATION-TI2-TARGETED-GIT-APPROVALS-2026-09-17.md)
resumes work after the operational index-write block; it does not expand the
scientific scope. G2-SPATIAL and G3 were `NOT_EVALUATED` at that resumption, as
recorded in the [execution-state snapshot](artifacts/evidence/TI2/execution-state.json).

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

Python 3.12 is required. CI runs the complete legacy regression suite in
a clean checkout known not to contain experimental data. The explicit recovery
authorization also permits the full synthetic suite locally with `TMPDIR`
inside the ignored repository subtree `.bootstrap-test-tmp/`; tests must never
read experimental bytes. Core contracts and CI
use the Python standard library. Authorized local experimental operations may
use already-installed scientific/codec tools with versions recorded in evidence;
those optional runtime tools are not installed or required by CI.

```bash
make test
make validate-manifest
PYTHONPATH=src python -B scripts/check_ti2_scope.py
```

These full-suite commands are not part of the local agent bootstrap task.

The following source-verification command documents the now-closed TI-1
workflow. TI2-E0 may revalidate the approved hashes only against the exact
operator-authorized source; the placeholder below grants no path access:

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

## Governed local TI-2 execution

Local agent work is governed by [`AGENTS.md`](AGENTS.md). Before any local
task, run:

```bash
/usr/bin/python3 -B scripts/check_repository_data.py
/usr/bin/python3 -B scripts/check_local_bootstrap.py
/usr/bin/python3 -B scripts/check_ti2_scope.py
```

No further sandbox/AppArmor diagnostic is authorized or needed. A sandbox
startup failure must never be retried outside the sandbox. Read-only Git
metadata protection is a separate operational constraint: exact-path staging
and commits require separate targeted approvals. Push approval is requested
only after final gate decisions and passing required tests; Draft PR creation
requires its own approval. Merging the TI-2 PR remains prohibited.

## Governance

The approved scientific protocol controls the technical implementation. Any
change to the task, label semantics, physical-time rule, split policy,
endpoints, or scientific claims requires formal change control. See
[`docs/protocols/TI1_EXECUTION_SPEC.md`](docs/protocols/TI1_EXECUTION_SPEC.md).
The approved, execution-authorized TI-2 plan is documented in
[`docs/protocols/TI2_EXECUTION_PLAN.md`](docs/protocols/TI2_EXECUTION_PLAN.md).
The bootstrap decision is separated into static conformance and local sandbox
readiness in [`docs/gates/LOCAL_BOOTSTRAP.md`](docs/gates/LOCAL_BOOTSTRAP.md).
