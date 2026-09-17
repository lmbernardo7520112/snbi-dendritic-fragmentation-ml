# Governed agent instructions

These instructions apply to the entire repository. They remain in force until a later, author-approved decision is committed to the repository.

## Authority

- Decision owner: **Leonardo Maximino Bernardo**.
- TI-0 and TI-1 are complete.
- The TI-2 execution plan is approved.
- **TI-2 execution is not authorized.**
- Only the governed local VS Code bootstrap is currently authorized.
- TI-3 through TI-8 remain blocked.
- If instructions conflict or scope is ambiguous, apply the most restrictive rule and stop with `BLOCKED`.

Machine-readable sentinel:

```text
TI2_EXECUTION_AUTHORIZED=false
AUTHORIZED_ACTIVITY=LOCAL_VSCODE_BOOTSTRAP
```

## Required reading

Before acting, read:

1. `README.md`;
2. `docs/decisions/AUTHORIZATION-TI2-PLAN-APPROVAL-LOCAL-BOOTSTRAP-2026-09-17.md`;
3. `docs/protocols/LOCAL_DEVELOPMENT.md`;
4. `docs/security/LOCAL_SANDBOX.md`;
5. `docs/protocols/TI2_EXECUTION_PLAN.md`.

Reading an approved plan does not authorize its execution.

## Repository boundary

- Operate only below the resolved repository root.
- Do not search, list, glob, hash, `stat`, or traverse `/`, `/home`, `$HOME`, parent directories, or sibling repositories.
- Do not follow symlinks. A versioned symlink is a blocking violation.
- Do not create nested `AGENTS.md` or `AGENTS.override.md` files.
- Never read `.env`, credentials, tokens, cookies, SSH private keys, Git credential stores, or editor authentication state.

The sole external read-only diagnostic exception is the exact allowlist in
`scripts/check_local_environment.py`: version calls for `git`, `bwrap`,
`unshare`, and `code`; Python/platform identifiers; the three exact proc/sys
keys documented in `docs/security/LOCAL_SANDBOX.md`; and the inert `bwrap`
capability probe when explicitly requested. This exception permits no search,
enumeration, data access, credential access, write, or additional command.

The only temporary-directory exception applies to the pre-existing TI-0/TI-1
regression suite in a clean CI checkout. A test may access only a fresh subtree
created by its own `TemporaryDirectory`, must not inspect pre-existing temporary
content or follow links, and must remove the subtree at completion.

## Opaque experimental areas

Treat these paths and any external scientific-source location as opaque:

- `data/raw/`;
- `data/interim/`;
- `data/processed/`;
- `data/derived/`;
- video, image, array, dataset, checkpoint, or model files.

Do not enumerate, open, decode, hash, inspect metadata, or otherwise access their contents during the local bootstrap.

## Authorized bootstrap work

Only the following classes of change are authorized:

- root agent instructions;
- local-development and sandbox documentation;
- versioned VS Code settings and explicit tasks;
- repository data-name guardrails;
- read-only local-environment diagnostics;
- tests using text, JSON, mocks, or temporary synthetic paths;
- CI, Makefile, contribution guidance, and PR-template changes required to enforce the bootstrap.

Tests must not implement registration, calibration, image geometry, frame handling, labels, datasets, baselines, or models—even with synthetic images.

The local VS Code task may run only the three bootstrap policy-test modules.
The legacy TI-0/TI-1 regression suite is reserved for a clean CI checkout; it
may create small, non-decodable synthetic byte fixtures, but it may not use
experimental bytes or invoke media decoding.

## Prohibited operations

- no `sudo`, `su`, `doas`, package installation, system service changes, kernel changes, AppArmor changes, mounts, `chmod`, `chown`, or ACL changes;
- no fallback outside the sandbox after a sandbox failure;
- no network access except an exact Git/GitHub action explicitly authorized in the current user instruction;
- no `ffmpeg`, `ffprobe`, OpenCV, Pillow, ImageMagick, video decoder, or image reader;
- no frame extraction or decoding and no pixel access;
- no spatial registration, ROI materialization, scale estimation, or calibration;
- no labels, event ledger, dataset, temporal split, baseline, CNN, training, evaluation, or sealed-test access;
- no commit, push, merge, force operation, branch switch, reset, clean, or worktree mutation unless the current user instruction explicitly authorizes that exact Git operation.

## Sandbox and approvals

- Diagnostic mode: `read-only`, user approval on request, network disabled.
- Write mode is forbidden until a real Codex command starts successfully in
  the Linux sandbox and the author separately authorizes workspace writes.
- The repository's inert `bwrap` capability probe is diagnostic only; a PASS
  does not establish Codex/seccomp readiness and does not authorize writes.
- A `bwrap`, namespace, or seccomp failure is `BLOCKED`; do not retry unsandboxed.
- Never use full-access, danger-full-access, `--yolo`, or an equivalent bypass.
- No operating-system remediation is authorized by this repository.

## Working-tree protocol

1. Confirm repository, branch, HEAD, and a clean initial status.
2. State the exact file allowlist before editing.
3. Stop if a pre-existing change overlaps the task.
4. Use deterministic, dependency-free tests where practical.
5. Run the repository data guard before other tests.
6. Show the final diff and status.
7. Report commands, exit codes, and limitations without usernames, home paths, hostnames, environment variables, or credentials.

## Mandatory stop conditions

Return `BLOCKED` without attempting a workaround when:

- sandbox isolation fails;
- a requested path is outside the repository or the declared allowlist;
- raw/derived experimental data might be accessed;
- installation, network, or an OS change appears necessary;
- a tracked symlink or forbidden binary/data path is found;
- the worktree contains unexplained changes;
- the requested action could execute TI-2 or any later phase.
