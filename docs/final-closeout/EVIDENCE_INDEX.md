# Índice de evidências do fechamento científico

Este índice mapeia conclusões para evidências textuais existentes e respectivos freezes/checkpoints Git. Nenhuma métrica foi recalculada durante o fechamento. Os JSON de resultados e estados abaixo são registros históricos; não são novos grants de autoridade. O [PROVENANCE.json](../../artifacts/evidence/FINAL_CLOSEOUT/PROVENANCE.json) reúne os vínculos de integração e publicação efetivamente observados.

## Domínio, geometria e resolução das weak labels

As referências desta seção foram conferidas documentalmente na auditoria histórica do fechamento. Um commit de resultado/encerramento é identificado como tal; não é apresentado como freeze anterior à execução.

| Fase/conclusão | Registro Git de origem | Evidência textual | Métrica/estado e limite |
| --- | --- | --- | --- |
| Domínio e modalidades de duas aquisições | `92b08e1b349a864be089a1b8dfcbd1fb9e5f6cf5`, checkpoint documental G1/G2_TEMP | [G1/modalities-report.json](../../artifacts/evidence/G1/modalities-report.json), [README](../../README.md) | G1 PASS; separação entre estrutural, campo solutal relativo e camada gráfica publicada; duas aquisições, sem Bi absoluto |
| Correspondência temporal | Mesmo checkpoint G1/G2_TEMP | [G2_TEMP/temporal-correspondence-report.json](../../artifacts/evidence/G2_TEMP/temporal-correspondence-report.json) | PASS para correspondência de índices; não identifica onset físico exato nem valida forecasting |
| Registro método-v1 insuficiente | `f3c6da78b04299475c7bb85e986eb7435b08bd22`, resultado preservado | [TI2/execution-report.md](../../artifacts/evidence/TI2/execution-report.md) | METHOD_V1=INSUFFICIENT_EVIDENCE; G2_SPATIAL=BLOCKED_METHOD_V1; G3=BLOCKED_DEPENDENCY_G2 |
| Tentativa FRAG bloqueada | C1 `5f9c22a0cfc75622614734e8eb288104f04da827`; C2 `40874c92e65fbd13a05be7b8d98aa17fadd1f79c` | [TI2R_FRAG/execution-report.md](../../artifacts/evidence/TI2R_FRAG/execution-report.md) | BLOCKED_REFERENCE_INSUFFICIENT; resultado histórico não substituído por sucesso posterior |
| Mapeamento direto da camada gráfica | C1 `cf84c5ef1c5b6f8efb39b87825d9bc08f34014b7`; C2 `a91b7093ce7dff530ab9020d5f69c30d365c10f5` | [TI2R_FRAG_DIRECT/execution-report.md](../../artifacts/evidence/TI2R_FRAG_DIRECT/execution-report.md) | PASS_DIRECT_RASTER_MAPPING; identidade (0,0); início da sequência NON_IDENTIFIABLE |
| Solutal DIRECT não discriminativo | C1 `45c5acbcfbc33e4a1af1d35fc2ef961d6bd15ad1`; C2 `8b5d286e227d896eb639a743c26da4c4fe6ec582` | [TI2R_SOLUTE_DIRECT/execution-report.md](../../artifacts/evidence/TI2R_SOLUTE_DIRECT/execution-report.md) | BLOCKED_IDENTITY_NOT_DISCRIMINATIVE; pisos absolutos SS8/NGF falharam, preservados como negativos |
| Critérios relativos V2 congelados em DEV | Freeze `e1a98917a20431ecc1c758f210b5e974b3533734` | [TI2R_SOLUTE_V2/execution-report.md](../../artifacts/evidence/TI2R_SOLUTE_V2/execution-report.md) | PASS_PROTOCOL_FROZEN_READY_FOR_HOLDOUT_DECISION; não equivale, sozinho, à execução holdout |
| Primeiro preflight holdout bloqueado | `7994771e239afdb998a644626c423c1c627f80a0`, checkpoint da recusa | [TI2R_SOLUTE_HOLDOUT/execution-report.md](../../artifacts/evidence/TI2R_SOLUTE_HOLDOUT/execution-report.md) | CONFIGURATION_DIVERGENCE; preflight FAIL antes de ciência e bytes |
| Holdout solutal após reparo autorizado | Reparo `febaa56efdcec210f6efb0d456ab1558bce7fe43`; resultado `893cbb8e9e5cdc5a8422081304ec4189000b8a42` | [Holdout repair-1/execution-report.md](../../artifacts/evidence/TI2R_SOLUTE_HOLDOUT/repair-1/execution-report.md) | G2_SOLUTE=PASS; uma execução consumida; resultados DIRECT/V2 anteriores preservados |
| A0: extração gráfica e bloqueio do target | `0f1284e86052e505e8ccfc9ceaecb58cb41065f2`, checkpoint preservado | [TI3_A0/execution-report.md](../../artifacts/evidence/TI3_A0/execution-report.md) | BLOCKED_TARGET_CONTRACT; 108 componentes aceitos, 380 ambíguos e 3 SMALL; extração gráfica não prova eventos físicos |
| Resolução explícita do target fraco | `41d523e038e844588ee7724e07b00f75bdf29fdc`, resolução publicada | [TI3_TARGET_RESOLUTION/execution-report.md](../../artifacts/evidence/TI3_TARGET_RESOLUTION/execution-report.md) | PASS; 52 sites / 108 observações / 383 IGNORE; target restrito FROZEN; A0 não reclassificado retroativamente |

Para uso didático de threshold/componentes, Sobel/NGF e decisões de exclusão, consultar [protocolo SOLUTE_DIRECT](../protocols/TI2R_SOLUTE_DIRECT_PROTOCOL.md), [alinhamento A0](../../artifacts/evidence/TI3_A0/COURSE_ALIGNMENT_LABEL_EXTRACTION.md), [alinhamento do target](../../artifacts/evidence/TI3_TARGET_RESOLUTION/COURSE_ALIGNMENT.md) e [alinhamento do fechamento Experiment 1](../../artifacts/evidence/TI3_FINAL_CLOSEOUT/COURSE_ALIGNMENT.md). A síntese deste fechamento está em [COURSE_ALIGNMENT_FINAL.md](COURSE_ALIGNMENT_FINAL.md).

## Experiment 1

| Fase/conclusão | Freeze científico | Checkpoint textual | Evidência | Métrica ou estado canônico |
| --- | --- | --- | --- | --- |
| TI3-A: baseline estrutural | `e6090121471faa8902f68ddd045ab8b54a2e77fc` | `cab4fcd6f2d1fb70027cc6abff2590fae3d7c64b` | [Relatório](../../artifacts/evidence/TI3_A_RESUME/c0r1-resume/execution-report.md), [results.json](../../artifacts/evidence/TI3_A_RESUME/c0r1-resume/results.json) | TI3_A=PASS; DEVELOPMENT BA = 0.6875; TRAIN 34 / DEV 16; uma execução; FINAL não avaliado nessa etapa |
| TI3-B: ablação multimodal | `965e2f10e25eef1fe45ac91c10b8424389f99c10` | `dc9d0bb467bfc3c94302bb59b91db296e788451e` | [Relatório](../../artifacts/evidence/TI3_B_SOLUTAL/execution-report.md), [results.json](../../artifacts/evidence/TI3_B_SOLUTAL/results.json) | TI3_B=PASS; DEVELOPMENT BA = 0.75; preferência STRUCTURAL_PLUS_RELATIVE_SOLUTE |
| TI3-C: CNN mínima e seleção | `b2d8839ca2b6c6e5ddd2be1de3ff9589ada9a93c` | `a0364a25694d149cb9e5dcb217de2b241fac0702` | [Relatório](../../artifacts/evidence/TI3_C_CNN/execution-report.md), [estado terminal](../../artifacts/evidence/TI3_C_CNN/terminal-state.json) | TI3_C=PASS; CNN DEVELOPMENT BA = 0.50; MULTIMODAL_LBP_RF selecionado; negativo preservado |
| TI3-D: FINAL único | `b7687575d391f642d2c80274f1bc984c45dbba1b` | `73afa095484817b32d9fb5de040848cdfec89a3f` | [Relatório](../../artifacts/evidence/TI3_D_FINAL/execution-report.md), [estado terminal](../../artifacts/evidence/TI3_D_FINAL/terminal-state.json) | TI3_D_FINAL=PASS; FINAL_BALANCED_ACCURACY = 0.6666666666666666; FINAL_CONFUSION_MATRIX = [[2,1],[1,2]]; FINAL_TEST_SAMPLES = 6; ML_FINAL_TEST=CONSUMED |
| Limites do resultado Experiment 1 | Mesmo freeze TI3-D | Mesmo checkpoint TI3-D | [Relatório, interpretação](../../artifacts/evidence/TI3_D_FINAL/execution-report.md), [terminal](../../artifacts/evidence/TI3_D_FINAL/terminal-state.json) | FINAL_RESULT_SCOPE=SMALL_INTERNAL_TEMPORAL_CONFIRMATION; SCIENTIFIC_MODELING_COMPLETE=true; sem estimativa externa/causal |

## Study2-A e reconciliação semântica

| Conclusão | Freeze científico | Checkpoint documental | Evidência | Campo/métrica e estado |
| --- | --- | --- | --- | --- |
| Mineração temporal integral | `7d89329bf005f6a85ddc67d51d88b9e362878478` | `b8f6b4dba80af79812b93a5db391392b5eb1e69c` | [Terminal A](../../artifacts/evidence/STUDY2_A_ANNOTATION_MINING/terminal-state.json), [relatório A](../../artifacts/evidence/STUDY2_A_ANNOTATION_MINING/execution-report.md) | STUDY2_A=PASS; ANNOTATION_FRAMES_PROCESSED = 689; UNIQUE_AUTO_GOLD_SITES = 87; DIRECT_VALID_OBSERVATIONS = 7941; AUTO_SILVER_OBSERVATIONS = 5737 |
| Continuidade com o legado | Mesmo freeze A | Mesmo checkpoint A | [Terminal A](../../artifacts/evidence/STUDY2_A_ANNOTATION_MINING/terminal-state.json) | LEGACY_SITES_MAPPED = 52; CONFLICT_RECORDS = 0; HUMAN_REVIEW_USED=false; HOUGH_EXECUTED=false |
| Semântica dos agregados corrigida aditivamente | Mesmo freeze A, inalterado | `7c192478554ea139752feaaff8cb2d44ff6747f7` | [Reconciliação JSON](../../artifacts/evidence/STUDY2_A_ANNOTATION_MINING/METRIC_SEMANTICS_RECONCILIATION.json), [explicação Markdown](../../artifacts/evidence/STUDY2_A_ANNOTATION_MINING/METRIC_SEMANTICS_RECONCILIATION.md) | STUDY2_A_METRIC_RECONCILIATION=PASS; SCIENTIFIC_RESULT_IMPACT=NONE; sete nomes de canonical_metrics |
| Ocorrências gráficas não são eventos físicos | Mesmo freeze A | Reconciliação acima | [Reconciliação, unit/canonical_definitions/future_consumer_contract](../../artifacts/evidence/STUDY2_A_ANNOTATION_MINING/METRIC_SEMANTICS_RECONCILIATION.json) | AMBIGUOUS_COMPONENTS_TOTAL = 24246; UNRESOLVED_SITE_HYPOTHESIS_COMPONENTS = 18962; NON_VALID_COMPONENTS_TOTAL = 24538; nenhuma dessas contagens significa novos sites/eventos |

## Study2-B

| Conclusão | Freeze científico | Checkpoint textual | Evidência | Campo/métrica e estado |
| --- | --- | --- | --- | --- |
| Corpus longitudinal completamente contabilizado | `06ea5467d495a6a531a48a622a92b31e050e037a` | `cf5a4b091db52c0fc2f4b532230ed32ee013a2f9` | [Terminal B](../../artifacts/evidence/STUDY2_B_CORPUS/terminal-state.json), [results.json](../../artifacts/evidence/STUDY2_B_CORPUS/results.json) | STUDY2_B=PASS; SITE_FRAME_ACCOUNTED_RECORDS = 27396; VALID_MULTIMODAL_PAIRS = 16500; INVALID_MULTIMODAL_PAIRS = 10896 |
| Tiers e ausência de negativos fabricados | Mesmo freeze B | Mesmo checkpoint B | [results.json, valid_tier_counts/input_tier_counts](../../artifacts/evidence/STUDY2_B_CORPUS/results.json), [relatório B](../../artifacts/evidence/STUDY2_B_CORPUS/execution-report.md) | GOLD 5218; SILVER 3687; UNLABELED_PRE 5181; UNLABELED_PERSISTENCE 2414 válidos; sem promoção para background |
| Domínio de suporte e pool BG | Mesmo freeze B | Mesmo checkpoint B | [Terminal B](../../artifacts/evidence/STUDY2_B_CORPUS/terminal-state.json), [relatório B](../../artifacts/evidence/STUDY2_B_CORPUS/execution-report.md) | UNIQUE_SITES_WITH_VALID_PAIRS = 52; BACKGROUND_CANDIDATES = 70844; BACKGROUND_TRACKS = 223; ML_RUNS = 0 |
| Exclusões preservadas | Mesmo freeze B | Mesmo checkpoint B | [results.json, pair_status_counts/invalid_support_policy](../../artifacts/evidence/STUDY2_B_CORPUS/results.json) | INVALID_BOTH = 10896; sem substituição/shift/padding; os 35 sites sem suporte não são erros de modelo |

## Study2-C

| Conclusão | Freeze científico | Checkpoint textual | Evidência | Campo/métrica e estado |
| --- | --- | --- | --- | --- |
| Benchmark agrupado com cinco modelos | `8c38384915807a15062782a4a189601f7c83c8c3` | `c715df53d5dc08815235f010c07616deef7bbb4a` | [Relatório C](../../artifacts/evidence/STUDY2_C_BENCHMARK/execution-report.md), [RESULTS_SUMMARY.json](../../artifacts/evidence/STUDY2_C_BENCHMARK/RESULTS_SUMMARY.json) | STUDY2_C=PASS; counts: 80 fits CV, 5 comparações, 1 SILVER, 1 final; cinco modelos comparados conforme protocolo |
| Pipeline final selecionado | Mesmo freeze C | Mesmo checkpoint C | [Terminal C](../../artifacts/evidence/STUDY2_C_BENCHMARK/terminal-state.json), [síntese, selection/silver/pipeline](../../artifacts/evidence/STUDY2_C_BENCHMARK/RESULTS_SUMMARY.json) | SELECTED_MODEL_FAMILY=RF_REFERENCE; SELECTED_SUPERVISION_REGIME=GOLD_PLUS_SILVER |
| Resultado final TEST | Mesmo freeze C | Mesmo checkpoint C | [Síntese, test](../../artifacts/evidence/STUDY2_C_BENCHMARK/RESULTS_SUMMARY.json), [terminal](../../artifacts/evidence/STUDY2_C_BENCHMARK/terminal-state.json) | test.primary_gmba = 0.8449139278495638; test.observation.balanced_accuracy = 0.8525933757278337; confusão [[2172,323],[126,636]]; TEST_STATE=CONSUMED |
| Domínio interno e limites | Mesmo freeze C | Mesmo checkpoint C | [Relatório C, interpretação restrita](../../artifacts/evidence/STUDY2_C_BENCHMARK/execution-report.md) | INTERNAL_GROUP_HELD_OUT_TEST; 52 sites de suporte válido; TEST 20 grupos / 3257 observações; mesmas duas aquisições; sem generalização externa |

## Study2-D

| Conclusão | Freeze/registro de origem | Checkpoint textual | Evidência | Campo/métrica e estado |
| --- | --- | --- | --- | --- |
| Desenho de atribuição fixo | Original `21400de67d21901aeb8e5abac528689fc39169fa` | `5e6f2191cfb84b3b72892130782e2f406d5477fa` | [Protocolo D](../../artifacts/evidence/STUDY2_D_ATTRIBUTION/STUDY2_D_PROTOCOL.md), [budget](../../artifacts/evidence/STUDY2_D_ATTRIBUTION/STUDY2_D_FIT_BUDGET.json), [relatório D](../../artifacts/evidence/STUDY2_D_ATTRIBUTION/EXECUTION_REPORT.md) | POST_HOC_CONTROLLED_ATTRIBUTION_ANALYSIS; RF_REFERENCE/LBP20; TRAIN 10907 rows / 64 grupos / quatro folds; 100 fits |
| Falha CI original preservada e reparo compatível | Original acima → reparo `8c6221da3d03a498158d812be5c08848c37c2247` | Mesmo checkpoint D | [Bloqueio original](../../artifacts/evidence/STUDY2_D_ATTRIBUTION/CI_BLOCKED_REPORT.md), [reparo](../../artifacts/evidence/STUDY2_D_ATTRIBUTION/CI_REPAIR_REPORT.md), [verificação do reparo](../../artifacts/evidence/STUDY2_D_ATTRIBUTION/CI_REPAIR_VERIFICATION.json) | Nenhuma ciência antes da autorização/CI verde; reparo operacional, scientific_method_changed=false; histórico não convertido retroativamente em PASS |
| Diversidade: benefício pequeno e misto | Método original, admissão operacional pelo reparo | Mesmo checkpoint D | [GROUP_DIVERSITY_RESULTS.json](../../artifacts/evidence/STUDY2_D_ATTRIBUTION/GROUP_DIVERSITY_RESULTS.json), [ATTRIBUTION_SUMMARY.json](../../artifacts/evidence/STUDY2_D_ATTRIBUTION/ATTRIBUTION_SUMMARY.json) | contrasts.K24_MINUS_K17.global.mean_paired_delta = 0.0039043309111838507; 11/20 positivos; GROUP_DIVERSITY_DESCRIPTOR=MIXED_POSITIVE |
| Densidade temporal: média menor | Mesmo método/admissão | Mesmo checkpoint D | [TEMPORAL_DENSITY_RESULTS.json](../../artifacts/evidence/STUDY2_D_ATTRIBUTION/TEMPORAL_DENSITY_RESULTS.json) | D1 GMBA = 0.7786692086875789; DALL = 0.7189698985429366; contrasts.DALL_MINUS_D1.global.mean_paired_delta = −0.059699310144642304; quatro folds globais negativos; NON_POSITIVE |
| Ponderação agrupada: sem benefício nesse cenário | Mesmo método/admissão | Mesmo checkpoint D | [GROUP_WEIGHTING_RESULTS.json](../../artifacts/evidence/STUDY2_D_ATTRIBUTION/GROUP_WEIGHTING_RESULTS.json) | GROUP_EQUAL = 0.7189698985429366; OBSERVATION_EQUAL = 0.7335568007189566; contrast.global.mean_paired_delta = −0.014586902176019961; quatro folds globais negativos; NO_GROUP_EQUAL_BENEFIT |
| Firewall e execução única | Mesmo método/admissão | Mesmo checkpoint D | [Terminal D](../../artifacts/evidence/STUDY2_D_ATTRIBUTION/terminal-state.json), [verificação terminal](../../artifacts/evidence/STUDY2_D_ATTRIBUTION/VERIFICATION_TERMINAL.json) | STUDY2_D=PASS; SCIENTIFIC_STUDY2D_RUNS = 1; DISTINCT_RF_FITS = 100; DEV_ROWS_READ/TEST_ROWS_READ/TEST_CACHE_ROWS_READ/TEST_FEATURES_COMPUTED = 0; EXPERIMENTAL_SOURCE_OPENS/FFMPEG_RUNS = 0 |
| Nenhuma decomposição causal do ganho histórico | Mesmo método/admissão | Mesmo checkpoint D | [Relatório D, interpretação obrigatória](../../artifacts/evidence/STUDY2_D_ATTRIBUTION/EXECUTION_REPORT.md), [síntese D](../../artifacts/evidence/STUDY2_D_ATTRIBUTION/ATTRIBUTION_SUMMARY.json) | effects_are_additive=false; p_values_computed=false; MODEL_SELECTION_REOPENED=false; K17 é somente NUMERICAL_SCALE_BRIDGE |

## Integrações e estado do fechamento

As integrações anteriores estão registradas em [INTEGRATION_AUDIT B](../../artifacts/evidence/STUDY2_B_CORPUS/INTEGRATION_AUDIT.json), [INTEGRATION_AUDIT C](../../artifacts/evidence/STUDY2_C_BENCHMARK/INTEGRATION_AUDIT.json) e [INTEGRATION_AUDIT D](../../artifacts/evidence/STUDY2_D_ATTRIBUTION/INTEGRATION_AUDIT.json):

| Fase integrada | PR | Merge registrado |
| --- | ---: | --- |
| Study2-A | 16 | `d4ef00bf1e1d84d49d4e3f2dce0d18f683598a4c` |
| Study2-B | 17 | `de7670bb8491d2ef01809b33aa326aa3a264324c` |
| Study2-C | 18 | `ec97cb5041ef35d4f6c9a79b54d756d6fbee674f` |
| Study2-D | 19 | `5a158443fe00ace9b20f403f61f4a1aad21b285a` |

A integração de Study2-D e a base exata da branch documental são registradas em [PROVENANCE.json](../../artifacts/evidence/FINAL_CLOSEOUT/PROVENANCE.json). O [FINAL_STATE.json](../../artifacts/evidence/FINAL_CLOSEOUT/FINAL_STATE.json) explicita o encerramento científico; [CANONICAL_METRICS.json](../../artifacts/evidence/FINAL_CLOSEOUT/CANONICAL_METRICS.json) é a projeção documental dos resultados; [verification.json](../../artifacts/evidence/FINAL_CLOSEOUT/verification.json) delimita as verificações deste fechamento.

O SHA do próprio checkpoint documental e a CI posterior pertencem ao retorno efetivo após publicação, sem antecipação de sucesso remoto ou autorreferência. Este fechamento não cria nova ciência, avaliação, build acadêmico ou permissão para pesquisa futura.
