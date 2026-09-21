# Study2-B — qualidade do corpus congelado

**PASS de construção e contabilização, sem gate de quantidade ou accuracy.**

Todos os 27.396 registros longitudinais têm exatamente um status. Os 10.896 inválidos estão presentes no índice com row_index=null; não houve substituição, padding, resize, deslocamento ou perda de registros.

| Tier | Entrada | Válidos | Inválidos | Cobertura |
| --- | ---: | ---: | ---: | ---: |
| GOLD | 7941 | 5218 | 2723 | 65.70960836% |
| SILVER | 5737 | 3687 | 2050 | 64.26703852% |
| UNLABELED_PRE | 8911 | 5181 | 3730 | 58.14162271% |
| UNLABELED_PERSISTENCE | 4807 | 2414 | 2393 | 50.21843145% |

Os não rotulados somam 13.718 entradas e 7.595 válidos. PRE não é negativo ou background; PERSISTENCE não foi promovido a GOLD/SILVER.

| Métrica | Valor |
| --- | --- |
| PAIR_COVERAGE | 0.6022777047744197 |
| GOLD_PAIR_COVERAGE | 0.6570960836166729 |
| SILVER_PAIR_COVERAGE | 0.6426703852187554 |
| UNLABELED_PAIR_COVERAGE | 0.5536521358798658 |
| VALID_PAIR_COUNT | 16500 |
| INVALID_PAIR_COUNT | 10896 |
| VALID_SITE_COUNT | 52 |
| SITES_WITH_COMPLETE_TRAJECTORY | 52 |
| STRUCTURAL_HASH_COMPLETENESS | true |
| SOLUTAL_HASH_COMPLETENESS | true |
| PAIR_HASH_COMPLETENESS | true |
| PROVENANCE_COMPLETENESS | true |
| BACKGROUND_POOL_SIZE | 70844 |
| BACKGROUND_TRACK_COUNT | 223 |
| STORAGE_BYTES | 259036080 |
| TEMP_BYTES | 0 |
| PEAK_RSS_KIB | 410376 |
| PEAK_RSS_SCOPE | Python parent only; child decoder peak not instrumented |

Contagem de status: VALID_PAIR=16.500; INVALID_BOTH=10.896; INVALID_STRUCTURAL_SUPPORT=0; INVALID_SOLUTAL_SUPPORT=0; DECODE_ERROR=0. As 52 trajetórias com suporte válido são completas; os outros 35 sites permanecem no corpus documental como exclusões. A coincidência numérica com os 52 sites legados não constitui identidade demonstrada desses conjuntos.

Hashes completos significam presença e formato/proveniência dos hashes produzidos durante a leitura/escrita única, com confronto dos 25 overlaps históricos. O container não foi reaberto para recomputar hashes ou inspecionar pixels após o run. Os ledgers textuais podem ser autenticados separadamente.

As views são row indices do mesmo container: GOLD_VIEW=5.218; GOLD_PLUS_SILVER_VIEW=8.905; UNLABELED_VIEW=7.595; FULL_LONGITUDINAL_VIEW=16.500. Não há duplicação de pixels entre views, split ou balanceamento.

O pool possui 70.844 candidatos e 223 tracks espaciais. Não foram materializados patches de background, aplicadas quotas ou selecionados candidatos por desempenho. A seleção e os grupos para um futuro benchmark dependem de autorização própria.

Armazenamento agregado: 259036080 bytes. Cache de pixels=139425000 bytes, abaixo de2GiB; ledgers=119611080 bytes, abaixo do budget adicional256MiB. TEMP_PEAK_BYTES=0. Free disk final=666263302144 bytes, acima de50GiB. PEAK_RSS=410376 KiB mede somente o processo Python; memória interna dos decoders não foi medida e não é confundida com temporários em disco.

GOLD e SILVER são tiers automáticos de localização gráfica publicada. Background não prova ausência física. Duas aquisições, 87 identidades gráficas e repetições temporais não equivalem a milhares de amostras experimentais independentes. Este PASS não demonstra adequação estatística de um futuro split, performance, onset físico, forecasting, causalidade, Bi absoluto, temperatura ou generalização externa.

ML_RUNS=0; HUMAN_REVIEW_USED=false; STUDY2_C_AUTHORIZED=false.

## Auditoria documental por aquisição

A auditoria de coordenadas textuais localizou os 35 sites excluídos fora da geometria histórica: 10 no limite superior, 22 no inferior, dois no esquerdo e um no direito. Isso explica a exclusão constante em ambas as modalidades sem reinspecionar chroma. Na aquisição bottom_up, 40 de 69 sites têm trajetória válida; na top_down, 12 de 18. Dos 52 sites válidos, 33 coincidem com identidades legadas e 19 são novos; outros 19 legados ficaram inválidos. A contagem 52 não representa repetição do conjunto legado.

O pool se distribui em 12.384 candidatos/75 tracks bottom_up e 58.460 candidatos/148 tracks top_down. Isso registra a composição observada; não houve rebalanceamento. As contagens e predicados completos constam em POST_RUN_INDEPENDENT_AUDIT.json.
