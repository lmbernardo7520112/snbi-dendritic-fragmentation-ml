# Resultados canônicos do programa científico

Este documento transcreve os resultados textuais já encerrados de Experiment 1 e Study2-A/B/C/D. O fechamento não executa scorer, fit, feature extractor ou avaliação, e não altera a seleção final. Os números integrais são preservados nas evidências indicadas. PASS descreve cumprimento do protocolo, não um piso de desempenho.

## Experiment 1 — desenvolvimento e confirmação final

| Etapa | População e papel | Resultado registrado | Fonte |
| --- | --- | --- | --- |
| TI3-A, LBP estrutural + RF | TRAIN 34 samples; DEVELOPMENT 16 samples | DEVELOPMENT balanced accuracy = 0.6875; confusão [[3,5],[0,8]] | [Relatório TI3-A](../../artifacts/evidence/TI3_A_RESUME/c0r1-resume/execution-report.md) |
| TI3-B, LBP multimodal + RF | Mesmos TRAIN e DEVELOPMENT | DEVELOPMENT balanced accuracy = 0.75; confusão [[4,4],[0,8]] | [Relatório TI3-B](../../artifacts/evidence/TI3_B_SOLUTAL/execution-report.md) |
| TI3-C, CNN mínima multimodal | Mesmos TRAIN e DEVELOPMENT; arquitetura fixa com 170 parâmetros | DEVELOPMENT balanced accuracy = 0.50; confusão [[0,8],[0,8]]; MULTIMODAL_LBP_RF selecionado pela regra prévia | [Relatório TI3-C](../../artifacts/evidence/TI3_C_CNN/execution-report.md) |
| TI3-D, avaliação final única | Um fit nos 50 TRAIN+DEV, 25 por classe; FINAL com seis samples, três por classe | Balanced accuracy, accuracy, precision, recall e F1 = 0.6666666666666666; confusão [[2,1],[1,2]] | [Relatório final](../../artifacts/evidence/TI3_D_FINAL/execution-report.md), [estado terminal](../../artifacts/evidence/TI3_D_FINAL/terminal-state.json) |

O resultado final corresponde a quatro acertos em seis weak labels, TN2/FP1/FN1/TP2. Seu escopo é `SMALL_INTERNAL_TEMPORAL_CONFIRMATION`, com exposição histórica declarada; `ML_FINAL_TEST=CONSUMED`. O resultado negativo da CNN permanece parte da história, sem nova arquitetura ou tuning retrospectivo.

## Study2-A — evidência gráfica temporal

A mineração processou 689 frames e estabeleceu 87 identidades AUTO_GOLD, com 7.941 observações DIRECT_VALID e 5.737 AUTO_SILVER. Os 52 sites legados foram mapeados; não houve conflito, Hough, revisão humana, criação de patches ou ML. Essas quantidades vêm do [estado terminal A](../../artifacts/evidence/STUDY2_A_ANNOTATION_MINING/terminal-state.json).

Os agregados de componentes usam exclusivamente os nomes da [reconciliação canônica](../../artifacts/evidence/STUDY2_A_ANNOTATION_MINING/METRIC_SEMANTICS_RECONCILIATION.json), chave `canonical_metrics`:

| Métrica canônica | Valor | Unidade/população |
| --- | ---: | --- |
| AMBIGUOUS_COMPONENTS_TOTAL | 24246 | Todas as ocorrências AMBIGUOUS |
| AMBIGUOUS_UNSUPPORTED_BY_KNOWN_SITE | 18670 | AMBIGUOUS sem suporte completo de site conhecido |
| AMBIGUOUS_EXPLAINED_BY_ONE_KNOWN_SITE | 5415 | AMBIGUOUS explicado por um site conhecido |
| AMBIGUOUS_EXPLAINED_BY_MULTIPLE_KNOWN_SITES | 161 | AMBIGUOUS explicado por múltiplos sites conhecidos |
| SMALL_COMPONENTS_TOTAL | 292 | Todas as ocorrências SMALL |
| UNRESOLVED_SITE_HYPOTHESIS_COMPONENTS | 18962 | AMBIGUOUS sem suporte + SMALL neste corpus |
| NON_VALID_COMPONENTS_TOTAL | 24538 | Todas as ocorrências AMBIGUOUS + SMALL |

A unidade é uma ocorrência `(source_id, frame_index, component_id)`, incluindo repetições temporais. Nenhuma contagem dessa tabela é número de novos sites ou eventos físicos. O nome histórico `potential_new_site_unresolved_components` ficou preservado na evidência original, mas seu valor 24538 corresponde a `NON_VALID_COMPONENTS_TOTAL` neste corpus; consumidores devem usar a reconciliação.

## Study2-B — corpus multimodal

| Quantidade canônica | Valor |
| --- | ---: |
| Registros site×frame de entrada e contabilizados | 27396 |
| Pares multimodais válidos | 16500 |
| INVALID_BOTH | 10896 |
| GOLD válido | 5218 |
| SILVER válido | 3687 |
| UNLABELED_PRE válido | 5181 |
| UNLABELED_PERSISTENCE válido | 2414 |
| Não rotulados válidos, total registrado | 7595 |
| Sites com pares válidos | 52 |
| Candidatos a background, somente metadados nessa fase | 70844 |
| Tracks espaciais de background | 223 |

Fontes: [estado terminal B](../../artifacts/evidence/STUDY2_B_CORPUS/terminal-state.json) e [results.json](../../artifacts/evidence/STUDY2_B_CORPUS/results.json), chaves `pair_status_counts`, `valid_tier_counts` e `metrics`. A cobertura registrada é 0.6022777047744197. Os 35 sites sem suporte válido foram preservados no inventário; não são erros de um classificador. Os 52 sites válidos não equivalem ao conjunto de 52 sites legados de A. Não houve substituição, deslocamento, padding ou promoção dos não rotulados a negativos. `ML_RUNS=0`.

## Study2-C — pipeline final selecionado

O resultado final permanece **RF_REFERENCE + GOLD_PLUS_SILVER**, com representação LBP20 de STRUCTURAL_Y + RELATIVE_SOLUTE_FIELD_Y, patches 65×65. O RF manteve 100 árvores, seed 42 e os 19 parâmetros históricos. A seleção usou DEVELOPMENT segundo GMBA prévia; Study2-D não a reabriu.

| Modelo comparado | GMBA DEVELOPMENT registrada no relatório, arredondada a seis casas |
| --- | ---: |
| LOGISTIC_REGRESSION | 0.845300 |
| SVM_RBF | 0.787188 |
| RF_REFERENCE | 0.875902 |
| RF_TUNED | 0.874898 |
| CNN_V2 | 0.705134 |

Os valores integrais e as decisões estão nos [resultados canônicos C](../../artifacts/evidence/STUDY2_C_BENCHMARK/RESULTS_SUMMARY.json); a tabela histórica está no [relatório C](../../artifacts/evidence/STUDY2_C_BENCHMARK/execution-report.md). A ablação SILVER registrou GMBA DEVELOPMENT GOLD = 0.8759021928689068 e GOLD+SILVER = 0.8775115148991031, delta = 0.0016093220301962585. A regra de melhora estrita selecionou GOLD_PLUS_SILVER; outras métricas não substituíram a primária.

| Métrica TEST canônica | Valor registrado |
| --- | ---: |
| GMBA primária | 0.8449139278495638 |
| Balanced accuracy por observação | 0.8525933757278337 |
| Accuracy por observação | 0.8621430764507215 |
| Precision por observação | 0.6631908237747653 |
| Recall por observação | 0.8346456692913385 |
| F1 por observação | 0.7391051714119697 |
| Macro recall dos sites positivos | 0.7933145536774319 |
| Macro especificidade dos tracks BG | 0.8965133020216957 |
| Balanced accuracy por voto majoritário de grupo | 0.95 |
| GMBA bottom_up | 0.8575480543482503 |
| GMBA top_down | 0.7943774218548179 |

A confusão TEST é [[2172,323],[126,636]], com classes [0,1], linhas verdadeiras e colunas preditas. São 3.257 observações, 762 GOLD e 2.495 BG, distribuídas em dez sites positivos e dez tracks BG, nas mesmas duas aquisições; top_down tem apenas dois sites + dois tracks. Houve 80 fits CV, cinco comparações, uma ablação SILVER e um fit final, além de uma única avaliação TEST. Fontes: `RESULTS_SUMMARY.json → counts`, `test`, e [estado terminal C](../../artifacts/evidence/STUDY2_C_BENCHMARK/terminal-state.json).

O escopo é `INTERNAL_GROUP_HELD_OUT_TEST`, restrito aos 52 sites com suporte válido. `TEST_STATE=CONSUMED`. A alta métrica por maioria não elimina erros dentro de trajetórias: o relatório registra um site com recall 2/32 = 0.0625 e 277 falsos positivos entre 790 observações BG em top_down.

## Study2-D — atribuição controlada pós-hoc

Study2-D usou exclusivamente 10.907 rows TRAIN de C: 3.858 GOLD e 7.049 BG, com 32 grupos de cada classe. Reutilizou quatro folds históricos e o RF/LBP fixo. Houve 100 fits distintos; D1/K24 e DALL/GROUP_EQUAL foram reutilizados nas comparações previstas. DEV, TEST, SILVER, novos backgrounds e vídeos ficaram fora.

| Condição | GMBA CV média registrada |
| --- | ---: |
| K4 / D1 / GROUP_EQUAL | 0.775093408673069 |
| K8 / D1 / GROUP_EQUAL | 0.7688974484656079 |
| K12 / D1 / GROUP_EQUAL | 0.7784961861373184 |
| K17 / D1 / GROUP_EQUAL | 0.7747648777763951 |
| K24 / D1 / GROUP_EQUAL | 0.7786692086875789 |
| K24 / D3 / GROUP_EQUAL | 0.7697124456485938 |
| K24 / D5 / GROUP_EQUAL | 0.7735548436540266 |
| K24 / DALL / GROUP_EQUAL | 0.7189698985429366 |
| K24 / DALL / OBSERVATION_EQUAL | 0.7335568007189566 |

Fonte: [relatório D, tabela narrativa](../../artifacts/evidence/STUDY2_D_ATTRIBUTION/EXECUTION_REPORT.md) e [RESULTS_TABLES.md](../../artifacts/evidence/STUDY2_D_ATTRIBUTION/RESULTS_TABLES.md). K é o número de grupos por classe no lado de treino do fold; D indica a amostragem temporal dentro de cada grupo. A validação usa todas as observações autorizadas dos grupos TRAIN retidos no fold. Esta tabela contém somente CV interna TRAIN de D, sem inserir o TEST C como condição comparável.

| Contraste | Delta médio GMBA | Sinais registrados | Descritor |
| --- | ---: | --- | --- |
| K24 − K17 | +0.0039043309111838507 | 11 positivos, 0 zero, 9 negativos; 20 pares | MIXED_POSITIVE |
| K24 − K4 | +0.0035758000145099554 | 11 positivos, 0 zero, 9 negativos; 20 pares | Sem descritor próprio pré-definido |
| DALL − D1 | −0.059699310144642304 | Quatro folds globais negativos | NON_POSITIVE |
| GROUP_EQUAL − OBSERVATION_EQUAL | −0.014586902176019961 | Quatro folds globais negativos | NO_GROUP_EQUAL_BENEFIT |

Fontes: [ATTRIBUTION_SUMMARY.json](../../artifacts/evidence/STUDY2_D_ATTRIBUTION/ATTRIBUTION_SUMMARY.json), [GROUP_DIVERSITY_RESULTS.json](../../artifacts/evidence/STUDY2_D_ATTRIBUTION/GROUP_DIVERSITY_RESULTS.json), [TEMPORAL_DENSITY_RESULTS.json](../../artifacts/evidence/STUDY2_D_ATTRIBUTION/TEMPORAL_DENSITY_RESULTS.json), [GROUP_WEIGHTING_RESULTS.json](../../artifacts/evidence/STUDY2_D_ATTRIBUTION/GROUP_WEIGHTING_RESULTS.json).

O benefício descritivo K24−K17 foi pequeno e misto. A curva de diversidade não é monotônica: K8 ficou abaixo de K4, e K17 abaixo de K12. Sob o protocolo congelado, replicação temporal densa não melhorou a CV agrupada e reduziu a GMBA média. A ponderação por grupo também não trouxe benefício no cenário denso fixo. Esses resultados permanecem válidos e não autorizam substituir retrospectivamente o pipeline C.

**NUMBER_OF_ROWS não equivale a NUMBER_OF_INDEPENDENT_EXPERIMENTAL_UNITS.** Milhares de rows temporalmente correlacionadas não superaram uma observação representativa por grupo neste desenho específico. Isso não é uma lei universal e não significa que mais frames causem dano físico.

## Relação entre os estudos

Experiment 1 teve TRAIN 17 positivos + 17 backgrounds e uma confirmação FINAL de três + três. K17 de D é apenas `NUMERICAL_SCALE_BRIDGE`: 17 grupos por classe com observação representativa não equivalem cientificamente a 17 samples por classe do primeiro estudo.

Experiment 1 reporta balanced accuracy por observação em FINAL pequeno; C reporta GMBA primária em TEST agrupado; D reporta CV pós-hoc restrita ao TRAIN original. Corpus, grupos, splits, pesos, quantidade e avaliação diferem. Seus valores não são estimativas diretamente equivalentes, e não foram recalculados neste fechamento.

Study2-D não identificou um fator positivo único suficiente para explicar a diferença histórica Experiment 1 → Study2-C. A diferença é compatível com uma combinação/interação de mudanças data-centric e metodológicas, cuja decomposição causal não foi identificada. Não se somam os deltas, não se atribuem percentuais causais e não se afirma generalização externa, significância universal ou causalidade física.

As [limitações científicas](SCIENTIFIC_LIMITATIONS.md) completam o escopo. Os estados históricos consumidos permanecem intactos; o [índice de evidências](EVIDENCE_INDEX.md) relaciona fontes e freezes.
