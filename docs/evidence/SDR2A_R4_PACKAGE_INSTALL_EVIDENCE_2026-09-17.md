# SDR-2-A evidence — gate R4 package transaction

## Metadata

- Date: 2026-09-17
- Execution actor: human operator
- Approved runbook baseline: 91d324baa4dcbfc8815a6bf780fa3d35b65ce1ff
- Authorization record: AUTHORIZATION-SDR2A-R4-EXACT-PACKAGE-CLOSURE-2026-09-17.md
- Evidence status: SANITIZED
- Package transaction performed: true
- AppArmor profile copied or loaded: false
- Codex sandbox smoke test performed: false

## Authorized transaction observed

The interactive APT plan matched the previously approved four-package closure.
The human operator accepted the transaction only after reviewing that plan.

| Action | Package | Version | Origin |
|---|---|---|---|
| Install | apparmor-profiles | 4.0.1really4.0.1-0ubuntu0.24.04.7 | Ubuntu noble-updates/main |
| Install | apparmor-utils | 4.0.1really4.0.1-0ubuntu0.24.04.7 | Ubuntu noble-updates/main |
| Install | python3-apparmor | 4.0.1really4.0.1-0ubuntu0.24.04.7 | Ubuntu noble-updates/main |
| Install | python3-libapparmor | 4.0.1really4.0.1-0ubuntu0.24.04.7 | Ubuntu noble-updates/main |

~~~text
downloaded_bytes_reported: 201 kB
additional_disk_space_reported: 1,416 kB
new_packages: 4
upgrades: 0
removals: 0
downgrades: 0
packages_not_upgraded: 176
suggested_only_not_installed: vim-addon-manager
APT_TRANSACTION_CONFORMITY: PASS
~~~

No apt update, Recommends, Suggests, unrelated package action, removal,
downgrade or upgrade was reported.

## Installed-state verification

The post-install dpkg query reported:

| Package | State | Version |
|---|---|---|
| apparmor | installed | 4.0.1really4.0.1-0ubuntu0.24.04.7 |
| apparmor-profiles | installed | 4.0.1really4.0.1-0ubuntu0.24.04.7 |
| apparmor-utils | installed | 4.0.1really4.0.1-0ubuntu0.24.04.7 |
| bubblewrap | installed | 0.9.0-1ubuntu0.1 |
| python3-apparmor | installed | 4.0.1really4.0.1-0ubuntu0.24.04.7 |
| python3-libapparmor | installed | 4.0.1really4.0.1-0ubuntu0.24.04.7 |

The targeted `dpkg --verify` command produced no output. Within the scope of
that check, dpkg reported no integrity deviation for the four newly installed
packages.

## Official profile-source evidence

~~~text
source_path: /usr/share/apparmor/extra-profiles/bwrap-userns-restrict
package_owner: apparmor-profiles
file_type: regular file
mode: 644
owner: root
group: root
sha256: 11d39094f044f0cda0febb3ad517b830301da6b2ce929664af09ee9e4dd264f9
PROFILE_SOURCE_PROVENANCE: PASS
~~~

The source profile was obtained from the installed Ubuntu package. No profile
was synthesized or downloaded separately.

## Preserved pre-change posture

~~~text
active_target_path: /etc/apparmor.d/bwrap-userns-restrict
active_target_state: ABSENT_EXPECTED
running_bwrap_process: NONE
loaded_bwrap_policy: NO_MATCH
apparmor_service: active
kernel.apparmor_restrict_unprivileged_userns: 1
repository_worktree_count: 0
repository_commit: e511249
PROFILE_ACTIVATION_PERFORMED: false
~~~

The absence of the active target and loaded policy confirms that R4 installed
the approved packages but did not cross into R5 profile installation or load.

## Technical gate assessment

~~~text
R1_STATUS: PASS
R2_STATUS: PASS
APT_DEPENDENCY_CLOSURE_STATUS: INSTALLED_VERIFIED
R4_TECHNICAL_ASSESSMENT: PASS
R4_FORMAL_CLOSURE: PENDING_AUTHOR_DECISION
REMEDIATION_STATUS: PACKAGES_INSTALLED_PROFILE_NOT_ACTIVE
R5_PROFILE_CHANGE_AUTHORIZED: false
CODEX_SMOKE_TEST_AUTHORIZED: false
REAL_CODEX_SANDBOX: BLOCKED_AT_BOOTSTRAP
CODEX_LOCAL_WRITE_READINESS: BLOCKED
TI2_EXECUTION_AUTHORIZED: false
MERGE_AUTHORIZED: false
~~~

## Next controlled decision

The next professional step is not profile activation. It is a separate,
read-only profile-validation gate that must be presented and explicitly
authorized before execution. That gate should validate the official source,
the absence of target, staging and local overrides, the policy names declared
by the file, parser compilation without kernel load, and the unchanged host
posture.

No copy, write under `/etc/apparmor.d`, profile load, smoke test, rollback or
TI-2 activity is authorized by this evidence record.
