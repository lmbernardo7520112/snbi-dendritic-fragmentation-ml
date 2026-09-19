# TI3-C0R1 + TI3-A — reparo aceito e baseline único concluído

**TI3_GOV_COMPAT=PASS; C0R1_CI=PASS; C1_CI=PASS; TI3_A=PASS.**
Uma única execução científica completou LBP/RF em TRAIN/DEVELOPMENT.
Foram lidos cinco buffers uma vez cada, 9.734.526 bytes. Cinquenta patches
passaram no suporte real; um fit RF foi realizado. FINAL teve zero opens,
zero bytes e nenhuma feature ou avaliação. A autoridade científica encerrou.

## Vinte itens do retorno autoral

| Item | Resultado |
| --- | --- |
| 1. C0 | 272695a4420e37fddf6674664d0040ef064c153f, preservado sem amend |
| 2. Linha problemática | `.github/workflows/ti3-synthetic.yml:28`: `run: python -B -m pip --isolated install --disable-pip-version-check --no-cache-dir --only-binary=:all: -r requirements-ti3-ml.txt`; `:` seguido de espaço em scalar YAML não citado |
| 3. Correção | Exclusivamente `run: >-` e cinco linhas autorizadas; comando shell preservado byte a byte |
| 4. Diff C0..C0R1 | Um step do workflow (6 linhas novas/1 removida), mais evidência textual; diff em TI3_GOV_COMPAT/c0r1/workflow.diff.txt; nenhum outro step, pin ou guard modificado |
| 5. Validação local | PyYAML 6.0.1 confirmou erro original e aceitou correção; data/phase guards PASS; 41 testes de governança e perfil C0 59 PASS, sem skips; nenhum checksum ativo alterado no reparo |
| 6. C0R1 | aba4fb6d66fd6bf640b3cd6adad07b2d60dfe49a, filho direto de C0; único corretivo |
| 7. Runs novos | C0R1: 35457621425 e 35457621439; C1: 35458441566 e 35458441568; todos SUCCESS nos respectivos SHAs |
| 8. Job TI3 | Criado e executado em C0R1 e C1, incluindo instalação CI, versões, guard e perfil sintético |
| 9. Jobs | deterministic-contracts, scientific-synthetic-contracts e ti3-synthetic-contracts: SUCCESS, todos os passos SUCCESS em C0R1 e C1 |
| 10. Governança | PASS, encerrada; 75 LEGACY + 4 A0 preservados; não houve nova arquitetura de governança |
| 11. C1 | e6090121471faa8902f68ddd045ab8b54a2e77fc, filho direto de C0R1; 45 textos congelados antes dos pixels |
| 12. CI C1 | PASS; prova exata em ci-proof.json, conferida antes de armar o receipt |
| 13. TRAIN/DEV | 5 opens, 9.734.526 bytes; 34 TRAIN e 16 DEV patches/feature vectors em memória |
| 14. FINAL | 0 opens/0 bytes; seis samples somente documentais, sem materialização, feature ou avaliação |
| 15. ML científico | 1 invocação CLI, 1 chamada ao baseline, 1 fit TRAIN, 1 avaliação DEV; retries=0; model_selection_runs=0 |
| 16. TRAIN | Balanced accuracy, accuracy, precision, recall e F1 = 1,0; TN17/FP0/FN0/TP17 |
| 17. DEV | Balanced accuracy=0,6875; accuracy=0,6875; precision=0,6153846153846154; recall=1,0; F1=0,7619047619047619 |
| 18. Confusão DEV | Linhas verdadeiro/colunas predito, classes [0,1]: [[3,5],[0,8]]; TN3/FP5/FN0/TP8 |
| 19. Limitações | Confusão possível classe/aquisição em TRAIN; DEV16 e FINAL6 pequenos; supervisão fraca, exposição histórica; sem generalização externa |
| 20. Terminal | PASS; CLOSED_CONSUMED; NONE_AWAITING_AUTHOR_DECISION; TI3-B e merge não autorizados |

## Reparo, freeze e preservação

PyYAML já instalado confirmou `mapping values are not allowed here`, linha28,
coluna111, no comando `--only-binary=:all:`. A causa agora é
VERIFIED_YAML_PLAIN_SCALAR_COLON_PARSE_ERROR. O relatório anterior de causa
NOT_VERIFIED continua intacto; esta é evidência posterior, não reescrita.
Não houve instalação local adicional nem rerun do run35455982251.

No reparo C0R1, somente a representação YAML mudou. O workflow não integrava
manifesto ativo de checksums: nenhuma entrada foi adicionada ou alterada.
O snapshot histórico de 95 entradas permaneceu byte-idêntico. C0R1 publicado
por fast-forward produziu nova CI, aprovada antes de continuar C1.

A preparação C1 revalidou arquivos e 15 hashes do planejamento. Os únicos
dois códigos adaptados antes do freeze receberam vínculos operacionais fixos:
parent C0R1, nova autoridade/namespace e leitura do manifesto original. Os
snapshots anteriores e operational-changes.json preservam a diferença exata.
O leitor, admissão, recibo exclusivo, hashes e contadores não foram relaxados.
Os onze estados científicos PLANNED→TRACKED e dois blobs operacionais foram
atualizados na partição existente, sem alterar seus 75+4, paths ou checkers.

Manifesto original: SHA-256
c8e82b72ff5dc51d188a764c577c11d514474b14d90aea6292c1439e776fb487.
Manifesto FINAL: SHA-256
985af14d0d6a74298bbc0380767f900d264f544303e46ecd8ed4dc0eb1ab649f.
Não houve reconstrução do target, ledger, 52 sites, 108 observações,
383 IGNORE, seleção geométrica, backgrounds ou split. Históricos bloqueados
e a autoridade anterior fechada permanecem intactos.

Antes de C1: perfil sintético109PASS sem skips; suíte stdlib535testes,
428passes/107skips opcionais; sete casos preparatórios do preflight PASS.
Três fits RF sintéticos pertencem ao perfil (dois smoke e um teste); são
distintos de SCIENTIFIC_ML_RUNS=1. Auditoria independente confirmou o freeze,
37 textos originais preservados e os dois snapshots operacionais. Depois de
C1 não houve alteração de código, parâmetro, máscara, critério ou modelo.

## Execução e I/O

Comando único no sandbox padrão, exit0:

```text
PYTHONPATH=src .venv/bin/python -B scripts/run_ti3_baseline.py
```

Receipt O_EXCL+fsync anterior aos buffers:
2026-09-19T17:35:47.061273+00:00, vinculado ao SHA C1 e ao manifesto exato.
O preflight anterior e a revalidação interna abriram somente textos; não
consumiram tentativa científica. Uma chamada CLI científica completou
estágio COMPLETED. O resultado e o receipt impedem nova execução.

| Buffer existente | Split | Opens | Bytes |
| --- | --- | ---: | ---: |
| ESM1:73 | TRAIN | 1 | 1.951.506 |
| ESM1:146 | TRAIN | 1 | 1.951.506 |
| ESM4:98 | TRAIN | 1 | 1.940.004 |
| ESM1:219 | DEVELOPMENT | 1 | 1.951.506 |
| ESM4:197 | DEVELOPMENT | 1 | 1.940.004 |
| ESM1:293 | FINAL_TEST | 0 | 0 |
| ESM4:295 | FINAL_TEST | 0 | 0 |

Os hashes nativos foram calculados durante a única leitura de cada buffer e
correspondem ao inventário congelado. Não houve reabertura posterior para
hash ou inspeção. As conferências finais usam apenas os registros textuais.
Não houve ESM2/3/5/6, novo frame, ZIP/MP4, FFmpeg/FFprobe ou fonte externa.

O guard de suporte integral passou em todos os 50 patches TRAIN/DEV antes
do fit. A rotina processou os componentes nativos necessários ao suporte;
não se afirma acesso somente aos pixels de patch. Os patches65×65, dez
features LBP por sample e modelo ficaram em memória. Não foram exportados
raw, imagem, tensor, feature array, pickle ou checkpoint. Materialization-manifest
registra 50 patches com hashes e os seis FINAL com input_opened=false e
patch_sha256=null; nenhum FINAL foi certificado por inspeção cromática.

## Métricas e limites

LBP P8/R1/uniform, histograma10/range(0,10)/density=True; RF100árvores,
random_state42 e demais defaults congelados. NumPy1.26.4, SciPy1.11.4,
scikit-image0.24.0 e scikit-learn1.5.2; ambiente completo em
environment-execution.json. Não houve segunda seed, tuning ou modelo alternativo.

| Métrica | TRAIN (34) | DEVELOPMENT (16) |
| --- | ---: | ---: |
| Balanced accuracy, primária | 1,000000 | 0,687500 |
| Accuracy | 1,000000 | 0,687500 |
| Precision | 1,000000 | 0,615385 |
| Recall | 1,000000 | 1,000000 |
| F1 | 1,000000 | 0,761905 |

Apresentação decimal arredondada; results.json retém os valores completos,
labels, predições, probabilidades, ordem dos samples e parâmetros.
Confusão DEV: TN3/FP5/FN0/TP8. O desempenho TRAIN é medido nos mesmos dados
usados no fit e não estima generalização. PASS significa execução conforme
protocolo; não depende de um score mínimo e não certifica utilidade externa.

TRAIN ESM1 conserva16positivos/6backgrounds; ESM4,1/11. A classe pode se
confundir com aquisição/condição. DEVELOPMENT contém somente16samples;
FINAL tem3positivos/3backgrounds, baixa potência e métricas granulares.
Não houve redistribuição ou exclusão por desempenho. As observações não são
aquisições independentes. Exposição histórica não ML continua declarada.

Os rótulos descrevem localização publicada sob supervisão fraca; background
não comprova ausência física. Recall aqui não é recall físico exaustivo de
fragmentação. Não há onset exato, forecasting, causalidade, concentração
absoluta de Bi, temperatura ou generalização externa. Campo solutal e CNN
não foram usados. G2 histórico não foi reexecutado ou alterado.

## Encerramento e custódia

Somente evidência textual é produzida após a ciência. A auditoria final pode
recalcular aritmética a partir das predições JSON; não chama kernels, extrai
features ou reabre buffers. O freeze45, os checksums95, os manifests e os
registros históricos são preservados. post-run-hashes.sha256 registra os
textos finais; verification-terminal.json registra os limites da conferência.

Um eventual C2 é exclusivamente evidência, conforme a continuação já aprovada.
Seu SHA e sua publicação pertencem ao histórico Git e ao retorno ao operador,
evitando autorreferência. Não há Ready, merge ou exclusão de branch. O estado
local/remoto final será reconfirmado depois da publicação desse checkpoint.

```text
TI3_GOV_COMPAT=PASS
C0R1=PASS
C0R1_CI=PASS
C1=PASS
C1_CI=PASS
TI3_A=PASS
TI3_A_DATASET=PASS
TI3_A_SPLIT=FROZEN_TEMPORAL_GROUPED
TI3_A_LEAKAGE_GUARDS=PASS
BASELINE_MODEL=LBP_RF
SCIENTIFIC_ML_RUNS=1
ML_FINAL_TEST=SEALED_WITH_HISTORICAL_NON_ML_EXPOSURE
ML_FINAL_TEST_EXECUTED=false
SOLUTAL_MODEL_INPUT=NOT_USED
TI3_B_READY_FOR_AUTHOR_DECISION=true
TI3_B_AUTHORIZED=false
MERGE_AUTHORIZED=false
TI3_A_EXECUTION_AUTHORIZED=false
STATE=CLOSED_CONSUMED
CURRENT_AUTHORIZED_ACTIVITY=NONE_AWAITING_AUTHOR_DECISION
```
