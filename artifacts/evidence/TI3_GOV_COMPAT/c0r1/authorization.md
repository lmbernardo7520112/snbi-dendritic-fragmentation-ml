# TI3-C0R1 — TARGETED CI SYNTAX REPAIR
# Correção única do workflow C0 seguida de retomada condicional de TI3-A
#
# NÃO redesenhar governança
# NÃO alterar ciência
# NÃO acessar pixels antes de CI verde
# NÃO fazer rerun do workflow C0 falho
# CONVERGÊNCIA OBRIGATÓRIA

Repositório:
snbi-dendritic-fragmentation-ml

Branch:
feat/ti3-canonical-dataset-baseline

HEAD esperado local/remoto:
272695a4420e37fddf6674664d0040ef064c153f

============================================================
1. ESTADO CANÔNICO
============================================================

C0 publicado:

272695a4420e37fddf6674664d0040ef064c153f

Estado comprovado:

SEMANTIC_SCOPE_RECLASSIFICATION=PASS

LEGACY_TI2_FILES=75
TI3_A0_FROZEN_FILES=4

LEGACY_SCOPE_GUARD=PASS
TI3_A0_FROZEN_GUARD=PASS
TI3_SCOPE_GUARD=PASS
PHASE_SCOPE_GUARD=PASS

Dois jobs históricos remotos:
SUCCESS

Workflow TI3:
FAILURE antes de criação de jobs.

C1=NOT_CREATED
C2=NOT_CREATED

EXPERIMENTAL_OPENS=0
EXPERIMENTAL_BYTES=0
SCIENTIFIC_ML_RUNS=0

ML_FINAL_TEST=
SEALED_WITH_HISTORICAL_NON_ML_EXPOSURE

ML_FINAL_TEST_EXECUTED=false

============================================================
2. CAUSA VERIFICADA
============================================================

No arquivo:

.github/workflows/ti3-synthetic.yml

existe atualmente:

run: python -B -m pip --isolated install --disable-pip-version-check --no-cache-dir --only-binary=:all: -r requirements-ti3-ml.txt

Esse comando é um YAML plain scalar.

O trecho:

--only-binary=:all:

contém um ":" final seguido por espaço antes de "-r".

Isso torna o YAML sintaticamente inválido para um parser YAML,
produzindo erro equivalente a:

mapping values are not allowed here

Isso explica o FAILURE antes da criação de jobs.

Classificar:

C0_CI_FAILURE_CAUSE=
VERIFIED_YAML_PLAIN_SCALAR_COLON_PARSE_ERROR

============================================================
3. AUTORIZAÇÃO DE CORREÇÃO
============================================================

Está autorizado modificar SOMENTE:

.github/workflows/ti3-synthetic.yml

e evidência textual diretamente necessária desta correção.

Não modificar:

- check_ti2_scope.py;
- check_ti3_scope.py;
- check_phase_scope.py;
- phase-scope-v1.json;
- partição 75 + 4;
- requirements-ti3-ml.txt;
- data guard;
- .gitignore;
- target;
- dataset;
- split;
- backgrounds;
- patch geometry;
- LBP;
- Random Forest;
- métricas;
- G2;
- FINAL_TEST.

============================================================
4. CORREÇÃO EXATA
============================================================

Substituir SOMENTE:

- name: Install pinned TI3 dependencies on CI
  run: python -B -m pip --isolated install --disable-pip-version-check --no-cache-dir --only-binary=:all: -r requirements-ti3-ml.txt

por:

- name: Install pinned TI3 dependencies on CI
  run: >-
    python -B -m pip --isolated install
    --disable-pip-version-check
    --no-cache-dir
    --only-binary=:all:
    -r requirements-ti3-ml.txt

Não remover:

--only-binary=:all:

Não alterar os pins.

Não modificar outro step.

============================================================
5. VALIDAÇÃO LOCAL
============================================================

Antes do commit:

1. confirmar diff limitado ao esperado;
2. executar data guard;
3. executar composed phase scope;
4. executar testes de governança já existentes;
5. executar perfil sintético C0 local.

Se houver parser YAML já disponível no ambiente SEM instalar
nova dependência, validar o arquivo também com ele.

Não instalar ferramenta adicional apenas para validar YAML.

Se qualquer outro problema surgir:

STOP.

============================================================
6. CHECKSUMS
============================================================

Verificar se:

.github/workflows/ti3-synthetic.yml

está incluído em algum manifesto de checksum ativo.

Se estiver:

atualizar exclusivamente sua entrada.

Se NÃO estiver:

não adicionar artificialmente nesta correção.

Não alterar:

checksums-pre-ti3-41d523e.sha256

Esse snapshot histórico permanece imutável.

============================================================
7. C0R1
============================================================

NÃO amend C0.

Criar exatamente UM novo commit corretivo:

fix(ci): quote ti3 binary-install command safely

ou mensagem semanticamente equivalente.

Nome conceitual:

C0R1

Registrar SHA completo.

O histórico deve permanecer:

C0
272695a...
    ↓
C0R1
<novo SHA>

============================================================
8. PUBLICAÇÃO
============================================================

Push fast-forward.

Não force-push.

NÃO fazer rerun do run:

35455982251

O novo SHA deve produzir novas execuções de CI.

============================================================
9. GATES REMOTOS
============================================================

Exigir:

deterministic-contracts=SUCCESS

scientific-synthetic-contracts=SUCCESS

ti3-synthetic-contracts=SUCCESS

O workflow TI3 deve desta vez:

- ser aceito pelo GitHub;
- criar seu job;
- executar seus steps;
- terminar SUCCESS.

Se o workflow novamente falhar antes dos jobs:

STOP.

Não fazer segundo commit corretivo automático.

Se criar job mas algum step falhar:

STOP.

Registrar step e erro exatos.

============================================================
10. FECHAMENTO DA GOVERNANÇA
============================================================

Se TODOS os jobs ficarem verdes:

registrar:

TI3_GOV_COMPAT=PASS
C0R1=PASS
C0R1_CI=PASS

LEGACY_SCOPE_GUARD=PASS
TI3_A0_FROZEN_GUARD=PASS
TI3_SCOPE_GUARD=PASS
PHASE_SCOPE_GUARD=PASS

A questão de governança deve ser considerada ENCERRADA.

Não criar GOV-COMPAT-v2/v3.

============================================================
11. RETOMADA AUTOMÁTICA PARA C1
============================================================

Se e somente se:

C0R1_CI=PASS

retomar diretamente TI3-A.

Não pedir nova autorização intermediária.

Usar os arquivos científicos locais já preparados.

Primeiro revalidar seus hashes.

Não refazer:

- target resolution;
- 52 sites;
- weak labels;
- deduplicação;
- planejamento geométrico;
- split;
- backgrounds;
- LBP;
- RF;
- métricas.

============================================================
12. C1 — METHOD FREEZE
============================================================

Preservar planejamento existente:

TRAIN:
17 POSITIVE
17 BACKGROUND

DEVELOPMENT:
8 POSITIVE
8 BACKGROUND

FINAL:
3 POSITIVE
3 BACKGROUND

PATCH:
65x65

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

PRIMARY_METRIC:
balanced_accuracy

SECONDARY:
accuracy
precision
recall
F1
confusion matrix

Criar C1:

feat(ti3): freeze canonical patch baseline protocol

Somente depois de todos os testes sintéticos verdes.

Ainda zero pixels.

============================================================
13. C1 CI
============================================================

Push fast-forward.

Exigir novamente:

todos os jobs obrigatórios SUCCESS.

Se qualquer CI C1 falhar:

STOP.

Nenhum pixel.

============================================================
14. EXECUÇÃO EXPERIMENTAL
============================================================

Somente com:

C1_CI=PASS

executar o real-support guard e então abrir somente:

TRAIN
DEVELOPMENT

Não abrir:

FINAL_TEST
ESM2
ESM5
ESM3
ESM6

============================================================
15. UMA EXECUÇÃO ML
============================================================

SCIENTIFIC_ML_RUNS máximo:

1

Executar:

LBP feature extraction
        ↓
Random Forest fit TRAIN
        ↓
DEVELOPMENT evaluation

Depois:

STOP científico.

Não ajustar modelo.

Não mudar seed.

Não repetir.

============================================================
16. FINAL TEST
============================================================

Manter:

ML_FINAL_TEST=
SEALED_WITH_HISTORICAL_NON_ML_EXPOSURE

ML_FINAL_TEST_EXECUTED=false

opens=0
bytes=0

============================================================
17. LIMITAÇÕES PRESERVADAS
============================================================

Não corrigir adaptativamente:

TRAIN:
ESM1 16 positivos / 6 backgrounds
ESM4 1 positivo / 11 backgrounds

FINAL:
3 positivos / 3 backgrounds

Registrar essas limitações.

Não redistribuir dados.

============================================================
18. ANTI-REFINAMENTO
============================================================

Esta autorização permite:

1 correção YAML
+
1 C0R1
+
1 nova CI
+
continuação condicional já planejada.

Não permite:

- segunda correção CI automática;
- nova arquitetura de governance;
- alteração científica;
- tuning;
- CNN;
- solutal no modelo;
- FINAL_TEST.

============================================================
19. REPORT
============================================================

Informar:

1. SHA C0;
2. linha problemática original;
3. correção aplicada;
4. diff C0..C0R1;
5. validações locais;
6. C0R1 SHA;
7. runs remotos novos;
8. presença do job ti3-synthetic-contracts;
9. resultado de cada job;
10. TI3_GOV_COMPAT;
11. C1 SHA, se criado;
12. C1 CI;
13. pixels TRAIN/DEV;
14. pixels FINAL;
15. scientific ML runs;
16. métricas TRAIN;
17. métricas DEV;
18. confusion matrix DEV;
19. limitações;
20. estado terminal.

SE C0R1 CI FICAR VERDE:
CONTINUE DIRETAMENTE PARA C1.

SE C1 CI FICAR VERDE:
EXECUTE UMA ÚNICA VEZ O BASELINE TRAIN/DEV.

NUNCA ABRA ML_FINAL_TEST.