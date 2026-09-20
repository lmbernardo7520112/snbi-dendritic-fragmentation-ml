# Pipeline final selecionado

Modelo: MULTIMODAL_LBP_RF; modalidade STRUCTURAL_PLUS_RELATIVE_SOLUTE. Y nativa uint8, patches 65×65 nos centros e IDs congelados. ESM1/4 estruturais; ESM2/5 exclusivamente RELATIVE_SOLUTE_FIELD, nunca concentração absoluta.

Para cada modalidade, o kernel LBP histórico usa P=8, R=1, method=uniform; histograma de dez bins, range=(0,10), density=True. Concatenação exata [STRUCTURAL_LBP_10, SOLUTAL_LBP_10], 20 features. Os 50 hashes de patches por modalidade e features devem coincidir com TI3-B antes do fit. Nenhum ajuste de centro, máscara, intensidade, feature ou representação.

RandomForestClassifier(n_estimators=100, random_state=42), sklearn 1.5.2; todos os demais parâmetros são iguais ao dicionário RF_PARAMETERS histórico, também incluído integralmente em configs/ti3/final-evaluation.json. NumPy1.26.4, SciPy1.11.4, scikit-image0.24.0 preservados. Predictions usam model.predict(); probabilidades model.predict_proba(); classes [0,1]. Não há threshold adicional, weights, seed alternativa, CNN ou modelo estrutural separado.

O hash lógico do fit autentica configuração, IDs e conteúdo aprendido em memória antes de FINAL. Nenhum pickle/joblib, modelo binário ou vetor de features é exportado. A especificação exata de digest está no código D1; o arquivo durável guarda somente hashes/configuração/resumos, não arrays de árvores.
