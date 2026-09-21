# Study2-B — pool de backgrounds somente como metadados

Não há quota, proporção de classes ou seleção por intensidade/texture/modelo.
Enumerar grid com passo65 e centros `(32+65*k,32+65*j)`, a partir da origem
nativa, por aquisição/frame. A área de segurança é o patch65 expandido por
três pixels; contatos também são tratados como interseção.

Excluir candidatos sem suporte integral na área de segurança, fora das bandas
textuais/bordas históricas ou intersectando qualquer região abaixo:

- União espacial global por aquisição dos patches dos 87 AUTO_GOLD sites,
  expandida pela mesma margem3, incluindo sites que só recebem anotação futura.
- Bboxes documentais dos footprints conhecidos em cada frame.
- Todas as bboxes AMBIGUOUS (24246 ocorrências) e SMALL (292), incluindo
  hipóteses não resolvidas. Nunca usar o campo histórico mal nomeado para filtrar.

As bboxes são conservadoras; não se promete completude física. A união global
impede classificar como background uma região de site ainda pré-anotação.
Suporte estrutural considera o mask cromático histórico do frame já admitido;
suporte solutal usa geometria. Nenhum patch background é extraído, persistido
ou apresentado. A análise do suporte não produz features ML.

Cada candidato admissível registra frame, centro, bounds, track, rank hash e
distâncias/estado das exclusões. BACKGROUND_TRACK_ID identifica somente
`acquisition_id|grid_x|grid_y`, constante entre frames. Um futuro split deve
manter cada track inteiro em uma partição. Hash rank é SHA-256 textual
determinístico; não é feature nem amostragem nesta fase.

Pool é BACKGROUND_CANDIDATE, não ausência física de fragmentação. Não inserir
UNLABELED longitudinal nesse pool. Views de sites não incluem backgrounds.
Study2-C deverá decidir seleção, pesos e split antes de materializar pixels
background; nenhuma dessas atividades é autorizada aqui.
