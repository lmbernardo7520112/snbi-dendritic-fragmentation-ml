# Suficiência estrutural dos weak labels disponíveis

**PASS estrutural: 52 annotation_site_ids únicos.** O gate autoral exige somente
a possibilidade combinatória de três partições futuras não vazias e disjuntas
por site. Não houve materialização de TRAIN, DEVELOPMENT ou FINAL_TEST.

| Fonte / aquisição | Observações positivas | Sites únicos | Uma observação | Repetidos | IGNORE |
| --- | ---: | ---: | ---: | ---: | ---: |
| ESM3 / bottom_up_anti_parallel | 71 | 38 | 18 | 20 | 357 |
| ESM6 / top_down_parallel | 37 | 14 | 1 | 13 | 26 |
| Total | 108 | 52 | 19 | 33 | 383 |

Os 383 IGNORE incluem 380 componentes ambíguos e três pequenos. São regiões
por observação, com bbox, motivo e proveniência no ledger; não são 383 locais
físicos independentes. Os 108 positivos são todas as aceitações A0, sem
seleção adicional. 52 sites operacionais também não são 52 aquisições/eventos
físicos independentes.

| Observações por site | Quantidade de sites |
| --- | ---: |
| 1 | 19 |
| 2 | 16 |
| 3 | 11 |
| 4 | 6 |

A soma ponderada é 108. Repetições de um site não aumentam o N de grupos.
Sites com uma observação não foram excluídos por conveniência.

## Distribuição temporal e FIRST_CONFIDENT_OBSERVATION

| Fonte:frame | Tempo experimental s | Positivos observados | IGNORE | Sites com primeira observação confiante |
| --- | ---: | ---: | ---: | ---: |
| ESM3:0 | -25.96 | 0 | 0 | 0 |
| ESM3:73 | 60.18 | 14 | 77 | 14 |
| ESM3:146 | 146.32 | 18 | 94 | 10 |
| ESM3:219 | 232.46 | 19 | 93 | 8 |
| ESM3:293 | 319.78 | 20 | 93 | 6 |
| ESM6:0 | -34.22 | 0 | 0 | 0 |
| ESM6:98 | 81.42 | 2 | 7 | 2 |
| ESM6:197 | 198.24 | 12 | 6 | 10 |
| ESM6:295 | 313.88 | 12 | 6 | 2 |
| ESM6:394 | 430.7 | 11 | 7 | 0 |

Os zeros de componentes nos frames iniciais não viram negativos físicos.
Primeira observação confiante é o primeiro aceite entre os frames examinados;
não é onset. Rejeições variáveis do extrator podem atrasar esse atributo.
Valores e centros individuais permanecem no SITE_DEDUPLICATION.json.
A associação fixada em 3 px não foi ajustada depois destas contagens.

## Gate e alcance

52 >=3 satisfaz o gate único. Ambas as aquisições têm mais de três sites,
permitindo representação de cada uma em três partições por contagem.
O SPLIT_CONTRACT.md especifica a regra determinística futura sem gerar IDs.

PASS não comprova poder estatístico, precisão de métricas, quantidade de
backgrounds utilizáveis, isolamento dos futuros patches ou suficiência dos
grupos após eventuais restrições de contexto. Esses requisitos da futura
materialização deverão ser testados antes de treinamento/avaliação.
Não foi inventado um limiar mínimo estatístico, reequilíbrio ou exclusão.

Os dez ativos A0 continuam de desenvolvimento de anotações e não são
promovidos a FINAL_TEST. A definição dos labels e dos sites teve exposição
histórica declarada. O futuro resultado poderá sustentar validação interna
agrupada nas duas aquisições disponíveis, não generalização externa ou um
teste de imagens globalmente virgens.

TARGET_CONTRACT=FROZEN no escopo de detecção de localização publicada.
TI3_A_READY_TO_RESUME=true significa prontidão para a próxima decisão do
autor, sem iniciar TI3-A nesta tarefa. ML_RUNS=0.
FINAL_TEST=NOT_DEFINED_NOT_OPENED.
