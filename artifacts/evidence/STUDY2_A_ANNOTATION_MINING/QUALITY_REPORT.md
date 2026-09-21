# Study2-A — qualidade documental do corpus longitudinal

**689/689 frames processados; 87 sites AUTO_GOLD; 52/52 sites históricos
mapeados.** A única mineração integral terminou sem retry. Este é um resultado
de reconstrução automática das anotações cumulativas publicadas, sem acurácia
de classificação, revisão humana ou certificação física dos eventos.

| Unidade | ESM3 | ESM6 | Total |
| --- | ---: | ---: | ---: |
| Frames processados | 294 | 395 | 689 |
| Sites únicos / AUTO_GOLD | 69 | 18 | 87 |
| Sites históricos mapeados | 38 | 14 | 52 |
| Sites adicionais ao legado | 31 | 4 | 35 |
| Observações DIRECT_VALID | 5.035 | 2.906 | 7.941 |
| Observações AUTO_SILVER | 4.660 | 1.077 | 5.737 |
| Componentes AMBIGUOUS por frame | 21.834 | 2.412 | 24.246 |
| Componentes SMALL por frame | 289 | 3 | 292 |
| Registros site×frame | 20.286 | 7.110 | 27.396 |
| PRE_FIRST_CONFIDENT_ANNOTATION | 6.090 | 2.821 | 8.911 |
| PERSISTENCE_EXPECTED_UNRESOLVED | 4.501 | 306 | 4.807 |
| CONFLICT / INVALID_FRAME | 0 / 0 | 0 / 0 | 0 / 0 |
| Transições de suporte para persistência não resolvida | 171 | 24 | 195 |

Os 7.941 componentes VALID também correspondem a 7.941 associações diretas
únicas nesta execução; são campos separados porque conflitos poderiam produzir
contagens diferentes. Os 27.396 registros equivalem a 69×294 +18×395, não a
87×689: sites não cruzam fontes. Aproximadamente **duas aquisições** permanecem
como unidades experimentais, independentemente do número de registros.

## Suporte, sobreposição e incerteza preservada

Dos 24.246 componentes ambíguos, 5.415 contêm integralmente a tinta de uma
âncora conhecida e 161 contêm duas âncoras. Eles produzem 5.576 registros de
componentes com OVERLAP_WITH_KNOWN_TRACKS e 5.737 observações AUTO_SILVER.
O termo operacional overlap designa incorporação da tinta conhecida em um
componente ambíguo, não prova geométrica ou física de um novo círculo/evento.

Outros 18.670 componentes ambíguos não têm suporte integral de nenhuma âncora.
Com os 292 SMALL, são 18.962 componentes diretamente não explicados por tracks.
Todos os 24.538 componentes não válidos conservam a possibilidade não resolvida
de tinta adicional, inclusive os que já contêm sites conhecidos. Esses números
contam componentes em frames, frequentemente repetidos ou pertencentes a texto
gráfico; não contam novos sites únicos nem novos eventos físicos.

AUTO_SILVER exige o conjunto inteiro de pixels cromáticos da primeira
observação válida dentro do componente atual, sem deslocamento ou tolerância
nova. Bbox apenas fornece proximidade. Compressão e mudanças gráficas podem
interromper esse suporte conservador. Os 4.807 estados de persistência não
resolvida e as 195 transições de desaparecimento do suporte permanecem no
ledger; não foram corrigidos, excluídos ou transformados em negativos.

## Distribuição temporal e primeira confiança

Há de 1 a 253 observações diretas por site ESM3 e de 7 a 309 por site ESM6.
Três sites têm uma única observação direta. A distribuição completa por
contagem e fonte está em CORPUS_SUMMARY.json; SITE_LEDGER.json contém os 87
históricos individuais, e QUALITY_DETAILS.json conserva a aritmética descritiva.

As primeiras observações diretas ocorrem nos frames 30–288 (ESM3) e 71–274
(ESM6). O último frame globalmente sem tinta cromática é 29 e 61, respectivamente.
Assim, todos os 87 sites possuem um bracket documental: (29, primeira direta]
ou (61, primeira direta]. Larguras: 1,18–305,62 s em ESM3 e 11,80–251,34 s em
ESM6. Os intervalos largos são uma limitação preservada. Ausência global de
tinta é distinta de ausência física de fragmentação; não foram certificadas
ausências locais intermediárias. PRE_FIRST não significa negativo nem prova
que a primeira anotação publicada surgiu exatamente no primeiro aceite A0.

Tempo experimental: −25,96+1,18i em ESM3; −34,22+1,18i em ESM6. A cadência
de reprodução de 5 fps não substitui essas fórmulas. Não há onset físico,
forecasting ou causalidade.

## Comparação com o Estudo 1 e limites

| Cobertura / unidade | Estudo 1 | Study2-A |
| --- | ---: | ---: |
| Frames de anotação examinados pelo detector | 10 | 689 |
| Observações diretas válidas | 108 | 7.941 |
| Sites operacionais únicos | 52 | 87 |
| Aquisições independentes novas | 0 | 0 |

O gate histórico reproduziu os dez hashes, 108/380/3 e centros dentro de
1e-9 px. As 108 observações originais mapeiam consistentemente para 52 tracks
distintos; nenhum legado foi eliminado. Os 35 sites adicionais decorrem da
maior cobertura temporal sob o método congelado. AUTO_GOLD é qualidade de
evidência gráfica e identidade, não uma medição de precisão contra ground truth
independente. O detector mantém todas as suas limitações A0, inclusive rejeições
radiais históricas. Círculo não é máscara ou extensão física de fragmento.

Nenhum ESM1/2/4/5 foi aberto. Não houve patches, features, ML, revisão visual,
centros manuais, Hough ou temporal delta. Não se afirma inventário físico
exaustivo, todos os eventos, validação externa, onset exato ou novo experimento
independente. Casos AMBIGUOUS/CONFLICT/UNRESOLVED são preservados para eventual
decisão futura; Study2-B e estudo com revisão humana não foram iniciados.

## Preservação e armazenamento

Dois containers textuais locais ignorados guardam 27.396 observações e
32.479 candidatos: 17.786.087 +49.636.870 = **67.422.957 bytes**.
LOCAL_ARTIFACT_MANIFEST.json contém caminhos, tamanhos, SHA-256 e contagens.
Não há 689 imagens exportadas ou arquivos individuais por observação.
Temporários de pixels, cache de patches e patches criados: zero.

O full run emitiu 1.345.528.320 bytes nativos, processados em memória. Pico RSS
Python: 243.760 KiB, incluindo detector/metadados; pico do decoder não medido.
Limite de transporte: três payloads nativos na transição produtor/consumidor,
sem janela anterior de frames retida. Footprints esparsos de âncoras permanecem
em memória e são distintos de cache de patches. A reserva de disco observada
ao final superou 666 bilhões de bytes, acima do mínimo de 53.687.091.200.

PASS depende de conformidade, cobertura, proveniência, legado e preservação.
Não depende de encontrar muitos sites ou obter uma métrica de modelo.
