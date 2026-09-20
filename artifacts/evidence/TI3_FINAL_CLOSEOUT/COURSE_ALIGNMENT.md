# Síntese do alinhamento curricular

A relação A4/A5 retoma o conteúdo descrito pelo autor e os registros anteriores.
Não foram acessados notebooks do curso nem executadas demonstrações novas nesta
integração. A pertinência de cada técnica dependeu da tarefa e de seus limites.

| Tema | Uso documentado no estudo | Limite da interpretação |
| --- | --- | --- |
| A4 — LBP e classificação Random Forest | TI3-A estrutural; TI3-B multimodal; TI3-D ajuste e avaliação final do modelo selecionado | Descritor de textura e classificação de weak labels; sem inferência física causal |
| A5 — CNN | TI3-C: Conv2d(2,8,3) → ReLU → MaxPool → AdaptiveAvgPool → Flatten → Linear(8,2), 170 parâmetros, dez épocas, DEV BA=0.50 | Comparação única; desempenho não motivou tuning e não refuta CNNs em geral |
| A5 — thresholding e análise binária | A0: limiar de chroma, componentes conexos e descrição geométrica das marcações publicadas | Extração do gráfico de annotation; círculo não é máscara física do fragmento |
| Ajuste algébrico de círculo | Centro operacional do traço gráfico usado na weak supervision posterior | Não mede forma, tamanho ou onset de fragmentação |
| A5 — Sobel/gradientes e NGF | Relação conceitual e histórico do registro multimodal G2 preservados | Nenhum kernel G2 reexecutado neste encerramento |
| A4 — descritores locais e SS8 | Auto-similaridade no histórico G2 | SS8 não é declarado implementação exata de MIND/MIND-SSC |
| SIFT, ORB/FAST/BRIEF | Não usados no baseline | Nenhum benchmark retrospectivo ou obrigação de incluir todas as técnicas |
| Canny e Hough | Canny não foi input do modelo; Hough não foi executado | Sem tuning retrospectivo do extrator ou das labels |
| Avaliação e seleção | DEV para escolhas congeladas; FINAL uma única vez após a seleção | Separação não produz aquisições independentes nem remove exposição histórica |

LBP usou P=8, R=1, método uniform e dez bins por modalidade. O pipeline final
concatena dez componentes estruturais e dez solutais relativos; RF tem
100 árvores e seed42. Esses parâmetros são apenas relatados, sem nova execução.
CNN não foi a família selecionada para FINAL. Não houve augmentation ou
ajuste retrospectivo de threshold a partir do teste final.

Fontes: [alinhamento A0](../TI3_A0/COURSE_ALIGNMENT_LABEL_EXTRACTION.md),
[resolução do target](../TI3_TARGET_RESOLUTION/COURSE_ALIGNMENT.md),
[planejamento TI3-A](../TI3_A_RESUME/COURSE_ALIGNMENT.md),
[TI3-A executado](../TI3_A_RESUME/c0r1-resume/execution-report.md),
[TI3-B](../TI3_B_SOLUTAL/execution-report.md),
[TI3-C](../TI3_C_CNN/execution-report.md) e
[TI3-D](../TI3_D_FINAL/execution-report.md).

Estados prospectivos dos documentos antigos conservam seu contexto histórico.
Esta síntese registra o uso posterior efetivo; não altera aqueles documentos
nem autoriza um novo exercício, notebook, treinamento ou avaliação.
