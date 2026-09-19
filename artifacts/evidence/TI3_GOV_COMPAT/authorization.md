# TI3-GOV-COMPAT + TI3-A RESUME
# Migração única de governança TI2-global -> composição LEGACY + TI3
# seguida, condicionalmente, do C1 e da única execução baseline TRAIN/DEV
#
# NÃO enfraquecer guards históricos
# NÃO ocultar TI3 do auditor
# NÃO acessar FINAL_TEST
# NÃO fazer tuning
# Convergência obrigatória

Repositório:
snbi-dendritic-fragmentation-ml

Branch:
feat/ti3-canonical-dataset-baseline

HEAD esperado:
41d523e038e844588ee7724e07b00f75bdf29fdc

============================================================
1. ESTADO CANÔNICO
============================================================

TI3_PREFLIGHT_RECOVERY=PASS

BLOCKED_STAGED_DATA_GUARD=RESOLVED

TI3_ML_ENVIRONMENT=READY

TI3_A=BLOCKED_CI_SCOPE_CONTRACT

C1=NOT_CREATED

CI_PREPIXEL=
NOT_RUN_BLOCKED_BY_LOCAL_SCOPE_PREFLIGHT

EXPERIMENTAL_OPENS=0
EXPERIMENTAL_BYTES=0
SCIENTIFIC_ML_RUNS=0

ML_FINAL_TEST=
SEALED_WITH_HISTORICAL_NON_ML_EXPOSURE

ML_FINAL_TEST_EXECUTED=false

TARGET_CONTRACT=FROZEN

TARGET=
PUBLISHED_FRAGMENTATION_LOCATION_PRESENT

G2_FRAG=PASS_DIRECT_RASTER_MAPPING
G2_SOLUTE=PASS

============================================================
2. ESTADO DO DATASET PLANEJADO
============================================================

52 annotation_site_ids permanecem no contrato.

Após os guards geométricos pré-pixel:

TRAIN:
17 POSITIVE
17 BACKGROUND
34 samples planejados

DEVELOPMENT:
8 POSITIVE
8 BACKGROUND
16 samples planejados

FINAL_TEST:
3 POSITIVE
3 BACKGROUND
6 samples planejados

Total planejado:
56 samples.

24 sites/candidatos foram excluídos por razões geométricas/contextuais
pré-especificadas, não por desempenho.

NÃO reotimizar esses números.

NÃO redistribuir sites para tornar FINAL maior.

A pequena dimensão do FINAL_TEST deverá permanecer como limitação explícita.

============================================================
3. CAUSA DO BLOQUEIO
============================================================

O guard histórico:

scripts/check_ti2_scope.py

foi concebido quando TI-3 era globalmente proibido.

Ele:

- bloqueia componentes de path como:
  annotation
  annotations
  label
  dataset
  split
  baseline
  model
  training
  train
  evaluation
  etc.;

- bloqueia imports como:
  sklearn
  torch
  tensorflow
  etc.;

- é atualmente executado sobre TODO o inventário tracked.

Portanto, código TI3 legítimo não pode coexistir com sua aplicação global.

Esse comportamento histórico NÃO é um bug.

Não alterá-lo para aceitar TI3 globalmente.

============================================================
4. PRINCÍPIO DE MIGRAÇÃO
============================================================

Preservar:

scripts/check_ti2_scope.py

como guard LEGACY.

Criar uma composição explícita:

PRE_TI3_LEGACY_SCOPE
+
TI3_SCOPE
=
CURRENT_REPOSITORY_SCOPE

Nenhum código tracked relevante pode ficar fora desses escopos.

============================================================
5. ARQUIVOS QUE DEVEM PERMANECER INTACTOS
============================================================

Não modificar nesta compatibilização:

scripts/check_ti2_scope.py

scripts/check_ti2_checksums.py

scripts/check_repository_data.py

.gitignore

kernels G2

configs científicos G2

artefatos científicos congelados G2

TARGET_CONTRACT

weak-label ledger

split científico já planejado

patch geometry

LBP configuration

Random Forest configuration

métricas congeladas

============================================================
6. FREEZE DO CORPUS PRÉ-TI3
============================================================

Antes de qualquer alteração de CI/governança:

construir um manifesto determinístico do código tracked existente
no HEAD 41d523e...

Esse manifesto representa o corpus histórico permitido antes
da introdução do novo código TI3.

Incluir, conforme aplicável:

src/**/*.py
scripts/**/*.py
tests/**/*.py

que já estejam tracked em 41d523e.

Criar, por exemplo:

configs/governance/pre-ti3-code-scope.json

O manifesto deve conter:

path
git_mode
blob_sha
classification="LEGACY_PRE_TI3"

Não incluir arquivos TI3 ainda não tracked.

O baseline SHA deve ser explicitamente:

41d523e038e844588ee7724e07b00f75bdf29fdc

============================================================
7. PRESERVAÇÃO DOS CHECKSUMS HISTÓRICOS
============================================================

Antes de modificar qualquer arquivo atualmente listado em:

artifacts/evidence/TI2/checksums.sha256

copiar BYTE-FOR-BYTE o manifesto atual para:

artifacts/evidence/TI2/
checksums-pre-ti3-41d523e.sha256

Registrar:

- SHA-256 do snapshot;
- número de entradas;
- baseline Git SHA.

Esse snapshot nunca será reescrito.

Ele preserva a fronteira histórica TI2/pre-TI3.

============================================================
8. CHECK_Ti3_SCOPE
============================================================

Criar:

scripts/check_ti3_scope.py

Esse checker deve validar SOMENTE o escopo TI3 explicitamente autorizado.

Não inferir autorização por nome de branch.

Usar allowlist explícita/configuração versionada.

Reutilizar, se já existir localmente e for consistente,
a configuração de autoridade TI3-A preparada no preflight.

Caso contrário criar configuração explícita, por exemplo:

configs/authority/ti3-a-baseline.json

Ela deve listar exatamente:

- paths TI3 autorizados;
- requirements-ti3-ml.txt;
- módulos;
- runners;
- testes;
- protocolos;
- evidências textuais permitidas;
- FINAL_TEST policy;
- scientific-run authority=false antes de C1/CI.

============================================================
9. POLÍTICA DO CHECK_Ti3_SCOPE
============================================================

TI3 pode usar somente as dependências pinadas:

numpy==1.26.4
scipy==1.11.4
scikit-image==0.24.0
scikit-learn==1.5.2

Permitir:

sklearn
skimage

SOMENTE nos paths TI3 explicitamente allow-listed.

Continuar proibindo, salvo futura decisão:

torch
torchvision
tensorflow
keras
xgboost
lightgbm
catboost
transformers
fastai

e quaisquer dependências não autorizadas.

============================================================
10. REQUIREMENTS
============================================================

Validar exatamente:

requirements-ti3-ml.txt

com:

numpy==1.26.4
scipy==1.11.4
scikit-image==0.24.0
scikit-learn==1.5.2

Não adicionar novas bibliotecas.

pyproject.toml [project].dependencies deve permanecer vazio,
preservando o contrato legado.

TI3 usa seu requirements separado.

============================================================
11. CHECK_PHASE_SCOPE
============================================================

Criar:

scripts/check_phase_scope.py

Este é o novo compositor.

Ele deve:

1. executar o data guard GLOBAL;
2. carregar todo o inventário tracked;
3. carregar PRE_TI3_LEGACY_SCOPE;
4. carregar TI3_SCOPE;
5. exigir que cada Python relevante em src/scripts/tests pertença
   a um escopo conhecido;
6. rejeitar paths não classificados;
7. aplicar check_ti2_scope.audit(entries=LEGACY_ENTRIES);
8. aplicar check_ti3_scope.audit(entries=TI3_ENTRIES);
9. combinar as violações;
10. PASS somente se AMBOS os domínios passarem.

Nenhum silent filtering.

Nenhum continue-on-error.

Nenhum path deve ser ignorado apenas porque contém “ti3”.

============================================================
12. INVARIANTE ANTI-EVASÃO
============================================================

Adicionar testes que demonstrem:

- código TI3 fora da allowlist -> FAIL;
- sklearn em código legado -> FAIL;
- sklearn em TI3 allowlisted -> PASS;
- torch em TI3 -> FAIL;
- path dataset TI3 não allowlisted -> FAIL;
- path legacy alterado/ausente -> FAIL;
- arquivo Python não classificado -> FAIL;
- data path experimental tracked -> FAIL;
- symlink -> FAIL;
- requisitos diferentes dos pins -> FAIL.

O novo sistema não pode ser menos restritivo que a união
dos dois contratos.

============================================================
13. CHECK_Ti2_SCOPE PERMANECE LEGADO
============================================================

Não alterar:

scripts/check_ti2_scope.py

Seu comportamento global histórico é preservado em Git.

No novo compositor ele será chamado com:

entries=LEGACY_ENTRIES

Isso utiliza a API audit(entries=...) já existente.

Não criar uma versão relaxada do TI2 checker.

============================================================
14. CHECKSUM ATIVO
============================================================

O snapshot pre-TI3 preserva os hashes históricos.

Se o workflow atual precisar ser modificado para usar
check_phase_scope.py:

atualizar o manifesto ATIVO:

artifacts/evidence/TI2/checksums.sha256

somente para os paths realmente modificados.

Não alterar hashes de arquivos que não mudaram.

Registrar exatamente quais entradas foram atualizadas.

O snapshot:

checksums-pre-ti3-41d523e.sha256

deve preservar os valores anteriores.

============================================================
15. CI — COMPOSIÇÃO
============================================================

Modificar a CI minimamente.

O job legado continua executando:

- data guard;
- bootstrap;
- manifest;
- time rule;
- historical checksums;
- legacy tests.

Substituir APENAS a aplicação global direta de:

scripts/check_ti2_scope.py

pela composição:

scripts/check_phase_scope.py

que internamente executa o TI2 checker no legacy scope
e o TI3 checker no TI3 scope.

Não remover o TI2 checker.

Não usar continue-on-error.

============================================================
16. JOB TI3 SINTÉTICO
============================================================

Adicionar/usar um job dedicado:

ti3-synthetic-contracts

Python:
3.12

Instalar exatamente:

requirements-ti3-ml.txt

Executar:

- data guard;
- phase scope guard;
- dependency/version guard;
- dataset synthetic tests;
- baseline synthetic tests;
- support synthetic tests;
- execution synthetic tests;
- tests de anti-leakage;
- FINAL_TEST no-access guards.

Zero experimental data.

Exigir:

zero failures
zero errors
zero unexpected skips.

============================================================
17. TESTES DE REGRESSÃO LEGACY
============================================================

Todos os testes históricos existentes devem continuar verdes.

Particularmente:

TI2
TI2R-FRAG
TI2R-SOLUTE
checksums
data guard
authority
bootstrap

Nenhum teste histórico deve ser alterado apenas para aceitar TI3.

============================================================
18. C0 — GOVERNANCE COMPATIBILITY COMMIT
============================================================

Criar UM commit exclusivamente de governança/CI.

Não incluir ainda o scientific baseline C1.

Conteúdo C0 pode incluir SOMENTE:

- decisão/autorização desta migração;
- pre-TI3 scope manifest;
- checksum historical snapshot;
- check_ti3_scope.py;
- check_phase_scope.py;
- testes desses guards;
- configuração de escopo/authority necessária;
- mudança mínima de CI;
- atualização mínima do checksum ativo;
- documentação diretamente necessária.

Não incluir:

baseline core;
patch extractor;
dataset builder científico;
runner científico;
resultados experimentais.

Mensagem sugerida:

chore(governance): compose legacy and ti3 scope guards

============================================================
19. C0 LOCAL GATES
============================================================

Antes do commit exigir:

data guard PASS

legacy scoped TI2 guard PASS

TI3 guard PASS

composed phase guard PASS

historical checksum snapshot valid

active checksums PASS

legacy full suite PASS

new governance tests PASS

zero experimental opens

============================================================
20. PUBLICAR C0
============================================================

Fazer push fast-forward.

Sem force.

Executar CI remota.

Exigir todos os jobs obrigatórios verdes.

Se C0 CI falhar:

STOP.

Não criar C1.

Não acessar pixels.

Não fazer segundo corretivo automático.

============================================================
21. SE E SOMENTE SE C0 CI = PASS
============================================================

Retomar TI3-A.

Usar os arquivos locais previamente preparados.

Não regenerar ciência apenas porque houve migração de governance.

Revalidar:

- hashes;
- target;
- dataset manifest;
- split;
- backgrounds;
- geometry;
- FINAL_TEST manifest;
- LBP;
- RF;
- metrics.

============================================================
22. C1 — SCIENTIFIC METHOD FREEZE
============================================================

Stagear exatamente os arquivos científicos/metodológicos TI3-A
já autorizados e agora permitidos pelo TI3 scope.

Não usar:

git add .
git add -A

Executar:

data guard
phase scope guard
full legacy suite
TI3 synthetic suite

Exigir tudo verde.

Criar:

C1

Mensagem:

feat(ti3): freeze canonical patch baseline protocol

C1 deve conter:

- requirements TI3;
- dataset/split protocol;
- background protocol;
- leakage model;
- LBP/RF baseline specification;
- claim scope;
- active TI3 code;
- tests;
- TI3 authority/scope;
- pre-pixel evidence.

Nenhum resultado experimental.

============================================================
23. C1 PUBLICAÇÃO / CI
============================================================

Push fast-forward.

CI obrigatória.

Se CI não for totalmente verde:

STOP.

Zero pixels.

============================================================
24. FINAL_TEST
============================================================

Preservar:

ML_FINAL_TEST=
SEALED_WITH_HISTORICAL_NON_ML_EXPOSURE

Planejado:

3 POSITIVE
3 BACKGROUND

Essa dimensão é pequena.

Registrar explicitamente em CLAIM_SCOPE:

- baixa potência estatística;
- alta granularidade das métricas;
- impossibilidade de claims externos;
- resultado final será descritivo/interno.

Não redistribuir samples para aumentar o teste.

Não abrir FINAL.

============================================================
25. EXECUÇÃO TRAIN/DEV
============================================================

Somente após C1 + CI verde.

Abrir exclusivamente:

TRAIN
DEVELOPMENT

Estrutural:

ESM1
ESM4

nos frames autorizados.

Não abrir:

ESM2
ESM5
ESM3
ESM6
FINAL_TEST input.

Aplicar primeiro o real-support guard.

Se qualquer patch TRAIN/DEV falhar suporte integral:

registrar BLOCKED_SUPPORT.

Não substituir sample.

Não mover centro.

Não reduzir margem.

Não retentar seleção.

============================================================
26. BASELINE
============================================================

Usar exatamente:

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

demais parâmetros:
defaults registrados.

Sem tuning.

============================================================
27. UMA EXECUÇÃO CIENTÍFICA
============================================================

SCIENTIFIC_ML_RUNS máximo:

1

Essa execução inclui:

fit em TRAIN

e

avaliação em DEVELOPMENT.

Não repetir com outra seed.

Não mudar modelo após DEV.

============================================================
28. MÉTRICAS
============================================================

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

Resultado baixo é válido.

Não existe score mínimo para TI3_A_BASELINE=PASS.

PASS significa:

pipeline científico executado conforme protocolo.

============================================================
29. EVIDÊNCIA PÓS-EXECUÇÃO
============================================================

Depois da única execução:

nenhuma alteração científica.

Criar evidência:

execution-report
results
io-audit
environment
commands
verification
post-run hashes

Se necessário criar C2:

C2 deve ser EVIDENCE-ONLY.

Mensagem sugerida:

test(ti3): record canonical baseline evidence

============================================================
30. NÃO INICIAR TI3-B
============================================================

Mesmo se baseline for excelente:

TI3_B_AUTHORIZED=false

Não executar CNN.

Não abrir solutal.

Não abrir FINAL_TEST.

Não selecionar modelo principal.

============================================================
31. CLAIMS
============================================================

Permitido:

- internal weak-label baseline;
- published-location classification;
- TRAIN/DEV performance;
- reproducible LBP/RF pipeline.

Proibido:

- physical fragmentation recall;
- exhaustive event detection;
- exact onset;
- forecasting;
- causality;
- external generalization;
- solutal benefit nesta fase.

============================================================
32. ESTADO FINAL — SUCESSO
============================================================

Se governance, C1, CI e baseline executarem:

TI3_GOV_COMPAT=PASS
LEGACY_SCOPE_GUARD=PASS
TI3_SCOPE_GUARD=PASS
PHASE_SCOPE_GUARD=PASS

TI3_A=PASS
TI3_A_DATASET=PASS
TI3_A_SPLIT=FROZEN_TEMPORAL_GROUPED
TI3_A_LEAKAGE_GUARDS=PASS

BASELINE_MODEL=LBP_RF
SCIENTIFIC_ML_RUNS=1

ML_FINAL_TEST=
SEALED_WITH_HISTORICAL_NON_ML_EXPOSURE

ML_FINAL_TEST_EXECUTED=false

SOLUTAL_MODEL_INPUT=NOT_USED

FORECASTING_AUTHORIZED=false
CAUSALITY_CLAIM_AUTHORIZED=false
EXTERNAL_GENERALIZATION_CLAIM=false

TI3_B_READY_FOR_AUTHOR_DECISION=true
TI3_B_AUTHORIZED=false

MERGE_AUTHORIZED=false

CURRENT_AUTHORIZED_ACTIVITY=
NONE_AWAITING_AUTHOR_DECISION

============================================================
33. SE QUALQUER GATE FALHAR
============================================================

STOP.

Não:

- afrouxar checker;
- renomear path para escapar;
- remover check;
- usar continue-on-error;
- modificar split;
- abrir pixels prematuramente;
- criar segundo corrective loop automático.

Registrar exatamente o bloqueio.

============================================================
34. REPORT FINAL
============================================================

Informar:

1. HEAD inicial;
2. pre-TI3 scope manifest;
3. snapshot dos checksums históricos;
4. arquivos legacy classificados;
5. arquivos TI3 classificados;
6. unclassified paths = 0;
7. resultado legacy guard;
8. resultado TI3 guard;
9. resultado composed guard;
10. C0 SHA;
11. C0 CI;
12. C1 SHA, se criado;
13. C1 CI;
14. experimental opens;
15. bytes;
16. real-support guard;
17. TRAIN válido;
18. DEV válido;
19. FINAL opens/bytes;
20. scientific ML runs;
21. LBP config;
22. RF config;
23. TRAIN metrics;
24. DEV metrics;
25. DEV confusion matrix;
26. limitações estatísticas;
27. C2 SHA, se criado;
28. CI final;
29. worktree/index;
30. estado terminal.

EXECUTE ESTA MIGRAÇÃO DE GOVERNANÇA UMA ÚNICA VEZ.

SE C0 CI FICAR VERDE,
CONTINUE DIRETAMENTE PARA C1.

SE C1 CI FICAR VERDE,
EXECUTE EXATAMENTE UMA VEZ O BASELINE TRAIN/DEV.

NUNCA ABRA ML_FINAL_TEST NESTA AUTORIZAÇÃO.