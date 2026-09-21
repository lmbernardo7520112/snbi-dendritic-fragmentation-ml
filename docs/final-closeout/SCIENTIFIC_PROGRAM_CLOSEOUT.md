# Encerramento canônico do programa científico

**Experimento 1 completo; Study2-A/B/C/D PASS; programa científico encerrado.**
O resultado final selecionado continua sendo RF_REFERENCE com
GOLD_PLUS_SILVER, LBP20 multimodal e TEST GMBA de **0.8449139278495638**.
O Study2-D acrescentou uma atribuição pós-hoc restrita ao TRAIN e não alterou
esse pipeline. Este fechamento reúne evidências existentes, sem nova ciência,
acesso experimental, recálculo de resultados ou construção de notebook.

O percurso teve bloqueios científicos, incidentes operacionais e decisões
subsequentes com escopo próprio. A sequência abaixo conserva essas distinções;
PASS significa cumprimento do protocolo aplicável, sem requisito de resultado
positivo. As métricas e respectivas unidades estão em
[CANONICAL_RESULTS.md](CANONICAL_RESULTS.md), e as âncoras de proveniência em
[EVIDENCE_INDEX.md](EVIDENCE_INDEX.md).

## A. Domínio experimental

O programa utiliza radiografias de solidificação de Sn–39,5 wt.% Bi, com duas
aquisições: bottom_up_anti_parallel e top_down_parallel. ESM1/ESM4 fornecem a
imagem estrutural; ESM2/ESM5, o campo solutal relativo; ESM3/ESM6, as marcações
cumulativas publicadas. As três modalidades de cada aquisição compartilham a
correspondência documental de índices: 294 frames na primeira e 395 na segunda.
Essas modalidades não constituem experimentos independentes.
[Fontes: G1](../../artifacts/evidence/G1/modalities-report.json) e
[G2-TEMP](../../artifacts/evidence/G2_TEMP/temporal-correspondence-report.json).

A reconciliação documental distingue tempo decorrido, 1,18 × frame_index,
de tempo experimental, com os offsets −25,96 s e −34,22 s. O FPS de reprodução
não representa a cadência física. A escala nominal de 1,40 μm/pixel está
documentada, mas a incerteza metrológica completa e a conversão física das
coordenadas não foram certificadas. A classificação posterior permaneceu em
coordenadas raster. [Reconciliação histórica](../../README.md) e
[limites de calibração](../../artifacts/evidence/G3/calibration-report.json).

## B. Registro e geometria

O TI2 inicial terminou com METHOD_V1=INSUFFICIENT_EVIDENCE,
G2_SPATIAL=BLOCKED_METHOD_V1 e G3=BLOCKED_DEPENDENCY_G2. O método não reuniu
correspondências suficientes para certificar transformação ou ROI. Isso não
demonstrou impossibilidade física de registro. Uma autorização posterior,
TI2R-FRAG, também terminou bloqueada por referência/cobertura insuficiente;
resíduos favoráveis em alguns instantes não substituíram os gates por instante.
[TI2](../../artifacts/evidence/TI2/execution-report.md) e
[TI2R-FRAG](../../artifacts/evidence/TI2R_FRAG/execution-report.md).

O protocolo separado FRAG-DIRECT restringiu os candidatos aos offsets inteiros
derivados das dimensões raster. Ambos os pares certificaram identidade, offset
(0,0), nos instantes identificáveis, incluindo validação temporal interna.
Os instantes iniciais permaneceram NON_IDENTIFIABLE e não receberam PASS ou
residual. A certificação dizia respeito ao piloto e ao mapeamento raster,
sem produzir metrologia ou validação externa.
[FRAG-DIRECT](../../artifacts/evidence/TI2R_FRAG_DIRECT/execution-report.md).

Na modalidade solutal, o SOLUTE-DIRECT V1 terminou
BLOCKED_IDENTITY_NOT_DISCRIMINATIVE: a identidade venceu controles relativos,
mas os scores não atingiram os pisos absolutos congelados de SS8 e NGF.
Nenhum holdout foi aberto nessa fase. O desenvolvimento V2, autorizado
separadamente, preservou kernels e resultados V1 e adotou discriminação relativa
e recuperação de perturbações inteiras. Seus quatro casos de desenvolvimento
passaram; isso ainda não constituía aprovação do holdout.
[SOLUTE-DIRECT](../../artifacts/evidence/TI2R_SOLUTE_DIRECT/execution-report.md) e
[SOLUTE-V2](../../artifacts/evidence/TI2R_SOLUTE_V2/execution-report.md).

A primeira CLI do locked holdout foi recusada no preflight porque a
serialização operacional converteu floats integrais em inteiros. Houve zero
execuções científicas e zero bytes experimentais nessa tentativa. Após reparo
operacional explicitamente autorizado, a primeira execução científica avaliou
os quatro casos e aprovou G2_SOLUTE sob o contrato V2. O bloqueio anterior e
os scores absolutos V1 permaneceram registrados. Não houve nova transformação,
calibração física ou certificação de ROI; a validação era temporal e interna às
mesmas aquisições.
[Incidente preservado](../../artifacts/evidence/TI2R_SOLUTE_HOLDOUT/execution-report.md)
e [primeira execução científica](../../artifacts/evidence/TI2R_SOLUTE_HOLDOUT/repair-1/execution-report.md).

## C. Resolução das weak labels

A0 isolou o chroma das marcações publicadas por threshold fixo, componentes
conexos e critérios geométricos. Dos 491 componentes examinados nos dez frames
históricos, 108 foram aceitos geometricamente, 380 permaneceram ambíguos e três
pequenos. A fase terminou BLOCKED_TARGET_CONTRACT: não comprovou extração
completa, persistência global ou onset físico. Nenhuma classificação ML foi
executada para contornar esse bloqueio.
[A0](../../artifacts/evidence/TI3_A0/execution-report.md).

A resolução posterior trabalhou somente com os JSON já produzidos e restringiu
explicitamente a semântica. As 108 observações aceitas sustentaram 52 sites
operacionais, 38 ESM3 e 14 ESM6; as 383 regiões restantes continuaram IGNORE.
O target passou a ser PUBLISHED_FRAGMENTATION_LOCATION_PRESENT, sob a estratégia
HIGH_CONFIDENCE_PLUS_IGNORE. Um círculo informa localização gráfica publicada;
não representa máscara do fragmento, onset exato ou evento físico confirmado.
BACKGROUND_CANDIDATE não prova ausência física, e IGNORE não foi convertido em
negativo. Essa resolução não reclassificou A0 retrospectivamente como PASS.
[Resolução do target](../../artifacts/evidence/TI3_TARGET_RESOLUTION/execution-report.md).

## D. Experimento 1

O primeiro experimento usou 34 samples TRAIN, 16 DEVELOPMENT e seis FINAL.
As comparações autorizadas conservaram os mesmos samples e suas limitações:
LBP/RF estrutural obteve BA DEVELOPMENT de 0.6875; a concatenação de LBP
estrutural e solutal relativo alcançou 0.75; a CNN multimodal mínima, com
170 parâmetros e dez épocas, obteve 0.50. A CNN classificou todos os samples
como positivos, resultado preservado sem tuning ou busca de arquitetura.
A regra prévia selecionou MULTIMODAL_LBP_RF.
[TI3-A](../../artifacts/evidence/TI3_A_RESUME/c0r1-resume/execution-report.md),
[TI3-B](../../artifacts/evidence/TI3_B_SOLUTAL/execution-report.md) e
[TI3-C](../../artifacts/evidence/TI3_C_CNN/execution-report.md).

TI3-D realizou um fit nos 50 TRAIN+DEVELOPMENT, 25 por classe, seguido de uma
avaliação dos seis FINAL, três por classe. O resultado foi quatro acertos:
BA, accuracy, precision, recall e F1 iguais a 0.6666666666666666; matriz
[[2,1],[1,2]], linhas verdadeiro/colunas predito, classes [0,1]. O estado
aprendido foi congelado antes de FINAL, e as predições foram gravadas antes do
scoring. Essa ordem computacional não equivale a cegamento humano ou ausência
de exposição histórica. FINAL está permanentemente consumido.
[TI3-D](../../artifacts/evidence/TI3_D_FINAL/execution-report.md).

O claim permanece SMALL_INTERNAL_TEMPORAL_CONFIRMATION. O conjunto pequeno,
a confusão potencial classe/aquisição e as weak labels impedem tratar o valor
como estimativa populacional precisa ou validação externa. O encerramento
anterior do Experimento 1 e a entrega acadêmica já existente permanecem
preservados; este fechamento não os reconstrói.
[Síntese histórica](../../artifacts/evidence/TI3_FINAL_CLOSEOUT/SCIENTIFIC_SUMMARY.md).

## E. Study2-A — mineração densa e tracking das anotações

Study2-A reutilizou o detector A0 congelado e conferiu sua reprodução histórica
antes da passagem integral. A única mineração dos 689 frames ESM3/ESM6 produziu
87 sites AUTO_GOLD e 27.396 registros site×frame, incluindo 7.941 observações
DIRECT_VALID e 5.737 AUTO_SILVER. Os 52 sites legados foram mapeados sem conflito;
os 35 adicionais são identidades gráficas recuperadas, não eventos físicos
novos comprovados. Estados de persistência não resolvida permaneceram separados
dos positivos. Não houve Hough, revisão humana ou modelagem ML.
[Study2-A](../../artifacts/evidence/STUDY2_A_ANNOTATION_MINING/execution-report.md).

A reconciliação documental posterior distinguiu as unidades dos agregados:
24.246 componentes AMBIGUOUS, 292 SMALL e 24.538 NON_VALID_COMPONENTS_TOTAL.
Os 18.962 UNRESOLVED_SITE_HYPOTHESIS_COMPONENTS não são 18.962 sites ou eventos.
O campo histórico mal nomeado foi explicado de forma aditiva, sem alterar
tracking, observações, sites ou resultados científicos.
[Reconciliação semântica](../../artifacts/evidence/STUDY2_A_ANNOTATION_MINING/METRIC_SEMANTICS_RECONCILIATION.md).

## F. Study2-B — corpus multimodal denso

Study2-B contabilizou todos os 27.396 registros, mantendo centros canônicos,
patches 65×65 e modalidades estrutural/solutal relativa. Admitiu 16.500 pares e
registrou 10.896 INVALID_BOTH, sem deslocamento, padding ou substituição para
aumentar cobertura. Entre os válidos, 5.218 são GOLD, 3.687 SILVER e 7.595 não
rotulados. Dos 87 sites, 52 têm suporte válido e 35 permanecem no inventário
como inválidos. Esses 52 não são o mesmo conjunto das 52 identidades legadas:
incluem 33 legadas e 19 adicionais.
[Study2-B](../../artifacts/evidence/STUDY2_B_CORPUS/execution-report.md).

O pool de backgrounds contém 70.844 candidatos frame×localização distribuídos
por 223 tracks, inicialmente somente metadados. Suas exclusões consideraram
todos os sites, inclusive futuros e inválidos, e as ambiguidades documentadas.
Não se balanceou por textura ou desempenho. GOLD/SILVER são níveis automáticos
de evidência gráfica; a construção do corpus não os transformou em ground
truth físico. Nenhum ML foi executado nessa fase.

## G. Study2-C — benchmark agrupado

Study2-C selecionou 52 sites válidos e 52 tracks background por regras textuais,
com 32/10/10 grupos de cada classe em TRAIN/DEV/TEST. A representação clássica
foi LBP20 multimodal; o benchmark comparou regressão logística, SVM RBF,
RF_REFERENCE, RF_TUNED e CNN_V2. Foram executados 80 fits CV, cinco fits de
comparação, uma ablação SILVER e um fit final: 87 ajustes em uma invocação.
CNN_V2 tem 5.010 parâmetros e vinte épocas; sua comparação com a CNN anterior
também envolve corpus e protocolo diferentes.
[Study2-C](../../artifacts/evidence/STUDY2_C_BENCHMARK/execution-report.md).

A GMBA, média entre recall macro por site positivo e especificidade macro por
track background, foi a métrica primária. RF_REFERENCE venceu DEV com
0.8759021928689068, por margem pequena sobre RF_TUNED. A ablação única de
SILVER elevou sua GMBA DEV a 0.8775115148991031, delta
0.0016093220301962585, e a regra estrita selecionou GOLD_PLUS_SILVER. Outras
métricas tiveram trocas: accuracy e F1 DEV caíram nessa ablação. A escolha não
foi revista para favorecer uma secundária.

O fit final usou 15.949 rows e 84 grupos TRAIN+DEV. O TEST único avaliou
3.257 observações de 20 grupos, com GMBA **0.8449139278495638**, BA por
observação **0.8525933757278337** e confusão [[2172,323],[126,636]]. O resultado
é INTERNAL_GROUP_HELD_OUT_TEST nas mesmas duas aquisições. O pipeline permanece
RF_REFERENCE + GOLD_PLUS_SILVER, com entrada STRUCTURAL_Y +
RELATIVE_SOLUTE_FIELD_Y; TEST_STATE=CONSUMED.

## H. Study2-D — atribuição controlada pós-hoc

Study2-D foi planejado após o benchmark para investigar diversidade de grupos,
densidade temporal e ponderação, mantendo LBP20, RF_REFERENCE e os quatro folds
históricos do TRAIN. Usou somente 10.907 rows GOLD+BG, de 32 sites e 32 tracks.
Não leu rows DEV/TEST nem seu cache TEST, não abriu vídeos e não mudou o
pipeline final. A CI do freeze original falhou em quatro testes sem skip de
NumPy; a ciência permaneceu parada até o reparo operacional autorizado e sua
CI verde. O original, a falha e o filho corretivo continuam preservados.
[Study2-D](../../artifacts/evidence/STUDY2_D_ATTRIBUTION/EXECUTION_REPORT.md).

A única execução completou exatamente 100 fits: 84 na curva de grupos,
12 adicionais na densidade e quatro adicionais na ponderação, reutilizando
condições já calculadas. Os contrastes globais canônicos foram:

| Fator | Contraste | Delta médio GMBA | Sinais pareados | Descritor |
| --- | --- | ---: | --- | --- |
| Grupos | K24 − K17, uma observação/grupo | +0.0039043309111838507 | 11 positivos e 9 negativos | MIXED_POSITIVE |
| Densidade | DALL − D1, mesmos grupos e GROUP_EQUAL | −0.059699310144642304 | Quatro folds negativos | NON_POSITIVE |
| Ponderação | GROUP_EQUAL − OBSERVATION_EQUAL, mesmas rows densas | −0.014586902176019961 | Quatro folds negativos | NO_GROUP_EQUAL_BENEFIT |

K24 versus K17 mostra benefício descritivo pequeno e misto; a curva de grupos
não é monotônica. Aumentar K aumenta também o número de exemplos representativos,
portanto não isola diversidade pura com n constante. K17 é somente uma ponte
de escala numérica com os 17 samples/classe do Experimento 1.

D1 teve GMBA média 0.7786692086875789 e DALL, 0.7189698985429366. Sob este
protocolo congelado, a replicação temporal densa reduziu a média global em vez
de melhorar a CV agrupada. Isso não significa que mais frames sejam fisicamente
prejudiciais, nem uma lei sobre outras representações ou modelos.

GROUP_EQUAL teve média 0.7189698985429366 e OBSERVATION_EQUAL,
0.7335568007189566. A ponderação por grupo não trouxe benefício nesse cenário
denso fixo; trocar pesos também pode alterar a massa total por classe. Os
quatro sinais globais negativos dos dois contrastes não se estendem
automaticamente aos estratos por aquisição. Nenhum desses resultados autoriza
trocar retrospectivamente os pesos do Study2-C.

## I. Conclusões finais

**Número de rows não equivale ao número de unidades experimentais independentes.**
Milhares de observações temporalmente correlacionadas não superaram uma
observação representativa por grupo no contraste DALL/D1 do protocolo fixo.
Essa conclusão pertence a este desenho e aos seus dados, não constitui regra
universal.

Study2-D não identificou um único fator positivo suficiente para explicar a
diferença histórica Experimento 1 → Study2-C. Ela é compatível com uma
combinação/interação de mudanças data-centric e metodológicas: corpus, grupos,
amostragem, split, pesos, seleção e métrica primária diferem. Os contrastes
condicionais não formam uma decomposição aditiva; não se atribuem percentuais
causais da diferença a grupos, densidade ou ponderação.

O programa documenta dados experimentais reais, pipeline rastreável,
proveniência das weak labels, comparação multimodal, representação clássica
versus aprendida, validação agrupada, TEST separado e atribuição pós-hoc. Essa
caracterização factual não constitui nota acadêmica, ranking ou certificação
institucional. Resultados negativos e limites de interpretação integram a
contribuição.

Study2-D foi integrado pelo [PR #19](https://github.com/lmbernardo7520112/snbi-dendritic-fragmentation-ml/pull/19)
no merge `5a158443fe00ace9b20f403f61f4a1aad21b285a`, preservando sua branch.
As CI do PR e pós-merge concluíram dez jobs e 110 passos SUCCESS em cada
verificação. Esta branch documental deriva exatamente desse merge; sua
[proveniência](../../artifacts/evidence/FINAL_CLOSEOUT/PROVENANCE.json) registra
as operações efetivas. O fechamento não realiza outra seleção ou avaliação.

## J. Limitações

São somente duas aquisições, sem validação externa. Frames, patches, sites,
tracks, folds e replicates não são novas réplicas experimentais independentes;
grupos próximos podem compartilhar contexto espacial. As labels são gráficas
e fracas, background não comprova ausência física e os campos solutais são
relativos. Não se demonstram causalidade física, onset exato, forecasting,
recall físico exaustivo, Bi absoluto ou significância universal. Study2-D é
pós-hoc; seus folds reutilizam o TRAIN histórico.
[Limitações completas](SCIENTIFIC_LIMITATIONS.md).

## K. Trabalho futuro e estado terminal

O roadmap separa possibilidades com o corpus existente — representação
temporal, agregação, embeddings de sequências, aprendizado autossupervisionado,
verificação humana assistida, formulações positive-unlabeled e augmentation
fisicamente restrita — das novas aquisições, replicatas, condições e ground
truth independente necessários à validação externa.
[FUTURE_RESEARCH_ROADMAP.md](FUTURE_RESEARCH_ROADMAP.md).

Nenhum desses itens foi executado neste fechamento. O programa científico está
completo; Experimento 1 FINAL e Study2-C TEST permanecem consumidos. A prontidão
para uma entrega acadêmica futura não autoriza construir notebook, refazer PDF
ou executar ciência. O estado canônico é
[FINAL_STATE.json](../../artifacts/evidence/FINAL_CLOSEOUT/FINAL_STATE.json):
CURRENT_AUTHORIZED_ACTIVITY=NONE_AWAITING_AUTHOR_DECISION.
