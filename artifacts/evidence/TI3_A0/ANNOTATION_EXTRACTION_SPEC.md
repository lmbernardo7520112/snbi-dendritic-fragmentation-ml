# TI3-A0 — especificação finita do protótipo gráfico

Status antes da extração: configuração congelada após caracterização autorizada
e testes sintéticos; nenhuma execução de ML. Somente os dez ativos de
development-manifest.json podem ser reabertos uma vez na fase extraction.
A caracterização anterior abriu cada ativo uma vez. Nenhum frame novo foi
selecionado. Resultados não justificam ajuste posterior.

## Escolha e critérios

Método principal único: threshold de chroma nativa, componentes conectados
8-vizinhos e ajuste algébrico de círculo para descrição geométrica.
A distância é max(abs(U−128), abs(V−128)) ≥20 nos planos YUV420p.
Cada amostra de chroma é expandida para seu bloco nativo 2×2.

O limiar 20 retoma somente a separação gráfica usada como exclusão histórica
G2, sem modificar ou executar seus kernels. A caracterização A0 encontrou
marcadores vermelhos de chroma forte (U/V próximos de 90/240), sem componente
≥20 nos frames iniciais, e caixas dominantes de 28×28 pixels nos anéis
isolados. Os demais critérios são conservadores para essa representação:

| Parâmetro | Valor |
| --- | ---: |
| chroma_distance | 20 |
| minimum_component_pixels | 32 |
| minimum_radius | 8 px |
| maximum_radius | 16 px |
| maximum_axis_ratio | 1,2 |
| maximum_radial_p95 | 4 px |
| minimum_angular_coverage | 0,9 |
| angular bins | 36 |
| persistence_tolerance_px | 2 px |

O raio permitido envolve o anel desenhado com caixa próxima de 28 pixels;
não é dimensão de fragmento. O limite radial aceita a espessura do traço e
a discretização de chroma 2×2, sem certificar incerteza física. A tolerância
temporal de dois pixels é um critério do diagnóstico do centro gráfico,
compatível com a discretização de chroma, não uma precisão metrológica.
Esses valores não foram escolhidos por desempenho de modelo e não serão
alterados depois da extração.

Exigir exatamente um buraco, cobertura angular e demais critérios para
VALID_GRAPHICAL_CIRCLE. Preservar como AMBIGUOUS_OR_NONCIRCULAR componentes
mesclados, preenchidos, cortados na borda, com forma inadequada ou ajuste
insuficiente. SMALL_COMPONENT é registrado, não descartado silenciosamente.
Até um glifo O pode ser geometricamente circular: classificação geométrica
não valida automaticamente semântica de evento. Não há máscara física.

## Hough e limites

Hough não é executado nesta tentativa. Componentes conectados bastam para
descrever anéis isolados; as sobreposições densas em ESM3 ficam explicitamente
não resolvidas, sem afirmar extração integral. Não há protocolo de referência
independente para certificar a separação desses grupos, nem se supõe que Hough
resolveria completude, o significado de negativos ou associação a eventos.
A tentativa não expandirá algoritmos para obter um PASS.

## Persistência e saída

Parear somente centros geometricamente válidos com correspondência recíproca
única dentro de dois pixels entre instantes consecutivos disponíveis.
Preservar unmatched e associações ambíguas. Qualquer componente não resolvido
impede PASS de persistência gráfica global da origem. PASS, quando observado,
refere-se aos instantes fornecidos e às marcas gráficas.

annotation_id é identificador do componente em um frame, não event_id físico.
center_x/center_y aceitos são nulos quando o componente é ambíguo; o centro
de ajuste diagnóstico permanece separado. Raio e espessura descrevem o traço.
A primeira observação amostrada não é EVENT_ONSET_FRAME.
Ausência de círculo permanece UNKNOWN, nunca ground truth negativo.

As 18 verificações sintéticas anteriores usaram apenas arrays gerados,
incluindo sobreposição, blob, texto, borda, discretização, entradas inválidas,
desaparecimento e associação ambígua. O módulo não abre fontes nem importa G2.
Os hashes do módulo, dos dois scripts e dos testes são congelados em
extraction-method.json antes da única chamada de extração.
