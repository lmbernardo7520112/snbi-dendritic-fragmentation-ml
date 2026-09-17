# Gate LB0 — Governed local VS Code bootstrap

## Scope

LB0 evaluates only the local development surface: repository instructions,
versioned editor configuration, data-name guardrails, sanitized diagnostics,
synthetic policy tests and the ability of the real Codex sandbox to initialize.
It does not authorize local writes or TI-2.

## Formal decision

The author approved LB0-STATIC and confirmed workspace sanitization on
17 September 2026. The initial local acceptance was PARTIAL because the Codex
Linux sandbox failed during bwrap bootstrap. SDR-2-A then applied the official
AppArmor-profile remediation under explicit, bounded authorizations.

The single terminal R6 smoke test returned exactly `CODEX_SANDBOX_OK`.
Consequently, the former PARTIAL state is superseded and LB0 local acceptance
is now PASS.

| Dimension | Formal status | Basis |
|---|---|---|
| Static/documental conformance | `PASS` | PR #4, deterministic CI, guards, synthetic tests and author approval |
| Workspace sanitization | `CONFIRMED_BY_AUTHOR` | Human inspection confirmed the standalone clone contains no scientific data |
| LB0 local acceptance | `PASS` | Static acceptance plus successful real Codex sandbox smoke test |
| Real Codex sandbox | `PASS_SMOKE` | Exact terminal output `CODEX_SANDBOX_OK` |
| SDR-2-A remediation | `RESOLVED` | Historical RTM_NEWADDR bootstrap blocker did not recur |
| Local Codex write readiness | `BLOCKED_PENDING_SEPARATE_AUTHOR_DECISION` | R6 authorized only one read-only command |
| TI-2 execution | `NOT_AUTHORIZED` | Approved TI-2 plan still requires explicit execution authority |

## Static acceptance evidence

- PR #4 was merged into `main` as merge commit `e511249`;
- the reviewed PR head was `d29dfe2`, with deterministic CI passing;
- the local checkout was standalone and clean;
- the tracked-repository guard examined 85 index entries, read zero content
  bytes, found no violations and returned PASS;
- the governed-bootstrap check returned PASS;
- the author confirmed workspace sanitization by human inspection.

## Sandbox remediation evidence

The historical failure was:

~~~text
bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted
~~~

SDR-2-A established that:

- Ubuntu AppArmor and its user-namespace restriction remained enabled;
- official Ubuntu AppArmor packages and the packaged
  `bwrap-userns-restrict` source were used;
- the source hash and parser compatibility were validated;
- the terminal protocol permitted only bounded profile activation,
  verification, one smoke test and conditional rollback;
- the operator reported the exact successful R6 output:

~~~text
CODEX_SANDBOX_OK
~~~

Detailed R5B stdout was not reproduced in the closure report. The gate's
functional claim is therefore limited to the directly observed successful
sandbox startup and read-only command.

## Interpretation

LB0 PASS means the governed local environment is technically capable of
starting the real Codex sandbox. It is not permission for the local Codex to
write files, execute arbitrary commands, access credentials or inspect
scientific data.

The Git-index guard remains a name-based tracked-path control. Workspace
sanitization remains a human attestation rather than a byte-level scan of
ignored paths.

## Closed and open authorities

Closed:

~~~text
LB0_STATIC: PASS
WORKSPACE_SANITIZATION: CONFIRMED_BY_AUTHOR
REAL_CODEX_SANDBOX: PASS_SMOKE
LB0_LOCAL_ACCEPTANCE: PASS
SDR2A_STATUS: RESOLVED
~~~

Still blocked:

~~~text
CODEX_LOCAL_WRITE_READINESS: BLOCKED_PENDING_SEPARATE_AUTHOR_DECISION
TI2_EXECUTION_AUTHORIZED: false
MERGE_PR5_AUTHORIZED: false
~~~

## Next controlled action

No further SDR-2-A diagnostic is justified.

The next project decision is:

1. review and formally close the documentation in Draft PR #5;
2. decide whether to make the PR ready and merge it;
3. separately authorize a bounded local Codex work scope and the exact first
   executable increment of TI-2.

TI-2, scientific-data access and local Codex writes remain closed until that
decision is explicit.
