# Governed agent instructions

These instructions apply to the entire repository. They remain in force until a later, author-approved decision is committed to the repository.

## Authority

- Decision owner: **Leonardo Maximino Bernardo**.
- TI-0 and TI-1 are complete.
- The TI-2 method-v1 scientific attempt is terminally blocked. Its evidence is
  preserved at `f3c6da78b04299475c7bb85e986eb7435b08bd22`.
- **Only TI2-CLOSEOUT-1 is authorized now**: documentary reconciliation,
  deterministic checks, an approved Git checkpoint, push, a Draft PR and remote
  CI verification. No TI-2R or new scientific analysis is authorized.
- LB0 is PASS and SDR-2-A is RESOLVED; repository writes in the default sandbox
  are authorized on `feat/ti2-registration-calibration`.
- Individual approvals remain required for the exact Git operations; the
  closeout authority permits publication of the scientifically blocked result.
- TI-3 through TI-8 remain blocked.
- If instructions conflict or scope is ambiguous, apply the most restrictive rule and stop with `BLOCKED`.

Current authoritative state:

```text
CURRENT_AUTHORIZED_ACTIVITY=TI2_CLOSEOUT_1
TI2_EXECUTION=TERMINAL_BLOCKED_PENDING_CLOSEOUT
METHOD_V1=INSUFFICIENT_EVIDENCE
G2_SPATIAL=BLOCKED_METHOD_V1
TRANSFORM_EXISTENCE=UNDETERMINED
G3=BLOCKED_DEPENDENCY_G2
E7=PASS_DOCUMENTARY
TI3_PLUS_AUTHORIZED=false
```

Historical compatibility sentinels retained for the unchanged bootstrap
validator follow. They record the prior execution authority; they **do not
authorize scientific execution now**. A static validator PASS does not override
the current closeout-only decision.

```text
TI2_EXECUTION_AUTHORIZED=true
AUTHORIZED_ACTIVITY=TI2_REGISTRATION_CALIBRATION
```

## Required reading

Before acting, read:

1. `README.md`;
2. `docs/decisions/AUTHORIZATION-TI2-CLOSEOUT-1-2026-09-17.md`;
3. `docs/protocols/LOCAL_DEVELOPMENT.md`;
4. `docs/security/LOCAL_SANDBOX.md`;
5. `docs/protocols/TI2_EXECUTION_PLAN.md`;
6. `docs/decisions/AUTHORIZATION-TI2-TARGETED-GIT-APPROVALS-2026-09-17.md`.

The closeout decision supersedes prior execution permissions for this session.
The approved plan is retained as the specification of the historical attempt;
reading it, a test PASS or green CI does not authorize another scientific run.

## Repository boundary

- Write only below the resolved standalone repository root, in the default
  sandbox and on `feat/ti2-registration-calibration`.
- Do not reopen experimental sources, MP4 members, frames or images. Only
  cryptographic integrity hashing of exact existing files as opaque bytes is
  allowed when needed; no decoding, metadata probing or pixel interpretation.
- Do not search, list, glob, hash, `stat`, or traverse `/`, `/home`, `$HOME`, parent directories, or sibling repositories.
- Do not follow symlinks. A versioned symlink is a blocking violation.
- Do not create nested `AGENTS.md` or `AGENTS.override.md` files.
- Never read `.env`, credentials, tokens, cookies, SSH private keys, Git credential stores, or editor authentication state.

No further sandbox/AppArmor diagnostic is authorized or required after SDR-2-A
closure. The diagnostic script, optional probe, and historical manual diagnostic
protocol remain historical tools; do not run them under the TI-2 authorization.

The external temporary-directory exception applies to the pre-existing TI-0/TI-1
regression suite in a clean CI checkout. A test may access only a fresh subtree
created by its own `TemporaryDirectory`, must not inspect pre-existing temporary
content or follow links, and must remove the subtree at completion. Local TI-2
tests may use only fresh synthetic temporary subtrees inside the repository
(for example `.bootstrap-test-tmp/`), with no experimental bytes or symlinks.

## Experimental boundary

Treat these paths and any external scientific-source location as opaque:

- `data/raw/`;
- `data/interim/`;
- `data/processed/`;
- `data/derived/`;
- video, image, array, dataset, checkpoint, or model files.

No pixel access, visualization, FFmpeg invocation, MP4-member access or further
decoding is permitted. The only byte-read exception is the bounded integrity
hash operation above. The historical pilot contained exactly 30 frames/items:

- ESM1, ESM2, ESM3: indices 0, 73, 146, 219, 293;
- ESM4, ESM5, ESM6: indices 0, 98, 197, 295, 394.

Those frames were decoded from MP4 without additional losses, preserving native
video resolution and pixel format. Existing `.raw` files are headerless decoded
pixel buffers, **not raw detector data**. Keep all experimental binaries ignored
and outside the Git index. Do not change, regenerate or add any experimental item.

## Authorized closeout work

The exact file allowlist must be declared before changes, limited to:

- root agent instructions;
- local-development and sandbox documentation;
- textual decisions, manifests, metadata and documentary configurations;
- deterministic tests of the approved temporal and nominal-scale semantics;
- reports, checksums and gate-state reconciliation;
- separately approved exact-path staging, commit, fast-forward push and Draft
  PR creation, followed by remote CI verification.

Existing synthetic suites may run, but do not modify `src/`, matching,
extraction/decoding, correspondences, matrices, ROI or scientific parameters.
If such a change is necessary, stop with `SOURCE_OR_SCIENTIFIC_CHANGE_REQUIRED`.

The local VS Code task may run only the three bootstrap policy-test modules.
The full synthetic regression suite runs in a clean CI checkout. The explicit
resumption authority also permits running it locally with `TMPDIR` set to an
ignored `.bootstrap-test-tmp/` subtree inside the repository. Legacy TI-0/TI-1
tests may create small, non-decodable synthetic byte fixtures there, but may
never use experimental bytes or invoke media decoding. This does not expand
the versioned VS Code task allowlist.

## Prohibited operations

- no `sudo`, `su`, `doas`, package installation, system service changes, kernel changes, AppArmor changes, mounts, `chmod`, `chown`, or ACL changes;
- no fallback outside the sandbox after a sandbox failure;
- no network access except an exact Git/GitHub action explicitly authorized in the current user instruction;
- no media decoding or pixel access, including the frozen pilot and quartiles;
- no mass extraction, additional frames, native image modification, label
  creation or cumulative-circle differencing;
- no projective/non-rigid registration or retrospective relaxation of limits;
- no labels, event ledger, dataset, temporal split, baseline, CNN, training, evaluation, or sealed-test access;
- no commit, push, merge, force operation, branch switch, reset, clean, or worktree mutation unless the current user instruction explicitly authorizes that exact Git operation.
- no merge of the TI-2 Draft PR without a new author decision.
- no `pull`, `merge`, `rebase`, `reset`, `clean`, `restore`, `stash`, `checkout`
  or `switch`; no `git add .`, `git add -A`, `git commit -a`, `--no-verify`,
  `--force` or `--force-with-lease`.

## Sandbox and approvals

- Default-sandbox repository writes are explicitly authorized by the closure/
  execution decision after the successful real Codex smoke test.
- Read-only `.git` protection is expected. A denial writing `.git/index.lock`
  does not itself indicate a sandbox startup or SDR-2-A failure. Never change
  permissions or bypass that protection.
- For an authorized Git metadata write, request approval for each exact
  `git add -- <explicit reviewed paths>` operation and a separate approval for
  `git commit`. No blanket Git approval, wildcard staging or `git add -A`.
- The closeout decision authorizes publication despite G2-SPATIAL/G3 being
  blocked. First require reconciled text, passing tests with exact pass/skip
  counts, passing guards/checksums and zero tracked experimental binaries.
  Obtain separate approval for a read-only remote-reference check and establish
  that push is fast-forward, then request the exact branch push approval.
  Request Draft PR creation separately and verify its remote CI to completion.
  These
  exact approved Git/GitHub actions are the sole exception to the default
  sandbox write restriction; they do not authorize other elevated commands,
  credential inspection, full access, scientific execution outside the
  sandbox, or a TI-2 PR merge.
- Network remains disabled except for the exact authorized Git/GitHub actions.
- The repository's inert `bwrap` capability probe is diagnostic only; a PASS
  does not establish Codex/seccomp readiness and does not authorize writes.
- A `bwrap`, namespace, or seccomp failure is `BLOCKED`; do not retry unsandboxed.
- Never use full-access, danger-full-access, `--yolo`, or an equivalent bypass.
- No operating-system remediation is authorized by this repository.

## Working-tree protocol

1. Confirm repository, branch and HEAD. Require a clean initial status or, on
   explicitly authorized resumption, reconcile every preserved change with
   the interrupted task before continuing.
2. State the exact file allowlist before editing.
3. Stop if an unexplained pre-existing change overlaps the task. Preserve
   authorized partial work on resumption; do not reset or clean it.
4. Use deterministic, dependency-free tests where practical.
5. Run the repository data guard before other tests.
6. Show the final diff and status.
7. Report commands, exit codes, and limitations without usernames, home paths, hostnames, environment variables, or credentials.

## Mandatory stop conditions

Return `BLOCKED` without attempting a workaround when:

- sandbox isolation fails;
- a write path is outside the repository, or a read path is outside the
  declared allowlist including the exact operator-authorized source;
- experimental bytes would be interpreted, or a read exceeds the explicitly
  bounded opaque-byte integrity-hashing exception;
- installation, unapproved network access, or an OS change appears necessary;
- a tracked symlink or forbidden binary/data path is found;
- the worktree contains unexplained changes;
- the requested action could execute TI-2R, any new scientific analysis, TI-3
  or a later phase, or requires changes to scientific source/parameters.

Return `TI2_CLOSEOUT_1 = PASS | PARTIAL | BLOCKED`. PASS requires documentary
reconciliation, passing tests/guards/checksums, commit, push, an open Draft PR,
completed green remote CI, a clean worktree and zero tracked experimental
binaries. No merge is permitted. Documentary PASS does not approve either
scientific gate, establish transformation existence or authorize TI-3.
