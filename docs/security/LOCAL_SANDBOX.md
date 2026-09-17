# Local Codex sandbox posture

## Observed state

During the first read-only Codex IDE audit on 17 September 2026, seven sandbox starts failed with a `bwrap ... Operation not permitted` error. The user approved a read-only fallback outside the sandbox; no repository changes occurred.

This is sufficient to validate repository comprehension, but it is not sufficient to authorize agent writes.

## Current decision

- documentation/static bootstrap: allowed;
- read-only diagnostic collection: allowed with user approval;
- Codex local write readiness: **BLOCKED**;
- unsandboxed fallback: prohibited;
- OS remediation: not authorized.

## Diagnostic boundary

The repository diagnostic may inspect only:

- tool presence and version for `git`, `bwrap`, `unshare`, and `code`;
- Python and operating-system version identifiers;
- exact read-only proc/sys keys relevant to user namespaces;
- one inert bubblewrap capability probe only when the user explicitly supplies
  `--probe-bwrap`.

Repository identity, branch, commit, and status are verified separately by
explicit human-reviewed Git commands; the diagnostic does not inherit or emit
Git repository state.

The capability probe does not exercise the complete Codex sandbox or its
seccomp policy. It therefore cannot change Codex write readiness by itself.

It must not enumerate the home directory, list environment variables, inspect credentials, traverse experimental data, or change system state.

## Read-only keys

- `/proc/sys/kernel/unprivileged_userns_clone`;
- `/proc/sys/user/max_user_namespaces`;
- `/proc/sys/kernel/apparmor_restrict_unprivileged_userns`, when present.

## Decision rule

| Observation | Result |
|---|---|
| inert `bwrap` capability probe returns zero | `PASS` for bubblewrap capability only; Codex writes remain `BLOCKED` |
| `bwrap` absent | `BLOCKED` |
| namespace/AppArmor denial | `BLOCKED` |
| probe requires privilege or OS change | `BLOCKED` |
| diagnostic attempts unsandboxed fallback | `BLOCKED` |

No repository result changes kernel, AppArmor, namespace, package, or extension
configuration. Write readiness requires both a successful real Codex sandbox
command and a separate author decision. Remediation requires separate
authorization after review of sanitized diagnostics.
