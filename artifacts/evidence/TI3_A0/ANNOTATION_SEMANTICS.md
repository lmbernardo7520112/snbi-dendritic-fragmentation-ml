# TI3-A0 — semântica e caracterização das anotações

Estado: localização cumulativa documentada; geometria caracterizada parcialmente;
contrato de target ML não validado. CIRCLE_IS_FRAGMENT_MASK=false.

## Evidência e representação

A [evidência documental](DOCUMENTARY_EVIDENCE.md) sustenta que as localizações
de eventos cumulativos são circundadas. Não documenta o interior do círculo
como extensão física nem comprova completude ou negativos confiáveis.

Foram examinados somente ESM3:0/73/146/219/293 e
ESM6:0/98/197/295/394, todos ANNOTATION_CONTRACT_DEVELOPMENT_ONLY e
permanentemente inelegíveis para FINAL_TEST. As visualizações foram geradas
desses mesmos dez buffers; nenhuma radiografia ESM1/ESM4 foi reaberta.

Os marcadores aparecem como anéis vermelhos. Nos planos nativos YUV420p,
valores fortes frequentes são U≈90 e V≈240; o cinza fica próximo de
U=V=128. A visualização RGB empregou conversão BT.601 limitada ilustrativa,
sem certificação de colorimetria. O algoritmo usa U/V nativos, não o RGB.

O interior de anéis isolados mostra conteúdo radiográfico cinza, em vez de
preenchimento vermelho. Isso é observação visual; identidade byte a byte com
a radiografia limpa não foi testada. Não se inferem tamanho ou máscara de
fragmento. Caixas isoladas são predominantemente 28×28 pixels na máscara de
chroma, que inclui discretização/halo. Nos candidatos aceitos, raio do ajuste
10,607489–10,846570 px; espessura radial P05–P95 6,891819–7,047511 px.
São descritores do traço gráfico, condicionados à seleção do protótipo,
não intervalos metrológicos nem dimensões físicas.

ESM3 tem grupos de anéis sobrepostos, marcas cortadas nas bordas e oclusões
pela barra/textos. ESM6 mostra anéis isolados nas imagens disponíveis.
Timestamp e barra são predominantemente acromáticos, mas podem cortar marcas
e alterar topologia. A ausência de chroma nos dois frames iniciais significa
ausência de componente acima do limiar, não ausência física de fragmentação.

## Resultado da extração única

| Fonte:índice | Componentes | Círculos aceitos | Ambíguos | Pequenos |
| --- | ---: | ---: | ---: | ---: |
| ESM3:0 | 0 | 0 | 0 | 0 |
| ESM3:73 | 91 | 14 | 77 | 0 |
| ESM3:146 | 112 | 18 | 93 | 1 |
| ESM3:219 | 112 | 19 | 92 | 1 |
| ESM3:293 | 113 | 20 | 92 | 1 |
| ESM6:0 | 0 | 0 | 0 | 0 |
| ESM6:98 | 9 | 2 | 7 | 0 |
| ESM6:197 | 18 | 12 | 6 | 0 |
| ESM6:295 | 18 | 12 | 6 | 0 |
| ESM6:394 | 18 | 11 | 7 | 0 |

491 componentes observados incluem repetições temporais. Os 108 círculos
aceitos geometricamente não são 108 eventos físicos independentes.
380 componentes ambíguos e três pequenos permaneceram registrados.
Todos conservam semantic_label=UNKNOWN; os centros dos componentes recusados
não são exportados como coordenadas aceitas.

A extração não é completa ou validada como ground truth. Há limitação do
próprio critério congelado: sete dos nove anéis visualmente isolados em
ESM6:98 foram recusados exclusivamente por P95 radial acima de 4 px
(aproximadamente 4,02–4,25 px). O diagnóstico mede a distribuição radial do
traço espesso, não erro contra um centro de referência independente.
Não ajustamos o limite depois desse resultado. Isso não prova defeito da
fonte nem impossibilidade de extrair seus marcadores.

## Persistência e surgimento

| Fonte | Transição | Correspondências de centros aceitos |
| --- | --- | ---: |
| ESM3 | 73→146 | 8 |
| ESM3 | 146→219 | 9 |
| ESM3 | 219→293 | 12 |
| ESM6 | 98→197 | 2 |
| ESM6 | 197→295 | 10 |
| ESM6 | 295→394 | 9 |

As transições a partir do índice 0 não têm círculo anterior para parear.
A inspeção visual é compatível com permanência de várias marcas e surgimento
de outras nos instantes amostrados. Porém o teste global retornou
UNRESOLVED_GRAPHICAL_AMBIGUITY em ambas as fontes. Rejeições que variam entre
frames podem produzir um unmatched sem desaparecimento real da marca;
sobreposições também impedem atribuição individual. Não se declara violação
física de cumulatividade.

CUMULATIVE_PERSISTENCE_SUPPORTED_ON_EXPOSED_DEVELOPMENT_FRAMES=
NOT_VERIFIED_GLOBALLY. Primeira observação amostrada não é primeira aparição
exata nem instante físico. Sem validação de identidade, nem todo componente
que aparece isolado depois pode ser chamado de evento novo. Mesmo uma
associação íntegra em cinco instantes forneceria limites entre observações,
não o frame exato de onset.

## Escalada de novos frames

Nenhuma janela temporal foi selecionada ou aberta. A fase 8 exige que
persistência/onset seja o único obstáculo restante. Extração robusta,
associação de marcas, tolerância do target e supervisão/avaliação sob
anotações possivelmente incompletas continuam pendentes. A condição não foi
satisfeita. Não houve segunda janela, busca adaptativa ou tuning.
