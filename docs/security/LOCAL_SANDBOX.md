# Local Codex sandbox posture

## Observed state

Earlier read-only Codex IDE audits produced generic `bwrap ... Operation not
permitted` startup failures. On 17 September 2026, the author performed the
governed real-sandbox acceptance test against the approved bootstrap branch.
The sandbox failed before the requested Python diagnostic started:

```text
bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted
```

The command was stopped without fallback, elevation, network access or host
modification. This proves that the real sandbox is not currently operational;
it does not identify the root cause by itself.

One earlier audit used an author-approved read-only fallback outside the
sandbox and produced no repository change. That historical exception is not
current authority and must not be repeated.

## Current decision

- LB0 static/documental conformance: `PASS`;
- workspace sanitization: `CONFIRMED_BY_AUTHOR`;
- LB0 local acceptance: `PARTIAL`;
- real Codex sandbox: `BLOCKED`;
- Codex local write readiness: `BLOCKED`;
- TI-2 execution: `NOT_AUTHORIZED`;
- unsandboxed fallback: prohibited;
- operating-system remediation: not authorized.

## Established read-only facts

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

## Diagnostic boundary

The next collection is governed by
`docs/protocols/LOCAL_SANDBOX_DIAGNOSTIC_PROTOCOL.md` and must be performed
manually by the author. It does not expand the command allowance for the local
Codex agent. The agent remains prohibited from executing commands while its
sandbox is blocked.

The manual protocol may inspect only:

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

## Decision rule

| Observation | Result |
|---|---|
| manual evidence collected within the exact allowlist | `COLLECTED` for diagnosis only |
| editor host or packaging cannot be identified read-only | `PARTIAL` |
| relevant log access is denied | record `BLOCKED_NO_PRIVILEGE`; do not elevate |
| direct sanitized denial identifies `bwrap` and a policy rule | `CONFIRMED`, pending review |
| configuration and error correlation only | `SUPPORTED_HYPOTHESIS` |
| evidence remains ambiguous | `UNRESOLVED` |
| any step requires privilege, installation or host change | `BLOCKED` |

No diagnostic outcome authorizes remediation. Write readiness requires a
successful real Codex sandbox command and a separate author decision after
review of the evidence.
