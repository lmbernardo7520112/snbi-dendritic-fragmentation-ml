# Authorization record — SDR-2-A gates R1 and R2

## Metadata

- Date: 2026-09-17
- Decision owner: Leonardo Maximino Bernardo
- Approved runbook commit: 91d324baa4dcbfc8815a6bf780fa3d35b65ce1ff
- Pull request: Draft PR #5
- Execution actor: HUMAN_OPERATOR
- Authorization status: APPROVED_R1_R2_ONLY

## Author decision

> APROVO O RUNBOOK SDR-2-A NA VERSÃO DO COMMIT 91d324b E AUTORIZO
> EXCLUSIVAMENTE A EXECUÇÃO MANUAL DOS GATES R1 E R2 — PREFLIGHT
> READ-ONLY E SIMULAÇÃO APT. NÃO AUTORIZO AINDA INSTALAÇÃO DE PACOTES,
> ALTERAÇÃO DO APPARMOR, CARREGAMENTO DE PERFIL, TESTE DO CODEX,
> ROLLBACK OU EXECUÇÃO DA TI-2.

## Released operations

The human operator may execute only the exact commands under:

- R1 — Read-only preflight;
- R2 — Read-only APT provenance and simulation.

The approved commands are those in the runbook blob present at commit
91d324baa4dcbfc8815a6bf780fa3d35b65ce1ff.

## Execution boundaries

- no local Codex tool execution;
- no package installation;
- no apt update or package-index refresh;
- no AppArmor profile copy, load, replace, removal or reload;
- no sysctl write;
- no sandbox smoke test;
- no rollback command;
- no repository write from the local clone;
- no full access, bypass or elevation beyond the single targeted read-only
  securityfs inspection listed in R1;
- no access to credentials or experimental data;
- no TI-2 or later phase;
- no PR merge or Ready-for-review transition.

## Stop conditions

Stop before R2 if any R1 invariant differs from the approved runbook.

Stop after the APT simulation regardless of its result. The transaction,
candidate origins and exact dependency closure must be reviewed before any
package operation can be considered.

## Current state

~~~text
RUNBOOK_APPROVED_COMMIT: 91d324baa4dcbfc8815a6bf780fa3d35b65ce1ff
RUNBOOK_STATUS: APPROVED_R1_R2_ONLY
RUNBOOK_EXECUTION_RELEASED: R1_R2_ONLY
EXECUTION_ACTOR: HUMAN_OPERATOR
PREFLIGHT_STATUS: NOT_RUN
APT_SIMULATION_STATUS: NOT_RUN
APT_DEPENDENCY_CLOSURE_STATUS: NOT_ESTABLISHED
PACKAGE_INSTALL_AUTHORIZED: false
APPARMOR_CHANGE_AUTHORIZED: false
CODEX_SMOKE_TEST_AUTHORIZED: false
REMEDIATION_STATUS: NOT_STARTED
REAL_CODEX_SANDBOX: BLOCKED_AT_BOOTSTRAP
CODEX_LOCAL_WRITE_READINESS: BLOCKED
TI2_EXECUTION_AUTHORIZED: false
MERGE_AUTHORIZED: false
~~~
