# Governed local development protocol

## Status and authority

LB0 is PASS and SDR-2-A is RESOLVED. The current
[TI2-CLOSEOUT-1 decision](../decisions/AUTHORIZATION-TI2-CLOSEOUT-1-2026-09-17.md)
permits only documentary reconciliation, deterministic tests, an approved
checkpoint, push, a Draft PR and remote CI verification. Ordinary writes remain
inside the repository and default sandbox on `feat/ti2-registration-calibration`.
The scientific state is `TERMINAL_BLOCKED_PENDING_CLOSEOUT`: method v1 has
`INSUFFICIENT_EVIDENCE`, G2-SPATIAL is `BLOCKED_METHOD_V1`, transformation
existence is `UNDETERMINED`, G3 is `BLOCKED_DEPENDENCY_G2`, and E7 is
`PASS_DOCUMENTARY`. TI-2R and TI-3 through TI-8 are not authorized.
The historical resumption snapshot records
`TI2_EXECUTION_STATUS=RESUMED_AFTER_OPERATIONAL_BLOCK`; G2-SPATIAL and G3 were
`NOT_EVALUATED` at resumption, independently of operational readiness.

## Architecture

- GitHub is the canonical repository and review boundary.
- VS Code is the local editor and test surface.
- Codex may operate only under root `AGENTS.md` instructions.
- Experimental sources remain external, immutable, and absent from an agent-writeable workspace.
- Pull requests and explicit author decisions control every phase transition.

## Required local posture

1. Use the stable official Codex extension.
2. Open only the repository root as the workspace.
3. Keep approvals user-controlled.
4. Keep network disabled except for an exact approved Git/GitHub operation.
5. Do not reopen sandbox/AppArmor diagnostics or remediation.
6. Keep ordinary writes inside the standalone repository and default sandbox;
   use individual Git approvals only as specified below.
7. Never retry a failed sandbox command outside the sandbox.

## Sanitized workspace rule

Experimental source files remain external and immutable. Closeout permits no
pixel access, source-member reads or decoding. Exact existing files may be
hashed as opaque bytes only when needed for integrity. The historical 30 pilot
frames were decoded from MP4 without additional losses, preserving video
resolution and pixel format; existing derivatives remain ignored. `.raw` files
are headerless decoded pixel buffers, not raw detector data. No further frames,
datasets or experimental binaries may enter Git. The standalone `.git` directory must
remain inside the repository root; linked worktrees are prohibited.
`.gitignore` is not a confidentiality or write barrier. The original sanitization
claim is the author's attestation; the Git-index guard is not a scan of ignored
content, and the later authorized pilot does not invalidate that historical
attestation.

## Authorized local workflow

1. Confirm the exact repository/branch, a clean initial worktree, no index lock,
   all three required commits and zero tracked experimental binaries. Record
   `TI2_EXECUTION_RESULT_COMMIT=f3c6da78b04299475c7bb85e986eb7435b08bd22`.
2. Read the current authorization and `AGENTS.md`.
3. Run `/usr/bin/python3 -B scripts/check_repository_data.py`.
4. Run `/usr/bin/python3 -B scripts/check_local_bootstrap.py`.
5. Run `/usr/bin/python3 -B scripts/check_ti2_scope.py`.
6. Use only explicit tasks and tests for the approved increment; no environment
   diagnostic, optional bwrap probe or repeated sandbox acceptance is required.
7. Run local tests in the default sandbox, with fresh synthetic temporary
   subtrees only inside `.bootstrap-test-tmp/` when needed. Core contracts and CI
   use the standard library. Existing optional synthetic tests may use already
   installed packages; no scientific execution or installation is authorized.
8. Run the complete regression suite in a clean CI checkout. The explicit
   resumption authority also permits the full synthetic suite locally with
   `TMPDIR` inside `.bootstrap-test-tmp/`; no experimental bytes or media
   decoding may enter the legacy tests.
9. Report exact discovered/run, passed, skipped, failure and error counts;
   retain historical logs. Review the full scoped diff and status before each
   Git approval. A required source/scientific change stops the task with
   `SOURCE_OR_SCIENTIFIC_CHANGE_REQUIRED`.

## Targeted Git approvals

The standard sandbox may expose `.git` read-only. A write denial for
`.git/index.lock` alone is an operational Git restriction, not a new SDR-2-A
failure. Do not alter filesystem permissions, hooks, operating-system policy or
sandbox configuration to resolve it.

- Review the exact files, then request approval for the individual
  `git add -- <explicit paths>` operation; no wildcard or all-files staging.
- Request a separate approval for the concrete `git commit` operation.
- Closeout explicitly permits publication of the blocked scientific result.
  Require documentary reconciliation, zero test failures/errors, passing guards
  and checksums, and zero tracked experimental binaries. Approve a read-only
  remote-reference check, establish a fast-forward push and approve that exact
  push separately. Request Draft PR creation separately, then verify remote CI
  to completion; never claim a run passed while it is pending.
- Never infer authority for a force operation, credential inspection, broad
  network access, another branch or merging the TI-2 PR.

These per-action approvals are the sole exception to the default-sandbox Git
metadata write restriction. Ordinary documentary development stays inside the
default sandbox; no new scientific execution is authorized. A real bwrap/namespace/seccomp startup failure still
requires an immediate stop without fallback.

## VS Code tasks

The versioned tasks are explicit `process` tasks. None runs on folder open, installs software, invokes media tools, accesses the network, or performs a mutating Git action.

## Data policy

The repository guard examines only names already present in the Git index. It
does not traverse ignored data directories or open experimental files. Its ban
on tracked experimental data and binaries remains unchanged. The approved
pilot exception applies only to ignored local derived storage.

## Evidence policy

A bootstrap report may record:

- repository identifier;
- branch and commit;
- clean/dirty status;
- commands and exit codes;
- guard/test outcomes;
- sanitized sandbox diagnostics.

Do not publish usernames, home directories, hostnames, environment variables,
credentials or external source paths. Bootstrap evidence contains no
experimental metadata. TI-2 evidence may contain the expressly authorized
source IDs, hashes, dimensions, frozen indices, explicitly distinguished elapsed
and experimental times, documented nominal scale, uncertainty and lineage,
using logical source identifiers instead of personal filesystem paths.

## Completion criteria

- root agent instructions exist and validate;
- VS Code JSON is valid and contains no automatic task;
- the data guard passes in CI;
- synthetic tests cover traversal, symlinks, case-insensitive suffixes, and prohibited paths;
- historical local diagnostics remain read-only and Git optional locks are disabled;
- deterministic tests have zero failures/errors, with pass/skip counts and skip
  reasons reported separately;
- Codex write readiness is `AUTHORIZED_DEFAULT_SANDBOX_REPOSITORY_ONLY` on the
  basis of the successful smoke test and separate execution decision;
- the closeout PASS additionally requires its commit, completed push, open Draft
  PR, completed green remote CI, clean worktree and zero tracked experimental
  binaries; targeted approvals do not change the scientific gates or authorize
  TI-2R/TI-3+.
