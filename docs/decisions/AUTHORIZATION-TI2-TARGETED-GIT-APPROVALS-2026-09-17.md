# Authorization record — TI-2 resumption with targeted Git approvals

## Metadata

- Date: 2026-09-17
- Decision owner: Leonardo Maximino Bernardo
- Repository: lmbernardo7520112/snbi-dendritic-fragmentation-ml
- Decision status: APPROVED
- Operator instruction: `TI2_RESUME_WITH_TARGETED_GIT_APPROVALS_V1`
- Authorized branch: `feat/ti2-registration-calibration`

## Basis and resumed state

The author explicitly resumed the TI-2 work preserved after staging failed with
`.git/index.lock: Read-only file system` in the default sandbox. Read-only Git
metadata is an operational restriction; it does not invalidate the successful
real Codex sandbox smoke test or reopen SDR-2-A.

The original
[closure/execution decision](AUTHORIZATION-LB0-SDR2A-CLOSURE-PR5-MERGE-TI2-EXECUTION-2026-09-17.md)
continues to control the scientific scope. LB0 remains PASS, SDR-2-A remains
RESOLVED, and no new sandbox/AppArmor diagnostic or OS remediation is authorized.

At the resumption boundary, before scientific gate evaluation:

```text
TI2_EXECUTION_AUTHORIZED=true
TI2_EXECUTION_STATUS=RESUMED_AFTER_OPERATIONAL_BLOCK
G2_SPATIAL_EVALUATION_STATE=NOT_EVALUATED
G3_EVALUATION_STATE=NOT_EVALUATED
```

These evaluation states record a resumption snapshot, not a gate decision. The
[execution-state evidence](../../artifacts/evidence/TI2/execution-state.json)
does not substitute for the eventual G2-SPATIAL or G3 evidence packages.

## Individually approved Git operations

The author permits requesting narrowly scoped approvals to complete Git
operations blocked by read-only Git metadata:

1. Review the exact file allowlist and request approval for the individual
   `git add -- <explicit reviewed paths>` operation. Do not stage with wildcards,
   `git add -A` or another all-files shortcut.
2. Request a separate approval for the concrete `git commit` operation.
3. Request push approval only after G2-SPATIAL and G3 each have a final
   `PASS`, `PARTIAL` or `BLOCKED` decision and the required tests pass.
4. Request Draft TI-2 PR creation as a separate action.

This record authorizes the targeted approval workflow; it does not state that
any individual Git operation has already been approved or completed. Each
request must identify the actual bounded action. No blanket escalation,
full-access mode, force operation, credential inspection, permission change or
sandbox bypass is authorized. The approved exception applies only to the exact
Git/GitHub action, not to scientific execution or arbitrary commands.

## Preserved boundaries

- Ordinary code, tests and evidence writes remain inside the standalone
  repository and default sandbox on the dedicated TI-2 branch.
- The required complete synthetic regression suite may run locally with
  `TMPDIR` inside ignored `.bootstrap-test-tmp/`; tests may not read experimental
  bytes. CI continues to use a clean checkout, and the editor task allowlist is
  unchanged.
- Experimental access remains read-only at the exact source supplied by the
  operator; only the 30 frozen source/index pairs may be decoded.
- Native source bytes remain immutable. Local pilot/diagnostic binaries remain
  ignored and absent from Git. Additional frames and mass extraction remain
  prohibited.
- The approved v1.0 scientific protocol, thresholds, estimation/validation split
  and fail-closed contracts are unchanged.
- Labels, event ledger, ML dataset, splits, baseline, CNN, training, model
  evaluation and TI-3 through TI-8 remain prohibited.
- Merging the TI-2 Draft PR requires a new author decision.
- A real bwrap/namespace/seccomp startup failure still requires stopping
  immediately without an unsandboxed retry.

Preserved partial changes must be reconciled on resumption; they must not be
reset or silently discarded. The scientific return condition remains final
G2-SPATIAL/G3 decisions or a real blocker requiring scope expansion.
