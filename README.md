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
The current [closeout decision](docs/decisions/AUTHORIZATION-TI2-CLOSEOUT-1-2026-09-17.md)
authorizes **only TI2-CLOSEOUT-1**: documentary reconciliation, deterministic
checks, an approved Git checkpoint, push, a Draft PR and remote CI verification.
Ordinary writes remain inside the repository and default sandbox on
`feat/ti2-registration-calibration`. TI-2R, further pixel access and new
scientific analysis are prohibited, as are TI-3 through TI-8, labels, ledger,
ML datasets, splits, baselines and training.

The author approved the terminal classification:

```text
TI2_EXECUTION = TERMINAL_BLOCKED_PENDING_CLOSEOUT
METHOD_V1 = INSUFFICIENT_EVIDENCE
G2_SPATIAL = BLOCKED_METHOD_V1
TRANSFORM_EXISTENCE = UNDETERMINED
G3 = BLOCKED_DEPENDENCY_G2
E7 = PASS_DOCUMENTARY
TI3_PLUS_AUTHORIZED = false
```

The original execution result is preserved at
`f3c6da78b04299475c7bb85e986eb7435b08bd22`. Exactly 30 pilot frames were decoded
from MP4 without additional losses, preserving the videos' native resolution
and pixel format. Their `.raw` files are headerless decoded pixel buffers,
**not raw detector data**, and remain outside Git. The frozen method did not provide enough
matches at every required estimation instant; no experimental transformation
or common ROI was certified. Reserved quartiles remain unanalysed. The
documented nominal scale is 1.40 µm/pixel in X and Y; the horizontal 500 µm bar
over 357 pixels supplies a compatible raster cross-check of 1.40056022409 µm/pixel.
Complete metrological uncertainty and physical orientation remain unresolved.
No coordinates are converted or scale transferred to unregistered modalities.
Insufficient method-v1 evidence does not demonstrate that registration is impossible.
See the [execution report](artifacts/evidence/TI2/execution-report.md),
[registration decision](artifacts/evidence/G2_SPATIAL/registration-report.json)
and [calibration decision](artifacts/evidence/G3/calibration-report.json).
Closeout publication is authorized despite the blocked scientific result.
Any revised scientific method or TI-3 requires a new author decision.

## Reconciled time and nominal scale

The closeout distinguishes elapsed time from experimental time:

```text
elapsed_from_first_frame_s = 1.18 * frame_index
ESM1–3: experimental_time_s = -25.96 + 1.18 * frame_index
ESM4–6: experimental_time_s = -34.22 + 1.18 * frame_index
time_zero_reference = solidification_front_entry_into_field_of_view
time_model_status = DOCUMENTED_AND_RECONCILED
```

Historical `physical_time_s` fields mean elapsed time from the first frame;
they are deprecated as ambiguous names and must not be interpreted as
experimental time with its offset. The author supplied and approved this
reconciliation and the nominal X/Y scale, citing Gibbs et al., *JOM* 68,
170–177 (2016), [DOI: 10.1007/s11837-015-1646-7](https://doi.org/10.1007/s11837-015-1646-7).
The paper and images were not reopened for this documentary correction.
The raster interval [1.38888888889, 1.41242937853] µm/pixel is a sensitivity
bound, not a statistical confidence interval or a complete metrological
uncertainty certificate. G3 remains blocked by registration, ROI and uncertainty.

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
use the Python standard library. The completed scientific attempt used
already-installed optional tools documented in its evidence; no installation
or further experimental operation is authorized by the closeout.

```bash
make test
make validate-manifest
PYTHONPATH=src python -B scripts/check_ti2_scope.py
```

These full-suite commands are not part of the local agent bootstrap task.

The following source-verification command documents the now-closed TI-1
workflow and must not be run under this TI-2 session. It covers the entire
manifest, including documents outside the historical ZIP-only authorization.
TI2-E0 instead used the bounded `scripts/run_ti2.py preflight` stage against
the exact operator-supplied ZIP; the placeholder below grants no path access:

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

## Governed local closeout

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
and commits require separate targeted approvals. The current closeout decision
explicitly permits publishing this blocked result after reconciliation and
passing tests, guards and checksums, with zero tracked experimental binaries.
It supersedes the earlier publication condition that required full E0–E7
scientific completion. Check the remote reference read-only with targeted
approval, confirm a fast-forward push and approve the exact push separately.
Draft PR creation requires its own approval, followed by completed remote CI
verification. The PR must remain open, in draft and without merge. Green CI
does not approve G2-SPATIAL/G3 or permit another scientific run.

## Governance

The approved scientific protocol controls the technical implementation. Any
change to the task, label semantics, physical-time rule, split policy,
endpoints, or scientific claims requires formal change control. See
[`docs/protocols/TI1_EXECUTION_SPEC.md`](docs/protocols/TI1_EXECUTION_SPEC.md).
The approved historical method-v1 specification is documented in
[`docs/protocols/TI2_EXECUTION_PLAN.md`](docs/protocols/TI2_EXECUTION_PLAN.md).
The bootstrap decision is separated into static conformance and local sandbox
readiness in [`docs/gates/LOCAL_BOOTSTRAP.md`](docs/gates/LOCAL_BOOTSTRAP.md).
