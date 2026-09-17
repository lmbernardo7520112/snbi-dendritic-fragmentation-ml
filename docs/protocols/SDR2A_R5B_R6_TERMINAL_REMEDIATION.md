# SDR-2-A — terminal R5B/R6 remediation

## Document status

- Status: DRAFT_PENDING_AUTHOR_APPROVAL
- R5A status: PASS
- Execution released: false
- Execution actor: human operator
- Profile mutation authorized: false
- Codex smoke test authorized: false
- Rollback authorized: false
- Local Codex write authorized: false
- TI2 execution authorized: false
- PR #5 merge authorized: false

This document is the terminal remediation proposal. Do not execute it until the
author explicitly approves this exact version.

## Objective

Activate the verified Ubuntu `bwrap-userns-restrict` profile, verify the
result and perform exactly one read-only Codex sandbox smoke test.

This is not a new diagnostic cycle. It must terminate in one of two states:

~~~text
RESOLVED
BLOCKED_AFTER_OFFICIAL_PROFILE
~~~

No second remediation branch is permitted within SDR-2-A.

## Frozen inputs

~~~text
source: /usr/share/apparmor/extra-profiles/bwrap-userns-restrict
target: /etc/apparmor.d/bwrap-userns-restrict
source_sha256: 11d39094f044f0cda0febb3ad517b830301da6b2ce929664af09ee9e4dd264f9
policies:
  - bwrap
  - unpriv_bwrap
bwrap_executable: /usr/bin/bwrap
apparmor_service: active
kernel.apparmor_restrict_unprivileged_userns: 1
~~~

## Global rules

- Run the terminal blocks manually in the ordinary Ubuntu terminal.
- Review each block's output, but do not request new exploratory commands.
- Do not alter the command text.
- Never disable AppArmor or change the user-namespace sysctl.
- Never use full access, danger-full-access, `--yolo` or a sandbox bypass.
- Do not access credentials or experimental data.
- Do not authorize general Codex execution or writes.
- If a mutation or verification condition fails, do not smoke-test Codex.
  Execute only the approved rollback block.
- If the smoke test fails, execute only the approved rollback block and close
  SDR-2-A as `BLOCKED_AFTER_OFFICIAL_PROFILE`.

## T1 — Immediate fail-closed precondition

~~~bash
profile_source=/usr/share/apparmor/extra-profiles/bwrap-userns-restrict
profile_target=/etc/apparmor.d/bwrap-userns-restrict
expected_sha256=11d39094f044f0cda0febb3ad517b830301da6b2ce929664af09ee9e4dd264f9

actual_sha256=$(sha256sum "$profile_source" | /usr/bin/awk '{print $1}')
printf 'source_sha256=%s\n' "$actual_sha256"

test "$actual_sha256" = "$expected_sha256"
source_hash_rc=$?
printf 'source_hash_rc=%s\n' "$source_hash_rc"

test ! -e "$profile_target"
target_absent_rc=$?
printf 'target_absent_rc=%s\n' "$target_absent_rc"

pgrep -a -x bwrap
bwrap_pgrep_rc=$?
printf 'bwrap_pgrep_rc=%s\n' "$bwrap_pgrep_rc"

sudo test -r /sys/kernel/security/apparmor/profiles
securityfs_readable_rc=$?
printf 'securityfs_readable_rc=%s\n' "$securityfs_readable_rc"

sudo /usr/bin/grep -E '^(bwrap|unpriv_bwrap)(//| )'   /sys/kernel/security/apparmor/profiles
loaded_bwrap_grep_rc=$?
printf 'loaded_bwrap_grep_rc=%s\n' "$loaded_bwrap_grep_rc"
~~~

Required:

~~~text
source_hash_rc=0
target_absent_rc=0
bwrap_pgrep_rc=1
securityfs_readable_rc=0
loaded_bwrap_grep_rc=1
~~~

Any other result blocks T2. Do not modify or remove an unexpected target or
loaded policy.

## T2 — Install the exact verified source

Executable only if every T1 result matches.

~~~bash
sudo /usr/bin/install -m 0644 -o root -g root   "$profile_source"   "$profile_target"

install_rc=$?
printf 'profile_install_rc=%s\n' "$install_rc"
~~~

Required: `profile_install_rc=0`.

Immediately verify before loading:

~~~bash
stat -Lc 'target_type=%F mode=%a owner=%U group=%G' "$profile_target"

sha256sum "$profile_source" "$profile_target"

/usr/bin/cmp -s "$profile_source" "$profile_target"
profile_copy_rc=$?
printf 'profile_copy_rc=%s\n' "$profile_copy_rc"
~~~

Required:

~~~text
target_type: regular file
mode: 644
owner: root
group: root
both hashes: 11d39094f044f0cda0febb3ad517b830301da6b2ce929664af09ee9e4dd264f9
profile_copy_rc=0
~~~

Any mismatch invokes rollback. Do not load.

## T3 — Load only the verified profile

Executable only if T2 verification passes.

~~~bash
sudo /usr/sbin/apparmor_parser -a -K "$profile_target"
profile_load_rc=$?
printf 'profile_load_rc=%s\n' "$profile_load_rc"
~~~

Add mode is intentionally fail-closed: an unexpected policy-name collision
must stop the operation. Do not substitute replace mode.

Required: `profile_load_rc=0`.

## T4 — Post-load verification

~~~bash
systemctl is-active apparmor.service
apparmor_service_rc=$?
printf 'apparmor_service_rc=%s\n' "$apparmor_service_rc"

sysctl -n kernel.apparmor_restrict_unprivileged_userns
apparmor_userns_sysctl_rc=$?
printf 'apparmor_userns_sysctl_rc=%s\n' "$apparmor_userns_sysctl_rc"

sudo /usr/bin/grep -E '^(bwrap|unpriv_bwrap)(//| )'   /sys/kernel/security/apparmor/profiles
loaded_bwrap_grep_rc=$?
printf 'loaded_bwrap_grep_rc=%s\n' "$loaded_bwrap_grep_rc"
~~~

Required:

- AppArmor: `active`, return code 0;
- restriction: `1`, return code 0;
- exactly `bwrap` and `unpriv_bwrap` shown in enforce mode;
- grep return code 0.

Any deviation invokes rollback and blocks R6.

## R6 — Single Codex sandbox smoke test

Only T1 through T4 PASS release this single attempt.

Open the existing Codex interface and paste this exact plain-text prompt:

~~~text
SDR-2-A FINAL SMOKE TEST. Execute exactly one read-only sandboxed command:

/usr/bin/printf 'CODEX_SANDBOX_OK\n'

Do not read or write any file. Do not use network access. Do not execute any
other command. Do not request elevation, full access or a sandbox bypass. If
sandbox startup fails, do not retry and report the exact error only.
~~~

### Terminal result

Exact sandboxed output:

~~~text
CODEX_SANDBOX_OK
~~~

means:

~~~text
SDR2A_STATUS: RESOLVED
REAL_CODEX_SANDBOX: PASS_SMOKE
CODEX_LOCAL_WRITE_READINESS: BLOCKED_PENDING_SEPARATE_DECISION
TI2_EXECUTION_AUTHORIZED: false
~~~

Any error, including the original RTM_NEWADDR error, means:

~~~text
SDR2A_STATUS: BLOCKED_AFTER_OFFICIAL_PROFILE
REAL_CODEX_SANDBOX: BLOCKED
~~~

Do not retry. Execute rollback.

## RB — Conditional rollback

Rollback is released only if:

- T2 created the target; and
- T2, T3, T4 or R6 failed.

First verify that the target still equals the frozen source:

~~~bash
/usr/bin/cmp -s "$profile_source" "$profile_target"
rollback_target_rc=$?
printf 'rollback_target_rc=%s\n' "$rollback_target_rc"
~~~

Required: `rollback_target_rc=0`. A mismatch stops automatic rollback for
manual review.

Remove the policies, then the exact runbook-created file:

~~~bash
sudo /usr/sbin/apparmor_parser -R -K "$profile_target"
profile_unload_rc=$?
printf 'profile_unload_rc=%s\n' "$profile_unload_rc"
~~~

Only when `profile_unload_rc=0`:

~~~bash
sudo /usr/bin/rm -- "$profile_target"
profile_remove_rc=$?
printf 'profile_remove_rc=%s\n' "$profile_remove_rc"
~~~

Verify restoration:

~~~bash
test ! -e "$profile_target"
target_restored_absent_rc=$?
printf 'target_restored_absent_rc=%s\n' "$target_restored_absent_rc"

sudo /usr/bin/grep -E '^(bwrap|unpriv_bwrap)(//| )'   /sys/kernel/security/apparmor/profiles
rollback_loaded_grep_rc=$?
printf 'rollback_loaded_grep_rc=%s\n' "$rollback_loaded_grep_rc"

systemctl is-active apparmor.service
sysctl -n kernel.apparmor_restrict_unprivileged_userns
~~~

Required:

~~~text
target_restored_absent_rc=0
rollback_loaded_grep_rc=1
apparmor_service=active
kernel.apparmor_restrict_unprivileged_userns=1
~~~

The installed Ubuntu packages remain installed. Their removal is outside this
terminal runbook.

## Scope after success

A successful smoke test proves only that the Codex sandbox can initialize and
run the exact read-only command.

It does not authorize:

- local Codex writes;
- general command execution;
- access to scientific data;
- R5B repetition;
- TI-2 or later phases;
- PR #5 readiness or merge.

Any later permission is a separate author decision.
