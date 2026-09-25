# Study4 S4-B0A — final matching and pair-aware fold freeze

This document records the author decision
`/STUDY4-S4-B0A-FINAL-MATCHING-FOLD-FREEZE`, based on
`fbeee342e7eca3fa55dcbf485a897a5d10aece6a`. It freezes pure implementation
and synthetic verification only. S4-A1 remains PASS/CLOSED_CONSUMED.
Its recorded capacities of 17 bottom-up pairs and eight top-down pairs
are future acceptance requirements, not new calculations on the corpus.

No final real pair, group identity, selected frame or fold is disclosed here.
This phase does not authorize a real runner, metadata analysis, coverage
control, experimental payload access or model execution.

## Exact final matching objective

Solve each acquisition independently over eligible positive/background edges.
An edge exists only when both groups belong to that acquisition and share
at least eight valid, distinct frame indices. Its support is the full
cardinality of that intersection, before selecting eight observations.

The ordered objectives are:

1. Maximize the number of matched pairs.
2. Among maximum-cardinality solutions, maximize the sum of common-frame
   support over selected edges.
3. Among remaining ties, choose the lexicographically smallest sorted list
   of `(positive_group_id, background_group_id)` keys, using normal comparison
   of canonical strings.

This is a global optimization, not a greedy approximation. The stdlib-only
solver uses exact integer min-cost maximum flow. It augments until no path
remains, establishing maximum cardinality. Support weights dominate the sum
of all tie-break bits; descending bits correspond to ascending edge keys,
therefore maximizing those bits selects the lexicographically smallest
edge list at fixed cardinality and support. Python integers avoid floating
point rounding and overflow in these objectives. Residual reverse edges
allow prior assignments to be revised; a greedy choice cannot lock the result.

Future real cardinalities must be exactly 17 for
`bottom_up_anti_parallel`, eight for `top_down_parallel`, and 25 total.
Any discrepancy blocks the result without adapting the matching method.
Explicitly disabling this count requirement is for invented small fixtures;
it grants no real-corpus authority.

## Eight shared real frames

Intersect the two valid frame sets and sort the distinct indices. Require
at least eight shared frames. For k from 0 through 7, select the nearest
integer rank to `k*(n-1)/7`, with exact half ties resolved downward.
Integer quotient/remainder arithmetic determines ranks; no float decides
a selected observation. Although denominator seven cannot produce an exact
half tie for integer numerators, the rational-rounding helper preserves
and tests the general lower-tie rule.

Both members receive exactly the same eight distinct real frame indices.
No interpolation, padding, repeated observations or synthetic frames are
permitted. Support weights still count the entire valid intersection,
not merely those eight selected indices.

## Pair identity

Canonical bytes are exactly:

```text
b"STUDY4_PAIR_V1\0"
+ acquisition_id.encode("utf-8")
+ b"\0"
+ positive_group_id.encode("utf-8")
+ b"\0"
+ background_group_id.encode("utf-8")
```

The identifier is `S4P_` plus the full 64-character lowercase SHA-256
hex digest. Identity strings must be canonical and valid UTF-8; embedded
NULs are rejected because they would make this delimiter encoding ambiguous.
No normalization or truncation changes identities. Any duplicate pair hash
or collision in a ledger blocks validation.

## Four folds by acquisition

The indivisible assignment unit is the pair. Historical Study3 folds are
not reused. For each pair, calculate:

```text
fold_key = SHA256(b"STUDY4_FOLD_V1\0" + pair_id.encode("utf-8")).hexdigest()
```

Within each acquisition, sort by `(fold_key, pair_id)`, enumerate from zero,
and assign `fold = i % 4`. Reset the index for each acquisition. Both members
inherit that single fold; no group can appear in more than one pair or fold.

The expected future pair counts are:

| Acquisition | Fold 0 | Fold 1 | Fold 2 | Fold 3 |
| --- | ---: | ---: | ---: | ---: |
| Bottom-up | 5 | 4 | 4 | 4 |
| Top-down | 2 | 2 | 2 | 2 |
| Total | 7 | 6 | 6 | 6 |

Each pair contributes one positive and one background group to its fold.
These are consequences of the frozen assignment and expected cardinalities,
not observed assignments of real groups.

The author's S4-B0A decision supersedes the earlier P0 proposal to conditionally
reuse historical folds or use a global cursor. Those local proposal documents
remain preserved outside this seven-path commit. They do not override this
operational freeze or authorize coverage-control implementation.

## Pure implementation and ledger validation

[study4_matching.py](../../src/snbi_fragmentation/study4_matching.py) accepts
explicit in-memory synthetic or, only under a future author decision,
authenticated group projections. Each projection supplies acquisition, role
and distinct valid frames. File opening, data loading, model imports and
scientific fitting are outside this module. There is no real runner.

Public operations provide an exact edge optimizer, integer rank selection,
shared-frame selection, pair IDs, deterministic fold assignment, ledger
construction and validation. Validation rejects malformed schemas,
noncanonical identities, invalid roles/acquisitions/frames, group reuse,
hash inconsistencies/collisions, unequal or incorrect selected frames,
wrong folds/cardinality, and solutions that violate the frozen objectives.
Validation never silently fixes a submitted ledger.

## Synthetic validation and custody

[Tests](../../tests/test_study4_matching.py) use invented IDs, graphs and frame
sets only. They compare the optimizer against independent brute-force
enumeration, cover greedy counterexamples and all three objectives, and
exercise determinism, frame selection, identities, collisions, indivisible
pairs and synthetic 17+8 fold counts. Filesystem and scientific dependencies
are denied during pure calls.

The required local checks are the complete Study4 synthetic suite, Study3
governance regressions, phase scope, TI3 scope, repository-data policy and
whitespace. They are execution gates; this document does not predeclare
their outcomes. Failures stop without automatic repair or retry.

The linked-worktree data check uses the existing Study3 governance composition:
validate checkout identity, then apply the immutable repository-data
`audit_entries` policy to the entire real index. The legacy standalone-only
main remains unchanged and is required in standalone remote CI.

Only the seven author-listed paths may be staged and committed. The
pre-existing P0 documents and local S4-A controls remain unchanged and outside
the index. Historical workflows, Study3, HANDOFF and S4-A evidence are
unchanged. Remote CI must succeed at the exact freeze SHA after the authorized
fast-forward push; CI never authorizes real matching.

## Authority and remaining boundary

[Authority](../../configs/study4/authority.json) identifies this freeze phase
and retains all scientific access flags as false. Final real matching requires
a future explicit author decision. The
[matching contract](../../configs/study4/matching-contract.json) records the
operational rules above.

[evaluation-contract.json](../../configs/study4/evaluation-contract.json)
remains byte-identical. Its pending coverage-neutralization statistic and
threshold are not decided, implemented or executed in this phase.

```text
PHASE=S4_B0A_FINAL_MATCHING_FOLD_FREEZE
REAL_MATCHING_EXECUTED=false
PAIR_IDENTITIES_SELECTED=false
REAL_CORPUS_METADATA_READS=0
EXPERIMENTAL_BINARY_READS=0
FEATURE_EXTRACTIONS=0
FITS=0
COVERAGE_CONTROL_IMPLEMENTED=false
EVALUATION_CONTRACT_CHANGED=false
FUTURE_FINAL_MATCHING_REQUIRES_EXPLICIT_AUTHOR_DECISION=true
CURRENT_AUTHORIZED_ACTIVITY=NONE_AWAITING_AUTHOR_DECISION_AFTER_FREEZE_PUBLICATION
```
