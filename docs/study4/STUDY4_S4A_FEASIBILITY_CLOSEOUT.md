# Study4 S4-A — Feasibility closeout

Este checkpoint preserva a única análise metadata-only S4-A1, executada no
freeze `ec00a82b168e187a93df8b9d725d7f069b28f179`. Os valores abaixo são
transcritos da evidência consumida; nenhuma análise ou matching foi reexecutado
neste checkpoint.

```text
STUDY4_S4A=PASS
STATE=CLOSED_CONSUMED
AUTHORITY_CONSUMED=true
METADATA_ANALYSIS_INVOCATIONS=1
RETRY_AUTHORIZED=false
FEASIBILITY_DECISION=SUFFICIENT_COMMON_SUPPORT
TOTAL_MAX_MATCHING_CAPACITY=25
BOTTOM_UP_MAX_MATCHING_CAPACITY=17
TOP_DOWN_MAX_MATCHING_CAPACITY=8
MIN_REQUIRED_PAIRS=16
BOTH_ACQUISITIONS_REPRESENTED=true
FINAL_PAIR_MATCHING_EXECUTED=false
PAIR_IDENTITIES_SELECTED=false
VISUAL_MODEL_EXECUTION_ALLOWED=false
CURRENT_AUTHORIZED_ACTIVITY=NONE_AWAITING_AUTHOR_DECISION
```

O corpus histórico possui common support temporal suficiente, segundo o
critério pré-registrado, para justificar o desenvolvimento do S4-B. A capacidade
25 é um resultado de feasibility: não significa que 25 pares finais já foram
selecionados, nem que a solução com 25 pares seja necessariamente única sob
todos os objetivos secundários. O resultado não demonstra aprovação do
coverage-neutralization gate, não autoriza qualquer CNN e não antecipa
desempenho visual positivo. O S4-B depende de nova decisão do autor.

A evidência registra 10.907 rows autenticadas: 3.858 positivas e 7.049
background, em 32 grupos positivos e 32 grupos background. O hash documental
do manifesto registrado é
`6ae3eee8e2fbe2c2e5de55eb84cb35b0ca7b561d37a8426b11125870003de531`.
O manifesto real não foi reaberto neste checkpoint.

| Aquisição | Grupos positivos | Grupos background | Candidate edges | Positivos isolados | Backgrounds isolados | Maximum matching capacity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Bottom-up | 24 | 24 | 227 | 7 | 4 | 17 |
| Top-down | 8 | 8 | 64 | 0 | 0 | 8 |

O grafo top-down é completo sob o critério de feasibility: há oito grupos de
cada classe e 64 candidate edges. O bottom-up contém grupos isolados e tem
capacidade máxima 17. Estes registros são agregados; não incluem identidades
de grupos ou pares, edge lists, possíveis pares ou frames selecionados.

Os três artefatos permanecem byte-idênticos aos auditados. O hash do resultado
também coincide com `result_sha256` registrado no terminal.

| Artefato em `artifacts/evidence/STUDY4_S4A_FEASIBILITY/` | SHA-256 |
| --- | --- |
| [s4a-feasibility-receipt.json](../../artifacts/evidence/STUDY4_S4A_FEASIBILITY/s4a-feasibility-receipt.json) | `e422f0d50dc99e1b5608331c99db6fc8250646901756012d810f14afb74c134e` |
| [feasibility-result.json](../../artifacts/evidence/STUDY4_S4A_FEASIBILITY/feasibility-result.json) | `a69257d10ee37580aa6a660e17cb41486cf3168a425d20bb11309dc91b152e63` |
| [terminal-state.json](../../artifacts/evidence/STUDY4_S4A_FEASIBILITY/terminal-state.json) | `6b2ae188ac558dcb39b2998ab4e4ca51bed767ef21c4e01c935f2db05dd7130c` |

```text
PAYLOAD_BINARY_READS=0
FEATURE_EXTRACTIONS=0
FITS=0
NEW_CORPUS_ANALYSIS=false
PAIR_IDENTITIES_DISCLOSED=false
SCIENTIFIC_METHOD_CHANGED=false
```

Antes de olhar identidades, o S4-B deverá congelar:

1. O algoritmo de final matching.
2. O objetivo secundário de common-frame support.
3. O desempate determinístico.
4. A seleção dos oito frames compartilhados.
5. A criação de pair_id.
6. A atribuição pair-aware de quatro folds.
7. A regra exata do coverage-neutralization gate.

Nenhum desses procedimentos foi executado neste checkpoint. O controle local
`STUDY4_S4A_FEASIBILITY_AUTHORIZATION.json` permanece intacto e untracked,
fora do index e deste commit, conforme esclarecimento explícito do autor.
