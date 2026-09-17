# Governed agent instructions

These instructions apply to the entire repository. Decision owner:
**Leonardo Maximino Bernardo**. TI-0 and TI-1 are complete. LB0 is PASS and
SDR-2-A is RESOLVED. No further sandbox diagnostic or OS remediation is authorized.

## Current authority

The author approved TI2-CLOSEOUT-1 as PASS. The scientific attempt remains
blocked, preserved at `f3c6da78b04299475c7bb85e986eb7435b08bd22`; published
closeout is `a1d675f5dbbe3862621aebad2bcb80ab7584858d`.

**The sole canonical active-state source is `pyproject.toml [tool.snbi]`.**
This block is a documentary mirror, not an alternative authorization source:

```text
CURRENT_AUTHORIZED_ACTIVITY=NONE_AWAITING_AUTHOR_DECISION
TI2_EXECUTION=TERMINAL_BLOCKED_CLOSED
TI2_CLOSEOUT_1=PASS
TI2_EXECUTION_AUTHORIZED=false
TI2R_AUTHORIZED=false
TI3_PLUS_AUTHORIZED=false
METHOD_V1=INSUFFICIENT_EVIDENCE
G2_SPATIAL=BLOCKED_METHOD_V1
TRANSFORM_EXISTENCE=UNDETERMINED
G3=BLOCKED_DEPENDENCY_G2
E7=PASS_DOCUMENTARY
MERGE_AUTHORIZED=false
```

The [remediation decision](docs/decisions/AUTHORIZATION-TI2-PR6-REMEDIATION-1-2026-09-17.md)
authorizes only bounded implementation, tests, one individually approved
commit, fast-forward push, new-SHA CI verification and a separately approved
PR body update. After the commit, active state remains NONE_AWAITING_AUTHOR_DECISION
while the expressly approved publication checks complete. No new scientific
execution, second corrective commit, ready transition or merge is authorized.

Historical decisions are immutable records. Validators must never infer
permission from historical true text, documentation or green tests/CI.
Missing, unknown, conflicting and noncanonical truthy values fail closed.
Every E0–E7 entry must deny before examining a source path or invoking science.

## Required reading

Read README.md, pyproject.toml, the remediation decision, LOCAL_DEVELOPMENT.md,
LOCAL_SANDBOX.md, terminal-state.json and remediation evidence. Read the
TI2_EXECUTION_PLAN.md, TI2-CLOSEOUT-1 authorization and
AUTHORIZATION-TI2-TARGETED-GIT-APPROVALS-2026-09-17.md as historical context.
The newest explicit author decision governs its exact scope.

## Repository and experimental boundaries

- Write only below this standalone repository in the default sandbox, on
  `feat/ti2-registration-calibration`, within an announced exact allowlist.
- Do not search, list, glob, hash, stat or traverse parent directories, the home
  directory, the filesystem root or sibling repositories.
- Do not follow symlinks. A versioned symlink is blocking.
- Do not create nested AGENTS.md or AGENTS.override.md.
- Never inspect .env, credentials, tokens, cookies, SSH keys, credential stores
  or editor authentication. Approved GitHub commands use existing authentication.
- Treat data/, sources, videos, images, arrays, models, datasets and checkpoints
  as opaque. No opening, content hashing, metadata probing, FFmpeg/FFprobe,
  decoding, source-member access or pixel inspection. The old opaque-byte
  experimental hashing exception is not active.
- Preserve the historical 30 pilot items. Existing .raw files are headerless
  MP4-decoded pixel buffers, not raw detector data; do not open them.
- No labels, ledger, datasets, splits, baseline, CNN, training, evaluation,
  sealed-test access, TI-2R or TI-3–TI-8.

## Bounded maintenance and synthetic verification

This remediation may change authority guards, safe text checksums, temporal
APIs/metadata validation, analytical-uncertainty classification, associated
tests, CI and documents. Do not change method-v1 matcher, grid, mask, margin,
thresholds, minimum matches, transform fitting, matrices or ROI. No experimental
physical-coordinate conversion or uncertainty propagation.

Do not invoke scripts/run_ti2.py as a scientific command. Denial tests use
mocks or control-flow inspection, without source access. Authorized unit tests
use tracked text and synthetic fixtures only. Local temporary subtrees are
fresh and controlled inside ignored .bootstrap-test-tmp/, never experimental
bytes or pre-existing external temporary content. Run the data guard first.

No local installation. Dependency-free tests report optional skips explicitly.
Only the separate pinned CI job runs exactly the five in-memory
SyntheticImageMatchingTests, requiring 5 passes and zero skips/failures/errors/
expected failures/unexpected successes. Synthetic tests grant no experimental
authority. Editor task allowlists remain unchanged. Historical regression
tests may use their own fresh temporary subtree in clean CI; locally the
temporary root stays inside the repository.

## Sandbox, Git and remote approvals

- no sudo, su, doas, local installation, OS/service/kernel/AppArmor change,
  mount, chmod, chown or ACL change;
- no fallback outside the sandbox after startup failure;
- no full access, danger-full-access, --yolo or bypass;
- no network except exact author-approved Git/GitHub operations;
- no pull, fetch, checkout, switch, reset, clean, restore, stash, rebase, merge,
  cherry-pick, amend or force;
- no git add ., git add -A, glob staging, git commit -am or --no-verify;
- no gh pr ready, gh pr merge or automatic reviewer requests.

Read-only .git protection is intentional. Show exact paths, diff, tests and
guards before separately approving exact-path staging, the single commit and
fast-forward push. Review staged content/checksums; never alter permissions.
Git metadata denial is distinct from a sandbox startup failure and grants no bypass.

Remote preflight must match the starting SHA, open Draft PR #6 and successful
historical CI. After push require both jobs and checksum step successful at
the new SHA, with no automatic rerun or second corrective commit. Only then
prepare and separately approve an update to the PR body. Keep it OPEN/DRAFT
and unmerged; ready and merge require a new author decision.

## Evidence and stop conditions

Preserve historical logs, authorizations and observations. Versioned publication
evidence records only the completed older closeout. The new commit SHA and CI
URL belong only in the effective PR body and terminal author report.

Report exact counters, checksum counts and commands/exit codes by boundary;
omit private paths, hostnames, environment dumps and secrets. Stop on preflight
divergence, scope expansion, experimental access, scientific retuning, unexplained
changes or sandbox failure without workaround. Refused Git approval means
BLOCKED_GIT_APPROVAL; unavailable remote tooling means BLOCKED_REMOTE_TOOL;
failed/cancelled/required-skipped CI means BLOCKED_CI; pending means BLOCKED_CI_PENDING.

Success requires TI2_PR6_REMEDIATION_1=PASS_READY_FOR_AUTHOR_REVIEW, a clean
worktree, equal local/remote SHA, an open Draft PR and both jobs successful.
PR6_MERGE_READINESS=READY_FOR_AUTHOR_REVIEW is readiness for the author's
decision only; MERGE_AUTHORIZED=false.
