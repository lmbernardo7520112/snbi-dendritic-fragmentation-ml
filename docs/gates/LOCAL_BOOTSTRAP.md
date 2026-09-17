# Gate LB0 — Governed local VS Code bootstrap

## Scope

LB0 evaluates only the local development surface: repository instructions,
versioned editor configuration, data-name guardrails, sanitized diagnostics,
synthetic policy tests and the ability of the real Codex sandbox to initialize.
LB0 alone does not authorize local writes or TI-2. The author subsequently
granted both, within the boundaries of the separate execution decision.

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
| Local Codex write readiness | `AUTHORIZED_DEFAULT_SANDBOX_REPOSITORY_ONLY` | Separate author-approved closure/execution decision after R6 |
| TI-2 execution | `AUTHORIZED_E0_E7_FROZEN_30_IMAGE_PILOT` | Explicit execution decision; no TI-3+ authority |

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
scientific data. The separate
[execution decision](../decisions/AUTHORIZATION-LB0-SDR2A-CLOSURE-PR5-MERGE-TI2-EXECUTION-2026-09-17.md)
supplies the current bounded authorization; it does not arise from LB0 PASS
alone.

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

Separately authorized:

~~~text
CODEX_LOCAL_WRITE_READINESS: AUTHORIZED_DEFAULT_SANDBOX_REPOSITORY_ONLY
TI2_EXECUTION_AUTHORIZED: true
MERGE_PR5_AUTHORIZED: true, conditional on green CI
~~~

## Controlled execution and Git approval

No further SDR-2-A diagnostic is justified.

The author approved PR #5 readiness and merge conditional on green CI,
fast-forward synchronization of main, the dedicated TI-2 branch and execution
E0–E7. This record describes authority, not evidence that any Git action ran.

The later [targeted Git approval decision](../decisions/AUTHORIZATION-TI2-TARGETED-GIT-APPROVALS-2026-09-17.md)
resumed TI-2 after the operational Git-index write block. Exact-path staging
and each commit require individual approvals. Push approval follows final gate
decisions and passing tests; Draft PR creation is separately approved. Read-only
Git metadata does not reopen the resolved sandbox incident.

At resumption, G2-SPATIAL and G3 were `NOT_EVALUATED`; see the
[execution-state snapshot](../../artifacts/evidence/TI2/execution-state.json).
Scientific gates require their own evidence, and TI-3 through TI-8 and merging
the TI-2 Draft PR remain prohibited without new author authority.
