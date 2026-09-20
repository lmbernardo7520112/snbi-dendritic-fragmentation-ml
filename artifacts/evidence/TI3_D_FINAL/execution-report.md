# TI3-C integrado; TI3-D — avaliação final única concluída

**TI3_C_INTEGRATION=PASS; TI3_D_FINAL=PASS; ML_FINAL_TEST=CONSUMED.**
O pipeline MULTIMODAL_LBP_RF foi ajustado uma vez nos 50 TRAIN+DEV e avaliado
uma vez nos seis FINAL. Balanced accuracy, accuracy, precision, recall e F1:
**2/3 = 0,6666666666666666**. TN2/FP1/FN1/TP2. Nenhum desempenho mínimo foi
usado como gate. A modelagem científica e a seleção estão encerradas.

## Os 31 itens do retorno autoral

| Item | Evidência e resultado |
| --- | --- |
| 1. PR TI3-C | [#13](https://github.com/lmbernardo7520112/snbi-dendritic-fragmentation-ml/pull/13): Draft → CI verde → Ready → merge commit; branch preservada |
| 2. Merge TI3-C | a8227901506c3de6fe4a5a4bd19021be3f39b2e8 |
| 3. CI pós-merge | 35518508717 / 35518508733 / 35518508712 / 35518508757: cinco jobs e todos os passos SUCCESS |
| 4. Branch TI3-D | feat/ti3d-final-evaluation, criada no merge exato após fast-forward de main |
| 5. D1 | b7687575d391f642d2c80274f1bc984c45dbba1b, filho direto do merge, 26 caminhos e 133 hashes textuais |
| 6. CI D1 | 35520647191 / 35520647070 / 35520647107 / 35520647083 / 35520647168: seis jobs e todos os passos SUCCESS antes do receipt |
| 7. Final training | 50 samples existentes, 25 positivos/25 backgrounds; ordem TRAIN+DEVELOPMENT de TI3-B |
| 8. Composição | bottom_up_anti_parallel 19 positivos/8 backgrounds; top_down_parallel 6/17; sem rebalanceamento |
| 9. Buffers TRAIN+DEV | ESM1/2:73,146,219 e ESM4/5:98,197; dez aberturas, uma por buffer |
| 10. Bytes TRAIN+DEV | 19.469.052 |
| 11. RF | 100 árvores, seed42, todos os 19 parâmetros históricos preservados; dicionário integral abaixo e em fit-freeze.json |
| 12. Fit final | Uma chamada efetiva e concluída; nenhum fit estrutural, CNN, variante ou retry |
| 13. Buffers FINAL | ESM1/2:293 e ESM4/5:295, somente após fit e freeze lógico durável |
| 14. Opens FINAL | Quatro, uma abertura por buffer; quatro tentativas |
| 15. Bytes FINAL | 7.783.020; total da execução 27.252.072 em 14 opens |
| 16. Suporte | PASS em todos os 56 pares de patches; os seis FINAL sem substituição, deslocamento ou redução de margem |
| 17. Prediction-first | predictions.json contém somente seis IDs/predições/probabilidades, ligado ao hash do fit; gravado com O_EXCL+fsync antes do scoring |
| 18. Labels true/pred | [0,1,1,0,0,1] / [0,1,0,0,1,1], ordem explícita na tabela abaixo |
| 19. Probabilidades | [p0,p1] integrais preservadas por sample_id em predictions.json e results.json |
| 20. Confusão | [[2,1],[1,2]], linhas verdadeiro/colunas predito; classes[0,1]; TN2/FP1/FN1/TP2 |
| 21. Balanced accuracy | 0,6666666666666666 |
| 22. Accuracy | 0,6666666666666666 |
| 23. Precision | 0,6666666666666666 |
| 24. Recall | 0,6666666666666666 |
| 25. F1 | 0,6666666666666666 |
| 26. Granularidade | Um erro altera sensitivity/specificity da classe em 33,333…pp; accuracy/BA em 16,666…pp neste desenho3/3 |
| 27. Claim scope | SMALL_INTERNAL_TEMPORAL_CONFIRMATION de localização publicada sob supervisão fraca; sem estimativa populacional precisa ou generalização externa |
| 28. D2 | Exclusivamente evidências textuais; SHA efetivo pertence ao Git e ao retorno ao operador, evitando autorreferência |
| 29. CI final | Será conferida no SHA D2 após publicação e informada no retorno efetivo; este texto não antecipa sucesso remoto |
| 30. Worktree/index | Ciência D1 preservada; somente textos de encerramento novos. Limpeza e igualdade local/remoto serão verificadas após D2 |
| 31. Terminal | PASS; CLOSED_CONSUMED; SCIENTIFIC_MODELING_COMPLETE=true; nenhuma nova modelagem ou merge TI3-D autorizado |

## Integração, testes e freeze

A integração confirmou C2 TI3-C a0364a25694d149cb9e5dcb217de2b241fac0702,
parent C1 b2d8839ca2b6c6e5ddd2be1de3ff9589ada9a93c, local/remoto iguais e
worktree/index limpos. C2 continha somente11 adições textuais. Freeze98/98,
pós-hashes109/109 e checksums95/95 passaram na auditoria independente.
A CI do PR #13 foi aprovada nos runs35518329967/35518329994/35518329948/
35518329941. O merge preservou parents48da1af69ce48b3287f19b26bfbd24b79243d90e
e a0364a2, com árvore0ac9a446fb3fcfd0e8b2196d2c6990bfed7f0f3e idêntica ao head.
A prova completa está em integration-audit.json; nenhuma branch foi excluída.

D1 preserva todos os 105 arquivos Python anteriores, seus modos e blobs. Somente o
manifesto de escopo anterior recebeu sete entradas: 75 LEGACY + 4 A0 + 33 ativos,
112 Python relevantes, zero não classificados. Nenhum checker, workflow anterior,
checksum histórico ou método A/B/C/G2 mudou. Um workflow adicional executa
os 59 novos testes; os cinco jobs anteriores continuam obrigatórios.

Testes locais: núcleo 14, suporte 9 e execução 36; perfil conjunto 59 PASS sem
skips/falhas/erros. A suíte de execução teve uma passagem 35 PASS e outra 36 PASS
após completar a preservação do estado consumido. Regressão stdlib:
706 testes, 567 passes e 139 skips opcionais, nenhum erro/falha. Dois fits RF
sintéticos reais locais antecederam D1, separados do único fit científico.
A configuração serializada foi comparada recursivamente por tipo e valor.
O preflight preparatório usou145 leituras textuais reais e Git/CI simulados
explicitamente, sem receipt; não substituiu a prova remota.

A revisão pré-freeze corrigiu a declaração da ordem FINAL, o tipo dos labels
passados ao scoring e o relato da recusa de uma segunda invocação. Nenhuma
correção ocorreu após D1 ou após observar pixels. A ordem FINAL agrupada por
source_inventory e sample_id foi declarada antes do freeze; IDs, labels,
centros, contextos e os manifests originais permanecem idênticos.

Manifesto original: c8e82b72ff5dc51d188a764c577c11d514474b14d90aea6292c1439e776fb487.
Manifesto FINAL: 985af14d0d6a74298bbc0380767f900d264f544303e46ecd8ed4dc0eb1ab649f.
Não houve novo target, site, ledger, split, background ou sample.

Ambiente preexistente: Python3.12.3, NumPy1.26.4, SciPy1.11.4,
scikit-image0.24.0, scikit-learn1.5.2. Os 22 pins existentes foram reconferidos;
nenhuma instalação local. Torch não foi importado pelo pipeline final.
actual-preflight.json registra o preflight real aprovado no D1 com 133 hashes,
seis jobs verdes e zero opens/bytes antes do receipt.

## Execução única e ordem efetiva

Comando único no sandbox padrão, TMPDIR dentro do repositório, exit 0:

```text
PYTHONPATH=src .venv/bin/python -B scripts/run_ti3d_final.py
```

Receipt exclusivo O_EXCL+fsync: **2026-09-20T15:49:21.376641+00:00**, vinculado
a D1, manifesto e inventário. Foram materializados todos os 50 pares de patches
TRAIN+DEV e admitido seu suporte antes de gerar features. Os 50 hashes estruturais,
50 solutais e 50 hashes de features coincidem com TI3-B. Só então ocorreu um fit.

O registro fit-freeze.json foi escrito exclusivamente e sincronizado antes de
liberar FINAL. Hash lógico completo do estado preditivo aprendido, campos das
100 árvores sem padding indeterminado:
`7eb72a60bc72f8d72e0c5f77f67cfde4d456be5264d0d8c5bea68398b0c11894`.
Hash do registro durável:
`2121642ec1fda8ceae6cad2f54d5ef88e079cfa5e6af369c0553f5e495e5aebf`.
Nenhum array de árvore ou modelo binário foi exportado.

O receipt de acesso FINAL, às **2026-09-20T15:49:21.786808+00:00**, referencia
esse mesmo hash e D1. Cada buffer foi aberto uma única vez, autenticando hash
na própria leitura. Os seis pares FINAL passaram integralmente no suporte
antes de gerar suas features ou inferência. Não houve reabertura para hash,
inspeção ou auditoria posterior. O reader terminou fechado, sem falhas.

O registro de seis predições foi gravado com O_EXCL+fsync antes de associar
true weak labels e calcular métricas. Seu SHA-256 é
`3b6ea70adfecf85658627e8f2688dcd7ada369f14110465a51c9030000be797b`.
A função de inferência não recebe labels; o scoring exige o estado de predições
congeladas. Isso é PREDICTION_FIRST_FINAL_EVALUATION, não cegamento humano:
IDs/metadados históricos podem revelar classes. Os vínculos de hash, código
congelado e testes verificam a ordem; não se alega monitoramento de syscalls.

| Conjunto | Buffers | Opens | Bytes |
| --- | --- | ---: | ---: |
| Final training estrutural | ESM1:73/146/219;ESM4:98/197 |5|9.734.526|
| Final training solutal | ESM2:73/146/219;ESM5:98/197 |5|9.734.526|
| FINAL estrutural | ESM1:293;ESM4:295 |2|3.891.510|
| FINAL solutal | ESM2:293;ESM5:295 |2|3.891.510|
| Total |14 buffers distintos|14|27.252.072|

Os guards usam os mesmos predicados numéricos anteriores. FINAL é admitido
explicitamente pelo novo módulo, sem renomear seu split como TRAIN. O suporte
estrutural examina os planos nativos necessários a chroma/halo/bordas; não se
alega leitura apenas dos pixels de patch. Features usam somente Y nativa,
LBP P8/R1/uniform, dez bins/range(0,10)/density=True por modalidade,
concatenação estrutural 10 + solutal 10. Patches 65×65, features e modelo ficaram
em memória. Não foram exportados imagens, patches, feature arrays, pickle,
joblib ou outro modelo binário. Nenhum ESM3/6, frame novo, ZIP/MP4,
FFmpeg/FFprobe, registro ou fonte externa foi acessado.

## Seis predições congeladas e parâmetros

| sample_id | True weak label | Predição | p0 | p1 |
| --- | ---: | ---: | ---: | ---: |
| background\|ESM1\|293\|622\|806 | 0 | 0 | 0.54 | 0.46 |
| positive\|ESM3:annotation-site:2d8693eaf74b3e06 | 1 | 1 | 0.1 | 0.9 |
| positive\|ESM3:annotation-site:f96050cb91a60afe | 1 | 0 | 0.64 | 0.36 |
| background\|ESM4\|295\|1142\|545 | 0 | 0 | 0.83 | 0.17 |
| background\|ESM4\|295\|817\|350 | 0 | 1 | 0.21 | 0.79 |
| positive\|ESM6:annotation-site:8c97cae8aaa8f4f3 | 1 | 1 | 0.15 | 0.85 |

Parâmetros RF integrais, sem alterações em relação a TI3-B:

```json
{
  "bootstrap": true,
  "ccp_alpha": 0.0,
  "class_weight": null,
  "criterion": "gini",
  "max_depth": null,
  "max_features": "sqrt",
  "max_leaf_nodes": null,
  "max_samples": null,
  "min_impurity_decrease": 0.0,
  "min_samples_leaf": 1,
  "min_samples_split": 2,
  "min_weight_fraction_leaf": 0.0,
  "monotonic_cst": null,
  "n_estimators": 100,
  "n_jobs": null,
  "oob_score": false,
  "random_state": 42,
  "verbose": 0,
  "warm_start": false
}
```

Resubstituição nos 50 samples de fit: TN25/FP0/FN0/TP25; todas as cinco métricas
iguais a 1. Isso descreve os próprios dados de ajuste e não estima generalização
nem influenciou decisão alguma. Não houve nova avaliação DEVELOPMENT separada.

## Interpretação e fechamento

FINAL acertou quatro das seis weak labels. O único FP é um BACKGROUND_CANDIDATE
classificado como PUBLISHED_FRAGMENTATION_LOCATION_PRESENT; não comprova
fragmentação física falsa. O único FN é uma localização publicada positiva
que não foi classificada como positiva pelo pipeline; não demonstra perda
definitiva de um evento físico.

O resultado é uma confirmação temporal interna pequena, com 3 samples por classe.
Um erro altera sensitivity/specificity em 33,333…pontos percentuais e accuracy/
BA em 16,666…pontos percentuais. Não sustenta estimativa populacional precisa,
significância, generalização a novas aquisições ou causalidade. A confusão
potencial classe/aquisição 19/8 versus 6/17 foi preservada. Patches não são
réplicas experimentais independentes; backgrounds não provam ausência física.

A exposição histórica não ML continua declarada, sem virgindade global de
holdout. ESM2/5 são campos relativos, nunca Bi absoluto. Círculo não é máscara
de fragmento; onset exato, forecasting, recall físico exaustivo, temperatura
e causalidade não são inferidos. Referências DEV A=0,6875 / B=0,75 / C=0,50 são apenas
históricas; FINAL não reabre família, modalidade, threshold ou modelagem.

A auditoria posterior lê somente textos e Git e recalcula aritmética de
predições; nenhum kernel, fit, feature extractor, buffer ou modelo é reexecutado.
O freeze 133 e checksums 95 permanecem íntegros. verification-terminal.json e
post-run-hashes.sha256 registram a custódia; commands-execution.json separa
ciência, testes sintéticos, aprovações Git e falhas auxiliares de preparação.
Os inventários são delimitados, não monitoramento universal de syscalls.

D2 registra somente evidência. Seu SHA, publicação, CI e estado Git final serão
informados após as operações efetivas. Nenhum merge ou exclusão da branch
TI3-D é autorizado. A seleção e a modelagem terminaram; nenhum retry, tuning,
nova seed/RF/CNN/modalidade/feature/patch/background/label/split ou FINAL2.

```text
TI3_C_INTEGRATION=PASS
TI3_D_FINAL=PASS
MODEL_FAMILY=MULTIMODAL_LBP_RF
FINAL_TRAINING_SAMPLES=50
FINAL_TEST_SAMPLES=6
SCIENTIFIC_FINAL_RUNS=1
FINAL_FIT_CALLS=1
FINAL_EVALUATIONS=1
ML_FINAL_TEST=CONSUMED
ML_FINAL_TEST_EXECUTED=true
MODEL_SELECTION_REOPENED=false
FORECASTING_AUTHORIZED=false
CAUSALITY_CLAIM_AUTHORIZED=false
EXTERNAL_GENERALIZATION_CLAIM=false
SCIENTIFIC_MODELING_COMPLETE=true
FINAL_REPORT_READY_FOR_AUTHOR_DECISION=true
MERGE_AUTHORIZED=false
TI3_D_EXECUTION_AUTHORIZED=false
STATE=CLOSED_CONSUMED
CURRENT_AUTHORIZED_ACTIVITY=NONE_AWAITING_AUTHOR_DECISION
```
