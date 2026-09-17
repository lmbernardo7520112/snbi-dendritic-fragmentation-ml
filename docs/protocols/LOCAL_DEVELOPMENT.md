# Governed local development protocol

## Status and authority

The local VS Code bootstrap is authorized. TI-2 execution is not authorized. This protocol configures a safe development surface; it does not process scientific data.

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
4. Keep network disabled for agent commands.
5. Use read-only mode for diagnostics.
6. Do not enable workspace-write until a real Codex command starts in the
   sandbox and the author separately approves workspace writes.
7. Never retry a failed sandbox command outside the sandbox.

## Sanitized workspace rule

An agent-writeable workspace must not contain raw videos or derived experimental
files. When experimental sources are introduced for a later authorized phase,
keep them outside the Codex workspace or use a standalone sanitized clone whose
`.git` directory is contained inside the repository root. Linked worktrees are
not permitted. `.gitignore` is not a confidentiality or write barrier.

## Bootstrap workflow

1. Verify remote, branch, HEAD, and clean status.
2. Read the current authorization and `AGENTS.md`.
3. Run `/usr/bin/python3 -B scripts/check_repository_data.py`.
4. Run `/usr/bin/python3 -B scripts/check_local_bootstrap.py`.
5. Run `/usr/bin/python3 -B scripts/check_local_environment.py` in read-only mode.
6. If explicitly requested, `--probe-bwrap` may test bubblewrap capability;
   it does not establish Codex sandbox readiness.
7. Start one harmless read-only command through the real Codex sandbox. If it
   fails, stop; do not retry unsandboxed or remediate the operating system.
8. Run `make bootstrap-tests` only within the authorized sandbox mode. The
   complete legacy suite remains confined to a clean CI checkout.
9. Review the diff and final Git status.

## VS Code tasks

The versioned tasks are explicit `process` tasks. None runs on folder open, installs software, invokes media tools, accesses the network, or performs a mutating Git action.

## Data policy

The repository guard examines only names already present in the Git index. It does not traverse ignored data directories or open experimental files. Forbidden data require explicit future change control before any exception.

## Evidence policy

A bootstrap report may record:

- repository identifier;
- branch and commit;
- clean/dirty status;
- commands and exit codes;
- guard/test outcomes;
- sanitized sandbox diagnostics.

It must not contain username, home directory, hostname, environment variables, credentials, source paths outside the repository, or experimental file metadata.

## Completion criteria

- root agent instructions exist and validate;
- VS Code JSON is valid and contains no automatic task;
- the data guard passes in CI;
- synthetic tests cover traversal, symlinks, case-insensitive suffixes, and prohibited paths;
- local diagnostics execute no mutating command and Git optional locks are disabled;
- all previous deterministic tests remain green;
- readiness for Codex writes remains BLOCKED until the real Codex sandbox works
  and the author makes a separate write-authorization decision.
