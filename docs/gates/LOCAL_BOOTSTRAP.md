# Gate LB0 — Governed local VS Code bootstrap

## Scope

LB0 evaluates only the local development surface: repository instructions,
versioned editor configuration, data-name guardrails, sanitized diagnostics,
and synthetic policy tests. It does not evaluate or authorize TI-2.

## Formal decision

The author reviewed the static evidence, inspected the standalone local clone,
confirmed that no experimental or derived scientific data had been placed in
that clone, and approved LB0-STATIC on 17 September 2026. The local acceptance
remains partial because the real Codex Linux sandbox did not start.

| Dimension | Formal status | Basis |
|---|---|---|
| Static/documental conformance | `PASS` | PR #4, deterministic CI run 21, guards and synthetic tests passed; author approval recorded |
| Workspace sanitization | `CONFIRMED_BY_AUTHOR` | Human inspection confirmed the standalone clone contains no videos, archives, frames, experimental images or scientific datasets |
| LB0 local acceptance | `PARTIAL` | Manual preflights passed, but the real Codex sandbox start failed |
| Real Codex sandbox | `BLOCKED` | `bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted` |
| Local Codex write readiness | `BLOCKED` | A functioning real sandbox and a separate author decision are both still required |
| TI-2 execution | `NOT_AUTHORIZED` | Approval of the TI-2 plan is not authorization to execute it |

The formal authority and preserved prohibitions are recorded in
`docs/decisions/AUTHORIZATION-LB0-STATIC-CLOSURE-LOCAL-DIAGNOSTIC-2026-09-17.md`.

## Prior proposal superseded by the author decision

Before the author reviewed the PR and inspected the local clone, the technical
proposal recorded static conformance as `PASS_PROPOSED` and workspace
sanitization as `NOT_VERIFIED`. Those were valid pre-decision states. They were
superseded, respectively, by `PASS` and `CONFIRMED_BY_AUTHOR` on 17 September
2026. Local acceptance was not promoted to PASS because the real sandbox test
failed.

## Acceptance evidence

- PR #4 was merged into `main` as merge commit `e511249` after the author
  approved LB0-STATIC;
- the reviewed PR head was `d29dfe2`, and deterministic CI run 21 completed
  successfully;
- the local checkout was on the reviewed head, reported a clean Git status,
  and returned `STANDALONE_OK` for its in-root `.git` directory;
- the tracked-repository guard examined 85 index entries, read zero content
  bytes, found no violations and returned `PASS`;
- the governed-bootstrap check returned `PASS`,
  `TI2_EXECUTION_AUTHORIZED=false`, and local write readiness `BLOCKED`;
- the default local-environment diagnostic returned `COLLECTED`, requested zero
  mutating commands, required no network and did not run the optional probe;
- the author confirmed workspace sanitization by human inspection;
- the real sandbox test failed with the exact `RTM_NEWADDR` error above and was
  stopped without fallback, elevation or operating-system change.

## Interpretation

`PASS` closes only the static/documental part of LB0. `PARTIAL` is the formal
result for local acceptance. The sandbox failure is host-environment evidence,
not a repository defect and not permission to bypass isolation.

The Git-index guard proves only that no tracked path or mode violates its
explicit name-based rules. It deliberately does not inspect file contents and
cannot recognize experimental bytes hidden under an otherwise allowed name.
The human sanitization statement is therefore recorded as an attestation, not
as a byte-level scan of ignored paths.

## Next controlled action

Only manual, deterministic, read-only collection under
`docs/protocols/LOCAL_SANDBOX_DIAGNOSTIC_PROTOCOL.md` is authorized. It may
identify the editor host, packaging, non-secret versions, AppArmor posture and
sanitized denial evidence. It may not remediate the host.

Local Codex commands, local Codex writes, unsandboxed fallback, privilege
elevation, package changes, AppArmor or kernel changes, and TI-2 execution
remain prohibited. A Draft PR does not authorize its own merge.
