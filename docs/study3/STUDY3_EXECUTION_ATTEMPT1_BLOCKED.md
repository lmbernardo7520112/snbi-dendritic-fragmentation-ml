# Study3 attempt 1: consumed before payload

The original attempt remains permanently preserved as
`BLOCKED_PARTIAL_EXECUTION`, `STATE=CLOSED_CONSUMED`, with
`retry_authorized=false`. The author decision
`/STUDY3-EXECUTION-RECOVERY-1-PREPARE-AND-FREEZE` authorizes preserving this
record and preparing a separate recovery; it does not reopen this attempt.

## Execution custody

- Original method freeze: `a3f45b645e9fb3e813a43220351c951698293963`.
- Branch: `feat/study3-temporal-site-representation`.
- Command: `PYTHONPATH=src $ORIGINAL_ROOT/.venv/bin/python -B scripts/run_study3.py`.
- One CLI invocation, started at `2026-09-24 12:12:22 UTC`; exit 1 observed
  at `2026-09-24 12:12:33 UTC`. The latter is the observation timestamp.
- Receipt created at `2026-09-24T12:12:26.039769+00:00`.
- Receipt SHA-256:
  `9dae20b674064870ca2a0e2d0acc2522bf67ce29011d8ac6db709c9445e80b44`.
- Receipt path: `artifacts/evidence/STUDY3_EXECUTION/scientific-execution-receipt.json`.
- Recorded controller elapsed time: `2.138692161000108` seconds.
- Exception: `FileNotFoundError: [Errno 2] No such file or directory: 'derived'`.

The receipt consumed the original authority even though no experimental
payload was read. The terminal is not scientific PASS. No retry was performed.

## Preserved observations

All 15 original artifacts remain byte-identical. The original checksum list
has 14 entries, all verified, including the receipt and terminal. The missing
`TEMPORAL_SELECTION_LEDGER.json` was never produced; no replacement is created.

The durable I/O audit records zero container opens, row attempts, scientific
binary bytes, authenticated payload rows and materialized rows. Feature
extractions started/completed and LBP rows are zero. The fit ledger has empty
started/completed lists and zero distinct fits. Every RF, CNN1D,
spatiotemporal CNN, metadata LogReg and acquisition-only fit counter is zero.
There are no model scores, acquisition-control results or contrasts.
DEV/TEST/TEST-cache/video accesses, MP4 opens and FFmpeg invocations are zero.
No separate SILVER counter was emitted; all scientific payload access was zero.

The documentary population was authenticated before the receipt: 10,907 TRAIN
rows (3,858 GOLD and 7,049 background), 64 groups (32 positive and 32 background),
four historical folds and two acquisitions. This metadata authentication is
distinct from the payload-reader counters, which remained zero.

## Root cause and bounded operational provisioning

`ROOT_CAUSE=WORKTREE_LOCAL_IGNORED_PAYLOAD_NOT_PROVISIONED`.

`Study3TrainAccess` delegates to `TrainCorpusAccess(root, ...)` without changing
the root. The frozen data contract declares
`payload_root=WORKTREE_ROOT_ONLY_NO_FALLBACK` and
`payload_locations_verified=false`. The original preflight authenticated
documents but did not verify local container locations. The reader walks
`data/derived/...` with directory descriptors before opening a container;
the missing `derived` component therefore raised before any container open or
scientific row read. This is an operational provisioning failure, not a model,
feature, label or dataset-corruption finding.

The separate preparation decision authorized metadata checks and filesystem
copying of exactly these containers from ORIGINAL_ROOT into WORKTREE_ROOT:

| Relative path | Source bytes | Destination bytes |
| --- | ---: | ---: |
| `data/derived/study2b/multimodal_patches_uint8.bin` | 139425000 | 139425000 |
| `data/derived/study2c/cachetrain_dev.bin` | 73827650 | 73827650 |

Before provisioning, local `data/derived` and both destinations were absent.
Sources and destinations were verified by metadata only: regular files,
not symlinks, exact sizes. `cp --reflink=auto --no-clobber` created distinct
destination files; metadata confirms no hardlinks. Both copies are ignored by
Git and absent from its index. No whole-container content hash was calculated.

```text
OPERATIONAL_PAYLOAD_PROVISIONING=true
OPERATIONAL_PAYLOAD_MATERIALIZATION_OCCURRED=true
OPERATIONAL_MATERIALIZED_BYTES=213252650
SCIENTIFIC_APPLICATION_PAYLOAD_READ=false
SCIENTIFIC_APPLICATION_BINARY_READS=0
SCIENTIFIC_ROWS_READ=0
SCIENTIFIC_FEATURE_EXTRACTIONS=0
SCIENTIFIC_FITS=0
```

Operational copying moves experimental payload; it must not be reported as
unqualified zero binary access. It produced no scientific rows, features,
fits or scores and did not change the original evidence.

## Separate recovery boundary

The proposed phase is a **new explicitly authorized recovery execution after a
pre-payload operational failure**. It requires an independent recovery
namespace, a new author decision, a new operational freeze and successful CI.
The original receipt, terminal, local control documents and authority remain
consumed. No recovery receipt or scientific execution is authorized in this
preparation phase. The original model selection, population, folds,
representations, metrics, hyperparameters and 28-fit budget remain fixed.

The canonical HANDOFF remains unchanged, SHA-256
`71bb1bf8f346f445c87561de86329d994354412354b879959f72cb4255bef445`.
