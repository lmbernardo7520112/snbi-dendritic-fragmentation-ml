# Study3 — escopo das conclusões

```text
STUDY3_KIND=INTERNAL_EXPLORATORY_TEMPORAL_REPRESENTATION_STUDY
PRIMARY_UNIT=GROUP_TRAJECTORY
EXTERNAL_GENERALIZATION=false
CONFIRMATORY_EXTERNAL_CLAIM=false
STUDY2_C_DEV_ACCESS=false
STUDY2_C_TEST_ACCESS=false
MODEL_SEARCH_AFTER_RESULTS=false
```

Esta fase recupera e prepara o freeze; não fornece resultado científico
Study3. A linguagem abaixo delimita resultados de eventual execução futura
expressamente autorizada. Testes sintéticos, uma arquitetura implementada ou
CI verde não são evidência de discriminação experimental.

| Formulação admitida | Limite obrigatório |
| --- | --- |
| Comparação interna, exploratória, agrupada, de representações temporais. | São os 64 grupos TRAIN históricos das mesmas duas aquisições, sem confirmação externa nova. |
| Discriminação descritiva frente a weak labels publicadas. | GOLD não é ground truth físico independente; background continua candidato. |
| Uma predição por trajetória, GMBA primária e deltas pareados entre quatro folds. | Trajetórias e folds não são aquisições independentes; não calcular p-values ou alegar significância universal. |
| CNN1D aprende representação temporal sobre LBP; CNN espacial-temporal aprende espaço e sequência. | Padrão aprendido não identifica dinâmica física, causalidade ou mecanismo de fragmentação. |
| Controles sugerem possível confusão por aquisição/cobertura. | Diagnósticos não estimam efeito causal e não autorizam adaptar população, folds ou modelos. |
| Resultado não positivo/colapso de modelo preservado sob protocolo fixo. | Não concluir que a família de modelos é universalmente impossível ou inferior. |

São proibidos: external validation, fresh confirmation, generalização externa,
causalidade física, onset exato, forecasting, recall físico exaustivo,
concentração absoluta de Bi, temperatura inferida, novas réplicas experimentais
e substituição do pipeline final Study2-C RF_REFERENCE+GOLD_PLUS_SILVER.

FCO é primeira observação confiante da marcação, não início físico da ruptura.
Site não é evento; track background não é ausência certificada. Classes
preditas são comparadas às labels gráficas. O campo solutal é relativo.

Study2-D perguntou se adicionar mais rows correlacionadas ajuda RF. Study3
pergunta se representar a trajetória explicitamente ajuda a discriminação
interna. D validava todas as rows dos grupos retidos; Study3 prediz uma classe
por grupo. Não tratar seus valores D1 como estimativas diretamente idênticas,
nem somar deltas para decompor causalmente Experiment 1→Study2-C.

Pré-registro do desenho não implica virgindade dos dados: histórico TRAIN já
foi usado, DEV/TEST históricos estão expostos/consumidos nos respectivos
papéis, e houve exposição operacional explícita a metadados TRAIN antes desta
recuperação. A autorização aceita
TEXTUAL_TRAIN_METADATA_EXPOSURE_ONLY; não permite chamá-la de zero metadata
access. O método foi especificado antes dessa exposição e não é adaptado por
ela. Não ocorreu leitura de pixels/features/fits naquele incidente.

PASS da recuperação significa gates operacionais satisfeitos, quando isso for
efetivamente verificado. PASS científico futuro exige 28/28 fits contratuais,
zero retry/adaptação/DEV/TEST/video e evidências preservadas; independe de
melhoria de score. Nenhum desses PASS certifica verdade física, nota acadêmica
ou avaliação humana independente.
