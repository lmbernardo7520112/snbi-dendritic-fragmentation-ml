# TI-2 — Registro de riscos

**Status:** `TERMINAL_BLOCKED_CLOSED`; closeout PASS; método v1 com evidência insuficiente.

Estado canônico em `pyproject.toml [tool.snbi]`: `NONE_AWAITING_AUTHOR_DECISION`.
[Remediação PR6](../decisions/AUTHORIZATION-TI2-PR6-REMEDIATION-1-2026-09-17.md) restrita a manutenção/publicação.
A decisão de closeout permanece registro histórico.
A declaração final de riscos aceitos para planejamento é histórica; a
autorização posterior de execução permitiu somente o piloto congelado e não
aceitou automaticamente risco residual. Agora `G2_SPATIAL=BLOCKED_METHOD_V1`,
`TRANSFORM_EXISTENCE=UNDETERMINED`, `G3=BLOCKED_DEPENDENCY_G2` e
`E7=PASS_DOCUMENTARY`. Nenhuma nova análise científica está autorizada.

| ID | Risco | Consequência | Controle preventivo | Resposta de gate |
|---|---|---|---|---|
| R2-01 | diferença de canvas confundida com escala | coordenadas deslocadas | testar crop/padding antes de modelos mais complexos | bloquear transformação inadequada |
| R2-02 | círculos contaminam a métrica de registro | alinhamento atraído pelo overlay | excluir overlay apenas da métrica de registro | não gerar labels |
| R2-03 | contraste do soluto induz falso alinhamento | ESM2/5 mal registrados | combinar geometria, bordas e informação mútua | PARTIAL/BLOCKED por modalidade |
| R2-04 | padrão dendrítico repetitivo cria máximo falso | erro espacial sistemático | marcos independentes e validação em quartis | bloquear se resíduos excederem limites |
| R2-05 | transformação varia no tempo | coordenada única não é válida | estimação em três tempos e validação sem reajuste | exigir regra temporal ou bloquear |
| R2-06 | flip altera gravidade/crescimento | interpretação física invertida | metadados de orientação e guardrail sem flips | BLOCKED imediato |
| R2-07 | escala espacial sem fonte primária | falsa precisão em µm | hierarquia de fontes e fail-closed de unidades | G3 PARTIAL/BLOCKED |
| R2-08 | ROI escolhida após observar eventos | viés de seleção | ROI baseada em suporte geométrico, não fragmentação | invalidar ROI enviesada |
| R2-09 | extração-piloto expande silenciosamente | antecipação de TI-3/TI-4 | allowlist exata de 30 imagens | BLOCKED imediato |
| R2-10 | interpolação altera intensidades | perda de informação quantitativa | preservar nativos; declarar interpolador nas cópias | bloquear uso quantitativo não validado |
| R2-11 | limiar relaxado após resultado | adaptação retrospectiva | congelar critérios antes da execução | change control obrigatório |
| R2-12 | dados derivados entram no Git | quebra de custódia/licença | `.gitignore`, auditor de binários e hashes externos | bloquear commit |
| R2-13 | registro é interpretado como ground truth | alegação científica indevida | gate de claims | impedir avanço documental |
| R2-14 | escala comum é forçada entre experimentos | comparação física inválida | calibração separada por condição | G3 não aprovado |

## Riscos residuais aceitos para planejamento

Nenhum risco experimental foi aceito nesta fase, pois nenhuma operação sobre pixels foi autorizada. O presente documento apenas predefine controles para uma futura execução.

## Evidência da execução autorizada de 17/09/2026

Os resultados científicos G2-SPATIAL/G3 permanecem bloqueados, agora com a
classificação terminal aprovada pelo autor no closeout, conforme
`artifacts/evidence/TI2/terminal-state.json`. O texto de planejamento acima é
histórico; os seguintes riscos não foram aceitos nem corrigidos retroativamente:

- A máscara de borda excluiu 20/35 centros da grade congelada, deixando até 15
  candidatos para o mínimo de 12 correspondências. O método não comprovou
  registro estático nos três instantes; isso não demonstra impossibilidade
  geométrica. Uma revisão metodológica exige decisão autoral antes de execução.
- Gravidade, gradiente térmico e crescimento permanecem `NOT_VERIFIED` no
  referencial dos pixels. Preservar paridade nativa não preenche essa lacuna.
- Sem transformação aceita, não há ROI comum certificada nem validação
  independente. Os quartis foram decodificados e verificados por hash, mas
  permanecem sem análise de pixels.
- A barra horizontal de 500 µm/357 px fornece verificação raster compatível com
  a escala nominal X/Y de 1,40 µm/pixel documentada pelo autor. A incerteza
  metrológica completa continua `UNRESOLVED`; o intervalo raster não é
  intervalo de confiança. Nenhuma coordenada é convertida nem escala propagada
  a modalidade sem registro certificado.
- A diferença entre os textos temporais e `i × 1,18 s` foi reconciliada
  documentalmente pelo autor: a primeira grandeza é tempo experimental relativo
  à entrada da frente no campo de visão, com offsets −25,96 s para ESM1–3 e
  −34,22 s para ESM4–6; a segunda é tempo decorrido desde o primeiro frame.
  `time_model_status=DOCUMENTED_AND_RECONCILED`, sem nova inspeção de pixels,
  reindexação ou seleção de frames. A fonte indicada é Gibbs et al., *JOM* 68,
  170–177 (2016), DOI 10.1007/s11837-015-1646-7; foi fornecida pelo autor e não
  consultada novamente pelo agente.

A preservação da fonte, os 30 itens e os limites TI-3+ permanecem controlados.
Os riscos detalhados e suas evidências estão no relatório de execução.
