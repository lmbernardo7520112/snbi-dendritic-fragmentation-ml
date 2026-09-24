# Study3-CNN — deliberação adversarial pré-ciência

Esta deliberação documental implementa o desenho que o autor especificou antes
da exposição operacional a metadados TRAIN. As nove perspectivas abaixo são
uma revisão assistida por agente, não nove especialistas humanos independentes.
Nenhum voto, credencial externa, nova análise de corpus ou resultado científico
é inferido deste documento.

A autorização vigente é **PRE_SCIENCE_FREEZE_AND_CI**: reconciliar o incidente,
implementar e testar com fixtures sintéticos, revisar, congelar, publicar e
verificar CI. Mesmo CI verde não permite criar receipt científico, abrir
payloads, executar `scripts/run_study3.py` ou iniciar fits experimentais nesta
fase. O estado PASS desta recuperação depende das verificações efetivas; este
parecer não afirma que elas já ocorreram.

## Contexto canônico e questão

A precedência documental é FINAL_CLOSEOUT → EVIDENCE_INDEX → evidências das
fases → Git → código. Os antigos espelhos de autoridade em AGENTS/README
descrevem autorizações históricas: não reativam fases consumidas. O HANDOFF
canônico explica essa diferença em seu registro de conflitos. A decisão atual
do autor concede somente o novo escopo explicitado acima.

[O fechamento](../final-closeout/SCIENTIFIC_PROGRAM_CLOSEOUT.md) preserva
Study2-A/B/C/D, as weak labels, o pipeline final C e os negativos históricos.
Study2-D perguntou se adicionar mais rows correlacionadas ajudava RF/LBP.
Study3 pergunta se representar explicitamente a trajetória fornece sinal
descritivo interno além de uma observação representativa. São perguntas
distintas. A comparação Study3 produzirá uma predição por grupo; não deve ser
confundida com a validação de todas as rows retidas por fold em Study2-D.

## Nove perspectivas

| Perspectiva | Objeção adversarial | Deliberação e limite residual |
| --- | --- | --- |
| 1. Ciência de Materiais / solidificação | Duas aquisições não identificam uma lei física; primeira observação confiante da marcação (FCO) não é onset. | A tarefa é discriminar referências gráficas publicadas em trajetórias históricas. Site não significa evento físico, campo solutal é relativo, e não se afirma mecanismo causal, temperatura, Bi absoluto ou forecasting. |
| 2. Visão Computacional | Textura e contexto espacial podem distinguir aquisições; patches vizinhos podem ser correlacionados. | Preservar canais STRUCTURAL_Y e RELATIVE_SOLUTE_FIELD_Y, LBP20 e patches históricos; ESM3/ESM6 não são input. Separação por grupo não garante independência espacial ou externa. |
| 3. Deep Learning / CNN | Com 64 grupos, CNNs podem memorizar aquisição/contexto e sobreajustar. | Duas arquiteturas, seed 42 e treino fixo antecedem a ciência. Não escolher arquitetura, época ou seed por score; preservar inclusive colapso para uma classe. Comparações não certificam superioridade universal de CNN ou RF. |
| 4. Modelagem temporal | Milhares de rows não são milhares de trajetórias; comprimento e suporte temporal podem virar proxies de classe. | Unidade GROUP_TRAJECTORY; ordenação determinística, resumos fixos e T=8 por ranks reais. Repetições em trajetórias curtas não criam observações novas. Posições relativas não identificam dinâmica em tempo físico nem igualam intervalos entre frames. |
| 5. Estatística / desenho experimental | Os quatro folds reutilizam os mesmos 64 grupos e duas aquisições. | Preservar folds históricos, uma predição por grupo e GMBA primária. Deltas pareados são descritivos; não fazer p-values, estimativas de generalização externa ou alegar novas réplicas experimentais. |
| 6. Weak supervision | GOLD é evidência automática; background candidato pode conter fenômeno físico não marcado. | Usar somente GOLD/BACKGROUND históricos, sem novos sites, tracks ou labels. Não promover SILVER, UNLABELED_PRE, UNLABELED_PERSISTENCE ou IGNORE. Erros são relativos à weak label, não recall físico de fragmentação. |
| 7. Engenharia de Software / MLOps | Um container compartilhado TRAIN/DEV pode permitir leitura incidental fora do grant. | Delegar offsets dirigidos a `study2d_io.TrainCorpusAccess`, com validação de identidade antes de paths, receipt antes de binários em eventual fase autorizada, deny de DEV/TEST e budget exato. Nesta fase o grant científico permanece fechado. |
| 8. Reprodutibilidade | Exposição histórica, incidente e ambiente podem ser ocultados por uma declaração exagerada de cegamento. | Preservar incidente TEXTUAL_TRAIN_METADATA_EXPOSURE_ONLY, hashes, proveniência e pins. Testes sintéticos e CI não são ciência nem autorização. Não declarar zero metadados acessados, nova confirmação cega ou equivalência universal entre ambientes. |
| 9. Revisor adversarial | Resultado desfavorável pode induzir novo modelo, rebalanceamento ou reabertura do TEST já consumido. | Congelar 28 fits e todos os contrastes antes da ciência; nenhum fit 29, retry, GRU, versão 2 ou escolha pós-resultado. Controles de aquisição e cobertura somente informam interpretação. Nenhum resultado substitui o pipeline final Study2-C. |

## População e exposição

Contrato histórico: 10.907 rows TRAIN, sendo 3.858 GOLD e 7.049 BACKGROUND,
32 grupos positivos + 32 tracks background, quatro folds históricos C/D.
Não são 10.907 experimentos independentes. A correlação temporal dentro de
grupos e a possível correlação espacial entre grupos continuam limitações.
Aquisição↔classe e comprimento da trajetória↔classe são confundimentos
possíveis; seu risco não foi descartado por inspeção dos metadados.

DEV histórico já foi usado para seleção e TEST C está consumido. Nesta fase
e no método proposto não há acesso material a DEV/TEST. Não existe validação
externa nem holdout novo. Os resultados Study3, se uma decisão posterior
autorizar sua execução, continuarão exploratórios e internos.

A leitura antecipada de metadados é registrada em
[STUDY3_PRE_SCIENCE_INCIDENT.md](STUDY3_PRE_SCIENCE_INCIDENT.md).
A [declaração de não adaptação](STUDY3_PREEXPOSURE_DESIGN_DECLARATION.md)
preserva os itens definidos antes dela. Não se produzem estatísticas novas do
corpus para justificar mudar o desenho.

## Decisão

O council admite a implementação e o congelamento do desenho exploratório
exato, condicionados a contratos, revisão, testes e CI aprovados. Não admite
execução científica sob a autorização de recuperação atual.

```text
STUDY3_KIND=INTERNAL_EXPLORATORY_TEMPORAL_REPRESENTATION_STUDY
PRIMARY_UNIT=GROUP_TRAJECTORY
STUDY2_C_DEV_ACCESS=false
STUDY2_C_TEST_ACCESS=false
DEVELOPMENT_ACCESS=false
TEST_ACCESS=false
EXTERNAL_GENERALIZATION=false
CONFIRMATORY_EXTERNAL_CLAIM=false
MODEL_SEARCH_AFTER_RESULTS=false
POST_RESULT_MODEL_SEARCH=false
METADATA_EXPOSURE_USED_TO_ADAPT_DESIGN=false
SCIENTIFIC_EXECUTION_AUTHORIZED=false
```

PASS científico, em eventual fase futura expressamente autorizada, dependerá
de execução contratual e preservação dos resultados, nunca de aumento de score
ou vitória de CNN. Esta decisão não marca freeze, CI ou execução como concluídos.
