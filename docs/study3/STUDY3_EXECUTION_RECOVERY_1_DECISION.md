# Study3 Execution Recovery 1: decision and operational boundary

The author decision `/STUDY3-EXECUTION-RECOVERY-1-PREPARE-AND-FREEZE`
authorizes preparation, synthetic verification, a separate operational freeze
and its publication checks. It does **not** authorize a recovery scientific
invocation, a recovery receipt or creation of the future recovery science
authorization and CI-proof documents. This record describes a **new explicitly
authorized recovery execution after a pre-payload operational failure**;
execution itself remains conditional on a subsequent author decision.

```text
RECOVERY_ID=STUDY3_EXECUTION_RECOVERY_1
RECOVERY_KIND=PRE_PAYLOAD_OPERATIONAL_EXECUTION_RECOVERY
RECOVERY_SCIENTIFIC_INDEPENDENCE=PRESERVED_WITH_EXPLICIT_OPERATIONAL_HISTORY
SCIENTIFIC_RECOVERY_RUNS=0
RECOVERY_RECEIPT_CREATED=false
```

The independence conclusion concerns the absence of scientific feedback from
the aborted execution. It does not assert statistical independence, previously
unseen TRAIN metadata or restored holdout virginity. The historical
`TEXTUAL_TRAIN_METADATA_EXPOSURE_ONLY` incident remains disclosed in the
[preparation incident record](STUDY3_PRE_SCIENCE_INCIDENT.md), and Study2-C
TEST remains consumed and closed. No historical exposure is erased.

## Preserved original attempt

The [original blocked-attempt record](STUDY3_EXECUTION_ATTEMPT1_BLOCKED.md)
documents the original execution and its operational provisioning history.
Its 15 evidence artifacts under `artifacts/evidence/STUDY3_EXECUTION/` remain
preserved. The evidence checkpoint is
`8026b821ab113f61d759a2b265ddb567e796c408`, whose parent is the original
method freeze `a3f45b645e9fb3e813a43220351c951698293963`.

The original receipt SHA-256 is
`9dae20b674064870ca2a0e2d0acc2522bf67ce29011d8ac6db709c9445e80b44`.
Its original state is permanently:

```text
STUDY3=BLOCKED_PARTIAL_EXECUTION
STATE=CLOSED_CONSUMED
SCIENTIFIC_STUDY3_RUNS=1
retry_authorized=false
```

The consumed receipt is binding even though that invocation produced zero
scientific container opens, scientific binary reads, row attempts,
authenticated payload rows, materialized rows, feature extractions, LBP rows,
fits and scores. DEV, TEST, TEST-cache and video accesses were zero. The
absence of a separate emitted SILVER counter does not create a new counter
claim: all scientific payload access was zero. No temporal selection ledger
was produced and no replacement is fabricated.

Neither the original receipt nor the terminal may be removed, renamed,
rewritten or bypassed. The original `scripts/run_study3.py`, `run` and
`preflight` must continue denying the consumed attempt. A new worktree cannot
reopen it. The original local scientific authorization and its CI proof cannot
authorize Recovery 1.

## Established cause and operational copying

```text
FAILURE_CLASS=PRE_PAYLOAD_OPERATIONAL_FAILURE
ROOT_CAUSE=WORKTREE_LOCAL_IGNORED_PAYLOAD_NOT_PROVISIONED
```

The frozen reader delegates to `TrainCorpusAccess` at the same worktree root.
The frozen data contract specifies `WORKTREE_ROOT_ONLY_NO_FALLBACK` and
`payload_locations_verified=false`. The original preflight authenticated
documentary contracts without checking local payload presence. The reader's
directory walk encountered missing `data/derived` and raised
`FileNotFoundError` before opening a container. This identifies a provisioning
failure; it provides no evidence about feature quality, model behavior or
dataset corruption.

The author separately allowed operational materialization of exactly two
containers into the worktree:

| Worktree-relative destination | Bytes |
| --- | ---: |
| `data/derived/study2b/multimodal_patches_uint8.bin` | 139425000 |
| `data/derived/study2c/cachetrain_dev.bin` | 73827650 |

The completed operation used `cp --reflink=auto --no-clobber`. That option
permits either reflinking or copying; this record does not claim which
filesystem mechanism occurred. Metadata checks established regular files,
exact sizes, no symlinks and no hardlinks to the originals. Both destinations
are ignored by Git and absent from its index. No whole-container content hash
or scientific row inspection was performed.

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

Copying operationally moves experimental bytes. Accordingly, an unqualified
`EXPERIMENTAL_BINARY_READS=0` assertion would be inappropriate after this
operation. The zero counters above apply to scientific application access.
Exact sizes and file types establish provisioning readiness, not content
authentication. The existing row-offset and row-hash checks remain mandatory
inside any subsequently authorized scientific read.

## Council: six required perspectives

The question is: can a second execution be authorized without model shopping
or scientific adaptation? The following are review perspectives, not claims
of independent human approvals. Each conclusion is conditional on preserving
the verified absence of original scientific payload access, features, fits
and scores, and on leaving every scientific choice unchanged.

| Perspective | Assessment and required boundary |
| --- | --- |
| Experimental design | The original failure provided no response, performance or feature signal for changing design. Preserve the exact TRAIN population, groups, historical folds, temporal selections and all comparison definitions. Recovery may repair local provisioning and execution custody only. |
| ML/CNN | No RF, CNN1D, spatiotemporal CNN or metadata-control fit started. There is no model outcome on which to choose architectures, representations, seeds, epochs, optimizers or hyperparameters. Preserve all frozen choices and the 28-fit budget. |
| Statistics | Zero scores and contrasts mean no outcome-based selection between attempts. This supports absence of adaptation from this failure; it does not supply new independent observations or expand inference beyond the frozen exploratory internal weak-label scope. Preserve metrics, aggregation and contrast rules. |
| Reproducibility | Preserve the original receipt, all 15 artifacts and closed terminal; commit them before operational changes. Bind a new namespace to their exact hashes and to the original method freeze. Record the earlier metadata incident and operational copying without zero-exposure shorthand. |
| MLOps | Missing worktree-local ignored containers is an established operational cause. Add metadata-only provisioning checks before a new receipt, retain worktree-root custody without fallback and preserve the original reader's per-row authentication. A new receipt requires its own later author decision and exact-freeze CI proof. |
| Adversarial reviewer | Treat any original payload access, feature, fit or score contradicting the evidence, any changed scientific file, reused authority, hidden retry or opened DEV/TEST boundary as blocking. Recovery is acceptable for preparation only when these checks deny on missing or inconsistent evidence. |

The resulting conclusion is
`RECOVERY_SCIENTIFIC_INDEPENDENCE=PRESERVED_WITH_EXPLICIT_OPERATIONAL_HISTORY`.
It supports preparing the bounded operational recovery. It does not grant a
scientific invocation and does not reclassify the original attempt as PASS.
If any stated premise fails, stop and request a new author decision without
creating a recovery receipt.

## Immutable scientific method

The original freeze continues to govern the population of 10,907 TRAIN rows
(3,858 GOLD and 7,049 background), 64 groups (32 positive and 32 background),
four historical folds and two acquisitions. Recovery creates no new labels,
backgrounds, sites, split or holdout. The seven comparisons, temporal
representations, group-level metrics and restricted claim scope remain those
in the original Study3 contracts and protocol.

The fixed budget remains 28 fits: 16 RF fits, four CNN1D fits, four
spatiotemporal CNN fits and four metadata LogReg fits. The acquisition-only
control requires zero fits. No GRU, adaptive search, retuning, seed search,
additional representation or extra fit is authorized.

The following 13 files must be byte-identical to the original method freeze
before a recovery can pass its gate:

| Scientific implementation | Scientific contract |
| --- | --- |
| `src/snbi_fragmentation/study3_domain.py` | `configs/study3/data-contract.json` |
| `src/snbi_fragmentation/study3_design.py` | `configs/study3/representation-contract.json` |
| `src/snbi_fragmentation/study3_io.py` | `configs/study3/cnn-contract.json` |
| `src/snbi_fragmentation/study3_temporal_features.py` | `configs/study3/model-contract.json` |
| `src/snbi_fragmentation/study3_cnn.py` | `configs/study3/fit-budget.json` |
| `src/snbi_fragmentation/study3_models.py` | `configs/study3/evaluation-contract.json` |
| `src/snbi_fragmentation/study3_metrics.py` | |

Both entrypoints must use the same scientific core. The allowed controller
changes concern evidence custody, authorization, metadata preconditions and
output namespace; they cannot create a second scientific implementation.

## Recovery contract and authorization gates

`configs/study3/execution-recovery-1-contract.json` must bind schema version 1,
the recovery identity, original method freeze, original receipt hash,
`CLOSED_CONSUMED` original state, zero original scientific reads/features/fits,
and the established failure class and root cause. It must record unchanged
method, population, folds, representations, models, hyperparameters, metrics
and fit budget; a maximum of one recovery invocation, 28 fits and zero
retries; and closed DEV, TEST, SILVER and video boundaries.

`preflight_recovery_1(root)` must fail closed before any recovery receipt or
scientific payload read unless all of the following hold:

1. The original 15 artifacts, exact receipt hash, closed terminal, scientific
   zero counters and pre-payload operational cause are authenticated.
2. The recovery contract is exact and the 13 scientific files match the
   original method freeze.
3. The two worktree-local payload paths exist with their exact sizes, regular
   file types and no symlink components; the operation remains metadata-only.
4. No recovery receipt, result or terminal has already consumed the new
   namespace, and all prohibited-data boundaries remain closed.
5. A separately authorized future recovery decision and its CI proof bind
   the exact new operational freeze and the required successful CI evidence.

`run_recovery_1(root)` may create a single-use receipt only after those gates
and a later science authorization. Its evidence belongs exclusively to
`artifacts/evidence/STUDY3_EXECUTION_RECOVERY_1/`. The new
`scripts/run_study3_recovery_1.py` must call this recovery entrypoint only.
The original entrypoint and evidence namespace retain their consumed state.

The reserved future local control paths are:

- `docs/study3/STUDY3_RECOVERY_1_SCIENCE_AUTHORIZATION.json`;
- `.bootstrap-test-tmp/study3/recovery-1-ci-proof.json`.

Neither control is created by this preparation decision. A subsequent
explicit science decision must have its own source digest, distinct from the
original scientific authorization, and bind the new frozen commit, recovery
identity, immutable contracts, one invocation, receipt custody, fit budget
and data boundaries. Its CI proof must refer to that exact commit and the
successful required jobs. This preparation prompt, old authorization text,
old control documents, green tests or green CI alone cannot activate science.

## Bounded preparation, verification and publication

After the preserved evidence checkpoint, the proposed operational freeze is
limited to these seven paths:

- `docs/study3/STUDY3_EXECUTION_RECOVERY_1_DECISION.md`;
- `configs/study3/execution-recovery-1-contract.json`;
- `src/snbi_fragmentation/study3_execution.py`;
- `scripts/run_study3_recovery_1.py`;
- `tests/test_study3_execution_recovery_1.py`;
- `configs/governance/phase-scope-v1.json`;
- `tests/test_study3_governance.py`.

The governance integration adds only the recovery script and recovery test to
the existing Study3 classification and preserves the original 19 entries.
Existing workflow discovery of `test_study3*.py` covers the new synthetic
suite, so no workflow change is needed. The new operational commit must be a
direct child of the evidence checkpoint, preserving ancestry
`original method freeze -> original evidence checkpoint -> recovery freeze`.

Required verification includes the authorized governance guards, original
Study3 synthetic tests, Study2-C/D regressions and recovery negative tests,
with zero scientific-dependency skips. Negative cases must deny consumed or
reused authority, changed original evidence, changed scientific method,
missing or malformed recovery contracts, wrong new freeze/CI evidence,
missing or malformed provisioned files, existing recovery evidence and
attempts to cross closed data boundaries. Synthetic checks must not read
experimental payloads or create a scientific receipt.

This decision does not certify completion of local gates, the new operational
commit, publication or CI. Their actual outcomes must be verified and reported
separately. Only after all required checks pass may the authorized freeze be
published and assessed at its exact SHA. No automatic CI retry, corrective
science run or continuation into recovery science follows from publication.

At successful preparation closeout the required state is:

```text
ATTEMPT1_EVIDENCE_PRESERVED=true
ROOT_CAUSE_CONFIRMED=true
PAYLOAD_PROVISIONED=true
SCIENTIFIC_METHOD_CHANGED=false
NEW_RECOVERY_METHOD_FROZEN=true
RECOVERY_PRE_SCIENCE_CI=PASS
SCIENTIFIC_RECOVERY_RUNS=0
RECOVERY_RECEIPT_CREATED=false
READY_FOR_RECOVERY_1_AUTHOR_DECISION=true
CURRENT_AUTHORIZED_ACTIVITY=NONE_AWAITING_AUTHOR_DECISION
```

These are closeout requirements, not assertions that pending freeze or CI
work has already passed. Stop after that preparation boundary and await the
author's separate recovery science decision.

## Local synthetic verification before staging

All commands used the explicitly selected existing Python interpreter with
`-B`, `PYTHONPATH=src:tests:.` and fresh synthetic temporary roots below
`.bootstrap-test-tmp/`. All 22 historical dependency pins matched. No package
installation or environment change was made.

| Suite/profile | Tests | Passes | Skips | Failures | Errors | Exit |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Study3, including Recovery 1 | 217 | 217 | 0 | 0 | 0 | 0 |
| Recovery 1, included above | 57 | 57 | 0 | 0 | 0 | 0 |
| Study2-C | 137 | 137 | 0 | 0 | 0 | 0 |
| Study2-D | 116 | 116 | 0 | 0 | 0 | 0 |
| Phase scope | 26 | 26 | 0 | 0 | 0 | 0 |
| TI3 scope | 15 | 15 | 0 | 0 | 0 | 0 |
| Study3 stdlib (`-S`) | 217 | 162 | 55 | 0 | 0 | 0 |

There were 511 distinct passing tests in the dependency-equipped profile;
the recovery subset and stdlib pass are not counted again. Expected failures,
unexpected successes and discovery errors were zero. Stdlib skips are limited
to optional scientific dependencies; the scientific dependency profile has
zero skips.

Recovery tests cover all 27 required cases, payload-location rejection before
receipt creation, immutable original evidence, both consumed namespaces and
the exact 28-fit schedule. Thirteen scientific files match the original
freeze byte for byte. The original admission and run functions match their
frozen AST, and the shared scientific execution block matches after only the
evidence writer name is normalized. Synthetic population, fold map, model
parameters, architectures, T=8, seed 42, 30 epochs, GMBA and seven contrasts
remain fixed. Controller fixtures simulate callbacks; historical synthetic
model tests use invented data. Neither category is experimental execution.

An independent agent reviewed the controller, runner, contract, governance
integration and synthetic tests without finding a material defect. No real
scientific preflight, original runner, recovery runner, recovery authorization,
recovery CI proof or recovery receipt was invoked or created. These local
results precede index guards, the operational freeze and remote CI; they do
not claim publication or grant scientific authority.
