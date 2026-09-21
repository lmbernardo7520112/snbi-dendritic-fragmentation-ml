# Alinhamento curricular final

O programa empregou técnicas de visão computacional e aprendizado de máquina
conforme a tarefa científica de cada fase. Este documento explica os usos
registrados e seus limites; não introduz demonstrações, benchmarks ou acesso
a notebooks do curso. As referências históricas a A4/A5 retomam os conteúdos
descritos pelo autor, sem atribuir nota ou certificação acadêmica.

## Técnicas efetivamente utilizadas

| Tema | Uso no programa | O que ensina e qual é o limite |
| --- | --- | --- |
| Threshold e componentes conexos | A0 isolou chroma das marcações com limiar fixo 20 e conectividade 8; Study2-A reutilizou o detector congelado | Limiarização transforma um critério de cor em regiões; componentes e geometria organizam candidatos. Aceitar um círculo gráfico não confirma um fragmento físico. |
| Ajuste geométrico e tracking | Centros de círculos aceitos sustentaram sites operacionais e associação temporal; evidência direta, suporte SILVER e estados desconhecidos permaneceram separados | Identidade e proveniência importam tanto quanto a detecção. Anotação cumulativa não identifica onset físico nem justifica propagar todo estado como positivo. |
| Sobel e NGF | O registro solutal comparou gradientes Sobel por NGF sign-invariant, com regularização e suporte congelados | gx/gy descrevem variação local; a comparação de orientação permite lidar com contraste diferente entre modalidades. Gradiente ausente não deve produzir concordância artificial. Não foi input do classificador final. |
| Auto-similaridade local | SS8 participou da seleção/validação de correspondência multimodal, acompanhado de auditoria NGF em blocos distintos | Relações locais podem ser úteis quando intensidades absolutas não são comparáveis. SS8 não é apresentado como implementação exata de MIND/MIND-SSC. |
| LBP | P=8, R=1, uniform; histograma de dez bins, range=(0,10), density=True por modalidade | Descritor manual de textura local. TI3-A usou dez features estruturais; TI3-B/D e Study2-C/D usaram concatenação multimodal de vinte features. Não mede composição absoluta. |
| Random Forest | RF_REFERENCE preservou 100 árvores, seed 42 e os parâmetros históricos; Study2-D manteve esse modelo fixo | Ensemble clássico sobre descritores manuais; separar variação do modelo de variação dos dados permite contrastes delimitados. Alterar pesos ou corpus ainda altera o experimento, mesmo com parâmetros iguais. |
| CNN | Experimento 1 comparou CNN mínima de 170 parâmetros/dez épocas; Study2-C comparou CNN_V2 de 5.010 parâmetros/vinte épocas | Representação aprendida de patches com dois canais, uint8→float32/255. Ambas foram comparações delimitadas; resultados não autorizam concluir superioridade universal de RF ou impossibilidade de CNNs. |
| Features multimodais | Y estrutural e Y do campo solutal relativo foram alinhados por contratos e concatenados no LBP20; CNN recebeu os dois canais | Complementaridade depende de correspondência, suporte e semântica. ESM3/ESM6 fornecem anotações, não features; os círculos publicados não são entregues ao modelo. |

Fontes: [extração A0](../../artifacts/evidence/TI3_A0/COURSE_ALIGNMENT_LABEL_EXTRACTION.md),
[resolução do target](../../artifacts/evidence/TI3_TARGET_RESOLUTION/COURSE_ALIGNMENT.md),
[protocolo Sobel/NGF/SS8](../protocols/TI2R_SOLUTE_DIRECT_PROTOCOL.md),
[mineração temporal](../../artifacts/evidence/STUDY2_A_ANNOTATION_MINING/execution-report.md),
[CNN do Experimento 1](../../artifacts/evidence/TI3_C_CNN/execution-report.md) e
[benchmark Study2-C](../../artifacts/evidence/STUDY2_C_BENCHMARK/execution-report.md).

## Validação agrupada e matriz de confusão

O Experimento 1 separou TRAIN, DEVELOPMENT e FINAL para escolhas sequenciais
pré-definidas e uma avaliação final pequena. O Study2-C explicitou a separação
por site positivo e track background, preservando cada grupo em uma partição.
Reutilizou quatro folds no TRAIN para as buscas autorizadas, DEV para as
decisões de família/supervisão e TEST uma única vez após o ajuste final. O
Study2-D permaneceu inteiramente nos quatro folds TRAIN históricos, sem nova
escolha de modelo ou acesso a DEV/TEST.

A métrica primária do Study2-C/D foi definida por grupos:

```text
GMBA = 0,5 × (média do recall por site positivo
              + média da especificidade por track background)
```

Ela torna explícita a unidade de agregação. A balanced accuracy por observação
responde a outra ponderação: grupos longos contribuem com mais observações.
Separar essas métricas evita confundir milhares de rows com milhares de
unidades experimentais independentes. Agrupar trajetórias ainda não equivale
a validar em outra aquisição e não elimina automaticamente contexto espacial
compartilhado entre grupos.

Nas matrizes registradas, linhas são labels verdadeiras, colunas são predições
e a ordem de classes é [0,1]. TN/FP/FN/TP descrevem erros contra weak labels:
um FP em BACKGROUND_CANDIDATE não comprova uma detecção fisicamente falsa;
um FN não estabelece perda definitiva de um evento físico. A CNN mínima do
Experimento 1 alcançou recall 1 ao prever positivo em todos os samples, mas
teve BA 0.50. Esse resultado histórico ilustra por que recall isolado não
descreve discriminação nem substitui a matriz completa.

Fontes: [TI3-C](../../artifacts/evidence/TI3_C_CNN/execution-report.md),
[TI3-D](../../artifacts/evidence/TI3_D_FINAL/execution-report.md),
[Study2-C](../../artifacts/evidence/STUDY2_C_BENCHMARK/execution-report.md) e
[Study2-D](../../artifacts/evidence/STUDY2_D_ATTRIBUTION/EXECUTION_REPORT.md).

## Decisões de não utilização

| Técnica ou prática | Decisão documentada | Justificativa no escopo executado |
| --- | --- | --- |
| Hough e tuning do extrator | Não executados | Não havia referência independente para resolver automaticamente todos os círculos sobrepostos; alterar o detector após seus resultados mudaria as weak labels históricas. |
| Canny como input científico | Não utilizado | O target veio do chroma das anotações, e os modelos receberam Y estrutural/solutal limpo. Bordas Canny não eram requisito da pergunta experimental. |
| Augmentation arbitrária | Não utilizada | Transformações adicionais exigiriam justificativa física e contrato próprio; não pertenciam às comparações congeladas. |
| Architecture search | Não executado | Cada CNN tinha arquitetura e treino fixados antes da comparação. O resultado desfavorável não abriu busca retrospectiva. |
| SIFT, ORB/FAST/BRIEF no baseline | Não utilizados | O baseline adotou LBP para textura; cobertura curricular não exigia executar toda técnica disponível. |

Essas decisões não declaram as técnicas inúteis em geral. Delimitam o que foi
adequado e autorizado neste programa. Os bloqueios de registro, o resultado
negativo da CNN mínima e os contrastes não positivos de densidade/ponderação
permanecem evidências científicas, sem ajustes destinados a tornar o relatório
mais favorável.
[Alinhamento histórico](../../artifacts/evidence/TI3_FINAL_CLOSEOUT/COURSE_ALIGNMENT.md)
e [atribuição terminal](../../artifacts/evidence/STUDY2_D_ATTRIBUTION/EXECUTION_REPORT.md).

## Contribuição metodológica e alcance acadêmico

O percurso conecta processamento de imagens, extração de atributos,
aprendizado clássico e aprendido, desenho de avaliação e gestão de evidências.
Dados experimentais reais, parâmetros congelados, testes sintéticos, registros
de execução, resultados negativos preservados e proveniência das weak labels
sustentam uma caracterização factual do trabalho. Nenhuma nota, ranking de
qualidade ou certificação institucional é inferida desses atributos.

A principal lição data-centric é específica ao protocolo: em Study2-D,
milhares de rows temporalmente correlacionadas não superaram uma observação
representativa por grupo no contraste DALL/D1. Não se conclui que mais frames
sejam universalmente prejudiciais, nem que um único fator explique toda a
diferença Experimento 1→Study2-C. Os limites estão em
[SCIENTIFIC_LIMITATIONS.md](SCIENTIFIC_LIMITATIONS.md); possibilidades futuras
estão em [FUTURE_RESEARCH_ROADMAP.md](FUTURE_RESEARCH_ROADMAP.md), sem execução
autorizada por esses documentos.
