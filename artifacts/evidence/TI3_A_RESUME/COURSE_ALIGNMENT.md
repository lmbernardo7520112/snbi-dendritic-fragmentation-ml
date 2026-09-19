# Alinhamento curricular e estado de uso

A4: LBP e Random Forest são as técnicas autorizadas para a baseline. Até superar
o gate geométrico foram usados somente no smoke sintético de dependências;
uso científico permanece condicionado a C1, CI e acesso TRAIN/DEV autorizado.
SIFT: NOT_USED_IN_BASELINE, complexidade adicional não justificada neste escopo.
ORB/FAST/BRIEF: NOT_USED_IN_BASELINE.

A5: CNN DEFERRED_TO_TI3_B, sem autorização nesta tarefa. Sobel já foi utilizado
conceitualmente em NGF histórico; nenhum kernel G2 foi reexecutado.
Canny: NOT_USED_AS_MODEL_INPUT. Thresholding/components já utilizados na
extração histórica de weak labels A0, preservada. Hough:
DELIBERATELY_NOT_USED, sem tuning retrospectivo.
