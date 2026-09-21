# Study2-A — reconciliação pós-run da semântica dos agregados

**STUDY2_A_METRIC_RECONCILIATION=PASS; SCIENTIFIC_RESULT_IMPACT=NONE.**
As três quantidades históricas contam populações distintas de componentes
gráficos. O campo `potential_new_site_unresolved_components=24538` soma todos
os componentes AMBIGUOUS e SMALL, inclusive os explicados por sites conhecidos.
Seu nome canônico reconciliado é `NON_VALID_COMPONENTS_TOTAL`.

Esta auditoria documental está ancorada no checkpoint
`b8f6b4dba80af79812b93a5db391392b5eb1e69c`, branch
`feat/study2a-dense-annotation-ledger`. A autorização é o anexo autoral
“STUDY2-A POST-RUN METRIC SEMANTICS RECONCILIATION”, SHA-256
`d51b0be1fcd806e3ab1e36c13ff854ca860d1ab3b944870d57a4158d4a9d0e8b`.
O freeze científico permanece
`7d89329bf005f6a85ddc67d51d88b9e362878478`.

## Terminologia canônica

A unidade é uma ocorrência de componente gráfico em uma fonte/frame,
identificada por `(source_id, frame_index, component_id)`. Repetições temporais
continuam sendo ocorrências diferentes. Nenhuma das contagens abaixo mede
identidades de sites ou eventos físicos.

| Nome canônico | Valor | População verificada |
| --- | ---: | --- |
| AMBIGUOUS_COMPONENTS_TOTAL | 24246 | Todos os componentes AMBIGUOUS_OR_NONCIRCULAR |
| AMBIGUOUS_UNSUPPORTED_BY_KNOWN_SITE | 18670 | AMBIGUOUS classificados como POTENTIAL_NEW_SITE_UNRESOLVED |
| AMBIGUOUS_EXPLAINED_BY_ONE_KNOWN_SITE | 5415 | AMBIGUOUS classificados como EXPLAINED_BY_KNOWN_SITE |
| AMBIGUOUS_EXPLAINED_BY_MULTIPLE_KNOWN_SITES | 161 | AMBIGUOUS classificados como EXPLAINED_BY_MULTIPLE_KNOWN_SITES |
| SMALL_COMPONENTS_TOTAL | 292 | Todos os SMALL_COMPONENT |
| UNRESOLVED_SITE_HYPOTHESIS_COMPONENTS | 18962 | AMBIGUOUS sem suporte de site conhecido + SMALL |
| NON_VALID_COMPONENTS_TOTAL | 24538 | Todos os AMBIGUOUS + SMALL |

As identidades foram conferidas nos registros textuais já produzidos:

```text
18670 + 5415 + 161 = 24246
18670 + 292 = 18962
24246 + 292 = 24538
```

Neste corpus imutável, todos os 292 SMALL têm classificação temporal
`POTENTIAL_NEW_SITE_UNRESOLVED`. Portanto, 18962 também coincide com o total
dessa classificação entre todos os componentes não válidos. “Sem suporte”
significa ausência de suporte completo da região da âncora segundo a regra
congelada; não comprova um evento ou site novo.

## Origem da divergência documental

| Artefato histórico preservado | Campo ou trecho | Valor | Interpretação reconciliada |
| --- | --- | ---: | --- |
| QUALITY_DETAILS.json | ambiguous_component_temporal_classification / POTENTIAL_NEW_SITE_UNRESOLVED | 18670 | Apenas AMBIGUOUS sem suporte |
| execution-report.md, linha 33 | potential unresolved | 18962 | AMBIGUOUS sem suporte + SMALL |
| results.json e CORPUS_SUMMARY.json | potential_new_site_unresolved_components | 24538 | Todos os componentes não válidos |

O rastreamento estático de
[study2a_tracking.py](../../../src/snbi_fragmentation/study2a_tracking.py)
mostra que o bloco das linhas 384–415 ignora VALID e atribui
`potential_additional_site_unresolved=true` a todo AMBIGUOUS/SMALL.
A classificação temporal é definida separadamente. A linha 490 soma esse
booleano, sem filtrar a classificação `POTENTIAL_NEW_SITE_UNRESOLVED`.
[study2a_execution.py](../../../src/snbi_fragmentation/study2a_execution.py)
agrega os totais por fonte nas linhas 496–503 e os serializa nos relatórios.
Esse caminho explica exatamente o valor 24538.

O booleano histórico conserva a possibilidade de traço adicional desconhecido
mesmo em um componente com suporte de site conhecido. Essa cautela não
transforma sua soma em número de possíveis sites. Os nomes canônicos separam
explicitamente o total não válido da classificação temporal não resolvida.

| População | ESM3 | ESM6 | Total |
| --- | ---: | ---: | ---: |
| AMBIGUOUS | 21834 | 2412 | 24246 |
| AMBIGUOUS sem suporte | 17335 | 1335 | 18670 |
| AMBIGUOUS explicado por um site | 4338 | 1077 | 5415 |
| AMBIGUOUS explicado por múltiplos sites | 161 | 0 | 161 |
| SMALL | 289 | 3 | 292 |
| Hipótese não resolvida | 17624 | 1338 | 18962 |
| Não válidos | 22123 | 2415 | 24538 |

## Prova de impacto científico NONE

A criação/associação de sites nas linhas 339–380, os estados das observações
nas linhas 423–436 e a elegibilidade AUTO_GOLD nas linhas 451–456 de
`study2a_tracking.py` não dependem desse agregado posterior. Os gates das
linhas 519–525 e 557–559 de `study2a_execution.py` também não o consomem.
A busca literal em src/scripts/tests identificou apenas a produção/agregação
do campo e uma asserção sintética do booleano; nenhum teste foi executado
localmente nesta reconciliação. Uma revisão estática independente conferiu
essa conclusão.

Permanecem 689 frames processados, 87 sites AUTO_GOLD, 7941 observações
DIRECT_VALID, 5737 AUTO_SILVER, 24246 AMBIGUOUS, 292 SMALL, 52/52 sites legados
mapeados e zero conflitos. Study2-A continua PASS, com uma execução científica
histórica e autoridade CLOSED_CONSUMED; HUMAN_REVIEW_USED e HOUGH_EXECUTED
continuam false. Nenhum código, parâmetro, site, observação, tracking ou
resultado científico foi alterado.

## Verificação e custódia

Foram autenticados os 35 hashes do freeze e os 34 hashes pós-run, incluindo
correspondência com os blobs Git no checkpoint. A verificação dos JSONL
existentes usou somente biblioteca padrão e aritmética, sem importar ou
invocar decoder, detector, tracker ou pipeline científico.

| JSONL textual existente | Bytes | Registros | SHA-256 |
| --- | ---: | ---: | --- |
| OBSERVATION_LEDGER.jsonl | 17786087 | 27396 | 3cb444271839b1fca18c3228f91e961e9566173e3036696db3dadf537234bfcc |
| candidate-components.jsonl | 49636870 | 32479 | b9e4ce16c967e4ffc6f6f2b1e86e21727971a444c20a38667cc1b53ae9ceb19c |

Esses dois arquivos em `data/derived/study2/` permaneceram inalterados e fora
do staging. Os 67422957 bytes acima são metadados derivados textuais; nenhum
conteúdo de fonte experimental foi aberto. Os registros completos de
contagem, hashes e referências estão no
[JSON desta reconciliação](METRIC_SEMANTICS_RECONCILIATION.json).
Os inventários delimitam as verificações realizadas; não constituem
monitoramento universal de syscalls.

Os quatro artefatos históricos `results.json`, `CORPUS_SUMMARY.json`,
`QUALITY_DETAILS.json` e `execution-report.md` foram preservados byte a byte.
Esta reconciliação aditiva não reescreve seus valores ou a história da execução.

## Contrato para consumidores futuros

Study2-B deve consumir exclusivamente os sete nomes de `canonical_metrics`
no JSON desta reconciliação. O campo histórico mal nomeado serve à auditoria
de proveniência; sua correspondência com `NON_VALID_COMPONENTS_TOTAL` foi
demonstrada para este corpus congelado, sem inferir equivalência universal.
É proibido interpretar 18670 como novos eventos físicos, 18962 como novos
sites ou 24538 como potenciais sites. Suporte por um site conhecido não prova
ausência de traço adicional desconhecido.

Este contrato não autoriza Study2-B, dataset, ML ou nova mineração. Qualquer
fase futura depende de decisão própria. A ciência Study2-A permanece consumida.

## Publicação e terminal

O escopo de publicação é exatamente este Markdown e o JSON correspondente,
em um único commit documental, seguido de push fast-forward na mesma branch.
Nenhuma CI futura é antecipada aqui: SHA efetivo, conclusão de todos os sete
jobs e seus passos e prontidão para integração serão informados no retorno
ao operador após a verificação remota. O commit não autoriza merge.

```text
STUDY2_A_METRIC_RECONCILIATION=PASS
SCIENTIFIC_RESULT_IMPACT=NONE
AMBIGUOUS_COMPONENTS_TOTAL=24246
AMBIGUOUS_UNSUPPORTED_BY_KNOWN_SITE=18670
AMBIGUOUS_EXPLAINED_BY_ONE_KNOWN_SITE=5415
AMBIGUOUS_EXPLAINED_BY_MULTIPLE_KNOWN_SITES=161
SMALL_COMPONENTS_TOTAL=292
UNRESOLVED_SITE_HYPOTHESIS_COMPONENTS=18962
NON_VALID_COMPONENTS_TOTAL=24538
LEGACY_SITES_MAPPED=52
UNIQUE_AUTO_GOLD_SITES=87
DIRECT_VALID_OBSERVATIONS=7941
AUTO_SILVER_OBSERVATIONS=5737
EXPERIMENTAL_SOURCE_OPENS=0
FRAMES_DECODED=0
SCIENTIFIC_RUNS=0
ML_RUNS=0
STUDY2_B_AUTHORIZED=false
MERGE_AUTHORIZED=false
CURRENT_AUTHORIZED_ACTIVITY=NONE_AWAITING_AUTHOR_DECISION
```
