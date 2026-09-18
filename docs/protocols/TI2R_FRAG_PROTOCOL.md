# TI2R-FRAG — protocolo integrado congelado em C1

Autoridade: decisão autoral TI2R-FRAG-2026-09-18. Base
`0245faf74aa15424d95d43f92e87b32a06ac987b`; branch
`feat/ti2r-frag-registration`. Este protocolo, configuração e implementação
integram C1 antes de qualquer leitura experimental. Não há ajuste humano,
nova rodada ou mudança de código após C2.

## Autoridade, ativos e custódia

`configs/authority/ti2r-frag.json` é a única autoridade deste namespace.
`pyproject.toml [tool.snbi]` continua sendo a autoridade histórica fechada;
nenhuma API E0–E7 é reativada. O validador exige simultaneamente o fechamento
legado e o estado exato do namespace, rejeitando permissões concorrentes,
campos desconhecidos e tipos ambíguos. Os guardas legados auditam o escopo
legado; não constituem permissão para este runner.

| Par móvel → referência | Desenvolvimento | Validação condicional |
| --- | --- | --- |
| ESM3 → ESM1 | 0,146,293 | 73,219 |
| ESM6 → ESM4 | 0,197,394 | 98,295 |

São 12 buffers de desenvolvimento e oito de validação, todos já existentes.
`exposure.json` preserva o manifesto original, hashes, dimensões, planos,
índices e distinção entre materialização/hash opaco e interpretação de pixels.
As atestações positivas dos relatórios de execução, validação, integridade,
encerramento e remediações sustentam o lacre condicional dos quartis. Isso é
evidência documental delimitada, não observação universal de acessos externos.
Ausência de log não é usada como evidência de lacre.

ESM1: 1278×1018; ESM3: 1280×1024; ESM4: 1278×1012; ESM6: 1280×1012.
Buffers YUV420p de 8 bits, headerless, decodificados de MP4 anteriormente;
não são dados brutos do detector. Nada é redimensionado ou redecodificado.
Nenhum ZIP, MP4, ESM2/ESM5, FFmpeg/FFprobe ou caminho alternativo é acessível.

C1: `PREPARED_INACTIVE`. C2 altera somente a autoridade e seu registro de
decisão para `ACTIVE_ONE_SHOT`. O runner exige HEAD C2 limpo, C1 pai, base
exata e diff C1→C2 limitado a esses dois arquivos. Confere os textos congelados
contra C1 e cria `receipt.json` com O_EXCL, fsync, SHA C2, hashes, 20 ativos,
custódia e contador 1, antes do primeiro byte experimental. Receipt preexistente
bloqueia qualquer nova invocação. A leitura é única por ativo; autoridade,
branch, HEAD, receipt, identidade, papel e lacre são conferidos antes de
conversão de caminho, stat, abertura, hash ou criação relacionada aos dados.
Travessia usa descritores e O_NOFOLLOW em todos os componentes. Tamanho/hash
divergente ou ativo ausente encerra sem procurar/redecodificar substituto.

## Coordenadas, máscaras e independência espacial

A matriz homogênea 3×3 mapeia **móvel → referência**, `x=coluna`, `y=linha`,
origem `(0,0)` no centro do pixel superior esquerdo. Uma única transformação
estática por par usa conjuntamente os três instantes de desenvolvimento.
Não há reflexão, inversão de eixos, transformação por frame, projetiva ou não
rígida. Unidades permanecem pixels; orientação física e escala não são inferidas.

Os parâmetros exatos estão em `configs/registration/ti2r-frag-method.json`.
Regras fixas: luminância Y; exclusão de crominância cuja distância máxima de
U/V a 128 seja ≥20, ampliada por halo quadrado de cinco pixels; exclusão dos
12% superiores, 15% inferiores e borda de quatro pixels, com erosão de um
pixel para o Sobel. Não se reconhecem, contam ou usam círculos como fiduciais.
Textos, timestamps e barra ficam fora pela regra geométrica, sem recorte visual.
Não há CLAHE ou exclusão por erro observado.

Avaliação independente: grade 4×4 nos centros normalizados
x=(0,18;0,39;0,61;0,82), y=(0,23;0,41;0,59;0,77).
Lado par: 7% da menor dimensão, limitado a 16–64 pixels. Ajuste exclui esses
tiles e halo de 34 pixels em ambos os rasters, cobrindo o domínio admissível
de movimento (32 pixels nos cantos), Sobel e interpolação. A normalização de
ajuste usa apenas suas amostras; cada tile de avaliação tem normalização local
independente. Os tiles nunca fornecem valores para otimização de parâmetros.
Os critérios de desenvolvimento selecionam a primeira classe admissível; logo
a estimativa de generalização temporal vem dos quartis, não desses critérios
de seleção de classe no desenvolvimento.

## Ajuste, hierarquia e referência independente

M0 identidade é sempre avaliado. Somente uma falha de critério absoluto permite
M1 translação, depois M2 rígida, depois M3 afim. O primeiro PASS interrompe a
hierarquia. Cobertura de referência insuficiente bloqueia o par sem procurar
outro método. Os dois pares são avaliados independentemente na mesma invocação;
um bloqueio científico de um par não modifica o método do outro. Falha de I/O,
autoridade ou interrupção encerra a invocação inteira.

M1–M3 minimizam a média igualmente ponderada dos três custos `1−NCC` de
magnitude do gradiente Sobel, em amostras nativas com passo quatro e no mínimo
256 pontos de ajuste por instante. Inicialização translacional usa correlação
de fase exclusivamente no suporte de ajuste; classes seguintes partem da
anterior, sem valores dos quartis. Powell tem no máximo 120 iterações/2000
avaliações, xtol=1e-4 e ftol=1e-6. Limites: translação ±16 px, rotação ±1,5°,
coeficientes afins em ±2,5 pontos percentuais em torno da identidade e movimento
de cantos ≤32 px. São limites desta tentativa, não limites físicos comprovados.
Inicializações finitas usam somente custo de ajuste: M1 testa o inicial de fase
e grade de translação com passo 4 px (82 candidatos); M2 usa ângulos com passo
0,25° e translações zero/anterior (27); M3 usa produto cartesiano dos quatro
coeficientes em (-2,5;-1,25;0;1,25;2,5), translação zero, mais o inicial anterior
(626). Powell refina o melhor custo em raios de 2 px, 0,35° e 0,8 ponto percentual,
respectivamente. Mantém o inicial se o refinamento piorar seu custo. Essas grades
são partes congeladas de um ajuste, não novas tentativas após os resultados.

O ajuste NCC não avalia seu próprio resultado. A referência automática mede
deslocamentos residuais por correlação de fase da luminância nos tiles
reservados, com janela Hann e refinamento parabólico limitado a ±0,5 pixel.
Interpolação de imagem/gradiente é bilinear; máscaras usam vizinho mais próximo
com erosão para garantir o suporte da interpolação. Validade de tile depende
somente de suporte e informação/texture predefinidos, nunca de residual alto.
Todo residual válido, inclusive o máximo, é preservado. Textura insuficiente
ou espectro sem informação não pode ser contado como alinhamento perfeito.
Cada tile exige 100% de suporte: buracos de máscara não são preenchidos nem
usados como sinal de alinhamento. Exigir desvio-padrão ≥0,5 em ambas as imagens,
razão mínima entre autovalores do gradiente da referência ≥0,01 e autocorrelação
periódica distante <0,98, a partir de defasagem de um quarto do lado. Esses
controles de informação são anteriores à medida de erro e podem bloquear a
tentativa por cobertura insuficiente; nenhum alto residual é descartado.

Exigir em **cada instante** ≥8 tiles válidos e os quatro quadrantes; exigir
também suporte válido pós-transformação ≥90% dos pixels elegíveis da máscara
fixa de referência. Os pixels excluídos por texto/borda/crominância não entram
nesse denominador, que é declarado no resultado. Não se alega 90% do canvas.
Mediana ≤1 px, P95 ≤2 px e máximo ≤3 px são exigidos por instante e no conjunto,
em desenvolvimento e validação. Determinante linear positivo e roundtrip ≤0,25
px são controles numéricos; não constituem evidência de precisão experimental.

Antes dos quartis, cada candidato aprovado é gravado em arquivo exclusivo
`<par>-freeze.json`, com matriz e métricas de desenvolvimento. Só o par com
candidato e lacre positivo pode abrir seus quatro buffers de validação.
Não há retorno à estimação, troca de classe, ajuste ou nova leitura após essa
abertura. Ausência de lacre permite apenas candidato de desenvolvimento.

## Resultados, limites e fechamento

Ambos os pares validados: PASS/G2_FRAG=PASS. Apenas um validado:
PARTIAL_ONE_CONDITION/G2_FRAG=PARTIAL, sem comparação entre condições.
Candidato sem validação lacrada: PARTIAL_DEVELOPMENT_ONLY/NOT_VALIDATED.
Sem candidato, sem referência, falha da hierarquia, da validação, de ativos,
escopo ou interrupção: respectivo BLOCKED definido na decisão. Nenhum estado
autoriza refinamento automático. G2_SOLUTE=NOT_EXECUTED e TI3_PLUS_AUTHORIZED=false.

Suporte comum é a interseção de máscaras válidas dos instantes avaliados.
Bounding box desse suporte não equivale a ROI retangular integralmente válida;
ROI permanece nula se não certificada. Suportes de desenvolvimento e validação
são reportados separadamente e não implicam ROI conjunta entre condições.
A referência automática não é ground truth metrológico: ambiguidade, textura
repetida, artefatos e censura por máscaras limitam suas alegações. PASS é limitado
aos pares, frames, critérios e envelope congelados; não certifica todos os
frames, orientação física, escala, eventos, TI-2 histórica ou G3.

Testes anteriores aos dados usam somente fixtures sintéticas: quatro classes,
mascaramento, reflexão, ordem/parada, referência degenerada, independência de
regiões, lacre, allowlist, zero ESM2/ESM5, autoridade antes de I/O, receipt único
e consumo definitivo. CI preserva versões e inclui esses contratos no job
científico existente. Testes stdlib declaram os skips opcionais; o job científico
exige execução real sem skips. Nenhuma instalação local.

C3 registra resultado/receipt e fecha `CLOSED_CONSUMED`, atividade NONE,
execução TI2R=false, TI3+=false, merge=false. Seu diff não altera código nem
configuração científica. Só então: guardrails/suítes, árvore limpa, push
fast-forward, Draft PR e CI automática no SHA C3. Sem Ready, merge, rerun ou
correção científica posterior. Checksums históricos são atualizados em C1
apenas para documentos/CI já cobertos; a autoridade e decisão mutáveis desta
fase não pertencem ao manifesto histórico. Os hashes dos textos científicos
congelados constam no receipt, independentemente da autoridade mutável.
