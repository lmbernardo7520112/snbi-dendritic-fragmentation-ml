# Study3 declaration of design before metadata exposure

The complete design originated in the author-approved Study3-CNN chat protocol
before the textual TRAIN metadata exposure recorded in
[the incident report](STUDY3_PRE_SCIENCE_INCIDENT.md). The subsequent recovery
decision preserves that scientific design and limits this phase to preparation,
freeze and CI. Experimental execution requires a separate author decision.

```text
DESIGN_ORIGIN=AUTHOR_APPROVED_CHAT_PROTOCOL_BEFORE_METADATA_EXPOSURE
DESIGN_CHANGED_AFTER_METADATA_EXPOSURE=false
METADATA_EXPOSURE_USED_TO_ADAPT_DESIGN=false
GROUP_SELECTION_CHANGED=false
FOLD_SELECTION_CHANGED=false
TEMPORAL_SELECTION_CHANGED=false
ARCHITECTURE_CHANGED=false
HYPERPARAMETERS_CHANGED=false
METRIC_CHANGED=false
FIT_BUDGET_CHANGED=false
CLAIM_SCOPE_CHANGED=false
```

The fixed population is historical Study2-C TRAIN GOLD/BACKGROUND only: 10,907
rows (3,858 GOLD and 7,049 BACKGROUND), 64 groups (32 positive and 32 background)
and four unchanged historical folds. The primary unit is the group trajectory.

The four RF_REFERENCE inputs are the lower temporal median observation,
trajectory mean, trajectory median and concatenated linear q25/q50/q75 LBP20
quantiles. Both CNNs use the same eight nearest real observations at positions
0, 1/7, 2/7, 3/7, 4/7, 5/7, 6/7 and 1, with ties to the lower rank and
deterministic repetitions for short trajectories. Architectures, seed 42,
30 epochs, Adam learning rate 0.001, weight decay zero and batch sizes 8/4
remain exactly as originally specified.

The acquisition majority control has no fit. The four coverage features and
fold-local StandardScaler/LogisticRegression remain fixed. Primary GMBA,
the seven paired contrasts, their descriptive decision rule, and the exact
16 RF + 4 CNN1D + 4 spatiotemporal CNN + 4 metadata fits are unchanged.

Metadata authentication may verify identities, counts, historical folds,
logical locators and hashes. It cannot justify a new group selection, fold,
representation, architecture, hyperparameter, metric, fit or claim. No pixels,
real features or scientific fits are authorized in the current phase. No
scientific receipt or result artifacts may be created by this recovery.
