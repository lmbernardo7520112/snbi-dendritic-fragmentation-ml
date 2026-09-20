# Métricas e avaliação prediction-first

PREDICTION_FIRST_FINAL_EVALUATION: inferência recebe seis IDs/vetores e não recebe true labels. Produz somente sample_id, predicted_label, probability_class_0, probability_class_1. Esse registro textual é gravado exclusivamente, fsync e autenticado por hash antes de associar true weak labels e chamar scoring. Não se alega cegamento humano: metadados/IDs históricos podem revelar classe.

Primária: balanced_accuracy. Secundárias: accuracy, precision, recall, F1, matriz de confusão, TN/FP/FN/TP. Classes [0,1]; linhas verdadeiras, colunas preditas; positiva1. Sem predição positiva, precision/F1 usam zero_division=0, convenção histórica. Nenhuma ROC-AUC/PR-AUC, p-value, bootstrap de seleção ou threshold search.

FINAL tem seis decisões, três positivos e três backgrounds. Um erro em uma classe altera sua sensitivity/specificity em 1/3 = 33,333… pontos percentuais. Um erro altera accuracy e balanced accuracy em 1/6 = 16,666… pontos percentuais neste desenho balanceado. Isso não é estimativa populacional precisa. Probabilidades/predições/métricas integrais são preservadas; arredondamento só na apresentação.

Não há piso de BA para PASS. Métricas TRAIN+DEV são ressubstituição descritiva e não influenciam nada. Referências DEV permanecem históricas. A seleção MULTIMODAL_LBP_RF permanece encerrada qualquer que seja o resultado FINAL.
