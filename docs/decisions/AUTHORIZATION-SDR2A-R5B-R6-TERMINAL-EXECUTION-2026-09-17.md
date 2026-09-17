# Authorization record — terminal SDR-2-A R5B/R6 execution

## Metadata

- Date: 2026-09-17
- Decision owner: Leonardo Maximino Bernardo
- Authorized protocol commit: d3ef075de08b92c4bc571ae52e0391da10f2bb1e
- Protocol: docs/protocols/SDR2A_R5B_R6_TERMINAL_REMEDIATION.md
- Execution actor: HUMAN_OPERATOR
- Authorization status: APPROVED_SINGLE_TERMINAL_EXECUTION

## Formal decisions

The author:

1. formally closed R5A with status PASS;
2. authorized exactly one manual execution of the terminal R5B/R6 protocol at
   commit `d3ef075de08b92c4bc571ae52e0391da10f2bb1e`;
3. authorized the immediate T1 precondition;
4. authorized installation of the verified official profile at
   `/etc/apparmor.d/bwrap-userns-restrict`;
5. authorized verification of the installed copy;
6. authorized strict loading with `apparmor_parser -a -K`;
7. authorized the exact post-load verification;
8. authorized exactly one read-only Codex sandbox smoke test;
9. authorized the documented conditional rollback if T2, T3, T4 or R6 fails.

The terminal outcome must be one of:

~~~text
RESOLVED
BLOCKED_AFTER_OFFICIAL_PROFILE
~~~

## Execution constraints

- The human operator executes the runbook manually.
- T1 through T4 are executed in the same ordinary terminal session.
- The terminal remains open during the single Codex smoke test so the frozen
  shell variables remain available if conditional rollback is required.
- A block may run only when the previous block's required results match.
- Any mismatch releases only the documented rollback when its preconditions
  are satisfied.
- The smoke test may be attempted once.
- Only sanitized evidence may be recorded.

## Explicitly prohibited

- changing any command or option in the approved protocol;
- retrying a failed mutation or smoke test;
- disabling or globally reloading AppArmor;
- changing any sysctl;
- full access, danger-full-access, `--yolo` or sandbox bypass;
- general or write-capable local Codex execution;
- accessing credentials or experimental data;
- PR #5 readiness or merge;
- TI-2 or phases TI-3 through TI-8.

## State at release

~~~text
R5A_STATUS: PASS
R5B_EXECUTION_RELEASED: true
R5B_EXECUTION_COUNT_LIMIT: 1
R5B_EXECUTION_ACTOR: HUMAN_OPERATOR
R6_SMOKE_TEST_AUTHORIZED: true
R6_SMOKE_TEST_COUNT_LIMIT: 1
CONDITIONAL_ROLLBACK_AUTHORIZED: true
CODEX_LOCAL_WRITE_READINESS: BLOCKED
TI2_EXECUTION_AUTHORIZED: false
MERGE_AUTHORIZED: false
~~~

## Closure requirement

The operator returns one consolidated sanitized report containing T1 through
T4, the single R6 result and, only if invoked, the rollback evidence.

No new diagnostic or remediation branch may be opened inside SDR-2-A after
that report. The phase must close in one of the two terminal states.
