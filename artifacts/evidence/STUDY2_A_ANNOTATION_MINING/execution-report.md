# Study2-A — reconstrução integral das anotações cumulativas

**STUDY2_A=PASS.** Uma execução científica reconstruiu **87 sites AUTO_GOLD**
e **27.396 registros site×frame**, processando os **689 frames** ESM3/ESM6.
Foram preservadas 7.941 observações diretas, 5.737 AUTO_SILVER e todas as
ambiguidades. Os 52 sites históricos mapearam integralmente; há 35 sites
adicionais ao legado. Nenhum modelo, patch, Hough ou revisão visual foi usado.
A autoridade está CLOSED_CONSUMED; Study2-B não foi iniciado.

## Retorno dos 29 itens autorais

| Item | Resultado comprovado |
| --- | --- |
| 1. Branch/base | feat/study2a-dense-annotation-ledger; base f36e43407f0e630d84f5e2d9306699b796b5ad2a; main sincronizada por fast-forward antes da nova branch |
| 2. Hashes das fontes | ESM3 d76a6466e50480a2116bc545a0ee2b8095cc14c54f861ecebee87de5b64e35be; ESM6 5b8747758afde34fb626f3c4ffbd0b49ba6ca6f6b49bfa81b8cf9ee8459280ea; ambos autenticados antes de qualquer decoder em cada fase |
| 3. Detector | A0 original direto: chroma20; componente32; raio8–16; razão de eixos1,2; erro radialP95≤4; cobertura angular≥0,9; persistência canônica≤2px; nenhum parâmetro alterado |
| 4. Reprodução histórica | PASS; dez hashes nativos idênticos;108VALID/380AMBIGUOUS/3SMALL; máximo desvio de centro6,821210263296962e-13px, abaixo de1e-9 |
| 5. Freeze | 7d89329bf005f6a85ddc67d51d88b9e362878478; filho direto da base;28paths;35hashes textuais |
| 6. CI anterior à ciência | Seis runs, sete jobs e79passos SUCCESS no SHA exato; último job14:38:12UTC; CI_PROOF.json |
| 7. Comando integral | PYTHONPATH=src .venv/bin/python -B scripts/run_study2a.py --run; uma invocação, exit0, zero retry |
| 8. Frames | 294ESM3+395ESM6=689 PROCESSED; zero DECODE_FAILED/INTEGRITY_FAILED e nenhuma lacuna |
| 9. I/O integral | Dois opens de autenticação/7.709.238bytes comprimidos; duas solicitações de entrada do decoder;689frames/1.345.528.320bytes nativos entregues; categorias distintas |
| 10. Sites únicos | 87 AUTO_GOLD:69ESM3/18ESM6; nenhuma identidade conflitante |
| 11. Diretas | 7.941:5.035ESM3/2.906ESM6; também7.941componentes VALID nesta execução |
| 12. Suporte temporal | 5.737 AUTO_SILVER:4.660ESM3/1.077ESM6; regra de inclusão integral da tinta da âncora |
| 13. Ambiguidade | 24.246componentes AMBIGUOUS e292SMALL preservados, sem negativos automáticos |
| 14. Conflitos | Zero registros site×frame CONFLICT e zero componentes VALID com identidade conflitante |
| 15. Legado | 52/52, injetivo,38ESM3/14ESM6;108observações originais conferidas individualmente, nenhuma excluída |
| 16. Sites adicionais | 35:31ESM3/4ESM6; não chamados eventos físicos novos |
| 17. Distribuição temporal | 1–253diretas/site ESM3;7–309ESM6; distribuição integral em CORPUS_SUMMARY.json;8.911PRE_FIRST/4.807persistências não resolvidas |
| 18. Primeira confiança | 87brackets documentais; limite inferior29ESM3/61ESM6; larguras1,18–305,62s e11,80–251,34s; não onset físico |
| 19. Sobreposição conhecida | 5.576componentes ambíguos com suporte:5.415a uma âncora e161a duas; geram5.737silver |
| 20. Não resolvidos | 18.962componentes classificados POTENTIAL_NEW_SITE_UNRESOLVED; todos24.538não válidos conservam hipótese de tinta/site adicional;195transições de suporte para persistência não resolvida |
| 21. Corpus armazenado | Dois JSONL locais ignorados:27.396observações/17.786.087bytes e32.479candidatos/49.636.870bytes; manifesto textual versionado |
| 22. Orçamentos | 67.422.957bytes agregados<268.435.456; temporários/cache de patches=0; reserva observada666.552.229.888bytes>53.687.091.200; Python RSS243.760KiB |
| 23. Revisão humana | HUMAN_REVIEW_USED=false; nenhuma inspeção visual dos frames, correção manual ou edição de centros |
| 24. Hough | NOT_EXECUTED; temporal delta também não executado |
| 25. Claims | Corpus longitudinal automatizado de localizações cumulativas publicadas;≈2aquisições; sem inventário físico exaustivo, onset, forecasting, causalidade ou validação externa |
| 26. Checkpoint de evidências | Exclusivamente textual após a ciência; SHA efetivo pertence ao Git e retorno final ao operador, sem autorreferência |
| 27. CI final | Conferida no checkpoint após sua publicação e informada no retorno efetivo; este documento não antecipa o resultado remoto |
| 28. Git | Freeze/código intactos; somente evidências novas após a ciência; academic-deliverable-build/ anterior preservado. Estado final local/remoto será reconfirmado após checkpoint |
| 29. Terminal | PASS; CLOSED_CONSUMED; STUDY2_B_READY_FOR_AUTHOR_DECISION=true; STUDY2_B_AUTHORIZED=false; MERGE_AUTHORIZED=false |

## Preparação, freeze e sequência real

O anexo foi preservado em [AUTHORIZATION.md](AUTHORIZATION.md). O autor permitiu
separadamente apenas a decodificação interna de intermediários necessária ao
gate dos dez frames, sem entregá-los ao detector, visualizar ou salvá-los;
[DECODER_GATE_AUTHORIZATION.md](DECODER_GATE_AUTHORIZATION.md) contém a resposta
exata. Esse gate precede a mineração integral e não conta como um segundo
full run. Nenhum buffer RAW antigo foi reaberto.

A0 foi reutilizado sem alterações. O novo protocolo separa o reader, o tracker
e a admissão/receipt; todos os módulos novos pertencem exclusivamente ao
Study2-A. O único arquivo anterior editado é phase-scope-v1.json: sete entradas
acrescentadas, conservando os112Python anteriores, seus modos/blobs e as75+4
fronteiras históricas. Nenhum checker, workflow anterior, checksum, configuração
ou ciência TI3-A/B/C/D foi alterado. O checksum histórico passou95/95.

Antes de qualquer vídeo, revisão independente detectou que bbox sozinha não
sustentava AUTO_SILVER. A regra foi fixada em inclusão completa do footprint
cromático da primeira DIRECT_VALID, sem translação ou threshold adicional.
Também foram implementados brackets baseados em frames globalmente sem tinta.
Essas decisões ocorreram antes do gate histórico, não após observar resultados.
As correções finais de escrita/reserva e fechamento após receipt também
precederam qualquer acesso. Nenhum código mudou depois do gate ou do freeze.

Perfil sintético final: **98PASS, zero skips/falhas/erros** —39tracker,
19streaming,22execução e18A0 históricos. Um perfil anterior de94PASS foi
preservado; a repetição decorreu de quatro testes adicionais e das correções
concretas anteriores ao gate. A regressão stdlib executou782testes,
638passes/144skips opcionais, zero falhas/erros, antes desses quatro testes
adicionais. As22verificações finais de execução passaram posteriormente;
a CI real também executou a regressão descoberta no commit. Suítes delegadas
e falhas de fixtures preparatórias estão separadas no inventário de comandos.
Nenhum fit sintético ou científico de ML foi realizado.

O gate legado recebeu10frames/19.545.600bytes nativos e passou. C1 publicou
35hashes e o protocolo, antecedendo os seis runs verdes:
[35613301780](https://github.com/lmbernardo7520112/snbi-dendritic-fragmentation-ml/actions/runs/35613301780),
[35613301986](https://github.com/lmbernardo7520112/snbi-dendritic-fragmentation-ml/actions/runs/35613301986),
[35613301302](https://github.com/lmbernardo7520112/snbi-dendritic-fragmentation-ml/actions/runs/35613301302),
[35613301801](https://github.com/lmbernardo7520112/snbi-dendritic-fragmentation-ml/actions/runs/35613301801),
[35613302381](https://github.com/lmbernardo7520112/snbi-dendritic-fragmentation-ml/actions/runs/35613302381) e
[35613301627](https://github.com/lmbernardo7520112/snbi-dendritic-fragmentation-ml/actions/runs/35613301627).

ACTUAL_PREFLIGHT.json passou com Git/blobs reais, sete jobs e zero novas
aberturas, sem armar. O runner repetiu internamente a admissão, gravou receipt
exclusivo O_EXCL+fsync às **2026-09-21T14:40:11.859567+00:00** e só então abriu
as duas fontes. O receipt e os resultados impedem nova execução. Não houve
reinício por falha parcial ou resultado insatisfatório.

## I/O e resultados preservados

| Categoria | Gate histórico | Full run | Total desta tarefa |
| --- | ---: | ---: | ---: |
| Opens Python de autenticação | 2 | 2 | 4 |
| Bytes comprimidos autenticados | 7.709.238 | 7.709.238 | 15.418.476 |
| Launches / solicitações de entrada do decoder | 2 | 2 | 4 |
| Frames entregues ao detector | 10 | 689 | 699 |
| Bytes nativos entregues | 19.545.600 | 1.345.528.320 | 1.365.073.920 |

A cobertura única é689; os dez históricos aparecem nas duas fases. No full
run, ESM3 emitiu578.027.520bytes e ESM6,767.500.800. EOFs e quantidades exatas,
hashes, metadados antes/depois, stderr vazio, exit0 e fechamento dos FDs foram
registrados. Os dez hashes reobservados na sequência integral também coincidem
com o legado. Não houve ZIP, fallback, fonte externa, FFprobe, ESM1/2/4/5,
exportação de frames ou inspeção visual.

Os bytes lidos internamente pelo FFmpeg e a quantidade de intermediários do
codec não foram instrumentados. Os contadores acima não são syscalls universais;
bytes comprimidos autenticados e payload nativo não devem ser somados como
tráfego físico de disco. O transporte admite até três payloads durante o repasse
ao consumidor, sem reter frames anteriores completos. Máscaras do detector,
footprints esparsos das âncoras e metadados residem em memória. Pico Python:
243.760KiB (238,046875MiB); pico do decoder não medido. Cache de patches e
temporários de pixels em disco: zero.

[LOCAL_ARTIFACT_MANIFEST.json](LOCAL_ARTIFACT_MANIFEST.json) autentica os dois
containers ignorados. Seus SHA-256 são:

- OBSERVATION_LEDGER.jsonl: `3cb444271839b1fca18c3228f91e961e9566173e3036696db3dadf537234bfcc`;
- candidate-components.jsonl: `b9e4ce16c967e4ffc6f6f2b1e86e21727971a444c20a38667cc1b53ae9ceb19c`.

Frames, sites, mapa legado, resultados e resumos são textos compactos no Git.
Nenhum pixel de footprint foi exportado. A auditoria posterior confere hashes,
contagens, IDs, tempos, vínculos de componentes, áreas/bboxes e registros de
suporte; não recalcula a inclusão de pixels nem reabre vídeos. O agente
principal também conferiu as108observações contra os membros originais dos52
sites históricos. [VERIFICATION_TERMINAL.json](VERIFICATION_TERMINAL.json)
declara os limites das revisões assistidas por IA.

## Interpretação e encerramento

[QUALITY_REPORT.md](QUALITY_REPORT.md) e [QUALITY_DETAILS.json](QUALITY_DETAILS.json)
separam unidades, distribuições, sobreposições e incertezas. O aumento de10para689
frames,108para7.941observações diretas e52para87sites mostra a informação
adicional recuperada sob o protocolo; não aumenta o número de aquisições.
Não há medida de accuracy ou garantia de recuperação exaustiva. Rejeições e
limitações do detector A0 foram preservadas, inclusive as radiais históricas.

AUTO_GOLD representa evidência gráfica e identidade rastreável, não evento
físico validado. Os intervalos de primeira confiança são documentais e podem
ser largos. Componentes ambíguos, inclusive os explicados por tinta conhecida,
podem conter hipótese adicional não resolvida. Os estados de persistência não
foram propagados como positivos. Círculo não é máscara/extensão de fragmento;
não se infere onset, inventário completo, forecasting, causalidade ou validação
externa. ESM2/5 não participaram e continuam significando campo solutal relativo.

Somente evidência textual foi produzida após a ciência. Estudo1, FINAL consumido
e entrega acadêmica G4 permanecem preservados. Não houve instalação, alteração
de sistema, credencial, PR, merge, exclusão de branch, tuning ou segundo run.
O commit documental e sua CI são publicados conforme a autorização; seus
identificadores efetivos constam no retorno final ao operador.

```text
STUDY2_A=PASS
STUDY2_A_METHOD=FULL_SEQUENCE_TEMPORAL_ANNOTATION_MINING
SCIENTIFIC_STUDY2A_RUNS=1
ANNOTATION_FRAMES_EXPECTED=689
ANNOTATION_FRAMES_PROCESSED=689
UNIQUE_AUTO_GOLD_SITES=87
DIRECT_VALID_OBSERVATIONS=7941
AUTO_SILVER_OBSERVATIONS=5737
AMBIGUOUS_OBSERVATIONS=24246
SITE_FRAME_RECORDS=27396
CONFLICT_RECORDS=0
LEGACY_SITES_EXPECTED=52
LEGACY_SITES_MAPPED=52
HUMAN_REVIEW_USED=false
HOUGH_EXECUTED=false
ESM1_OPENS=0
ESM2_OPENS=0
ESM4_OPENS=0
ESM5_OPENS=0
PATCHES_CREATED=0
ML_RUNS=0
STUDY2_B_READY_FOR_AUTHOR_DECISION=true
STUDY2_B_AUTHORIZED=false
MERGE_AUTHORIZED=false
STATE=CLOSED_CONSUMED
CURRENT_AUTHORIZED_ACTIVITY=NONE_AWAITING_AUTHOR_DECISION
```
