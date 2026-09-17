# TI-2 — Plano executivo de registro e calibração

**Status:** método v1 terminalmente bloqueado; somente TI2-CLOSEOUT-1 autorizada
**Dependências:** G1 PASS, G2-TEMP PASS e TI-1 encerrada  
**Gates-alvo:** G2-SPATIAL e G3  
**Versão:** 1.0.0

A [decisão de closeout](../decisions/AUTHORIZATION-TI2-CLOSEOUT-1-2026-09-17.md)
registra `METHOD_V1=INSUFFICIENT_EVIDENCE`,
`G2_SPATIAL=BLOCKED_METHOD_V1`, `TRANSFORM_EXISTENCE=UNDETERMINED`,
`G3=BLOCKED_DEPENDENCY_G2` e `E7=PASS_DOCUMENTARY`.
A redação prospectiva abaixo preserva a especificação histórica aprovada,
seus 30 frames-piloto identificados por fonte/índice, contratos e limites
quantitativos. Não autoriza TI-2R, novo acesso a pixels ou execução científica.

## 1. Finalidade

A TI-2 deverá estabelecer um referencial espacial reproduzível entre as três modalidades de cada condição experimental, definir regiões de interesse válidas e documentar a conversão entre pixels e dimensão física, quando houver fonte primária suficiente.

O resultado esperado não é um dataset de aprendizado de máquina. É uma camada de calibração que permita, em fases posteriores, transferir localizações das anotações cumulativas para as radiografias limpas sem alterar a geometria ou a orientação física do experimento.

## 2. Perguntas bloqueantes

1. A diferença dimensional entre as modalidades decorre de borda, *padding*, recorte, translação, rotação ou mudança de escala?
2. Uma transformação espacial única por condição/modalidade permanece válida ao longo do tempo?
3. Qual região possui suporte válido comum às três modalidades?
4. Existe fonte rastreável para a escala espacial em `µm/pixel`?
5. Qual incerteza deve acompanhar transformações, ROI, escala e futuras coordenadas de eventos?

## 3. Entradas congeladas

| Condição | Fonte | Modalidade | Dimensões | Frames |
|---|---|---|---:|---:|
| bottom-up / anti-paralela | ESM1 | radiografia limpa | 1278×1018 | 294 |
| bottom-up / anti-paralela | ESM2 | soluto relativo | 1278×1018 | 294 |
| bottom-up / anti-paralela | ESM3 | anotação cumulativa | 1280×1024 | 294 |
| top-down / paralela | ESM4 | radiografia limpa | 1278×1012 | 395 |
| top-down / paralela | ESM5 | soluto relativo | 1278×1012 | 395 |
| top-down / paralela | ESM6 | anotação cumulativa | 1280×1012 | 395 |

Os hashes de G0, a semântica de G1 e a correspondência por índice de G2-TEMP
permanecem normativos. No closeout, o autor reconciliou duas grandezas:
`elapsed_from_first_frame_s = 1,18 × i`; e
`experimental_time_s = offset + 1,18 × i`, com offset de −25,96 s para ESM1–3
e −34,22 s para ESM4–6. O zero experimental é a entrada da frente de
solidificação no campo de visão (`time_model_status=DOCUMENTED_AND_RECONCILED`).
Os 5 fps continuam sendo apenas cadência de reprodução. O campo histórico
`physical_time_s` representava o tempo decorrido e está depreciado por
ambiguidade; a reconciliação não muda índices ou bytes experimentais.

O autor forneceu também a escala nominal documentada X/Y de 1,40 µm/pixel,
citando Gibbs et al., *JOM* 68, 170–177 (2016),
[DOI 10.1007/s11837-015-1646-7](https://doi.org/10.1007/s11837-015-1646-7).
A fonte não foi consultada novamente neste closeout. A verificação raster
500/357 = 1,40056022409 µm/pixel é compatível com o nominal; seu intervalo
[1,38888888889; 1,41242937853] não é intervalo estatístico de confiança.
A incerteza metrológica completa permanece `UNRESOLVED`, sem conversão de
coordenadas ou transferência de escala a modalidades sem registro certificado.

## 4. Convenções espaciais

- origem nativa: canto superior esquerdo;
- `x`: coluna, crescente para a direita;
- `y`: linha, crescente para baixo;
- coordenadas de pixels referem-se aos centros dos pixels;
- a radiografia limpa será o referencial canônico de cada condição;
- cada transformação será representada por matriz homogênea 3×3, com transformação inversa registrada;
- nenhuma operação poderá sobrescrever o frame nativo;
- direção de gravidade, gradiente térmico e direção de crescimento serão metadados obrigatórios e não poderão ser alterados silenciosamente.

## 5. Amostragem-piloto proposta

Após autorização de execução, e somente então, será permitida uma extração-piloto limitada, determinística e cega aos eventos. Para uma sequência com `N` frames:

\[
S(N)=\left\{0,\left\lfloor\frac{N-1}{4}\right\rfloor,
\left\lfloor\frac{N-1}{2}\right\rfloor,
\left\lfloor\frac{3(N-1)}{4}\right\rfloor,N-1\right\}.
\]

| Grupo | Índices congelados | Fontes | Total de imagens-piloto |
|---|---|---|---:|
| ESM1–3 | 0, 73, 146, 219, 293 | 3 modalidades | 15 |
| ESM4–6 | 0, 98, 197, 295, 394 | 3 modalidades | 15 |

O teto histórico foi de 30 frames-piloto decodificados dos MP4 sem perdas
adicionais, preservando resolução e formato de pixels nativos dos vídeos.
Os buffers `.raw` sem cabeçalho não são dados brutos do detector. Os derivados
ficam ignorados pelo Git, acompanhados de hashes e *lineage*. Não há busca
manual por frames “favoráveis” nem nova decodificação autorizada no closeout.

Para estimar transformações serão usados os índices inicial, central e final. Os dois quartis serão reservados para validação espacial, sem reajuste.

## 6. Sequência de execução futura

### TI2-E0 — Preflight e RED

- revalidar hashes de G0;
- verificar versões das ferramentas;
- materializar testes sintéticos inicialmente falhos;
- confirmar ausência de imagens derivadas anteriores;
- emitir relatório de escopo antes de decodificar qualquer frame.

### TI2-E1 — Decodificação-piloto controlada

- decodificar somente os 30 frames/itens previstos, identificados por fonte e índice;
- preservar resolução, profundidade/canais e formato de pixels nativos dos MP4,
  armazenando os frames decodificados sem perdas adicionais;
- registrar fonte, índice, tempo físico, codec, dimensões, hash e comando;
- proibir correção de contraste, CLAHE, *resize* ou recorte nesta etapa.

### TI2-E2 — Auditoria geométrica

- identificar bordas, *padding*, overlays e suporte válido;
- testar se as diferenças dimensionais são explicadas por recortes inteiros;
- verificar orientação e paridade dos eixos;
- documentar qualquer indício de transformação dependente do tempo.

### TI2-E3 — Estimação hierárquica do registro

A busca obedecerá à seguinte ordem, parando na solução mais simples que satisfaça os critérios:

1. identidade;
2. remoção determinística de borda ou *padding*;
3. translação inteira;
4. translação subpixel;
5. transformação rígida: translação e rotação;
6. similaridade: rígida mais escala uniforme;
7. afim, somente mediante evidência geométrica explícita.

Transformações projetivas e não rígidas ficam proibidas. Qualquer necessidade dessas classes exige mudança de escopo e nova autorização.

O registro ESM3/6 → radiografia deverá excluir das métricas os pixels do overlay de anotação sem converter círculos em labels. Para ESM2/5, métricas robustas a contraste, bordas e informação mútua deverão complementar a inspeção geométrica.

### TI2-E4 — Validação independente

- congelar os parâmetros após os três frames de estimação;
- aplicá-los sem reajuste aos dois frames de validação;
- medir resíduos em marcos ou bordas independentes;
- executar revisão visual documentada pelo autor;
- bloquear o gate se houver deriva temporal incompatível com transformação estática.

### TI2-E5 — ROI canônica

Definir, separadamente para cada condição, a maior região retangular constante com suporte válido nas três modalidades após transformação. Não será imposta igualdade artificial de ROI entre os dois experimentos.

Cada ROI deverá registrar:

- coordenadas no referencial canônico;
- transformação de retorno ao frame nativo;
- orientação física;
- pixels excluídos e justificativa;
- estabilidade nos cinco instantes-piloto.

### TI2-E6 — Escala e incerteza

A escala espacial seguirá a hierarquia de evidência:

1. metadado original de aquisição ou documentação da linha de luz;
2. declaração explícita em artigo ou suplemento;
3. barra de escala cuja geometria e unidade possam ser auditadas;
4. dimensão experimental primária documentada.

Nenhuma escala será inferida a partir da aparência das dendritas. Sem fonte
suficiente, as coordenadas permanecerão em pixels, `scale_status` será
`UNRESOLVED` e G3 não poderá receber PASS integral. No closeout, distinguir
`SPATIAL_SCALE_NOMINAL_STATUS=DOCUMENTED` de
`METROLOGICAL_UNCERTAINTY_STATUS=UNRESOLVED`: a declaração nominal não certifica
registro, ROI ou incerteza e não libera conversões.

A incerteza deverá incluir, quando aplicável:

- incerteza da escala;
- resíduo do registro;
- variação temporal dos parâmetros;
- discretização de pixels;
- sensibilidade aos limites da ROI.

### TI2-E7 — Evidência e decisão

Produzir relatórios imutáveis de G2-SPATIAL e G3, checksums, ambiente, matriz de contratos e decisão `PASS`, `PARTIAL` ou `BLOCKED`. Nenhum avanço para TI-3 será implícito.

## 7. Critérios quantitativos propostos

Os limiares abaixo serão congelados antes da execução:

| Métrica | Aceitação proposta |
|---|---:|
| erro mediano de registro na validação | ≤ 1,0 pixel |
| percentil 95 do erro de registro | ≤ 2,0 pixels |
| erro máximo de marco validado | ≤ 3,0 pixels |
| erro de ida e volta `T⁻¹(T(p))` | ≤ 0,25 pixel |
| suporte válido dentro da ROI | 100% nas modalidades e frames-piloto |
| alteração de orientação física | 0 ocorrências |
| frames-piloto fora da lista congelada | 0 |

O não atendimento não autoriza afrouxar limiares retrospectivamente. O resultado deverá ser `PARTIAL` ou `BLOCKED`, ou uma alteração protocolar deverá ser aprovada antes de nova execução.

## 8. Artefatos futuros previstos

- `configs/registration/*.json`: matrizes, inversas e convenções;
- `configs/calibration/*.json`: ROI, escala, unidades e incertezas;
- `artifacts/metadata/ti2-pilot-manifest.json`;
- `artifacts/evidence/G2_SPATIAL/registration-report.json`;
- `artifacts/evidence/G3/calibration-report.json`;
- figuras diagnósticas de sobreposição, exclusivamente como evidência;
- relatório de testes RED/GREEN e checksums.

Os frames-piloto e binários experimentais não serão versionados no Git.

## 9. Fora de escopo

- extração massiva;
- detecção ou diferença de círculos;
- ledger de eventos;
- labels positivos, negativos ou ambíguos;
- segmentação de dendritas;
- definição de janelas temporais, blocos ou splits;
- baseline, CNN, treinamento ou *hyperparameter tuning*;
- acesso a teste selado;
- quantificação absoluta de Bi a partir de ESM2/5;
- comparação causal entre condições com `n=1`.

## 10. Critério de encerramento da TI-2

A TI-2 somente poderá ser encerrada se:

1. todos os contratos bloqueantes possuírem evidência;
2. G2-SPATIAL e G3 tiverem decisão formal;
3. limitações e incertezas estiverem explícitas;
4. nenhuma atividade TI-3+ tiver sido executada;
5. o autor aprovar o encerramento e, separadamente, eventual planejamento da TI-3.
