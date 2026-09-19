# TI3-B integrado; TI3-C — comparação única de família concluída

**TI3_B_INTEGRATION=PASS; TI3_C=PASS; preferência final de desenvolvimento: MULTIMODAL_LBP_RF.**
A CNN mínima terminou suas dez épocas na única execução autorizada.
DEVELOPMENT BA=0,50 contra RF multimodal 0,75, delta −0,25. A regra congelada
seleciona RF; o resultado não motivou tuning, retry ou outra arquitetura.
FINAL estrutural e solutal permaneceram com zero opens/bytes. A autoridade
científica está CLOSED_CONSUMED.

## Os 25 itens do retorno autoral

| Item | Resultado comprovado |
| --- | --- |
| 1. PR/merge TI3-B | [PR #12](https://github.com/lmbernardo7520112/snbi-dendritic-fragmentation-ml/pull/12), Draft → CI verde → Ready → merge commit; branch preservada |
| 2. Merge SHA | 48da1af69ce48b3287f19b26bfbd24b79243d90e |
| 3. CI pós-merge | 35468947398 / 35468947411 / 35468947421, quatro jobs e todos os passos SUCCESS |
| 4. Branch TI3-C | feat/ti3c-minimal-multimodal-cnn, criada no merge exato após fast-forward de main |
| 5. Dependency freeze | requirements-ti3c-cnn.txt e constraints-ti3c-cnn.txt; 22 pins, instalados somente na .venv e no job dedicado; quatro pins científicos anteriores preservados |
| 6. Torch | 2.4.1+cpu; Python3.12.3 local; build CUDA nulo; sem torchvision/torchaudio |
| 7. Arquitetura | Conv2d(2,8,3,padding1) → ReLU → MaxPool2d(2,2) → AdaptiveAvgPool2d(1,1) → Flatten → Linear(8,2) |
| 8. Parâmetros | 170 treináveis, 152 convolucionais +18 lineares, contagem verificada |
| 9. C1-CNN | b2d8839ca2b6c6e5ddd2be1de3ff9589ada9a93c; parent igual ao merge; 24 paths, 98 hashes congelados |
| 10. CI pré-pixel | 35471095523 / 35471095595 / 35471095533 / 35471095570, cinco jobs e todos os passos SUCCESS |
| 11. Buffers | ESM1/2:73,146,219 e ESM4/5:98,197; dez buffers existentes, uma abertura cada |
| 12. Bytes | 19.469.052; 9.734.526 estruturais +9.734.526 solutais |
| 13. FINAL | ESM1/2:293 e ESM4/5:295, zero tentativas/opens/bytes; seis samples sem materialização |
| 14. Diagnóstico por aquisição | Metadata-only DEV BA=0,5625; TN6/FP2/FN5/TP3, congelado antes dos pixels |
| 15. Losses | Dez valores integrais na tabela abaixo e em results.json, sem escolha de época |
| 16. TRAIN | BA=accuracy=precision=0,5; recall=1; F1=0,6666666666666666; TN0/FP17/FN0/TP17 |
| 17. DEV | BA=accuracy=precision=0,5; recall=1; F1=0,6666666666666666 |
| 18. Confusão DEV | [[0,8],[0,8]], linhas verdadeiro/colunas predito, classes [0,1]; TN0/FP8/FN0/TP8 |
| 19. RF referência | BA multimodal DEV=0,75; consumida, sem novo fit/avaliação RF |
| 20. CNN BA | 0,50 em DEVELOPMENT |
| 21. Delta | −0,25, ou −25 pontos percentuais, descritivo |
| 22. Família selecionada | MULTIMODAL_LBP_RF, pela regra prévia CNN>0,75; empate também favoreceria RF |
| 23. Runs científicos | Uma CLI, uma invocação consumida/concluída, um treinamento de dez épocas, uma avaliação TRAIN e uma DEV; retries/tuning=0 |
| 24. SHA de evidências | O checkpoint exclusivamente textual posterior terá seu SHA no histórico Git e retorno ao operador, sem autorreferência |
| 25. Terminal | PASS; MODEL_FAMILY_SELECTION=COMPLETE; CLOSED_CONSUMED; FINAL e merge TI3-C não autorizados |

## Integração e preparação antes de pixels

A auditoria inicial confirmou B2 local/remoto dc9d0bb467bfc3c94302bb59b91db296e788451e,
worktree/index limpos, 11 evidências apenas, freeze B1 67/67 e checksums95/95.
Os runs de B2 e do PR #12 passaram integralmente antes de Ready/merge. O merge
preserva parents 7a205327b363f8cdbba99c5e58bf2f1e5d1253d3 e B2; árvore
1240d3ec99c8d634cb75f28a23cad0543a769651 idêntica ao head. Os quatro jobs
pós-merge passaram antes da branch TI3-C. integration-audit.json guarda a prova.

A instalação foi inicialmente impedida pela rede/DNS do sandbox. O mesmo
comando delimitado foi aprovado para resolver e instalar os pins na .venv;
nenhuma instalação global, alteração do SO, credencial ou bypass de sandbox.
O wheel CPU cp312 e hashes de distribuição estão em dependency-resolution.json.
requirements/constraints e environment.json permanecem congelados em C1.
Torch só é admitido em src/snbi_fragmentation/ti3c_cnn.py e seu teste; o resto
do domínio continua a recusá-lo. Somente check_ti3_scope.py e phase-scope-v1.json
foram adaptados entre arquivos anteriores. Preservados 75 LEGACY, quatro A0,
19 ativos anteriores e toda ciência A/B; seis paths Python novos classificados.
Os freezes históricos conservam seus hashes originais, ancorados no Git.

Os 34 TRAIN e 16 DEV retêm IDs, labels, centros, contextos, backgrounds e ordem
TI3-B. Manifesto: c8e82b72ff5dc51d188a764c577c11d514474b14d90aea6292c1439e776fb487.
Nada foi replanejado, deduplicado, redistribuído ou excluído por desempenho.
O diagnóstico usa maiorias TRAIN por aquisição: bottom_up [6,16]→classe1;
top_down [11,1]→classe0. Em DEV, BA0,5625 e confusão [[6,2],[5,3]]. Não é
modelo treinado, não usa pixels e não influencia seleção ou split. Sua ordem
no JSON segue o manifesto original; predições são ligadas por sample_id,
independentemente da ordem agrupada usada pelo runner.

Testes antes de C1: 19 núcleo, 27 execução e 22 escopo; perfil combinado
TI3-A/B/C de 221 PASS sem skips; stdlib647, 519passes/128skips opcionais.
Houve quatro treinos CNN sintéticos locais (dois isolados e dois no perfil
combinado), distintos do único treinamento científico. Quatro fits RF
sintéticos pertencem apenas ao perfil de regressão/smoke. Oito controles
preparatórios verificaram preflight serializado e recusas de CI/tipos, com
Git/CI simulados explicitamente, sem receipt. A revisão independente aprovou
núcleo, reader, runner, metadados e freeze98. A distinção entre tentativa e
conclusão em falha parcial foi ajustada antes de C1; não houve reparo posterior.

ci-proof.json registra os cinco jobs reais SUCCESS no SHA C1, todos os passos
concluídos antes do receipt. O último terminou em 21:41:40 UTC.
actual-preflight.json registra PASS com arquivos Git C1 reais, dependências
22/22 e zero opens/bytes, sem armar. O runner revalidou antes da execução única.

## Execução, parâmetros e I/O

Comando único, sandbox padrão, exit0, com TMPDIR no repositório:

```text
PYTHONPATH=src .venv/bin/python -B scripts/run_ti3c_cnn.py
```

Receipt O_EXCL+fsync: 2026-09-19T21:44:14.059880+00:00, anterior aos bytes,
vinculado ao C1, manifesto, inventário e freeze. Foram materializados seis
buffers TRAIN (11.686.032 bytes); depois ocorreram dez épocas e avaliação TRAIN.
Somente então os quatro buffers DEV (7.783.020 bytes) foram abertos e avaliados
uma vez. Os quatro FINAL nunca foram tentados. Hashes nativos foram calculados
na única leitura, sem reabertura posterior. I/O é instrumentação da aplicação,
não monitoramento universal de syscalls.

Todos os 50 pares passaram nos guards históricos de suporte. Os hashes dos
patches estrutural e solutal correspondem exatamente aos 50 registros TI3-B.
Os planos nativos estruturais necessários ao guard foram processados; não se
alega acesso somente aos pixels dos patches. Os tensores científicos usam
somente Y nativa, canal0 estrutural/canal1 solutal relativo, uint8→float32/255.
Não houve LBP/RF científico repetido, registro, novos frames, ESM3/6, ZIP/MP4,
FFmpeg/FFprobe, Canny, augmentation ou máscaras novas. Inputs e modelo ficaram
em memória; nenhuma imagem, array, feature ou modelo binário foi exportado.

Python/NumPy/Torch e Generator têm seed42, CPU e algoritmos determinísticos,
uma thread, zero workers. CrossEntropyLoss e Adam(lr0,005), weight_decay0,
demais defaults registrados em results.json. Batch8, shuffleTRAIN, dez épocas,
50 passos Adam. Sem DEV durante treino, early stopping, scheduler ou tuning.
Predições finais por argmax dos dois logits; cada vetor de logits/probabilidade,
label e sample_id está preservado no JSON, sem escolha retrospectiva de threshold.

| Época | Loss média ponderada pelos samples dos minibatches |
| --- | ---: |
| 1 | 0.6979416153010201 |
| 2 | 0.6929170524372774 |
| 3 | 0.6905957074726329 |
| 4 | 0.6914088726043701 |
| 5 | 0.6899096404804903 |
| 6 | 0.6915857230915743 |
| 7 | 0.6879432061139275 |
| 8 | 0.6885284536025104 |
| 9 | 0.6895678393981036 |
| 10 | 0.6908964619917028 |

## Métricas, escolha e limites

| Métrica | TRAIN34 CNN | DEVELOPMENT16 CNN | DEVELOPMENT RF histórico |
| --- | ---: | ---: | ---: |
| Balanced accuracy | 0,50 | 0,50 | 0,75 |
| Accuracy | 0,50 | 0,50 | 0,75 |
| Precision | 0,50 | 0,50 | 0,666667 |
| Recall | 1,00 | 1,00 | 1,00 |
| F1 | 0,666667 | 0,666667 | 0,80 |

A CNN previu classe1 para todos os 50 samples. O recall1 não demonstra boa
discriminação: todos os backgrounds foram classificados como positivos.
A apresentação arredonda F1; os valores integrais e decisões estão no JSON.
A regra exclusiva CNNDEV>0,75 selecionou RF multimodal com delta−0,25; quatro
acertos líquidos a menos nos 16 DEV. A referência estrutural0,6875 também
permanece histórica, sem reexecução. TRAIN não participou da escolha e não
estima generalização. A condição pré-especificada TRAIN1/DEVmenor não ocorreu;
isso não certifica ausência de outros problemas de ajuste. Não houve segunda
seed, repetição, busca ou tentativa de melhorar a CNN.

PASS certifica execução conforme protocolo, independentemente da superioridade.
A conclusão é somente preferência interna de desenvolvimento nesta comparação
congelada. Não demonstra impossibilidade de CNNs ou significância estatística.
TRAIN ainda pode confundir classe/aquisição (ESM1:16positivos/6backgrounds;
ESM4:1/11). DEV16 e FINAL6 são pequenos, patches não são aquisições independentes.
Supervisão fraca representa localização cumulativa publicada; background não
prova ausência física, FP não prova falsa fragmentação física, recall não é
inventário físico exaustivo. ESM2/5 são campos relativos, não Bi absoluto.
Não há onset exato, forecasting, causalidade, temperatura ou generalização externa.

FINAL permanece SEALED_WITH_HISTORICAL_NON_ML_EXPOSURE, nunca globalmente virgem.
Os seis samples têm hashes de input/patch nulos e nenhuma inspeção de suporte
ou inferência nesta fase. A comparação termina; avaliação final depende de
nova decisão autoral e não foi iniciada.

## Custódia e fechamento

Receipt/results fecham permanentemente a configuração condicional. Ciência,
configuração e parâmetros não mudaram depois de C1. Verificação posterior usa
somente textos, aritmética dos resultados e Git; nenhum kernel, teste de treino,
buffer ou modelo foi reaberto/reexecutado. Os 98 textos e 95 checksums históricos
continuam verificáveis. post-run-hashes.sha256 autentica a evidência final;
verification-terminal.json registra conferências e limitações. O inventário
de comandos é delimitado, sem alegação de monitoramento universal.

O checkpoint posterior é exclusivamente documental. Seu SHA e eventual
publicação/CI pertencem ao histórico Git e ao retorno efetivo ao operador,
sem inventar estado futuro. Não há Ready, merge ou exclusão da branch TI3-C.

```text
TI3_B_INTEGRATION=PASS
TI3_C=PASS
SCIENTIFIC_TI3C_RUNS=1
MODEL_FAMILY_SELECTION=COMPLETE
FINAL_MODEL_FAMILY_PREFERENCE=MULTIMODAL_LBP_RF
ML_FINAL_TEST=SEALED_WITH_HISTORICAL_NON_ML_EXPOSURE
ML_FINAL_TEST_EXECUTED=false
FORECASTING_AUTHORIZED=false
CAUSALITY_CLAIM_AUTHORIZED=false
EXTERNAL_GENERALIZATION_CLAIM=false
FINAL_EVALUATION_READY_FOR_AUTHOR_DECISION=true
FINAL_EVALUATION_AUTHORIZED=false
MERGE_AUTHORIZED=false
TI3_C_EXECUTION_AUTHORIZED=false
STATE=CLOSED_CONSUMED
CURRENT_AUTHORIZED_ACTIVITY=NONE_AWAITING_AUTHOR_DECISION
```
