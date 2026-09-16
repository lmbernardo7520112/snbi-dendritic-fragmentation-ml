# TI-2 — Registro de riscos

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
