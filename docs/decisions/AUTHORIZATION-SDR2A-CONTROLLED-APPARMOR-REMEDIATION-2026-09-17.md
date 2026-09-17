# Authorization record — SDR-2-A controlled local sandbox remediation

## Metadata

- Date: 2026-09-17
- Author and decision owner: Leonardo Maximino Bernardo
- Repository: lmbernardo7520112/snbi-dendritic-fragmentation-ml
- Working branch: docs/post-lb0-readonly-diagnostic
- Pull request: Draft PR #5
- Decision status: AUTHORIZED_AT_POLICY_LEVEL
- Execution actor: HUMAN_OPERATOR
- Runbook status: DRAFT_PENDING_AUTHOR_APPROVAL
- Execution gate: CLOSED

## Author decision

The author stated:

> CONFIRMO E APROVO INTEGRALMENTE A ETAPA SDR-2-A NOS TERMOS APRESENTADOS.

This decision authorizes preparation of a bounded remediation runbook and,
after separate approval of that exact runbook, manual execution by the human
operator. It does not authorize the local Codex agent to execute commands or
write files while its sandbox is blocked.

## Basis for the decision

Collected evidence establishes:

- Ubuntu 24.04.4 LTS on x86_64;
- bubblewrap 0.9.0 from the Ubuntu bubblewrap package;
- AppArmor enabled and active;
- kernel.apparmor_restrict_unprivileged_userns=1;
- no readable bwrap-userns-restrict profile in the active or extra-profile
  paths inspected before remediation;
- local Codex tool startup fails with:
  bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted;
- the automated diagnostic stops before reading attachments or running
  commands.

Official OpenAI sandbox guidance documents an Ubuntu 24.04 remediation that
loads the bwrap AppArmor profile without disabling the global AppArmor
restriction:

https://learn.chatgpt.com/docs/sandboxing

The current causal classification remains:

SUPPORTED_HYPOTHESIS_HIGH_NOT_CONFIRMED

## Authorized remediation objective

Restore the standard Linux Codex sandbox by installing only the approved
Ubuntu AppArmor support packages, activating the official bwrap profile, and
performing one bounded read-only Codex sandbox smoke test.

## Authorized scope

Subject to approval of the exact runbook, the human operator may:

1. perform the listed read-only preflight;
2. inspect Ubuntu package candidates and simulate the APT transaction;
3. request approval of the exact dependency closure if the transaction
   changes anything beyond the two named target packages;
4. install apparmor-profiles and apparmor-utils from verified official Ubuntu
   sources;
5. verify provenance of the packaged bwrap-userns-restrict profile;
6. install that profile into the active AppArmor directory only when the
   destination was proven absent;
7. load the profile without weakening global AppArmor policy;
8. run the listed post-change checks;
9. perform one read-only local Codex sandbox smoke test;
10. execute the bounded policy rollback if a defined rollback condition occurs;
11. record sanitized evidence in Draft PR #5.

## Explicit prohibitions

The authorization does not permit:

- command execution or file writes by local Codex before sandbox verification;
- danger-full-access, --yolo, sandbox bypass or unsandboxed fallback;
- disabling AppArmor;
- changing kernel.apparmor_restrict_unprivileged_userns;
- granting broad file capabilities or setuid to bwrap;
- package removals, downgrades or unrelated upgrades;
- unreviewed dependencies, Recommends or Suggests;
- third-party package origins;
- access to credentials, authentication files or experimental data;
- execution of TI-2 or phases TI-3 through TI-8;
- marking Draft PR #5 ready, merging it or merging any remediation record.

## APT dependency-closure gate

The expression “install only apparmor-profiles and apparmor-utils” does not
silently authorize additional package changes.

| Simulated APT result | Decision |
|---|---|
| Both targets already installed; no change | Record and continue to profile gate |
| Only the two target packages are newly installed | Eligible after runbook approval |
| New required dependency appears | Stop; enumerate and obtain explicit approval |
| Existing package would be upgraded | Stop |
| Removal, downgrade or replacement appears | Stop |
| Recommends or Suggests would be installed | Stop |
| Official Ubuntu origin cannot be established | Stop |
| Package indexes must be refreshed | Stop and obtain a bounded source/update authorization |

## Required gates

1. R0 — Runbook review and explicit approval.
2. R1 — Read-only host and repository preflight.
3. R2 — APT candidate provenance and transaction simulation.
4. R3 — Exact dependency-closure decision.
5. R4 — Approved package transaction.
6. R5 — Profile provenance, copy and load.
7. R6 — Post-change security verification.
8. R7 — One read-only Codex sandbox smoke test.
9. R8 — Result or rollback evidence recorded in Draft PR #5.

A failure or scope divergence at any gate stops the procedure.

## Current machine and project state

~~~text
SDR2A_POLICY_AUTHORIZED: true
EXECUTION_ACTOR: HUMAN_OPERATOR
RUNBOOK_STATUS: DRAFT_PENDING_AUTHOR_APPROVAL
RUNBOOK_EXECUTION_RELEASED: false
EXECUTION_GATE: CLOSED
PREFLIGHT_STATUS: NOT_RUN
APT_SIMULATION_STATUS: NOT_RUN
APT_DEPENDENCY_CLOSURE_STATUS: NOT_ESTABLISHED
REMEDIATION_STATUS: NOT_STARTED
VERIFICATION_STATUS: NOT_RUN
ROLLBACK_STATUS: NOT_REQUIRED
CAUSE_ATTRIBUTION: SUPPORTED_HYPOTHESIS_HIGH_NOT_CONFIRMED
LOCAL_SANDBOX_STATUS: BLOCKED_AT_BOOTSTRAP
AUTOMATED_DIAGNOSTIC: BLOCKED_AT_SANDBOX_BOOTSTRAP
SYSTEM_CHANGES_EXECUTED: 0
CODEX_LOCAL_WRITE_READINESS: BLOCKED
DRAFT_PR_5_MUST_REMAIN_DRAFT: true
MERGE_AUTHORIZED: false
TI2_EXECUTION_AUTHORIZED: false
~~~

No execution is released by this record alone.
