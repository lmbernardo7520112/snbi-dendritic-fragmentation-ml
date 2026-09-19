# Background documental — pré-registro

BACKGROUND_CANDIDATE significa ausência de anotação publicada utilizável na
região selecionada, não ausência física comprovada de fragmentação.

Grid de centros com passo 65 px, ancorado no canto mínimo do suporte documental
acrescido de 32 px. Somente patches 65×65 totalmente contidos nesse suporte.
Nenhuma intensidade, textura, score, feature ou desempenho será consultado.

Excluir interseção ou contato com zonas POSITIVE de raio 35 px de todas as
observações da aquisição, incluindo sites que serão indisponíveis. Essa zona
cobre o suporte gráfico documentado dos círculos aceitos e a margem requerida.
Excluir igualmente as bboxes IGNORE de todos os instantes documentados da
mesma aquisição, expandidas por 3 px. Bbox A0 é half-open; converter seu
limite superior para o último pixel antes de aplicar a margem.
A união temporal conservadora preserva a incerteza de marcadores cumulativos;
um IGNORE jamais vira negativo por desaparecer do extrator em outro instante.
IGNORE não cancela a aceitação canônica de um positivo.

Quota: número de positivos válidos por split, sem exigir quota por frame.
Frames elegíveis: somente os declarados naquele split. Ordem de candidatos:
SHA256 UTF-8 de 'TI3_BACKGROUND_V1|42|source|frame|x|y', empate pelo texto.
Selecionar TRAIN, depois DEVELOPMENT, depois FINAL_TEST. Um background não
pode interceptar outro background já selecionado da mesma aquisição, mesmo
em outro frame, evitando reutilizar a mesma região espacial entre partições.

Conservar contagens e razões. Sem candidatos suficientes:
BLOCKED_BACKGROUND_SUPPORT e STOP. Nenhuma redução de margem, segunda grade,
novo threshold, mudança de patch, split ou ordem será testada após resultados.
