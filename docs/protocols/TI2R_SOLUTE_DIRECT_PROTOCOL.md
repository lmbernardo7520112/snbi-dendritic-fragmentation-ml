# TI2R-SOLUTE-DIRECT — protocolo multimodal congelado antes dos pixels

Decisão autoral de 2026-09-18; base pós-merge PR #8
`db03183e1456f67b5b663a4cb71361cad1404dcb`; branch
`feat/ti2r-solute-direct-mapping`. G2_FRAG=PASS_DIRECT_RASTER_MAPPING permanece
aceito e fechado, independentemente do resultado solutal. Este protocolo não
reabre autoridades anteriores nem modifica seus métodos ou resultados.

## Hipótese, ativos e custódia

Somente identidade raster de ESM2→ESM1 e ESM5→ESM4. Origem no centro do pixel
superior esquerdo, x=coluna, y=linha; móvel→referência: x_ref=x_mov, y_ref=y_mov.
Única matriz admissível e sua inversa: identidade 3×3. Os 48 deslocamentos
inteiros não nulos em [-3,+3]² são exclusivamente controles negativos;
nenhum resultado permite adotar translação ou outro modelo.

| Par | Dimensões de ambos os membros | Desenvolvimento | Holdout |
| --- | --- | --- | --- |
| ESM2→ESM1 | 1278×1018 | 0,146,293 | 73,219 |
| ESM5→ESM4 | 1278×1012 | 0,197,394 | 98,295 |

Exatamente 20 buffers YUV420p de 8 bits já existentes no manifesto. Dimensões
foram conferidas documentalmente antes dos pixels; o guard exige os mesmos
tamanhos, formato e hashes antes de entregar bytes ao método. São buffers
MP4 decodificados, não dados brutos do detector. Não abrir ESM3/6, ZIP/MP4,
novos frames ou fontes alternativas; sem FFmpeg/FFprobe ou redecodificação.

O registro de exposição é explícito: os desenvolvimentos já foram observados
em TI-2; as referências ESM1/ESM4, inclusive seus holdouts, foram usadas na
tentativa FRAG-DIRECT. Os holdouts móveis ESM2/ESM5 não foram analisados em
TI-2 e ficaram fora das tentativas FRAG. Elegibilidade nesta fase não significa
virgindade global nem independência estatística. O holdout é temporal interno
à mesma aquisição e só abre após desenvolvimento aprovado e identidade
congelada. Não haverá retorno ao desenvolvimento ou nova abertura de ativo.

## Máscaras, partição e representação

Parâmetros normativos completos: `configs/registration/ti2r-solute-direct-method.json`.
Representação na luminância Y nativa, sem conversão física, equalização,
CLAHE, histogram matching ou normalização entre modalidades. U/V permanecem
preservados nos buffers originais; crominância não determina exclusão.
O filtro cromático de anotações FRAG não é transferido aos campos solutais.

Exclusões geométricas congeladas: 12% superiores, 15% inferiores e borda de
quatro pixels para camada de apresentação, textos, timestamps e barra.
São baseadas nas regiões documentadas anteriormente, sem nova inspeção visual.
Não se presume que qualquer cor seja overlay; a prova depende também dos
controles temporais, para impedir que moldura ou estrutura estática certifique
correspondência do mesmo instante. Nenhuma máscara é ajustada após C2.

Grade 6×6 na faixa restante, checkerboard separando irrevogavelmente seleção
e auditoria. Guarda interior de 20 pixels cobre descritor, derivadas e
controles; nenhum footprint de um papel alcança o outro. Regularização é
individual e local ao bloco/papel, nunca uma estatística global compartilhada.
Cada comparação usa os mesmos pixels elegíveis para identidade e controles,
aceita máscaras parciais e exige pelo menos 512 pixels absolutos por bloco.
Não há gate de suporte integral, fração global de 90% ou ROI escolhida visualmente.

## Identificabilidade individual

Classificar cada imagem separadamente antes de comparar pares. Considerar
energia/distribuição dos gradientes, entropia, saturação e quantidade/cobertura
de pixels. Um instante do par é IDENTIFIABLE somente quando ambas as imagens
satisfazem seus critérios individuais, com oito blocos por papel e quatro
quadrantes. Não consultar outro frame, offset vencedor, score comparativo,
residual ou resultado esperado para mudar essa classificação.

O índice inicial pode ser NON_IDENTIFIABLE. Isso não constitui PASS ou
desalinhamento. Propriedades individuais insuficientes dos demais instantes
também permanecem registradas; não se selecionam frames favoráveis.

## Seleção por auto-semelhança e auditoria NGF

Implementação explícita `LOCAL_SELF_SIMILARITY_8`, permitida como descritor
de auto-semelhança multimodal. **Não se alega implementação exata MIND-SSC**.
Oito canais com deslocamentos axiais/diagonais de dois pixels; cada distância
é o SSD médio em patch 3×3. Subtrair a menor distância local, normalizar pela
média das oito distâncias, com proteção numérica congelada, e aplicar
exponencial negativa. Score de seleção: 1 menos a distância absoluta média
dos descritores nos pixels e canais permitidos, depois média entre blocos.
Inversão e transformações de intensidade são avaliadas apenas em phantoms;
não se presume invariância universal à mudança de modalidade.

Auditoria usa somente os outros blocos: NGF sign-invariant,
`(g_ref·g_mov)^2 / ((|g_ref|²+eta_ref²)(|g_mov|²+eta_mov²))`.
Gradientes Sobel e regularização individual por bloco, com regra congelada;
ausência de gradiente não gera concordância artificial. Não se usa correlação
bruta de intensidades, SSIM ou realce como prova geométrica.

Em cada instante identificável, identidade deve superar todos os 48 controles
espaciais com a margem pré-registrada, tanto na seleção como na auditoria.
Todos os pares temporais incorretos R_i→M_j (i≠j) são comparados sob identidade;
o correto deve superar cada controle temporal nas duas métricas. No
desenvolvimento, são seis controles dirigidos possíveis por par; no holdout,
os dois instantes atuam como controles incorretos entre si, pela mesma regra,
sem reabrir desenvolvimento. Os controles associados a instante inconclusivo
não servem para aprová-lo. A informação de cada imagem permanece independente
do resultado dos controles. Resultados e suportes são preservados.

Todos os pares temporais dirigidos ficam registrados. Se o par correto for
NON_IDENTIFIABLE, seus controles ficam explicitamente inconclusivos, sem
score/resultado inventado; os controles contra todas as móveis, inclusive
individuais NON_IDENTIFIABLE, continuam obrigatórios nos instantes identificáveis.
O relatório distingue quantidade de registros e quantidade efetivamente medida.

| Critério congelado | Valor |
| --- | --- |
| Informação individual por bloco | gradiente RMS≥0,25; razão de autovalores≥0,01; entropia≥1 bit em 32 bins |
| Saturação individual | Y≤16 ou Y≥235 em no máximo 50% dos pixels |
| Periodicidade individual | coerência NGF própria máxima<0,98 nos lags axiais 2..12; mínimo 128 pixels |
| Piso do score em cada bloco medido | auto-semelhança≥0,90; NGF≥0,80 |
| Margens espacial e temporal de cada métrica | ≥0,005 contra todos os controles |
| Regularização NGF individual do bloco | eta=max(0,01; 0,03×RMS do gradiente) |
| Ambiguidade de pico / proteção numérica | 1e-9 / 1e-12 |

Resíduo local: posição do máximo NGF na grade fixa [-3,+3]², somente como
métrica de auditoria. Eventual interpolação parabólica da posição mede erro,
nunca modifica a identidade. Empate/ambiguidade e máximo na borda da pesquisa
bloqueiam por evidência insuficiente/censurada; não certificam erro fora da
janela como se fosse pequeno. Todo resíduo calculável é registrado, inclusive
se exceder limiar. Sem trimming, descarte por erro ou outliers.

## Gates e parada

Desenvolvimento: pelo menos dois de três instantes identificáveis e todos eles
aprovados, identidade única nas duas métricas, controles espaciais/temporais
vencidos, oito blocos por papel, quatro quadrantes e nenhuma contradição.
Resíduos por instante e agregado separado: mediana≤1 px, P95≤2 px, máximo≤3 px.
O agregado é requisito adicional, nunca substitui falha local ou temporal.

Os dois desenvolvimentos são concluídos antes de qualquer holdout. Cada par
aprovado grava `<par>-freeze.json` uma única vez, com identidade e relatório
de desenvolvimento, antes de abrir seus quatro buffers reservados. Holdout
exige ao menos um de dois instantes identificáveis; todos os identificáveis
devem passar exatamente os mesmos parâmetros e controles congelados.
Sem refit, nova máscara, offset alternativo, retry ou novo registrador.

Dois pares aprovados: PASS_DIRECT_MULTIMODAL_MAPPING e
G2_SOLUTE=PASS_INTERNAL_DIRECT_RASTER_IDENTITY;
G2_SPATIAL=PASS_WITHIN_SAMPLED_ACQUISITIONS. Um: PARTIAL_ONE_PAIR e
G2_SPATIAL=PARTIAL. Nenhum: classificação bloqueante com razões por par;
G2_SOLUTE=BLOCKED e G2_SPATIAL=PARTIAL_FRAG_ONLY. Custódia/dimensão divergente
interrompe a fase. Se múltiplas razões coexistirem sem par aprovado, a ordem
de resumo é custódia/dimensão, holdout, discordância multimodal, identidade
não discriminativa e informação insuficiente. Todas as razões individuais
permanecem disponíveis. Uma interrupção técnica é declarada como tal, nunca
disfarçada como resultado científico. G2_FRAG permanece PASS em todos os casos.
G3=PENDING_SEPARATE_DECISION; TI-3+ permanece não autorizada.

## Governança e limites

Autoridade independente: `configs/authority/ti2r-solute-direct.json`, exigindo
consumo de todas as autoridades anteriores. C1 congela tudo inativo antes dos
pixels; C2 altera somente autoridade e decisão. O runner valida branch,
base/C1/C2, árvore limpa, diff limitado e 14 textos idênticos a C1. Receipt
O_EXCL/fsync anterior aos bytes, contador 1; cada ativo só admite uma tentativa
de abertura O_RDONLY/O_NOFOLLOW, com tamanho/hash do manifesto. Sem retry.

Testes usam apenas phantoms/fixtures sintéticos: inversão de contraste,
transformação monotônica não linear, uniforme, periodicidade, saturação,
conteúdo independente, deslocamentos conhecidos, controles temporais estáticos
e incorretos, separação espacial, máscaras parciais e preservação de erros.
As margens são fixadas somente nesses controles antes de C1. Dependências
locais preexistentes; nenhuma instalação local ou alteração do sistema.

C3 contém somente resultado, evidência, relatório e CLOSED_CONSUMED. Depois:
testes/guardrails, push fast-forward, Draft PR e CI automática. Não criar
commit pós-publicação, remediação, Ready ou merge. Evidências dinâmicas de SHA
C3, push e CI ficam no PR e retorno ao autor. Estados finais: atividade NONE,
TI2R=false, TI3+=false, merge=false. Métodos/resultados anteriores imutáveis.

Mesmo em PASS, alegar somente congruência espacial dos campos radiográficos
relativos de soluto com suas radiografias nos instantes das duas aquisições
amostradas, dentro deste protocolo e tolerâncias. Não alegar concentração
absoluta/wt.% Bi, calibração de intensidade, ground truth metrológico,
convecção, causalidade, generalização, independência entre frames, escala física
ou incerteza completa. ROI/máscaras experimentais não são exportadas.

Após PARTIAL/BLOCKED, o registro solutal automático encerra definitivamente.
Alternativas futuras exigem nova decisão: scripts/coordenadas originais,
documentação da produção dos vídeos normalizados, landmarks humanos com
protocolo independente, rederivação dos dados radiográficos ou nova aquisição.
