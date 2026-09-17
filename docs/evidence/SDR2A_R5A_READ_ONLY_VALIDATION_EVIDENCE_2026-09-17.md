# SDR-2-A evidence — R5A read-only profile validation

## Metadata

- Date: 2026-09-17
- Execution actor: human operator
- Authorized protocol commit: 70106b5e9319867c60699867e85484eb543ad25c
- Evidence status: SANITIZED
- System mutation performed by R5A: false
- Profile copied or loaded: false
- Codex smoke test performed: false

## Consolidated evidence

### Package and official source

~~~text
apparmor-profiles: installed, 4.0.1really4.0.1-0ubuntu0.24.04.7
bubblewrap: installed, 0.9.0-1ubuntu0.1
source_owner_package: apparmor-profiles
source_type: regular file
source_mode: 644
source_owner: root
source_group: root
source_sha256: 11d39094f044f0cda0febb3ad517b830301da6b2ce929664af09ee9e4dd264f9
dpkg_verify_deviations: none reported
~~~

### Target, staging and overrides

~~~text
/etc/apparmor.d/bwrap-userns-restrict: ABSENT_EXPECTED
/etc/apparmor.d/.bwrap-userns-restrict.sdr2a: ABSENT_EXPECTED
/etc/apparmor.d/local/bwrap-userns-restrict: ABSENT_EXPECTED
/etc/apparmor.d/local/unpriv_bwrap: ABSENT_EXPECTED
~~~

### Executable identity

~~~text
command_path: /usr/bin/bwrap
canonical_path: /usr/bin/bwrap
package_owner: bubblewrap
file_type: regular file
mode: 755
owner: root
group: root
~~~

### Static policy review

The official source declares exactly two relevant profiles:

- `bwrap`, attached to `/usr/bin/bwrap`;
- `unpriv_bwrap`, used for the stacked child policy.

The two optional local includes correspond to paths already proven absent.
No unexpected executable target, policy name or local override was observed.

### Process and loaded-policy baseline

~~~text
bwrap_pgrep_rc: 1
securityfs_readable_rc: 0
loaded_bwrap_grep_rc: 1
~~~

Return code 1 from pgrep and targeted grep means no matching process and no
matching loaded policy. Securityfs was readable.

### Parser and host validation

~~~text
declared_policy_names:
  - bwrap
  - unpriv_bwrap
policy_names_rc: 0
profile_compile_rc: 0
apparmor_service: active
apparmor_service_rc: 0
kernel.apparmor_restrict_unprivileged_userns: 1
apparmor_userns_sysctl_rc: 0
~~~

The parser commands used `-N -K` and `-Q -K` without sudo. They neither
loaded policy into the kernel nor used the AppArmor cache.

## Gate decision

~~~text
R5A_STATIC_SOURCE: PASS
R5A_TARGET_AND_OVERRIDES: PASS
R5A_EXECUTABLE_IDENTITY: PASS
R5A_PROCESS_AND_POLICY_ABSENCE: PASS
R5A_POLICY_NAMES: PASS
R5A_PARSER_DRY_RUN: PASS
R5A_POSTURE: PASS
R5A_STATUS: PASS
REMEDIATION_STATUS: PACKAGES_INSTALLED_PROFILE_VALIDATED_NOT_ACTIVE
R5B_PROFILE_CHANGE_AUTHORIZED: false
CODEX_SMOKE_TEST_AUTHORIZED: false
REAL_CODEX_SANDBOX: BLOCKED_AT_BOOTSTRAP
CODEX_LOCAL_WRITE_READINESS: BLOCKED
TI2_EXECUTION_AUTHORIZED: false
MERGE_AUTHORIZED: false
~~~

## Convergence decision

The read-only investigation is complete. No further diagnostic microgate is
justified before the controlled profile activation.

The remaining remediation must be terminal:

1. one controlled profile installation and load;
2. one post-change verification;
3. one Codex read-only smoke test;
4. PASS, or rollback followed by terminal BLOCKED status.

R5A PASS does not itself authorize any of those operations.
