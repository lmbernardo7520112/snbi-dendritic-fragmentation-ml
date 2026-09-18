# TI2-PR6-REMEDIATION-2 — precommit verification

This is a bounded precommit record, not evidence of a future publication. The
single corrective commit SHA and new CI URLs belong only in the effective PR
body and terminal author report. No second commit, ready transition or merge is
authorized. Canonical current activity remains NONE_AWAITING_AUTHOR_DECISION.

## Preflight and partial acceptance

Initial SHA: `af5deb3f80e5ef0b326131c44d1f30a169b65194`.
Branch: `feat/ti2-registration-calibration`. The standalone real .git,
clean index/worktree, expected origin/upstream and equal remote SHA passed.
PR #6 was OPEN/DRAFT/unmerged, base main, at the initial SHA. Previous runs
35276612925 and 35276608001 were completed successfully.

The author partially accepted REMEDIATION-1. The independent audit identified
three remaining gaps, confirmed by textual inspection: stale LB0 active
authority, an incomplete empirical MEASURED contract and public experimental
I/O without a canonical guard before supplied-path access. This decision
corrects those gaps without changing the preserved scientific result.

## Implemented corrections

- `pyproject.toml [tool.snbi]` remains the sole authority. TI-2, TI-2R and
  TI-3 through TI-8 are explicitly blocked; all execution and merge permissions
  are false; local write readiness is BLOCKED_AWAITING_AUTHOR_DECISION.
  Former branch/pilot aliases are rejected in active authority. Renamed metadata
  lives only in `tool.snbi_history.ti2_e0_e7`, HISTORICAL_CONSUMED_NON_AUTHORIZING.
- The shared authority implementation is in the package; the script is a
  compatibility facade exporting identical functions/classes, without duplicate
  parsing. Existing guard/test imports were reconciled.
- LOCAL_BOOTSTRAP and TI2_GATE_PLAN each contain exactly one six-field JSON
  mirror with explicit current delimiters. The only document allowlist is these
  two gates. Explicitly delimited historical true states grant no authority.
  Missing/duplicate/malformed/incomplete/unknown/conflicting blocks and residual
  declarations, including Markdown emphasis, fail closed. Bootstrap and scope
  integrate this gate audit.
- MEASURED requires EMPIRICAL_MEASUREMENT, nonempty empirical provenance,
  finite nonboolean nonnegative value and nonempty unit/method. Analytical
  provenance/assumption fields are rejected. MODELLED contracts and both
  existing calibration configurations remain unchanged.
- Ten public I/O entries call the same canonical guard first, before any
  supplied-path conversion, lookup, open, subprocess, temporary file or write:
  pilot hash_stream/open_readonly/verify_archive/extract_pilot; custody
  verify_sources/verify_main; metadata probe_zip_member/ffprobe_version; and
  TI-1 main/write_json. Custody main only routes the literal textual validate
  command separately. AST, ExplodingPath and downstream mocks prove denial.
  Legacy byte fixtures use explicit guard mocks and entirely synthetic content.

## Completed local validation

Dependency-free suite: **215 executed / 210 passed / 5 skipped / 0 failures /
0 errors / 0 expected failures / 0 unexpected successes**.
The five explicit skips are the optional matching tests in the -S profile.
They also ran locally, as separately permitted by REMEDIATION-2, using already
available NumPy 1.26.4 and SciPy 1.11.4: **5 executed / 5 passed / 0 skips /
0 failures / 0 errors / 0 expected failures / 0 unexpected successes**.
No dependency was installed and only in-memory synthetic arrays were used.

Data guard, bootstrap and scope passed. Data guard reports content_bytes_read=0,
violations=[], zero tracked experimental binaries (165 index entries before
staging the new textual files). Both current gates passed. All 44 Python files
compiled in memory. Local logs, exact counters, scoped commands and limitations
are in `verification.json`.

AST comparison confirms existing I/O function bodies are preserved after
removing the added entry guards; custody retains its prior implementation
behind the new closed verification dispatch. Only the approved uncertainty
validator changed in geometry. Scientific matcher/calibration code, frozen
parameters, matrices/ROI/scale configurations, experimental gate reports,
terminal-state, pilot manifest and CI workflow remain byte-identical.

An initial focused gate test rejected a generic narrative phrase outside the
historical block; its wording was corrected. Independent review caught one
legacy facade mock and one Markdown residual-authority gap; both were corrected
before final verification. All final tests pass; no postcommit correction is
claimed or authorized.

## Checksum boundary and publication

Historical counts remain distinct: **70** at CLOSEOUT-1 and **84** at
REMEDIATION-1. The final textual manifest is prepared for **95** unique members,
excluding itself; only directly affected textual entries are updated/added.
New files are still untracked at this record's cutoff. The unchanged strict
verifier must use the real index after exact-path staging and pass before the
single commit. Its observed listed/unique/verified counters will be included
in CI logs, the effective PR body and terminal report; no untracked exception
or prospective successful verification is asserted here.

Only after both new-SHA CI runs pass the deterministic and scientific jobs,
checksums and zero-skip synthetic tests may the PR body be updated. PR #6 must
remain OPEN/DRAFT/unmerged. Ready for Review and merge require a new express
author decision. No optional follow-on hardening is authorized.

No experimental source, path, file, buffer, pixel or content hash was accessed.
No FFmpeg/FFprobe, redecoding, E0–E7, TI-2R or TI-3–TI-8 execution, scientific
retuning, installation, OS change, credential inspection or broad elevation
occurred. Only exact approved Git/GitHub actions may cross their stated boundary.
G2_SPATIAL=BLOCKED_METHOD_V1; TRANSFORM_EXISTENCE=UNDETERMINED;
G3=BLOCKED_DEPENDENCY_G2. Documentary and synthetic PASS do not approve science.

## Exact file allowlist

- `AGENTS.md`
- `README.md`
- `artifacts/evidence/TI2/checksums.sha256`
- `artifacts/evidence/TI2_PR6_REMEDIATION_2/remediation-report.md`
- `artifacts/evidence/TI2_PR6_REMEDIATION_2/verification.json`
- `docs/decisions/AUTHORIZATION-TI2-PR6-REMEDIATION-2-2026-09-17.md`
- `docs/gates/LOCAL_BOOTSTRAP.md`
- `docs/gates/TI2_GATE_PLAN.md`
- `docs/protocols/LOCAL_DEVELOPMENT.md`
- `docs/security/LOCAL_SANDBOX.md`
- `pyproject.toml`
- `scripts/check_local_bootstrap.py`
- `scripts/check_ti2_scope.py`
- `scripts/run_ti1_audit.py`
- `scripts/ti2_authority.py`
- `src/snbi_fragmentation/custody.py`
- `src/snbi_fragmentation/gate_authority.py`
- `src/snbi_fragmentation/metadata.py`
- `src/snbi_fragmentation/ti2_authority.py`
- `src/snbi_fragmentation/ti2_geometry.py`
- `src/snbi_fragmentation/ti2_pilot.py`
- `tests/test_gate_authority.py`
- `tests/test_hash_verifier.py`
- `tests/test_local_bootstrap.py`
- `tests/test_scope_guard.py`
- `tests/test_ti2_authority.py`
- `tests/test_ti2_execution.py`
- `tests/test_ti2_geometry.py`
- `tests/test_ti2_io_authority.py`
- `tests/test_ti2_pilot.py`
