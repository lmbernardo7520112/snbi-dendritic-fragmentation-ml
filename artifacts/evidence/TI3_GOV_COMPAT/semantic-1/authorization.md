# TI3-GOV-COMPAT — SEMANTIC SCOPE RECLASSIFICATION
# + retomada condicional de TI3-A
#
# Correção terminal da classificação LEGACY_PRE_TI3
# após BLOCKED_LEGACY_BASELINE_CLASSIFICATION.
#
# NÃO modificar o checker TI2.
# NÃO excluir silenciosamente paths.
# NÃO renomear arquivos para escapar de regras.
# NÃO acessar pixels antes de C1 + CI verde.
# NÃO fazer tuning.
# CONVERGÊNCIA OBRIGATÓRIA.

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

TI3_ML_ENVIRONMENT=READY

TARGET_CONTRACT=FROZEN

TI3_GOV_COMPAT=
BLOCKED_LEGACY_BASELINE_CLASSIFICATION

LEGACY_SCOPE_GUARD=BLOCKED

TI3_SCOPE_GUARD=
NOT_IMPLEMENTED_NOT_RUN_STOP

PHASE_SCOPE_GUARD=
NOT_IMPLEMENTED_NOT_RUN_STOP

C0=NOT_CREATED
C1=NOT_CREATED
C2=NOT_CREATED

CI=NOT_RUN

EXPERIMENTAL_OPENS=0
EXPERIMENTAL_BYTES=0
SCIENTIFIC_ML_RUNS=0

ML_FINAL_TEST=
SEALED_WITH_HISTORICAL_NON_ML_EXPOSURE

ML_FINAL_TEST_EXECUTED=false

G2_FRAG=PASS_DIRECT_RASTER_MAPPING
G2_SOLUTE=PASS

============================================================
2. BLOQUEIO QUE ESTA AUTORIZAÇÃO RESOLVE
============================================================

O manifesto cronológico anterior classificou todos os
79 arquivos Python tracked no HEAD como:

LEGACY_PRE_TI3.

Isso é semanticamente excessivo.

Quatro desses arquivos pertencem comprovadamente à fase
TI3-A0 já versionada:

scripts/extract_ti3_a0_annotations.py

scripts/inspect_ti3_a0_annotations.py

src/snbi_fragmentation/ti3_a0_annotations.py

tests/test_ti3_a0_annotations.py

Os três primeiros são corretamente rejeitados pelo checker
TI-2 porque contêm o componente "annotations".

O quarto pertence ao mesmo domínio TI3-A0, embora a regra
nominal do checker TI2 não alcance tests/.

Portanto:

esses QUATRO arquivos NÃO pertencem semanticamente ao domínio
LEGACY_TI2.

============================================================
3. PRINCÍPIO DA CORREÇÃO
============================================================

Não alterar:

scripts/check_ti2_scope.py

A correção ocorre ANTES de sua aplicação, mediante classificação
de domínio explícita e exaustiva.

Definir três classes:

LEGACY_TI2

TI3_A0_FROZEN

TI3_ACTIVE

Nenhum path Python relevante pode existir fora dessas classes.

As classes devem ser:

- explicitamente versionadas;
- mutuamente exclusivas;
- coletivamente exaustivas;
- auditáveis por path e blob SHA.

============================================================
4. PRESERVAR A TENTATIVA BLOQUEADA
============================================================

Os artefatos produzidos pela tentativa anterior devem permanecer
imutáveis.

Preservar:

artifacts/evidence/TI3_GOV_COMPAT/

incluindo:

authorization.md
preflight.json
legacy-scope-gate.json
results.json
commands.json
verification.json
execution-report.md

Não reescrever o BLOCKED como PASS.

============================================================
5. MANIFESTO CRONOLÓGICO ANTERIOR
============================================================

O arquivo local:

configs/governance/pre-ti3-code-scope.json

foi construído sob a regra cronológica que levou ao bloqueio.

Ele NÃO deve ser usado como classificação normativa futura.

Preservar uma cópia textual exata dele na evidência, por exemplo:

artifacts/evidence/TI3_GOV_COMPAT/
pre-ti3-code-scope.blocked-snapshot.json

Registrar:

- SHA-256;
- tamanho;
- 79 entradas;
- razão de supersessão classificatória.

Não apagar a evidência histórica.

O arquivo normativo novo terá outro nome.

============================================================
6. SNAPSHOT DE CHECKSUMS HISTÓRICOS
============================================================

Preservar o snapshot já criado:

artifacts/evidence/TI2/
checksums-pre-ti3-41d523e.sha256

Ele contém 95 entradas e representa a fronteira histórica.

Não alterar um byte desse snapshot.

Verificar novamente seu SHA esperado:

e7d30ca626088e1e3c58c8702b96e9afc388ee75c48011d885393230dc7d245d

Se divergir:

STOP.

============================================================
7. CLASSIFICAÇÃO NORMATIVA NOVA
============================================================

Criar:

configs/governance/phase-scope-v1.json

O schema deve incluir:

schema_version
baseline_sha
domains

baseline_sha:

41d523e038e844588ee7724e07b00f75bdf29fdc

Domínios:

LEGACY_TI2
TI3_A0_FROZEN
TI3_ACTIVE

============================================================
8. LEGACY_TI2
============================================================

LEGACY_TI2 deve conter todos os arquivos Python tracked
do corpus de 79, EXCETO exatamente os quatro TI3_A0_FROZEN.

Contagem esperada:

79 - 4 = 75.

Não hardcode a contagem como substituto da enumeração.

Enumerar explicitamente:

path
git_mode
blob_sha

Para cada arquivo.

Nenhum pattern broad allowlist.

============================================================
9. TI3_A0_FROZEN
============================================================

Classificar EXATAMENTE:

scripts/extract_ti3_a0_annotations.py

scripts/inspect_ti3_a0_annotations.py

src/snbi_fragmentation/ti3_a0_annotations.py

tests/test_ti3_a0_annotations.py

Para cada um registrar:

path
git_mode
blob_sha
classification="TI3_A0_FROZEN"
origin_phase="TI3_A0"
mutable=false

Obter os blob SHAs diretamente do Git no HEAD esperado.

Não confiar em hashes inventados no prompt.

============================================================
10. REGRA TI3_A0_FROZEN
============================================================

Esses quatro arquivos não são auditados como TI2.

Eles também NÃO recebem permissão genérica de TI3 ativo.

Seu contrato é mais restritivo:

- path deve ser exatamente igual;
- Git mode deve ser exatamente igual;
- blob SHA deve ser exatamente igual ao baseline;
- conteúdo não pode mudar;
- arquivo não pode ser removido;
- arquivo não pode ser renomeado;
- arquivo adicional não pode entrar nessa classe.

Qualquer divergência:

FROZEN_A0_SCOPE=BLOCKED

STOP.

============================================================
11. NÃO É UMA EXCEÇÃO NOMINAL
============================================================

É proibido implementar algo como:

if "ti3_a0" in path:
    skip

ou:

if "annotations" in path and path.startswith(...):
    ignore

A classificação deve decorrer SOMENTE do manifesto explícito:

phase-scope-v1.json

e dos quatro path+blob exatos.

============================================================
12. TI3_ACTIVE
============================================================

TI3_ACTIVE representa código novo da baseline TI3-A.

Utilizar a allowlist exata dos paths já preparados localmente,
conforme o inventário terminal anterior.

Não usar globs amplos como:

src/**/ti3*
scripts/ti3*

Cada path deve ser enumerado explicitamente.

Paths TI3_ACTIVE ausentes antes de C1 podem ser declarados como:

state="PLANNED"

e, após staging/C1:

state="TRACKED"

O checker deve verificar coerência desse estado.

============================================================
13. INVARIANTE DE PARTIÇÃO
============================================================

Para o inventário Python relevante:

ALL_RELEVANT_CODE
=
LEGACY_TI2
∪
TI3_A0_FROZEN
∪
TI3_ACTIVE_TRACKED

Exigir:

LEGACY_TI2 ∩ TI3_A0_FROZEN = ∅

LEGACY_TI2 ∩ TI3_ACTIVE = ∅

TI3_A0_FROZEN ∩ TI3_ACTIVE = ∅

UNCLASSIFIED_PATHS = 0

DUPLICATELY_CLASSIFIED_PATHS = 0

Qualquer violação:

STOP.

============================================================
14. LEGACY CHECKER
============================================================

Executar:

check_ti2_scope.audit(
    entries=LEGACY_TI2_ENTRIES
)

O checker:

scripts/check_ti2_scope.py

permanece byte-idêntico.

Resultado exigido:

PASS.

Não alterar seu BLOCKED_COMPONENTS.

Não alterar BLOCKED_IMPORTS.

Não alterar dependências TI2.

============================================================
15. A0 FROZEN CHECKER
============================================================

Implementar no compositor, ou em helper dedicado,
um guard:

audit_ti3_a0_frozen()

Ele verifica somente:

- os quatro paths;
- modes;
- blobs;
- presença;
- imutabilidade.

Não precisa reinterpretar sua ciência.

Não executa os scripts.

Não abre pixels.

Resultado exigido:

PASS.

============================================================
16. TI3 CHECKER
============================================================

Criar:

scripts/check_ti3_scope.py

Ele deve operar exclusivamente em:

TI3_ACTIVE_ENTRIES.

Usar allowlist explícita.

Permitir somente dependências ML congeladas:

numpy==1.26.4
scipy==1.11.4
scikit-image==0.24.0
scikit-learn==1.5.2

Imports TI3 permitidos conforme necessidade:

numpy
scipy
skimage
sklearn

Continuar proibindo:

torch
torchvision
tensorflow
keras
xgboost
lightgbm
catboost
transformers
fastai

salvo futura autorização explícita.

============================================================
17. REQUIREMENTS TI3
============================================================

Validar:

requirements-ti3-ml.txt

com exatamente:

numpy==1.26.4
scipy==1.11.4
scikit-image==0.24.0
scikit-learn==1.5.2

Não adicionar dependências.

pyproject.toml [project].dependencies
permanece vazio para preservar o contrato legacy.

============================================================
18. COMPOSITOR GLOBAL
============================================================

Criar:

scripts/check_phase_scope.py

Fluxo obrigatório:

1. data guard GLOBAL;
2. ler inventário tracked;
3. carregar phase-scope-v1.json;
4. verificar partição exaustiva/disjunta;
5. verificar LEGACY blob/mode expectations;
6. executar TI2 checker sobre LEGACY somente;
7. verificar TI3_A0_FROZEN exact blobs;
8. executar TI3 checker sobre TI3_ACTIVE;
9. rejeitar qualquer path não classificado;
10. agregar todos os resultados.

PASS somente se:

DATA_GUARD=PASS
LEGACY_SCOPE=PASS
A0_FROZEN_SCOPE=PASS
TI3_SCOPE=PASS
PARTITION=PASS

============================================================
19. TESTES ADVERSARIAIS OBRIGATÓRIOS
============================================================

Adicionar testes sintéticos/documentais que provem:

A)
um dos quatro A0 muda um byte
→ FAIL

B)
um A0 é renomeado
→ FAIL

C)
quinto arquivo tenta entrar em A0_FROZEN
→ FAIL

D)
um A0 é classificado também como LEGACY
→ FAIL

E)
um path não recebe classe
→ FAIL

F)
um path recebe duas classes
→ FAIL

G)
sklearn em LEGACY
→ FAIL

H)
sklearn em TI3_ACTIVE allowlisted
→ PASS

I)
torch em TI3_ACTIVE
→ FAIL

J)
novo annotations.py não listado
→ FAIL

K)
data experimental tracked
→ FAIL

L)
symlink
→ FAIL

============================================================
20. CORREÇÃO CONCEITUAL DO MANIFESTO
============================================================

A classificação antiga:

classification=LEGACY_PRE_TI3

significava apenas:

“já tracked no baseline”.

Ela NÃO deve ser reinterpretada como:

“pertence ao domínio científico TI2”.

Registrar isso claramente.

A classificação normativa atual passa a ser semântica.

============================================================
21. CI
============================================================

Somente após todos os guards locais PASS:

modificar minimamente:

.github/workflows/ci.yml

No local onde o workflow executava globalmente:

scripts/check_ti2_scope.py

usar:

scripts/check_phase_scope.py

O TI2 checker continua executado INTERNAMENTE
sobre LEGACY_TI2.

Não remover nenhum controle histórico.

============================================================
22. CHECKSUMS ATIVOS
============================================================

O snapshot histórico permanece intacto.

Se arquivos atualmente listados no manifesto ativo mudarem,
por exemplo:

.github/workflows/ci.yml

atualizar SOMENTE os hashes correspondentes em:

artifacts/evidence/TI2/checksums.sha256

Não alterar entradas de arquivos que não mudaram.

Registrar old_hash/new_hash/path.

============================================================
23. C0 — ÚNICO COMMIT DE GOVERNANÇA
============================================================

Se todos os gates locais passarem:

criar exatamente UM C0.

Mensagem:

chore(governance): partition legacy a0 and ti3 scopes

C0 pode conter:

- evidência da tentativa bloqueada;
- snapshot cronológico bloqueado;
- phase-scope-v1.json;
- snapshot histórico checksums;
- check_ti3_scope.py;
- check_phase_scope.py;
- testes de governança;
- requirements TI3, se necessário ao guard;
- atualização mínima da CI;
- atualização mínima do checksum ativo;
- documentação direta de governança.

Não incluir ainda:

- execução científica;
- resultados ML;
- pixels;
- C1 baseline científico.

============================================================
24. GATES C0
============================================================

Antes de commit:

GLOBAL_DATA_GUARD=PASS

SCOPE_PARTITION=PASS

LEGACY_FILE_COUNT=75

A0_FROZEN_FILE_COUNT=4

UNCLASSIFIED=0

DUPLICATE_CLASSIFICATION=0

LEGACY_SCOPE_GUARD=PASS

TI3_A0_FROZEN_GUARD=PASS

TI3_SCOPE_GUARD=PASS

PHASE_SCOPE_GUARD=PASS

HISTORICAL_CHECKSUM_SNAPSHOT=PASS

ACTIVE_CHECKSUMS=PASS

GOVERNANCE_TESTS=PASS

LEGACY_TESTS=PASS

EXPERIMENTAL_OPENS=0

============================================================
25. PUSH / CI C0
============================================================

Fazer push fast-forward.

Sem force-push.

Executar CI.

Exigir todos os jobs obrigatórios verdes.

Se C0 CI falhar:

STOP.

Não criar C1.

Não abrir pixels.

Não fazer segundo corretivo automático.

============================================================
26. RETOMADA AUTOMÁTICA DE TI3-A
============================================================

SE E SOMENTE SE:

C0_CI=PASS

retomar TI3-A exatamente do ponto anterior.

Não refazer:

- target resolution;
- 52 sites;
- deduplicação;
- weak labels;
- planejamento geométrico;
- split;
- backgrounds;
- LBP;
- RF;
- métricas.

Apenas revalidar hashes/contratos.

============================================================
27. ESTADO DO PLANEJAMENTO CIENTÍFICO
============================================================

Preservar:

TRAIN:
17 POSITIVE
17 BACKGROUND

DEVELOPMENT:
8 POSITIVE
8 BACKGROUND

FINAL_TEST:
3 POSITIVE
3 BACKGROUND

Não redistribuir.

Não aumentar FINAL.

============================================================
28. LIMITAÇÃO DE TRAIN
============================================================

Preservar a limitação já observada:

TRAIN ESM1:
16 positivos / 6 backgrounds

TRAIN ESM4:
1 positivo / 11 backgrounds

Isso pode permitir confusão entre:

classe
e
aquisição/condição.

NÃO reselecionar backgrounds agora.

Registrar essa limitação no CLAIM_SCOPE e no relatório.

Uma eventual correção exigiria nova decisão científica,
não pertence a esta compatibilização.

============================================================
29. C1 — METHOD FREEZE
============================================================

Após C0 CI verde:

stagear exatamente os arquivos TI3-A científicos previamente
preparados e allowlisted.

Executar:

data guard
phase scope
legacy suite
TI3 synthetic suite

Se tudo PASS:

criar C1:

feat(ti3): freeze canonical patch baseline protocol

Sem pixels ainda.

============================================================
30. CI C1
============================================================

Push fast-forward.

Exigir CI completamente verde.

Se falhar:

STOP.

Zero pixels.

============================================================
31. EXECUÇÃO TRAIN/DEV
============================================================

Somente com C1 + CI verde:

executar real-support guard.

Abrir SOMENTE TRAIN e DEVELOPMENT.

Não abrir FINAL_TEST.

Não abrir ESM2/ESM5.

Não abrir ESM3/ESM6.

Baseline:

PATCH=65x65

LBP:
P=8
R=1
uniform
10 bins
range 0..10
density=True

RF:
100 árvores
seed 42
defaults restantes congelados.

============================================================
32. UMA EXECUÇÃO CIENTÍFICA
============================================================

SCIENTIFIC_ML_RUNS <= 1

Executar:

fit TRAIN
+
evaluate DEVELOPMENT

Depois:

STOP científico.

Nenhum tuning.

Nenhuma segunda seed.

============================================================
33. MÉTRICAS
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

TP FP TN FN

Não existe threshold mínimo de desempenho para
TI3_A_BASELINE=PASS.

============================================================
34. FINAL_TEST
============================================================

Preservar:

ML_FINAL_TEST=
SEALED_WITH_HISTORICAL_NON_ML_EXPOSURE

ML_FINAL_TEST_EXECUTED=false

FINAL_TEST opens=0
FINAL_TEST bytes=0

Mesmo se DEV for excelente.

============================================================
35. SOLUTAL E CNN
============================================================

Não executar:

CNN

nem:

STRUCTURAL_PLUS_RELATIVE_SOLUTE

nesta autorização.

Preservar:

TI3_B_AUTHORIZED=false

SOLUTAL_MODEL_INPUT=NOT_USED

============================================================
36. ANTI-REFINAMENTO
============================================================

Se a classificação semântica:

75 LEGACY
+
4 A0_FROZEN
+
TI3_ACTIVE

não conseguir produzir todos os guards PASS:

STOP.

NÃO criar quarta taxonomia.

NÃO criar exceção adicional.

NÃO mudar checker TI2.

NÃO renomear arquivos.

NÃO esconder paths.

Esse é o limite de convergência da migração.

============================================================
37. ESTADO FINAL ESPERADO
============================================================

Se toda a sequência passar:

TI3_GOV_COMPAT=PASS

SCOPE_PARTITION=PASS

LEGACY_TI2_FILES=75
TI3_A0_FROZEN_FILES=4

LEGACY_SCOPE_GUARD=PASS
TI3_A0_FROZEN_GUARD=PASS
TI3_SCOPE_GUARD=PASS
PHASE_SCOPE_GUARD=PASS

C0=PASS
C0_CI=PASS

C1=PASS
C1_CI=PASS

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
38. REPORT FINAL
============================================================

Informar:

1. HEAD inicial;
2. snapshot do bloqueio anterior;
3. 79 paths cronológicos;
4. 75 LEGACY_TI2 paths;
5. 4 TI3_A0_FROZEN paths;
6. blob SHA dos 4 A0;
7. TI3_ACTIVE paths;
8. unclassified count;
9. duplicate classification count;
10. legacy guard;
11. A0 frozen guard;
12. TI3 guard;
13. phase guard;
14. governance tests;
15. historical checksum snapshot;
16. active checksum changes;
17. C0 SHA;
18. C0 CI;
19. C1 SHA;
20. C1 CI;
21. real-support result;
22. TRAIN/DEV opens;
23. FINAL opens;
24. scientific ML runs;
25. TRAIN metrics;
26. DEV metrics;
27. DEV confusion matrix;
28. statistical limitations;
29. C2 if evidence-only;
30. terminal state.

EXECUTE ESTA CLASSIFICAÇÃO SEMÂNTICA UMA ÚNICA VEZ.

SE C0 CI PASSAR:
CONTINUE PARA C1.

SE C1 CI PASSAR:
EXECUTE UMA ÚNICA VEZ O BASELINE TRAIN/DEV.

NUNCA ABRA ML_FINAL_TEST.