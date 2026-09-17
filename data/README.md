# Experimental data custody

Raw sources are immutable external research assets and are not stored in this
public repository. The path `data/raw/` is reserved and ignored for a future,
explicitly authorized manual workflow; it must remain absent from any workspace
in which a coding agent has write access.

The canonical manifest identifies each source by logical ID, byte size, digest,
storage form, modality, and experimental condition. Verification reads bytes in
binary mode and does not extract frames or alter the source.

Absence of a local source produces an explicit verification failure; it never
causes a silent skip or a fabricated PASS.

Raw or derived experimental data must not be placed inside a workspace in
which a coding agent has write access. For later authorized scientific phases,
use an external read-only source location or a standalone sanitized clone with
its own in-root `.git` directory and an explicitly reviewed access contract.
Linked worktrees are not permitted. `.gitignore` prevents accidental staging;
it does not prevent an agent or process from reading or modifying local files.
