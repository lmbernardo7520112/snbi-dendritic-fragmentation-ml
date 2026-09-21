# STUDY2-D — AUTHORIZED CI COMPATIBILITY REPAIR
#
# AUTORIZAÇÃO COMPLEMENTAR APÓS STOP CORRETO DA SEÇÃO 51.
#
# Objetivo único:
# reparar a incompatibilidade entre quatro testes Study2-D que atravessam
# TrainCorpusAccess.load() e o histórico deterministic-contracts executado
# com `python -S`, SEM alterar qualquer aspecto científico de Study2-D.
#
# NÃO É NOVO METHOD SEARCH.
# NÃO É RETRY CIENTÍFICO.
# NÃO É AUTORIZAÇÃO PARA FIT ANTES DA NOVA CI 10/10 VERDE.

REPOSITÓRIO:
snbi-dendritic-fragmentation-ml

BRANCH:
feat/study2d-data-centric-bridge

METHOD_FREEZE_ORIGINAL=
21400de67d21901aeb8e5abac528689fc39169fa

STUDY2_C_MERGE_BASE=
ec97cb5041ef35d4f6c9a79b54d756d6fbee674f

CI_FAILURE_RUN=
35649522192

============================================================
1. ESTADO E AUTORIZAÇÃO
============================================================

Confirmar inicialmente:

HEAD local =
21400de67d21901aeb8e5abac528689fc39169fa

remote branch =
mesmo SHA

index limpo
tracked worktree limpo

SCIENTIFIC_STUDY2D_RUNS=0

Nenhum:

- fit científico;
- feature extraction experimental;
- DEV access;
- TEST access;
- TEST feature computation;
- source video access.

Se divergir:

STOP.

Esta autorização cobre APENAS:

CI_COMPATIBILITY_REPAIR.

============================================================
2. DIAGNÓSTICO CONGELADO
============================================================

O job histórico deterministic-contracts usa:

PYTHONPATH=src python -S -B -m unittest discover -s tests -v

Portanto site-packages não estão disponíveis.

Quatro testes em:

tests/test_study2d_io.py

atravessam:

TrainCorpusAccess.load()

que importa NumPy lazymente.

Testes afetados exatamente:

1. test_exact_directed_reads_and_hashes
2. test_short_read_closes
3. test_hash_mismatch_closes
4. test_fingerprint_change_denied

Falha observada:

ModuleNotFoundError:
No module named 'numpy'

Não reinterpretar essa falha como:

- problema de dataset;
- problema dos containers;
- problema dos hashes;
- problema do RF;
- problema do LBP;
- problema do desenho de atribuição.

============================================================
3. REPARO DOS QUATRO TESTES
============================================================

Modificar SOMENTE o necessário em:

tests/test_study2d_io.py

Adicionar import stdlib:

import importlib.util

Definir uma única condição, por exemplo:

NUMPY_AVAILABLE = importlib.util.find_spec("numpy") is not None

Aplicar:

@unittest.skipUnless(
    NUMPY_AVAILABLE,
    "optional NumPy unavailable; fully required by Study2-D scientific synthetic CI"
)

EXATAMENTE aos quatro testes listados.

Não aplicar skip à classe inteira.

Não aplicar skip aos outros 25 testes de I/O.

Não tornar skip dependente de:

- plataforma;
- branch;
- CI;
- variável secreta;
- resultado anterior;
- performance.

============================================================
4. COBERTURA OBRIGATÓRIA
============================================================

No perfil stdlib:

os quatro skips são permitidos porque a dependência
NumPy foi deliberadamente removida por `python -S`.

No job dedicado:

study2d-synthetic-contracts

NumPy está instalado.

Portanto:

todos os testes Study2-D devem executar.

ZERO skips Study2-D no job dedicado.

Se algum dos quatro testes for skipped no job dedicado:

STOP.

Não executar ciência.

============================================================
5. NÃO ALTERAR O WORKFLOW HISTÓRICO
============================================================

NÃO instalar NumPy em deterministic-contracts.

NÃO remover `-S`.

NÃO alterar seu propósito histórico.

NÃO editar workflow para mascarar o conflito.

O reparo pertence ao contrato dos novos testes,
não ao job histórico.

============================================================
6. FREEZE ORIGINAL É IMUTÁVEL HISTORICAMENTE
============================================================

O SHA:

21400de67d21901aeb8e5abac528689fc39169fa

continua sendo denominado:

STUDY2_D_METHOD_FREEZE_ORIGINAL.

Não amend.

Não rebase.

Não force-push.

Criar um único filho direto:

<CI_REPAIR_SHA>

A cadeia obrigatória será:

ec97cb5041ef35d4f6c9a79b54d756d6fbee674f
  ↓
21400de67d21901aeb8e5abac528689fc39169fa
  ↓
<CI_REPAIR_SHA>

============================================================
7. PRE-FLIGHT ANCESTRY
============================================================

Ajustar apenas a lógica operacional necessária em:

src/snbi_fragmentation/study2d_execution.py

para aceitar EXATAMENTE a cadeia acima.

No HEAD de reparo exigir:

HEAD^ ==
21400de67d21901aeb8e5abac528689fc39169fa

e

HEAD^^ ==
ec97cb5041ef35d4f6c9a79b54d756d6fbee674f

Não aceitar:

- ancestral arbitrário;
- merge intermediário;
- segundo repair commit;
- branch diferente;
- bypass de CI.

============================================================
8. DIFF ALLOWLIST
============================================================

Entre METHOD_FREEZE_ORIGINAL e CI_REPAIR_SHA,
permitir somente paths estritamente necessários:

- tests/test_study2d_io.py
- tests/test_study2d_execution.py
- src/snbi_fragmentation/study2d_execution.py
- configs/governance/phase-scope-v1.json
- evidence/proofs necessários do reparo
- hashes/freeze operacionais estritamente necessários

Se aparecer alteração em:

- study2d_design.py
- study2d_models.py
- study2d_io.py científico
- TRAIN_INPUT_MANIFEST.json
- STUDY2_D_ATTRIBUTION_DESIGN.json
- STUDY2_D_FIT_BUDGET.json
- MODEL_CONTRACT.json
- folds Study2-C
- caches
- dataset
- RF params
- LBP params

STOP.

============================================================
9. DECISÃO ADITIVA
============================================================

Criar evidência textual explícita, por exemplo:

CI_REPAIR_AUTHORIZATION.md
CI_REPAIR_DIFF.json
CI_REPAIR_VERIFICATION.json

Registrar:

REPAIR_CLASS=
TEST_ENVIRONMENT_COMPATIBILITY_ONLY

SCIENTIFIC_METHOD_CHANGED=false
DATASET_CHANGED=false
TRAIN_ALLOWLIST_CHANGED=false
FOLDS_CHANGED=false
GROUPS_CHANGED=false
FEATURES_CHANGED=false
MODEL_CHANGED=false
RF_PARAMETERS_CHANGED=false
FIT_BUDGET_CHANGED=false
METRICS_CHANGED=false
DEV_AUTHORIZATION_CHANGED=false
TEST_AUTHORIZATION_CHANGED=false

METHOD_FREEZE_ORIGINAL=
21400de67d21901aeb8e5abac528689fc39169fa

============================================================
10. METHOD_FREEZE / SYNTHETIC PROOFS
============================================================

Se a implementação do preflight exige atualização de:

METHOD_FREEZE.json
SYNTHETIC_TESTS.json

pode fazê-la SOMENTE como freeze operacional do repair.

O registro deve preservar explicitamente:

parent_method_freeze_sha =
21400de67d21901aeb8e5abac528689fc39169fa

e declarar que nenhum contrato científico mudou.

Não sobrescrever o significado histórico do freeze original.

Git deve preservar a versão anterior.

============================================================
11. TESTES DE ANCESTRALIDADE
============================================================

Em:

tests/test_study2d_execution.py

ajustar exclusivamente fixtures/asserts necessárias para provar:

ACEITO:

HEAD^ = METHOD_FREEZE_ORIGINAL
HEAD^^ = STUDY2_C_MERGE_BASE

RECUSAR:

- parent errado;
- grandparent errado;
- ancestry mais longa;
- merge inesperado;
- HEAD direto no BASE;
- segundo repair child não autorizado.

Nenhum array experimental.

Nenhum fit científico.

============================================================
12. TESTES LOCAIS PRÉ-COMMIT
============================================================

Executar primeiro o perfil stdlib equivalente.

Esperado:

- nenhum ERROR;
- nenhum FAILURE;
- exatamente os quatro novos skips Study2-D atribuíveis
  à indisponibilidade de NumPy;
- restante dos contratos executando normalmente.

Depois executar o perfil Study2-D dedicado com dependências pinadas.

Esperado:

- todos os testes Study2-D PASS;
- ZERO skips;
- ZERO errors;
- ZERO failures.

Não executar:

- runner científico;
- planner novamente;
- feature extraction experimental;
- 100 fits.

============================================================
13. COMMIT ÚNICO
============================================================

Criar exatamente UM commit corretivo filho do freeze.

Mensagem sugerida:

test(study2d): repair stdlib CI compatibility

Não amend.
Não squash local.
Não rebase.
Não force.

Publicar por push fast-forward.

============================================================
14. NOVA CI
============================================================

A nova CI deve pertencer ao:

CI_REPAIR_SHA

e não ao SHA antigo.

Não rerun do job antigo como substituto.

Exigir:

TODOS OS 10 JOBS
+
TODOS OS PASSOS RELEVANTES

SUCCESS.

No deterministic-contracts:

os quatro testes NumPy-dependent podem aparecer SKIPPED
por causa de `python -S`.

No study2d-synthetic-contracts:

os mesmos quatro testes DEVEM PASSAR.

ZERO skips Study2-D nesse job.

============================================================
15. GATE CIENTÍFICO
============================================================

Somente se:

CI_REPAIR=PASS
CI_JOBS=10/10_SUCCESS
STUDY2D_DEDICATED_SKIPS=0
SCIENTIFIC_STUDY2D_RUNS=0

então:

executar o preflight real.

O preflight deve verificar:

- ancestry exata;
- original freeze;
- repair diff;
- hashes;
- TRAIN allowlist 10.907;
- 64 grupos;
- fold hash histórico;
- RF_REFERENCE;
- LBP20;
- fit budget 100;
- CI proof no novo SHA;
- DEV=forbidden;
- TEST=forbidden.

Se preflight falhar:

STOP.

============================================================
16. EXECUÇÃO CIENTÍFICA APÓS CI VERDE
============================================================

Somente após todos os gates anteriores:

executar UMA única CLI Study2-D.

Ela pode realizar exatamente:

100 distinct RF fits

já pré-registrados.

Nenhum fit 101.

Nenhum retry.

Nenhum adaptive branching.

Nenhuma nova condição.

Nenhum DEV.

Nenhum TEST.

Nenhum vídeo.

============================================================
17. PÓS-RUN
============================================================

Se a ciência concluir:

produzir somente os outputs já autorizados pelo
AUTHORIZATION.md.

Depois:

evidence-only checkpoint.

Nenhuma nova ciência.

Nenhum merge automático.

============================================================
18. REPORT AO AUTOR
============================================================

Antes de prosseguir além do reparo, informar:

1. confirmação do freeze original;
2. nomes dos quatro testes reparados;
3. diff exato;
4. arquivos alterados;
5. confirmação de scientific-method unchanged;
6. resultados stdlib;
7. número exato de skips stdlib;
8. resultados do job dedicado;
9. confirmação de zero skips dedicado;
10. CI_REPAIR_SHA;
11. ancestry SHA parent/grandparent;
12. todos os 10 jobs;
13. estado da CI;
14. SCIENTIFIC_STUDY2D_RUNS;
15. DEV_ROWS_READ;
16. TEST_ROWS_READ;
17. decisão de liberação para preflight/ciência.

Se 10/10 CI não estiver verde:

STOP.

============================================================
AUTORIZAÇÃO
============================================================

AUTHORIZED_CI_REPAIR=true

SCIENTIFIC_EXECUTION_AUTHORIZED=
CONDITIONAL_ON_NEW_10_OF_10_GREEN_CI

CURRENT_AUTHORIZED_ACTIVITY=
APPLY_EXACT_CI_COMPATIBILITY_REPAIR

EXECUTE O REPARO LIMITADO.