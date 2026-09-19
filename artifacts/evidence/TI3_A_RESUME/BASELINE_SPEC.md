# Baseline congelado pelo autor — implementação condicionada aos gates

Somente radiografia estrutural ESM1/ESM4. Scikit-image 0.24.0:
local_binary_pattern(P=8, R=1, method="uniform") sobre patch uint8 65×65.
numpy.histogram com 10 bins, range=(0,10), density=True: dez features.

Scikit-learn 1.5.2: RandomForestClassifier(n_estimators=100, random_state=42).
Demais defaults integrais constam de preflight-recovery/environment.json.
Sem class weighting, busca de hiperparâmetros, tuning ou modelo alternativo.
NumPy 1.26.4 e SciPy 1.11.4. Ambiente isolado .venv no repositório.

Métrica primária: balanced_accuracy. Secundárias: accuracy, precision, recall,
F1, confusion matrix e TP/FP/TN/FN. Mede concordância com supervisão fraca,
não recall físico exaustivo. Exatamente uma execução científica válida,
TRAIN e avaliação DEVELOPMENT; desempenho baixo é resultado válido.
FINAL_TEST nunca é avaliado nesta autorização.

Implementação e execução dependem do gate de viabilidade documental. Nenhum
fit experimental foi iniciado. Testes de dependências com matrizes geradas
em memória são técnicos e não contam como uma execução científica.
