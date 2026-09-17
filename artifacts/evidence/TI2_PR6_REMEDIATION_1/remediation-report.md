# TI2-PR6-REMEDIATION-1 — verification before publication

This evidence describes completed local maintenance and tests before the single
authorized commit. The new commit SHA and new CI URL will be recorded only in
the effective PR body and terminal report after publication, never in this file.

## Initial checkpoint and scope

Starting SHA: `a1d675f5dbbe3862621aebad2bcb80ab7584858d`.
Branch: `feat/ti2-registration-calibration`. Initial index/worktree clean;
standalone real .git; expected origin and remote SHA; PR #6 OPEN/DRAFT/unmerged,
base main; historical CI 35265631917 completed successfully. All preconditions
were checked before edits. The author accepted TI2-CLOSEOUT-1 as PASS.

The sole active-state source is `pyproject.toml [tool.snbi]`.
TI2_EXECUTION=TERMINAL_BLOCKED_CLOSED; TI2_CLOSEOUT_1=PASS;
CURRENT_AUTHORIZED_ACTIVITY=NONE_AWAITING_AUTHOR_DECISION;
TI2_EXECUTION_AUTHORIZED=false; TI2R_AUTHORIZED=false; TI3_PLUS_AUTHORIZED=false.
G2_SPATIAL=BLOCKED_METHOD_V1, G3=BLOCKED_DEPENDENCY_G2 and
TRANSFORM_EXISTENCE=UNDETERMINED remain unchanged; E7=PASS_DOCUMENTARY.

## Implemented corrections

- Exact typed canonical authorization fails closed for absent, unknown,
  conflicting or truthy noncanonical fields. No historical text is consulted.
  Bootstrap PASS means coherent policy with scientific readiness BLOCKED;
  scope declares no authorized scientific phase. Runner guard precedes every
  entry, source argument and optional scientific import.
- Safe stdlib checksum verification uses exact bytes, canonical relative/index
  paths, no-follow descriptors and deterministic counts. Experimental/private
  paths and malformed/duplicate/self/untracked/nonregular inputs are rejected.
- CI retains deterministic-contracts and adds scientific-synthetic-contracts,
  Python 3.12, read-only contents and nonpersisted checkout credentials.
  NumPy 1.26.4 and SciPy 1.11.4 are installed only on that runner; Pillow is
  unnecessary. The strict runner requires exactly the five frozen test IDs,
  imported pinned versions and 5/5 passes, with every other result count zero.
- Operational time semantics use Decimal and one validated source→offset map.
  The existing 30-item manifest now requires elapsed, experimental and deprecated
  physical_time_s fields, with exact recalculation and no playback-FPS input.
  Manifest/config bytes, source/frame hashes and decode metadata are unchanged.
- Per-axis discretization 1/sqrt(12)=0.2886751345948129 pixel is MODELLED with
  evidence_kind=ANALYTICAL_ASSUMPTION and explicit uniform-quantization
  assumption. Validator requires finite nonnegative value, unit, method and
  provenance. Physical calibration remains UNRESOLVED with zero conversions.
- Versioned historical publication evidence and the six-point method-v1
  limitations addendum close the documentary gaps without rerunning E6.

## Local verification

Full dependency-free suite: **173 run / 168 passed / 5 skipped / 0 failures /
0 errors / 0 expected failures / 0 unexpected successes**.
The five optional NumPy/SciPy image-matching tests skip under -S; they are
required without skips in the separate remote job. Their IDs/reasons and actual
local runner output are retained in local-verification.json. No dependency was
installed locally and no scientific matching runner was invoked locally.

Data guard: PASS, content_bytes_read=0, violations=[].
Bootstrap/scope: PASS with all scientific permissions false.
All 40 Python files compile in memory; no bytecode compilation output is needed.
AST comparison confirms unchanged scientific bodies except approved entry
guards/import placement and textual time/uncertainty validators. Frozen matching,
calibration algorithm, grid, masks, thresholds, registration configurations,
gate decisions and experimental observations remain unchanged.
Independent reviews found no blocking defect.

historical_checksum_count=70. Before staging, 72/72 tracked-text entries passed.
After approved first staging, **84 listed / 84 unique / 84 verified**, PASS,
with no violations. New files had no untracked exception; verification used
the real index. Counts and evidence are retained in local-verification.json.
The checksum file excludes itself and contains no experimental entry.

## Publication condition and limits

This file does not claim the future new-SHA CI has passed. One approved commit
and fast-forward push are permitted, followed by both required CI jobs. Only
after success may the PR body be updated with separate approval. No automatic
rerun, second corrective commit, ready transition, merge or reviewer request.

No experimental file, content hash or pixel was accessed; no FFmpeg/FFprobe,
redecoding, new frames, correspondences, matrices, ROI, E0–E7, TI-2R or TI-3–TI-8
execution occurred. Synthetic fixtures do not establish scientific gate PASS.
After the commit, active authority stays NONE_AWAITING_AUTHOR_DECISION, and
ready/merge require a new author decision.

## Exact remediation file scope

This single remediation checkpoint changes 39 files (27 modified, 12 new).
The earlier closeout alone changed 27; its full PR comparison had 69.

- `.github/workflows/ci.yml`
- `AGENTS.md`
- `README.md`
- `artifacts/evidence/TI2/checksums.sha256`
- `artifacts/evidence/TI2/execution-report.md`
- `artifacts/evidence/TI2/terminal-state.json`
- `artifacts/evidence/TI2_PR6_REMEDIATION_1/closeout-publication-record.md`
- `artifacts/evidence/TI2_PR6_REMEDIATION_1/commands.json`
- `artifacts/evidence/TI2_PR6_REMEDIATION_1/local-verification.json`
- `artifacts/evidence/TI2_PR6_REMEDIATION_1/method-v1-limitations.md`
- `artifacts/evidence/TI2_PR6_REMEDIATION_1/remediation-report.md`
- `configs/calibration/bottom-up.json`
- `configs/calibration/top-down.json`
- `docs/decisions/AUTHORIZATION-TI2-PR6-REMEDIATION-1-2026-09-17.md`
- `docs/gates/TI2_GATE_PLAN.md`
- `docs/protocols/LOCAL_DEVELOPMENT.md`
- `docs/protocols/TI2_CONTRACT_MATRIX.md`
- `docs/protocols/TI2_EXECUTION_PLAN.md`
- `docs/risks/TI2_RISK_REGISTER.md`
- `docs/security/LOCAL_SANDBOX.md`
- `pyproject.toml`
- `scripts/check_local_bootstrap.py`
- `scripts/check_ti2_checksums.py`
- `scripts/check_ti2_scope.py`
- `scripts/run_scientific_synthetic_contracts.py`
- `scripts/run_ti2.py`
- `scripts/ti2_authority.py`
- `src/snbi_fragmentation/ti2_geometry.py`
- `src/snbi_fragmentation/ti2_pilot.py`
- `src/snbi_fragmentation/timebase.py`
- `tests/test_local_bootstrap.py`
- `tests/test_scientific_synthetic_runner.py`
- `tests/test_scope_guard.py`
- `tests/test_ti2_authority.py`
- `tests/test_ti2_checksums.py`
- `tests/test_ti2_execution.py`
- `tests/test_ti2_geometry.py`
- `tests/test_ti2_pilot.py`
- `tests/test_timebase.py`
