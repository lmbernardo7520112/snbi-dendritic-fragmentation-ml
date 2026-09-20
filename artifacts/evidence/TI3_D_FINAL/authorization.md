# TI3-C INTEGRATION + TI3-D FINAL EVALUATION
#
# Avaliação final única do pipeline selecionado:
#
# STRUCTURAL_PLUS_RELATIVE_SOLUTE
#           +
# LBP
#           +
# RANDOM FOREST
#
# MODEL_FAMILY_SELECTION já está COMPLETE.
#
# Esta fase NÃO seleciona modelo.
# Esta fase NÃO faz tuning.
# Esta fase consome ML_FINAL_TEST uma única vez.
#
# Após a execução, nenhuma nova modelagem é autorizada.
#
# DDD + SDD + evidence-first
# + frozen-before-test
# + prediction-first evaluation
# + single-consumption holdout
# + fail-closed
# + convergence governance

Repositório:
snbi-dendritic-fragmentation-ml

Branch atual TI3-C:
feat/ti3c-minimal-multimodal-cnn

HEAD esperado:
a0364a25694d149cb9e5dcb217de2b241fac0702

============================================================
1. ESTADO CANÔNICO
============================================================

TI3_B_INTEGRATION=PASS

TI3_C=PASS

SCIENTIFIC_TI3C_RUNS=1

MODEL_FAMILY_SELECTION=COMPLETE

FINAL_MODEL_FAMILY_PREFERENCE=
MULTIMODAL_LBP_RF

TI3-A structural reference:

DEV_BALANCED_ACCURACY=0.6875

TI3-B multimodal LBP/RF:

DEV_BALANCED_ACCURACY=0.75

TN=4
FP=4
FN=0
TP=8

TI3-C minimal multimodal CNN:

DEV_BALANCED_ACCURACY=0.50

TN=0
FP=8
FN=0
TP=8

MODEL SELECTION:

MULTIMODAL_LBP_RF

é FINAL para este experimento.

Não poderá ser reaberta depois do FINAL_TEST.

============================================================
2. TARGET E CLAIM SCOPE
============================================================

TARGET=

PUBLISHED_FRAGMENTATION_LOCATION_PRESENT

POSITIVE=

high-confidence published fragmentation location.

BACKGROUND=

BACKGROUND_CANDIDATE_NOT_PHYSICAL_ABSENCE.

Preservar permanentemente:

CIRCLE_IS_FRAGMENT_MASK=false

EXACT_ONSET_AVAILABLE=false

FORECASTING_AUTHORIZED=false

CAUSALITY_CLAIM_AUTHORIZED=false

EXTERNAL_GENERALIZATION_CLAIM=false

SOLUTAL_INPUT_SEMANTICS=
RELATIVE_SOLUTE_FIELD

============================================================
3. FINAL TEST ATUAL
============================================================

ML_FINAL_TEST=

SEALED_WITH_HISTORICAL_NON_ML_EXPOSURE

Samples:

3 POSITIVE
3 BACKGROUND_CANDIDATE

Total:

6

Até esta autorização:

ML opens = 0
ML bytes = 0
features = NOT_MATERIALIZED
predictions = NOT_EVALUATED

Não alegar:

GLOBAL_VIRGIN_HOLDOUT.

============================================================
PART I — INTEGRAR TI3-C
============================================================

4. AUDITORIA PRÉ-MERGE

Confirmar:

- HEAD local:
  a0364a25694d149cb9e5dcb217de2b241fac0702

- remote branch no mesmo SHA;

- index limpo;

- worktree limpo;

- checkpoint de evidências posterior a C1-CNN;

- nenhuma alteração científica posterior a
  b2d8839ca2b6c6e5ddd2be1de3ff9589ada9a93c;

- SCIENTIFIC_TI3C_RUNS=1;

- retries=0;

- tuning=0;

- FINAL structural opens=0;

- FINAL solutal opens=0;

- CI final TI3-C completamente verde.

Se qualquer divergência:

STOP.

============================================================
5. PR TI3-C

Se não existir PR:

criar Draft PR:

feat/ti3c-minimal-multimodal-cnn
→
main

O corpo deve registrar:

- integração TI3-B;
- CNN mínima 170 parâmetros;
- único run;
- CNN TRAIN BA=0.50;
- CNN DEV BA=0.50;
- all-positive collapse;
- RF multimodal reference DEV BA=0.75;
- MODEL_FAMILY_SELECTION=COMPLETE;
- MULTIMODAL_LBP_RF selecionado;
- FINAL intocado;
- limitações.

Não afirmar:

“CNNs não funcionam.”

Formulação correta:

“a configuração CNN mínima congelada não apresentou
discriminação útil sob o protocolo interno executado.”

============================================================
6. MERGE TI3-C

Exigir PR CI completamente verde.

Se PASS:

Ready
+
merge por merge commit.

Não squash.

Não rebase.

Registrar:

TI3_C_MERGE_SHA.

============================================================
7. POST-MERGE CI

Exigir todos os jobs existentes SUCCESS:

- deterministic-contracts;
- scientific-synthetic-contracts;
- ti3-synthetic-contracts;
- ti3b-synthetic-contracts;
- ti3c-synthetic-contracts.

Se qualquer um falhar:

STOP.

Não iniciar avaliação final.

============================================================
PART II — TI3-D FINAL
============================================================

Somente se post-merge CI = PASS.

============================================================
8. NOVA BRANCH

Fast-forward local main.

Criar exatamente:

feat/ti3d-final-evaluation

a partir do:

TI3_C_MERGE_SHA.

============================================================
9. PERGUNTA FINAL

Esta fase responde somente:

“Qual é o desempenho do pipeline selecionado
MULTIMODAL_LBP_RF nos seis samples temporais
reservados do ML_FINAL_TEST?”

Nada mais.

Não testar:

- outra modalidade;
- CNN;
- structural-only RF;
- outro RF;
- outro threshold;
- outra seed;
- outro patch;
- outro feature extractor.

============================================================
10. PIPELINE FINAL CONGELADO

INPUT:

STRUCTURAL_LUMINANCE
+
RELATIVE_SOLUTE_FIELD_LUMINANCE

Patch:

65 × 65

Structural feature:

LBP
P=8
R=1
method=uniform

histogram:
10 bins
range=(0,10)
density=True

Solutal feature:

mesmo LBP e histograma.

Concatenação:

[
 STRUCTURAL_LBP_10,
 SOLUTAL_LBP_10
]

Feature dimension:

20

============================================================
11. MODELO FINAL CONGELADO

RandomForestClassifier:

n_estimators=100
random_state=42

Todos os demais parâmetros devem ser exatamente
os utilizados em TI3-B.

Não alterar:

criterion
max_depth
max_features
min_samples_split
min_samples_leaf
bootstrap
class_weight
ou qualquer outro parâmetro.

Nenhum threshold tuning.

Prediction:

sklearn predict() congelado.

============================================================
12. FINAL TRAINING POLICY
============================================================

Antes de qualquer pixel FINAL, congelar:

FINAL_TRAINING_SET=

TRAIN ∪ DEVELOPMENT

Total esperado:

50 samples

25 POSITIVE
25 BACKGROUND_CANDIDATE

Usar exatamente os mesmos:

- sample_ids;
- labels;
- centers;
- patches;
- context groups;
- structural sources;
- solutal sources;

de TI3-A/B/C.

Nenhum sample novo.

Nenhum sample excluído.

Nenhum background reselecionado.

============================================================
13. RAZÃO DO TRAIN+DEV

O DEVELOPMENT já foi usado exclusivamente para:

- modalidade;
- família de modelo.

Essas escolhas estão encerradas.

Portanto, antes do FINAL_TEST:

TRAIN e DEVELOPMENT tornam-se:

FINAL_TRAINING_SET.

Não haverá mais development evaluation
nem decisão baseada nesses 50 samples.

============================================================
14. CONFOUNDING PRESERVADO

Registrar antes da execução:

FINAL_TRAINING_SET por aquisição:

bottom_up_anti_parallel:

19 POSITIVE
8 BACKGROUND

top_down_parallel:

6 POSITIVE
17 BACKGROUND

Essa associação aquisição/classe permanece
uma limitação estrutural.

Não corrigir.

Não rebalancear por aquisição.

Não mudar weights.

Não trocar backgrounds.

============================================================
15. BUFFERS DE FINAL TRAINING

Para reconstruir as 50 features,
autoriza-se exatamente UMA leitura adicional de:

STRUCTURAL:

ESM1:73
ESM1:146
ESM1:219

ESM4:98
ESM4:197

SOLUTAL:

ESM2:73
ESM2:146
ESM2:219

ESM5:98
ESM5:197

Total esperado:

10 opens

19,469,052 bytes.

Nenhum outro TRAIN/DEV buffer.

============================================================
16. FINAL TEST BUFFERS

Depois do fit final, autoriza-se exatamente UMA abertura de:

STRUCTURAL FINAL:

ESM1:293
ESM4:295

SOLUTAL FINAL:

ESM2:293
ESM5:295

Total esperado:

4 opens

7,783,020 bytes.

Total esperado de toda execução:

14 opens

27,252,072 bytes.

Se bytes/hashes esperados divergirem:

STOP.

============================================================
17. FINAL SUPPORT

FINAL nunca teve suporte cromático/material
certificado por inspeção ML.

Durante a ÚNICA abertura de cada buffer FINAL:

- autenticar hash nativo;
- aplicar os guards de suporte congelados;
- materializar apenas os patches previstos;
- não mover centro;
- não substituir sample;
- não alterar patch;
- não reduzir margem.

Se qualquer sample FINAL falhar:

FINAL_EVALUATION=
BLOCKED_FINAL_SUPPORT

registrar que o FINAL foi consumido para suporte;

NÃO substituir;

NÃO continuar avaliação parcial;

STOP.

============================================================
18. FINAL MODEL FIT

Somente depois de materializar os 50 TRAIN+DEV:

extrair exatamente as 20 features congeladas.

Executar:

ONE FINAL FIT.

fit_calls_final=1

random_state=42.

Não calcular nenhuma nova regra a partir de resubstitution.

TRAIN+DEV metrics podem ser registradas somente
como descrição.

Não influenciam nada.

============================================================
19. ORDEM OPERACIONAL OBRIGATÓRIA

A ordem científica deve ser:

1. freeze protocolo;
2. CI pré-FINAL verde;
3. receipt exclusivo;
4. abrir TRAIN+DEV;
5. gerar 50 features;
6. fit RF final;
7. congelar hash/configuração lógica do fit;
8. somente então abrir FINAL;
9. verificar suporte FINAL;
10. extrair seis feature vectors;
11. gerar seis predictions/probabilities;
12. congelar predictions;
13. somente depois calcular métricas finais.

============================================================
20. PREDICTION-FIRST EVALUATION

O código deve separar logicamente:

INFERENCE

de:

SCORING.

Primeiro gerar para os seis samples:

sample_id
predicted_label
probability_class_0
probability_class_1

Congelar esse registro textual.

Somente depois associar:

true weak label

e calcular métricas.

Não alegar avaliação humana cega.

Chamar:

PREDICTION_FIRST_FINAL_EVALUATION.

============================================================
21. FINAL METRICS

PRIMARY:

balanced_accuracy

SECONDARY:

accuracy
precision
recall
F1
confusion matrix

Também:

TP
FP
TN
FN

Não acrescentar após ver resultados:

ROC-AUC
PR-AUC
threshold search
bootstrap model selection
p-value
ou nova métrica decisória.

============================================================
22. GRANULARIDADE OBRIGATÓRIA

Registrar antes dos pixels:

FINAL sample count:

6

POSITIVE:

3

BACKGROUND:

3

Logo:

um único erro em uma classe altera
a respectiva sensitivity/specificity em:

33.333... pontos percentuais.

Um erro que afeta uma das seis decisões altera
accuracy em:

16.666... pontos percentuais.

Balanced accuracy também possui granularidade
extremamente alta neste desenho.

Portanto:

FINAL_RESULT_SCOPE=
SMALL_INTERNAL_TEMPORAL_CONFIRMATION

Não estimativa populacional precisa.

============================================================
23. REFERÊNCIAS DE DEVELOPMENT

Preservar somente para comparação descritiva:

STRUCTURAL_LBP_RF_DEV_BA=
0.6875

MULTIMODAL_LBP_RF_DEV_BA=
0.75

MINIMAL_CNN_DEV_BA=
0.50

O resultado FINAL NÃO pode:

- reabrir seleção;
- mudar modalidade;
- mudar família;
- gerar novo modelo.

Mesmo se FINAL for ruim:

MODEL_SELECTION permanece encerrada.

============================================================
24. NENHUM THRESHOLD DE PASS CIENTÍFICO

Não definir:

FINAL BA >= X
para “sucesso”.

A fase PASS se:

- protocolo foi seguido;
- fit final ocorreu uma vez;
- FINAL foi avaliado uma vez;
- métricas foram calculadas corretamente.

Uma métrica baixa é resultado científico válido.

============================================================
25. INTERPRETAÇÃO DE FALSE POSITIVE

Se houver FP:

não escrever:

“fragmentação falsa.”

Escrever:

“BACKGROUND_CANDIDATE classificado como
PUBLISHED_FRAGMENTATION_LOCATION_PRESENT.”

Background weak-label não prova ausência
física de fragmentação.

============================================================
26. INTERPRETAÇÃO DE FALSE NEGATIVE

Se houver FN:

não escrever:

“o modelo perdeu definitivamente um evento físico.”

Escrever:

“localização publicada positiva não foi
classificada como positiva pelo pipeline.”

============================================================
27. NÃO COMPARAR CAUSALIDADE

Mesmo se FINAL for excelente:

não afirmar:

- soluto causa fragmentação;
- campo solutal é precursor causal;
- modelo prevê evento futuro;
- modelo detecta todas as fragmentações;
- desempenho generaliza para novas aquisições.

============================================================
28. PRÉ-REGISTRO FINAL

Antes dos pixels criar:

FINAL_EVALUATION_PROTOCOL.md
FINAL_MODEL_SPEC.md
FINAL_TRAINING_POLICY.md
FINAL_CLAIM_SCOPE.md
FINAL_IO_CONTRACT.md
FINAL_METRIC_CONTRACT.md

e código/testes necessários.

Congelar:

- 50 training IDs;
- 6 final IDs;
- 20 features;
- RF params;
- metrics;
- I/O;
- prediction-first rule;
- failure rules.

============================================================
29. TESTES SINTÉTICOS

Antes dos pixels exigir testes para:

- exactly 50 training samples;
- 25/25 classes;
- exactly 6 FINAL samples;
- 3/3 classes;
- no ID overlap;
- feature dimension=20;
- RF exact params;
- one final fit;
- no CNN call;
- no structural-only model;
- no threshold tuning;
- prediction-before-scoring;
- FINAL access denied before receipt;
- no replacement on support failure;
- single-use receipt;
- second execution denied.

Zero pixels.

============================================================
30. D1 — FINAL METHOD FREEZE

Criar UM commit pré-pixel:

feat(ti3d): freeze final evaluation protocol

Registrar:

D1_SHA.

Ainda:

ML_FINAL_TEST_EXECUTED=false

FINAL_TEST opens=0.

============================================================
31. D1 CI

Push fast-forward.

Executar todos os jobs históricos:

TI2
TI3-A
TI3-B
TI3-C

+
novo:

ti3d-final-synthetic-contracts

Exigir tudo SUCCESS.

Se qualquer job falhar:

STOP.

Não abrir FINAL.

============================================================
32. SCIENTIFIC FINAL EXECUTION

Somente após D1 CI completamente verde.

SCIENTIFIC_FINAL_RUNS máximo:

1

Uma única CLI científica.

Uma única final RF fit.

Uma única FINAL evaluation.

Nenhum retry.

============================================================
33. FINAL CONSUMPTION STATE

No instante anterior à primeira leitura de FINAL:

ML_FINAL_TEST=

SEALED_WITH_HISTORICAL_NON_ML_EXPOSURE

Após primeira leitura:

ML_FINAL_TEST=

CONSUMED

Esse estado é irreversível.

Mesmo se houver falha posterior:

não reabrir.

============================================================
34. EVIDÊNCIA FINAL

Após a execução registrar textualmente:

- D1;
- receipt;
- input hashes;
- opens;
- bytes;
- patch hashes;
- feature hashes/summary;
- RF full params;
- 50-training composition;
- resubstitution metrics descritivas;
- six prediction-first outputs;
- FINAL labels;
- FINAL confusion matrix;
- FINAL metrics;
- limitations;
- claim scope.

Não salvar:

pickle;
joblib;
model binary;
raw patches;
image exports;
feature arrays;

salvo nova autorização específica.

============================================================
35. D2 — EVIDENCE ONLY

Depois da ciência:

nenhum código ou parâmetro muda.

Criar somente evidência textual.

Commit sugerido:

test(ti3d): record single final evaluation

D2 é evidence-only.

============================================================
36. TERMINAL SUCCESS

Se a avaliação for tecnicamente concluída:

TI3_D_FINAL=PASS

MODEL_FAMILY=
MULTIMODAL_LBP_RF

FINAL_TRAINING_SAMPLES=50

FINAL_TEST_SAMPLES=6

SCIENTIFIC_FINAL_RUNS=1

FINAL_FIT_CALLS=1

FINAL_EVALUATIONS=1

ML_FINAL_TEST=CONSUMED

ML_FINAL_TEST_EXECUTED=true

MODEL_SELECTION_REOPENED=false

FORECASTING_AUTHORIZED=false

CAUSALITY_CLAIM_AUTHORIZED=false

EXTERNAL_GENERALIZATION_CLAIM=false

SCIENTIFIC_MODELING_COMPLETE=true

FINAL_REPORT_READY_FOR_AUTHOR_DECISION=true

MERGE_AUTHORIZED=false

CURRENT_AUTHORIZED_ACTIVITY=
NONE_AWAITING_AUTHOR_DECISION

============================================================
37. TERMINAL BLOCKED

Se FINAL support ou integridade falhar:

TI3_D_FINAL=
BLOCKED_FINAL_SUPPORT_OR_INTEGRITY

ML_FINAL_TEST=CONSUMED

ML_FINAL_TEST_EXECUTED=false

SCIENTIFIC_FINAL_RUNS=
<contador real>

Não substituir.

Não reabrir.

Não criar novo FINAL.

Não voltar a DEV.

STOP.

============================================================
38. PROIBIÇÃO PÓS-FINAL

Depois que FINAL for aberto:

é permanentemente proibido:

- tuning;
- nova CNN;
- novo RF;
- nova seed;
- novo threshold;
- mudar modalidade;
- mudar features;
- mudar patch;
- mudar backgrounds;
- redefinir labels;
- criar “FINAL2”;
- mover samples para outro split.

A próxima etapa será somente:

INTERPRETAÇÃO
+
DOCUMENTAÇÃO
+
NOTEBOOK/RELATÓRIO FINAL.

============================================================
39. REPORT FINAL

Informar:

1. PR TI3-C;
2. TI3-C merge SHA;
3. post-merge CI;
4. branch TI3-D;
5. D1 SHA;
6. D1 CI;
7. final training sample count;
8. final training acquisition/class composition;
9. TRAIN+DEV buffers abertos;
10. TRAIN+DEV bytes;
11. final RF params;
12. final fit count;
13. FINAL buffers;
14. FINAL opens;
15. FINAL bytes;
16. support result;
17. prediction-first records;
18. FINAL true/pred labels;
19. FINAL probabilities;
20. confusion matrix;
21. balanced accuracy;
22. accuracy;
23. precision;
24. recall;
25. F1;
26. metric granularity warning;
27. scientific claim scope;
28. D2 SHA;
29. final CI;
30. worktree/index;
31. terminal state.

EXECUTE SOMENTE:

TI3-C INTEGRATION
+
TI3-D FINAL EVALUATION.

UMA ÚNICA AVALIAÇÃO FINAL.

APÓS CONSUMIR FINAL:
NENHUMA NOVA MODELAGEM É AUTORIZADA.