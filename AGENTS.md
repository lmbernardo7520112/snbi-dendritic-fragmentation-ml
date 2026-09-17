# Governed agent instructions

These instructions apply to the entire repository. They remain in force until a later, author-approved decision is committed to the repository.

## Authority

- Decision owner: **Leonardo Maximino Bernardo**.
- TI-0 and TI-1 are complete.
- The TI-2 execution plan is approved.
- **TI-2 execution E0–E7 is authorized**, exclusively under the approved
  executive plan and the 17 September 2026 closure/execution decision.
- LB0 is PASS and SDR-2-A is RESOLVED; repository writes in the default sandbox
  are authorized on `feat/ti2-registration-calibration`.
- The author resumed TI-2 after the operational Git-index write block, with
  individual approvals for exact Git operations; this does not reopen SDR-2-A.
- TI-3 through TI-8 remain blocked.
- If instructions conflict or scope is ambiguous, apply the most restrictive rule and stop with `BLOCKED`.

Machine-readable sentinel:

```text
TI2_EXECUTION_AUTHORIZED=true
AUTHORIZED_ACTIVITY=TI2_REGISTRATION_CALIBRATION
```

## Required reading

Before acting, read:

1. `README.md`;
2. `docs/decisions/AUTHORIZATION-LB0-SDR2A-CLOSURE-PR5-MERGE-TI2-EXECUTION-2026-09-17.md`;
3. `docs/protocols/LOCAL_DEVELOPMENT.md`;
4. `docs/security/LOCAL_SANDBOX.md`;
5. `docs/protocols/TI2_EXECUTION_PLAN.md`;
6. `docs/decisions/AUTHORIZATION-TI2-TARGETED-GIT-APPROVALS-2026-09-17.md`.

The execution decision supersedes the historical planning/bootstrap-only
restriction. Reading a plan or obtaining a gate result does not authorize any
additional phase.

## Repository boundary

- Write only below the resolved standalone repository root, in the default
  sandbox and on `feat/ti2-registration-calibration`.
- Read experimental sources only at the exact location explicitly supplied by
  the operator, and only the manifest-declared files/members needed by TI-2.
  This is a narrow read-only exception; do not search for source locations,
  enumerate neighboring paths, or copy raw sources into the repository.
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

Except for the exact operator-authorized source and the frozen TI-2 pilot,
treat these paths and any external scientific-source location as opaque:

- `data/raw/`;
- `data/interim/`;
- `data/processed/`;
- `data/derived/`;
- video, image, array, dataset, checkpoint, or model files.

Do not enumerate, open, decode, hash, inspect metadata, or otherwise access
unapproved experimental content. TI2-E0 may revalidate the approved source
hashes read-only. TI2-E1 may decode only these 30 source/index pairs:

- ESM1, ESM2, ESM3: indices 0, 73, 146, 219, 293;
- ESM4, ESM5, ESM6: indices 0, 98, 197, 295, 394.

Keep lossless native pilot images and diagnostic binaries in ignored local
derived storage only. No experimental binary may enter the Git index. Preserve
native channels, depth, orientation and source bytes; no extra frame is allowed.

## Authorized TI-2 work

The following classes of change are authorized within TI2-E0–E7:

- root agent instructions;
- local-development and sandbox documentation;
- versioned VS Code settings and explicit tasks;
- repository data-name guardrails;
- tests using text, JSON, mocks, or temporary synthetic paths;
- CI, Makefile, contribution guidance, and PR-template changes required to enforce the bootstrap.
- TI-2 pilot controls, numerical registration/calibration code and tests;
- configuration, contracts, reports, lineage, checksums and gate evidence;
- professional commits and one Draft TI-2 pull request.

Synthetic registration, calibration and image-geometry contract tests are
authorized. Labels, datasets, splits, baselines and models remain prohibited.

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
- no media decoding or pixel access outside the frozen TI-2 pilot;
- no mass extraction, additional frames, native image modification, label
  creation or cumulative-circle differencing;
- no projective/non-rigid registration or retrospective relaxation of limits;
- no labels, event ledger, dataset, temporal split, baseline, CNN, training, evaluation, or sealed-test access;
- no commit, push, merge, force operation, branch switch, reset, clean, or worktree mutation unless the current user instruction explicitly authorizes that exact Git operation.
- no merge of the TI-2 Draft PR without a new author decision.

## Sandbox and approvals

- Default-sandbox repository writes are explicitly authorized by the closure/
  execution decision after the successful real Codex smoke test.
- Read-only `.git` protection is expected. A denial writing `.git/index.lock`
  does not itself indicate a sandbox startup or SDR-2-A failure. Never change
  permissions or bypass that protection.
- For an authorized Git metadata write, request approval for each exact
  `git add -- <explicit reviewed paths>` operation and a separate approval for
  `git commit`. No blanket Git approval, wildcard staging or `git add -A`.
- Request a targeted push approval only after final G2-SPATIAL/G3 decisions
  and passing required tests. Request Draft PR creation separately. These
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
- raw/derived experimental data outside the frozen TI-2 scope might be accessed;
- installation, unapproved network access, or an OS change appears necessary;
- a tracked symlink or forbidden binary/data path is found;
- the worktree contains unexplained changes;
- the requested action could execute TI-3 or any later phase, decode an extra
  frame, or require a projective/non-rigid transformation.

Execution returns with G2-SPATIAL and G3 each PASS, PARTIAL or BLOCKED, or on a
real blocker requiring scope expansion. Gate PASS and TI-2 closure do not
authorize TI-3; formal closure remains the author's decision.
