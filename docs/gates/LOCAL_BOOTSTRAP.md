# Gate LB0 — Governed local VS Code bootstrap

## Scope

LB0 evaluates only the local development surface: repository instructions,
versioned editor configuration, data-name guardrails, sanitized diagnostics,
and synthetic policy tests. It does not evaluate or authorize TI-2.

## Split decision

| Dimension | Technical status | Basis |
|---|---|---|
| Static/documental conformance | `PASS_PROPOSED` | Bootstrap contracts and synthetic tests pass in the review environment |
| Local Codex write readiness | `BLOCKED` | A real sandboxed command on the author's VS Code host and a separate authorization are still required |
| Workspace sanitization | `NOT_VERIFIED` | Index-only checks deliberately do not inspect ignored local data areas |
| TI-2 execution | `NOT_AUTHORIZED` | Approval of its plan is not authorization to execute it |

`PASS_PROPOSED` is a technical assessment for review, not a substitute for the
author's gate decision. A successful standalone `bwrap` capability probe is
insufficient to establish full Codex/seccomp readiness. A failed real sandbox
start must not trigger an unsandboxed retry or operating-system change.

## Acceptance evidence

- root `AGENTS.md` contains machine-readable authorization sentinels;
- VS Code settings exclude opaque data areas from search and file watching;
- tasks are exact, explicit process invocations and never run automatically;
- the Git-index guard rejects data paths, forbidden binary suffixes, symlinks,
  submodules, path traversal, and non-allow-listed artifacts without opening
  their contents;
- local diagnostics execute no mutating command, disable optional Git locks,
  are sanitized and do not run a capability probe without `--probe-bwrap`;
- bootstrap policy tests use only text, JSON, mocks, and fictitious path
  strings; the pre-existing TI-0/TI-1 CI regression suite uses small synthetic
  byte containers but never experimental data or media decoding;
- no test implements frame handling, pixel access, registration, calibration,
  labels, datasets, baselines, models, training, or evaluation.

## Closure rule

LB0-STATIC may be closed only after CI passes and the author reviews the PR. Local
Codex write readiness additionally requires a successful real sandboxed
command on the actual host and a separate author decision. Neither closure nor
sandbox readiness changes the state of TI-2.

The Git-index guard proves only that no tracked path or mode violates its
explicit name-based rules. It deliberately does not inspect file contents and
cannot recognize experimental bytes hidden under an otherwise allowed name. It
also does not prove that an ignored local data directory is absent. Before any
future local write authorization, the author must attest that the opened
workspace is a standalone sanitized clone, with an in-root `.git` directory
and without experimental sources or derived data. Linked worktrees are not
permitted.
