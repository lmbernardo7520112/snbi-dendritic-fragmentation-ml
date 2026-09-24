# Study4 — especificação conceitual congelada

Este documento descreve somente execução futura. A
[autoridade](../../configs/study4/authority.json) mantém ciência, matching,
payloads, features, fits e receipts desautorizados.

## Unidade e viabilidade futura

Unidade primária: MATCHED_POSITIVE_BACKGROUND_PAIR; comprimento temporal T=8.
A origem conceitual é o TRAIN histórico elegível de Study3, somente papéis
positivo/background já existentes, sem mineração de labels ou backgrounds.
A allowlist exata e a definição operacional de frame válido precisam de
contrato autorizado antes de ler o corpus. Os 64 grupos históricos não
implicam que existam 16 pares elegíveis.

O gate exige MIN_MATCHED_PAIRS=16, REQUIRED_FOLDS=4 e representação de ambas
as aquisições. Não inventar quota adicional por aquisição ou substituir os
limites após observar suporte. Falha implica INSUFFICIENT_COVERAGE_OVERLAP,
sem modelos. Ver [contrato de viabilidade](../../configs/study4/feasibility-contract.json).

## Matching e seleção de frames

Um edge exige mesma aquisição e pelo menos oito frame indices válidos comuns.
O matching será um pareamento um-para-um: nenhum grupo poderá compor mais de
um par, nem migrar entre treino e validação. Deve ser determinístico,
independente de pixels, features, performance e labels além dos papéis
positivo/background.

Objetivo lexicográfico futuro: maximizar quantidade de pares; entre soluções
de cardinalidade máxima, maximizar suporte comum total (soma das cardinalidades
das interseções dos pares); depois desempatar por identidades estáveis em ordem
determinística. O algoritmo e a codificação operacional desse desempate serão
congelados antes da execução; não são implementados aqui.

Para cada par, shared_frames é a interseção dos conjuntos de frames válidos.
Se houver menos de oito, o par é inadmissível. Ordenar os frames distintos e,
para k=0,...,7, usar a posição relativa k/7 no intervalo de ranks de 0 a n-1:
rank inteiro mais próximo de k*(n-1)/7, com empate exato para o menor rank.
Positivo e background recebem os mesmos oito frame indices. Sem interpolação,
frames sintéticos ou repetição para preencher trajetória insuficiente.
Ver [contrato de matching](../../configs/study4/matching-contract.json).

As representações futuras usam esse suporte comum selecionado. D1 preserva
a regra de mediana temporal inferior de Study3, aplicada aos oito frames
pareados; MEAN agrega somente esses oito frames. As CNNs recebem a mesma
seleção T=8. O controle de cobertura usa apenas esse suporte, com as quatro
features e normalizações de Study3; cobertura original não pareada não será
reinserida como feature. A identidade dos vetores de cobertura dentro de cada
par deverá ser verificada, sem presumir PASS do controle aprendido.

## Folds e avaliação

Os dois membros do par devem permanecer no mesmo fold. A alocação operacional
dos quatro folds será deliberada e congelada antes da execução, sem escolha
por score. Não presumir que a alocação histórica Study3 já preserve pares.
Grupo, par ou frames do mesmo grupo não podem atravessar treino e validação.
Pré-processamento aprendido permanece fold-local.

Cada condição gera uma predição por membro/grupo, mantendo o par como unidade
de divisão e dependência. A GMBA herdada é resumida nos quatro folds comuns;
pares e frames não são novas réplicas físicas. Os cinco contrastes e seus
descritores estão no [contrato de avaliação](../../configs/study4/evaluation-contract.json).
Não calcular métricas ou p-values em S4-0.

## Condições e orçamento futuros

| Condição permitida | Fits máximos |
| --- | ---: |
| D1_LBP20 + RF_REFERENCE | 4 |
| TRAJECTORY_MEAN_LBP20 + RF_REFERENCE | 4 |
| TEMPORAL_CNN1D_LBP20 | 4 |
| SPATIOTEMPORAL_CNN_SMALL | 4 |
| COVERAGE_METADATA_LOGREG | 4 |
| ACQUISITION_ONLY | 0 |

MAX_DISTINCT_FITS=20; FIT_21_PROHIBITED=true.
SCIENTIFIC_INVOCATIONS=1; RETRIES=0, apenas sob decisão científica futura.
Os quatro fits metadata pertencem ao mesmo orçamento; não são piloto extra.
O controle deve preceder todos os fits visuais, inclusive RF. Se falhar,
nenhum modelo visual é executado. Falta de suporte encerra antes de qualquer
fit. Não adicionar mediana, quantis, outros modelos ou novas seeds.

## Reutilização sem retuning

Referências imutáveis na base documental Study3:

- [Representações/LBP](../../configs/study3/representation-contract.json):
  LBP uniforme, P=8, R=1, dez bins por canal, dois canais, LBP20.
- [Modelos](../../configs/study3/model-contract.json): todos os parâmetros
  RF_REFERENCE e LogisticRegression; aquisição-only por maioria no treino,
  desempate classe 0, sem fit.
- [CNN](../../configs/study3/cnn-contract.json): seed 42, CPU, uma thread,
  Adam, learning rate 0.001, weight decay 0, CrossEntropyLoss, 30 epochs.
  CNN1D Conv1d 20→32→32, pooling global e Linear 32→2, 5.122 parâmetros,
  batch size 8 e normalização fold-local.
  CNN espaço-temporal com encoder Conv2d 2→8→16, head Conv1d 16→16,
  pooling global e Linear 16→2, 2.138 parâmetros, batch size 4 e /255.

O código histórico de desenho, CNN, modelos e métricas é a referência de
implementação, não uma autorização para importar/executar seus controladores.
Não retunar seed, optimizer, learning rate, epochs, batch size, arquitetura,
RF ou LBP. A integração de suporte/pares exige autorização posterior específica,
testes sintéticos e freeze anterior à ciência; nenhum código é modificado agora.

O threshold operacional de neutralização é deliberadamente PENDING_AUTHOR_DECISION.
Seu alvo conceitual é compatibilidade com chance. A definição da estatística,
regra de aceitação e threshold deverá ser congelada antes de qualquer execução
científica futura. Não escolher threshold com base no resultado observado.
