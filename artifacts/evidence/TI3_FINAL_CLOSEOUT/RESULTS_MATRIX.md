# Matriz final de resultados históricos

Transcrição das evidências congeladas; nenhum modelo, métrica decisória nova,
feature ou avaliação foi executado para produzir esta síntese.

| Fase | Modelo | Partição | Balanced accuracy |
| --- | --- | --- | ---: |
| TI3-A | STRUCTURAL_LBP_RF | DEVELOPMENT (16) | 0.6875 |
| TI3-B | MULTIMODAL_LBP_RF | DEVELOPMENT (16) | 0.75 |
| TI3-C | MINIMAL_MULTIMODAL_CNN | DEVELOPMENT (16) | 0.50 |
| TI3-D | MULTIMODAL_LBP_RF | FINAL (6) | 0.6666666666666666 |

A/B/C usam DEVELOPMENT para as decisões autorizadas, sob regras congeladas.
TI3-D usa FINAL após a seleção, com um fit nos 50 TRAIN+DEVELOPMENT.
Os endpoints são diferentes; FINAL não reabre a comparação de famílias ou
modalidades. A superioridade de B em DEV é descritiva, sem prova de benefício
solutal populacional ou causal. O resultado de C não demonstra impossibilidade
de CNNs. O desempenho de ressubstituição não estima generalização.

## FINAL consumido

Linhas = true weak label; colunas = predição; ordem de classes [0,1].

```text
[[2,1],
 [1,2]]
```

TN=2; FP=1; FN=1; TP=2. Quatro acertos em seis classificações de weak labels.

| Métrica FINAL | Valor registrado |
| --- | ---: |
| Balanced accuracy | 0.6666666666666666 |
| Accuracy | 0.6666666666666666 |
| Precision | 0.6666666666666666 |
| Recall | 0.6666666666666666 |
| F1 | 0.6666666666666666 |

As cinco métricas são as já registradas em TI3-D. Não são estimativas
populacionais precisas, e recall não significa inventário físico exaustivo.
Não foi usado um mínimo de desempenho para declarar PASS da execução.

Proveniência: [TI3-A](../TI3_A_RESUME/c0r1-resume/execution-report.md),
[TI3-B](../TI3_B_SOLUTAL/execution-report.md),
[TI3-C](../TI3_C_CNN/execution-report.md),
[TI3-D](../TI3_D_FINAL/execution-report.md),
[predições congeladas](../TI3_D_FINAL/predictions.json) e
[resultados TI3-D](../TI3_D_FINAL/results.json).
