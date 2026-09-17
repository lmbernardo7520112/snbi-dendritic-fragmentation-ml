# Local Codex sandbox posture

## Historical startup failure

Earlier read-only Codex IDE audits produced generic `bwrap ... Operation not
permitted` startup failures. On 17 September 2026, the author performed the
governed real-sandbox acceptance test against the approved bootstrap branch.
The sandbox failed before the requested Python diagnostic started:

```text
bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted
```

The command was stopped without fallback, elevation, network access or host
modification. This established a historical startup failure; it did not
identify the root cause by itself. SDR-2-A subsequently closed after the real
Codex smoke test returned exactly `CODEX_SANDBOX_OK`. The author formally
approved LB0 PASS and SDR-2-A RESOLVED in the
[closure/execution decision](../decisions/AUTHORIZATION-LB0-SDR2A-CLOSURE-PR5-MERGE-TI2-EXECUTION-2026-09-17.md).

One earlier audit used an author-approved read-only fallback outside the
sandbox and produced no repository change. That historical exception is not
current authority and must not be repeated.

## Current decision

- LB0 static/documental conformance: `PASS`;
- workspace sanitization: `CONFIRMED_BY_AUTHOR`;
- LB0 local acceptance: `PASS`;
- real Codex sandbox: `PASS_SMOKE`;
- SDR-2-A: `RESOLVED`;
- Codex local write readiness: `AUTHORIZED_DEFAULT_SANDBOX_REPOSITORY_ONLY`;
- TI-2 execution: `AUTHORIZED_E0_E7_FROZEN_30_IMAGE_PILOT`;
- unsandboxed fallback: prohibited;
- operating-system remediation: not authorized.

## Historical read-only facts

The approved manual preflight established, without changing the host:

- Linux kernel identifier `6.17.0-1032-oem`;
- Python `3.12.3`, supported by the repository bootstrap;
- `bwrap` present at version `0.9.0`;
- `git` and `unshare` present;
- the `code` launcher not found on the terminal `PATH`;
- unprivileged user namespaces enabled and the configured namespace maximum
  greater than zero;
- `kernel.apparmor_restrict_unprivileged_userns=1`;
- no inert `bwrap` probe executed.

These facts are diagnostic inputs. In particular, AppArmor restriction is a
relevant observation but is not accepted as the cause without direct evidence.
The missing `code` launcher does not prove that no compatible editor exists.

## Closed diagnostic boundary

`docs/protocols/LOCAL_SANDBOX_DIAGNOSTIC_PROTOCOL.md` is retained as historical
evidence. No further sandbox, namespace or AppArmor diagnosis/remediation is
authorized or required for TI-2. Neither the historical protocol nor the
presence of diagnostic scripts or editor tasks authorizes another run.

The historical manual protocol allowed only:

- editor product and official extension identity through the GUI;
- categorical presence and non-secret versions of exact editor/package names;
- operating-system release identifiers;
- the exact AppArmor/profile-presence and namespace indicators listed by the
  protocol;
- filtered, sanitized kernel-denial lines relevant to `bwrap`, AppArmor,
  user namespaces or `RTM_NEWADDR`.

It must not enumerate the home directory, list environment variables, inspect
credentials, traverse experimental data, access the network, use privilege
elevation or change system state.

## Historical diagnostic decision rule

| Observation | Result |
|---|---|
| manual evidence collected within the exact allowlist | `COLLECTED` for diagnosis only |
| editor host or packaging cannot be identified read-only | `PARTIAL` |
| relevant log access is denied | record `BLOCKED_NO_PRIVILEGE`; do not elevate |
| direct sanitized denial identifies `bwrap` and a policy rule | `CONFIRMED`, pending review |
| configuration and error correlation only | `SUPPORTED_HYPOTHESIS` |
| evidence remains ambiguous | `UNRESOLVED` |
| any step requires privilege, installation or host change | `BLOCKED` |

No diagnostic outcome authorizes remediation. The successful real Codex smoke
test and the separate author decision now establish bounded write readiness.

## Git metadata protection and resumption

Read-only `.git` protection is expected under the standard sandbox. The observed
`.git/index.lock: Read-only file system` error stopped Git staging; it did not
establish a bwrap/namespace/seccomp startup failure or reopen SDR-2-A.

The [targeted Git approval decision](../decisions/AUTHORIZATION-TI2-TARGETED-GIT-APPROVALS-2026-09-17.md)
permits separate approvals for exact-path staging and commits. Push is subject
to final gate decisions and passing tests; Draft PR creation is approved as a
separate action. These exceptions cover only the individually approved
Git/GitHub actions. They do not authorize scientific work outside the sandbox,
full access, broad escalation, credential inspection, permission changes or OS
remediation. TI-2 PR merge still requires a new author decision.

If sandbox startup itself fails again with bwrap, namespace or seccomp errors,
stop immediately; no unsandboxed fallback is authorized.
