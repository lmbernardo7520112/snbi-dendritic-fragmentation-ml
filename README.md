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
The author accepted TI2-CLOSEOUT-1 as **PASS**. The sole canonical active state
is `pyproject.toml [tool.snbi]`: **NONE_AWAITING_AUTHOR_DECISION**, with scientific
execution permissions false. The [PR6 remediation decision](docs/decisions/AUTHORIZATION-TI2-PR6-REMEDIATION-1-2026-09-17.md)
authorizes its bounded code/test/documentary correction, one approved commit,
push, new-SHA CI verification and Draft PR body update only.
Ordinary writes remain inside the repository and default sandbox on
`feat/ti2-registration-calibration`. TI-2R, further pixel access and new
scientific analysis are prohibited, as are TI-3 through TI-8, labels, ledger,
ML datasets, splits, baselines and training.

The author approved the terminal classification:

```text
TI2_EXECUTION = TERMINAL_BLOCKED_CLOSED
TI2_CLOSEOUT_1 = PASS
CURRENT_AUTHORIZED_ACTIVITY = NONE_AWAITING_AUTHOR_DECISION
TI2_EXECUTION_AUTHORIZED = false
TI2R_AUTHORIZED = false
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
The closeout was published as Draft PR #6 with green historical CI.
The remediation preserves that publication and closes all execution permissions.
Ready for review and merge both require a new author decision.
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
pre-existing optional tools documented in its evidence. No local installation
or experimental operation is authorized. A separate CI job installs NumPy
1.26.4 and SciPy 1.11.4 only on its runner, logs their imported versions and
requires exactly five synthetic matching tests to pass with zero skips.
The stdlib checksum step rejects unsafe, experimental or untracked paths.

```bash
/usr/bin/python3 -B scripts/check_repository_data.py
TMPDIR=.bootstrap-test-tmp PYTHONPATH=src /usr/bin/python3 -S -B -m unittest discover -s tests -v
PYTHONPATH=src /usr/bin/python3 -S -B -m snbi_fragmentation.custody validate configs/sources/source_manifest.json
PYTHONPATH=src /usr/bin/python3 -S -B scripts/check_ti2_scope.py
```

The local temporary root must be the real, ignored `.bootstrap-test-tmp/`
directory inside this repository; each test creates its own controlled subtree.
`-S` keeps the five optional matching tests out of the local dependency-free
profile. Their mandatory execution belongs only to the separate pinned CI job.
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

## Governed local maintenance

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
and commits require separate targeted approvals. The remediation decision
permits only its single checkpoint and fast-forward push with individual
approvals, new-SHA CI verification and separately approved update of PR #6
body. No second corrective commit or automatic CI rerun is authorized. Both
CI jobs and the checksum step must succeed; the PR stays open, draft and
unmerged. Guard PASS reports coherent policy while scientific readiness is
BLOCKED. Missing, unknown, conflicting or truthy noncanonical TOML authority
fails closed before source-path access; historical text grants no permission.

## Governance

The approved scientific protocol controls the technical implementation. Any
change to the task, label semantics, physical-time rule, split policy,
endpoints, or scientific claims requires formal change control. See
[`docs/protocols/TI1_EXECUTION_SPEC.md`](docs/protocols/TI1_EXECUTION_SPEC.md).
The approved historical method-v1 specification is documented in
[`docs/protocols/TI2_EXECUTION_PLAN.md`](docs/protocols/TI2_EXECUTION_PLAN.md).
The bootstrap decision is separated into static conformance and local sandbox
readiness in [`docs/gates/LOCAL_BOOTSTRAP.md`](docs/gates/LOCAL_BOOTSTRAP.md).
