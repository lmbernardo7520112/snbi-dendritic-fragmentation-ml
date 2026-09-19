# TI3-A — PREFLIGHT RECOVERY
# Resolução de BLOCKED_STAGED_DATA_GUARD + dependências ML
# e retomada da TI3-A já autorizada
#
# NÃO reiniciar ciência
# NÃO acessar pixels durante esta correção
# NÃO alterar target, split científico ou modelo congelado
# NÃO enfraquecer guardrails

Repositório:
snbi-dendritic-fragmentation-ml

Branch:
feat/ti3-canonical-dataset-baseline

HEAD atual esperado:
0f1284e86052e505e8ccfc9ceaecb58cb41065f2

============================================================
1. ESTADO CANÔNICO
============================================================

TI3_TARGET_RESOLUTION=PASS
TARGET_CONTRACT=FROZEN

WEAK_LABEL_STRATEGY=
HIGH_CONFIDENCE_PLUS_IGNORE

PUBLISHED_FRAGMENTATION_LOCATION_TARGET=
VALID_FOR_INTERNAL_ML

52 annotation_site_ids únicos.

G2_FRAG=PASS_DIRECT_RASTER_MAPPING
G2_SOLUTE=PASS

FINAL_TEST=NOT_DEFINED_NOT_OPENED
ML_RUNS=0

TI3-A RESUME foi iniciada, mas interrompida ANTES
de qualquer pixel por:

BLOCKED_STAGED_DATA_GUARD

Estado reportado:

HEAD=
0f1284e86052e505e8ccfc9ceaecb58cb41065f2

TARGET_RESOLUTION_CHECKPOINT=NOT_COMMITTED

INDEX=19_AUTHORIZED_FILES_STAGED

C1=NOT_CREATED
CI=NOT_RUN
EXPERIMENTAL_OPENS=0
SCIENTIFIC_ML_RUNS=0

Nenhum resultado científico foi produzido nesta tentativa.

============================================================
2. CAUSA DO BLOQUEIO
============================================================

O tracked-data guard rejeitou exatamente:

artifacts/evidence/TI3_TARGET_RESOLUTION/resolve.py

artifacts/evidence/TI3_TARGET_RESOLUTION/run_resolution.py

artifacts/evidence/TI3_TARGET_RESOLUTION/test_resolution.py

com:

artifact is not an approved text evidence type

A política existente permite sob artifacts/ somente:

.json
.md
.txt
.sha256

Esta política está correta.

NÃO modificar:

scripts/check_repository_data.py

.gitignore

TEXT_EVIDENCE_SUFFIXES

TEXT_ARTIFACT_PREFIXES

ou qualquer regra para fazer os .py passarem.

============================================================
3. PRINCÍPIO DA CORREÇÃO
============================================================

Os três scripts são artefatos históricos de reprodução da
TI3_TARGET_RESOLUTION já concluída.

Eles NÃO devem ser transformados artificialmente em código científico
ativo de TI3-A.

Preservá-los como SNAPSHOTS TEXTUAIS byte-idênticos.

Forma:

resolve.py
    ->
resolve.py.snapshot.txt

run_resolution.py
    ->
run_resolution.py.snapshot.txt

test_resolution.py
    ->
test_resolution.py.snapshot.txt

Os .py originais devem permanecer:

- locais;
- ignorados;
- inalterados.

Não deletar.

Não editar.

Não stagear.

============================================================
4. RECUPERAÇÃO DO INDEX
============================================================

O index contém atualmente os 19 arquivos autorizados staged.

Não resetar tudo.

Remover do index SOMENTE os três caminhos .py rejeitados,
sem modificar seus bytes no working tree.

Usar operação Git index-only, explicitamente limitada aos três caminhos.

Depois confirmar:

- os 16 textos previamente staged continuam staged;
- os três .py continuam fisicamente presentes;
- os três .py continuam ignorados;
- nenhum outro caminho foi alterado.

============================================================
5. CRIAR SNAPSHOTS TEXTUAIS
============================================================

Para cada script:

copiar o conteúdo byte-for-byte para o correspondente
.snapshot.txt.

Não acrescentar:

- cabeçalho;
- comentário;
- Markdown fence;
- timestamp;
- metadata dentro do snapshot.

O conteúdo do .snapshot.txt deve ter exatamente o mesmo SHA-256
dos bytes de conteúdo do .py original.

Criar também:

artifacts/evidence/TI3_TARGET_RESOLUTION/
script-snapshots.sha256

Esse manifesto deve registrar:

original_local_path
snapshot_tracked_path
sha256
byte_count

para os três scripts.

============================================================
6. VERIFICAÇÃO DE PRESERVAÇÃO
============================================================

Exigir para cada par:

SHA256(original.py)
==
SHA256(original.py.snapshot.txt)

e:

byte_count(original.py)
==
byte_count(snapshot.txt)

Se qualquer diferença existir:

STOP.

Não corrigir automaticamente conteúdo histórico.

============================================================
7. STAGING CORRIGIDO
============================================================

Stagear:

- os 16 arquivos textuais já autorizados;
- os três .snapshot.txt;
- script-snapshots.sha256.

NÃO stagear os três .py.

Executar novamente:

scripts/check_repository_data.py

Resultado obrigatório:

PASS.

Também executar:

git diff --cached --check

e inspeção exata dos paths staged.

Nenhum pixel.

============================================================
8. CHECKPOINT TARGET_RESOLUTION
============================================================

Se e somente se o guard passar:

criar UM commit preservando a resolução de target.

Mensagem sugerida:

docs(ti3): freeze fragmentation target resolution

Esse commit é documental/reprodutivo.

Registrar SHA:

TARGET_RESOLUTION_CHECKPOINT=<sha>

Depois confirmar:

- index limpo;
- .py históricos ainda locais/ignorados;
- snapshots tracked;
- hashes idênticos.

============================================================
9. SEGUNDO BLOQUEIO — DEPENDÊNCIAS ML
============================================================

Foi verificado que:

scikit-image
e
scikit-learn

não possuem metadata de instalação no ambiente atual.

Não interpretar isso como falha científica.

O baseline LBP + Random Forest exige um ambiente reproduzível.

============================================================
10. POLÍTICA DE DEPENDÊNCIAS TI3
============================================================

Não fazer instalação global.

Não usar:

sudo pip
pip --user
apt
conda global
modificação do Python do sistema.

Autoriza-se SOMENTE:

ambiente virtual local:

.venv/

dentro do repositório.

A pasta já deve permanecer não versionada.

============================================================
11. DEPENDÊNCIAS TOP-LEVEL CONGELADAS
============================================================

Criar um arquivo versionado apropriado, por exemplo:

requirements-ti3-ml.txt

com exatamente:

numpy==1.26.4
scipy==1.11.4
scikit-image==0.24.0
scikit-learn==1.5.2

Justificativa:

- preserva NumPy/SciPy já utilizados no projeto;
- scikit-image 0.24.0 suporta Python 3.12;
- scikit-learn 1.5.2 suporta Python 3.12;
- fornece local_binary_pattern e RandomForestClassifier
  compatíveis com o baseline curricular definido.

Não selecionar versões com base em desempenho.

============================================================
12. CRIAR AMBIENTE ISOLADO
============================================================

Antes de pixels:

criar/reutilizar somente:

.venv/

Se .venv já existir:

não sobrescrever cegamente.

Primeiro verificar:

- interpreter;
- Python version;
- packages instalados.

Se inconsistente com o ambiente TI3 requerido:

STOP e reporte.

Se inexistente:

criar com Python 3.12.

Instalar somente dentro de .venv:

requirements-ti3-ml.txt

Nenhuma instalação no sistema.

============================================================
13. REGISTRAR AMBIENTE
============================================================

Registrar em evidência:

- Python version;
- numpy version;
- scipy version;
- scikit-image version;
- scikit-learn version;
- joblib version;
- threadpoolctl version;
- demais dependências transitivas efetivamente resolvidas.

Não registrar:

- tokens;
- credentials;
- environment variables privadas.

Criar fingerprint textual reproduzível do ambiente.

============================================================
14. TESTE DE DEPENDÊNCIAS SEM PIXELS
============================================================

Antes de qualquer dado experimental:

testar imports:

numpy
scipy
skimage.feature.local_binary_pattern
sklearn.ensemble.RandomForestClassifier

Exigir versões top-level exatamente iguais às congeladas.

Executar pequenos testes sintéticos:

1. LBP em imagem sintética;
2. histograma 10 bins;
3. RandomForestClassifier com matriz sintética;
4. fit;
5. predict;
6. predict_proba;
7. determinismo com random_state=42.

Zero dados experimentais.

============================================================
15. CI
============================================================

Atualizar a CI de modo mínimo para incluir um job TI3 sintético
SEM dados experimentais.

O job deve usar Python 3.12 e instalar exatamente:

requirements-ti3-ml.txt

Depois executar:

- tracked-data guard;
- testes TI3 sintéticos;
- imports/versões;
- guards de target/split;
- nenhum acesso experimental.

Não alterar jobs científicos históricos de G2 exceto quando
estritamente necessário para compatibilidade.

============================================================
16. NÃO EXECUTAR PIXELS AINDA
============================================================

Esta autorização de recuperação operacional termina primeiro com:

TARGET_RESOLUTION_CHECKPOINT criado
+
guard PASS
+
dependências reproduzíveis
+
testes sintéticos PASS.

Depois disso, retomar o prompt TI3-A RESUME original
na fase de pré-registro do dataset/baseline.

Não pular diretamente para pixels.

============================================================
17. PRESERVAR CONTRATOS TI3-A
============================================================

Manter inalterados:

TARGET=
PUBLISHED_FRAGMENTATION_LOCATION_PRESENT

52 sites únicos

PATCH_RADIUS_PX=32
PATCH_SIDE_PX=65

split temporal previamente autorizado

LBP:
P=8
R=1
method=uniform

histograma:
10 bins
range=(0,10)
density=True

Random Forest:
n_estimators=100
random_state=42

PRIMARY_METRIC=
balanced_accuracy

SECONDARY_METRICS:
accuracy
precision
recall
F1
confusion matrix

Nenhum desses elementos pode ser alterado em resposta
ao bloqueio operacional.

============================================================
18. PROIBIÇÕES
============================================================

NÃO:

- modificar o data guard;
- modificar .gitignore para liberar .py;
- force-add dos .py dentro de artifacts/;
- mover scripts históricos para src/ fingindo que são código ativo;
- alterar target;
- alterar split;
- alterar patch size;
- alterar LBP;
- alterar Random Forest;
- instalar globalmente;
- abrir pixels;
- executar FINAL_TEST;
- iniciar CNN;
- usar solutal;
- fazer tuning.

============================================================
19. CONVERGÊNCIA
============================================================

A incompatibilidade atual possui solução única:

.py históricos em artifacts/
        ↓
snapshots textuais aprovados
        ↓
guard PASS

e:

dependências ausentes
        ↓
.venv isolado
        ↓
dependências pinadas
        ↓
testes sintéticos
        ↓
CI
        ↓
retomar TI3-A

Não abrir uma nova fase científica.

Não criar TI3-A0.2.

Não redefinir target.

============================================================
20. ESTADO ESPERADO DESTA RECUPERAÇÃO
============================================================

Se tudo passar:

BLOCKED_STAGED_DATA_GUARD=RESOLVED
TARGET_RESOLUTION_CHECKPOINT=COMMITTED
TARGET_RESOLUTION_SCRIPTS=PRESERVED_AS_TEXT_SNAPSHOTS
TRACKED_DATA_GUARD=PASS
TI3_ML_ENVIRONMENT=READY
TI3_ML_DEPENDENCIES=PINNED
TI3_SYNTHETIC_DEPENDENCY_TESTS=PASS
EXPERIMENTAL_OPENS=0
SCIENTIFIC_ML_RUNS=0
ML_FINAL_TEST=NOT_DEFINED_NOT_OPENED
TI3_A_RESUME_READY=true

Depois:

CONTINUE TI3-A RESUME
a partir do próximo gate ainda não executado.

============================================================
21. SE HOUVER NOVO BLOQUEIO
============================================================

Se:

- snapshot divergir;
- guard continuar bloqueado;
- dependência não puder ser instalada em .venv;
- versão incompatível;
- teste sintético falhar;
- CI pré-pixel falhar;

STOP.

Não acessar pixels.

Não improvisar pacote alternativo.

Não substituir Random Forest por implementação caseira.

Não substituir LBP por implementação ad hoc.

Reporte o bloqueio exato.

============================================================
22. REPORT
============================================================

Informar:

1. HEAD inicial;
2. três .py removidos apenas do index;
3. confirmação dos .py locais intactos;
4. hashes dos três snapshots;
5. igualdade byte-for-byte;
6. paths staged finais;
7. data guard;
8. TARGET_RESOLUTION_CHECKPOINT SHA;
9. Python do .venv;
10. versões top-level;
11. versões transitivas relevantes;
12. testes LBP sintéticos;
13. testes RF sintéticos;
14. alterações de CI;
15. CI, se executada;
16. experimental opens;
17. scientific ML runs;
18. FINAL_TEST;
19. worktree/index;
20. próximo gate de TI3-A.

EXECUTE SOMENTE ESTA RECUPERAÇÃO E,
SE TODOS OS GATES PRÉ-PIXEL PASSAREM,
RETOME TI3-A RESUME EXATAMENTE DO PONTO SEGUINTE.
