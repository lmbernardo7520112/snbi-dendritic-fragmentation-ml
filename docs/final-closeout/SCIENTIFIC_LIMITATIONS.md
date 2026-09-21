# Limites científicos do programa encerrado

O resultado final descreve classificação de localizações gráficas publicadas em duas aquisições de solidificação Sn–Bi. O [Experimento 1](../../artifacts/evidence/TI3_D_FINAL/execution-report.md), o [benchmark Study2-C](../../artifacts/evidence/STUDY2_C_BENCHMARK/execution-report.md) e a [atribuição Study2-D](../../artifacts/evidence/STUDY2_D_ATTRIBUTION/EXECUTION_REPORT.md) têm desenhos distintos; suas métricas não constituem uma estimativa causal comum. Este documento transcreve limites já registrados, sem nova análise ou recálculo.

## Unidades experimentais e domínio de validade

Há somente duas aquisições, bottom_up_anti_parallel e top_down_parallel. Milhares de rows temporais, dezenas de sites e tracks e quatro folds não são milhares de experimentos independentes. Separar grupos evita compartilhar a identidade do site/track entre treino e avaliação; não elimina a correlação temporal dentro de trajetórias nem o contexto espacial comum entre grupos próximos. Não houve validação em aquisições externas, novas composições ou condições independentes.

O domínio do benchmark contém os 52 sites com suporte válido entre 87 identidades AUTO_GOLD. Os 35 excluídos por suporte permanecem contabilizados e não são erros do modelo. O corpus B registra 16.500 pares válidos em 27.396 entradas. A cobertura observada não autoriza extrapolação aos sites sem suporte. No TEST C, o estrato top_down tem apenas dois sites e dois tracks; resultados por aquisição têm base limitada. [Corpus e qualidade](../../artifacts/evidence/STUDY2_B_CORPUS/QUALITY_REPORT.md), [TEST C](../../artifacts/evidence/STUDY2_C_BENCHMARK/TEST_METRICS.json).

## O que os labels significam

O target é PUBLISHED_FRAGMENTATION_LOCATION_PRESENT. GOLD e SILVER são graus automáticos de evidência gráfica publicada, sem confirmação física humana. Círculos não são máscaras de fragmentos. BACKGROUND_CANDIDATE não prova ausência de fragmentação física. Um falso positivo ou negativo é uma divergência frente à weak label, sem estabelecer um evento físico falso ou perdido. A extração não fornece inventário físico exaustivo, onset exato ou recall de todos os eventos.

Os componentes AMBIGUOUS/SMALL repetidos entre frames são ocorrências gráficas. Os totais reconciliados 18.670, 18.962 e 24.538 não medem novos eventos ou identidades de sites. [Contrato do target](../../artifacts/evidence/TI3_TARGET_RESOLUTION/execution-report.md), [reconciliação A](../../artifacts/evidence/STUDY2_A_ANNOTATION_MINING/METRIC_SEMANTICS_RECONCILIATION.md).

## Modalidades, geometria e exposição histórica

ESM2/5 representam campo solutal relativo, sem estimativa de concentração absoluta de Bi ou temperatura. A correspondência de raster e a discriminação multimodal não certificam metrologia física completa, orientação física ou incerteza de coordenadas. FPS de reprodução não equivale ao tempo físico do experimento. A seleção de uma representação multimodal não demonstra mecanismo físico causal.

A exposição histórica a fontes e metadados permanece declarada. O programa não reivindica virgindade global de holdouts ou cegamento humano. Em C, a reserva por grupos para TEST foi lógica para tensors/features/modelagem; o streaming de frames compartilhados não isolava fisicamente todos os pixels TEST. O registro FINAL_FIT_FREEZE C prova conclusão/configuração durável, sem constituir hash lógico do modelo aprendido. Os limites dos registros de I/O e sua ausência de monitoramento universal de syscalls permanecem os do [relatório C](../../artifacts/evidence/STUDY2_C_BENCHMARK/execution-report.md).

## Comparabilidade e atribuição pós-hoc

O FINAL do Experimento 1 tem seis samples, três por classe, e balanced accuracy 0,6666666666666666. O TEST C tem 3.257 observações em 20 grupos e GMBA 0,8449139278495638. Tamanho, unidade de avaliação, split, composição, supervisão, pesos e métrica primária mudaram. Não se pode atribuir sua diferença numérica exclusivamente ao corpus, à multimodalidade ou à arquitetura. K=17 grupos por classe em D é apenas NUMERICAL_SCALE_BRIDGE para os 17 samples por classe no TRAIN original.

Study2-D é POST_HOC_CONTROLLED_ATTRIBUTION_ANALYSIS, restrito ao TRAIN histórico, com modelo, features e folds fixos. Folds e replicates compartilham dados e não são experimentos independentes. Em A, aumentar grupos mantendo uma observação por grupo também aumenta o número de exemplos; não é diversidade isolada a tamanho amostral constante. Em C, a ponderação muda a massa por grupo e pode mudar a massa por classe. Os efeitos são condicionais a esses pontos do desenho e podem interagir. Não há desenho fatorial que permita decomposição percentual aditiva ou teste de significância universal.

K24−K17 apresentou benefício pequeno e misto: +0.0039043309111838507, com 11/20 contrastes positivos. DALL−D1 foi −0.059699310144642304 e GROUP_EQUAL−OBSERVATION_EQUAL foi −0.014586902176019961, ambos negativos nos quatro folds globais. Essa consistência global não implica o mesmo padrão em todos os estratos por aquisição. A curva de diversidade não foi monotônica e os resultados não estabelecem saturação temporal. [Resultados e interpretação D](../../artifacts/evidence/STUDY2_D_ATTRIBUTION/EXECUTION_REPORT.md).

Esses resultados não significam que mais frames sejam fisicamente prejudiciais ou que a ponderação por grupo nunca funcione. Study2-D não identificou um único fator positivo suficiente para explicar a diferença histórica Experimento 1 → Study2-C. A diferença permanece compatível com combinação/interação de mudanças data-centric e metodológicas. O pipeline final C permanece RF_REFERENCE + GOLD_PLUS_SILVER; seus pesos, sua seleção e seu TEST consumido não são alterados retrospectivamente.

## Fronteira das conclusões e do encerramento

O programa não sustenta causalidade física, forecasting, onset exato, generalização externa, recall físico exaustivo ou significância estatística universal. PASS significa cumprimento do protocolo e preserva os resultados negativos. As auditorias assistidas por IA e o Git fornecem verificações delimitadas, sem certificação humana ou institucional.

As etapas científicas estão encerradas. Os terminais e históricos permanecem intactos; a [síntese final de estado](../../artifacts/evidence/FINAL_CLOSEOUT/FINAL_STATE.json) não reativa autorizações anteriores. O [roadmap](FUTURE_RESEARCH_ROADMAP.md) descreve possibilidades futuras, todas dependentes de decisão própria.
