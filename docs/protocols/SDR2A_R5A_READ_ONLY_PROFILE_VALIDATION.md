# SDR-2-A — R5A read-only profile validation

## Document status

- Status: DRAFT_PENDING_AUTHOR_APPROVAL
- R4 technical assessment: PASS
- R4 formal closure: pending author decision
- R5A execution released: false
- Execution actor: human operator only
- System mutation authorized by this document: none
- R5B profile installation or load authorized: false
- Codex smoke test authorized: false
- TI2 execution authorized: false

Do not execute any command in this protocol until the author explicitly
authorizes this exact R5A gate.

## Purpose

R5A separates static validation of the official packaged profile from the
later, mutating installation and load operation. It is intended to establish,
without changing the host, that:

1. the source remains owned by the approved Ubuntu package and retains the
   recorded identity;
2. the active target, staging path and local overrides are absent;
3. the bwrap executable resolves to the expected distribution binary;
4. no bwrap process or relevant AppArmor policy is active;
5. the profile declares only the expected policy names;
6. AppArmor's parser accepts the source without loading policy into the kernel
   or reading or writing its cache;
7. AppArmor, the global user-namespace restriction and the repository remain
   unchanged after validation.

## Non-mutation guarantee

The only AppArmor parser modes eligible in R5A are:

- `-N -K`: print declared policy names without loading policy and without
  cache use;
- `-Q -K`: parse while explicitly skipping kernel load and cache use.

The following remain prohibited:

- `-a`, `-r`, `-R`, `-W`, `-C` or any other parser mode;
- `sudo` for either parser invocation;
- copying, creating, replacing, deleting or changing a file under
  `/etc/apparmor.d`;
- starting or killing bwrap;
- reloading AppArmor or changing a sysctl;
- starting the Codex smoke test;
- network access, package operations, rollback or TI-2.

If an exact command fails, stop. Do not retry with sudo or an alternative
option.

## Global stop rules

Stop R5A and return the sanitized output if:

- a package, version, owner, file type, mode, owner, group or hash differs from
  the recorded R4 evidence;
- the active target, reserved staging path or a local override exists;
- bwrap resolves outside `/usr/bin/bwrap` or is not owned by the Ubuntu
  `bubblewrap` package;
- a bwrap process or relevant loaded policy is present;
- a securityfs readability check fails;
- a policy-state grep returns a code other than 1;
- policy-name listing returns an unexpected name;
- parser validation prints a warning/error or returns nonzero;
- AppArmor is inactive or the restriction is not 1;
- the repository is dirty or no longer at the recorded commit;
- any command requests an unapproved privilege, write, network operation or
  scope expansion.

## R5A.1 — Re-anchor package and source identity

Run from the sanitized standalone repository root:

~~~bash
dpkg-query -W   -f='${binary:Package}\t${db:Status-Status}\t${Version}\n'   apparmor-profiles bubblewrap 2>/dev/null

dpkg-query -S   /usr/share/apparmor/extra-profiles/bwrap-userns-restrict

stat -Lc 'source_type=%F mode=%a owner=%U group=%G'   /usr/share/apparmor/extra-profiles/bwrap-userns-restrict

sha256sum   /usr/share/apparmor/extra-profiles/bwrap-userns-restrict

dpkg --verify apparmor-profiles bubblewrap
~~~

Required source result:

~~~text
package_owner: apparmor-profiles
source_type: regular file
mode: 644
owner: root
group: root
sha256: 11d39094f044f0cda0febb3ad517b830301da6b2ce929664af09ee9e4dd264f9
dpkg_verify_output: empty
~~~

Any divergence stops the gate.

## R5A.2 — Exclude active target, staging and local overrides

~~~bash
for path in   /etc/apparmor.d/bwrap-userns-restrict   /etc/apparmor.d/.bwrap-userns-restrict.sdr2a   /etc/apparmor.d/local/bwrap-userns-restrict   /etc/apparmor.d/local/unpriv_bwrap; do
  if test -e "$path"; then
    printf '%s=PRESENT_STOP\n' "$path"
  else
    printf '%s=ABSENT_EXPECTED\n' "$path"
  fi
done
~~~

All four paths must report `ABSENT_EXPECTED`. R5A neither creates nor removes
them.

## R5A.3 — Resolve the executable identity

~~~bash
command -v bwrap
readlink -e "$(command -v bwrap)"
dpkg-query -S /usr/bin/bwrap
stat -Lc 'bwrap_type=%F mode=%a owner=%U group=%G' /usr/bin/bwrap
~~~

Required:

- command and canonical path: `/usr/bin/bwrap`;
- package owner: `bubblewrap`;
- regular root-owned executable.

Any alternative installation or wrapper stops the gate.

## R5A.4 — Inspect the static policy source

~~~bash
nl -ba   /usr/share/apparmor/extra-profiles/bwrap-userns-restrict
~~~

This prints only the distribution-provided policy source. Record the output
for review. Do not edit the file. Any unexpected local path, executable target,
policy name or external include stops the gate pending review.

## R5A.5 — Establish process and loaded-policy absence unambiguously

~~~bash
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
bwrap_pgrep_rc=1
securityfs_readable_rc=0
loaded_bwrap_grep_rc=1
~~~

For `pgrep` and `grep`, code 1 means no match. Code 0 means a process or
policy is present. Code 2 or greater means an error. Both cases stop R5A.

The two sudo operations are targeted read-only inspections. No password or
authentication output may be recorded.

## R5A.6 — List policy names without kernel load

Run without sudo:

~~~bash
/usr/sbin/apparmor_parser -N -K   /usr/share/apparmor/extra-profiles/bwrap-userns-restrict
policy_names_rc=$?
printf 'policy_names_rc=%s\n' "$policy_names_rc"
~~~

Required:

- return code 0;
- only the expected bwrap-related policy names;
- no warning or error.

Record every printed policy name. An additional or different name stops the
gate for review.

## R5A.7 — Parse without kernel load or cache use

Run without sudo:

~~~bash
/usr/sbin/apparmor_parser -Q -K   /usr/share/apparmor/extra-profiles/bwrap-userns-restrict
parser_dry_run_rc=$?
printf 'parser_dry_run_rc=%s\n' "$parser_dry_run_rc"
~~~

Required:

~~~text
parser_dry_run_rc=0
~~~

Any warning, error, privilege request or nonzero code stops the gate. Do not
retry with sudo.

## R5A.8 — Verify unchanged post-state

~~~bash
pgrep -a -x bwrap
bwrap_pgrep_post_rc=$?
printf 'bwrap_pgrep_post_rc=%s\n' "$bwrap_pgrep_post_rc"

sudo test -r /sys/kernel/security/apparmor/profiles
securityfs_post_readable_rc=$?
printf 'securityfs_post_readable_rc=%s\n' "$securityfs_post_readable_rc"

sudo /usr/bin/grep -E '^(bwrap|unpriv_bwrap)(//| )'   /sys/kernel/security/apparmor/profiles
loaded_bwrap_post_grep_rc=$?
printf 'loaded_bwrap_post_grep_rc=%s\n' "$loaded_bwrap_post_grep_rc"

test -e /etc/apparmor.d/bwrap-userns-restrict   && echo 'active_profile_target=PRESENT_STOP'   || echo 'active_profile_target=ABSENT_EXPECTED'

systemctl is-active apparmor.service
sysctl -n kernel.apparmor_restrict_unprivileged_userns

sha256sum   /usr/share/apparmor/extra-profiles/bwrap-userns-restrict

git --no-optional-locks status --porcelain=v1 | /usr/bin/wc -l
git branch --show-current
git --no-optional-locks rev-parse --short HEAD
~~~

Required:

~~~text
bwrap_pgrep_post_rc: 1
securityfs_post_readable_rc: 0
loaded_bwrap_post_grep_rc: 1
active_profile_target: ABSENT_EXPECTED
apparmor_service: active
kernel.apparmor_restrict_unprivileged_userns: 1
sha256: unchanged
repository_status_count: 0
branch: main
commit: e511249
~~~

## Decision states

PASS:

~~~text
R5A_STATIC_SOURCE: PASS
R5A_TARGET_AND_OVERRIDES: PASS
R5A_EXECUTABLE_IDENTITY: PASS
R5A_PROCESS_AND_POLICY_ABSENCE: PASS
R5A_POLICY_NAMES: PASS
R5A_PARSER_DRY_RUN: PASS
R5A_POST_STATE: UNCHANGED
R5A_STATUS: PASS
REMEDIATION_STATUS: PACKAGES_INSTALLED_PROFILE_VALIDATED_NOT_ACTIVE
~~~

BLOCKED:

~~~text
R5A_STATUS: BLOCKED
REMEDIATION_STATUS: PACKAGES_INSTALLED_PROFILE_NOT_ACTIVE
REAL_CODEX_SANDBOX: BLOCKED_AT_BOOTSTRAP
~~~

In every outcome:

~~~text
R5B_PROFILE_CHANGE_AUTHORIZED: false
CODEX_SMOKE_TEST_AUTHORIZED: false
CODEX_LOCAL_WRITE_READINESS: BLOCKED
TI2_EXECUTION_AUTHORIZED: false
MERGE_AUTHORIZED: false
~~~

## Subsequent gate remains closed

A PASS in R5A would establish only that the packaged source is suitable for a
separate mutation proposal. It would not authorize copying or loading it.

Before any R5B proposal, the mutating procedure must be independently reviewed
for no-clobber publication and time-of-check/time-of-use protection. The
overwrite-capable copy in the earlier runbook remains non-executable unless a
later approved addendum explicitly supersedes it.
