# Alinhamento curricular da resolução

| Técnica | Decisão nesta etapa |
| --- | --- |
| Thresholding + componentes conexos | Uso real anterior em A0 para extrair marcações gráficas; extrator e resultados preservados |
| Ajuste geométrico do círculo | Centro operacional da weak label, não geometria do fragmento |
| Hough | NÃO EXECUTADO; rejeitado para evitar tuning retrospectivo do extrator |
| LBP + Random Forest | Candidato apropriado a baseline clássico futuro se target PASS e unidade patch mantida; não treinado nem selecionado aqui |
| CNN | Candidato futuro se target PASS; nenhuma arquitetura escolhida ou executada |
| Sobel / gx / gy → NGF | Conexão didática preservada do registro multimodal; nenhum G2 reaberto |
| Descritores locais → self-similarity → SS8 | Conexão didática preservada, sem novo benchmark ou execução |

SS8 pode ser descrito como local self-similarity descriptor inspired by the
modality-independent self-similarity principle. Não se declara implementação
exata de MIND/MIND-SSC.

Extrair weak labels gráficas não obriga o futuro modelo a receber círculos,
Canny, Hough ou overlays. Os inputs futuros são imagens limpas.
MODEL_SELECTION=NOT_STARTED. ML_RUNS=0.
