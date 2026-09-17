# Authorization record — SDR-2-A gate R4 package transaction

## Metadata

- Date: 2026-09-17
- Decision owner: Leonardo Maximino Bernardo
- Approved runbook baseline: 91d324baa4dcbfc8815a6bf780fa3d35b65ce1ff
- Evidence baseline: 5e586ba145de8734028c7e1bf7134fcd54ff93c6
- Execution actor: HUMAN_OPERATOR
- Authorization status: APPROVED_R4_EXACT_CLOSURE

## Author decision

The author approved R1 and R2 and authorized only R4 for this exact package
closure from official Ubuntu noble-updates:

| Package | Version | Architecture | Action |
|---|---|---|---|
| apparmor-profiles | 4.0.1really4.0.1-0ubuntu0.24.04.7 | all | install |
| apparmor-utils | 4.0.1really4.0.1-0ubuntu0.24.04.7 | all | install |
| python3-apparmor | 4.0.1really4.0.1-0ubuntu0.24.04.7 | all | install |
| python3-libapparmor | 4.0.1really4.0.1-0ubuntu0.24.04.7 | amd64 | install |

The authorization includes the required download and ordinary dpkg maintainer
scripts for exactly these packages.

## Released operation

The human operator may run the R4 package transaction without automatic
confirmation and may perform the approved read-only post-install verification.

The transaction must be rejected if the interactive APT plan differs from the
approved simulation.

## Explicitly blocked

- apt update or package-index refresh;
- any package or version outside the exact closure;
- Recommends or Suggests;
- upgrades, removals, downgrades or replacements;
- copying, loading, replacing or removing an AppArmor profile;
- changing a sysctl or reloading AppArmor;
- local Codex execution or smoke testing;
- rollback;
- local Codex writes;
- TI-2 or any later phase;
- PR readiness or merge.

## Current state

~~~text
R1_STATUS: PASS
R2_STATUS: PASS
APT_DEPENDENCY_CLOSURE_STATUS: APPROVED_EXACT
R4_PACKAGE_TRANSACTION_AUTHORIZED: true
R4_POST_INSTALL_READ_ONLY_VERIFICATION_AUTHORIZED: true
R5_PROFILE_CHANGE_AUTHORIZED: false
CODEX_SMOKE_TEST_AUTHORIZED: false
REMEDIATION_STATUS: NOT_STARTED
CODEX_LOCAL_WRITE_READINESS: BLOCKED
TI2_EXECUTION_AUTHORIZED: false
MERGE_AUTHORIZED: false
~~~
