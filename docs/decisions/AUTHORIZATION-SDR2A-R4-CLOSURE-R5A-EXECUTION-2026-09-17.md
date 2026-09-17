# Authorization record — SDR-2-A R4 closure and R5A execution

## Metadata

- Date: 2026-09-17
- Decision owner: Leonardo Maximino Bernardo
- R4 evidence commit: e4850b2866609ef121ea2055b0e1b1cad813c89e
- Authorized R5A protocol commit: 70106b5e9319867c60699867e85484eb543ad25c
- Execution actor: HUMAN_OPERATOR
- Authorization status: R4_CLOSED_PASS_R5A_READ_ONLY_AUTHORIZED

## Author decision

The author formally closed gate R4 with status PASS and authorized exclusively
the manual execution of gate R5A, as defined by
`docs/protocols/SDR2A_R5A_READ_ONLY_PROFILE_VALIDATION.md` at commit
`70106b5e9319867c60699867e85484eb543ad25c`.

The authorization covers the read-only inspections in that protocol and the
following exact unprivileged AppArmor parser modes:

- `apparmor_parser -N -K`, for policy-name listing without kernel load or
  cache use;
- `apparmor_parser -Q -K`, for parsing with kernel load and cache use
  explicitly disabled.

Neither parser invocation may use `sudo`. A failure must stop the gate; it
must not be retried with broader privileges or different options.

## Released scope

The human operator may execute, in protocol order:

1. package, ownership, metadata, hash and dpkg-integrity inspection;
2. absence checks for the active target, reserved staging path and local
   overrides;
3. distribution bwrap executable identity inspection;
4. static display of the packaged profile;
5. targeted process and loaded-policy checks, including only the explicitly
   documented privileged read of AppArmor securityfs;
6. exact `-N -K` policy-name listing without sudo;
7. exact `-Q -K` parser validation without sudo;
8. post-state verification of process, policy, target, AppArmor, sysctl, source
   hash and repository integrity.

Only sanitized results may be retained in the Draft PR.

## Fail-closed rules

The operator must stop without substitution, remediation or retry if:

- any package, source, executable, target, staging or override invariant
  differs;
- a bwrap process or relevant policy is present;
- securityfs cannot be read by the exact authorized check;
- policy names are unexpected;
- either parser command warns, errors or returns nonzero;
- a command requests unapproved privilege, write, network or scope;
- AppArmor, the sysctl value, source hash or repository state changes.

## Explicitly prohibited

- copying, creating, replacing, deleting or changing any file under
  `/etc/apparmor.d`;
- loading, replacing, removing or reloading an AppArmor policy;
- any parser mode other than the two exact read-only invocations;
- sudo for either parser invocation;
- changing AppArmor, sysctl, namespaces, services or operating-system
  configuration;
- starting or terminating bwrap;
- Codex sandbox smoke testing;
- rollback;
- local Codex command execution or write access;
- PR #5 readiness or merge;
- access to credentials or experimental data;
- TI-2 or phases TI-3 through TI-8.

## Formal state after this decision

~~~text
R1_STATUS: PASS
R2_STATUS: PASS
R4_STATUS: PASS
R4_FORMAL_CLOSURE: APPROVED
APT_DEPENDENCY_CLOSURE_STATUS: INSTALLED_VERIFIED
REMEDIATION_STATUS: PACKAGES_INSTALLED_PROFILE_NOT_ACTIVE
R5A_EXECUTION_RELEASED: true
R5A_EXECUTION_ACTOR: HUMAN_OPERATOR
R5B_PROFILE_CHANGE_AUTHORIZED: false
CODEX_SMOKE_TEST_AUTHORIZED: false
REAL_CODEX_SANDBOX: BLOCKED_AT_BOOTSTRAP
CODEX_LOCAL_WRITE_READINESS: BLOCKED
TI2_EXECUTION_AUTHORIZED: false
MERGE_AUTHORIZED: false
~~~

## Required return

The operator must return the sanitized output block-by-block. R5A is not
considered closed until its evidence has been reviewed, recorded and formally
accepted.

A PASS in R5A will not authorize R5B, profile activation, Codex testing or
TI-2. Each remains subject to a separate explicit decision.
