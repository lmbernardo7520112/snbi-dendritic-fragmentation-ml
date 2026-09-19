# TI2R-SOLUTE — reparo operacional e primeira execução do locked holdout

**PRE_HOLDOUT_GATE=PASS; G2_SOLUTE=PASS; HOLDOUT_SOLUTE=CONSUMED.**
Os quatro casos satisfizeram individualmente os critérios V2 congelados.
Uma execução científica, oito buffers abertos uma vez cada, 15.566.040 bytes,
zero retry científico. A autoridade está encerrada, aguardando decisão autoral.

## Histórico preservado e autoridade

O checkpoint inicial é `7994771e239afdb998a644626c423c1c627f80a0`.
Ele preserva a CLI operacional anterior: exit 3,
`CONFIGURATION_DIVERGENCE`, zero execuções científicas, opens ou bytes.
Todos os arquivos daquela evidência permanecem byte-idênticos. Não se
reescreveu o incidente como sucesso nem se excluiu seu estado terminal.

A decisão nova está em `authorization.md` deste diretório `repair-1`.
Ela autoriza uma correção operacional e, condicionado ao preflight integral,
somente a primeira execução científica. Não autoriza outro reparo, retry
científico, tuning, TI-3+, Ready ou merge. Autoridades antigas continuam
consumidas e não foram reativadas.

Branch: `feat/ti2r-solute-v2-calibration`, PR #10 OPEN/DRAFT.
C1 científico: `e1a98917a20431ecc1c758f210b5e974b3533734`.
C2 remoto: `0b820bc61e6dae3b7a98654a3b7d5cd292ca925e`.
Base: `fcfc5e1445467248566e881c61929d4d3da7b1d8`.
Commit de reparo e HEAD da execução:
`febaa56efdcec210f6efb0d456ab1558bce7fe43`.
Seu parent é exatamente o checkpoint inicial. O SHA do commit final de
evidências pertence ao Git e ao retorno ao operador, sem autorreferência.

## Reparo autorizado e testes sem pixels

A coerção anterior ocorreu na orquestração JavaScript da sessão: a saída
JSON das configurações foi lida por `JSON.parse` e o novo manifesto foi
escrito com `JSON.stringify`. Nessa passagem, floats integrais foram
serializados como inteiros; a configuração científica no repositório não mudou.
O produtor agora lê diretamente os JSON congelados em Python e usa
`encode_manifest`, que chama o serializador Python existente e exige
roundtrip com `_exact` inalterado. Nenhum valor ou contrato foi flexibilizado.

| Campo V1 | Valor no manifesto novo | Tipo após leitura |
| --- | ---: | --- |
| minimum_entropy_bits | 1.0 | float |
| saturation_low_y | 16.0 | float |
| saturation_high_y | 235.0 | float |
| median_limit_px | 1.0 | float |
| p95_limit_px | 2.0 | float |
| maximum_limit_px | 3.0 | float |

Três testes mínimos verificam os seis campos reais, preservação recursiva de
floats/ints/strings/bools/listas/maps e rejeição das substituições de tipo.
Passaram sem skips, falhas ou erros. A suíte stdlib passou 426 testes:
340 passes e 86 skips opcionais. Nenhuma imagem experimental foi usada.

Diff do reparo: dois arquivos, 83 inserções e 15 remoções:
`scripts/run_ti2r_solute_locked_holdout.py` e
`tests/test_ti2r_solute_holdout_manifest.py`.
Além do produtor, o runner vincula a autorização ao filho direto do checkpoint
e aos dois caminhos exatos; separa HEAD local de C2 remoto; usa o namespace
novo sem apagar terminais antigos; distingue os contadores históricos.
O avaliador e os 25 arquivos científicos permanecem byte-idênticos.
A revisão independente do diff não identificou alteração científica.

## Novo preflight e freeze

O preflight integral foi chamado sem criar receipt ou leitor experimental
após a geração do manifesto. Retornou PASS com zero opens/bytes.
O runner revalidou os mesmos contratos imediatamente antes de armar a
execução. Essas verificações operacionais não são execuções científicas.

Manifesto SHA-256:
`54ca71aaf8f38877a3ad2944d67b4fc31c0b6212e855ef185207bac992a9a101`.
`frozen-hashes.sha256` contém 32 hashes: 25 arquivos científicos, seis
operacionais e o manifesto. Todos foram conferidos novamente após a ciência.
Os tipos finais foram verificados no JSON serializado real, além dos testes.

Os 25 arquivos correspondem exatamente a C1/C2. Kernels, SS8, NGF,
preprocessing, máscaras, índices, thresholds, critérios, pesos e resíduos
não mudaram. Os seis arquivos operacionais também não mudaram após freeze.
Os checksums históricos do runner anterior identificam seus bytes em
7994771; não foram adulterados para corresponder ao reparo atual.

NumPy 1.26.4 e SciPy 1.11.4 preexistentes foram confirmados, sem instalação.
O receipt foi criado com O_EXCL e fsync antes dos pixels, incluindo timestamp,
HEAD, configurações, hashes, allowlist e contador de tentativa um.
Receipt SHA-256:
`102ca1c4e6aa02c79e719386ab42e3be18ec3682c59f2ca8d5913978a2e0ef25`.

## Execução e contadores

Comando do runner, sandbox padrão, exit 0:

```text
PYTHONPATH=src /usr/bin/python3 -B scripts/run_ti2r_solute_locked_holdout.py
```

Receipt/início: 2026-09-19T00:16:21.169784+00:00.
Fim: 2026-09-19T00:16:40.297742+00:00.
No fuso America/Fortaleza, a execução ocorreu em 18/09/2026.

| Contador do runner | Anterior | Autorização atual | Total |
| --- | ---: | ---: | ---: |
| Invocações CLI do runner | 1 | 1 | 2 |
| Execuções científicas do holdout | 0 | 1 | 1 |
| Retries científicos | 0 | 0 | 0 |
| Buffers experimentais abertos | 0 | 8 | 8 |
| Bytes experimentais lidos | 0 | 15.566.040 | 15.566.040 |

Uma chamada científica completa contém duas chamadas por par e quatro casos.
O total de CLI acima se refere ao entry point do runner, não aos comandos
auxiliares de leitura, testes, criação de documentos ou à chamada somente de
preflight no produtor. Esses comandos estão discriminados em `commands.json`.
A repetição operacional autorizada não é um retry científico.

| Buffers autorizados | Opens por buffer | Bytes por buffer |
| --- | ---: | ---: |
| ESM1:73, ESM1:219, ESM2:73, ESM2:219 | 1 | 1.951.506 |
| ESM4:98, ESM4:295, ESM5:98, ESM5:295 | 1 | 1.940.004 |

Os oito hashes correspondem ao manifesto piloto congelado, calculados
durante a única leitura de cada arquivo. Nenhum buffer foi reaberto para
verificação posterior; ela usa somente os registros textuais.
Nenhum DEV, novo frame, ZIP, MP4, FFmpeg/FFprobe ou fonte externa foi acessado.

## Resultados por caso

Todos os casos foram IDENTIFIABLE e aprovaram cada critério individual.
Cada métrica manteve 18 blocos e quatro quadrantes em cada caso.
As 16 perturbações tiveram máximo único no inverso correto, rank 1 e erro
discreto zero nas duas métricas: 64 combinações de caso e perturbação,
128 verificações separadas nas duas métricas, sem descarte ou resgate por médias.
Os oito controles identidade também passaram.

| Par | Índice | Estado | SS8 recuperações | NGF recuperações | Menor margem SS8 | Menor margem NGF |
| --- | ---: | --- | --- | --- | ---: | ---: |
| ESM2→ESM1 | 73 | PASS | 16/16 | 16/16 | 0.011209150 | 0.017397890 |
| ESM2→ESM1 | 219 | PASS | 16/16 | 16/16 | 0.013259779 | 0.025711767 |
| ESM5→ESM4 | 98 | PASS | 16/16 | 16/16 | 0.010396944 | 0.017907335 |
| ESM5→ESM4 | 295 | PASS | 16/16 | 16/16 | 0.014791578 | 0.032258218 |

A tabela usa apresentação decimal abreviada; as decisões usaram os valores
completos de `results.json`, sem arredondamento para atingir limites.
Margem exigida: >=0,005; erro <=0,5 px; recuperação exigida: 16/16 em
cada caso e métrica, com concordância SS8/NGF e quatro quadrantes.

| Caso | Mediana residual px | P95 px | Máximo px |
| --- | ---: | ---: | ---: |
| ESM2→ESM1:73 | 0.093889503 | 0.155991379 | 0.225884158 |
| ESM2→ESM1:219 | 0.038444418 | 0.097543533 | 0.144702395 |
| ESM5→ESM4:98 | 0.052849891 | 0.181930969 | 0.186484318 |
| ESM5→ESM4:295 | 0.061581624 | 0.097818458 | 0.136946235 |

Resíduos NGF originais: 18 por caso, preservados, sem exclusão por erro.
Limites congelados: mediana<=1, P95<=2, máximo<=3 px. Não houve picos
ambíguos/censurados bloqueantes ou ajuste da transformação a partir deles.

| Caso | Score identidade SS8 | Score identidade NGF | Margem espacial SS8 / NGF | Margem temporal SS8 / NGF |
| --- | ---: | ---: | --- | --- |
| ESM2→ESM1:73 | 0.774652789 | 0.600061721 | 0.011210904 / 0.017397890 | 0.109587027 / 0.184524892 |
| ESM2→ESM1:219 | 0.778822822 | 0.566380387 | 0.013253688 / 0.025711767 | 0.108257844 / 0.078237810 |
| ESM5→ESM4:98 | 0.781391374 | 0.619990495 | 0.010397035 / 0.017907335 | 0.129810557 / 0.217781135 |
| ESM5→ESM4:295 | 0.770967268 | 0.576919730 | 0.014809332 / 0.032258218 | 0.105394656 / 0.096813103 |

Os controles temporais foram recíprocos entre os dois instantes reservados,
conforme o código congelado, e sua identificabilidade foi registrada.
Os scores absolutos permanecem abaixo dos pisos históricos V1 0,90/0,80;
os estados brutos V1 `FAIL_IDENTITY_DISCRIMINATION` estão preservados.
O protocolo V2 já congelado em C1 usa os critérios relativos e a recuperação,
sem esses pisos como gates. O PASS não reclassifica os resultados históricos.

`results.json` retém todos os scores de candidatos e blocos, margens,
ranks, correções/perturbações, máximos, quadrantes, resíduos, informação
individual, controles temporais e critérios booleanos de cada caso.
`io-audit.json`, receipt e estado terminal concordam sobre contadores e hashes.

## Limitações, publicação e encerramento

G2_SOLUTE=PASS é a aprovação do protocolo congelado neste locked holdout
temporal interno às mesmas aquisições. Não demonstra generalização externa.
Frames, blocos e perturbações não são réplicas experimentais independentes.
A exposição histórica das referências ESM1/ESM4 em FRAG-DIRECT permanece
declarada; o lacre solutal não significava virgindade global das imagens.

Não houve calibração física, conversão de unidades, estimativa metrológica,
novo ajuste de matriz ou certificação de ROI. Os campos de matriz/inversa/ROI
do adaptador permanecem nulos. G2_FRAG conserva seu PASS histórico;
os demais gates e autoridades não são reabertos por este resultado.
Não houve desenvolvimento, reparo adicional ou alteração científica após
observação do holdout. Não se propõe tuning ou nova execução.

CI C2 reconfirmada nos runs
[35399554524](https://github.com/lmbernardo7520112/snbi-dendritic-fragmentation-ml/actions/runs/35399554524)
e [35399558120](https://github.com/lmbernardo7520112/snbi-dendritic-fragmentation-ml/actions/runs/35399558120):
ambos SUCCESS, dois jobs obrigatórios e todos os passos aprovados.
Os commits novos são locais; sua CI remota não foi executada.
Não houve push, alteração de PR, Ready, merge ou exclusão de branch.
O PR #10 permanece na condição OPEN/DRAFT consultada.

A auditoria textual independente confirmou todos os critérios, contadores e
hashes. Conferiu 198.288 valores de matrizes por bloco e sua correspondência
aritmética com os 136 vetores de scores agregados (identidade e perturbações).
Nenhum kernel foi reexecutado nessa conferência. Os 12 arquivos da evidência
histórica permanecem byte-idênticos ao checkpoint 7994771.
A verificação final confirma o freeze e o inventário textual.
`post-run-hashes.sha256` autentica a evidência atual; `commands.json`
discrimina comandos, testes e o único comando científico.
Após o commit final, HEAD e worktree/index são confirmados no retorno ao
operador, evitando outro commit somente para autorreferência.

```text
PRE_HOLDOUT_GATE=PASS
TI2R_SOLUTE_HOLDOUT=PASS
G2_SOLUTE=PASS
HOLDOUT_SOLUTE=CONSUMED
SCIENTIFIC_HOLDOUT_EXECUTIONS=1
STATE=CLOSED
TI3_PLUS_AUTHORIZED=false
MERGE_AUTHORIZED=false
CURRENT_AUTHORIZED_ACTIVITY=NONE_AWAITING_AUTHOR_DECISION
```
