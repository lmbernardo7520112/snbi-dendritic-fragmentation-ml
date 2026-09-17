# SDR-2-A evidence — gates R1 and R2

## Metadata

- Date: 2026-09-17
- Execution actor: human operator
- Approved runbook: commit 91d324baa4dcbfc8815a6bf780fa3d35b65ce1ff
- Evidence status: SANITIZED
- System changes during collection: 0
- Network use during collection: false
- Package installation performed: false

## R1 — Read-only preflight

### Repository

~~~text
repository_status: CLEAN
branch: main
commit: e511249
standalone_checkout: YES
R1_REPOSITORY: PASS
~~~

### Host and sandbox prerequisites

~~~text
os_id: ubuntu
os_version: 24.04.4 LTS
kernel: 6.17.0-1032-oem
architecture: x86_64
bubblewrap_version: 0.9.0
apparmor_service: active
kernel.apparmor_restrict_unprivileged_userns: 1
R1_HOST: PASS
~~~

### Installed package state before remediation

| Package | State | Version |
|---|---|---|
| apparmor | installed | 4.0.1really4.0.1-0ubuntu0.24.04.7 |
| bubblewrap | installed | 0.9.0-1ubuntu0.1 |
| apparmor-utils | not-installed | — |
| apparmor-profiles | not-installed / no installed entry | — |

### Profile and process state

~~~text
active_profile_target: ABSENT_EXPECTED
packaged_profile_source: ABSENT_BEFORE_INSTALL
running_bwrap_process: NONE
loaded_bwrap_policy: NO_MATCH
R1_PROFILE_STATE: PASS
~~~

The privileged securityfs inspection was read-only. No profile was loaded,
copied, replaced or removed.

## R2 — APT provenance and simulation

### Candidate origin

Both target candidates were resolved from official Ubuntu archives:

~~~text
suite: noble-updates/main
candidate_version: 4.0.1really4.0.1-0ubuntu0.24.04.7
archive: http://archive.ubuntu.com/ubuntu
~~~

The older Noble base version was visible but was not selected.

### Simulated exact transaction

| Action | Package | Version | Architecture / origin |
|---|---|---|---|
| Install | python3-libapparmor | 4.0.1really4.0.1-0ubuntu0.24.04.7 | amd64, Ubuntu noble-updates |
| Install | python3-apparmor | 4.0.1really4.0.1-0ubuntu0.24.04.7 | all, Ubuntu noble-updates |
| Install | apparmor-utils | 4.0.1really4.0.1-0ubuntu0.24.04.7 | all, Ubuntu noble-updates |
| Install | apparmor-profiles | 4.0.1really4.0.1-0ubuntu0.24.04.7 | all, Ubuntu noble-updates |

~~~text
new_packages: 4
upgrades: 0
removals: 0
downgrades: 0
packages_not_upgraded: 176
suggested_only_not_selected: vim-addon-manager
APT_SIMULATION_STATUS: PASS_WITH_EXACT_CLOSURE_PENDING_APPROVAL
~~~

The count of 176 packages not upgraded is informational; the simulated
transaction does not upgrade them.

## Gate result

~~~text
R1_STATUS: PASS
R2_STATUS: PASS
APT_DEPENDENCY_CLOSURE_STATUS: ESTABLISHED_PENDING_AUTHOR_APPROVAL
APT_UPDATE_REQUIRED: false
PACKAGE_INSTALL_AUTHORIZED: false
APPARMOR_CHANGE_AUTHORIZED: false
CODEX_SMOKE_TEST_AUTHORIZED: false
REMEDIATION_STATUS: NOT_STARTED
REAL_CODEX_SANDBOX: BLOCKED_AT_BOOTSTRAP
CODEX_LOCAL_WRITE_READINESS: BLOCKED
TI2_EXECUTION_AUTHORIZED: false
~~~

## Next decision

The two Python packages are required dependencies not named in the earlier
target-only authorization. Fail-closed governance therefore requires explicit
approval of all four package names, exact versions and official origins before
R4 can be released.

Any real APT prompt that differs from this closure must be rejected.
