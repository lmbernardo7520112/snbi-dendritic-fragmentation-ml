# TI2R-FRAG-DIRECT — protocolo terminal congelado antes dos pixels

Decisão autoral de 2026-09-18; base pós-merge PR #7
`b7bbb6a1f0d3eaa43866027762eb2ed061c3d7c6`, branch
`feat/ti2r-frag-direct-mapping`. A tentativa anterior foi aceita como resultado
bloqueado válido. Seu código, protocolo, configurações, receipt e resultados
permanecem históricos e inalterados. A hipótese identidade foi considerada
fortemente sustentada, ainda não certificada, pelo autor.

## Hipótese, coordenadas e ativos

Somente derivação anotada no mesmo raster, admitindo identidade ou recorte
inteiro compatível com diferenças documentadas de canvas. Origem `(0,0)` no
centro do pixel superior esquerdo; x=coluna e y=linha. Para origem de recorte
`(ox,oy)` na móvel: `referência(x,y) ↔ móvel(x+ox,y+oy)`.
Matriz móvel→referência: `[[1,0,-ox],[0,1,-oy],[0,0,1]]`; inversa com +ox/+oy.
Nenhuma transformação subpixel, rotação, escala, similaridade, afim, projetiva,
não rígida ou estimador ECC. Não há competição entre algoritmos.

| Par | Dimensões referência / móvel | Conjunto integral e exaustivo |
| --- | --- | --- |
| ESM3→ESM1 | 1278×1018 / 1280×1024 | ox=0..2, oy=0..6: 21 |
| ESM6→ESM4 | 1278×1012 / 1280×1012 | ox=0..2, oy=0: 3 |

Dimensão divergente bloqueia antes de ampliar candidatos. Os buffers existentes
são YUV420p de 8 bits e preservam todas as componentes; são decodificações MP4
headerless, não raw do detector. Sem redimensionamento ou nova decodificação.

Desenvolvimento: ESM1/ESM3 em 0,146,293; ESM4/ESM6 em 0,197,394.
Holdout: ESM1/ESM3 em 73,219; ESM4/ESM6 em 98,295. Exatamente 20 ativos.
Os 12 de desenvolvimento já foram observados algoritmicamente; os resultados
anteriores influenciaram a hipótese e o redesenho dos gates por decisão autoral.
O novo registro de exposição preserva esse fato. Os oito holdouts têm atestações
positivas de ausência de análise/uso em desenvolvimento, inclusive no resultado
do PR #7; decodificação e hashing mecânicos prévios não são omitidos. Custódia é
documental delimitada, sem alegação de auditoria universal de acessos externos.

## Partição, máscaras e informação de referência

Parâmetros exatos em `configs/registration/ti2r-frag-direct-method.json`.
Exclusões fixas de 12% superiores, 15% inferiores, borda quatro pixels,
crominância U/V distante ≥20 de 128, halo cinco pixels e erosão um pixel para
Sobel. A regra exclui círculos/halos/textos/timestamps/barra e não os usa como
fiduciais. Não há escolha visual de ROI ou exclusão baseada em erro.

Grade fixa 6×6 na faixa radiográfica restante; paridade das células alterna
seleção e auditoria. Margem interior de 20 pixels separa os papéis, cobrindo
recorte máximo seis pixels, pesquisa residual ±12 e derivadas/interpolação.
Usa-se raster nativo. As imagens não são normalizadas usando pixels do outro
papel espacial. Cada bloco admite máscara parcial e exige quantidade absoluta
mínima de 512 pixels úteis, sem limiar de 100% por tile ou 90% global.

Identificabilidade é calculada **somente na referência**: textura de luminância
com desvio-padrão ≥0,5, tensor de gradiente com razão entre autovalores ≥0,01,
quantidade absoluta de pixels e cobertura de pelo menos oito blocos em cada
papel, distribuídos nos quatro quadrantes. Alterações na móvel, máscaras móveis,
residual ou candidato desejado não alteram IDENTIFIABLE/NON_IDENTIFIABLE.
Falha de informação/suporte móvel num frame identificável é falha de comparação.
Um frame NON_IDENTIFIABLE é inconclusivo, sem PASS e sem evidência de desalinhamento.

## Seleção exaustiva e auditoria independente

Seleção usa somente seus blocos e compara **todos** os 21 ou três offsets.
Em cada bloco, a interseção de suportes de todos os candidatos fixa os mesmos
pixels para comparar offsets. Score: correlação normalizada dos componentes
Sobel, centrados por bloco e agregados com pesos iguais. Score mínimo 0,8 e
margem mínima do melhor contra **todos** os demais ≥0,005, congelados por testes
sintéticos anteriores a C1. Empate ou informação insuficiente não vira identidade.

Métricas espaciais finais usam exclusivamente blocos de auditoria. Residual
local é medido por ZNCC mascarada da luminância, via somas exatas de sobreposição
obtidas por convolução FFT: contagem, somas, energias e produto cruzado para cada
defasagem da grade fixa `dx,dy ∈ [-12,12]`. O zero usado na convolução não é
interpretado como pixel válido; máscaras não viram sinais de alinhamento.
Essa formulação foi escolhida para aceitar máscaras parciais sem o pico artificial
que buracos comuns podem introduzir na correlação de fase ingênua. É métrica
independente local, não novo estimador do mapeamento. Refinamento parabólico,
quando admissível, afeta apenas o residual relatado, nunca o offset inteiro.

Não há descarte por erro alto, trimming ou escolha posterior de blocos.
Todo residual computável é preservado. Blocos com menos de 512 pixels em alguma
defasagem ficam UNAVAILABLE_SUPPORT, registrados sem residual; ainda são exigidos
oito blocos medidos e quatro quadrantes. Correlação indefinida ou pico ambíguo
bloqueia o frame; se houve residual calculável, ele permanece no registro.
O controle de variância nula considera tolerância numérica relativa de 1e-12
nas somas FFT, impedindo que cancelamento numérico em regiões constantes produza
informação fictícia. Falta de suporte/energia e ambiguidade não geram residual
zero artificial. Limiares por instante identificável e
por conjunto: mediana ≤1 px, P95 ≤2 px, máximo ≤3 px. Agregados são exigidos
adicionalmente e não apagam falhas locais ou instantes contraditórios.

## Desenvolvimento, congelamento e holdout

Exigir pelo menos dois dos três instantes de desenvolvimento IDENTIFIABLE,
o mesmo offset único vencedor em todos eles, quatro quadrantes, margem de
unicidade e aprovação integral da auditoria. O instante inicial pode permanecer
NON_IDENTIFIABLE. Nenhum instante identificável pode contrariar o mapeamento.

O candidato aprovado é gravado uma vez em `<par>-freeze.json` antes de abrir
os quatro ativos de holdout daquele par. A seleção dos dois pares termina antes
da primeira abertura de holdout. Falha de um par não muda o método do outro.
Holdout usa os mesmos candidatos, máscaras, scores e limiares para confirmar o
offset congelado; nunca o substitui. Sua auditoria mede sempre sob o offset
congelado, mesmo quando o ranking revela um vencedor contraditório e bloqueante.
Exigir ao menos um de dois instantes
IDENTIFIABLE e aprovação em todos os identificáveis. Sem retorno ao desenvolvimento.
Trata-se de **validação temporal interna à mesma aquisição**, não validação
experimental externa nem ground truth metrológico. Orientação física, escala,
eventos e validade em frames não examinados ficam fora das alegações.

## Autoridade, testes e parada definitiva

Autoridade nova: `configs/authority/ti2r-frag-direct.json`, independente da
autorização consumida. O validador exige fechamento TI-2 e FRAG antes de aceitar
DIRECT. C1 congela protocolo/configuração/código/testes/exposição com estado
PREPARED_INACTIVE, RED reais preservados e contratos verdes somente sintéticos.
C2 altera exclusivamente autoridade e decisão para ACTIVE_ONE_SHOT.

Runner novo, exatamente uma invocação. Antes de qualquer byte experimental:
validar autoridade, C2/base/branch/árvore limpa, diff C1→C2 restrito, textos iguais
a C1; criar receipt com O_EXCL/fsync, SHA C2, 12 hashes congelados, 20 ativos,
exposição e contador 1. Nenhum path de ativo é normalizado/examinado antes da
guarda. Travessia por descritores/O_NOFOLLOW, tamanho/hash do manifesto e abertura
única por ID. Recibo preexistente impede retry. ZIP/MP4/ESM2/ESM5 e fontes
alternativas não são opções de recuperação.

Testes cobrem os offsets finitos, unicidade, máscaras parciais, controles negativos
(constante, periódico, móvel sem informação, conteúdo independente), erro local
alto preservado, separação espacial, identificabilidade independente da móvel,
contradição temporal, holdout contrário, dimensões, autoridade antes de I/O,
receipt único e consumo. Usar somente dependências existentes; CI mantém pins.

C3 registra evidências/resultado e CLOSED_CONSUMED, atividade NONE, TI2R=false,
TI3+=false e merge=false. Nenhum código/parâmetro muda depois de C2. Interrupção
consome a tentativa e não permite nova execução. Só após C3: testes/guardrails,
push fast-forward, Draft PR e CI automática. Sem Ready, merge ou remediação.

Dois pares certificados: PASS, G2_FRAG=PASS_DIRECT_RASTER_MAPPING e
G2_SPATIAL=PARTIAL_PENDING_G2_SOLUTE. Um: PARTIAL_ONE_PAIR. Nenhum mapeamento
único estável: BLOCKED_DIRECT_MAPPING. Referência insuficiente:
BLOCKED_REFERENCE_STILL_INSUFFICIENT. Dimensões divergentes:
BLOCKED_DIMENSION_DIVERGENCE. Sempre G2_SOLUTE=NOT_EXECUTED e
G3=BLOCKED_OR_PENDING_G2_COMPLETE. Nenhum resultado autoriza TI-3+.

Após PARTIAL/BLOCKED, nenhuma nova tentativa automática para o par não aprovado.
Alternativas futuras limitadas a coordenadas originais das anotações, referência
manual independente com protocolo próprio, nova anotação, nova aquisição ou
abandono justificado; todas dependem de nova decisão, não são implementadas aqui.
