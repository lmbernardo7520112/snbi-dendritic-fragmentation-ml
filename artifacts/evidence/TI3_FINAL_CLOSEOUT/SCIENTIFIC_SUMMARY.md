# Estudo científico 1 — encerramento integrado

**TI3_D_INTEGRATION=PASS; SCIENTIFIC_STUDY_1=COMPLETE.** O estudo terminou
com o pipeline MULTIMODAL_LBP_RF, selecionado antes de FINAL. A avaliação
final histórica acertou quatro das seis weak labels: balanced accuracy,
accuracy, precision, recall e F1 = 0.6666666666666666. A matriz de confusão
é [[2,1],[1,2]], com TN2/FP1/FN1/TP2. PASS expressa cumprimento do protocolo;
nenhum desempenho mínimo foi usado como gate.

## Resultado científico preservado

O target é PUBLISHED_FRAGMENTATION_LOCATION_PRESENT: localização cumulativa
publicada sob supervisão fraca. BACKGROUND_CANDIDATE não comprova ausência
física de fragmentação. Os campos ESM2/ESM5 são RELATIVE_SOLUTE_FIELD,
sem interpretação de concentração absoluta de Bi.

TI3-A avaliou LBP/RF estrutural; TI3-B comparou a representação multimodal;
TI3-C comparou uma CNN mínima. A regra prévia selecionou RF multimodal com
DEVELOPMENT BA=0.75. TI3-D realizou exatamente um fit nos 50 TRAIN+DEV
(25 positivos/25 backgrounds) e uma avaliação dos seis FINAL (3/3).
O fit foi congelado de forma durável antes de abrir FINAL. Predições foram
gravadas antes da associação aos labels para scoring: prediction-first,
sem alegação de cegamento humano. Não houve retry, tuning ou seleção após FINAL.

O resultado permite somente SMALL_INTERNAL_TEMPORAL_CONFIRMATION de
classificação de weak labels. Sustenta a descrição de quatro classificações
corretas em seis, com escolha do modelo anterior ao teste. Não sustenta
generalização externa, causalidade, forecasting, detecção física exaustiva,
onset exato, Bi absoluto ou estimativa populacional precisa de desempenho.
As limitações estão em [LIMITATIONS.md](LIMITATIONS.md).

## Integração terminal

| Fase | PR | Merge commit |
| --- | --- | --- |
| TI3-A | [#11](https://github.com/lmbernardo7520112/snbi-dendritic-fragmentation-ml/pull/11) | 7a205327b363f8cdbba99c5e58bf2f1e5d1253d3 |
| TI3-B | [#12](https://github.com/lmbernardo7520112/snbi-dendritic-fragmentation-ml/pull/12) | 48da1af69ce48b3287f19b26bfbd24b79243d90e |
| TI3-C | [#13](https://github.com/lmbernardo7520112/snbi-dendritic-fragmentation-ml/pull/13) | a8227901506c3de6fe4a5a4bd19021be3f39b2e8 |
| TI3-D | [#14](https://github.com/lmbernardo7520112/snbi-dendritic-fragmentation-ml/pull/14) | 4165dcf551ffa3130592e1e59f3db7849f889e1e |

O PR #14 passou por Draft, CI verde, Ready e merge commit em
2026-09-20T16:59:41Z. D2 auditado: 73afa095484817b32d9fb5de040848cdfec89a3f.
D1: b7687575d391f642d2c80274f1bc984c45dbba1b. Os 133 hashes do freeze
permanecem intactos; D2 contém somente 14 adições textuais de evidência.
Pós-hashes 147/147 e checksums históricos 95/95 conferidos. O merge tem
parents a8227901506c3de6fe4a5a4bd19021be3f39b2e8 e D2; sua árvore
418112f66aba7539cf43a7d5c0418da5f2b17584 é idêntica à de D2.

As CI de D2, PR e pós-merge passaram, cada uma com seis jobs e 68 passos
SUCCESS no SHA correspondente. Runs do PR: 35523550474, 35523550606,
35523550536, 35523550434, 35523550553. Runs pós-merge: 35524432873,
35524432885, 35524432958, 35524432807, 35524432778. URLs e respostas dos
jobs/passos estão em [FINAL_STATE.json](FINAL_STATE.json).

As 15 branches remotas foram preservadas; somente main avançou para o merge.
Não houve squash, rebase, exclusão de branch, commit corretivo ou rerun de CI.
Durante esta integração: **zero opens/bytes experimentais e zero ML runs**.
As CI executaram seus contratos sintéticos; não reexecutaram o experimento.

## Custódia e alcance deste encerramento

Este diretório contém somente os seis textos autorizados. Foram criados após
o merge e sua CI; ficam locais, sem staging/commit/publicação adicional.
A branch local permanece feat/ti3d-final-evaluation em D2. Main e origin/main
locais continuam em a8227901506c3de6fe4a5a4bd19021be3f39b2e8, sem fetch,
switch ou sincronização local nesta autorização. Main remota foi confirmada
em 4165dcf551ffa3130592e1e59f3db7849f889e1e. O estado local não é apresentado
como sincronizado. Código, resultados e documentos históricos não foram editados.

A auditoria usa apenas textos, Git e CI. A ausência de ciência pós-FINAL é
sustentada pelo histórico e pelos registros auditados, não por monitoramento
universal de syscalls. Nenhum runner, kernel, fit, leitor experimental ou
extração de features foi invocado localmente nesta integração.

Fontes: [TI3-A](../TI3_A_RESUME/c0r1-resume/execution-report.md),
[TI3-B](../TI3_B_SOLUTAL/execution-report.md),
[TI3-C](../TI3_C_CNN/execution-report.md),
[TI3-D](../TI3_D_FINAL/execution-report.md) e seu
[estado terminal](../TI3_D_FINAL/terminal-state.json).

ML_FINAL_TEST=CONSUMED; SCIENTIFIC_MODELING_COMPLETE=true;
MODEL_SELECTION_REOPENED=false. A próxima atividade indicada é preparação
acadêmica, ainda aguardando decisão do autor. Nenhuma nova modelagem está
autorizada; qualquer investigação futura exige NEW_STUDY + NEW_AUTHORIZATION.
