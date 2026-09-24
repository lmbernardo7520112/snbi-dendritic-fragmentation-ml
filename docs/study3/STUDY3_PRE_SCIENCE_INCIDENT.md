# Study3 pre-science incident

The author classified and accepted this incident for bounded recovery in
`/STUDY3-CNN-PRE-SCIENCE-RECOVERY-AND-FREEZE`. This phase authorizes documentation,
interpreter bootstrap, implementation, synthetic verification, one method freeze
commit, fast-forward publication and pre-science CI only. It does not authorize
the scientific runner, experimental payload reads or a scientific receipt.

```text
INCIDENT_CLASS=PRE_SCIENCE_METADATA_SEQUENCE_DEVIATION
EXPOSURE_DESCRIPTION=TEXTUAL_TRAIN_METADATA_EXPOSURE_ONLY
TRAIN_METADATA_EXPOSURE_OCCURRED=true
SCIENTIFIC_EXECUTION_OCCURRED=false
EXPERIMENTAL_BINARY_ACCESS_OCCURRED=false
PIXEL_ACCESS_OCCURRED=false
FEATURE_ACCESS_OCCURRED=false
MODEL_FIT_OCCURRED=false
DEV_ACCESS_OCCURRED=false
TEST_ACCESS_OCCURRED=false
```

Before the previous stop, delegated read commands opened the full text of
`artifacts/evidence/STUDY2_D_ATTRIBUTION/TRAIN_INPUT_MANIFEST.json` and
`artifacts/evidence/STUDY2_D_ATTRIBUTION/STUDY2_D_ATTRIBUTION_DESIGN.json`.
The manifest was opened by two agents; the design by one. Returned terminal
output was truncated, which does not negate the reads performed by the commands.
The exposure included TRAIN sample/group identities, acquisition and weak-label
fields, frames, coordinates, historical fold/design declarations, hashes and
storage descriptors (logical paths, offsets, dtype and shape). It did not
include experimental image payloads, feature arrays or fitted models. Canonical
closeout documents, the HANDOFF, source code and historical contracts were also
read as documentary context.

The report must not call this `ZERO_METADATA_ACCESS` or
`SCIENTIFIC_TRAINING_DATA_PIXEL_ACCESS`. Scientific runs, experimental feature
extractions, experimental fits, binary-cache reads, DEV/TEST reads, MP4 opens
and FFmpeg runs were zero. No files, commits, push, CI, PR, method freeze or
scientific receipt were created during that attempt. The worktree remained
clean at `68ae723b392a41f52c07e2a8345437b169d5ea78` on
`feat/study3-temporal-site-representation`.

Both guard command attempts returned exit 127 because the implicit `python`
command was unavailable. Neither guard actually ran. The current author decision
allows one effective invocation of each guard using an explicitly selected
interpreter. This operational recovery is not a scientific retry.

The Study3-CNN design existed in the author-approved chat protocol before this
operational exposure: 10,907 TRAIN rows; 32 positive and 32 background groups;
four historical folds; D1/mean/median/q25-q50-q75 representations; T=8 real-row
selection; both exact CNN architectures; fixed metadata-control features;
historical RF_REFERENCE parameters; seeds, epochs, learning rates and batch
sizes; GMBA, contrasts and descriptors; and an exact budget of 28 fits.

```text
DESIGN_ORIGIN=AUTHOR_APPROVED_CHAT_PROTOCOL_BEFORE_METADATA_EXPOSURE
METADATA_EXPOSURE_USED_TO_ADAPT_DESIGN=false
```

None of these choices may be adapted using the exposed metadata. Recovery
permits only textual information necessary to authenticate the already fixed
contracts, not new corpus statistics, feature exploration or performance.
Synthetic model fits are verification on invented fixtures and must be reported
separately from the experimental counters above. This record reconciles the
incident; it does not claim that the Study3 freeze or CI has already passed.

## Verificação efetiva da recuperação

Estado desta recuperação: **BLOCKED_OPERATIONAL_GOVERNANCE_BEFORE_FREEZE**.
A implementação e os testes sintéticos estão concluídos localmente. Os gates
históricos de governança não passaram, portanto não há method freeze, commit,
push, CI remota ou prontidão para decisão científica. Nenhum resultado
experimental Study3 foi produzido. Este documento é o relatório da fase;
nenhum diretório de evidência científica foi criado.

### Workspace e interpretador

Worktree: `snbi-dendritic-fragmentation-ml-study3`, no root autorizado pelo
autor. Branch: `feat/study3-temporal-site-representation`. HEAD inicial e final
preservado: `68ae723b392a41f52c07e2a8345437b169d5ea78`. A árvore versionada estava
limpa antes dos dois primeiros documentos; ao terminar há somente 34 arquivos
novos da allowlist Study3, ainda não staged. Nenhum arquivo histórico foi
modificado. `academic-deliverable-build/`, `program-final/`, Experiment 1 e
Study2-A/B/C/D foram preservados.

O interpretador selecionado foi `$ORIGINAL_ROOT/.venv/bin/python`, Python
3.12.3, usado com `-B` e somente como ambiente existente read-only. O worktree
não tinha `.venv/bin/python` executável. `/usr/bin/python3` também era 3.12.3,
mas não tinha o conjunto científico necessário; a sondagem de versões desse
interpretador retornou exit 1 por ausência de scikit-image. Não foi criada
venv nem feita instalação, alteração de pins ou modificação do ambiente
original. Nenhuma ferramenta voltou a usar o comando implícito `python`.

Os 22 pins de `constraints-ti3c-cnn.txt` foram comparados com as distribuições
instaladas e todos coincidiram (exit 0): NumPy 1.26.4, SciPy 1.11.4,
scikit-image 0.24.0, scikit-learn 1.5.2, PyTorch 2.4.1+cpu, joblib 1.6.0,
threadpoolctl 3.7.0, cloudpickle 3.1.2, imageio 2.37.4, lazy-loader 0.5,
networkx 3.6.1, packaging 26.3, pillow 12.3.0, tifffile 2026.3.3,
typing-extensions 4.16.0, filelock 4.0.1, fsspec 2026.9.0, jinja2 3.1.6,
setuptools 84.0.0, sympy 1.14.0, markupsafe 3.0.3 e mpmath 1.3.0.

### Guards: tentativas anteriores e execução efetiva

| Fronteira | Comando | Resultado |
| --- | --- | --- |
| Tentativa anterior data guard | `python -B scripts/check_repository_data.py` | exit 127; ENVIRONMENT_COMMAND_FAILURE; guard não executou. |
| Tentativa anterior phase scope | `python -B scripts/check_phase_scope.py` | exit 127; ENVIRONMENT_COMMAND_FAILURE; guard não executou. |
| Execução efetiva 1 data guard | `$ORIGINAL_ROOT/.venv/bin/python -B scripts/check_repository_data.py` | exit 1; BLOCKED; `audit failure: ValueError`; content_bytes_read=0. |
| Execução efetiva 1 phase scope | `$ORIGINAL_ROOT/.venv/bin/python -B scripts/check_phase_scope.py` | exit 1; BLOCKED; `phase scope audit unavailable: ValueError`; experimental_content_bytes_read=0. |
| Higiene do diff versionado | `git diff --check` | exit 0. |
| Inventário local vs base | `git diff --name-only 68ae723b392a41f52c07e2a8345437b169d5ea78 --` | exit 0, vazio: nenhum histórico alterado. |

Cada guard teve exatamente uma execução efetiva nesta recuperação. A leitura
estática identifica a causa: `check_repository_data.require_standalone_checkout`
exige `.git` como diretório; o linked worktree autorizado usa a forma rejeitada.
`check_phase_scope` chama o mesmo requisito. Não ocorreu falha de startup do
sandbox e não se fez remediação do SO, bypass ou fallback fora do sandbox.

Para incluir os arquivos ainda não versionados na revisão de whitespace,
`git diff --no-index --check -- /dev/null <path>` foi aplicado aos 34 paths:
todos retornaram 1 por haver diferenças (arquivos novos), sem qualquer mensagem
de whitespace em stdout/stderr. O agregador inicial tratou esse código de
diferença como erro; a interpretação foi corrigida sem alteração de arquivos
para disfarçar o resultado. O comando comum `git diff --check` não examina
arquivos untracked, por isso seu exit 0 não foi usado como prova suficiente
para os novos arquivos.

### Testes sintéticos e regressões

Todos os comandos usaram explicitamente o interpretador selecionado, `-B` e
`PYTHONPATH=src:tests:.`. As suites foram carregadas por `unittest.TestLoader`
e executadas por `unittest.TextTestRunner`, com contadores explícitos e recusa
de skips/falhas/erros no perfil científico. Nenhum teste executou a CLI
`scripts/run_study3.py` ou seu preflight contra o worktree real. Testes do
controlador usam roots descartáveis dentro de `.bootstrap-test-tmp/`, preflight
falso e fixtures inventados; receipts nesses roots são fixtures sintéticos,
não receipts científicos. Fits sintéticos necessários aos testes não entram
no contador de fits experimentais.

| Suite final | Tests | Passes | Skips | Failures | Errors | Exit |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Study3 com pins científicos | 126 | 126 | 0 | 0 | 0 | 0 |
| Study2-C sintético | 137 | 137 | 0 | 0 | 0 | 0 |
| Study2-D sintético | 116 | 116 | 0 | 0 | 0 | 0 |
| Study3 stdlib (`-S`) | 126 | 74 | 52 | 0 | 0 | 0 |

Expected failures, unexpected successes e erros de discovery foram zero nas
suites finais. Os 52 skips do perfil stdlib são exclusivamente de testes que
exigem dependências científicas; o perfil Study3 com essas dependências teve
zero skips. O workflow dedicado exige zero skips. São 379 testes distintos
aprovados no conjunto Study3+C+D, sem somar novamente a passagem stdlib.

Contagem Study3 por arquivo: domain 13, design 7, io 18, temporal_features 10,
cnn 22, models 23, metrics 8, execution 25. Regressões C: design 30, io 31,
models 25, cnn 10, execution 41. Regressões D: design 20, io 29, models 20,
execution 47.

A primeira verificação integrada Study3 teve 124/124 passes. Depois foram
adicionados dois testes relevantes: recusa de campos de autoridade
desconhecidos/retipados e falha na gravação final de checksums sem terminal
PASS indevido. A primeira passagem stdlib detectou import obrigatório de
NumPy no novo teste temporal (116 tests, 74 passes, 41 skips, 1 error, exit 1);
o import opcional foi corrigido no novo teste antes do freeze. A passagem final
acima confirma a correção. Nenhum método, parâmetro ou arquivo histórico foi
alterado por esses ajustes.

### Council, método e revisão adversarial

O council documental de nove perspectivas aprovou somente a preparação do
desenho interno exploratório condicionado aos gates. Unidade GROUP_TRAJECTORY;
duas aquisições; 10.907 TRAIN rows, 3.858 GOLD/7.049 BACKGROUND e 32+32 grupos;
quatro folds históricos. A pergunta exata permanece no
[protocolo](STUDY3_MASTER_PROTOCOL.md).

Representações: D1_LBP20, TRAJECTORY_MEAN_LBP20,
TRAJECTORY_MEDIAN_LBP20 (primária clássica), TRAJECTORY_Q2575_LBP60.
CNN1D: Conv1d20→32→32, pooling global, Linear32→2, 5.122 parâmetros.
Espaço-temporal: encoder compartilhado Conv2d2→8→16, head Conv1d16→16,
pooling global e Linear16→2, 2.138 parâmetros. T=8, seed 42 e 30 epochs
permanecem fixos. Controles: majority por aquisição, sem fit; quatro features
de cobertura com StandardScaler/LogisticRegression fold-local.

Primária GMBA; sete contrastes fixos: MEDIAN_MINUS_D1, CNN1D_MINUS_D1,
SPATIOTEMPORAL_MINUS_D1, SPATIOTEMPORAL_MINUS_MEDIAN,
SPATIOTEMPORAL_MINUS_CNN1D, MEAN_MINUS_D1 e Q2575_MINUS_D1. Budget exato:
16 RF + 4 CNN1D + 4 espaço-temporal + 4 metadata = 28; fit 29 negado.

A revisão cobriu os arquivos novos, contratos, testes, workflow e fontes de
integração histórica. Nenhuma decisão de método veio de dados vistos;
DEV/TEST aparecem somente como fronteiras negadas e estado histórico
consumido; não há resultados científicos. Foram corrigidas falhas de
implementação antes do freeze: serialização do fold como int, validação dos
30 callbacks de epoch, preflight obrigatório em toda entrada do controlador,
schemas de resultado/scaler, receipt verdadeiro e terminal PASS publicado
somente depois do manifesto de checksums. Receipts e ledger temporal integram
os checksums. O teste final de falha de checksum prova fechamento BLOCKED.
As sentinelas de path provam recusa antes do acesso para DEV, TEST, SILVER,
cache/index TEST, MP4, offsets e identidades alteradas. Contratos JSON das
arquiteturas/modelos foram comparados com o código por nove testes específicos.

### Inventário criado — 34 arquivos, nenhum ainda no Git index

```text
docs/study3/STUDY3_PRE_SCIENCE_INCIDENT.md
docs/study3/STUDY3_PREEXPOSURE_DESIGN_DECLARATION.md
docs/study3/STUDY3_COUNCIL_DECISION.md
docs/study3/STUDY3_MASTER_PROTOCOL.md
docs/study3/STUDY3_SPECIFICATIONS.md
docs/study3/STUDY3_DATA_CONTRACT.md
docs/study3/STUDY3_CLAIM_SCOPE.md
docs/study3/STUDY3_RISK_REGISTER.md
docs/study3/FUTURE_STUDY3_EXTENSIONS.md
configs/study3/authority.json
configs/study3/data-contract.json
configs/study3/representation-contract.json
configs/study3/cnn-contract.json
configs/study3/model-contract.json
configs/study3/fit-budget.json
configs/study3/evaluation-contract.json
src/snbi_fragmentation/study3_domain.py
src/snbi_fragmentation/study3_design.py
src/snbi_fragmentation/study3_io.py
src/snbi_fragmentation/study3_temporal_features.py
src/snbi_fragmentation/study3_cnn.py
src/snbi_fragmentation/study3_models.py
src/snbi_fragmentation/study3_metrics.py
src/snbi_fragmentation/study3_execution.py
scripts/run_study3.py
tests/test_study3_domain.py
tests/test_study3_design.py
tests/test_study3_io.py
tests/test_study3_temporal_features.py
tests/test_study3_cnn.py
tests/test_study3_models.py
tests/test_study3_metrics.py
tests/test_study3_execution.py
.github/workflows/study3-synthetic-ci.yml
```

### Bloqueio e proposta operacional para nova decisão

Três incompatibilidades impedem o freeze sob os gates atuais:

1. [Data guard](../../scripts/check_repository_data.py) exige checkout standalone,
   e [phase scope](../../scripts/check_phase_scope.py) herda esse requisito.
2. Phase scope rejeita qualquer Python versionado fora das classificações do
   manifesto histórico: os 17 novos arquivos Python Study3 precisam de uma
   integração explícita. O estado untracked ainda não expõe esse segundo
   erro ao index audit; a conclusão vem da leitura estática.
3. [Guard de imports](../../scripts/check_ti3_scope.py) permite Torch somente
   nos quatro paths CNN históricos, não nos dois novos paths CNN Study3.

`check_repository_data.py` pertence ao domínio LEGACY_TI2 e seu blob é
imutável pelo baseline. Alterá-lo e atualizar seu hash não preservaria a
custódia histórica. A proposta é uma **camada adicional de governança**, ainda
não implementada nem autorizada, com inventário explícito que particione
exaustivamente os paths antigos e novos, preserve todos os hashes antigos,
valide o worktree vinculado autorizado e permita Torch somente em
`src/snbi_fragmentation/study3_cnn.py` e `tests/test_study3_cnn.py` além dos
paths já históricos. Nenhum arquivo desconhecido pode desaparecer da auditoria.
Não usar monkeypatch para suprimir guards, modificar baseline ou declarar
PASS no lugar de uma verificação efetiva.

Essa correção exigiria autorizar um checker/manifesto/testes adicionais e
integração explícita nos workflows que hoje chamam os guards antigos:
`ci.yml`, `ti3-synthetic.yml`, `ti3b-synthetic.yml`, `ti3c-synthetic.yml`,
`ti3d-final-synthetic.yml`, `study2a-synthetic.yml`, `study2b-synthetic.yml`,
`study2c-synthetic.yml`, `study2d-synthetic.yml` e o novo workflow Study3.
Também seria necessário ajustar a validação operacional do inventário de
freeze em `study3_execution.py`, hoje limitada às 34 adições originais.
Nenhuma arquitetura, feature, seleção, fold, métrica ou budget mudaria.

A nova decisão precisaria autorizar expressamente essa integração operacional
e outra execução dos guards. O item 9 do prompt atual limita cada guard a uma
execução efetiva, já realizada; o item 33 permite o commit somente após todos
os gates PASS. Portanto não foram feitos staging, commit, push ou CI remota,
nem a correção de governança fora da allowlist. A autorização de commit/push
existente não foi confundida com autorização para ignorar gates falhos.

### Estado de publicação e fronteiras finais

```text
STUDY3_PRE_SCIENCE_RECOVERY=BLOCKED_OPERATIONAL_GOVERNANCE_BEFORE_FREEZE
METADATA_INCIDENT_DOCUMENTED=true
PRE_SCIENCE_TRAIN_METADATA_EXPOSURE=true
DESIGN_CHANGED_AFTER_METADATA_EXPOSURE=false
LOCAL_IMPLEMENTATION_CREATED=true
STUDY3_SYNTHETIC_TESTS=126_PASS_0_SKIP_0_FAILURE_0_ERROR
HISTORICAL_SYNTHETIC_TESTS=253_PASS_0_SKIP_0_FAILURE_0_ERROR
METHOD_FREEZE_CREATED=false
STUDY3_CNN_METHOD_FREEZE_SHA=NOT_CREATED
FILES_IN_FREEZE_COMMIT=0
COMMITS_CREATED=0
PUSHES=0
REMOTE_CI_RUNS=0
REMOTE_CI_JOBS=0
REMOTE_CI_STEPS=0
PRE_SCIENCE_CI=NOT_RUN_BLOCKED_BEFORE_FREEZE
SCIENTIFIC_STUDY3_RUNS=0
EXPERIMENTAL_BINARY_READS=0
PIXELS_READ=0
SCIENTIFIC_ROWS_MATERIALIZED=0
EXPERIMENTAL_FEATURE_EXTRACTIONS=0
EXPERIMENTAL_FIT_CALLS=0
DEV_ROWS_READ=0
TEST_ROWS_READ=0
TEST_CACHE_ROWS_READ=0
MP4_OPENS=0
FFMPEG_RUNS=0
SCIENTIFIC_RECEIPT_CREATED=false
SCIENTIFIC_PREFLIGHT_EXECUTED=false
HANDOFF_MODIFIED=false
READY_FOR_AUTHOR_SCIENCE_DECISION=false
CURRENT_AUTHORIZED_ACTIVITY=NONE_AWAITING_AUTHOR_DECISION
```

O hash do HANDOFF na revalidação permanece
`71bb1bf8f346f445c87561de86329d994354412354b879959f72cb4255bef445`.
Os zeros científicos não negam a exposição textual a metadados, explicitamente
reconciliada e permitida no escopo contratual desta recuperação. O estado
final preserva os arquivos novos para revisão; não promete árvore totalmente
limpa, commit congelado ou CI que não ocorreu.

## Authorized operational governance repair

A decisão autoral complementar `/STUDY3-GOVERNANCE-REPAIR-AND-FREEZE`
autoriza exclusivamente corrigir as três incompatibilidades operacionais,
validar sinteticamente, fazer staging exato, executar os guards autorizados
uma vez sobre o index real, criar um único method-freeze commit, publicar por
push fast-forward e verificar a CI no SHA exato. Esta seção é aditiva: todo
o relato anterior, incluindo os bloqueios efetivamente observados e a
exposição TEXTUAL_TRAIN_METADATA_EXPOSURE_ONLY, permanece preservado.

O novo escopo substitui a proposta ampla anterior por mudanças mínimas:
`scripts/check_phase_scope.py`, `scripts/check_ti3_scope.py` e
`configs/governance/phase-scope-v1.json`; novos
`scripts/check_study3_governance.py` e `tests/test_study3_governance.py`;
ajustes somente de inventário operacional em `study3_execution.py`, do
workflow Study3 e desta seção. Nenhum quarto domínio é criado. Os 19 novos
Python Study3 pertencem explicitamente a TI3_ACTIVE, origin_phase STUDY3.
Torch continua restrito aos quatro paths históricos e aos dois paths CNN
Study3, totalizando exatamente seis.

`scripts/check_repository_data.py` permanece byte-idêntico, com Git blob
`9e39878e5bf18df0e05d6388c26745b7c11a4414`. Os nove workflows históricos
também permanecem intactos. O novo guard local reutiliza a política imutável
`audit_entries`, pois o main histórico continua standalone-only. O main
histórico não será reexecutado localmente esperando PASS; sua execução em
checkout standalone será exigida na CI remota.

A validação adicional aceita somente checkout standalone normal ou linked
worktree com gitfile regular, limitado e bem formado, identidade Git
coerente e layout common-dir/worktrees/name. Nenhuma identidade Git concede
autoridade científica, de dados ou de paths experimentais.

O conjunto exato é de 36 adições e três modificações históricas: 39 paths.
Nenhum 40º path pode integrar o freeze. O método científico, contratos,
representações, arquiteturas, folds, métricas, seeds e budget de 28 fits
permanecem inalterados. Esta autorização termina na CI pré-ciência:
nenhum preflight científico real, receipt, payload, feature ou fit
experimental é autorizado; `scripts/run_study3.py` não será executado.

Esta decisão substitui, somente neste escopo, as restrições operacionais
anteriores de não alterar nenhum checker e não executar novamente os guards,
inclusive o registro histórico em `STUDY3_RISK_REGISTER.md`. Não apaga os
dois BLOCKED anteriores: ambos decorreram da exigência standalone no linked
worktree. As incompatibilidades de classificação e Torch foram identificadas
estaticamente e agora recebem somente as extensões explicitamente autorizadas.

### Verificação local anterior ao staging

O interpretador explícito foi `$ORIGINAL_ROOT/.venv/bin/python`, com `-B`,
`PYTHONPATH=src:tests:.` e fixtures temporários locais sob
`.bootstrap-test-tmp/`. Os 22 pins históricos permanecem idênticos ao ambiente
existente. Não houve instalação nem modificação da venv original.

| Suite/perfil | Tests | Passes | Skips | Failures | Errors | Exit |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Study3 com dependências | 159 | 159 | 0 | 0 | 0 | 0 |
| Governança Study3, incluída nos 159 | 33 | 33 | 0 | 0 | 0 | 0 |
| Study2-C sintético | 137 | 137 | 0 | 0 | 0 | 0 |
| Study2-D sintético | 116 | 116 | 0 | 0 | 0 | 0 |
| Phase scope | 26 | 26 | 0 | 0 | 0 | 0 |
| TI3 scope | 15 | 15 | 0 | 0 | 0 | 0 |
| Study3 stdlib (`-S`) | 159 | 107 | 52 | 0 | 0 | 0 |

São 453 testes distintos aprovados no perfil com dependências, sem contar
novamente os 33 de governança ou a passagem stdlib. Expected failures,
unexpected successes e erros de discovery foram zero. Os 52 skips stdlib
correspondem às dependências opcionais ausentes nesse perfil; a execução
com os pins científicos teve zero skips. Fits em fixtures inventados são
exclusivamente testes sintéticos e não são fits experimentais.

A revisão independente não identificou falha material. O manifesto adiciona
exatamente 19 rows TI3_ACTIVE/TRACKED/STUDY3 e altera somente os dois blobs
históricos autorizados. Os hashes Git foram calculados em memória, sem escrita
de objetos. O teste de custódia compara todas as rows históricas com a base.
Os 31 arquivos Study3 fora dos três ajustes permitidos conservam seus SHA-256
iniciais. Os primeiros 17.045 bytes deste documento também conservam o
SHA-256 original `046075d21ba065ec8f1dae5202e6fe72a0dfe094d99c7f2a1b1b5292ac3208ad`.

O inventário local e a revisão de whitespace dos 36 arquivos novos passaram;
`git diff --check` retornou exit 0. Somente os três arquivos históricos
autorizados aparecem no diff versionado. O HANDOFF conserva
`71bb1bf8f346f445c87561de86329d994354412354b879959f72cb4255bef445`.
Nenhuma execução científica, leitura experimental, extração de features,
fit experimental, receipt ou preflight científico ocorreu neste reparo.
Os resultados de publicação e CI no SHA congelado serão reportados após
sua execução, sem criar outro commit para registrar eventos posteriores.

### Guards efetivos sobre o index real

O staging exato foi comprovado por `git diff --cached --name-status
--no-renames`: 36 adições, três modificações e nenhum path extra. Os 21
blobs Python novos/alterados coincidiram entre bytes locais, manifest e index.
Não havia alterações unstaged nem arquivos untracked. Após esse staging,
cada entrada autorizada abaixo foi executada exatamente uma vez, nesta ordem,
com `$ORIGINAL_ROOT/.venv/bin/python -B`:

| Entrada | Status | Exit | Bytes experimentais |
| --- | --- | ---: | ---: |
| `scripts/check_phase_scope.py` | PASS | 0 | 0 |
| `scripts/check_study3_governance.py` | PASS; LINKED_WORKTREE | 0 | 0 |
| `scripts/check_ti3_scope.py` | PASS via composição histórica | 0 | 0 |

A política de dados examinou 846 entradas do index, sem ler conteúdo
experimental. A partição exaustiva classificou 165 arquivos Python:
75 LEGACY_TI2, quatro TI3_A0_FROZEN e 86 TI3_ACTIVE; zero ausentes,
duplicados, planejados ou não classificados. As três custódias passaram.
O campo `scientific_readiness=BLOCKED` é esperado e foi preservado:
nenhuma dessas verificações concede autoridade científica.

```text
LOCAL_PHASE_SCOPE=PASS
LOCAL_STUDY3_GOVERNANCE=PASS
LOCAL_TI3_SCOPE=PASS
LEGACY_DATA_GUARD_MAIN_LOCAL=NOT_APPLICABLE_TO_LINKED_WORKTREE_BY_DESIGN
DATA_POLICY_LOGIC_LOCAL=PASS_VIA_IMMUTABLE_AUDIT_ENTRIES
EXACT_39_PATH_ALLOWLIST=PASS
SCIENTIFIC_STUDY3_RUNS=0
EXPERIMENTAL_BINARY_READS=0
PIXELS_READ=0
SCIENTIFIC_ROWS_MATERIALIZED=0
EXPERIMENTAL_FEATURE_EXTRACTIONS=0
EXPERIMENTAL_FIT_CALLS=0
DEV_ROWS_READ=0
TEST_ROWS_READ=0
TEST_CACHE_ROWS_READ=0
MP4_OPENS=0
FFMPEG_RUNS=0
SCIENTIFIC_RECEIPT_CREATED=false
SCIENTIFIC_PREFLIGHT_EXECUTED=false
HANDOFF_MODIFIED=false
```

Este resultado autoriza o único commit já aprovado pelo autor. A CI remota
continua sendo gate obrigatório antes de declarar prontidão para nova
decisão científica. O SHA desse commit e a contagem real de workflows,
jobs e steps pertencerão ao relatório terminal da execução.
