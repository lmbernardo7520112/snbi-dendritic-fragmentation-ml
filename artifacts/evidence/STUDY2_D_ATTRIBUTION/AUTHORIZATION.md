# STUDY2-D — CONTROLLED DATA-CENTRIC BRIDGE ATTRIBUTION
#
# Experimento-ponte pós-hoc para investigar quais mudanças
# data-centric podem explicar a diferença observada entre
# o Experimento 1 e o Estudo 2.
#
# NÃO É MODEL SEARCH.
# NÃO É TUNING.
# NÃO É TENTATIVA DE MELHORAR O GMBA FINAL.
# NÃO REABRIR TEST.
# NÃO USAR DEVELOPMENT.
#
# VARIÁVEL COMPUTACIONAL FIXA:
#
# LBP20 + RF_REFERENCE
# RandomForestClassifier(
#     n_estimators=100,
#     random_state=42,
#     demais parâmetros históricos
# )
#
# PERGUNTAS EXCLUSIVAS:
#
# Q1 — efeito do número/diversidade de grupos de treinamento;
# Q2 — efeito da densidade temporal dentro dos mesmos grupos;
# Q3 — efeito da ponderação group-aware.
#
# DDD + SDD
# + one-factor-at-a-time attribution
# + frozen historical model
# + fixed TRAIN-only group CV
# + deterministic subsets
# + no TEST/DEV access
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
STUDY2_B=PASS
STUDY2_C=PASS

STUDY2_C_METHOD=
GROUP_AWARE_MULTIMODAL_BENCHMARK

SELECTED_MODEL_FAMILY=
RF_REFERENCE

SELECTED_SUPERVISION_REGIME=
GOLD_PLUS_SILVER

STUDY2_C_TEST_GMBA=
0.8449139278495638

STUDY2_C_TEST_OBSERVATION_BA=
0.8525933757278337

STUDY2_C_TEST_STATE=
CONSUMED

O TEST de Study2-C é permanentemente consumido.

Study2-D NÃO altera:

- pipeline final;
- seleção de modelo;
- supervisão final;
- TEST;
- resultados Study2-C.

============================================================
2. INTEGRAR STUDY2-C
============================================================

Branch atual esperada:

feat/study2c-group-aware-benchmark

Checkpoint documental esperado:

c715df53d5dc08815235f010c07616deef7bbb4a

Freeze científico:

8c38384915807a15062782a4a189601f7c83c8c3

Confirmar:

- local = remote;
- index e tracked limpos;
- checkpoint evidence-only;
- CI final:
  9 jobs / 100 steps SUCCESS;
- TEST_STATE=CONSUMED;
- nenhuma ciência posterior ao freeze;
- caches locais autenticados;
- academic-deliverable-build/ preservado.

Criar Draft PR contra main.

Exigir CI verde.

Ready + merge commit.

NÃO squash.
NÃO rebase.

Registrar:

STUDY2_C_MERGE_SHA.

Exigir CI pós-merge verde.

Somente então iniciar Study2-D.

============================================================
3. NOVA BRANCH
============================================================

Fast-forward main.

Criar:

feat/study2d-data-centric-bridge

exatamente a partir de:

STUDY2_C_MERGE_SHA.

============================================================
4. NATUREZA DO STUDY2-D
============================================================

Study2-D é:

POST_HOC_CONTROLLED_ATTRIBUTION_ANALYSIS

e não:

CONFIRMATORY_TEST
MODEL_SELECTION
MODEL_IMPROVEMENT
HYPERPARAMETER_SEARCH.

Objetivo:

investigar mecanismos plausíveis da melhoria observada
entre o pequeno Experimento 1 e o corpus expandido.

============================================================
5. PERGUNTAS
============================================================

Q1 — GROUP DIVERSITY

Mantendo modelo, features, folds, métrica,
densidade por grupo e classes constantes:

o que acontece quando cresce o número
de sites/tracks distintos usados no treino?

Q2 — TEMPORAL DENSITY

Mantendo exatamente os mesmos grupos:

o que acontece quando fornecemos
1, 3, 5 ou todas as observações temporais
de cada grupo?

Q3 — GROUP WEIGHTING

Mantendo corpus, grupos e observações idênticos:

o que acontece quando cada observação pesa igualmente

versus

quando cada grupo possui peso total 1?

============================================================
6. DADOS PERMITIDOS
============================================================

Usar EXCLUSIVAMENTE o split TRAIN
já congelado no Study2-C.

Esperado:

32 positive site groups
32 background track groups.

TRAIN GOLD rows historicamente:

3858

TRAIN BG rows historicamente:

7049

Total histórico:

10907 rows.

NÃO usar:

DEV positive groups
DEV background groups
TEST positive groups
TEST background groups.

============================================================
7. SUPERVISÃO
============================================================

Usar somente:

GOLD positive observations

+
BACKGROUND_CANDIDATE observations.

SILVER:

PROIBIDO em Study2-D.

Razão:

seu efeito já foi isolado em Study2-C
e foi pequeno.

UNLABELED:

PROIBIDO.

============================================================
8. INPUT
============================================================

Usar exatamente:

STRUCTURAL_Y
+
RELATIVE_SOLUTE_FIELD_Y

patch 65×65.

Classical representation:

LBP structural:
P=8
R=1
method=uniform
10 bins
range=(0,10)
density=True

LBP solutal:
mesmo contrato.

Concatenação:

20 features.

Nenhuma nova feature.

============================================================
9. MODELO FIXO
============================================================

Único modelo autorizado:

RF_REFERENCE.

RandomForestClassifier:

n_estimators=100
random_state=42

todos os demais 19 parâmetros exatamente
iguais aos registrados no Study2-C.

NÃO executar:

RF_TUNED
LogisticRegression
SVM
CNN
XGBoost
LightGBM
MLP.

============================================================
10. NENHUM HYPERPARAMETER SEARCH
============================================================

Não alterar:

n_estimators
max_depth
min_samples_leaf
max_features
class_weight
seed
threshold.

Study2-D não escolhe modelo.

============================================================
11. FOLDS
============================================================

Reutilizar EXATAMENTE os quatro folds TRAIN-only
congelados no Study2-C.

Hash esperado do contrato histórico:

cv_fold_by_group_sha256 =
85edac3d7da06994d7b16c4fa50e2aeb806abd7743a1d471842f54fdcf049ef2

Cada validation fold histórico contém por classe:

bottom_up = 6 groups
top_down = 2 groups.

Cada training fold contém por classe:

bottom_up = 18 groups
top_down = 6 groups.

Total training pool/fold:

24 positive groups
+
24 BG groups.

Não criar novos folds.

============================================================
12. DEV/TEST FIREWALL
============================================================

Obrigatório:

DEV_GROUPS_READ=0
TEST_GROUPS_READ=0

DEV_ROWS_READ=0
TEST_ROWS_READ=0

TEST_CACHE_ROWS_READ=0

TEST_FEATURES_COMPUTED=0

Nenhum resultado Study2-D pode usar
DEV ou TEST do Study2-C.

============================================================
13. FONTES DE PIXELS
============================================================

Reutilizar somente os containers/caches
já materializados.

Não abrir MP4.

Não rodar FFmpeg.

Não abrir ESM1..6.

Esperado:

EXPERIMENTAL_SOURCE_OPENS=0
FFMPEG_RUNS=0.

Positive GOLD:

container Study2-B.

Background TRAIN:

cache TRAIN/DEV de Study2-C,
mas ler somente rows explicitamente TRAIN.

A abertura do container físico não constitui
autorização para acessar rows DEV.

Instrumentar row-level access.

============================================================
14. FEATURES
============================================================

Extrair LBP20 uma única vez
para todas as rows TRAIN autorizadas.

Manter em memória durante Study2-D.

Pode persistir um cache compacto local ignorado
se necessário, desde que:

- somente TRAIN;
- 20 features;
- hash;
- schema;
- row IDs;
- nenhum DEV/TEST.

Não é necessário se RAM permitir.

============================================================
PART A — GROUP DIVERSITY ATTRIBUTION
============================================================

15. OBJETIVO A
============================================================

Isolar principalmente o efeito de aumentar
o número de GRUPOS distintos.

Para minimizar o efeito de densidade temporal:

usar exatamente UMA observação por grupo.

============================================================
16. OBSERVAÇÃO REPRESENTATIVA
============================================================

Para cada positive site group:

selecionar deterministicamente a observação GOLD
temporalmente mediana daquele grupo
dentro do TRAIN autorizado.

Para cada background track:

selecionar deterministicamente a observação
temporalmente mediana daquele track
dentro do TRAIN autorizado.

Definição:

ordenar por frame_index.

Se n ímpar:
índice central.

Se n par:
usar a observação anterior ao meio,
regra congelada.

Não selecionar por:

feature
intensity
model score
distance
performance.

============================================================
17. GROUP COUNT LEVELS
============================================================

Por classe, testar:

K = 4
K = 8
K = 12
K = 17
K = 24

onde K significa:

K positive groups
+
K background groups

dentro do training side daquele CV fold.

K=17 é incluído como ponte narrativa
para a escala numérica do TRAIN do Experimento 1.

IMPORTANTE:

17 groups/class no Study2-D
NÃO equivale cientificamente aos
17 samples/class do Experimento 1.

Registrar essa diferença.

============================================================
18. ACQUISITION QUOTAS
============================================================

Para cada K manter aproximadamente
a proporção histórica 3:1 do training pool:

K=4:
bottom_up=3
top_down=1

K=8:
bottom_up=6
top_down=2

K=12:
bottom_up=9
top_down=3

K=17:
bottom_up=13
top_down=4

K=24:
bottom_up=18
top_down=6.

Aplicar a mesma quota
para positive e background.

============================================================
19. SUBSET REPLICATES
============================================================

Para K < 24:

usar cinco rankings determinísticos independentes:

STUDY2D_GROUP_R1
STUDY2D_GROUP_R2
STUDY2D_GROUP_R3
STUDY2D_GROUP_R4
STUDY2D_GROUP_R5

Ranking por:

SHA256(
salt
|
fold_id
|
class
|
acquisition
|
group_id
)

Nenhum pixel no ranking.

Cada replicate deve ser nested:

os primeiros 4 grupos
⊂ primeiros 8
⊂ primeiros 12
...

quando quotas permitirem.

K=24 usa todos os training groups
e deve ser executado somente uma vez por fold.

============================================================
20. FITS DA CURVA DE GRUPOS
============================================================

Por fold:

K=4:
5 replicates

K=8:
5 replicates

K=12:
5 replicates

K=17:
5 replicates

K=24:
1 execução.

Total esperado:

4 folds ×
(5+5+5+5+1)
=
84 distinct RF fits.

Nenhum retry.

============================================================
21. EVALUATION DO PART A
============================================================

Cada fit é avaliado no validation side
HISTÓRICO daquele mesmo CV fold.

Validation usa:

TODAS as GOLD observations
dos positive groups do fold

+
TODAS as BG observations
dos BG groups do fold.

Evaluation set permanece idêntico
entre K e replicates daquele fold.

Primary:

GROUP_MACRO_BALANCED_ACCURACY.

============================================================
22. RESULTADOS PART A
============================================================

Para cada K reportar:

mean GMBA
median GMBA
standard deviation descritivo
min
max
n_fits

por aquisição
e global.

Comparações principais:

Δ24_minus_4
Δ24_minus_8
Δ24_minus_12
Δ24_minus_17.

Para K<24:

parear cada replicate com
o K=24 do mesmo fold.

Reportar:

mean paired delta
median paired delta
positive_delta_count
zero_delta_count
negative_delta_count.

Não calcular p-value.

============================================================
23. GROUP DIVERSITY DESCRIPTOR
============================================================

Pré-definir:

CONSISTENT_POSITIVE

se:

mean Δ24_minus_17 > 0
e
pelo menos 15/20 paired deltas > 0.

MIXED_POSITIVE

se:

mean delta > 0
mas menos de 15/20 são positivos.

NON_POSITIVE

se:

mean delta <= 0.

É um descriptor interno,
não teste de significância.

============================================================
PART B — TEMPORAL DENSITY ATTRIBUTION
============================================================

24. OBJETIVO B
============================================================

Isolar o efeito de múltiplas observações temporais
mantendo os GRUPOS fixos.

Usar sempre:

K=24 positive groups
+
K=24 background groups

por training fold.

============================================================
25. DENSITY LEVELS
============================================================

Por grupo testar:

D1 = 1 observation

D3 = até 3 observations

D5 = até 5 observations

DALL = todas as observations TRAIN autorizadas
do grupo.

============================================================
26. TEMPORAL SAMPLING
============================================================

D1:

mediana temporal.

D3:

quantis temporais aproximados:
25%, 50%, 75%.

D5:

0%, 25%, 50%, 75%, 100%.

Selecionar nearest ranked observation.

Remover duplicatas.

Se grupo possuir menos observações que o nível:

usar todas as disponíveis.

Nunca duplicar uma row artificialmente.

Registrar:

effective_rows_per_group.

============================================================
27. WEIGHTS NO PART B
============================================================

Em TODOS os níveis D1/D3/D5/DALL:

usar GROUP_EQUAL weighting:

weight(row) =
1 /
n_selected_rows_of_that_group.

Assim o aumento de densidade
não aumenta o peso total do grupo.

============================================================
28. DENSITY FITS
============================================================

Por fold:

D1
D3
D5
DALL.

4 folds × 4 levels =
16 conceptual fits.

Entretanto:

D1 com K=24
já foi produzido no Part A.

Reusar exatamente esse resultado.

Não refitar.

Distinct new fits esperados:

12.

============================================================
29. EVALUATION PART B
============================================================

Validation side permanece exatamente igual
ao Part A:

todas as GOLD observations
+
todas as BG observations
dos held-out groups.

Primary:

GMBA.

Comparações:

D3-D1
D5-D1
DALL-D1
DALL-D5.

Reportar 4 paired fold deltas.

============================================================
30. TEMPORAL DENSITY DESCRIPTOR
============================================================

CONSISTENT_POSITIVE

se:

mean(DALL-D1) > 0

e

pelo menos 3/4 folds têm delta > 0.

MIXED_POSITIVE

se mean >0 mas menos de3/4.

NON_POSITIVE

se mean <=0.

============================================================
PART C — GROUP WEIGHTING ATTRIBUTION
============================================================

31. OBJETIVO C
============================================================

Isolar o efeito da ponderação.

Fixar:

K=24 groups/class

DENSITY=DALL

mesmos training rows.

Comparar apenas:

OBSERVATION_EQUAL

versus

GROUP_EQUAL.

============================================================
32. OBSERVATION_EQUAL
============================================================

Cada row recebe:

sample_weight=1.

Um grupo com 200 rows pesa aproximadamente
200 vezes um grupo com 1 row.

============================================================
33. GROUP_EQUAL
============================================================

Cada row recebe:

1 / nrows_do_group.

Peso total:

1 por group.

Este é o esquema Study2-C.

============================================================
34. WEIGHTING FITS
============================================================

GROUP_EQUAL + DALL
já existe no Part B.

Reusar.

Executar somente:

OBSERVATION_EQUAL

para os quatro folds.

Distinct new fits:

4.

============================================================
35. WEIGHTING EVALUATION
============================================================

Mesmo validation set.

Mesmo GMBA.

Calcular:

GROUP_EQUAL_MINUS_OBSERVATION_EQUAL

por fold.

Reportar:

mean delta
median delta
4 fold deltas.

Descriptor:

CONSISTENT_GROUP_EQUAL_BENEFIT

se mean >0 e >=3/4 deltas >0.

MIXED_GROUP_EQUAL_BENEFIT

se mean >0 e <3/4.

NO_GROUP_EQUAL_BENEFIT

se mean <=0.

============================================================
36. TOTAL FIT BUDGET
============================================================

Esperado:

Part A:
84 distinct fits

Part B:
12 additional distinct fits

Part C:
4 additional distinct fits

TOTAL DISTINCT RF FITS=
100.

Não executar fit extra.

Se implementação exigir número diferente:

explicar ANTES da ciência
e STOP para decisão autoral.

============================================================
37. MÉTRICA PRIMÁRIA
============================================================

Usar exatamente a definição Study2-C:

GROUP_MACRO_BALANCED_ACCURACY.

Positive group:

recall por site.

Negative group:

specificity por track.

GMBA =
0.5 *
(
mean_positive_site_recall
+
mean_background_track_specificity
).

============================================================
38. MÉTRICAS SECUNDÁRIAS
============================================================

Para cada condição também calcular:

observation balanced accuracy
accuracy
precision
recall
F1

positive-group macro recall

background-track macro specificity

per-acquisition GMBA.

Nenhuma secundária substitui a primária.

============================================================
39. NÃO USAR TEST
============================================================

O TEST Study2-C é apenas referência histórica textual:

STUDY2_C_TEST_GMBA=
0.8449139278495638

Não carregar:

TEST patches
TEST background cache
TEST features
TEST predictions

durante Study2-D.

============================================================
40. NÃO USAR DEV
============================================================

Study2-C DEV também permanece fora.

Razão:

Study2-D deve ser um diagnóstico inteiramente
contido no TRAIN original.

Isso mantém a atribuição independente das decisões
que já utilizaram DEV.

============================================================
41. EXPERIMENTO 1 — REFERÊNCIA HISTÓRICA
============================================================

Pode registrar textualmente:

Experiment1 TRAIN:
17 positive
17 background.

Experiment1 FINAL:
3 positive
3 background.

FINAL observation BA:
2/3.

Mas NÃO reexecutar Experimento 1.

Não abrir seus pixels.

Não recalcular métricas.

Não afirmar que:

K=17 Study2-D
=
Experiment1.

Chamar somente:

NUMERICAL_SCALE_BRIDGE.

============================================================
42. NÃO SOMAR EFEITOS
============================================================

Os efeitos podem interagir.

Portanto é proibido escrever:

"X% da melhora veio de grupos,
Y% da densidade,
Z% da ponderação"

como decomposição aditiva.

Study2-D mede:

efeitos condicionais
sob pontos específicos do protocolo.

============================================================
43. CLAIMS AUTORIZADOS
============================================================

Se resultados suportarem:

"under a fixed RF/LBP and group-aware CV protocol,
increasing training-group diversity was associated
with / contributed to improved internal CV performance."

"greater temporal density within fixed groups
provided / did not provide additional benefit."

"group-equal weighting provided / did not provide
additional benefit under the fixed dense setting."

Em português no relatório final:

"mantidos modelo, representação, folds e métrica,
a ampliação sistemática de [...] produziu ..."

============================================================
44. CLAIMS PROIBIDOS
============================================================

Não afirmar:

- causalidade física;
- generalização externa;
- decomposição percentual exata da melhoria;
- novos experimentos independentes;
- que Study2-D prova sozinho a causa total
  da diferença Experimento1→Study2;
- significância estatística universal.

============================================================
45. SEM SILVER
============================================================

SILVER não participa.

Study2-C já mediu:

GMBA GOLD:
0.8759021928689068

GMBA GOLD+SILVER:
0.8775115148991031

delta:
0.0016093220301962585.

Esse efeito pode ser citado textualmente,
mas não reexecutado.

============================================================
46. SEM TUNING
============================================================

Nenhuma condição Study2-D pode gerar:

- nova seed;
- novo RF;
- novo threshold;
- nova feature;
- nova escolha de background;
- novo fold;
- novo split.

============================================================
47. BACKGROUND GROUPS
============================================================

Usar exatamente os 32 TRAIN background tracks
já escolhidos no Study2-C.

Não selecionar novos tracks
dos 171 reserves.

============================================================
48. POSITIVE GROUPS
============================================================

Usar exatamente os 32 TRAIN positive sites
já congelados no Study2-C.

Não adicionar DEV sites.

Não adicionar TEST sites.

============================================================
49. PRE-FIT FREEZE
============================================================

Antes de qualquer fit experimental,
congelar:

- input groups;
- allowed rows;
- four historical folds;
- representative-row rule;
- K levels;
- acquisition quotas;
- five replicate salts;
- density levels;
- temporal sampling;
- weighting schemes;
- RF parameters;
- feature parameters;
- metrics;
- descriptors;
- fit budget;
- claim scope.

Criar:

STUDY2_D_PROTOCOL.md
STUDY2_D_ATTRIBUTION_DESIGN.json
STUDY2_D_FIT_BUDGET.json
STUDY2_D_CLAIM_SCOPE.md

Commit sugerido:

feat(study2d): freeze data-centric bridge attribution

Registrar:

STUDY2_D_METHOD_FREEZE_SHA.

============================================================
50. SYNTHETIC TESTS
============================================================

Antes do freeze testar:

- exact TRAIN group allowlist;
- DEV rejection;
- TEST rejection;
- fold hash;
- no group crossing;
- deterministic median row;
- deterministic quantiles;
- nested K subsets;
- acquisition quotas;
- replicate salts;
- no pixel ranking;
- group equal weights sum=1;
- observation equal weights;
- GMBA implementation identical to Study2-C;
- RF params exact;
- LBP params exact;
- distinct fit counter;
- fit budget=100;
- no silver;
- no model search;
- no MP4 access.

============================================================
51. CI PRÉ-FIT
============================================================

Push method freeze.

Exigir:

todos os historical workflows
+
Study2-A
+
Study2-B
+
Study2-C
+
Study2-D synthetic contracts

SUCCESS.

Se qualquer falha:

STOP.

SCIENTIFIC_STUDY2D_RUNS=0.

============================================================
52. SCIENTIFIC EXECUTION
============================================================

Depois de freeze + CI verde:

executar UMA CLI científica.

Essa única CLI pode realizar
os 100 fits previamente autorizados.

SCIENTIFIC_STUDY2D_RUNS=1.

No retry.

No adaptive branching.

Todas as condições já devem existir
no protocol antes da execução.

============================================================
53. EXECUTION ORDER
============================================================

Executar deterministicamente:

A)
Group Diversity

B)
Temporal Density

C)
Group Weighting

mas nenhuma decisão do A
pode alterar B ou C.

Os três desenhos são pré-congelados.

============================================================
54. OUTPUTS
============================================================

Persistir textualmente:

GROUP_DIVERSITY_RESULTS.json

TEMPORAL_DENSITY_RESULTS.json

GROUP_WEIGHTING_RESULTS.json

ATTRIBUTION_SUMMARY.json

RESULTS_TABLES.md

EXECUTION_REPORT.md

terminal-state.json

e hashes/evidence usuais.

Não persistir modelo RF.

Não persistir TEST data.

============================================================
55. ATTRIBUTION SUMMARY
============================================================

Produzir quadro:

FACTOR:
GROUP_DIVERSITY

CONTRAST:
K24 vs K17
K24 vs K8
K24 vs K4

MEAN_GMBA_DELTA
MEDIAN_DELTA
PAIRWISE_POSITIVE_COUNT
DESCRIPTOR.

FACTOR:
TEMPORAL_DENSITY

CONTRAST:
ALL vs 1
ALL vs 5

MEAN_GMBA_DELTA
FOLD_DELTAS
DESCRIPTOR.

FACTOR:
GROUP_WEIGHTING

CONTRAST:
GROUP_EQUAL vs OBSERVATION_EQUAL

MEAN_GMBA_DELTA
FOLD_DELTAS
DESCRIPTOR.

============================================================
56. NARRATIVE BRIDGE TABLE
============================================================

Gerar tabela didática para o futuro relatório:

| Condição | O que muda | O que fica fixo | GMBA |

Incluindo pelo menos:

K4 / D1 / group-equal

K8 / D1 / group-equal

K12 / D1 / group-equal

K17 / D1 / group-equal

K24 / D1 / group-equal

K24 / D3 / group-equal

K24 / D5 / group-equal

K24 / DALL / group-equal

K24 / DALL / observation-equal.

Não inserir Study2-C TEST nessa mesma tabela
como se fosse diretamente comparável.

============================================================
57. INTERPRETAÇÃO OBRIGATÓRIA
============================================================

O relatório deverá responder em linguagem clara:

1. Aumentar a diversidade de grupos ajudou?
2. O benefício cresce de forma consistente?
3. O que acontece próximo da escala K=17?
4. Mais frames do mesmo site acrescentam informação?
5. Esse efeito satura?
6. Group weighting ajuda?
7. Qual dos três fatores apresenta evidência
   descritiva mais consistente?
8. O que ainda não pode ser atribuído causalmente?

============================================================
58. NÃO RANQUEAR COMO PERCENTUAIS CAUSAIS
============================================================

Pode dizer:

"o efeito mais consistente foi..."

se sustentado pelos contrastes.

Não dizer:

"72% da melhora foi causada por..."

Não há desenho fatorial completo suficiente
para essa decomposição.

============================================================
59. STORAGE
============================================================

Study2-D deve utilizar apenas caches existentes.

Nenhum vídeo.

Nenhum novo background patch.

Nenhum grande corpus novo.

Persistência esperada:

somente resultados textuais compactos.

============================================================
60. I/O TERMINAL
============================================================

Esperado:

ESM1_OPENS=0
ESM2_OPENS=0
ESM3_OPENS=0
ESM4_OPENS=0
ESM5_OPENS=0
ESM6_OPENS=0

FFMPEG_RUNS=0

DEV_ROWS_READ=0
TEST_ROWS_READ=0

TEST_FEATURES_COMPUTED=0

============================================================
61. PASS
============================================================

STUDY2_D=PASS significa:

todos os contrastes pré-registrados foram executados
sob o modelo e folds fixos.

Não depende do efeito ser positivo.

Se mais dados NÃO ajudarem:

isso é resultado científico válido.

============================================================
62. PÓS-RUN
============================================================

Depois da execução:

nenhum novo fit.

Somente evidence-only.

Criar checkpoint documental.

Não merge automaticamente.

============================================================
63. TERMINAL
============================================================

Emitir:

STUDY2_D=PASS

STUDY2_D_METHOD=
CONTROLLED_DATA_CENTRIC_BRIDGE_ATTRIBUTION

SCIENTIFIC_STUDY2D_RUNS=1

RF_MODEL=
RF_REFERENCE

FEATURES=
LBP20_MULTIMODAL

TRAIN_POSITIVE_GROUPS_AVAILABLE=32

TRAIN_BACKGROUND_GROUPS_AVAILABLE=32

CV_FOLDS=4

DISTINCT_RF_FITS=100

GROUP_DIVERSITY_DESCRIPTOR=<real>

GROUP_DIVERSITY_DELTA_K24_K17=<real>

GROUP_DIVERSITY_DELTA_K24_K4=<real>

TEMPORAL_DENSITY_DESCRIPTOR=<real>

TEMPORAL_DENSITY_DELTA_ALL_1=<real>

GROUP_WEIGHTING_DESCRIPTOR=<real>

GROUP_WEIGHTING_DELTA=<real>

DEV_GROUPS_READ=0
TEST_GROUPS_READ=0

DEV_ROWS_READ=0
TEST_ROWS_READ=0

TEST_STATE=UNCHANGED_CONSUMED

NEW_MODEL_SEARCH=false

MODEL_SELECTION_REOPENED=false

STUDY2_ATTRIBUTION_ANALYSIS_COMPLETE=true

SCIENTIFIC_PROGRAM_READY_FOR_FINAL_CLOSEOUT=true

CURRENT_AUTHORIZED_ACTIVITY=
NONE_AWAITING_AUTHOR_DECISION

============================================================
64. REPORT FINAL
============================================================

Informar:

1. Study2-C PR/merge;
2. merge SHA;
3. post-merge CI;
4. Study2-D branch;
5. TRAIN allowlist;
6. fold hash;
7. RF exact params;
8. LBP exact params;
9. representative-row rule;
10. K levels;
11. replicate salts;
12. density rules;
13. weighting rules;
14. fit budget;
15. freeze SHA;
16. CI pré-fit;
17. run command;
18. actual fit count;
19. group curve full table;
20. K24-K17 contrast;
21. K24-K4 contrast;
22. density table;
23. ALL-vs-1 contrast;
24. weighting contrast;
25. descriptors;
26. per-acquisition diagnostics;
27. narrative bridge table;
28. relation to Experiment1;
29. relation to Study2-C;
30. causal limitations;
31. DEV access confirmation;
32. TEST access confirmation;
33. source I/O confirmation;
34. runtime;
35. evidence checkpoint;
36. final CI;
37. Git state;
38. terminal state.

STOP.

NÃO EXECUTAR:
- novo modelo;
- augmentation;
- Hough;
- human review;
- self-supervised learning;
- novo TEST;
- nova CNN;
- novo hyperparameter search.