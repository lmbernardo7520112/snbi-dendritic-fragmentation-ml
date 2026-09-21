# Study2-A integrado; Study2-B — corpus multimodal denso concluído

**STUDY2_A_INTEGRATION=PASS; STUDY2_B=PASS.** A única construção contabilizou todos os **27.396 registros**: **16.500 pares válidos** e **10.896 INVALID_BOTH**, sem substituições. Foram preservados quatro tiers, com 5.218 GOLD, 3.687 SILVER e 7.595 não rotulados válidos. O pool contém 70.844 candidatos a background, somente metadados. ML_RUNS=0; autoridade científica CLOSED_CONSUMED.

## Retorno dos 33 itens autorais

| Item | Evidência e resultado |
| --- | --- |
| 1. Study2-A PR/merge | [PR #16](https://github.com/lmbernardo7520112/snbi-dendritic-fragmentation-ml/pull/16), Draft → CI verde → Ready → merge commit; branch preservada |
| 2. Merge SHA | d4ef00bf1e1d84d49d4e3f2dce0d18f683598a4c |
| 3. CI pós-merge | Sete jobs e79stepsSUCCESS; respostas em INTEGRATION_AUDIT.json |
| 4. Branch | feat/study2b-dense-multimodal-corpus, criada no merge exato após fast-forward de main |
| 5. Source hashes | ESM1/2/4/5 autenticados integralmente antes de cada passagem; quatro hashes exatos abaixo; ESM3/6 não abertos |
| 6. Schema | STUDY2_B_CORPUS_SCHEMA.json; uint8,65×65,canal0estrutural/canal1solutalrelativo; centro canônico fixo; quatro tiers |
| 7. Background | Contrato congelado, grid65, união global dos87sites, footprints/bboxes, suporte e tracks persistentes; sem balanceamento |
| 8. Storage | HYBRID_STREAM_LEDGER_SELECTIVE_CACHE; container agregado memory-mappable, sem header; cap2GiB,temporários256MiB,reserva50GiB |
| 9. Legacy gate | 50/50fixturesPASS;25/25overlaps canônicos; dez hashes de frames históricos iguais; uma invocação anterior ao freeze |
| 10. Freeze SHA | 06ea5467d495a6a531a48a622a92b31e050e037a;32paths;41textos autenticados |
| 11. CI pré-execução | Sete workflows,oito jobs,90stepsSUCCESS no SHA exato; CI_PROOF.json |
| 12. Comando | PYTHONPATH=src .venv/bin/python -B scripts/run_study2b.py full; uma invocação,exit 0,retries0 |
| 13. Opens/bytes | Full:4opensPython de autenticação,4requestsdecoder;108.466.048bytes comprimidos autenticados;1.378frames/2.680.088.688bytes nativos; fronteiras abaixo |
| 14. Contabilização | 27.396entradas=27.396linhas de índice, cada identidade uma vez |
| 15. Pares válidos | 16.500; cobertura60,22777047744197% |
| 16. Inválidos | 10.896INVALID_BOTH;0invalid-onlyestrutural/solutal;0DECODE_ERROR; sem padding/resize/shift/replacement |
| 17. GOLD | 7.941entradas;5.218válidos;2.723GOLD_INVALID_SUPPORT |
| 18. SILVER | 5.737entradas;3.687válidos;2.050inválidos; sem promoção de tier |
| 19. Não rotulados | PRE:8.911→5.181válidos;PERSISTENCE:4.807→2.414;totalválido7.595; nenhum convertido em negativo/background |
| 20. Sites | 87contabilizados;52com pares válidos e trajetória completa;35sem suporte válido |
| 21. Background candidatos | 70.844registros frame×location, metadados apenas |
| 22. Background tracks | 223identidades espaciais por aquisição |
| 23. Future-positive | União global dos87sites antes de filtro de suporte, inclusive regiões futuras/pré-anotação e sites inválidos |
| 24. Ambiguity | Todas24.246AMBIGUOUS+292SMALL excluídas conforme bboxes; sete métricas canônicas, sem usar o agregado histórico mal nomeado para decidir pool |
| 25. Container | 139.425.000bytes;16.500×2×65×65uint8;SHA completo abaixo |
| 26. Índice | 69.620.377bytes;27.396registros;SHA completo abaixo |
| 27. Storage/free | Total de 259.036.080 bytes;TEMP_PEAK_BYTES=0;freefinal 666.263.302.144 bytes;PEAK_RSS Python410.376KiB |
| 28. Human review | false; sem inspeção visual de fontes, patches ou correção humana de labels |
| 29. ML | ML_RUNS=0; sem fit, scoring, LBP/features ou comparação de modelos; testes científicos anteriores não reexecutados localmente |
| 30. Evidence checkpoint | Exclusivamente novos textos desta pasta; SHA efetivo informado após commit no retorno ao operador |
| 31. CI final | Conferência no SHA documental após push; sucesso não antecipado por este documento |
| 32. Git state | Método/fonte científica preservados; arrays/ledgers grandes ignorados; academic-deliverable-build/ preexistente preservado; estado após checkpoint informado no retorno |
| 33. Terminal | PASS;CLOSED_CONSUMED;STUDY2_C_AUTHORIZED=false;MERGE_AUTHORIZED=false;NONE_AWAITING_AUTHOR_DECISION |

## Integração e congelamento

Study2-A foi conferido no head7c192478554ea139752feaaff8cb2d44ff6747f7: reconciliação aditiva de dois textos,freeze35/35,pós-hashes34/34 e dois JSONLs locais intactos. O merge preservou parents f36e43407f0e630d84f5e2d9306699b796b5ad2a/7c192478554ea139752feaaff8cb2d44ff6747f7 e árvore 3a4a488fb20fe3a244931bc012c2e8f539eec45e idêntica ao head. As provas de PR e pós-merge estão em INTEGRATION_AUDIT.json.

A extensão de escopo adicionou sete paths Python e preservou os 119anteriores, modos e blobs:75 LEGACY + 4 A0 + 47 ativos = 126,zero não classificados ou duplicados. Esse manifesto é o único arquivo pré-existente alterado. Checkers, workflows anteriores,95 checksums históricos e ciência A/Estudo 1 permaneceram intactos. Não houve nova instalação local.

Os testes finais cobrem100 casos sintéticos únicos:35 núcleo, 25 streaming, 40 execução. O perfil conjunto anterior executou99 PASS; o wrapper esperava 97 e retornouexit 1 apesar dos99 resultados PASS. O relatório original e log foram preservados, e a contagem foi reconciliada por IDs. A revisão estática posterior detectou que o manifesto textual do piloto obrigatório não era admitido pelo leitor. Antes do gate histórico, somente esse caminho exato foi acrescentado; a suíte afetada executou 40 PASS, zero skips/falhas/erros. Não se afirma uma execução local conjunta de100 casos. A CI do freeze executou o perfil final sem skips. Nenhum teste usa vídeo real ou modelo ML.

O gate histórico exigia decodificar intermediários internamente. A decisão suplementar DECODER_GATE_AUTHORIZATION.md autorizou somente esse procedimento, entregando ao código ESM1/2:73,146,219 e ESM4/5:98,197. Os intermediários não foram entregues, analisados, visualizados ou salvos; sua quantidade interna não foi instrumentada. Dez hashes nativos e todos os 50 pares de patches históricos coincidiram. Os 25 backgrounds históricos foram somente fixtures transitórios de compatibilidade; não alimentaram o pool novo. Os contadores LEGACY_PATCH_PAIRS_EXPECTED/MATCHED/HASH_MATCHES=25 referem-se somente aos overlaps site/frame/centro.

Após esse gate, código, configuração e contratos conservaram seus dez hashes de implementação. METHOD_FREEZE.json autentica 41 textos. O freeze é filho direto do merge. Os oito jobs / 90 steps reais terminaram com SUCCESS; o último terminou às 16:16:58 UTC, antes do receipt científico às 2026-09-21T16:18:04.248111+00:00. O preflight real confirmou SHA, 41 hashes, CI, reserva e ausência de outputs; foi repetido internamente antes do receipt exclusivo O_EXCL+fsync. Nenhuma mudança ou reparo ocorreu após o freeze ou os pixels inéditos.

## Construção e I/O

Comando científico único, no sandbox padrão, exit 0:

```text
PYTHONPATH=src .venv/bin/python -B scripts/run_study2b.py full
```

Somente ESM1/2/4/5 foram abertos. Antes de iniciar qualquer decoder em cada passagem, os quatro MP4 completos foram autenticados contra os hashes autorais:

| Fonte | SHA-256 |
| --- | --- |
| ESM1 | 4d07ee422e97661b1ee0ae681b7617fd7971476015603f3039c20ddf8b0c5c6d |
| ESM2 | 4eb1762dc4ee65c3e8b1411d80812a75257b1324d539db4c3dcf6c97c1ed9a0a |
| ESM4 | 9e6be3e78699d3bdd16fa71d56917479d7e16f7418b857ab3925e1115df91ebe |
| ESM5 | c9054d18f330e018e82cc6bd4db2ccfbda7ac76e01326a831857a835d1feade6 |

| Fronteira | Gate histórico | Construção integral | Soma das duas passagens |
| --- | ---: | ---: | ---: |
| OpensPython de autenticação |4|4|8|
| Bytes comprimidos autenticados |108466048|108466048|216932096|
| Requests de abertura de input pelo decoder |4|4|8|
| Frames nativos entregues ao código |10|1378|1388|
| Bytes nativos recebidos/entregues |19469052|2680088688|2699557740|

Na construção, ESM1/2 têm294 frames cada;ESM4/5,395 cada. São 689 pares temporais. Todos os decoders terminaram exit 0 e os descritores foram fechados. O hash de cada frame foi calculado em memória durante sua passagem. Nenhuma fonte foi reaberta depois para auditoria. Bytes comprimidos lidos internamente pelo FFmpeg são NOT_INSTRUMENTED, distintos da autenticação Python e dos bytes nativos. Os números acima não são contagem universal de syscalls.

Os campos source_auth_bytes_read/source_auth_compressed_bytes_read são aliases, não somáveis. frames_written=0 e patches_written=0 em IO_AUDIT.json pertencem ao leitor streaming: ele não exporta imagens. O escritor do corpus persistiu 16.500 pares, ou 33.000 patches de canal, comprovados por CORPUS_CONTAINER_BYTES e LOCAL_ARTIFACT_MANIFEST.json. IO_ACCOUNTING.json explicita essa distinção sem reescrever a evidência original.

O reader mantém no máximo dois decoders do mesmo par simultaneamente. A janela declarada de seis payloads nativos é limite conservador do leitor e não inclui arrays/máscaras do controlador nem memória interna FFmpeg. PEAK_RSS 410.376 KiB cobre somente Python; não é pico total da árvore de processos. MAX_TEMP_BYTES limita temporários em disco, que foram zero. Não houve exportação de full frames, PNG/JPEG, features, modelos ou um arquivo por patch.

## Corpus, exclusões e grupos

Os 87 sites e 27.396 estados vieram exclusivamente do ledger A congelado. O centro canônico é fixo em todos os frames; arredondamento ao mais próximo com empate para cima, slice [y−32:y+33,x−32:x+33],sem resize ou offsets novos. Os mappings históricos G2 foram consumidos documentalmente, sem registro novo. As modalidades preservam a identidade temporal e raster; canal 0 Y estrutural, canal 1 Y campo solutal relativo. A projeção de chroma serve apenas ao suporte estrutural histórico e nunca a features ou labels.

Os quatro tiers permanecem separados. Todos os inválidos têm row_index e hashes de patch/par nulos; os hashes/proveniência de fonte/frame permanecem documentados. GOLD inválido é GOLD_INVALID_SUPPORT, jamais substituído. As 35 identidades sem suporte não foram removidas do inventário. A auditoria de coordenadas textuais localizou os 35 sites excluídos fora da geometria histórica: 10 no limite superior, 22 no inferior, dois no esquerdo e um no direito. Isso explica a exclusão constante em ambas as modalidades sem reinspecionar chroma. Na aquisição bottom_up, 40 de 69 sites têm trajetória válida; na top_down, 12 de 18. Dos 52 sites válidos, 33 coincidem com identidades legadas e 19 são novos; outros 19 legados ficaram inválidos. A contagem 52 não representa repetição do conjunto legado.

GROUP_ID=acquisition_id|site_id é constante. site_observation_count considera todos os registros daquele site; site_supervised_observation_count usa GOLD + SILVER históricos antes da admissão. candidate_equal_site_weight=1/esse denominador é somente metadado prospectivo, não um peso aplicado a modelo.

A ordem congelada é acquisition_id,frame_index,site_id,supervision_tier, compatível com streaming e contiguidade. GOLD_VIEW tem 5.218 rows; GOLD_PLUS_SILVER_VIEW 8.905; UNLABELED_VIEW 7.595; FULL_LONGITUDINAL_VIEW 16.500. Todas referenciam o mesmo payload sem duplicação de pixels. Nenhum split foi escolhido.

O pool utiliza centros (32+65k, 32+65j), suporte integral do patch expandido 3 px nas duas modalidades e interseção literal incluindo contato. A união global inclui todos os 87 sites por aquisição, antes de filtro de suporte, inclusive sites reconhecidos futuramente e sites que acabaram inválidos. Footprints conhecidos usam bboxes VALID; todas as 24.246 AMBIGUOUS e 292 SMALL são exclusões temporais, mesmo quando explicadas por sites conhecidos. Não se usa o agregado histórico potential_new_site_unresolved_components para decidir background. Os sete nomes reconciliados permanecem intactos.

BACKGROUND_TRACK_ID=acquisition_id|x|y persiste entre frames. O rank SHA-256 textual é determinístico, não feature. Distâncias são relativas a envelopes documentais, não a fragmentos físicos. O pool não contém patches de luminância, quotas, amostragem por intensidade/textura ou balanceamento. Um futuro split deve preservar grupos de sites e tracks completos, mas esta construção não certifica independência nem resolve a política de amostragem.

## Armazenamento, custódia e limites

O formato HEADERLESS_C_CONTIGUOUS_UINT8 equivale a um array memory-mappable de shape (16500, 2, 65, 65), offset 0, 8.450 bytes/row. Evita reescrever header ou criar temporário quando o número admissível só é conhecido após o suporte. O manifesto contém dtype,shape,ordem,contagem e hashes. Views são apenas índices.

| Arquivo local ignorado | Bytes | Registros | SHA-256 |
| --- | ---: | ---: | --- |
| data/derived/study2b/multimodal_patches_uint8.bin | 139425000 | 16500 | 3957ba2480805fa108c216e500238f1b0fcf39520cfddd0d7d722d65f773b914 |
| data/derived/study2b/corpus-index.jsonl | 69620377 | 27396 | ae322dca1b81c93628d012898d152ca0bfe79f84d0f0284cf82ff22d09977edc |
| data/derived/study2b/background-pool.jsonl | 49990703 | 70844 | 7b92837a152415d10769a79a5224dee02ffb68331bfff8ced60463f8d1b52dd3 |

Os 139.425.000 bytes de pixels ficam abaixo de 2 GiB. Os 119.611.080 bytes dos dois ledgers ficam abaixo do budget adicional de 256 MiB. Total de 259.036.080 bytes; temporários zero; reserva final 666.263.302.144 bytes, acima de 50 GiB. Os hashes do container e dos ledgers foram calculados durante append, com flush/fsync final. O container não foi reaberto para recomputar hash, visualizar ou extrair features. A auditoria pós-run usa somente textos, aritmética e Git; tamanho do container pode ser conferido por stat.

QUALITY_REPORT.md preserva as coberturas reais e os denominadores. POST_RUN_INDEPENDENT_AUDIT.json registra a conferência textual dos registros/views/tracks e seus limites. A documentação é aditiva: resultados,receipts,código,contratos e logs anteriores ficam intactos. Os 41 hashes do freeze e95 checksums históricos continuam verificáveis. Os grandes arquivos locais permanecem ignorados e fora de qualquer staging. Nenhum conteúdo do Estudo 1 ou da entrega acadêmica foi refeito.

PASS significa corpus integralmente contabilizado, provenance e contratos satisfeitos. A cobertura de 60,23% e as exclusões são resultados observados, sem piso de aprovação ou tentativa de aumentá-las. Milhares de registros temporais de duas aquisições não são milhares de réplicas independentes. GOLD/SILVER são níveis automáticos de evidência gráfica publicada, não confirmação física humana; background não prova ausência física. Não há novo onset,forecasting,causalidade,recall físico exaustivo,generalização externa,Bi absoluto ou temperatura. ML_FINAL_TEST do Estudo 1 permanece CONSUMED, sem nova avaliação. Não houve modelo,fit,LBP,CNN,classificação ou tuning nesta construção.

O checkpoint posterior registra somente novos textos. Seu SHA, publicação,CI e estado Git finais pertencem ao retorno efetivo após as operações, sem autorreferência. Nenhum PR/Ready/merge  de Study2-B é iniciado. Receipt e terminal-state encerram permanentemente a autoridade científica; não há retry nem Study2-C automático.

```text
STUDY2_A_INTEGRATION=PASS
STUDY2_B=PASS
STUDY2_B_METHOD=DENSE_MULTIMODAL_LONGITUDINAL_CORPUS
SCIENTIFIC_STUDY2B_RUNS=1
SITE_FRAME_INPUT_RECORDS=27396
SITE_FRAME_ACCOUNTED_RECORDS=27396
VALID_MULTIMODAL_PAIRS=16500
GOLD_VALID_PAIRS=5218
SILVER_VALID_PAIRS=3687
UNLABELED_VALID_PAIRS=7595
INVALID_MULTIMODAL_PAIRS=10896
UNIQUE_SITES_WITH_VALID_PAIRS=52
BACKGROUND_CANDIDATES=70844
BACKGROUND_TRACKS=223
HUMAN_REVIEW_USED=false
ML_RUNS=0
STUDY2_C_READY_FOR_AUTHOR_DECISION=true
STUDY2_C_AUTHORIZED=false
MERGE_AUTHORIZED=false
STATE=CLOSED_CONSUMED
CURRENT_AUTHORIZED_ACTIVITY=NONE_AWAITING_AUTHOR_DECISION
```
