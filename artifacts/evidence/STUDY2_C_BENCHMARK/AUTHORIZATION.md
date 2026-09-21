# STUDY2-C — GROUP-AWARE MULTIMODAL MODEL BENCHMARK
#
# Benchmark controlado de famílias de ML sobre o
# corpus multimodal denso congelado em Study2-B.
#
# OBJETIVOS:
#
# 1. comparar Logistic Regression, SVM, Random Forest
#    e CNN v2;
#
# 2. selecionar UMA família usando DEVELOPMENT;
#
# 3. testar, somente para a família selecionada,
#    GOLD versus GOLD+SILVER;
#
# 4. congelar o pipeline vencedor;
#
# 5. avaliar uma única vez o TEST agrupado.
#
# NÃO alterar o corpus.
# NÃO melhorar labels.
# NÃO reexecutar Study2-A/B.
# NÃO fazer Hough.
# NÃO usar revisão humana.
# NÃO buscar accuracy por tentativa-e-erro.
#
# DDD + SDD
# + group-aware validation
# + train-only model selection
# + fixed development comparison
# + single final test
# + evidence-first
# + convergence.

Repositório:

/home/leonardomaximinobernardo/My_projects/snbi-dendritic-fragmentation-ml

============================================================
1. ESTADO CANÔNICO
============================================================

EXPERIMENT_1=
COMPLETE_WITH_FINAL_EVALUATION

STUDY2_A=PASS

STUDY2_A_METRIC_RECONCILIATION=PASS

STUDY2_B=PASS

STUDY2_B_METHOD=
DENSE_MULTIMODAL_LONGITUDINAL_CORPUS

SITE_FRAME_INPUT_RECORDS=27396

VALID_MULTIMODAL_PAIRS=16500

GOLD_VALID_PAIRS=5218

SILVER_VALID_PAIRS=3687

UNLABELED_VALID_PAIRS=7595

INVALID_MULTIMODAL_PAIRS=10896

UNIQUE_SITES_WITH_VALID_PAIRS=52

BACKGROUND_CANDIDATES=70844

BACKGROUND_TRACKS=223

HUMAN_REVIEW_USED=false

ML_RUNS=0

Study2-A e Study2-B são imutáveis.

============================================================
2. INTEGRAR STUDY2-B
============================================================

Branch atual esperada:

feat/study2b-dense-multimodal-corpus

HEAD documental esperado:

cf5a4b091db52c0fc2f4b532230ed32ee013a2f9

Confirmar:

- local = remote;
- worktree/index científico limpo;
- ciência Study2-B permanece no freeze;
- checkpoint posterior evidence-only;
- corpus container e ledgers locais conferem hashes;
- CI final 8 jobs / 90 steps SUCCESS.

Criar Draft PR para main.

Exigir CI verde.

Ready.

Merge por merge commit.

Não squash.

Não rebase.

Registrar:

STUDY2_B_MERGE_SHA.

Exigir CI pós-merge verde.

Somente então criar Study2-C.

============================================================
3. BRANCH
============================================================

Criar:

feat/study2c-group-aware-benchmark

exatamente a partir de:

STUDY2_B_MERGE_SHA.

============================================================
4. QUESTÃO CIENTÍFICA
============================================================

Responder:

"Com grupos temporais isolados e pesos por site,
qual família de modelo melhor discrimina
PUBLISHED_FRAGMENTATION_LOCATION_PRESENT
de BACKGROUND_CANDIDATE no corpus multimodal
válido?"

E secundariamente:

"A adição de AUTO_SILVER ao TRAIN melhora
o desenvolvimento da família selecionada?"

============================================================
5. DOMÍNIO DO CLAIM
============================================================

O benchmark utiliza somente os:

52 sites com suporte multimodal válido.

Não afirmar que eles representam todos os 87 sites.

Registrar permanentemente:

VALID_SUPPORT_SITE_DOMAIN_ONLY=true

Os 35 sites sem suporte continuam no corpus histórico
e NÃO são failures do modelo.

============================================================
6. INPUT PRIMÁRIO
============================================================

Usar multimodal:

channel 0 =
STRUCTURAL_Y

channel 1 =
RELATIVE_SOLUTE_FIELD_Y

patch:

2 × 65 × 65 uint8.

O container Study2-B é a fonte canônica
para pares positivos já materializados.

Não redecodificar vídeos para esses pares.

============================================================
7. POSITIVOS PRIMÁRIOS
============================================================

Para model-family benchmark:

usar somente:

SUPERVISION_TIER=GOLD

DIRECT_VALID.

Não usar SILVER inicialmente.

Não usar PRE_FIRST.

Não usar PERSISTENCE_EXPECTED.

============================================================
8. BACKGROUND
============================================================

Consumir:

background-pool.jsonl.

Não usar intensidade, textura ou modelo
para escolher tracks.

Primeiro selecionar GROUPS de background.

Depois materializar somente os patches dos tracks
selecionados.

============================================================
9. SPLIT UNIT
============================================================

POSITIVES:

GROUP_ID =
acquisition_id | site_id

BACKGROUNDS:

GROUP_ID =
background_track_id

Nenhum GROUP_ID pode cruzar splits.

Nenhum patch individual decide split.

============================================================
10. METADATA-ONLY SPLIT GATE
============================================================

ANTES de materializar qualquer background pixel:

verificar distribuição dos:

52 sites positivos válidos

esperado documentalmente:

bottom_up = 40
top_down = 12.

Contar background tracks disponíveis:

bottom_up
top_down.

Se houver pelo menos:

40 bottom_up tracks
12 top_down tracks

prosseguir.

Caso contrário:

STUDY2_C=
BLOCKED_BACKGROUND_GROUP_CAPACITY

STOP.

Não alterar cotas silenciosamente.

============================================================
11. BACKGROUND TRACK SELECTION
============================================================

Selecionar exatamente:

40 bottom_up background tracks
12 top_down background tracks

por ranking SHA-256 textual determinístico,
independente de pixels e desempenho.

Tracks restantes ficam:

UNUSED_BACKGROUND_RESERVE.

Não selecionar por:

intensity;
texture;
frame count;
model score;
distance beyond frozen admissibility.

============================================================
12. GROUP SPLIT
============================================================

Congelar:

BOTTOM_UP positive sites:

TRAIN 24
DEV 8
TEST 8

BOTTOM_UP background tracks:

TRAIN 24
DEV 8
TEST 8

TOP_DOWN positive sites:

TRAIN 8
DEV 2
TEST 2

TOP_DOWN background tracks:

TRAIN 8
DEV 2
TEST 2.

Totais:

TRAIN:
32 positive groups
32 background groups

DEV:
10 positive groups
10 background groups

TEST:
10 positive groups
10 background groups.

Alocação dentro de cada acquisition/class stratum:

SHA-256 deterministic ranking.

Nenhum pixel.

Nenhum resultado de modelo.

============================================================
13. TEST LOGICAL SEAL
============================================================

Depois do split:

TEST groups tornam-se:

LOGICALLY_SEALED_TEST.

Nenhum TEST row pode ser usado para:

fit;
scaler fit;
hyperparameter selection;
epoch selection;
feature selection;
model family selection;
silver decision.

Inputs já existem historicamente,
portanto NÃO chamar TEST de globally virgin.

Chamar:

GROUP_HELD_OUT_INTERNAL_TEST.

============================================================
14. TRAIN/DEV/TEST MANIFEST
============================================================

Congelar:

positive group IDs;
background track IDs;
all row IDs;
acquisition;
supervision tier;
frame IDs;
sample counts;
hashes.

Commit antes do primeiro fit.

============================================================
15. BACKGROUND MATERIALIZATION
============================================================

Depois do split freeze:

materializar somente candidates pertencentes
aos 52 background tracks selecionados.

Usar:

65×65 structural
+
65×65 relative-solute.

Mesmo mapping histórico.

Sem padding.

Sem shift.

Sem replacement.

Persistir container agregado uint8
ou reutilizar cache controlado.

Registrar hashes.

============================================================
16. GROUP-EQUAL TRAIN WEIGHTS
============================================================

Para cada training positive site:

sample_weight(row) =
1 / number_of_training_rows_in_that_site.

Para cada training background track:

sample_weight(row) =
1 / number_of_training_rows_in_that_track.

Assim:

peso total de cada group = 1.

Como há números iguais de positive/background groups:

peso total por classe também será igual.

Não usar class_weight adicional
na configuração principal.

============================================================
17. PRIMARY METRIC
============================================================

Definir:

GROUP_MACRO_BALANCED_ACCURACY.

Para positive groups:

site_recall(g) =
mean(predicted_label == 1)
entre GOLD observations do site g.

POSITIVE_GROUP_MACRO_RECALL =
mean(site_recall).

Para background groups:

track_specificity(h) =
mean(predicted_label == 0)
entre observations do track h.

NEGATIVE_GROUP_MACRO_SPECIFICITY =
mean(track_specificity).

PRIMARY:

GMBA =
0.5 *
(
 POSITIVE_GROUP_MACRO_RECALL
 +
 NEGATIVE_GROUP_MACRO_SPECIFICITY
).

============================================================
18. SECONDARY METRICS
============================================================

Também calcular:

observation balanced_accuracy
accuracy
precision
recall
F1
confusion matrix

positive-group macro recall

background-track macro specificity

majority-vote group balanced accuracy

per-acquisition GMBA.

Não usar métricas secundárias
para substituir retrospectivamente a primária.

============================================================
19. CLASSICAL FEATURE REPRESENTATION
============================================================

Para:

Logistic Regression
SVM
Random Forest

usar exatamente a representação curricular
comparável ao Experimento 1:

STRUCTURAL LBP:

P=8
R=1
method=uniform
10 bins
range=(0,10)
density=True

SOLUTAL LBP:

mesmo contrato.

Concatenação:

20 features.

Não adicionar:

HOG;
SIFT;
ORB;
PCA;
new texture stats.

============================================================
20. LOGISTIC REGRESSION
============================================================

Pipeline:

StandardScaler
+
LogisticRegression

random_state=42
max_iter suficiente para convergência,
congelado antes da execução.

Train-only grid:

C ∈ {0.1, 1, 10}

penalty = L2.

Nenhum outro search.

============================================================
21. SVM
============================================================

Pipeline:

StandardScaler
+
SVC

kernel=RBF

probability=false.

Train-only grid:

C ∈ {0.1, 1, 10}

gamma ∈ {
"scale",
0.01,
0.1
}

Nenhum outro kernel.

Nenhum polynomial SVM.

Nenhum probability calibration.

============================================================
22. RANDOM FOREST REFERENCE
============================================================

RF_REFERENCE deve reproduzir:

RandomForestClassifier(
 n_estimators=100,
 random_state=42
)

demais defaults históricos.

Não tuning.

Isso mede o efeito do NOVO CORPUS
mantendo o antigo algoritmo.

============================================================
23. RANDOM FOREST TUNED
============================================================

RF_TUNED permitido com espaço restrito:

n_estimators ∈ {100, 300}

max_depth ∈ {None, 8}

min_samples_leaf ∈ {1, 3}

max_features = "sqrt"

random_state=42

Demais parâmetros congelados.

Seleção somente via TRAIN group CV.

============================================================
24. TRAIN-ONLY GROUP CV
============================================================

Para tuning clássico:

usar 4 folds determinísticos.

Cada fold TRAIN deve preservar grupos inteiros
e, quando matematicamente possível:

bottom_up positive
top_down positive
bottom_up background
top_down background.

Nenhuma observação do mesmo group
aparece em dois folds simultaneamente.

PRIMARY CV metric:

GROUP_MACRO_BALANCED_ACCURACY.

Selecionar hiperparâmetros apenas por média dos 4 folds.

Tie:

menor complexidade conforme regra congelada.

============================================================
25. CNN V2
============================================================

Implementar exatamente:

Input:
2 × 65 × 65

Conv2d(
 in_channels=2,
 out_channels=16,
 kernel_size=3,
 padding=1
)

ReLU

MaxPool2d(2,2)

Conv2d(
 in_channels=16,
 out_channels=32,
 kernel_size=3,
 padding=1
)

ReLU

MaxPool2d(2,2)

AdaptiveAvgPool2d((1,1))

Flatten

Linear(32,2)

Esperado:

PARAMETER_COUNT=5010.

Se diferente:

BLOCKED_ARCHITECTURE_DIVERGENCE.

============================================================
26. CNN NORMALIZATION
============================================================

uint8 → float32 / 255.0

Não:

global dataset normalization;
DEV statistics;
TEST statistics;
CLAHE;
Canny;
histogram equalization.

============================================================
27. CNN TRAINING
============================================================

Seeds:

Python=42
NumPy=42
Torch=42.

CPU.

deterministic algorithms.

num_workers=0.

batch_size=32.

epochs=20.

optimizer:

Adam(
 lr=0.001,
 weight_decay=0
)

loss:

CrossEntropyLoss(reduction="none")

Aplicar sample weight de group-equal contribution.

Por batch:

weighted_loss =
sum(loss_i * weight_i)
/
sum(weight_i).

Sem scheduler.

Sem early stopping.

Sem epoch selection pelo DEV.

Sem augmentation nesta comparação principal.

============================================================
28. CNN INTERPRETATION
============================================================

Essa CNN é um NOVO modelo para um NOVO corpus.

Não chamar:

retry da CNN do Experimento 1.

Comparação histórica permitida:

CNN1:
170 parameters / sparse dataset.

CNN2:
5010 parameters / dense group-aware corpus.

Não inferir que qualquer diferença
seja exclusivamente causada por arquitetura,
pois dataset também mudou.

============================================================
29. MODEL BENCHMARK
============================================================

Treinar exatamente:

LOGISTIC_REGRESSION

SVM_RBF

RF_REFERENCE

RF_TUNED

CNN_V2

em TRAIN GOLD + TRAIN background.

Cada modelo:

um desenvolvimento científico após seus
train-only hyperparameter choices.

Não repetir seed.

============================================================
30. DEV EVALUATION
============================================================

Avaliar cada modelo exatamente uma vez
em:

DEV GOLD
+
DEV background.

Não incluir SILVER no DEV target.

Calcular primary e secondary metrics.

============================================================
31. MODEL FAMILY SELECTION
============================================================

PRIMARY:

DEV GROUP_MACRO_BALANCED_ACCURACY.

Maior valor vence.

Em empate numérico exato:

1. maior DEV observation balanced accuracy;

se ainda empate:

2. ordem de simplicidade congelada:

LOGISTIC_REGRESSION
SVM_RBF
RF_REFERENCE
RF_TUNED
CNN_V2.

Registrar:

SELECTED_MODEL_FAMILY.

============================================================
32. NÃO REABRIR MODEL SEARCH
============================================================

Depois da seleção:

não tentar:

novo SVM;
novo RF;
CNN maior;
CNN menor;
nova seed;
novo LR;
nova epoch count;
XGBoost;
LightGBM;
ResNet;
ViT.

MODEL_FAMILY_SELECTION torna-se fechada.

============================================================
33. SILVER ABLATION
============================================================

Somente para:

SELECTED_MODEL_FAMILY.

Comparar duas configurações:

A:
TRAIN GOLD + background

B:
TRAIN GOLD + SILVER + background.

SILVER é positivo somente no TRAIN B.

DEV continua:

GOLD + background.

Não avaliar silver como ground truth DEV.

============================================================
34. SILVER GROUP WEIGHTING
============================================================

Em GOLD+SILVER:

para cada site positivo:

todas as observações supervisionadas daquele site,
GOLD ou SILVER,

compartilham peso total 1:

weight =
1 /
(number_gold + number_silver)
daquele site.

Não atribuir peso arbitrário 0.5 ao SILVER.

O tier permanece registrado para análise.

============================================================
35. SILVER DECISION
============================================================

Se:

GMBA_DEV(GOLD+SILVER)
>
GMBA_DEV(GOLD)

então:

SELECTED_SUPERVISION_REGIME=
GOLD_PLUS_SILVER

senão:

SELECTED_SUPERVISION_REGIME=
GOLD_ONLY.

Empate favorece GOLD_ONLY.

Nenhum tuning adicional.

============================================================
36. FINAL PIPELINE FREEZE
============================================================

Depois de selecionar:

MODEL_FAMILY
+
SUPERVISION_REGIME

congelar:

FINAL_STUDY2_PIPELINE.

Não abrir TEST antes desse freeze.

============================================================
37. FINAL TRAINING
============================================================

Combinar:

TRAIN + DEV groups.

Nunca misturar TEST.

Usar hiperparâmetros já escolhidos.

Se supervision regime:

GOLD_ONLY:
usar GOLD positivo.

GOLD_PLUS_SILVER:
usar GOLD + SILVER positivo.

Background:

TRAIN+DEV selected background tracks.

Aplicar mesmos group-equal weights.

Uma única fit final.

============================================================
38. TEST EVALUATION
============================================================

Depois do final-fit:

avaliar exatamente UMA vez:

10 positive TEST sites
+
10 TEST background tracks.

Positive evaluation:

GOLD observations somente.

Silver TEST não entra no target primário.

Registrar:

SCIENTIFIC_TEST_EVALUATIONS=1.

Após isso:

TEST=CONSUMED.

============================================================
39. TEST CLAIM
============================================================

Esse TEST é:

INTERNAL_GROUP_HELD_OUT_TEST

e não:

external experiment validation.

Todos os grupos pertencem às mesmas duas aquisições.

============================================================
40. PER-ACQUISITION METRICS
============================================================

Reportar separadamente:

bottom_up GMBA

top_down GMBA

mas não selecionar modelo novamente com esses resultados.

Especialmente registrar que top_down TEST
tem apenas:

2 positive sites
+
2 background tracks.

Interpretação deve ser altamente cautelosa.

============================================================
41. SPATIAL SUPPORT LIMITATION
============================================================

Registrar:

35/87 AUTO_GOLD sites não possuem
suporte multimodal válido.

O benchmark descreve apenas:

52 VALID_SUPPORT_SITES.

Não atribuir invalid-support sites
como erros do classificador.

============================================================
42. UNLABELED DATA
============================================================

7595 unlabeled valid pairs:

não usar no supervised benchmark.

Não tratar como negative.

Não usar para selecionar modelo.

Preservar para estudo posterior de:

self-supervised representation
/
encoder-decoder

sem autorização nesta fase.

============================================================
43. AUGMENTATION
============================================================

DATA_AUGMENTATION=NONE

neste benchmark.

Razão:

queremos primeiro medir o efeito do corpus denso
e da família do modelo.

Augmentation fisicamente restrita poderá ser
uma futura ablação somente se ainda justificada.

============================================================
44. STORAGE
============================================================

Não duplicar os 16500 patches positivos existentes.

Criar cache apenas dos backgrounds selecionados.

Respeitar:

MAX_PATCH_CACHE_BYTES=2GiB

MAX_TEMP_BYTES=256MiB

MIN_FREE_DISK_RESERVE=50GiB.

Persistir:

features clássicas
se desejado em formato agregado compacto.

Não persistir tensors CNN float32.

============================================================
45. PRE-FIT FREEZE
============================================================

Antes de qualquer fit científico, congelar:

- group split;
- selected background tracks;
- all row IDs;
- model list;
- classical grids;
- CNN architecture;
- CNN train config;
- weighting;
- primary metric;
- selection rule;
- silver ablation;
- final-test procedure.

Criar commit:

feat(study2c): freeze group-aware benchmark protocol

Registrar:

STUDY2_C_METHOD_FREEZE_SHA.

============================================================
46. CI PRÉ-FIT
============================================================

Executar:

historical jobs
+
Study2-A/B jobs
+
Study2-C synthetic contracts.

Exigir tudo verde.

Se falhar:

STOP.

Nenhum fit científico.

============================================================
47. EXECUTION BUDGET
============================================================

Permitir exatamente:

classical TRAIN-only CV fits
conforme grids congelados;

1 TRAIN fit por modelo para DEV;

1 GOLD+SILVER comparison
somente para selected family;

1 final TRAIN+DEV fit;

1 final TEST evaluation.

Distinguir:

hyperparameter CV fits

de:

scientific model comparisons.

Não chamar CV interno de retry.

============================================================
48. RESULTS
============================================================

Registrar para cada modelo:

train-only CV result
chosen hyperparameters
TRAIN metrics
DEV primary
DEV secondary
per-acquisition DEV metrics
sample/group counts
weights
runtime
memory if readily available.

Para final:

TEST primary
TEST secondary
per-acquisition TEST
confusion matrix
group-level details.

============================================================
49. PASS
============================================================

STUDY2_C=PASS significa:

benchmark executado conforme protocolo.

Não depende de:

CNN vencer;
accuracy melhorar;
RF vencer;
GMBA exceder Study1.

Um resultado inferior continua científico.

============================================================
50. TERMINAL
============================================================

Emitir:

STUDY2_C=PASS

STUDY2_C_METHOD=
GROUP_AWARE_MULTIMODAL_BENCHMARK

VALID_SUPPORT_SITES=52

SELECTED_BACKGROUND_TRACKS=52

TRAIN_POSITIVE_GROUPS=32
TRAIN_BACKGROUND_GROUPS=32

DEV_POSITIVE_GROUPS=10
DEV_BACKGROUND_GROUPS=10

TEST_POSITIVE_GROUPS=10
TEST_BACKGROUND_GROUPS=10

MODELS_EVALUATED=5

SELECTED_MODEL_FAMILY=<real>

SELECTED_SUPERVISION_REGIME=
<GOLD_ONLY/GOLD_PLUS_SILVER>

FINAL_STUDY2_PIPELINE=<real>

TEST_STATE=CONSUMED

SCIENTIFIC_TEST_EVALUATIONS=1

HUMAN_REVIEW_USED=false

AUGMENTATION_USED=false

EXTERNAL_GENERALIZATION_CLAIM=false

STUDY2_CLOSED=true

CURRENT_AUTHORIZED_ACTIVITY=
NONE_AWAITING_AUTHOR_DECISION

============================================================
51. REPORT FINAL
============================================================

Informar:

1. Study2-B PR/merge;
2. merge SHA;
3. post-merge CI;
4. Study2-C branch;
5. group distributions;
6. background capacity gate;
7. selected background tracks;
8. split hashes;
9. background materialization;
10. method-freeze SHA;
11. CI pré-fit;
12. group-equal weighting;
13. Logistic config/CV;
14. SVM config/CV;
15. RF_REFERENCE;
16. RF_TUNED;
17. CNN v2 architecture/parameter count;
18. CNN training;
19. TRAIN results;
20. DEV results by model;
21. primary metric comparison;
22. selected family;
23. silver ablation;
24. selected supervision regime;
25. final pipeline;
26. final fit;
27. TEST GMBA;
28. TEST standard metrics;
29. TEST group metrics;
30. per-acquisition TEST;
31. comparison with Study1, descriptively only;
32. spatial-support limitation;
33. claim scope;
34. runtime/storage;
35. evidence SHA;
36. final CI;
37. Git state;
38. terminal state.

STOP.

NÃO INICIAR NOVO MODEL SEARCH.
NÃO EXECUTAR AUGMENTATION STUDY.
NÃO INICIAR SELF-SUPERVISED STUDY.