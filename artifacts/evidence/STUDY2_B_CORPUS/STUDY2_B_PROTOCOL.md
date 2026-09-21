# Study2-B — protocolo de corpus longitudinal multimodal

## Autoridade e pergunta

A decisão [AUTHORIZATION.md](AUTHORIZATION.md), SHA-256
`51795aef0a7494ee076f04174eea55b54170a77e358d427682b49570de974cfe`,
autoriza a integração A e uma construção B. PR16 integrado por merge commit
`d4ef00bf1e1d84d49d4e3f2dce0d18f683598a4c`, árvore idêntica ao head A,
com sete jobs pós-merge aprovados. A branch B nasce exatamente desse merge.
Questão: podemos transformar o ledger A em corpus longitudinal pareado,
consistente, rastreável e adequado a benchmarks futuros? Nenhum score ML
participa desta fase. Experimento 1 e Study2-A permanecem imutáveis.

## Entradas e transformações fixas

Somente ESM1/2/4/5, nos paths exatos definidos no leitor, são admitidos.
ESM1/2 têm 1278×1018 e 294 frames; ESM4/5, 1278×1012 e 395 frames.
Todos são YUV420p nativo de oito bits. Os quatro hashes integrais são
verificados antes de iniciar qualquer decoder. Os descritores autenticados
são retidos; symlinks, mudança de identidade/tamanho e hash divergente bloqueiam.
G2_FRAG [0,0] e G2_SOLUTE [0,0] são históricos; não se estima nova matriz,
offset espacial/temporal, registro ou alinhamento. Pares têm o mesmo índice.
Tempo experimental: ESM1/2 `−25,96 + 1,18*i`; ESM4/5 `−34,22 + 1,18*i`,
preservando os tempos documentais do ledger.

SITE_LEDGER, OBSERVATION_LEDGER e candidate-components A são entradas
imutáveis, autenticadas contra Git e manifesto. ESM3/6 não são reabertos.
O JSONL de observações usa `status`; a projeção B registra esse estado e o
tier derivado, sem alterar o original. A reconciliação fornece exclusivamente
os sete nomes canônicos. Todos os 27396 registros de 87 sites são contabilizados.

Cada centro é `canonical_center_xy_px` do site A, arredondado uma única vez
por `floor(v+0.5)`. O centro float original também é preservado. Todas as
observações desse site usam o mesmo crop half-open
`[y-32:y+33,x-32:x+33]`, sem jitter, padding, resize, recorte assimétrico,
deslocamento, substituição ou exclusão por aparência.

## Representação, tiers e grupos

Cada par válido contém dois planos 65×65 uint8: canal0 STRUCTURAL_Y;
canal1 RELATIVE_SOLUTE_FIELD_Y. Nenhuma normalização float persistida, LBP,
feature de modelo ou treinamento. A cor solutal não é máscara de overlay.

| Estado A | Tier B | Registros de entrada |
| --- | --- | ---: |
| DIRECT_VALID | GOLD | 7941 |
| TEMPORAL_SUPPORTED_AMBIGUOUS | SILVER | 5737 |
| PRE_FIRST_CONFIDENT_ANNOTATION | UNLABELED_PRE | 8911 |
| PERSISTENCE_EXPECTED_UNRESOLVED | UNLABELED_PERSISTENCE | 4807 |

GROUP_ID é `acquisition_id|site_id`; site inteiro deve permanecer em um split
futuro. Esta fase não cria split. `site_observation_count` e
`candidate_equal_site_weight` são metadados prospectivos; o denominador do
peso é o número histórico de GOLD+SILVER por site, antes do filtro de suporte.
Não são pesos aplicados. UNLABELED não significa negativo ou background;
SILVER nunca é promovido.

Ordem alternativa explicitamente congelada para permitir append em streaming:
`acquisition_id,frame_index,site_id,supervision_tier`. É independente da ordem
do filesystem. O índice tem uma linha por registro de entrada; `row_index`
é inteiro contíguo apenas para válidos e null para inválidos.

## Suporte e exclusões

Replicam-se somente os predicados numéricos históricos em módulo B próprio.
Estrutural: `max(abs(U−128),abs(V−128))>=20`; expansão nearest2; halo quadrado
11×11; bandas top ceil(12%H), bottom ceil(15%H), borda4; erosão3×3 com borda0.
Solutal: geometria histórica erodida em um pixel, sem exclusão cromática.
Bounds geométricos half-open: ESM1/2 [5,124,1273,864]; ESM4/5 [5,123,1273,859].
Um patch requer suporte integral nas duas modalidades. O código antigo não
é chamado com metadados disfarçados e seus imports ML não são reutilizados.

PAIR_STATUS: VALID_PAIR, INVALID_STRUCTURAL_SUPPORT, INVALID_SOLUTAL_SUPPORT,
INVALID_BOTH ou DECODE_ERROR. Falha de suporte é resultado registrado e não
causa substituição. GOLD inválido recebe razão GOLD_INVALID_SUPPORT.
Erro terminal de fonte/decode encerra I/O sem retry; registros restantes são
contabilizados como DECODE_ERROR com razão explícita de não admissão após
falha, sem fingir que todos foram decodificados. Resultados parciais bloqueiam.

## Gate, freeze e execução

Primeiro, testes sintéticos de todos os contratos e conferência dos inputs
textuais. Depois, uma passagem histórica seleciona apenas ESM1/2:73,146,219
e ESM4/5:98,197. A [exceção de decodificação interna](DECODER_GATE_AUTHORIZATION.md)
nunca entrega intermediários ao código. Os dez hashes nativos e os 50 pares
históricos são comparados, sem LBP/modelo e sem persistir esses patches.
Os 25 backgrounds históricos são fixtures de compatibilidade, não seleção
de background B. O overlap exato com os sites B é esperado em 25 pares;
50 fixtures e 25 overlaps são relatados separadamente. Divergência bloqueia.

O gate também autentica os hashes de implementação/protocolos; eles ficam
inalterados depois dele. METHOD_FREEZE.json registra código, testes, decisões,
contratos, inputs e gate. Um commit filho direto do merge, publicado com CI
verde em oito jobs, antecede qualquer construção integral.

Um receipt exclusivo O_EXCL+fsync é persistido antes de cada passagem de
fontes. A passagem completa única abre quatro streams autenticados e consome
um par da mesma aquisição por vez, com no máximo dois decoders concorrentes.
Nenhum frame completo é exportado. RESULT/terminal/receipt fecham a autorização;
uma segunda invocação é recusada antes de fonte. Não há retry por resultado.

## Saídas e métricas

Corpus, índice e pool em containers locais ignorados. Hashes de cada patch
e par, hash incremental de cada container, proveniência de fonte/frame/site
e row_index acompanham os registros. As quatro views contêm somente índices,
sem duplicar pixels: GOLD, GOLD+SILVER, UNLABELED e FULL_LONGITUDINAL.

Coverage total usa denominador27396; GOLD7941; SILVER5737; UNLABELED13718.
Reportar válidos/inválidos por status/tier/site, sites completos (todos seus
registros válidos), completude dos três hashes e da proveniência, pool/tracks,
storage, temporários e RSS do processo Python. Pico dos decoders não é
instrumentado e não será apresentado como RSS total. Nenhum mínimo de pares
ou accuracy define PASS. PASS exige contabilidade integral, integridade,
suporte/mappings corretos, tiers preservados, budgets e zero ML.

Após a construção: somente evidência, checkpoint documental e CI. Nada de
alterar centros, regras, schema, código ou parâmetros em resposta ao resultado.
Study2-C e merge B permanecem não autorizados.
