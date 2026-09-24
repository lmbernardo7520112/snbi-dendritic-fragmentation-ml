# Study3-CNN — protocolo mestre pré-registrado

## Autoridade e estado

O desenho provém do prompt autoral Study3-CNN anterior à exposição operacional
a metadados TRAIN. A autorização posterior de recuperação termina em
**PRE_SCIENCE_FREEZE_AND_CI**. Implementação, documentação, fixtures sintéticos,
revisão, um freeze commit, push fast-forward e verificação de CI são o escopo
atual. Não há autoridade atual para receipt científico, acesso a pixels/caches,
extração real de LBP, fit experimental ou execução de `scripts/run_study3.py`.
Mesmo CI verde exige STOP e nova decisão do autor antes de ciência.

Este documento fixa o método a implementar; não relata resultados, freeze já
criado ou CI já aprovada. O [incidente](STUDY3_PRE_SCIENCE_INCIDENT.md) e a
[declaração pré-exposição](STUDY3_PREEXPOSURE_DESIGN_DECLARATION.md) integram sua
proveniência. Nenhuma leitura de metadados autoriza adaptação do desenho.

## Questão científica exata

Can explicit group-level temporal representations,
including convolutionally learned temporal and
spatiotemporal representations, provide descriptive
internal discrimination beyond a single representative
observation within historical Study2-C TRAIN groups?

Em português: representar explicitamente a trajetória temporal de cada
site/track, inclusive por CNN temporal e espaço-temporal, fornece sinal
discriminativo interno além de uma única observação representativa?

Study2-D investigou mais rows correlacionadas sob RF/LBP fixo; Study3 investiga
representação explícita da trajetória. O resultado negativo de densidade D
permanece preservado. O valor de D1 de Study3 não precisa reproduzir a métrica
histórica D1 de D: D validava todas as rows dos grupos retidos, enquanto Study3
produz uma predição por grupo usando a representação correspondente.

## População, unidade e folds

```text
STUDY3_KIND=INTERNAL_EXPLORATORY_TEMPORAL_REPRESENTATION_STUDY
STUDY3_POPULATION=HISTORICAL_STUDY2C_TRAIN_ONLY
PRIMARY_UNIT=GROUP_TRAJECTORY
ROWS=10907
GOLD_ROWS=3858
BACKGROUND_ROWS=7049
POSITIVE_GROUPS=32
BACKGROUND_GROUPS=32
TOTAL_GROUPS=64
FOLDS=4
```

Preservar os quatro folds C/D, sem resplit, substituição ou grupo novo. O hash
histórico do mapa group→fold é
`85edac3d7da06994d7b16c4fa50e2aeb806abd7743a1d471842f54fdcf049ef2`.
São somente duas aquisições, `bottom_up_anti_parallel` e `top_down_parallel`.
Excluir SILVER, UNLABELED_PRE, UNLABELED_PERSISTENCE, DEVELOPMENT, TEST,
reserve tracks e sites inválidos. Um grupo pertence a uma aquisição e uma
classe; em cada fold ocupa TRAIN xor VALIDATION. VALIDATION designa o lado
retido do TRAIN histórico, nunca o DEVELOPMENT histórico C.

Entidades e contratos estão em [STUDY3_SPECIFICATIONS.md](STUDY3_SPECIFICATIONS.md)
e [STUDY3_DATA_CONTRACT.md](STUDY3_DATA_CONTRACT.md). Site não é evento físico;
track background não é ausência física; trajetória não é experimento
independente. GOLD e BACKGROUND são weak labels históricas.

## Features históricas e representação A

Patches uint8 2×65×65, com canal 0 STRUCTURAL_Y e canal 1
RELATIVE_SOLUTE_FIELD_Y. LBP por canal: P=8, R=1, `method="uniform"`, histograma
de 10 bins, range=(0,10), `density=True`. Concatenar estrutural seguido de
solutal: 20 features. Em eventual execução autorizada, extrair LBP20 uma única
vez por row autorizada e reutilizar os vetores em todas as representações.

Ordenar cada grupo por `(frame_index, sample_id)`. Cada representação fornece
um vetor por grupo, tanto no lado de treino como no lado de validação.

| ID | Nome fixo | Construção | Dimensão |
| --- | --- | --- | ---: |
| A0 | D1_LBP20 | Row no rank inteiro `floor((n-1)/2)`; mediana temporal inferior, não mediana das features. | 20 |
| A1 | TRAJECTORY_MEAN_LBP20 | Média por dimensão de todas as rows do grupo. | 20 |
| A2 | TRAJECTORY_MEDIAN_LBP20 | Mediana por dimensão de todas as rows; mediana numérica convencional. | 20 |
| A3 | TRAJECTORY_Q2575_LBP60 | `np.quantile(values, [0.25,0.50,0.75], axis=0, method="linear")`; concatenar q25[20], q50[20], q75[20]. | 60 |

`PRIMARY_CLASSICAL_TEMPORAL_REPRESENTATION=A2`. Todas usam RF_REFERENCE sem
busca, um exemplo por grupo e contribuição uniforme dos grupos. Os 19
parâmetros são os históricos:

```json
{
  "bootstrap": true,
  "ccp_alpha": 0.0,
  "class_weight": null,
  "criterion": "gini",
  "max_depth": null,
  "max_features": "sqrt",
  "max_leaf_nodes": null,
  "max_samples": null,
  "min_impurity_decrease": 0.0,
  "min_samples_leaf": 1,
  "min_samples_split": 2,
  "min_weight_fraction_leaf": 0.0,
  "monotonic_cst": null,
  "n_estimators": 100,
  "n_jobs": null,
  "oob_score": false,
  "random_state": 42,
  "verbose": 0,
  "warm_start": false
}
```

Fonte: [MODEL_CONTRACT D](../../artifacts/evidence/STUDY2_D_ATTRIBUTION/MODEL_CONTRACT.json).
Não usar RF_TUNED ou scaler aprendido nas representações RF. Budget A: quatro
representações × quatro folds = 16 fits.

## Seleção temporal comum às CNNs

Para cada grupo ordenado, usar q=[0,1/7,2/7,3/7,4/7,5/7,6/7,1]. O alvo é
`q*(n-1)` e a seleção é o rank inteiro mais próximo; empate escolhe o inferior.
Usar aritmética racional/inteira para preservar essa regra. Selecionar a row
real existente. Quando n<8, repetir deterministicamente; manter oito posições,
sem interpolar pixels, sintetizar frames ou remover repetições.

Em eventual execução, persistir group_id, selected_sample_ids,
selected_frame_indices, rank_targets e duplicate_flags. A seleção é congelada
antes dos fits e é a mesma nas duas CNNs. As oito posições representam ranks
relativos da trajetória; não pretendem ser intervalos iguais de tempo físico.

## B — TEMPORAL_CNN1D_LBP20

Input B×20×8, correspondente ao LBP20 das oito rows selecionadas.

```text
Conv1d(20,32,kernel_size=3,padding=1)
ReLU
Conv1d(32,32,kernel_size=3,padding=1)
ReLU
AdaptiveAvgPool1d(1)
Flatten
Linear(32,2)
```

Com bias convencional habilitado: 1.952 + 3.104 + 66 = **5.122 parâmetros**.
Uma instância nova por fold; seed=42; CPU; `torch.set_num_threads(1)`;
30 epochs; batch_size=8 grupos; Adam lr=0.001, weight_decay=0;
CrossEntropyLoss; shuffle somente do lado TRAIN. Não usar BatchNorm, Dropout,
scheduler, early stopping, augmentation, outra seed ou seleção de época.

Normalização por feature: mean/std calculados somente nos grupos TRAIN daquele
fold, sobre grupos×8 timepoints. Repetições selecionadas continuam posições
do input. Usar desvio padrão populacional; std=0→1. Persistir mean, std e hash
do scaler em eventual execução. Validation não participa do cálculo.
Budget: quatro folds = quatro fits.

## C — SPATIOTEMPORAL_CNN_SMALL

Input B×8×2×65×65, canal 0 estrutural e canal 1 campo solutal relativo.
Converter uint8→float32/255.0; nenhuma estatística aprendida na validação.
O mesmo encoder espacial, com os mesmos pesos, processa todos os timepoints:

```text
Conv2d(2,8,kernel_size=3,padding=1)
ReLU
MaxPool2d(2)
Conv2d(8,16,kernel_size=3,padding=1)
ReLU
AdaptiveAvgPool2d((1,1))
Flatten
```

Cada timepoint fornece embedding de 16 dimensões. A sequência B×8×16 é transposta para
B×16×8 antes do head temporal:

```text
Conv1d(16,16,kernel_size=3,padding=1)
ReLU
AdaptiveAvgPool1d(1)
Flatten
Linear(16,2)
```

Com bias habilitado: 152 + 1.168 + 784 + 34 = **2.138 parâmetros**.
Uma instância nova por fold; seed=42; CPU; um thread torch; 30 epochs;
batch_size=4 grupos; Adam lr=0.001, weight_decay=0; CrossEntropyLoss;
shuffle somente TRAIN. Proibidos Conv3d, GRU, LSTM, Transformer, attention,
BatchNorm, Dropout, augmentation, scheduler, early stopping ou nova seed.
Budget: quatro folds = quatro fits.

## D — controles de confundimento

**ACQUISITION_ONLY**, zero fits: para cada aquisição, calcular classe
majoritária nos grupos TRAIN do fold; empate→classe 0. Aplicar a regra aos
grupos de validação. Apenas diagnóstico.

**COVERAGE_METADATA_LOGREG**, quatro fits: vetor por grupo, nesta ordem:
`log1p(n_rows)`, primeiro frame normalizado, último frame normalizado e span
temporal normalizado. Normalizar frame e diferença último−primeiro por 293
em bottom_up e 394 em top_down. Não incluir aquisição one-hot, coordenadas,
IDs, pixels ou LBP. StandardScaler somente TRAIN do fold; LogisticRegression
C=1, penalty=l2, solver=lbfgs, max_iter=10000. Não criar calibração ou tuning.

Desempenho dos controles informa possível confusão; não é teste de
significância e não identifica causalmente aquisição ou cobertura. Nenhum
diagnóstico autoriza rebalancear, excluir grupos, mudar folds ou retreinar.

## Métricas e contrastes

Uma predição por grupo. Primária: GROUP_MACRO_BALANCED_ACCURACY (GMBA),
numericamente balanced accuracy dessas unidades. Secundárias: accuracy,
precision, recall, specificity, F1 e matriz de confusão, classes[0,1], linhas
verdadeiras e colunas preditas. Reportar diagnósticos por aquisição. Somente
GMBA governa a interpretação primária; não calcular p-values.

| Contraste | Estatuto |
| --- | --- |
| TRAJECTORY_MEDIAN_LBP20 − D1_LBP20 | Primário clássico: MEDIAN_MINUS_D1 |
| TEMPORAL_CNN1D_LBP20 − D1_LBP20 | CNN1D_MINUS_D1 |
| SPATIOTEMPORAL_CNN_SMALL − D1_LBP20 | SPATIOTEMPORAL_MINUS_D1 |
| SPATIOTEMPORAL_CNN_SMALL − TRAJECTORY_MEDIAN_LBP20 | SPATIOTEMPORAL_MINUS_MEDIAN |
| SPATIOTEMPORAL_CNN_SMALL − TEMPORAL_CNN1D_LBP20 | SPATIOTEMPORAL_MINUS_CNN1D |
| TRAJECTORY_MEAN_LBP20 − D1_LBP20 | Secundário: MEAN_MINUS_D1 |
| TRAJECTORY_Q2575_LBP60 − D1_LBP20 | Secundário: Q2575_MINUS_D1 |

Cada contraste reporta os quatro deltas pareados de fold, mean, median,
std populacional (ddof=0), min, max e contagens positiva/zero/negativa. Zero é
comparação numérica exata. Essas convenções descritivas seguem Study2-D.

```text
mean_delta > 0 e positive_fold_count >= 3:
    CONSISTENT_POSITIVE_INTERNAL
mean_delta > 0:
    MIXED_POSITIVE_INTERNAL
caso contrário:
    NON_POSITIVE_INTERNAL
```

Os descritores não são testes de significância.

## Budget, ordem e irrevogabilidade

```text
RF_FITS=16
CNN1D_FITS=4
SPATIOTEMPORAL_CNN_FITS=4
METADATA_LOGREG_FITS=4
TOTAL_DISTINCT_FITS=28
ACQUISITION_ONLY_FITS=0
FIT_29_ALLOWED=false
```

Em uma futura execução expressamente autorizada, a ordem única será:
autenticar TRAIN; ler apenas offsets autorizados; extrair LBP20 uma vez por
row; construir trajetórias; congelar seleção T=8; A0–A3; CNN1D; CNN espacial+
temporal; controle metadata; acquisition-only; persistir resultados; terminal.
Não pausar entre etapas para adaptar a seguinte ao resultado anterior.

Antes do primeiro binário, eventual receipt O_EXCL+fsync vinculará freeze SHA,
HEAD, branch, hashes de população/folds/contratos, budget e timestamp. A
existência do receipt consome a tentativa; código, configs, protocolo,
representações e métricas tornam-se imutáveis. Esse receipt e a execução
**não são autorizados nesta recuperação**; sua lógica é testada somente com
fixtures sintéticos e grants falsos.

Não adicionar famílias, seeds, épocas, learning rates, larguras, augmentation,
RF_TUNED, SVM, PCA, feature selection, XGBoost ou CatBoost após resultados.
Não criar Study3-v2, Study3-E, retry ou CNN-tuned. Resultado desfavorável deve
ser preservado. [Extensões](FUTURE_STUDY3_EXTENSIONS.md) são NOT_CURRENT_WORK.

## Gates de congelamento desta fase

Completar council, protocolo, especificações, contratos, código, testes e
workflow. Verificação somente sintética, com zero skips no perfil Study3,
guards e regressões históricas pertinentes. Revisar diff inteiro, parâmetros,
isolamento, receipt ordering e hash do HANDOFF. Falha não vira PASS por
documentação; conflito operacional exige resolução explícita no escopo permitido.

Somente com todos os gates aprovados: um commit
`feat(study3): freeze convolutional temporal representation study`, sem
receipt, outputs ou resultados científicos; push fast-forward; CI em SHA
exato, todos os workflows aplicáveis SUCCESS e Study3 zero skips. Falha remota
exige STOP e proposta limitada, sem reparo automático. CI verde encerra esta
fase: `CURRENT_AUTHORIZED_ACTIVITY=NONE_AWAITING_AUTHOR_DECISION`.

Os claims seguem [STUDY3_CLAIM_SCOPE.md](STUDY3_CLAIM_SCOPE.md). PASS futuro
significa 28/28 fits contratuais, zero retry/DEV/TEST/video/adaptação, contratos
e resultados preservados; não exige score maior nem CNN vencedora.
