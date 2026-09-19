# TI3-A0 — viabilidade do split temporal interno

**SPLIT_FEASIBILITY=BLOCKED_PENDING_TARGET_AND_EXPOSURE_CONTRACT.**
O split temporal interno é uma proposta ainda não executada. Nenhum ID,
seed, limite temporal ou partição TRAIN/DEVELOPMENT/FINAL_TEST foi definido.
**FINAL_TEST=NOT_DEFINED_NOT_OPENED.** Não há evidência de lacre de uma
partição existente, execução de ML ou prontidão para iniciar TI3-A.

Este documento registra a análise documental a partir dos contratos
históricos e das observações da primeira extração comunicadas pelo executor
de TI3-A0. Sua elaboração não abriu pixels nem repetiu a extração.

## Evidência disponível e bloqueio do target

A primeira extração, única e posterior ao congelamento da configuração,
registrou 491 componentes: 108 círculos aceitos pelo critério gráfico,
380 componentes ambíguos e três pequenos. Esses números são contagens de
componentes gráficos; não representam 108 eventos físicos independentes,
108 targets validados ou 491 samples ML.

Em ESM3 e ESM6, a persistência permaneceu
`UNRESOLVED_GRAPHICAL_AMBIGUITY`. O limite congelado de P95 de 4 px recusou
componentes que o executor descreveu visualmente como anéis isolados em
ESM6, com valores entre aproximadamente 4,02 e 4,25 px. Essa observação
explica uma limitação operacional do extrator; não autoriza arredondar
resultados, relaxar o limite, reclassificar casos por conveniência ou
reexecutar a extração. Os parâmetros permaneceram inalterados.

A candidata principal é **point-event localization das posições publicadas**.
Ela ainda não constitui target congelado. Localização de marca publicada,
localização do evento físico, extensão do fragmento e instante de ocorrência
são entidades diferentes. Círculo não é máscara de fragmento, conforme
ANN-201 da [matriz TI2](../../../docs/protocols/TI2_CONTRACT_MATRIX.md).

Permanecem sem justificativa suficiente a completude da extração, a
completude das anotações, a tolerância de localização fisicamente sustentada
e uma avaliação adequada aos casos desconhecidos. O limite gráfico de
4 px não fornece automaticamente uma tolerância de erro do futuro modelo.
Regiões sem círculo continuam **UNLABELED/UNKNOWN**, nunca negativos
verificados por ausência de marca.

Não se conclui que supervisão com positivos e casos não rotulados seja
impossível em geral. Sua adoção aqui exigiria explicitar o processo de
anotação, hipóteses de supervisão, objetivo e métricas válidas. Esses
requisitos ainda não foram satisfeitos; trocar o tipo de supervisão não
resolve automaticamente o contrato pendente.

## Unidades e exposição permanente

Há dois grupos documentais de aquisição, aproximadamente uma corrida por
condição. Frames, patches, modalidades, perturbações e versões registradas
não são novas aquisições independentes. A limitação está documentada no
[protocolo SOLUTE V2](../../../docs/protocols/TI2R_SOLUTE_V2_PROTOCOL.md).

Os dez frames de anotação abaixo permanecem irrevogavelmente **DEV_ONLY**:

| Fonte | Índices DEV_ONLY |
| --- | --- |
| ESM3 | 0, 73, 146, 219, 293 |
| ESM6 | 0, 98, 197, 295, 394 |

Essa restrição acompanha seus derivados e os grupos de proveniência ou de
evento que carreguem a informação exposta. Recortar um patch, alterar a
representação, trocar de modalidade correspondente ou registrar a imagem
não apaga a exposição. A identidade de evento, quando verificável, deve
acompanhar todas as repetições cumulativas da mesma ocorrência.

Os frames finais ESM3:293 e ESM6:394 também são DEV_ONLY. Suas marcações
cumulativas podem revelar localizações de eventos ocorridos em intervalos
intermediários. Portanto, reservar outros IDs de frames não comprova que
seus targets estejam não expostos. É necessário avaliar as dependências
da anotação e do evento, além da procedência dos pixels.

O holdout histórico SOLUTE permanece CONSUMED. Nenhum piloto exposto é
apresentado como globalmente virgem. Isso não prova a impossibilidade de
qualquer teste interno futuro, mas impede afirmar sua independência sem
um contrato explícito de exposição e de finalidade da avaliação.

## Requisitos da proposta temporal

Uma proposta futura deve usar blocos temporais contíguos e declarar o
objetivo de avaliação interna às aquisições disponíveis. Com dois grupos
não se obtêm três partições não vazias disjuntas por aquisição. Uma divisão
interna não deve ser apresentada como generalização externa ou como
replicação experimental independente.

Antes de atribuir qualquer frame a um bloco, devem ser definidos:

- a informação disponível no instante da predição;
- o suporte temporal da entrada e do target;
- a persistência e a identidade das marcações;
- o histórico necessário para diferenciar ocorrências;
- as relações entre frames, modalidades, derivados e eventos;
- o tratamento da exposição dos dez frames DEV_ONLY e de seus targets;
- a finalidade e os limites do futuro FINAL_TEST.

Seja `h_lookback` a extensão histórica necessária ao contrato temporal do
target. Não se atribui valor a essa extensão nesta fase. Sua definição
depende da persistência, do regime cumulativo e do significado da primeira
aparição observada. O primeiro frame disponível deve constituir uma
baseline com censura à esquerda: marcas já presentes não podem ser
automaticamente classificadas como eventos NEW. Uma aparição observada
entre dois instantes pode sustentar apenas um intervalo, sem identificar
o instante físico exato do evento.

Sejam `L` e `R` as extensões efetivas à esquerda e à direita do suporte
temporal de um sample, incluindo entrada, target e o `h_lookback`
necessário. Elas são requisitos a definir, não parâmetros escolhidos.
Se `p` for o último índice central de um bloco e `q` o primeiro do bloco
seguinte, sob extensões comuns e suporte inclusivo `[i-L, i+R]`, a condição
necessária para não haver sobreposição direta é:

```text
q - p > L + R
```

Com extensões diferentes, devem ser considerados o suporte à direita do
bloco anterior e o suporte à esquerda do seguinte. A desigualdade protege
somente contra sobreposição do suporte declarado. Não garante independência
estatística, não remove exposição prévia de targets e não elimina a
persistência de um mesmo evento através da fronteira.

A correlação temporal adicional permanece não quantificada. Não foi
inventado um tempo de decorrelação, um `tau`, uma quantidade de frames de
embargo ou uma seed. A cadência normativa de 1,18 s não fornece esses
valores. Se a anotação cumulativa depender de um histórico mais amplo,
essa dependência deve ser incluída no contrato; não pode ser escondida
atrás de uma janela finita escolhida por conveniência.

## Escalada de novos frames e decisão

A escalada única de novos frames exige localização sustentada e
persistência/onset como único obstáculo restante. Essa condição não foi
satisfeita: continuam pendentes completude, justificativa do target e
avaliação dos casos UNKNOWN, além da ambiguidade gráfica. **Nenhum novo
frame foi acessado.** A escalada não pode servir para contornar esses
requisitos ou selecionar casos mais fáceis.

Para aprovar a viabilidade será necessário um único target principal
sustentado, uma unidade amostral compatível, supervisão e avaliação válidas,
e um contrato temporal e de exposição que justifique a separação proposta.
A identificação de possibilidades teóricas não satisfaz esses requisitos.

O estado atual é BLOCKED, sem aprovação empírica do split. Não houve
treinamento, seleção de modelo ou avaliação TRAIN/DEV/FINAL_TEST. Os gates
G2_FRAG e G2_SOLUTE permanecem históricos e inalterados; este documento não
reabre ciência anterior nem autoriza execução de ML.

```text
SPLIT_FEASIBILITY=BLOCKED_PENDING_TARGET_AND_EXPOSURE_CONTRACT
FINAL_TEST=NOT_DEFINED_NOT_OPENED
ML_RUNS=0
TI3_A_READY=false
```
