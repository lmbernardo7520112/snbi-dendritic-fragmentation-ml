# TI3-A — RESUME
# CANONICAL PATCH DATASET + TEMPORAL/GROUP-SAFE SPLIT + LBP/RF BASELINE
#
# Retomada após:
# TI3_TARGET_RESOLUTION=PASS
#
# DDD + SDD + evidence-first
# + preregistration-before-pixels
# + leakage control
# + bounded experimentation
# + convergence governance
#
# UMA execução científica baseline válida no máximo.
# FINAL_TEST NÃO será executado.

Repositório:
snbi-dendritic-fragmentation-ml

Branch:
feat/ti3-canonical-dataset-baseline

Baseline integrada de origem:
67786bd4e23406e7f19860a53fe237e6d7b648cb

============================================================
1. ESTADO CANÔNICO
============================================================

Estados científicos anteriores:

G2_FRAG=PASS_DIRECT_RASTER_MAPPING
G2_SOLUTE=PASS
TI2R_SOLUTE=COMPLETE

SOLUTAL_INTERNAL_VALIDATION=PASS
SOLUTAL_EXTERNAL_GENERALIZATION=NOT_CLAIMED

Target resolution:

TI3_TARGET_RESOLUTION=PASS
TARGET_CONTRACT=FROZEN

WEAK_LABEL_STRATEGY=
HIGH_CONFIDENCE_PLUS_IGNORE

PUBLISHED_FRAGMENTATION_LOCATION_TARGET=
VALID_FOR_INTERNAL_ML

CIRCLE_IS_FRAGMENT_MASK=false
EXACT_ONSET_AVAILABLE=false

SOLUTAL_INPUT_SEMANTICS=
RELATIVE_SOLUTE_FIELD

FORECASTING_AUTHORIZED=false
CAUSALITY_CLAIM_AUTHORIZED=false
EXTERNAL_GENERALIZATION_CLAIM=false

ML_RUNS=0

============================================================
2. TARGET CONGELADO
============================================================

TARGET:

PUBLISHED_FRAGMENTATION_LOCATION_PRESENT

POSITIVE:

centro de círculo de alta confiança aceito pelo
extrator A0, com semântica restrita de localização
publicada de fragmentação.

IGNORE:

qualquer componente ambíguo, rejeitado, pequeno,
incompleto ou não certificável.

BACKGROUND_CANDIDATE:

região válida sem localização publicada utilizável,
suficientemente distante de POSITIVE e IGNORE.

BACKGROUND_CANDIDATE NÃO significa ausência física
comprovada de fragmentação.

ESM3 / ESM6:

LABEL SOURCE ONLY.

Nunca são features.

============================================================
3. SITUAÇÃO DOS WEAK LABELS
============================================================

Resultados congelados:

108 observações positivas aceitas.

52 annotation_site_ids únicos.

Distribuição:

ESM3 / bottom-up:
71 observações
38 sites

ESM6 / top-down:
37 observações
14 sites

Sites:

19 com uma observação
33 com repetição temporal

IGNORE:

383 regiões.

FIRST_CONFIDENT_OBSERVATION:

ESM3:
73  -> 14 sites
146 -> 10 sites
219 -> 8 sites
293 -> 6 sites

ESM6:
98  -> 2 sites
197 -> 10 sites
295 -> 2 sites
394 -> 0 sites

FIRST_CONFIDENT_OBSERVATION
NÃO é fragmentation onset.

============================================================
4. PRIMEIRA OBRIGAÇÃO — PRESERVAR TARGET RESOLUTION
============================================================

Existem atualmente 19 arquivos locais da
TI3_TARGET_RESOLUTION:

- 16 textos não staged;
- 3 scripts ignorados pela regra artifacts/**.

ANTES de qualquer novo pixel:

1. validar os 19 arquivos;
2. comparar hashes com o report terminal;
3. confirmar que nenhuma evidência foi alterada;
4. stage exatamente os 16 arquivos ordinários;
5. usar git add -f SOMENTE nos três scripts ignorados
   pertencentes à TI3_TARGET_RESOLUTION;
6. NÃO alterar .gitignore;
7. criar UM commit de preservação.

Mensagem sugerida:

docs(ti3): freeze fragmentation target resolution

Os três scripts devem ser preservados byte-for-byte.

Não modificar sua lógica.

Se qualquer divergência existir:

STOP.

============================================================
5. PRINCÍPIO DESTA FASE
============================================================

TI3-A deve responder somente:

“Existe um dataset ML patch-level reproduzível,
sem leakage conhecido, e um baseline clássico
end-to-end funcional?”

Não procurar melhor modelo.

Não procurar melhor accuracy.

Não executar CNN.

Não usar solutal no baseline.

Não abrir FINAL_TEST.

============================================================
6. UNIDADE AMOSTRAL CANÔNICA
============================================================

Para esta baseline:

uma unidade POSITIVE independente será:

UM annotation_site_id

representado somente por sua:

FIRST_CONFIDENT_OBSERVATION.

Portanto:

52 annotation_site_ids
→ no máximo 52 positivos canônicos.

Repetições temporais NÃO geram novas unidades
independentes nesta baseline.

Não duplicar um site porque aparece em vários frames.

============================================================
7. INPUT BASELINE
============================================================

Usar somente:

ESM1 para os sites provenientes de ESM3;

ESM4 para os sites provenientes de ESM6.

INPUT_BASELINE=
STRUCTURAL_RADIOGRAPHY_ONLY

Não abrir nesta baseline:

ESM2
ESM5

O campo solutal será reservado para uma comparação
multimodal posterior.

============================================================
8. MAPEAMENTO LABEL -> RADIOGRAFIA
============================================================

Usar exclusivamente o mapeamento já certificado em:

G2_FRAG=PASS_DIRECT_RASTER_MAPPING.

Não recalibrar.

Não estimar novo offset.

Não fazer novo registration.

Não alterar coordenadas para melhorar suporte.

Um centro que não esteja no suporte válido do input
deve ser marcado UNAVAILABLE.

Não usar padding artificial para salvar amostra.

============================================================
9. GEOMETRIA DO PATCH — CONGELADA
============================================================

Para esta baseline, usar:

PATCH_RADIUS_PX=32

PATCH_SIDE_PX=65

Patch centrado no pixel:

[x-32 : x+32]
[y-32 : y+32]

incluindo o centro e resultando em 65 × 65 pixels.

Justificativa:

- janela fixa;
- centro pixel-exato;
- contexto local suficiente para baseline;
- nenhuma seleção baseada em desempenho;
- não representa extensão física do fragmento.

Não testar:

32
48
64
96
128

Não escolher tamanho por accuracy.

PATCH_SIDE_PX=65 fica congelado nesta baseline.

============================================================
10. SEM PRÉ-PROCESSAMENTO DE CONTRASTE
============================================================

Para o baseline usar luminância nativa documentada.

Não aplicar:

- CLAHE;
- histogram equalization;
- resize;
- sharpening;
- denoising adaptativo;
- Canny;
- Otsu;
- Gaussian blur orientado por desempenho.

LBP será extraído diretamente do patch estrutural
de luminância.

============================================================
11. SPLIT TEMPORAL PRÉ-ESPECIFICADO
============================================================

Não fazer random split por site.

Usar FIRST_CONFIDENT_OBSERVATION apenas como índice
documental de alocação, NÃO como onset físico.

Split congelado:

--------------------------------------------------
TRAIN
--------------------------------------------------

ESM3-derived / ESM1:
frame 73
frame 146

ESM6-derived / ESM4:
frame 98

Positivos esperados:
14 + 10 + 2 = 26

--------------------------------------------------
DEVELOPMENT
--------------------------------------------------

ESM3-derived / ESM1:
frame 219

ESM6-derived / ESM4:
frame 197

Positivos esperados:
8 + 10 = 18

--------------------------------------------------
ML_FINAL_TEST
--------------------------------------------------

ESM3-derived / ESM1:
frame 293

ESM6-derived / ESM4:
frame 295

Positivos esperados:
6 + 2 = 8

--------------------------------------------------

A ordem é temporal dentro de cada aquisição:

TRAIN
→ DEVELOPMENT
→ FINAL_TEST

Nenhum desempenho foi observado para escolher essa divisão.

============================================================
12. REGRA POR annotation_site_id
============================================================

Cada annotation_site_id pertence integralmente
a UM único split.

Como esta baseline usa somente
FIRST_CONFIDENT_OBSERVATION:

cada site produz apenas um positivo canônico.

Mesmo assim, o manifesto deve verificar:

TRAIN ∩ DEV = ∅

TRAIN ∩ FINAL = ∅

DEV ∩ FINAL = ∅

por annotation_site_id.

============================================================
13. CONTEXT GROUP GUARD
============================================================

Definir:

context_group_id =
source/acquisition + frame_index

Um frame inteiro pertence a apenas UM split.

Nenhum patch de um frame TRAIN pode entrar DEV ou FINAL.

Nenhum patch de um frame DEV pode entrar TRAIN ou FINAL.

Nenhum patch de um frame FINAL pode entrar TRAIN ou DEV.

Isso vale para:

- positivos;
- backgrounds;
- derivados;
- features;
- caches.

============================================================
14. CONTROLE DE CONTEXTO ENTRE SITES
============================================================

Um patch não pode conter o centro de outro
annotation_site_id pertencente a split diferente.

Antes de materializar qualquer patch:

usar o ledger completo dos 52 sites para verificar interseção.

Expandir cada centro de site por:

PATCH_RADIUS_PX + REGISTRATION_GUARD_PX

onde:

REGISTRATION_GUARD_PX=3.

Se o patch candidato interceptar zona de outro site
incompatível com seu split:

marcar INVALID_CONTEXT.

Não mover o centro para salvá-lo.

============================================================
15. BACKGROUND — REGRA DETERMINÍSTICA
============================================================

Objetivo:

1 BACKGROUND_CANDIDATE por POSITIVE
em cada split.

Logo, se todos os positivos forem válidos:

TRAIN:
26 positive + 26 background

DEV:
18 positive + 18 background

FINAL:
8 positive + 8 background

Gerar candidatos de background SEM olhar os valores
dos pixels.

Usar somente:

- dimensões documentadas;
- POSITIVE centers;
- IGNORE bounding boxes;
- bordas;
- patch radius;
- registration guard.

Criar grid determinístico de centros candidatos.

Filtrar qualquer candidato cujo patch:

- ultrapasse suporte válido;
- intercepte POSITIVE safety area;
- intercepte IGNORE safety area;
- intercepte outro candidate patch já escolhido
  quando a regra exigir independência espacial.

Selecionar candidatos por ordenação determinística
com:

BACKGROUND_SEED=42

A seleção não pode depender de:

- intensidade;
- textura;
- score;
- LBP;
- modelo.

Se não existirem backgrounds suficientes:

BLOCKED_BACKGROUND_SUPPORT

STOP.

Não reduzir safety margin.

============================================================
16. FINAL_TEST — DEFINIR ANTES DOS PIXELS
============================================================

Construir manifesto completo dos IDs e coordenadas
do futuro FINAL_TEST antes de abrir seu input.

Depois do freeze registrar:

ML_FINAL_TEST=
SEALED_WITH_HISTORICAL_NON_ML_EXPOSURE

Essa formulação é obrigatória.

Razão:

alguns ativos tiveram exposição histórica nas fases
de registro, mas não podem participar de construção,
treinamento ou seleção de modelo ML.

Não alegar:

GLOBAL_VIRGIN_HOLDOUT.

============================================================
17. PROIBIÇÃO DE FINAL TEST
============================================================

Nesta tarefa NÃO abrir pixels ESM1/ESM4 correspondentes
ao ML_FINAL_TEST.

Não extrair:

- patches;
- LBP;
- estatísticas;
- thumbnails;
- histogramas;
- previews.

Não contar textura.

Não executar modelo.

O manifesto pode conter:

- IDs;
- coordenadas;
- lineage;
- hashes conhecidos;
- split;

sem abrir pixels.

============================================================
18. PRÉ-REGISTRO ANTES DOS PIXELS TRAIN/DEV
============================================================

Antes de abrir ESM1/ESM4 TRAIN ou DEV:

criar e congelar:

DATASET_SPEC.md
SPLIT_PROTOCOL.md
BACKGROUND_PROTOCOL.md
BASELINE_SPEC.md
LEAKAGE_THREAT_MODEL.md
COURSE_ALIGNMENT.md

Implementar:

- dataset manifest builder;
- patch extractor;
- LBP feature extractor;
- split guards;
- context guards;
- baseline runner;
- testes sintéticos.

Nenhum arquivo experimental deve ser necessário
para os testes.

============================================================
19. BASELINE CURRICULAR — LBP
============================================================

Usar o princípio apresentado no notebook A4
da Trilha 2.

Configuração congelada:

LBP:

P=8
R=1
method="uniform"

Histograma:

10 bins
range=(0,10)
normalizado com density=True

Cada patch 65x65 gera:

10 features LBP.

Não acrescentar SIFT nesta baseline.

Razão:

LBP testa diretamente a informação de textura local
com baixa dimensionalidade e é compatível com a
escassez de unidades independentes.

SIFT permanece técnica curricular discutida,
mas não utilizada.

============================================================
20. BASELINE CURRICULAR — RANDOM FOREST
============================================================

Random Forest congelado:

n_estimators=100
random_state=42

Sem:

- grid search;
- random search;
- tuning;
- seleção de depth;
- seleção por DEV.

Usar defaults da versão pinada para os demais
parâmetros, registrando-os integralmente.

Nenhum class weighting automático se o dataset
estiver 1:1 conforme especificação.

============================================================
21. MÉTRICAS CONGELADAS
============================================================

Tarefa:

binary weak-label classification

POSITIVE:
PUBLISHED_FRAGMENTATION_LOCATION_PRESENT

BACKGROUND:
NO_PUBLISHED_ANNOTATION_IN_VALID_CANDIDATE_REGION

PRIMARY_METRIC:

balanced_accuracy

SECONDARY_METRICS:

- accuracy;
- precision;
- recall;
- F1;
- confusion matrix.

Registrar também:

- TP;
- FP;
- TN;
- FN.

Não escolher métrica depois de observar resultado.

============================================================
22. CLAIM SOBRE MÉTRICAS
============================================================

As métricas medem concordância com o
WEAK-LABEL TARGET.

Elas NÃO medem diretamente:

- recall físico de todas as fragmentações;
- sensibilidade para eventos não anotados;
- exaustividade experimental;
- causalidade;
- forecasting.

============================================================
23. C1 — METHOD FREEZE
============================================================

Depois que:

- protocolos;
- código;
- configs;
- testes sintéticos;

estiverem concluídos:

executar toda a suíte permitida.

Exigir:

zero falhas.

Criar UM commit científico/metodológico antes
dos pixels.

Mensagem sugerida:

feat(ti3): freeze canonical patch baseline protocol

Registrar SHA C1.

Nenhuma configuração científica pode mudar
depois de C1.

============================================================
24. PUBLICAÇÃO / CI DE C1
============================================================

Fazer push fast-forward da branch.

Não force-push.

Executar CI aplicável.

CI deve validar no mínimo:

- contratos;
- testes sintéticos;
- dataset guards sem dados experimentais;
- ausência de FINAL_TEST access;
- integridade G2.

Se CI falhar:

STOP.

Não abrir pixels.

============================================================
25. EXECUÇÃO EXPERIMENTAL AUTORIZADA
============================================================

Somente com C1 congelado e CI verde:

abrir exatamente os inputs estruturais necessários
para TRAIN e DEVELOPMENT.

Nunca FINAL_TEST.

Registrar:

- arquivo;
- frame;
- opens;
- bytes;
- hashes;
- patches extraídos.

Não abrir ESM2/ESM5.

Não abrir ESM3/ESM6 novamente.

============================================================
26. RUNS
============================================================

Permitir:

TECHNICAL_RUNS:

somente smoke tests sintéticos antes da ciência.

SCIENTIFIC_ML_RUNS:

exatamente 1 baseline válido.

Essa execução inclui:

TRAIN
+
DEVELOPMENT evaluation.

Se executar com sucesso:

STOP.

Não treinar novamente com outra seed.

Não tentar melhorar score.

============================================================
27. AUSÊNCIA DE TUNING
============================================================

Após resultado DEV:

NÃO alterar:

- patch size;
- LBP;
- RF;
- backgrounds;
- split;
- métricas;
- seed;
- preprocessing.

DEV serve para medir o baseline.

Não para iniciar tuning nesta autorização.

============================================================
28. RESULTADO BAIXO É VÁLIDO
============================================================

Um baseline com desempenho baixo NÃO constitui
falha de TI3-A se:

- dataset estiver correto;
- split estiver correto;
- ausência de leakage estiver sustentada;
- pipeline executar;
- métricas forem calculadas corretamente.

TI3_A_BASELINE=PASS

significa:

“baseline end-to-end executado conforme contrato.”

Não:

“modelo possui alto desempenho.”

============================================================
29. COURSE_ALIGNMENT.md
============================================================

Registrar explicitamente:

A4:

LBP
→ UTILIZED

Random Forest
→ UTILIZED

SIFT
→ NOT_USED_IN_BASELINE
  razão: complexidade adicional não justificada.

ORB/FAST/BRIEF
→ NOT_USED_IN_BASELINE.

A5:

CNN
→ DEFERRED_TO_TI3_B

Sobel
→ ALREADY_USED_CONCEPTUALLY_IN_NGF

Canny
→ NOT_USED_AS_MODEL_INPUT

thresholding/components
→ ALREADY_USED_FOR_WEAK_LABEL_EXTRACTION

Hough
→ DELIBERATELY_NOT_USED
  para evitar tuning retrospectivo.

============================================================
30. PAPEL DO SOLUTAL
============================================================

Nesta TI3-A:

SOLUTAL_MODEL_INPUT=NOT_USED

ESM2/ESM5 não são abertos.

A fase futura poderá comparar:

STRUCTURAL_ONLY

versus

STRUCTURAL_PLUS_RELATIVE_SOLUTE

para testar informação incremental.

Não autorizar isso automaticamente.

============================================================
31. DETECTION ≠ FORECASTING ≠ CAUSALITY
============================================================

Preservar:

FORECASTING_AUTHORIZED=false

CAUSALITY_CLAIM_AUTHORIZED=false

EXTERNAL_GENERALIZATION_CLAIM=false

O baseline atual é:

classificação/detecção associativa
de localizações publicadas.

Não previsão futura.

============================================================
32. ARTEFATOS
============================================================

Produzir:

artifacts/evidence/TI3_A_RESUME/

DATASET_SPEC.md
dataset_manifest.json
SPLIT_PROTOCOL.md
BACKGROUND_PROTOCOL.md
LEAKAGE_THREAT_MODEL.md
BASELINE_SPEC.md
COURSE_ALIGNMENT.md
CLAIM_SCOPE.md
method-freeze.json
execution-receipt.json
io-audit.json
results.json
commands.json
environment.json
verification.json
execution-report.md

Código científico reutilizável deve ficar em:

src/
scripts/
tests/

e não apenas em diretório ignorado.

============================================================
33. DATASET MANIFEST
============================================================

Cada sample deve incluir:

sample_id
annotation_site_id_or_background_id
source_id
acquisition_id
frame_index
experimental_time_s
center_x
center_y
patch_radius_px
patch_side_px
label
split
context_group_id
provenance
input_opened
input_hash_if_opened

Para FINAL_TEST:

input_opened=false.

============================================================
34. GATES
============================================================

Verificar:

[ ] target-resolution PASS foi versionado integralmente
[ ] 3 scripts históricos preservados
[ ] G2 intacto
[ ] 52 sites reconhecidos
[ ] um positivo canônico por site
[ ] FIRST_CONFIDENT_OBSERVATION não chamado onset
[ ] split temporal exato congelado
[ ] context-group leakage bloqueado
[ ] site leakage bloqueado
[ ] patch 65x65 congelado
[ ] backgrounds escolhidos sem consultar pixels
[ ] FINAL_TEST manifestado
[ ] FINAL_TEST não aberto
[ ] LBP P=8/R=1 uniform congelado
[ ] RF 100 árvores / seed 42 congelado
[ ] métricas congeladas
[ ] C1 criado antes dos pixels
[ ] CI C1 verde antes dos pixels
[ ] somente TRAIN/DEV abertos
[ ] ESM2/5 não abertos
[ ] uma execução científica ML
[ ] zero tuning
[ ] resultados DEV registrados
[ ] claims restritos a weak labels
[ ] worktree/index controlados

============================================================
35. ESTADO FINAL ESPERADO
============================================================

Se tudo executar:

TI3_A=PASS
TI3_A_DATASET=PASS
TI3_A_TARGET=FROZEN
TI3_A_SPLIT=FROZEN_TEMPORAL_GROUPED
TI3_A_LEAKAGE_GUARDS=PASS
TI3_A_BASELINE=PASS
BASELINE_MODEL=LBP_RF
SCIENTIFIC_ML_RUNS=1
SOLUTAL_MODEL_INPUT=NOT_USED
ML_FINAL_TEST=SEALED_WITH_HISTORICAL_NON_ML_EXPOSURE
ML_FINAL_TEST_EXECUTED=false
FORECASTING_AUTHORIZED=false
CAUSALITY_CLAIM_AUTHORIZED=false
EXTERNAL_GENERALIZATION_CLAIM=false
TI3_B_READY_FOR_AUTHOR_DECISION=true
TI3_B_AUTHORIZED=false
MERGE_AUTHORIZED=false
CURRENT_AUTHORIZED_ACTIVITY=NONE_AWAITING_AUTHOR_DECISION

============================================================
36. BLOQUEIOS
============================================================

Se ocorrer bloqueio ANTES dos pixels:

não acessar dados.

Se ocorrer erro técnico DEPOIS de pixels mas antes
de uma execução científica válida:

registrar exatamente o incidente.

Não fazer retry científico automático.

Se o baseline científico válido executar:

seja o resultado bom ou ruim:

STOP.

============================================================
37. REPORT FINAL
============================================================

Informar:

1. checkpoint TARGET_RESOLUTION;
2. C1 method-freeze SHA;
3. branch/HEAD;
4. CI pré-pixels;
5. número de sites;
6. samples positivos por split;
7. backgrounds por split;
8. samples inválidos/excluídos e motivo;
9. patch geometry;
10. split exato;
11. anti-leakage;
12. FINAL_TEST manifest/hash;
13. FINAL_TEST opens/bytes;
14. TRAIN/DEV opens/bytes;
15. LBP config;
16. RF config;
17. runs técnicos;
18. runs científicos;
19. métricas TRAIN;
20. métricas DEVELOPMENT;
21. confusion matrix DEV;
22. decisão curricular;
23. papel do solutal;
24. claims permitidos;
25. claims proibidos;
26. arquivos criados/modificados;
27. testes;
28. CI;
29. worktree/index;
30. estado final.

EXECUTE SOMENTE TI3-A RESUME.
