# TI3-A INTEGRATION + TI3-B SOLUTAL INCREMENTAL ABLATION
#
# Fechamento canônico de TI3-A seguido, somente se integração/CI PASS,
# de uma única comparação multimodal controlada.
#
# Objetivo TI3-B:
# testar se RELATIVE_SOLUTE_FIELD acrescenta informação discriminativa
# ao baseline LBP/RF estrutural.
#
# NÃO executar CNN.
# NÃO executar FINAL_TEST.
# NÃO fazer tuning.
# NÃO alterar weak labels.
# NÃO alterar split.
# NÃO reexecutar baseline estrutural.
# CONVERGÊNCIA OBRIGATÓRIA.

Repositório:
snbi-dendritic-fragmentation-ml

Branch TI3-A atual:
feat/ti3-canonical-dataset-baseline

HEAD TI3-A esperado:
cab4fcd6f2d1fb70027cc6abff2590fae3d7c64b

============================================================
1. ESTADO CANÔNICO TI3-A
============================================================

TI3_GOV_COMPAT=PASS

C0R1=PASS
C0R1_CI=PASS

C1=PASS
C1_CI=PASS

TI3_A=PASS

TI3_A_DATASET=PASS

TI3_A_SPLIT=
FROZEN_TEMPORAL_GROUPED

TI3_A_LEAKAGE_GUARDS=PASS

BASELINE_MODEL=LBP_RF

SCIENTIFIC_ML_RUNS=1

TRAIN:
34 samples
17 POSITIVE
17 BACKGROUND

TRAIN metrics:
balanced_accuracy=1.0
accuracy=1.0
precision=1.0
recall=1.0
F1=1.0

DEVELOPMENT:
16 samples
8 POSITIVE
8 BACKGROUND

DEVELOPMENT metrics:

balanced_accuracy=0.6875
accuracy=0.6875
precision=0.6153846153846154
recall=1.0
F1=0.7619047619047619

confusion:

TN=3
FP=5
FN=0
TP=8

Structural baseline configuration:

PATCH_SIDE=65
PATCH_RADIUS=32

LBP:
P=8
R=1
method=uniform
10 bins
range=(0,10)
density=True

RF:
n_estimators=100
random_state=42
remaining parameters=frozen sklearn defaults

PRIMARY_METRIC=
balanced_accuracy

============================================================
2. CLAIM SCOPE PRESERVED
============================================================

Target:

PUBLISHED_FRAGMENTATION_LOCATION_PRESENT

POSITIVE:
high-confidence published fragmentation location.

BACKGROUND:
BACKGROUND_CANDIDATE_NOT_PHYSICAL_ABSENCE.

Therefore:

false positive against the weak label
does NOT prove false physical fragmentation.

Preserve:

FORECASTING_AUTHORIZED=false

CAUSALITY_CLAIM_AUTHORIZED=false

EXTERNAL_GENERALIZATION_CLAIM=false

EXACT_ONSET_AVAILABLE=false

============================================================
3. FINAL TEST
============================================================

ML_FINAL_TEST=

SEALED_WITH_HISTORICAL_NON_ML_EXPOSURE

Samples:

3 POSITIVE
3 BACKGROUND

Current ML access:

opens=0
bytes=0

Do not open.

Do not inspect.

Do not extract feature.

Do not validate chroma/support using FINAL.

Do not execute any model on FINAL.

============================================================
PART I — INTEGRATE TI3-A
============================================================

4. PRE-MERGE AUDIT

Confirm:

- HEAD local =
  cab4fcd6f2d1fb70027cc6abff2590fae3d7c64b;

- remote branch equals local;

- worktree/index clean;

- C2 is evidence-only;

- C1 scientific freeze intact;

- no post-C1 scientific modifications;

- FINAL_TEST remains zero opens/bytes;

- latest historical CI SUCCESS;

- latest TI3 CI SUCCESS.

If any divergence:

STOP.

============================================================
5. PR TI3-A
============================================================

If no PR currently exists for:

feat/ti3-canonical-dataset-baseline

open a Draft PR against main.

The PR description must summarize:

- target resolution;
- weak-label semantics;
- 52 sites;
- governance migration;
- TI3-A split;
- LBP/RF baseline;
- TRAIN/DEV metrics;
- FINAL_TEST untouched;
- limitations.

Do not claim:

external generalization;
physical exhaustive recall;
forecasting;
causality;
solute benefit.

============================================================
6. PR CI
============================================================

Require all mandatory workflows SUCCESS.

No rerun unless a purely infrastructure-level transient is
explicitly authorized separately.

If PR CI fails:

STOP.

============================================================
7. MERGE TI3-A
============================================================

If:

- diff audited;
- PR CI fully green;
- C1/C2 relationship preserved;

this authorization permits:

mark Ready if required
and merge using merge commit.

Do not squash scientific/history commits.

Record:

TI3_A_MERGE_SHA.

============================================================
8. POST-MERGE CI
============================================================

Require post-merge:

deterministic-contracts=SUCCESS
scientific-synthetic-contracts=SUCCESS
ti3-synthetic-contracts=SUCCESS

If any fail:

STOP.

Do not start TI3-B.

============================================================
PART II — TI3-B
============================================================

Only if post-merge CI is completely green.

============================================================
9. NEW BRANCH
============================================================

Synchronize local main by fast-forward.

Create:

feat/ti3b-solutal-ablation

from exactly:

TI3_A_MERGE_SHA.

Do not reuse the TI3-A branch.

============================================================
10. SCIENTIFIC QUESTION
============================================================

TI3-B asks exactly:

“Does the registered relative solute-field modality
provide incremental discriminative information for
PUBLISHED_FRAGMENTATION_LOCATION_PRESENT beyond the
structural radiography under the same LBP/RF model?”

Nothing else.

============================================================
11. FROZEN REFERENCE
============================================================

The structural result is already consumed.

Reference:

STRUCTURAL_DEV_BALANCED_ACCURACY=0.6875

STRUCTURAL_DEV_CONFUSION=
TN3 FP5 FN0 TP8

Do NOT rerun structural LBP/RF.

Do NOT use DEV structural predictions to tune the
multimodal representation.

============================================================
12. MULTIMODAL INPUT
============================================================

Use the same samples, centers, patches and splits.

Structural:

ESM1 for bottom-up
ESM4 for top-down

Solutal relative field:

ESM2 paired with ESM1
ESM5 paired with ESM4

Use the identity mapping already certified by G2_SOLUTE.

No new registration.

No offset estimation.

No coordinate tuning.

============================================================
13. TRAIN / DEV SOLUTAL BUFFERS
============================================================

Authorized solutal ML inputs:

TRAIN:

ESM2:73
ESM2:146
ESM5:98

DEVELOPMENT:

ESM2:219
ESM5:197

Expected native I/O if each opened once:

5 buffers

9,734,526 bytes total.

FINAL solutal candidates:

ESM2:293
ESM5:295

must remain:

0 opens
0 bytes

for ML.

Historical non-ML exposure remains declared.

============================================================
14. SOLUTAL SEMANTICS
============================================================

ESM2 / ESM5 are:

RELATIVE_SOLUTE_FIELD

Do not call:

absolute Bi concentration;
temperature;
thermal field;
causal precursor measurement.

============================================================
15. SOLUTAL REPRESENTATION
============================================================

For this controlled ablation use the native luminance/Y
representation already supported by the project's multimodal
processing infrastructure.

This experiment evaluates the information contained in that
registered visual representation of the RELATIVE_SOLUTE_FIELD.

It does NOT certify that luminance is a complete quantitative
representation of physical solute concentration.

Do not inspect DEV to choose another color representation.

============================================================
16. MULTIMODAL FEATURE VECTOR
============================================================

Structural patch:

65x65
        ↓
LBP P8/R1/uniform
        ↓
10-bin normalized histogram

Solutal patch at exact corresponding coordinates:

65x65
        ↓
same LBP P8/R1/uniform
        ↓
10-bin normalized histogram

Concatenate in fixed order:

[STRUCTURAL_LBP_10,
 SOLUTAL_LBP_10]

Feature dimension:

20

No additional statistics.

No PCA.

No feature selection.

No scaling learned from DEV.

============================================================
17. MODEL
============================================================

Use exactly the same Random Forest contract:

n_estimators=100
random_state=42

all remaining parameters equal to TI3-A.

No tuning.

No class weighting change.

No threshold optimization.

Classification threshold remains sklearn default prediction rule.

============================================================
18. DATASET
============================================================

Use EXACTLY the same:

- 17+17 TRAIN;
- 8+8 DEVELOPMENT;
- same labels;
- same backgrounds;
- same annotation sites;
- same patch centers;
- same context groups.

Do not replace samples that fail solutal support.

If a TRAIN/DEV solutal patch cannot be validly materialized:

BLOCKED_SOLUTAL_SUPPORT

STOP.

Do not move coordinates.

Do not choose a substitute.

============================================================
19. ANTI-LEAKAGE
============================================================

Reuse all TI3-A guards.

Additionally require:

structural and solutal components of one sample
belong to the same split and same sample_id.

No modality from a FINAL sample may be opened.

============================================================
20. METRICS
============================================================

Primary:

balanced_accuracy

Secondary:

accuracy
precision
recall
F1
confusion matrix
TP FP TN FN

Also compute descriptively:

DELTA_DEV_BALANCED_ACCURACY =

MULTIMODAL_DEV_BALANCED_ACCURACY
-
0.6875

Do not invent statistical significance.

With 8 examples per class, metric granularity is coarse.

============================================================
21. DEVELOPMENT DECISION RULE
============================================================

Before pixels freeze:

If:

MULTIMODAL_DEV_BALANCED_ACCURACY
>
0.6875

then:

DEV_MODALITY_PREFERENCE=
STRUCTURAL_PLUS_RELATIVE_SOLUTE

If:

MULTIMODAL_DEV_BALANCED_ACCURACY
<=
0.6875

then:

DEV_MODALITY_PREFERENCE=
STRUCTURAL_ONLY

Tie favors the simpler structural model.

This is a DEVELOPMENT decision only.

It is not evidence of external generalization.

============================================================
22. IMPORTANT INTERPRETATION
============================================================

If multimodal improves:

allowed statement:

“The relative solute-field representation provided
incremental discriminative information on the internal
development set under the frozen LBP/RF protocol.”

Not allowed:

“solute causes fragmentation.”

Not allowed:

“the model predicts future fragmentation.”

If multimodal does not improve:

allowed statement:

“No incremental development-set benefit was observed
for the frozen solutal representation under this
LBP/RF protocol.”

Do not conclude:

“solute is physically irrelevant.”

============================================================
23. METHOD FREEZE
============================================================

Before solutal pixels:

create protocol/config/tests.

Run:

- data guard;
- phase scope;
- legacy tests;
- TI3 synthetic tests;
- multimodal synthetic tests.

Create scientific freeze commit B1.

Suggested message:

feat(ti3b): freeze solutal incremental ablation

Push.

Require complete CI green.

If CI fails:

STOP.

Zero solutal ML pixels.

============================================================
24. SCIENTIFIC EXECUTION
============================================================

After B1 + CI green:

execute exactly ONE multimodal TRAIN/DEV run.

SCIENTIFIC_TI3B_RUNS=1

No retry.

No alternate feature representation.

No alternate RF.

No alternate seed.

============================================================
25. FINAL_TEST
============================================================

Never open:

ESM1:293
ESM4:295
ESM2:293
ESM5:295

for ML in TI3-B.

FINAL_TEST must remain zero opens/bytes.

============================================================
26. EVIDENCE
============================================================

After the single run, write evidence only.

Record:

- exact I/O;
- feature dimension;
- parameters;
- TRAIN metrics;
- DEV metrics;
- confusion matrix;
- delta versus structural reference;
- development modality preference;
- limitations.

Any B2 commit must be evidence-only.

============================================================
27. NO CNN YET
============================================================

TI3-B does NOT authorize:

CNN;
deep learning;
transfer learning;
augmentation;
architecture search.

Reason:

TI3-B isolates modality contribution before changing
model family.

============================================================
28. TERMINAL STATES
============================================================

If multimodal execution completes:

TI3_B=PASS

SOLUTAL_ABLATION=COMPLETED

SCIENTIFIC_TI3B_RUNS=1

ML_FINAL_TEST_EXECUTED=false

FORECASTING_AUTHORIZED=false

CAUSALITY_CLAIM_AUTHORIZED=false

EXTERNAL_GENERALIZATION_CLAIM=false

TI3_C_READY_FOR_AUTHOR_DECISION=true

TI3_C_AUTHORIZED=false

MERGE_AUTHORIZED=false

CURRENT_AUTHORIZED_ACTIVITY=
NONE_AWAITING_AUTHOR_DECISION

PASS means experiment executed according to protocol,
not that solutal must improve performance.

============================================================
29. CONVERGENCE
============================================================

Do not:

- tune solutal representation;
- use U/V after seeing results;
- change LBP;
- change RF;
- change backgrounds;
- alter split;
- rerun structural baseline;
- rerun multimodal;
- open FINAL;
- begin CNN.

Exactly one multimodal experiment.

Then STOP.

============================================================
30. REPORT FINAL
============================================================

Report:

1. TI3-A PR;
2. TI3-A merge SHA;
3. post-merge CI;
4. TI3-B branch/base;
5. B1 freeze SHA;
6. B1 CI;
7. solutal buffers opened;
8. bytes;
9. FINAL structural opens/bytes;
10. FINAL solutal opens/bytes;
11. multimodal feature definition;
12. RF parameters;
13. TI3-B scientific runs;
14. TRAIN metrics;
15. DEV metrics;
16. DEV confusion matrix;
17. structural reference BA;
18. multimodal BA;
19. delta BA;
20. DEV_MODALITY_PREFERENCE;
21. limitations;
22. evidence commit SHA;
23. CI final;
24. worktree/index;
25. terminal state.

EXECUTE SOMENTE:
TI3-A INTEGRATION
+
UMA TI3-B SOLUTAL INCREMENTAL ABLATION.

NUNCA ABRA ML_FINAL_TEST.