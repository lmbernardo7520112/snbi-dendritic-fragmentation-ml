# Manual read-only protocol for local Codex sandbox diagnosis

## Purpose and authority

This protocol collects the minimum sanitized evidence needed to distinguish an
editor/packaging constraint from an AppArmor, namespace or other host-policy
constraint associated with:

```text
bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted
```

It is a diagnostic protocol, not a remediation procedure. The author is the
only operator. The local Codex agent must not execute any command while its
sandbox remains blocked.

## Invariants

- manual human execution only;
- read-only commands only;
- no network access;
- no `sudo`, `su`, `doas` or approval elevation;
- no package, editor, service, kernel, namespace, AppArmor or file changes;
- no environment-variable listing, home-directory traversal or credential
  access;
- no experimental or derived scientific-data access;
- no `bwrap` capability probe and no repeated Codex sandbox attempt;
- no raw log publication: share only the filtered and redacted output defined
  below.

If an exact command is unavailable, record `NOT_AVAILABLE`. If access is
denied, record `BLOCKED_NO_PRIVILEGE`. Do not install, elevate or substitute a
broader command.

## Stage A — GUI identification

With the editor already open, collect manually:

1. **Help → About:** product name, product version, build/commit when shown,
   architecture and operating-system label;
2. **Extensions:** extension identifier, publisher, installed version and
   stable/pre-release channel for the OpenAI Codex extension;
3. **Output/Logs → Codex:** only the exact sandbox failure line and its local
   timestamp. Do not export or share the complete log.

Redact username, hostname, home paths, repository paths, session identifiers,
tokens and account information. A screenshot is optional; sanitized text is
preferred.

## Stage B — Repository preflight

Run from the standalone sanitized repository root:

```bash
git --no-optional-locks status --porcelain=v1 | /usr/bin/wc -l
git branch --show-current
git --no-optional-locks rev-parse --short HEAD
test -d .git && test ! -L .git && echo STANDALONE_OK || echo BLOCKED
```

The first output must be `0`. Stop if it is not zero; do not list filenames.
Do not run `reset`, `clean`,
`checkout`, `switch`, `pull` or any other mutating Git command in this stage.

## Stage C — Release, editor and local packaging

Run exactly:

```bash
/usr/bin/grep -E '^(ID|NAME|VERSION_ID|VERSION)=' /etc/os-release
uname -sr
uname -m
systemd-detect-virt 2>/dev/null || echo 'virtualization=NONE_OR_UNAVAILABLE'

if test -r /proc/self/attr/current; then
  printf 'operator_shell_security_profile='
  /usr/bin/cat /proc/self/attr/current
else
  echo 'operator_shell_security_profile=NOT_READABLE'
fi

for name in code code-insiders codium antigravity snap flatpak; do
  if command -v "$name" >/dev/null 2>&1; then
    printf '%s=PRESENT\n' "$name"
  else
    printf '%s=NOT_AVAILABLE\n' "$name"
  fi
done

ps -eo comm= | /usr/bin/grep -E '^(code|code-insiders|codium|antigravity)$' \
  | /usr/bin/sort -u || true
```

If `dpkg-query` is present, run this exact local-package query:

```bash
dpkg-query -W -f='${binary:Package}=${Version}\n' \
  bubblewrap apparmor apparmor-utils apparmor-profiles \
  code code-insiders codium 2>/dev/null || true
```

If `snap` is present, query only these exact local package names:

```bash
for package in code codium antigravity; do
  snap list "$package" 2>/dev/null || printf '%s=NOT_LISTED_BY_SNAP\n' "$package"
done
```

If `flatpak` is present, query only these exact application identifiers:

```bash
for app in com.visualstudio.code com.visualstudio.code-insiders com.vscodium.codium; do
  if flatpak info "$app" >/dev/null 2>&1; then
    printf '%s=INSTALLED:' "$app"
    flatpak info --show-version "$app"
  else
    printf '%s=NOT_LISTED_BY_FLATPAK\n' "$app"
  fi
done
```

These queries inspect only local package databases. Do not run refresh, update,
search, install or any network-enabled package command.

## Stage D — Bubblewrap and AppArmor posture

Run exactly:

```bash
bwrap --version
unshare --version | /usr/bin/head -n 1

if test -e /usr/bin/bwrap; then
  dpkg-query -S /usr/bin/bwrap 2>/dev/null || echo 'bwrap_package_owner=UNRESOLVED'
  stat -Lc 'bwrap_mode=%a owner_uid=%u owner_gid=%g' /usr/bin/bwrap
  if command -v getcap >/dev/null 2>&1; then
    getcap /usr/bin/bwrap || true
  else
    echo 'getcap=NOT_AVAILABLE'
  fi
else
  echo 'system_bwrap=NOT_AVAILABLE'
fi

if test -r /sys/module/apparmor/parameters/enabled; then
  printf 'apparmor_module='
  /usr/bin/cat /sys/module/apparmor/parameters/enabled
else
  echo 'apparmor_module=NOT_READABLE'
fi

for key in \
  kernel.unprivileged_userns_clone \
  user.max_user_namespaces \
  kernel.apparmor_restrict_unprivileged_userns; do
  value=$(sysctl -n "$key" 2>/dev/null) || value=NOT_AVAILABLE
  printf '%s=%s\n' "$key" "$value"
done

test -r /etc/apparmor.d/bwrap-userns-restrict \
  && echo 'apparmor_active_profile_file=PRESENT' \
  || echo 'apparmor_active_profile_file=ABSENT_OR_UNREADABLE'

test -r /usr/share/apparmor/extra-profiles/bwrap-userns-restrict \
  && echo 'apparmor_extra_profile_file=PRESENT' \
  || echo 'apparmor_extra_profile_file=ABSENT_OR_UNREADABLE'

systemctl is-active apparmor.service 2>/dev/null \
  || echo 'apparmor_service=UNKNOWN_OR_INACTIVE'

/usr/bin/grep -E \
  '^(NoNewPrivs|Seccomp|Seccomp_filters|CapInh|CapPrm|CapEff|CapBnd|CapAmb):' \
  /proc/self/status

if command -v aa-status >/dev/null 2>&1; then
  aa-status 2>/dev/null | /usr/bin/grep -Ei 'bwrap|userns' \
    || echo 'bwrap_loaded_profile=NO_MATCH_OR_DENIED'
else
  echo 'aa_status=NOT_AVAILABLE'
fi
```

Do not run `apparmor_parser`, `aa-enforce`, `aa-complain`, `systemctl reload`,
`sysctl -w` or any command that changes the observed posture.

## Stage E — Filtered denial evidence

Use the timestamp collected from the Codex GUI to define a maximum window of
five minutes before and five minutes after the failure. Replace the two
placeholders below with that local interval. If the timestamp is unavailable,
record `failure_window=NOT_VERIFIED` and do not query the whole boot.

Run without `sudo`:

```bash
if journalctl -k -b -o cat --no-pager \
  --since '<START_LOCAL>' --until '<END_LOCAL>' >/dev/null 2>&1; then
  journalctl -k -b -o cat --no-pager \
    --since '<START_LOCAL>' --until '<END_LOCAL>' \
    | /usr/bin/grep -Ei \
      'apparmor|audit|denied|bwrap|userns|netlink|RTM_NEWADDR|cap_net_admin' \
    | /usr/bin/tail -n 80 \
    | /usr/bin/sed -E \
      -e 's#(/home/)[^/[:space:]"]+#\1<USER>#g' \
      -e 's#/run/user/[0-9]+[^/[:space:]"]*#<USER_RUNTIME_PATH>#g' \
      -e 's#(auid|uid|gid|pid|ppid|ses)=[0-9]+#\1=<REDACTED>#g'
else
  echo 'kernel_log=BLOCKED_NO_PRIVILEGE'
fi
```

If journal access is denied, record `kernel_log=BLOCKED_NO_PRIVILEGE` and stop
this stage. Do not retry with privilege and do not substitute an unrestricted
log dump. If no line is returned, record `kernel_log=NO_MATCHING_LINE`.

## Stage F — Sanitized evidence record

Return only this schema, populated from the stages above:

```text
diagnostic_status: COLLECTED | PARTIAL | BLOCKED
repository_status: CLEAN | BLOCKED
standalone_checkout: YES | NO
editor_product: <sanitized product name or UNRESOLVED>
editor_version: <version or UNRESOLVED>
editor_commit: <commit or UNRESOLVED>
codex_extension_id: <identifier or UNRESOLVED>
codex_extension_version: <version or UNRESOLVED>
codex_extension_channel: STABLE | PRE_RELEASE | UNRESOLVED
editor_packaging: DEB | SNAP | FLATPAK | APPIMAGE | OTHER | UNRESOLVED
os_id: <identifier>
os_version: <version>
kernel: <release>
architecture: <architecture>
virtualization: <value or UNRESOLVED>
bwrap_version: <version>
bwrap_package_owner: <package or UNRESOLVED>
apparmor_module: ENABLED | DISABLED | UNRESOLVED
apparmor_userns_restriction: 0 | 1 | UNRESOLVED
bwrap_profile_file: PRESENT | ABSENT_OR_UNREADABLE
loaded_profile_evidence: EVIDENCE_FOUND | NO_MATCH_OR_DENIED | UNRESOLVED
operator_shell_security_profile: <sanitized profile or UNRESOLVED>
seccomp_mode: <value or UNRESOLVED>
failure_window: <bounded local interval or NOT_VERIFIED>
kernel_log: EVIDENCE_FOUND | NO_MATCHING_LINE | BLOCKED_NO_PRIVILEGE
failure_signature: bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted
cause_attribution: CONFIRMED | SUPPORTED_HYPOTHESIS | UNRESOLVED
mutating_commands_executed: 0
network_used: false
privilege_elevation_used: false
codex_local_write_readiness: BLOCKED
ti2_execution_authorized: false
```

Do not paste raw outputs when the schema is sufficient. Attach at most the
specific redacted denial lines needed to support `CONFIRMED` attribution.

## Stage G — Final repository integrity

Repeat from the repository root:

```bash
git --no-optional-locks status --porcelain=v1 | /usr/bin/wc -l
git --no-optional-locks rev-parse --short HEAD
```

The first output must remain `0`, and the commit must match Stage B. Otherwise
set `diagnostic_status=BLOCKED` and stop.

## Completion and stop rules

- `COLLECTED` means the allowlisted evidence was obtained; it is not a sandbox
  PASS and does not authorize remediation.
- `PARTIAL` means at least one evidence source was unavailable without
  privilege; preserve the unavailable state.
- `BLOCKED` means an invariant would have to be violated to continue.
- `CONFIRMED` requires a temporally compatible, sanitized policy-denial line
  that identifies `bwrap` and the denied operation or rule.
- `apparmor_restrict_unprivileged_userns=1` combined only with `EPERM` supports
  at most `SUPPORTED_HYPOTHESIS`.
- absence of a matching log does not prove AppArmor was uninvolved.
- a profile present on disk does not prove that it is loaded or sufficient.
- `REAL_CODEX_SANDBOX`, local Codex writes and TI-2 remain blocked regardless
  of the diagnostic result.
- Any proposed remediation requires a new, explicit author decision after the
  Draft PR and evidence have been reviewed.
