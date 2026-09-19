# TI3-A — protocolo documental antes dos pixels

Target: PUBLISHED_FRAGMENTATION_LOCATION_PRESENT. Uma observação canônica
por annotation_site_id: a própria coordenada da FIRST_CONFIDENT_OBSERVATION,
não o medoid que pode vir de um frame posterior. Os 52 sites, 108 observações
e 383 IGNORE históricos ficam intactos. FIRST_CONFIDENT_OBSERVATION não é onset.

Mapeamento G2_FRAG_DIRECT: ESM3→ESM1 e ESM6→ESM4 com offset inteiro (0,0).
Centro raster: floor(coordenada + 0.5), arredondamento ao pixel mais próximo,
com empate para cima; conservar também a coordenada documental original.
Não mover centro para aumentar suporte. Patch de índices inclusivos x±32/y±32,
65×65, luminância nativa uint8, sem padding de extração, resize ou contraste.

Suporte geométrico documental, em xyxy half-open: [5, ceil(0.12*h)+1,
w-5, h-ceil(0.15*h)-1]. Reutiliza border=4, bandas textuais e erosão de 1 px
da preparação histórica FRAG_DIRECT. Não é nova ROI científica, calibração
física ou certificação de toda máscara cromática. Fora desse suporte:
UNAVAILABLE. O raio de patch não mede fragmento físico.

O módulo de planejamento recebe somente listas JSON materializadas. Não tem
I/O experimental. Nenhum método histórico será chamado. A materialização
experimental exige manifesto válido, C1 publicado e CI verde no mesmo SHA.
Este texto pré-registra escolhas antes da primeira aplicação geométrica real;
não afirma que o dataset será viável ou que C1 já existe.
