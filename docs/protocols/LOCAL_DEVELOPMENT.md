# Governed local development protocol

## Active state and authority

The author accepted TI2-CLOSEOUT-1 as PASS. The sole canonical active state is
`pyproject.toml [tool.snbi]`: TI2 execution TERMINAL_BLOCKED_CLOSED, activity
NONE_AWAITING_AUTHOR_DECISION, and TI2/TI2R/TI3+ execution permissions false.
The [remediation decision](../decisions/AUTHORIZATION-TI2-PR6-REMEDIATION-2-2026-09-17.md)
permits only its single bounded maintenance/publication transaction.
After its commit, that closed state remains active while the expressly
authorized push, CI verification and Draft PR body update complete.
REMEDIATION-2 is a single-use corrective authority after partial acceptance of
REMEDIATION-1. It addresses exactly the audited gate, MEASURED and direct I/O
guard gaps. Both TI-2 and TI-2R are explicitly blocked in canonical authority.

METHOD_V1=INSUFFICIENT_EVIDENCE; G2_SPATIAL=BLOCKED_METHOD_V1;
TRANSFORM_EXISTENCE=UNDETERMINED; G3=BLOCKED_DEPENDENCY_G2;
E7=PASS_DOCUMENTARY. LB0 remains PASS and SDR-2-A RESOLVED.
Bootstrap PASS now means coherent safeguards with scientific readiness BLOCKED
and codex_write_readiness=BLOCKED_AWAITING_AUTHOR_DECISION, not scientific
execution authority. Old authorizations remain historical, never parsed as
current permission.

## Local boundaries

Use only the standalone repository on feat/ti2-registration-calibration and
the default sandbox. Do not inspect credentials, parent/sibling locations,
experimental data or ignored derivatives. No source/ZIP/MP4/raw/image opening,
hashing, pixel inspection, FFmpeg/FFprobe, E0–E7 execution or scientific retuning.
No local dependencies, operating-system changes or sandbox diagnostics.

Workspace sanitization is the historical author attestation, not a new scan of
ignored files. The Git data guard examines only index paths and reports
content_bytes_read=0. Existing derivatives remain opaque and ignored.

## Verification under this decision

1. Confirm exact branch/starting SHA, standalone .git, clean index/worktree,
   origin, equal remote SHA and open Draft PR #6; verify historical CI.
2. Run the repository data guard before tests.
3. Run bootstrap and scope guards; both must report no scientific authorization.
4. Compile authorized Python source in memory and run the dependency-free suite
   with fresh synthetic temporary subtrees inside ignored .bootstrap-test-tmp/.
5. Validate the current gate blocks, canonical authority, MEASURED and preserved
   MODELLED contracts, plus zero-access I/O guards with mocks and ExplodingPath.
   Existing textual metadata regressions remain allowed; never open raw paths.
6. Run the stdlib checksum verifier. Only safe tracked text is admissible; new
   untracked files cannot be exempted. Verify the final staged inventory before
   the sole commit and exclude the checksum manifest itself.
7. Report exact run/pass/skip/failure/error counts and review the full diff.

No scientific command is an authorized local verification. Denial tests mock
boundaries or inspect control flow. Legacy tests use only controlled synthetic
fixtures. No experimental coordinate conversion or uncertainty propagation.
The editor task allowlist remains unchanged. The separate CI scientific job
runs only five synthetic in-memory tests with exactly pinned NumPy/SciPy; the
deterministic job remains dependency-free and reports its five optional skips.
The current instruction also permits those five synthetic tests locally when
the required dependencies are already available; no installation or external
tool invocation. No workflow/dependency changes are needed. The shared authority
lives in `src/snbi_fragmentation/ti2_authority.py`; the script is only a facade.
`LOCAL_BOOTSTRAP.md` and `TI2_GATE_PLAN.md` are the explicit current-gate allowlist.

## Git and remote protocol

Request separate approvals for exact-path staging, the single commit and
fast-forward push. Review status, ordered paths, diff and guards first; inspect
staged bytes/checksums. No all-files staging, force, amend, second corrective
commit, fetch, branch/history repair or permission changes.

Require both new-SHA CI jobs successful and the checksum step PASS; require
five scientific tests passed with zero skips. No automatic CI rerun. Only then
prepare an ignored sanitized PR body and separately approve its update.
Keep PR #6 OPEN/DRAFT/unmerged. Ready and merge require new author authorization.
Unavailable tooling must not trigger installation or credential inspection.

## Evidence and completion

Preserve historical logs and decisions. The versioned publication record
contains only the older completed closeout; new commit SHA/CI URL appear only
afterward in the effective PR body and terminal report, avoiding self-reference.
Report commands/exit codes without private paths, hostnames, environment dumps
or credentials. A scoped grouped inventory must state its limits explicitly.

Success means PASS_READY_FOR_FINAL_MERGE_DECISION, equal local/remote SHA, clean
worktree and open Draft PR with required CI complete. Active authority remains
NONE_AWAITING_AUTHOR_DECISION; green CI does not approve the scientific gates.
