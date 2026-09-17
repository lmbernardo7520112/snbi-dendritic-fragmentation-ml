# Authorization record — LB0/SDR-2-A closure, PR #5 merge and TI-2 execution

## Metadata

- Date: 2026-09-17
- Decision owner: Leonardo Maximino Bernardo
- Repository: lmbernardo7520112/snbi-dendritic-fragmentation-ml
- PR: #5
- Decision status: APPROVED

## Formal closure

The author approved:

~~~text
LB0_LOCAL_ACCEPTANCE: PASS
SDR2A_STATUS: RESOLVED
REAL_CODEX_SANDBOX: PASS_SMOKE
ROLLBACK_REQUIRED: false
~~~

No further sandbox or AppArmor diagnostic is authorized or required in this
phase.

## PR #5 authority

The author authorized:

1. marking PR #5 ready for review;
2. merging PR #5 into `main`, conditional on green CI;
3. fast-forward synchronization of the local `main` after merge;
4. creation of `feat/ti2-registration-calibration` from the updated
   `main`.

## Local Codex authority

After the merge, the local Codex is authorized to write only inside the
standalone repository and only on the dedicated TI-2 branch, using the default
sandbox.

Explicitly prohibited:

- sudo or operating-system mutation;
- full access, danger-full-access, `--yolo` or sandbox bypass;
- credentials, tokens or authentication files;
- writes outside the repository;
- unapproved network access;
- modification of the raw experimental source.

## TI-2 execution authority

The author authorized complete execution of TI2-E0 through TI2-E7 under the
approved v1.0 executive plan.

Permitted:

- code, tests, configurations and documentation;
- professional commits;
- one Draft TI-2 pull request;
- read-only access to the experimental source path explicitly supplied by the
  human operator;
- deterministic decoding of only the 30 frozen lossless pilot images;
- ignored local derived-data storage;
- registration, independent validation, ROI, scale and uncertainty analysis;
- evidence packages and G2-SPATIAL/G3 decisions.

Frozen pilot:

| Group | Sources | Frame indices | Images |
|---|---|---|---:|
| bottom-up | ESM1, ESM2, ESM3 | 0, 73, 146, 219, 293 | 15 |
| top-down | ESM4, ESM5, ESM6 | 0, 98, 197, 295, 394 | 15 |

The clean radiographies are the canonical references:

- ESM2 and ESM3 map to ESM1;
- ESM5 and ESM6 map to ESM4.

## Preserved prohibitions

- mass extraction;
- any frame outside the frozen list;
- labels or cumulative-circle differencing;
- event ledger;
- ML dataset, temporal split or test lock;
- classical baseline;
- CNN, training or evaluation;
- TI-3 through TI-8;
- merge of the future TI-2 Draft PR without a new author decision.

## Return condition

TI-2 must continue without command-by-command authorization and return only
when:

~~~text
G2-SPATIAL: PASS | PARTIAL | BLOCKED
G3: PASS | PARTIAL | BLOCKED
~~~

or when a real blocker requires scope expansion.

A blocking invariant, attempted OS mutation, request for additional frames,
need for a projective/non-rigid transform, or need to open TI-3 must stop the
execution fail-closed.
