# TI2R-SOLUTE — encerramento por falha no preflight

**PRE_HOLDOUT_GATE=FAIL. Ciência não iniciada; holdout SEALED.**
A única invocação de CLI retornou código 3, `CONFIGURATION_DIVERGENCE`,
antes do receipt e de qualquer acesso experimental. Não houve retry,
correção do manifesto ou alteração do método. Este é um incidente operacional
de preparação do agente, não um resultado científico do protocolo.

## Objetivo, identidade e autoridade

Objetivo autorizado: avaliar uma única vez os quatro casos reservados usando
os critérios V2-D congelados, com oito buffers existentes.
Repositório: `lmbernardo7520112/snbi-dendritic-fragmentation-ml`.
Branch: `feat/ti2r-solute-v2-calibration`; PR #10 OPEN/DRAFT.
HEAD da invocação e remoto auditado:
`0b820bc61e6dae3b7a98654a3b7d5cd292ca925e`.
C1 científico: `e1a98917a20431ecc1c758f210b5e974b3533734`.
Base preservada: `fcfc5e1445467248566e881c61929d4d3da7b1d8`.
O eventual SHA do único checkpoint final pertence ao histórico e retorno
ao operador; este documento não inventa SHA futuro.

A nova decisão está em `authorization.md`. Sua fase 0 manda parar quando
o preflight falha. Essa condição prevalece sobre os blocos PASS/FAIL e
CONSUMED, que pressupõem uma avaliação científica válida.
A autoridade encerra esta tarefa aguardando decisão do autor.
Nenhuma autoridade histórica é reativada.

## Freeze e auditoria

Os 25 arquivos congelados correspondem byte a byte aos blobs de C1 e C2.
C2 alterou somente sete arquivos de evidência, sem ciência.
A preparação acrescentou dois scripts de orquestração que chamam os kernels
inalterados; seus hashes foram congelados antes da invocação.
Eles não são apresentados como parte de C1. Não houve ajuste de descritor,
preprocessing, máscara, threshold, transformação, índices ou resíduos.

A auditoria preparatória foi registrada como PASS antes da primeira chamada.
A revisão estática verificou os scripts e os kernels, mas não comparou os
tipos numéricos do manifesto serializado final, ainda não criado na ocasião.
O runner executou essa comparação e recusou a configuração.
O PASS preparatório foi invalidado, não tratado como permissão para contornar
o contrato. `PRE_EXECUTION_AUDIT.md` agora conclui FAIL e explica o incidente.
A cópia exata anterior está em `PRE_EXECUTION_AUDIT_AT_FREEZE.md`, com hash
`17d38a1cc8e19f849536737a5f9436203c94c04c1436c8e8052935c2727f3f08`.

O manifesto original permanece intocado:
`581e2c721319f176dca365374e5621dc408c05f2af23e366eb1779608bf96676`.
Os 31 hashes pré-execução permanecem como registro histórico.
Desses caminhos, somente a auditoria documental recebeu o encerramento FAIL;
seu conteúdo original é verificável pelo snapshot. Os 25 textos congelados,
os dois scripts, a autorização, a verificação e o manifesto não mudaram.
Os hashes atuais completos estão em `post-run-hashes.sha256`.

## Incidente e análise descritiva

Categoria **A — implementação/pipeline**, especificamente serialização do
manifesto preparado pelo agente. A serialização JSON normalizou os tipos:

| Campo V1 | Arquivo congelado | Manifesto serializado |
| --- | --- | --- |
| minimum_entropy_bits | float 1.0 | int 1 |
| saturation_low_y | float 16.0 | int 16 |
| saturation_high_y | float 235.0 | int 235 |
| median_limit_px | float 1.0 | int 1 |
| p95_limit_px | float 2.0 | int 2 |
| maximum_limit_px | float 3.0 | int 3 |

O contrato `_exact` exige o mesmo tipo, além do mesmo valor. A recusa
`CONFIGURATION_DIVERGENCE` é coerente com esse contrato.
A configuração científica original conserva seus floats e hashes.
A inspeção posterior comparou somente JSON textual; não executou ciência.
Nenhuma correção, relaxamento do contrato ou segunda invocação foi realizada.
Não se infere capacidade ou incapacidade de generalização.

## Inventário e I/O

| Buffer existente reservado | Bytes previstos | Opens reais | Bytes reais |
| --- | ---: | ---: | ---: |
| ESM1:73 | 1.951.506 | 0 | 0 |
| ESM1:219 | 1.951.506 | 0 | 0 |
| ESM2:73 | 1.951.506 | 0 | 0 |
| ESM2:219 | 1.951.506 | 0 | 0 |
| ESM4:98 | 1.940.004 | 0 | 0 |
| ESM4:295 | 1.940.004 | 0 | 0 |
| ESM5:98 | 1.940.004 | 0 | 0 |
| ESM5:295 | 1.940.004 | 0 | 0 |
| Total | 15.566.040 | 0 | 0 |

`io-audit.json` registra zero arquivos, zero opens e zero bytes.
O runner parou no preflight antes de criar AccountedReader e receipt.
A ausência do receipt textual foi confirmada; ele não foi fabricado
posteriormente. `HOLDOUT_RUN_ATTEMPT=NOT_ARMED`, CLI=1, ciência=0,
chamadas por par=0, retries=0. Nenhum DEV foi reaberto.

Comando único, sandbox padrão, exit 3:

```text
PYTHONPATH=src /usr/bin/python3 -B scripts/run_ti2r_solute_locked_holdout.py
```

## Resultados por caso e decisão

| Par | Índice | Identificabilidade | Scores, margens, ranks e resíduos | Resultado |
| --- | ---: | --- | --- | --- |
| ESM2→ESM1 | 73 | Não avaliada | Não calculados | NOT_EVALUATED |
| ESM2→ESM1 | 219 | Não avaliada | Não calculados | NOT_EVALUATED |
| ESM5→ESM4 | 98 | Não avaliada | Não calculados | NOT_EVALUATED |
| ESM5→ESM4 | 295 | Não avaliada | Não calculados | NOT_EVALUATED |

Nenhuma condição científica foi testada. Não existem scores favoráveis ou
desfavoráveis a selecionar, cobertura medida, resíduos, recuperação,
máximo único, rank ou controle temporal calculado nesta tarefa.
`results.json` conserva stdout, exit code, incidente e campos nulos.
G2_SOLUTE permanece **BLOCKED_PENDING_LOCKED_HOLDOUT**.
Declarar PASS, FAIL científico ou CONSUMED seria incorreto neste caso.

Permanecem congelados os critérios por caso: SS8/NGF, máximo único da
identidade, margens >=0,005, suporte mínimo, quatro quadrantes, resíduos
mediana<=1/P95<=2/máximo<=3 px, ausência de ambiguidade/censura; identidade
e 16/16 recuperações, margem>=0,005, erro<=0,5 px e concordância.
Eles não foram flexibilizados nem executados sobre estes buffers.

## Verificações, CI e limites

Guard de dados: PASS, 250 entradas históricas, zero bytes experimentais.
Suíte stdlib antes da invocação: 423 testes, 337 passes, 86 skips opcionais.
Orquestração com mocks: 23 testes aprovados, zero erros/falhas/skips
(9 adaptador, 11 runner, 3 incidentes parciais).
Esses testes não substituíram a validação real do manifesto, que falhou.

CI remota consultada no C2: runs
[35399554524 — push](https://github.com/lmbernardo7520112/snbi-dendritic-fragmentation-ml/actions/runs/35399554524)
e [35399558120 — PR](https://github.com/lmbernardo7520112/snbi-dendritic-fragmentation-ml/actions/runs/35399558120);
ambos SUCCESS, dois jobs obrigatórios e todos os passos aprovados.
Não se alega CI remota do novo checkpoint local.
Não houve push, alteração do PR, Ready, merge ou exclusão de branch.

SEALED é específico à avaliação solutal: a exposição histórica das referências
em FRAG-DIRECT está declarada no manifesto e no protocolo C1.
O conjunto não constitui holdout globalmente virgem nem validação externa
em aquisições independentes. Nenhum pixel foi observado nesta tarefa.
Não houve desenvolvimento após observação de holdout, pois ela não ocorreu;
também não houve reparo ou desenvolvimento após o incidente.

`commands.json` registra os comandos e limites do inventário sanitizado.
Os comandos de staging/commit/verificação final pertencem ao retorno e ao
histórico Git, evitando novo commit autorreferente. O estado local final
deve ser confirmado após o checkpoint.

## Estado terminal

```text
PRE_HOLDOUT_GATE=FAIL
TI2R_SOLUTE_HOLDOUT=BLOCKED_PRE_EXECUTION_CONFIGURATION_DIVERGENCE
G2_SOLUTE=BLOCKED_PENDING_LOCKED_HOLDOUT
HOLDOUT_SOLUTE=SEALED
HOLDOUT_RUN_ATTEMPT=NOT_ARMED
SCIENTIFIC_INVOCATIONS=0
RETRIES=0
STATE=BLOCKED_PRE_EXECUTION
CURRENT_AUTHORIZED_ACTIVITY=NONE_AWAITING_AUTHOR_DECISION
TI2R_SOLUTE_HOLDOUT_AUTHORIZED=false
TI3_PLUS_AUTHORIZED=false
MERGE_AUTHORIZED=false
```

A fase encerra em incidente operacional antes dos pixels. Qualquer retomada
exige nova decisão do autor; não há retry automático nesta autorização.
