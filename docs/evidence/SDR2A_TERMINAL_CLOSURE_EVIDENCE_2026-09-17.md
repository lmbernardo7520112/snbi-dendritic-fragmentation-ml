# SDR-2-A terminal closure evidence

## Metadata

- Date: 2026-09-17
- Execution actor: human operator
- Authorized terminal protocol: d3ef075de08b92c4bc571ae52e0391da10f2bb1e
- Authorization record: AUTHORIZATION-SDR2A-R5B-R6-TERMINAL-EXECUTION-2026-09-17.md
- Evidence status: OPERATOR_REPORTED_SANITIZED
- Smoke-test attempts authorized: 1
- Smoke-test attempts reported: 1

## Terminal functional evidence

The operator reported the exact output required by R6:

~~~text
CODEX_SANDBOX_OK
~~~

The authorized prompt permitted exactly one sandboxed, read-only command:

~~~text
/usr/bin/printf 'CODEX_SANDBOX_OK\n'
~~~

The result demonstrates that the real local Codex sandbox initialized and
executed the allowed command without the historical RTM_NEWADDR bootstrap
failure.

## Evidence boundary

The operator returned the terminal smoke-test result rather than the complete
T1 through T4 stdout. This record therefore treats the exact functional result
as conclusive evidence for sandbox startup, while preserving the narrower
provenance statement:

~~~text
R5B_DETAILED_STDOUT: NOT_REPRODUCED_IN_CLOSURE_REPORT
R6_FUNCTIONAL_OUTPUT: VERIFIED_EXACT
~~~

No claim is made here about general command execution, write behavior,
scientific-data access or TI-2.

## Terminal decision

~~~text
SDR2A_STATUS: RESOLVED
REAL_CODEX_SANDBOX: PASS_SMOKE
R6_SMOKE_TEST: PASS
ROLLBACK_REQUIRED: false
LB0_LOCAL_ACCEPTANCE: PASS
CODEX_LOCAL_WRITE_READINESS: BLOCKED_PENDING_SEPARATE_AUTHOR_DECISION
TI2_EXECUTION_AUTHORIZED: false
MERGE_AUTHORIZED: false
~~~

## Consequences

- Do not execute rollback after the successful smoke test.
- Do not repeat the smoke test.
- The prior sandbox blocker is closed.
- Local Codex write permission remains blocked because it was not part of R6.
- TI-2 remains blocked because its approved plan still requires a separate
  execution authorization.
- PR #5 remains Draft until a separate review and merge decision.

## Next project decision

The project can now return from host remediation to the scientific roadmap.
The next controlled decision is to close and review this documentation branch,
then determine the exact first executable scope of TI-2. No further SDR-2-A
diagnostic is justified.
