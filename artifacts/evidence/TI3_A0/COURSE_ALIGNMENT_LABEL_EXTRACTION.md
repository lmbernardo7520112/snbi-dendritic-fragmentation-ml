# TI3-A0 — alinhamento curricular para extração do gráfico de annotation

A necessidade parte do dado: separar traço cromático e descrever localizações
anotadas. As técnicas abaixo não são introduzidas no registro G2 nem impostas
como entrada do futuro modelo. A correspondência A4/A5 usa o conteúdo descrito
pelo autor; os notebooks originais não foram acessados nesta etapa.

| Técnica / origem didática | Decisão | Uso e justificativa |
| --- | --- | --- |
| Threshold de intensidade, A5 | NOT_APPROPRIATE_FOR_CURRENT_EXTRACTION | Estrutura radiográfica e overlays acromáticos compartilham intensidades; intensidade não isola semanticamente o traço vermelho |
| Threshold de cor/chroma, extensão de thresholding A5 | USED | Distância de U/V a 128 separa o traço cromático no buffer nativo; limiar fixo 20 |
| Threshold adaptativo, A5 | NOT_USED | Não há benefício demonstrado nesta tentativa para separar sobreposições; sua aplicação não supre o contrato semântico |
| Otsu, A5 | NOT_USED | Não se introduziu seleção automática de threshold sem hipótese adicional; a representação cromática permitiu regra explícita |
| Connected components, operação associada à análise binária | USED | Inventaria todos os componentes de chroma com conectividade 8; preserva componentes mesclados e pequenos |
| Contornos, A5 | CONCEPTUALLY_RELEVANT_NOT_EXECUTED_AS_SEPARATE_METHOD | Forma, caixa, buracos e cobertura angular foram diagnosticados diretamente nos pixels do componente, sem pipeline adicional de contornos |
| Hough Circle Transform, família Hough A5 | OPTIONAL_EXPLORATORY_NOT_EXECUTED | Poderia ser estudada para sobreposições sob outra decisão, mas não há referência independente de decomposição e ela não resolveria sozinha os demais requisitos do target |
| Canny, A5 | NOT_USED | Não foi necessário para isolar chroma e não é entrada obrigatória de um modelo |
| Ajuste algébrico de círculo | USED_FOR_GRAPHICAL_DESCRIPTION | Descreve centro e raio do traço; não é treinamento ML ou medida de fragmento |

O método avaliado foi único: threshold de chroma + componentes + descrição
geométrica. Seu resultado parcial e suas rejeições são preservados; técnica
ensinada no curso não foi tratada como garantia de adequação ou PASS.

## Relações G2 preservadas

A5 Sobel → gx/gy → comparação de orientação de gradientes normalizados/NGF.
A4 descritores/características locais → representação estrutural →
self-similarity → SS8. Estas são conexões conceituais para o notebook futuro.
Os kernels G2 não foram modificados, importados ou executados nesta tarefa.

SS8 é um descritor local de auto-similaridade inspirado no princípio de
auto-similaridade independente de modalidade; não é declarado implementação
exata de MIND ou MIND-SSC. Nenhum benchmark retrospectivo com SIFT, ORB,
Canny, Otsu ou Hough foi realizado. O uso de uma operação para extrair o label
gráfico não a torna input obrigatório de ML.

Não houve leitura dos notebooks, CNN, Random Forest, t-SNE, matriz de confusão,
seleção de modelo ou treinamento. Este documento registra pertinência
didática e limites; não autoriza nova experiência.
