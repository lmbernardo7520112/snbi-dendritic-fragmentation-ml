# TI3-A — bloqueio metodológico antes do dataset e do baseline

**TI3_A=BLOCKED_METHOD_PRECONDITIONS.** A fase 0 foi concluída. A auditoria
documental da fase 1 não encontrou um contrato verificável para converter as
anotações cumulativas em targets ML, nem premissas suficientes para congelar
o split. Nenhum pixel foi aberto e nenhum treinamento foi iniciado.

A condição do [anexo autoral](authorization.md) determina: “Se houver bloqueio
metodológico: não improvisar workaround; não abrir FINAL_TEST; não alterar
ciência anterior; registrar bloqueio; STOP.” Este registro aplica essa condição.
O bloqueio não decorre das antigas permissões TI3=false: a decisão nova
autoriza TI3-A no seu escopo, mas não supre os pré-requisitos metodológicos
que ela própria exige. Não há conclusão científica de baseline.

## Baseline, branch e preservação

- Repositório: lmbernardo7520112/snbi-dendritic-fragmentation-ml.
- Branch: `feat/ti3-canonical-dataset-baseline`.
- HEAD e origem da branch: `67786bd4e23406e7f19860a53fe237e6d7b648cb`.
- `main == origin/main == HEAD` após fetch exato e fast-forward.
- Branch TI2R anterior preservada em `893cbb8e9e5cdc5a8422081304ec4189000b8a42`.
- Os 25 textos científicos congelados foram comparados por SHA-256 com
  o manifesto repair-1 e os blobs de C1/C2: todos byte-idênticos.
- Nenhum conteúdo versionado foi alterado em relação à baseline integrada.
  Apenas os seis novos textos deste diretório registram a parada.
- Não houve commit, push, PR, merge novo, exclusão de branch, instalação,
  alteração do sistema ou acesso a credenciais. A sincronização local foi
  fast-forward do merge já integrado, sem criar outro merge commit.

A CI pós-merge da baseline
[35413304435](https://github.com/lmbernardo7520112/snbi-dendritic-fragmentation-ml/actions/runs/35413304435)
foi verificada com SUCCESS na tarefa de integração precedente; ela não foi
reconsultada nem apresentada como CI dos novos textos TI3-A.

## Inventário documental do domínio

Estas informações vêm exclusivamente de textos versionados, não de nova
inspeção de fontes ou buffers:

| Fontes | Papel | Dimensões nativas documentadas | Frames na fonte |
| --- | --- | --- | ---: |
| ESM1 / ESM2 | radiografia / campo solutal relativo | 1278 × 1018 | 294 por fonte |
| ESM3 | anotação cumulativa de localização de fragmentação | 1280 × 1024 | 294 |
| ESM4 / ESM5 | radiografia / campo solutal relativo | 1278 × 1012 | 395 por fonte |
| ESM6 | anotação cumulativa de localização de fragmentação | 1280 × 1012 | 395 |

Proveniência: [manifesto de fontes](../../../configs/sources/source_manifest.json)
e [metadados de aquisição](../../metadata/acquisition_metadata.json).
ESM1–3 pertencem à condição bottom_up_anti_parallel; ESM4–6 a
top_down_parallel. ESM2/ESM5 não são concentração absoluta de Bi.

O [manifesto piloto](../../metadata/ti2-pilot-manifest.json) contém 30 buffers:
cinco instantes por condição, em três modalidades. Índices ESM1–3:
0/73/146/219/293; ESM4–6: 0/98/197/295/394. Isso representa dez grupos de
instantes correspondentes, não 30 amostras ML independentes. Os números
294/395 descrevem os vídeos inventariados; não significam frames extraídos
ou samples rotulados disponíveis nesta tarefa.

O incremento normativo é 1,18 s, com índices desde zero. Tempo decorrido:
1,18 × i. Tempo experimental: −25,96 + 1,18 × i para ESM1–3 e
−34,22 + 1,18 × i para ESM4–6. Os 5 fps de reprodução não definem tempo
experimental; `physical_time_s` histórico é alias depreciado de tempo decorrido.
Nenhum horizonte de previsão, janela de entrada ou embargo deriva
automaticamente dessa cadência.

[G2_FRAG](../TI2R_FRAG_DIRECT/execution-report.md) certificou mapeamento raster
identidade no protocolo/piloto. [G2_SOLUTE](../TI2R_SOLUTE_HOLDOUT/repair-1/execution-report.md)
passou o holdout temporal interno com os critérios V2 congelados.
Isso não certifica labels ML, ROI, calibração física ou generalização externa.
As matrizes/inversas/ROI nulas do adaptador SOLUTE não foram preenchidas.

## Bloqueios e evidência

**B1 — contrato do target não comprovado.**
O manifesto de fontes descreve ESM3/ESM6 como anotações cumulativas de
localização. Não foi encontrado nos textos auditados um schema de targets ML
validado, inventário de eventos individuais, regra de primeira aparição,
tratamento de persistência, negativos, ambiguidade ou horizonte preditivo.
O contrato ANN-201 da
[matriz TI2](../../../docs/protocols/TI2_CONTRACT_MATRIX.md) explicita que
círculo não é máscara de fragmento. O relatório FRAG-DIRECT declara que
não produziu labels, ledger ou dataset.

Portanto, `WHAT_IS_ONE_SAMPLE`, `TARGET` e tarefa ML permanecem
`NOT_VERIFIED`. A hierarquia aquisição → instante → modalidades é uma
unidade de proveniência, não uma escolha de sample de treinamento.
Controles positivos/negativos de registro não são classes de fragmentação.
Não se afirma inexistência absoluta de labels fora do escopo documental:
arquivos experimentais, fontes externas e diretórios vizinhos não foram
inspecionados.

**B2 — hipótese do split não resolvida.**
O [protocolo V2](../../../docs/protocols/TI2R_SOLUTE_V2_PROTOCOL.md) declara
aquisição como unidade experimental, aproximadamente uma corrida por condição.
O manifesto piloto usa dois experiment_id correspondentes às condições;
aquisições independentes adicionais são `NOT_VERIFIED`.
Com dois grupos não se obtêm três partições não vazias disjuntas por aquisição.
Uma avaliação temporal interna pode ser considerada em decisão posterior,
mas requer target, persistência do evento, janela, horizonte e embargo
justificados. Não seria avaliação externa entre aquisições.

Os riscos já identificados incluem vizinhos temporais, patches/augmentations
do mesmo original, modalidades e versões registradas do mesmo instante,
anotações cumulativas que revelem futuro, target presente no input, campo
solutal do evento avaliado e metadados que codifiquem condição/label.
Não foram escolhidos grupos, seed, exclusões, métricas ou parâmetros para
contornar esses riscos.

**B3 — FINAL_TEST ainda não existe como partição congelada.**
Não foram definidos IDs TRAIN/DEVELOPMENT/FINAL_TEST. Nenhum ativo foi
atribuído ao teste final, aberto ou avaliado. O estado correto é
`FINAL_TEST=NOT_DEFINED_NOT_OPENED`, e não SEALED de um manifesto inexistente.
O holdout histórico SOLUTE continua CONSUMED. A exposição histórica combinada
dos pilotos em FRAG-DIRECT e SOLUTE impede chamá-los de globalmente virgens;
isso não é, por si só, uma prova de impossibilidade de qualquer teste interno
futuro, cuja finalidade e limitações precisariam ser explicitadas.

## Resultado por entrega solicitada

| Entrega | Estado desta tarefa |
| --- | --- |
| Branch e baseline de origem | PASS; SHA exato acima |
| WHAT_IS_ONE_SAMPLE | NOT_VERIFIED; não definido arbitrariamente |
| Inputs | potenciais ESM1/4 estruturais e ESM2/5 relativos; nenhum tensor carregado |
| Target e frames com labels ML validados | NOT_VERIFIED |
| Samples ML e distribuição de labels | NOT_VERIFIED; zero samples materializados |
| Distribuição documental | dois grupos; cinco instantes piloto por grupo; três modalidades |
| Dataset manifesto / exclusões | NOT_CREATED; nenhuma exclusão por desempenho |
| Split / IDs / seed / hashes de split | NOT_DEFINED |
| Política anti-leakage | riscos documentados; protocolo e guards não congelados |
| Métricas | NOT_FROZEN; dependem da tarefa real |
| Matriz curricular / COURSE_ALIGNMENT.md | NOT_REACHED por parada na fase 1 |
| Técnicas A4/A5 aceitas ou rejeitadas para TI3 | NOT_DELIBERATED; nenhuma introduzida |
| LBP + RF | NOT_DELIBERATED_BLOCKED_TARGET; incompatibilidade não demonstrada |
| Baseline / parâmetros | NOT_SELECTED |
| Runs técnicos de ML | 0; verificações textuais não são smoke tests de ML |
| Runs científicos de baseline | 0 |
| Resultados TRAIN/DEV | NOT_EVALUATED |
| FINAL_TEST | NOT_DEFINED_NOT_OPENED; acessos e bytes experimentais = 0 |
| Testes de baseline | NOT_RUN |
| CI TI3-A | NOT_RUN; nenhuma publicação iniciada |
| Index / worktree | index intacto; seis arquivos novos e não staged na allowlist |
| Próxima fase | TI3_B_READY_FOR_AUTHOR_DECISION=false; TI3_B_AUTHORIZED=false |

A deliberação curricular dependia da tarefa real e não foi simulada para
preencher um checklist. Nenhuma técnica foi imposta por constar em A4/A5.
NGF e SS8 permanecem intactos; não houve benchmark retrospectivo.
SS8 não é declarado implementação exata de MIND ou MIND-SSC.

## Verificações, arquivos e limites do registro

O guard de dados passou com 277 entradas examinadas e zero bytes de conteúdo.
A inspeção do índice não encontrou symlinks versionados. A custódia textual
dos 25 arquivos está em [verification.json](verification.json). Não houve
importação de kernels científicos, FFmpeg/FFprobe, abertura de imagens,
recálculo de resultados ou execução de qualquer runner científico.

Arquivos criados, exclusivamente neste diretório:

- authorization.md
- execution-report.md
- results.json
- commands.json
- environment.json
- verification.json

O relatório de ambiente limita-se ao runtime efetivamente observado.
Não foram instaladas ou inspecionadas dependências de ML. O inventário de
comandos discrimina sandbox e aprovações Git pontuais, além do escopo e das
lacunas declaradas do registro do auditor independente. A verificação final
dos novos JSON e do estado Git será comunicada no retorno ao operador.

## Decisão necessária para retomar

É necessário estabelecer o target científico e um protocolo validável de
conversão das anotações cumulativas: significado de um evento, localização
versus extensão espacial, instante de referência, persistência, negativos e
ambiguidade. Esses elementos devem sustentar unidade amostral, contexto de
entrada e horizonte. Também é necessário delimitar o objetivo do teste
interno ou entre aquisições, seus grupos e separação temporal; se a avaliação
exigir três aquisições disjuntas, o inventário documental atual é insuficiente.

A tarefa encerra com evidência de bloqueio. Não foi criada autorização
operacional alternativa nem reativada uma autoridade histórica.

```text
TI3_A=BLOCKED_METHOD_PRECONDITIONS
TI3_A_DATASET=BLOCKED_TARGET_CONTRACT_NOT_VERIFIED
TI3_A_SPLIT=NOT_DEFINED
TI3_A_LEAKAGE_GUARDS=NOT_IMPLEMENTED
TI3_A_CURRICULAR_ALIGNMENT=NOT_REACHED
TI3_A_BASELINE=NOT_STARTED
FINAL_TEST=NOT_DEFINED_NOT_OPENED
MODEL_SELECTION=NOT_STARTED
G2_SOLUTE=PASS
HOLDOUT_SOLUTE=CONSUMED
TI3_B_READY_FOR_AUTHOR_DECISION=false
TI3_B_AUTHORIZED=false
MERGE_AUTHORIZED=false
CURRENT_AUTHORIZED_ACTIVITY=NONE_AWAITING_AUTHOR_DECISION
```
