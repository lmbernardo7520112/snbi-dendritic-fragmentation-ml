# Governed local development protocol

## Status and authority

LB0 is PASS and SDR-2-A is RESOLVED. The author authorized TI-2 E0–E7 and
repository-only writes in the default sandbox on
`feat/ti2-registration-calibration`. The governing records are the
[execution decision](../decisions/AUTHORIZATION-LB0-SDR2A-CLOSURE-PR5-MERGE-TI2-EXECUTION-2026-09-17.md)
and [targeted Git approval decision](../decisions/AUTHORIZATION-TI2-TARGETED-GIT-APPROVALS-2026-09-17.md).
TI-3 through TI-8 remain blocked. The resumption snapshot records
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

Raw experimental sources remain external and immutable; only the exact
operator-declared source may be read. The authorized TI-2 exception permits
the 30 frozen lossless pilot images and their diagnostic derivatives in ignored
local derived storage. It does not permit raw videos in the workspace, additional
pilot frames, datasets or binaries in Git. The standalone `.git` directory must
remain inside the repository root; linked worktrees are prohibited.
`.gitignore` is not a confidentiality or write barrier. The original sanitization
claim is the author's attestation; the Git-index guard is not a scan of ignored
content, and the later authorized pilot does not invalidate that historical
attestation.

## Authorized local workflow

1. Verify repository, branch, HEAD and status. At an authorized resumption,
   reconcile preserved partial changes with the recorded task before editing.
2. Read the current authorization and `AGENTS.md`.
3. Run `/usr/bin/python3 -B scripts/check_repository_data.py`.
4. Run `/usr/bin/python3 -B scripts/check_local_bootstrap.py`.
5. Run `/usr/bin/python3 -B scripts/check_ti2_scope.py`.
6. Use only explicit tasks and tests for the approved increment; no environment
   diagnostic, optional bwrap probe or repeated sandbox acceptance is required.
7. Run local tests in the default sandbox, with fresh synthetic temporary
   subtrees only inside `.bootstrap-test-tmp/` when needed. Core contracts and CI
   use the standard library; optional experimental runtime tools must already
   exist and their versions must be recorded, without installation.
8. Run the complete regression suite in a clean CI checkout. The explicit
   resumption authority also permits the full synthetic suite locally with
   `TMPDIR` inside `.bootstrap-test-tmp/`; no experimental bytes or media
   decoding may enter the legacy tests.
9. Review the scoped diff and final status before each exact Git approval.

## Targeted Git approvals

The standard sandbox may expose `.git` read-only. A write denial for
`.git/index.lock` alone is an operational Git restriction, not a new SDR-2-A
failure. Do not alter filesystem permissions, hooks, operating-system policy or
sandbox configuration to resolve it.

- Review the exact files, then request approval for the individual
  `git add -- <explicit paths>` operation; no wildcard or all-files staging.
- Request a separate approval for the concrete `git commit` operation.
- Request push approval only after final G2-SPATIAL/G3 decisions and passing
  required tests. Request Draft PR creation separately.
- Never infer authority for a force operation, credential inspection, broad
  network access, another branch or merging the TI-2 PR.

These per-action approvals are the sole exception to the default-sandbox Git
metadata write restriction. Ordinary development and scientific execution stay
inside the default sandbox. A real bwrap/namespace/seccomp startup failure still
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
source IDs, hashes, dimensions, frozen indices, physical times and lineage,
using logical source identifiers instead of personal filesystem paths.

## Completion criteria

- root agent instructions exist and validate;
- VS Code JSON is valid and contains no automatic task;
- the data guard passes in CI;
- synthetic tests cover traversal, symlinks, case-insensitive suffixes, and prohibited paths;
- historical local diagnostics remain read-only and Git optional locks are disabled;
- all previous deterministic tests remain green;
- Codex write readiness is `AUTHORIZED_DEFAULT_SANDBOX_REPOSITORY_ONLY` on the
  basis of the successful smoke test and separate execution decision;
- targeted Git approvals do not change scientific gates or authorize TI-3+.
