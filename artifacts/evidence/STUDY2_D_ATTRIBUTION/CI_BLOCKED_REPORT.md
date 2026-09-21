# Study2-C integrado; Study2-D bloqueado na CI pré-execução

**STUDY2_C_INTEGRATION=PASS; STUDY2_D=BLOCKED_CI.** O freeze publicado é
`21400de67d21901aeb8e5abac528689fc39169fa`. Nove dos dez jobs passaram; o job
`deterministic-contracts` falhou por quatro testes novos que precisam declarar
NumPy como dependência opcional no perfil stdlib. Nenhuma CLI científica D,
extração de LBP ou fit experimental foi iniciada. Não há resultado de atribuição.

## Integração e preparação concluídas

O [PR #18](https://github.com/lmbernardo7520112/snbi-dendritic-fragmentation-ml/pull/18)
integrou C por merge commit `ec97cb5041ef35d4f6c9a79b54d756d6fbee674f`, com branch
preservada. CI de C, PR e pós-merge: nove jobs e cem passos SUCCESS em cada
fronteira, conforme INTEGRATION_AUDIT.json. D foi criado exatamente nesse merge
na branch `feat/study2d-data-centric-bridge`.

A autorização complementar de custódia foi cumprida. A integração autenticou
somente as 10.907 rows TRAIN necessárias: 3.858 GOLD e 7.049 backgrounds, em
dois opens e 92.164.150 bytes de leituras direcionadas por offset. Todos os
hashes de par e de canais conferiram. Não houve varredura, rehash integral,
arrays ou features. Custódia DEV/TEST foi documental. O binário TEST e seu
índice não foram abertos. Esses acessos TRAIN de integração estão preservados
e separados dos zero acessos científicos D posteriores; não são apagados dos
contadores.

O desenho textual foi produzido uma vez: 32 sites/32 tracks TRAIN, quatro folds
históricos, K4/8/12/17/24, cinco salts, D1/D3/D5/DALL e dois regimes de peso.
O hash dos folds permanece
`85edac3d7da06994d7b16c4fa50e2aeb806abd7743a1d471842f54fdcf049ef2`.
O plano fixa 84+12+4=100 fits RF, oito referências reutilizadas e os mesmos
19 parâmetros RF_REFERENCE/LBP20. A auditoria independente por aritmética
stdlib verificou todos os rankings, quantis, quotas e identidades, sem chamar
o planner de novo. São 52 hashes textuais no freeze e 46 caminhos no commit.
Somente o manifesto de escopo mudou entre arquivos anteriores: nove entradas
novas, preservando 137 caminhos Python prévios e todos os demais conteúdos.

Testes locais: desenho20, modelos20, I/O29, execução38; perfil conjunto107 PASS
sem skips/falhas/erros; governança41 PASS. O perfil conjunto foi executado antes
e depois de uma correção pré-freeze do relato de contadores em falha. A primeira
prova está preservada. Seis fits RF sintéticos locais (dois isolados e dois em
cada perfil conjunto) são distintos dos zero fits experimentais. O preflight
preparatório conferiu textos reais com Git/CI futuros simulados e declarados;
ele não era prova CI real e não armou receipt. A revisão auxiliar e a revisão
principal passaram antes do commit, mas não detectaram a omissão no perfil
sem dependências. O perfil stdlib integral não foi executado localmente antes
do freeze; essa lacuna de validação não é ocultada pelo sucesso do job dedicado.

## Falha remota e STOP

[Run 35649522192](https://github.com/lmbernardo7520112/snbi-dendritic-fragmentation-ml/actions/runs/35649522192):
`deterministic-contracts` falhou em `Run deterministic tests`.
Comando: `PYTHONPATH=src python -S -B -m unittest discover -s tests -v`.
Resultado: 1.130 testes, 859 passes, quatro erros, 267 skips opcionais.
Os quatro erros são `ModuleNotFoundError: No module named 'numpy'` nos testes
`test_exact_directed_reads_and_hashes`, `test_fingerprint_change_denied`,
`test_hash_mismatch_closes` e `test_short_read_closes` de `test_study2d_io.py`.

O [job dedicado](https://github.com/lmbernardo7520112/snbi-dendritic-fragmentation-ml/actions/runs/35649522272)
passou, exigindo 107 testes sem skips. O conjunto remoto tem dez jobs: nove
SUCCESS e um FAILURE. Dos 110 passos registrados, 108 SUCCESS, um FAILURE e
um SKIPPED subsequente. Não houve rerun, segundo commit ou alteração do freeze.
CI_BLOCKED_PROOF.json guarda as respostas integrais, e ci-blocked.log.txt guarda
o log recebido. BLOCKED_CI.json separa as contagens e fronteiras.

A [seção 51 da autorização](AUTHORIZATION.md) determina: “Se qualquer falha:
STOP.” O bloqueio ocorreu antes do preflight real e antes do receipt científico.
Não existe EXECUTION_RECEIPT.json nem terminal científico consumido de D.
As curvas, contrastes, descriptors, diagnósticos por aquisição e tabela-ponte
científica não foram calculados. Tempo de execução científica não se aplica.
Nenhum PASS científico D, novo freeze aprovado ou evidência de execução é
antecipado. TEST C continua UNCHANGED_CONSUMED.

## Estado preservado e próximo passo delimitado

Os 52 hashes do freeze foram reconferidos, todos íntegros. HEAD local e remoto
continuam `21400de67d21901aeb8e5abac528689fc39169fa`; parent é o merge C. Index e
conteúdo tracked estão limpos. `academic-deliverable-build/` permanece untracked
e preservado. Apenas evidências locais aditivas do bloqueio foram criadas nesta
pasta após a falha, sem staging/commit/push delas e sem PR ou merge D.

[PROPOSED_CI_REPAIR.md](PROPOSED_CI_REPAIR.md) delimita a correção necessária,
inclusive a admissão explícita de um único commit corretivo filho do freeze,
os testes de ancestralidade e a atualização dos hashes afetados. O diff
proposto não foi aplicado. Retomada depende de decisão autoral complementar;
não é uma continuação automática após CI falha.

```text
STUDY2_C_INTEGRATION=PASS
STUDY2_D=BLOCKED_CI
STUDY2_D_METHOD_FREEZE_SHA=21400de67d21901aeb8e5abac528689fc39169fa
CI_SUCCESSFUL_JOBS=9
CI_FAILED_JOBS=1
SCIENTIFIC_STUDY2D_RUNS=0
DISTINCT_RF_FITS=0
FEATURE_EXTRACTIONS=0
DEV_ROWS_READ=0
TEST_ROWS_READ=0
TEST_CACHE_ROWS_READ=0
TEST_FEATURES_COMPUTED=0
EXPERIMENTAL_SOURCE_OPENS=0
FFMPEG_RUNS=0
TEST_STATE=UNCHANGED_CONSUMED
MODEL_SELECTION_REOPENED=false
SCIENTIFIC_EXECUTION_STARTED=false
CURRENT_AUTHORIZED_ACTIVITY=NONE_AWAITING_AUTHOR_DECISION
```
