# SDR-2-A — Controlled AppArmor remediation runbook

## Document status

- Status: DRAFT_PENDING_AUTHOR_APPROVAL
- Execution released: false
- Execution actor: human operator only
- Local Codex command execution: blocked until the smoke-test gate
- System changes already performed by this runbook: 0
- TI2 execution authorized: false
- Draft PR #5 merge authorized: false

**Do not execute this runbook until the author explicitly approves this exact
version.** Approval of the SDR-2-A policy did not pre-approve commands that had
not yet been presented.

## Objective

Apply the narrow Ubuntu 24.04 remediation documented by OpenAI for a Codex
Linux sandbox blocked while creating the bwrap environment:

https://learn.chatgpt.com/docs/sandboxing

The intended change is to activate the packaged bwrap-userns-restrict AppArmor
profile while preserving:

- AppArmor enabled;
- kernel.apparmor_restrict_unprivileged_userns=1;
- the ordinary distribution bwrap binary;
- sandboxed Codex execution;
- a closed TI-2 gate.

## Known evidence

~~~text
OS: Ubuntu 24.04.4 LTS
ARCHITECTURE: x86_64
BWRAP_VERSION: 0.9.0
BWRAP_PACKAGE_OWNER: bubblewrap
APPARMOR_MODULE: enabled
APPARMOR_SERVICE: active
APPARMOR_UNPRIVILEGED_USERNS_RESTRICTION: 1
ACTIVE_BWRAP_PROFILE_FILE: absent_or_unreadable
EXTRA_BWRAP_PROFILE_FILE: absent_or_unreadable
LOCAL_CODEX_FAILURE: bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted
CAUSE_ATTRIBUTION: SUPPORTED_HYPOTHESIS_HIGH_NOT_CONFIRMED
~~~

## Global stop rules

Stop immediately and report the observed output if:

- a command differs from this runbook;
- sudo requests anything other than the operator's normal local
  authentication;
- an unexpected repository, package origin, package action or file appears;
- a command proposes a removal, downgrade or unrelated upgrade;
- a package candidate is not from an official Ubuntu archive;
- the active target profile exists before this runbook creates it;
- the packaged source profile is absent after the approved package transaction;
- source and installed profile hashes differ;
- AppArmor becomes inactive;
- kernel.apparmor_restrict_unprivileged_userns changes from 1;
- any command accesses credentials or scientific data;
- the Codex smoke test fails.

Never compensate by using danger-full-access, --yolo, a sandbox bypass,
disabling AppArmor or changing a sysctl.

## Execution model

Each fenced block is run manually in the normal Ubuntu terminal, never by the
local Codex agent. Run one block at a time. Preserve only sanitized output.
Do not paste passwords, usernames, hostnames, home paths or authentication
information.

---

## R0 — Approval gate

Required state before any command:

~~~text
RUNBOOK_STATUS: APPROVED_BY_AUTHOR
RUNBOOK_EXECUTION_RELEASED: true
EXECUTION_ACTOR: HUMAN_OPERATOR
~~~

Until those values are recorded, all later blocks are documentary only.

---

## R1 — Read-only preflight

Run from the sanitized standalone repository root.

### R1.1 Repository integrity

~~~bash
git --no-optional-locks status --porcelain=v1 | /usr/bin/wc -l
git branch --show-current
git --no-optional-locks rev-parse --short HEAD
test -d .git && test ! -L .git && echo STANDALONE_OK || echo BLOCKED
~~~

Expected:

- first output: 0;
- branch: main;
- commit: e511249;
- standalone result: STANDALONE_OK.

Any difference stops the runbook. Do not switch, pull, reset or clean.

### R1.2 Host posture

~~~bash
/usr/bin/grep -E '^(ID|VERSION_ID|VERSION)=' /etc/os-release
uname -sr
uname -m
bwrap --version
systemctl is-active apparmor.service 2>/dev/null   || echo 'apparmor_service=UNKNOWN_OR_INACTIVE'
sysctl -n kernel.apparmor_restrict_unprivileged_userns 2>/dev/null   || echo 'apparmor_userns_restriction=NOT_AVAILABLE'
~~~

Expected:

- Ubuntu 24.04;
- x86_64;
- bubblewrap 0.9.0;
- AppArmor active;
- restriction value 1.

### R1.3 Package state

~~~bash
dpkg-query -W   -f='${binary:Package}\t${db:Status-Status}\t${Version}\n'   bubblewrap apparmor apparmor-profiles apparmor-utils 2>/dev/null || true
~~~

This block inventories package state. A blank or absent package line must not
be interpreted as installed.

### R1.4 Profile path state

~~~bash
test -e /etc/apparmor.d/bwrap-userns-restrict   && echo 'active_profile_target=PRESENT_STOP'   || echo 'active_profile_target=ABSENT_EXPECTED'

test -r /usr/share/apparmor/extra-profiles/bwrap-userns-restrict   && echo 'packaged_profile_source=PRESENT'   || echo 'packaged_profile_source=ABSENT_BEFORE_INSTALL'
~~~

The target must be ABSENT_EXPECTED. If it is present, stop: this runbook is not
authorized to overwrite it.

R1 produces no system change.

---

## R2 — Read-only APT provenance and simulation

Do not run apt update in this gate. The simulation uses the current local
package index and does not contact a repository.

### R2.1 Candidate provenance

~~~bash
apt-cache policy apparmor-profiles apparmor-utils
~~~

The operator must verify that each candidate is associated with an official
Ubuntu archive or Ubuntu security archive. If the origin is absent, ambiguous
or third-party, stop.

### R2.2 Exact transaction simulation

~~~bash
apt-get --simulate --no-install-recommends install   apparmor-profiles apparmor-utils
~~~

Do not execute the installation yet.

Record exactly:

- target packages to be installed;
- required dependencies to be installed;
- existing packages to be upgraded;
- removals;
- downgrades;
- held packages;
- candidate versions.

### R2 decision table

| Simulation result | Action |
|---|---|
| No change; both targets already installed | Continue to R4 after review |
| Only the two targets would be installed | Eligible after runbook release |
| Any new required dependency | Stop and obtain exact closure approval |
| Any existing package upgrade | Stop |
| Any removal, downgrade or replacement | Stop |
| Any Recommends or Suggests installation | Stop |
| Candidate origin not demonstrably official | Stop |
| No candidate because indexes are stale/missing | Stop; do not run apt update |

The operator returns the sanitized R1 and R2 outputs for review. R3 remains
closed until the exact transaction is accepted.

---

## R3 — Exact APT dependency-closure gate

This gate records one of:

~~~text
APT_DEPENDENCY_CLOSURE_STATUS: APPROVED_EXACT
APT_DEPENDENCY_CLOSURE_STATUS: BLOCKED
~~~

If the simulation contains any new dependency beyond the two target packages,
the author must explicitly approve every package name, version, action and
official origin.

No generic approval of “all dependencies” is valid.

---

## R4 — Approved package transaction

This block is executable only when R0 through R3 are PASS and the real APT
transaction shown at the confirmation prompt exactly matches the approved
simulation.

~~~bash
sudo apt-get --no-install-recommends install   apparmor-profiles apparmor-utils
~~~

Do not add -y. Review the displayed transaction before confirming.

If the displayed transaction differs from the approved simulation, answer no
and stop.

This runbook deliberately omits apt update. If updated indexes are required,
stop and obtain a separate authorization that constrains repository sources.

### R4 verification

~~~bash
dpkg-query -W   -f='${binary:Package}\t${db:Status-Status}\t${Version}\n'   bubblewrap apparmor apparmor-profiles apparmor-utils 2>/dev/null || true

test -r /usr/share/apparmor/extra-profiles/bwrap-userns-restrict   && echo 'packaged_profile_source=PRESENT'   || echo 'packaged_profile_source=BLOCKED_MISSING'
~~~

If the packaged source is missing, stop. Do not synthesize or download a
profile.

---

## R5 — Profile provenance, controlled installation and load

### R5.1 Provenance and immutable-source evidence

~~~bash
dpkg-query -S   /usr/share/apparmor/extra-profiles/bwrap-userns-restrict 2>/dev/null   || echo 'profile_package_owner=UNRESOLVED'

sha256sum   /usr/share/apparmor/extra-profiles/bwrap-userns-restrict

test -e /etc/apparmor.d/bwrap-userns-restrict   && echo 'active_profile_target=PRESENT_STOP'   || echo 'active_profile_target=ABSENT_EXPECTED'
~~~

Expected:

- package owner resolved to an approved Ubuntu package;
- source hash produced;
- target still absent.

Any divergence stops the runbook.

### R5.2 Install the exact packaged profile

~~~bash
sudo install -m 0644   /usr/share/apparmor/extra-profiles/bwrap-userns-restrict   /etc/apparmor.d/bwrap-userns-restrict
~~~

### R5.3 Verify the copy before loading it

~~~bash
stat -Lc 'profile_mode=%a owner_uid=%u owner_gid=%g'   /etc/apparmor.d/bwrap-userns-restrict

sha256sum   /usr/share/apparmor/extra-profiles/bwrap-userns-restrict   /etc/apparmor.d/bwrap-userns-restrict

/usr/bin/cmp -s   /usr/share/apparmor/extra-profiles/bwrap-userns-restrict   /etc/apparmor.d/bwrap-userns-restrict   && echo 'profile_copy=MATCH'   || echo 'profile_copy=BLOCKED_MISMATCH'
~~~

Required:

~~~text
profile_mode=644 owner_uid=0 owner_gid=0
profile_copy=MATCH
~~~

A mismatch stops the runbook before profile loading.

### R5.4 Load the profile without a global reload

~~~bash
sudo /usr/sbin/apparmor_parser -r   /etc/apparmor.d/bwrap-userns-restrict
~~~

Do not use sysctl -w and do not disable or reload all AppArmor policy.

---

## R6 — Post-change read-only verification

~~~bash
systemctl is-active apparmor.service 2>/dev/null   || echo 'apparmor_service=UNKNOWN_OR_INACTIVE'

sysctl -n kernel.apparmor_restrict_unprivileged_userns 2>/dev/null   || echo 'apparmor_userns_restriction=NOT_AVAILABLE'

sudo /usr/sbin/aa-status 2>/dev/null   | /usr/bin/grep -Ei 'bwrap|userns'   || echo 'loaded_bwrap_profile=BLOCKED_NO_MATCH'
~~~

Required:

- AppArmor remains active;
- restriction remains 1;
- the bwrap/userns profile produces matching loaded-profile evidence.

If any requirement fails, do not test Codex. Evaluate the rollback gate.

---

## R7 — Single Codex sandbox smoke test

Close no security control and change no Codex permission mode.

Open the existing Codex extension and paste this exact message as plain text,
not as an attachment:

~~~text
SDR-2-A SMOKE TEST. Execute exactly one read-only sandboxed command:

/usr/bin/printf 'CODEX_SANDBOX_OK\n'

Do not read or write any file. Do not use network access. Do not execute any
other command. Do not request elevation or full access. If sandbox startup
fails, do not retry and report the exact error only.
~~~

Only one attempt is authorized.

### R7 outcomes

| Result | State |
|---|---|
| Exact output CODEX_SANDBOX_OK | REAL_CODEX_SANDBOX=PASS_SMOKE |
| Original RTM_NEWADDR failure | REAL_CODEX_SANDBOX=BLOCKED; no retry |
| Different error | REAL_CODEX_SANDBOX=BLOCKED_UNEXPECTED; no retry |
| Codex proposes fallback/full access | Reject and stop |

A smoke-test PASS does not authorize local Codex writes or TI-2. Those remain
separate gates.

---

## R8 — Repository integrity and sanitized evidence

From the repository root:

~~~bash
git --no-optional-locks status --porcelain=v1 | /usr/bin/wc -l
git --no-optional-locks rev-parse --short HEAD
~~~

Required:

- first output remains 0;
- commit remains e511249.

Return only sanitized results. Never include sudo passwords, tokens, account
data, unrestricted logs, usernames, hostnames or home paths.

---

## Rollback gate

Rollback is permitted only when:

- R1 recorded that the target profile was absent;
- this runbook created the target;
- the target still matches the packaged source;
- a load, verification or smoke-test failure requires restoration of the prior
  policy state.

### RB1 — Validate the exact target

~~~bash
/usr/bin/cmp -s   /usr/share/apparmor/extra-profiles/bwrap-userns-restrict   /etc/apparmor.d/bwrap-userns-restrict   && echo 'rollback_target=VALIDATED'   || echo 'rollback_target=BLOCKED_MISMATCH'
~~~

Do not continue unless the output is rollback_target=VALIDATED.

### RB2 — Unload the exact profile

~~~bash
sudo /usr/sbin/apparmor_parser -R   /etc/apparmor.d/bwrap-userns-restrict
~~~

If unloading reports an error, stop and do not remove the file.

### RB3 — Remove only the runbook-created active copy

~~~bash
sudo /usr/bin/rm --   /etc/apparmor.d/bwrap-userns-restrict
~~~

This removal is recoverable from the verified packaged source.

### RB4 — Verify restored policy posture

~~~bash
test -e /etc/apparmor.d/bwrap-userns-restrict   && echo 'rollback_target=BLOCKED_STILL_PRESENT'   || echo 'rollback_target=ABSENT_RESTORED'

systemctl is-active apparmor.service 2>/dev/null   || echo 'apparmor_service=UNKNOWN_OR_INACTIVE'

sysctl -n kernel.apparmor_restrict_unprivileged_userns 2>/dev/null   || echo 'apparmor_userns_restriction=NOT_AVAILABLE'
~~~

The packages are not automatically removed during policy rollback. Package
removal may alter dependency state and requires a separate reviewed
transaction and authorization.

---

## Completion states

Success:

~~~text
REMEDIATION_STATUS: APPLIED
APPARMOR_SERVICE: ACTIVE
APPARMOR_USERNS_RESTRICTION: 1
BWRAP_PROFILE: LOADED
REAL_CODEX_SANDBOX: PASS_SMOKE
CODEX_LOCAL_WRITE_READINESS: BLOCKED_PENDING_SEPARATE_DECISION
TI2_EXECUTION_AUTHORIZED: false
~~~

Blocked:

~~~text
REMEDIATION_STATUS: BLOCKED
REAL_CODEX_SANDBOX: BLOCKED
CODEX_LOCAL_WRITE_READINESS: BLOCKED
TI2_EXECUTION_AUTHORIZED: false
~~~

Rolled back:

~~~text
REMEDIATION_STATUS: ROLLED_BACK_POLICY_ONLY
APPARMOR_USERNS_RESTRICTION: 1
CODEX_LOCAL_WRITE_READINESS: BLOCKED
TI2_EXECUTION_AUTHORIZED: false
~~~
