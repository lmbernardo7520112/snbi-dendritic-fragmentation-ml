# Experimental data custody

Raw sources are immutable external research assets and are not stored in this
public repository. Locally authorized copies may be placed under `data/raw/`,
which is ignored by Git.

The canonical manifest identifies each source by logical ID, byte size, digest,
storage form, modality, and experimental condition. Verification reads bytes in
binary mode and does not extract frames or alter the source.

Absence of a local source produces an explicit verification failure; it never
causes a silent skip or a fabricated PASS.

