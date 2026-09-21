# Study2-A — protocolo anterior à sequência integral

Autoridade: AUTHORIZATION.md e a exceção administrativa estreita em
DECODER_GATE_AUTHORIZATION.md. Base Git: f36e43407f0e630d84f5e2d9306699b796b5ad2a;
branch feat/study2a-dense-annotation-ledger. Estudo 1 permanece imutável.
Esta fase reconstrói metadados das anotações cumulativas publicadas. Não é
experimento de acurácia, treinamento ou validação física de fragmentação.

## Portas de execução

1. Testes sintéticos; custódia do A0 e das fontes textuais históricas.
2. Uma compatibilidade histórica: somente ESM3 0/73/146/219/293 e
   ESM6 0/98/197/295/394 chegam ao detector. A decodificação interna de
   intermediários está explicitamente autorizada; eles não chegam ao Python,
   não são analisados, visualizados ou salvos. Divergência encerra a tarefa.
3. Commit de freeze, filho direto da base, depois do gate e testes aprovados.
4. Push e sete jobs CI SUCCESS no SHA exato, incluindo todos os passos.
5. Preflight textual; receipt exclusivo e durável; uma passagem integral de
   ESM3 0..293 e ESM6 0..394. Nenhum retry científico, inclusive falha parcial.
6. Somente evidências posteriores, checkpoint documental e CI final; STOP.

Receipt ou resultado pré-existente impede armar nova execução. Autoridades
históricas não são reativadas. A presença de terminal-state.json encerra a nova
autoridade. O preflight não abre fontes. A execução não possui caminho de
revisão humana ou saída gráfica. Nenhum conteúdo de ESM1/2/4/5 é aberto.

## Detector congelado e compatibilidade

Reutilização direta de src/snbi_fragmentation/ti3_a0_annotations.py, cujo
SHA-256 é 89e4dd58cab51bcd4ed2c607e2abc14d11a2f44f5c5e827fa4e58917539619e7.
Parâmetros: chroma_distance=20; minimum_component_pixels=32;
minimum_radius=8.0; maximum_radius=16.0; maximum_axis_ratio=1.2;
maximum_radial_p95=4.0; minimum_angular_coverage=0.9. Conectividade 8,
expansão de cada amostra cromática em bloco nativo 2×2, ajuste A0 inalterado.
Y é transportado no frame nativo, mas não influencia decisão de marcador.

O gate exige os dez hashes nativos históricos, todas as contagens, componentes,
classificações, áreas, bboxes e razões idênticas. Diferença euclidiana máxima
permitida nos centros VALID: 1e-9 px, somente tolerância numérica, sem tuning.
Totais obrigatórios: 108 VALID, 380 AMBIGUOUS, 3 SMALL. Nenhum RAW histórico é
reaberto. A0, núcleo novo, runner e configuração são autenticados no gate;
o preflight integral recusa mudanças posteriores nesses textos.

## Identidades e estados temporais

Um site pertence a uma única fonte/aquisição. Seu centro canônico é o centro
da primeira observação DIRECT_VALID, nunca atualizado. Associação: distância
euclidiana <=2.0 px e correspondência única recíproca entre componente e site.
Todos os sites anteriores são mantidos. Candidato compatível com mais de um
site, dois candidatos compatíveis com um site, ou candidato novo a <=2 px de
outro VALID contemporâneo geram CONFLICT, sem desempate pelo mais próximo.
Nenhum site nasce desse conflito. Site afetado perde permanentemente AUTO_GOLD.
ID: SHA-256 da representação determinística de fonte, primeiro frame,
primeiro componente e centro canônico. Não há drift transitivo.

Componentes ambíguos preservam todos os campos A0. Proximidade por bbox é
diagnóstico, nunca suficiente para AUTO_SILVER. Para sustentar um site anterior,
o componente AMBIGUOUS deve conter **todos os pixels cromáticos da sua primeira
observação direta**. A mesma máscara A0 (20, conectividade 8) fornece footprints
em memória; IDs, áreas e bboxes são conferidos com A0. Não há novo ajuste,
limiar, dilatação ou busca. Só footprints das âncoras válidas persistem entre
frames; pixels não são exportados. Hash e quantidade da âncora documentam a
proveniência. Esta regra conservadora pode perder suporte após pequenas
mudanças gráficas; ela não autoriza mover âncora ou relaxar o predicado.

Suporte completo em componente ambíguo produz TEMPORAL_SUPPORTED_AMBIGUOUS e
AUTO_SILVER_OBSERVATION; múltiplas âncoras no mesmo componente são mantidas,
com OVERLAP_WITH_KNOWN_TRACKS. Isso não cria o eventual novo site desconhecido.
Bbox sem suporte completo permanece evidência de proximidade e hipótese não
resolvida. SMALL nunca sustenta silver. Não se infere NON_SITE_GRAPHICAL_AMBIGUITY.
Nenhuma rejeição vira negativo. TEMPORAL_DELTA=NOT_EXECUTED; HOUGH=NOT_EXECUTED.

Estados site×frame: DIRECT_VALID; TEMPORAL_SUPPORTED_AMBIGUOUS;
PERSISTENCE_EXPECTED_UNRESOLVED; PRE_FIRST_CONFIDENT_ANNOTATION; CONFLICT;
INVALID_FRAME. Persistência esperada não é positivo. Cada site possui um
registro para cada frame contabilizado da própria fonte, inclusive retrospecto
anterior à descoberta. AUTO_GOLD exige observação direta, identidade sem conflito,
âncora e proveniência completas; não significa evento físico validado.

## Primeira confiança e tempo

FIRST_CONFIDENT_ANNOTATION_FRAME é a primeira DIRECT_VALID. Quando há frame
anterior processado com colored_pixel_count=0 e nenhum componente, o último
deles fornece LAST_CONFIDENT_MARKER_ABSENCE_FRAME. Trata-se exclusivamente de
ausência de tinta sob o critério cromático congelado, não ausência física de
fragmentação nem negativo ML. Na falta dessa evidência, o limite inferior é
null/NOT_ESTABLISHED. Intervalo documental (última ausência, primeira presença];
nenhum onset físico. PRE_FIRST não certifica ausência de todos os seus frames.
Tempo experimental ESM3=-25,96+1,18i; ESM6=-34,22+1,18i, aritmética inteira
em centésimos antes da apresentação. 5 fps é reprodução.

## I/O, armazenamento e falhas

Só os dois MP4 exatos da autorização. SHA ESM3:
d76a6466e50480a2116bc545a0ee2b8095cc14c54f861ecebee87de5b64e35be;
ESM6: 5b8747758afde34fb626f3c4ffbd0b49ba6ca6f6b49bfa81b8cf9ee8459280ea.
Ambos autenticados antes de qualquer decoder. Leitura sem symlinks por FDs;
identidade/tamanho/mtime/ctime reconferidos. FFmpeg recebe FD autenticado,
um processo por fonte, YUV420P nativo, sem autorotate, resize ou fps conversion.
EOF e contagem exata obrigatórios. Timeout por fonte: 3600 s, incluindo pausas
do consumidor; stderr limitado a 65536 bytes. Sem ZIP de fallback.

Limite conservador de transporte: até três payloads nativos simultâneos na
transição produtor/consumidor; exclui máscaras/labels e metadados do detector.
Uma janela temporal de análise, sem retenção de frames inteiros anteriores.
Sem arquivos temporários de pixels, PNGs, patches ou cache: zero bytes.
Reserva >=53687091200 bytes; temporários <=268435456; patch cache<=2147483648.
Dois JSONL agregados locais ignorados em data/derived/study2, orçamento combinado
268435456 bytes, com manifesto de path/size/SHA-256/record_count no Git.
Metadados compactos de frames/sites/resumos são textos versionados.

I/O instrumentado distingue opens/bytes de autenticação comprimida, solicitações
de abertura de decoder, frames/bytes emitidos e processados. Leituras comprimidas
internas do FFmpeg e intermediários internos não são monitorados; não inventar
contagem universal de syscalls. Pico RSS Python registrado separadamente do
decoder. Qualquer falha termina sem pular ou repetir frames. Frames restantes
recebem INTEGRITY_FAILED/NOT_ADMITTED_AFTER_TERMINAL_PIPELINE_FAILURE, com
processed=false e distinção explícita de tentativa de decode não certificada;
não são apresentados como frames decodificados ou negativos.

## Legado, unidades e sucesso

Cada uma das 108 observações antigas deve mapear por ID original a um único
track; todas de um site antigo devem concordar e sites antigos diferentes não
podem colapsar. Publicar todos os 52 IDs e eventuais divergências. Gate de promoção
congelado: 52/52 mapeados; falha preserva o corpus produzido como BLOCKED.
Mapeamento por observações antigas e elegibilidade AUTO_GOLD final são distintos.

Contar separadamente: aquisições (aproximadamente duas), sites, sites AUTO_GOLD,
componentes VALID do detector, observações diretas com identidade única,
AUTO_SILVER, componentes ambíguos, pequenos, registros site×frame, PRE_FIRST,
persistência esperada, conflitos de site×frame e de candidatos sem identidade.
Distribuições: contagem direta por site, primeira confiança e intervalos,
transições de suporte para desaparecimento gráfico não resolvido.

PASS exige execução integral, proveniência/custódia, 689 frames processados,
identidades consistentes, 52/52 mapeados, limites e resultados preservados.
Não há mínimo de sites, accuracy ou comparação de modelos. Mais observações
não aumentam o número de experimentos independentes. Não há inventário físico
exaustivo, onset exato, forecasting, causalidade ou generalização externa.
Study2-B, revisão humana futura e merge permanecem não autorizados.
