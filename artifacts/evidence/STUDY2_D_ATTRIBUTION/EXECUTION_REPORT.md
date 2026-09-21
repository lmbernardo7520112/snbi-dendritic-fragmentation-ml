# Study2-C integrado; Study2-D — atribuição pós-hoc concluída

**STUDY2_C_INTEGRATION=PASS; STUDY2_D=PASS; DISTINCT_RF_FITS=100.** A execução única concluiu os três contrastes congelados usando apenas as 10.907 rows TRAIN. A diversidade teve efeito médio pequeno e misto: K24−K17 = **+0,0039043309111838507**, com 11/20 deltas positivos. DALL−D1 = **−0,059699310144642304**, e GROUP_EQUAL−OBSERVATION_EQUAL = **−0,014586902176019961**, ambos negativos nos quatro folds globais. Não foi identificada uma explicação positiva consistente para toda a diferença histórica entre os estudos. PASS significa cumprimento do protocolo, independentemente do sinal dos efeitos.

## Retorno dos 38 itens autorais

| Item | Evidência e resultado |
| --- | --- |
| 1. Study2-C PR/merge | [PR #18](https://github.com/lmbernardo7520112/snbi-dendritic-fragmentation-ml/pull/18): Draft → CI verde → Ready → merge commit; branch preservada |
| 2. Merge SHA | ec97cb5041ef35d4f6c9a79b54d756d6fbee674f |
| 3. CI pós-merge C | Nove jobs e 100 passos SUCCESS; INTEGRATION_AUDIT.json |
| 4. Branch D | feat/study2d-data-centric-bridge, criada no merge exato |
| 5. TRAIN allowlist | 32 sites GOLD + 32 tracks BG; 3.858 + 7.049 = 10.907 rows; identidades e offsets em TRAIN_INPUT_MANIFEST.json |
| 6. Folds | Quatro folds históricos; SHA-256 85edac3d7da06994d7b16c4fa50e2aeb806abd7743a1d471842f54fdcf049ef2 |
| 7. RF | RF_REFERENCE, 100 árvores/seed42; 19 parâmetros completos abaixo, idênticos em todos os fits |
| 8. LBP | Dois canais Y nativos, 65×65 uint8; P8/R1/uniform; dez bins/range(0,10)/density=True por canal; concatenação20 |
| 9. Representante | Ordenação temporal; mediana inferior: índice (n−1)//2; nenhuma escolha por pixels ou desempenho |
| 10. K | 4, 8, 12, 17, 24 grupos por classe; quotas bottom/top 3/1, 6/2, 9/3, 13/4, 18/6 |
| 11. Replicates | STUDY2D_GROUP_R1 a R5; SHA-256 textual por salt/fold/classe/aquisição/group_id; prefixos aninhados por estrato; K24 uma vez/fold |
| 12. Densidade | D1 mediana; D3 quantis 25/50/75%; D5 0/25/50/75/100%; rank mais próximo com empate inferior; deduplicação; grupos curtos usam todos |
| 13. Pesos | GROUP_EQUAL=1/n selecionado por grupo; OBSERVATION_EQUAL=1 por row; não há class_weight |
| 14. Budget | 84 fits A + 12 adicionais B + 4 adicionais C = 100; oito referências a resultados reutilizados |
| 15. Freeze | Original21400de67d21901aeb8e5abac528689fc39169fa; reparo operacional8c6221da3d03a498158d812be5c08848c37c2247; método original inalterado |
| 16. CI pré-fit | No reparo: nove workflows, dez jobs e 110 passos SUCCESS; dedicado116/116 sem skips; CI_PROOF.json |
| 17. Comando | PYTHONPATH=src .venv/bin/python -B scripts/run_study2d.py run; TMPDIR controlado no repositório; uma invocação, exit0 |
| 18. Fits reais | 100 iniciados, 100 concluídos e 100 avaliações CV; 84/12/4; zero retry; uma extração LBP20 para 10.907 rows |
| 19. Curva de grupos | Tabela completa global e por aquisição abaixo; média, mediana, desvio populacional, mínimo, máximo e n |
| 20. K24−K17 | +0,0039043309111838507; mediana +0,001946324342305794; 11 positivos/0 zero/9 negativos |
| 21. K24−K4 | +0,0035758000145099554; mediana +0,0008605457837255193; 11 positivos/0 zero/9 negativos |
| 22. Tabela densidade | D1=0,7786692086875789; D3=0,7697124456485938; D5=0,7735548436540266; DALL=0,7189698985429366 |
| 23. ALL−1 | −0,059699310144642304; quatro deltas globais negativos, vetores completos abaixo |
| 24. Ponderação | GROUP_EQUAL−OBSERVATION_EQUAL=−0,014586902176019961; quatro deltas globais negativos |
| 25. Descritores | MIXED_POSITIVE; NON_POSITIVE; NO_GROUP_EQUAL_BENEFIT, respectivamente; regras prévias preservadas |
| 26. Por aquisição | Diagnósticos e sinais abaixo; top_down tem somente dois sites + dois tracks em cada validação |
| 27. Ponte narrativa | Nove condições abaixo; TEST histórico não integra a tabela |
| 28. Experimento 1 | K17 é NUMERICAL_SCALE_BRIDGE; 17 grupos/classe não equivalem a 17 samples/classe; nenhum pixel ou métrica histórica reexecutado |
| 29. Study2-C | Referência textual: TEST GMBA0,8449139278495638; SILVER DEV delta0,0016093220301962585; nenhuma seleção final alterada |
| 30. Causalidade | Efeitos condicionais pós-hoc; não somáveis; sem atribuição percentual da melhoria, causalidade física, significância universal ou generalização externa |
| 31. DEV | DEV_GROUPS_READ=0; DEV_ROWS_READ=0; nenhuma row/tensor/feature DEV |
| 32. TEST | TEST_GROUPS_READ=0; TEST_ROWS_READ=0; TEST_CACHE_ROWS_READ=0; TEST_FEATURES_COMPUTED=0; binário e índice TEST não abertos |
| 33. Fontes | ESM1..6_OPENS=0; EXPERIMENTAL_SOURCE_OPENS=0; FFMPEG_RUNS=0; somente dois containers existentes via pread dirigido |
| 34. Runtime | 28.42156980100026s medidos pelo controlador; pico Python 613,284 KiB; não é pico de todo o sistema |
| 35. Checkpoint | Posterior exclusivamente documental; SHA efetivo no Git e no retorno final, evitando autorreferência |
| 36. CI final | Será conferida no SHA documental após push; esta versão não antecipa conclusão remota |
| 37. Git | Fontes do reparo preservadas; nenhum novo binário/cache; academic-deliverable-build/ preservado; estado após publicação informado no retorno |
| 38. Terminal | PASS; CLOSED_CONSUMED; nenhum fit adicional/model search/DEV/TEST/PR/Ready/merge D autorizado |

## Integração, reparo e congelamento

O checkpoint C c715df53d5dc08815235f010c07616deef7bbb4a foi integrado após a conferência local/remota, dos registros consumidos e da CI. O merge ec97cb5 preserva parents de7670bb8491d2ef01809b33aa326aa3a264324c/c715df53d5dc08815235f010c07616deef7bbb4a e a árvore1c51c1e5b089de9c91371a198b4bf87c11719224, idêntica ao head C. O fast-forward de main antecedeu a nova branch. As provas remotas estão em INTEGRATION_AUDIT.json.

A decisão suplementar de custódia prevaleceu sobre qualquer leitura ampla da seção2: a integração autenticou materialmente somente as 10.907 rows TRAIN, por 10.907 preads/92.164.150 bytes e dois opens. Os três hashes de cada par/canal estavam disponíveis e coincidiram; não foi necessário ampliar o acesso. Caches com DEV/TEST foram autenticados documentalmente pelos registros existentes de C. O cache TEST e seu índice não foram abertos. Metadados de splits de manifests previamente comprometidos foram lidos para formar a allowlist; isso não é leitura de pixels/tensors/features dos grupos DEV/TEST. INTEGRATION_TRAIN_CUSTODY.json registra esse limite e distingue custódia histórica de autenticação material atual.

O plano metadata-only foi gerado uma vez, antes do freeze original. PLAN_TEXT_AUDIT.json conferiu independentemente grupos, folds, quotas, rankings, amostras temporais, memberships e 100 specs sem executar novamente o planner. O freeze original21400de é filho direto do merge e preserva 52 hashes textuais. A CI original falhou no perfil `python -S`: quatro testes I/O atravessavam a importação lazy de NumPy sem seu skip opcional. Nenhuma ciência ocorreu antes ou após essa falha até a autorização complementar e a nova CI verde. O diagnóstico original, o log e o bloqueio permanecem históricos.

A [autorização complementar](CI_REPAIR_AUTHORIZATION.md) permitiu exatamente um filho corretivo. O commit8c6221d acrescentou os quatro skips condicionais e a verificação operacional da cadeia ec97cb5→21400de→8c6221d, com testes de recusa de ancestrais/merges/filhos adicionais. Seis arquivos existentes mudaram; 21 provas textuais foram adicionadas. Nenhum desenho, corpus, reader científico, feature, parâmetro RF, fold, peso ou métrica foi alterado. A comparação AST independente preserva o corpo científico do executor; CI_REPAIR_DIFF.json e CI_REPAIR_SOURCE_DIFF.txt delimitam o diff.

Stdlib final: 1.139 testes, 868 passes e 271 skips opcionais, zero falhas/erros; os quatro novos skips são exclusivamente os autorizados. A primeira passagem anterior ao último assert literal de BASE também passou e foi preservada. Dedicado final:116/116 PASS local e remoto, zero skips;20 desenho,20 modelos,29 I/O,47 execução. Dois fits RF locais desse perfil foram sintéticos; acumulado local sintético de oito incluindo a preparação original, separado dos100 fits científicos. Nenhuma instalação local. Os22 pins anteriores foram reconferidos.

O freeze operacional autentica72 textos e referencia explicitamente o original sem substituir sua história. O preparatório usou textos reais e Git/CI futuros simulados, declarado como tal. O real aprovou o SHA do reparo, ancestralidade exata,52 hashes originais,72 hashes atuais,27 paths do reparo,10.907 rows/64 grupos,fold,RF/LBP,budget100 e dez jobs reais. Os guards aprovaram146 Python classificados e95 checksums históricos; não houve alteração dos workflows.

## Execução e fronteiras de acesso

Comando único no sandbox padrão, exit0, com TMPDIR no diretório controlado `.bootstrap-test-tmp/`:

```text
PYTHONPATH=src .venv/bin/python -B scripts/run_study2d.py run
```

Último job exigido terminou às **2026-09-21T20:58:12Z**. Receipt exclusivo O_EXCL+fsync às **2026-09-21T21:00:10.897031+00:00**, vinculado ao reparo, desenho e manifesto. O preflight real ocorreu antes do receipt e foi repetido internamente pela CLI. Código e dados científicos congelados permaneceram iguais após os resultados.

O reader abriu somente o container positivo B e o cache compartilhado TRAIN+DEV C. Validou o split, tier, sample_id/group_id, offset, shape e três hashes por row antes de formar o tensor. Cada acesso foi um pread de exatamente8.450 bytes; todos os descritores foram fechados. Não houve rehash integral, varredura sequencial do container, mmap ou leitura DEV para autenticação. As10907rows e seus offsets estão integralmente em IO_AUDIT.json. Os contadores medem ranges entregues à aplicação; não instrumentam caching/readahead do kernel nem constituem monitoramento universal de syscalls.

| Fronteira | Opens de containers | Rows/preads | Bytes de payload TRAIN | Features |
| --- | --- | --- | --- | --- |
| Custódia pré-integração | 2 | 10907 | 92164150 | 0; bytes opacos autenticados |
| CLI científica D | 2 | 10907 | 92164150 | 10907×20 em RAM, uma extração |
| Soma dessas duas fases | 4 | 21814 | 184328300 | nenhuma extração na custódia |
| Reparo e auditorias posteriores | 0 | 0 | 0 | 0 |

Na ciência, GOLD leu **32,600,100 bytes** e BG **59,564,050 bytes**. DEV/TEST, seus features e todos os ESM/FFmpeg ficaram em zero. Não houve novo patch/background, arquivo de modelo, array de features ou cache científico persistido. Os resultados são textos JSON/Markdown, incluindo predições completas e probabilidades por condição. A ramificação dos100 fits estava congelada antes da execução; nenhum resultado A alterou B ou C.

Runtime do controlador **28.42156980100026s**; pico Python **613284KiB**, limitado ao processo Python. A execução concluiu84+12+4 fits e100 avaliações CV. D1/K24 foi reutilizado quatro vezes em B e GROUP_EQUAL/DALL quatro vezes em C, sem refit. As validações têm3.131/2.926/2.429/2.421 rows nos folds0–3: todas as GOLD+BG dos16 grupos held-out de cada fold. São272.675 predições condição×row, e não272.675 observações independentes.

## Desenho mantido fixo

TRAIN contém por classe24 grupos bottom_up e8 top_down. Cada validação contém6+2 por classe; cada treino18+6 por classe. Os mesmos quatro folds são usados em todas as condições. Não foram usados os171 tracks de reserva, os35 sites sem suporte, SILVER ou UNLABELED. D não seleciona outro pipeline nem procura um hiperparâmetro.

Em A, uma mediana temporal por grupo mantém a densidade fixa; aumentar K também aumenta o total de rows de2K. Portanto, a intervenção é o aumento conjunto do número de grupos e de exemplos representativos, não uma comparação de diversidade pura com n constante. O ranking é SHA256(salt|fold_id|class|acquisition|group_id), classes canônicas POSITIVE/BACKGROUND; os prefixos são aninhados separadamente por classe/aquisição. K24 usa todos os48 grupos de treino e ocorre somente uma vez/fold.

Em B, D3 aproxima25/50/75% e D5 inclui0/25/50/75/100% do rank temporal. Usa-se a observação mais próxima deq×(n−1), empate para o índice inferior; D1 usa(n−1)//2. Duplicatas são removidas e grupos menores que o nível usam todas as rows disponíveis. As identidades/effective_rows_per_group estão congeladas em cada spec. GROUP_EQUAL atribui1/n selecionado, total1 por grupo em todos os níveis.

Em C, os mesmos grupos e exatamente as mesmas rows DALL recebem pesos1 ou1/n. A mudança também altera os totais por classe quando os números de observações diferem; ela não separa esses dois componentes. Bootstrap RF não garante influência efetiva idêntica por grupo, embora a soma dos pesos fornecidos seja controlada. Nenhum class_weight foi aplicado.

Parâmetros RF integrais, preservados em cada um dos100 registros:

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

Features: canal0 STRUCTURAL_Y, canal1 RELATIVE_SOLUTE_FIELD_Y, patches65×65uint8. Em cada canal LBP P8/R1/uniform, dez bins/range(0,10)/density=True; concatenação20. O campo solutal é relativo, nunca Bi absoluto. Nenhum scaler, seed adicional, threshold adaptativo ou feature nova.

## Part A — diversidade de grupos

As tabelas arredondam para nove casas somente para leitura. JSONs preservam os valores integrais. Desvio padrão é descritivo populacional(ddof0), não erro padrão, intervalo de confiança ou teste de significância. Em K<24 há20 fits; K24 tem quatro. Cada baseline K24 é reutilizado em cinco pares dentro do fold, portanto os20 deltas não são experimentos independentes.

| K/classe | Escopo | Média GMBA | Mediana | DP | Mín | Máx | n_fits |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 4 | global | 0.775093409 | 0.773867512 | 0.043430735 | 0.700995711 | 0.847096474 | 20 |
| 4 | bottom_up_anti_parallel | 0.798509162 | 0.796391481 | 0.046586278 | 0.708994741 | 0.874551399 | 20 |
| 4 | top_down_parallel | 0.704846148 | 0.700316849 | 0.073451191 | 0.572784810 | 0.821518987 | 20 |
| 8 | global | 0.768897448 | 0.760823752 | 0.045814331 | 0.696232124 | 0.856973449 | 20 |
| 8 | bottom_up_anti_parallel | 0.782931727 | 0.784577453 | 0.052444887 | 0.687843190 | 0.871512516 | 20 |
| 8 | top_down_parallel | 0.726794613 | 0.719007481 | 0.053676982 | 0.626332515 | 0.826289264 | 20 |
| 12 | global | 0.778496186 | 0.795368759 | 0.050126246 | 0.693467935 | 0.846219077 | 20 |
| 12 | bottom_up_anti_parallel | 0.792057082 | 0.815574059 | 0.061662333 | 0.680691221 | 0.859893337 | 20 |
| 12 | top_down_parallel | 0.737813497 | 0.743648859 | 0.049373147 | 0.636268802 | 0.822867939 | 20 |
| 17 | global | 0.774764878 | 0.789291226 | 0.050808057 | 0.691942553 | 0.850423906 | 20 |
| 17 | bottom_up_anti_parallel | 0.787666222 | 0.811225780 | 0.061500498 | 0.680704043 | 0.861622637 | 20 |
| 17 | top_down_parallel | 0.736060845 | 0.737751973 | 0.046315510 | 0.634783349 | 0.816827710 | 20 |
| 24 | global | 0.778669209 | 0.792198746 | 0.047800644 | 0.701235417 | 0.829043925 | 4 |
| 24 | bottom_up_anti_parallel | 0.794864993 | 0.815016499 | 0.058106947 | 0.697644136 | 0.851782837 | 4 |
| 24 | top_down_parallel | 0.730081857 | 0.736418224 | 0.034230981 | 0.682911392 | 0.764579586 | 4 |

| Contraste global | Delta médio | Mediana | Positivos | Zeros | Negativos |
| --- | --- | --- | --- | --- | --- |
| K24_MINUS_K4 | 0.003575800 | 0.000860546 | 11 | 0 | 9 |
| K24_MINUS_K8 | 0.009771760 | 0.001515199 | 12 | 0 | 8 |
| K24_MINUS_K12 | 0.000173023 | -0.002850184 | 8 | 0 | 12 |
| K24_MINUS_K17 | 0.003904331 | 0.001946324 | 11 | 0 | 9 |

O contraste primário K24−K17 teve média positiva, mas11/20 deltas positivos, abaixo dos15/20 previamente exigidos para CONSISTENT_POSITIVE. Descritor **MIXED_POSITIVE**. A curva não é monotônica: K8<K4 e K17<K12. K24−K12 é praticamente nulo em média(+0,0001730225502605043), com mediana negativa e somente8/20 deltas positivos. Não houve regra nova após observar isso.

## Part B — densidade temporal nos mesmos grupos

| Densidade | GMBA médio | Mediana | DP | Mín | Máx | Fits conceituais |
| --- | --- | --- | --- | --- | --- | --- |
| D1 | 0.778669209 | 0.792198746 | 0.047800644 | 0.701235417 | 0.829043925 | 4 |
| D3 | 0.769712446 | 0.767186172 | 0.045633765 | 0.713187750 | 0.831289688 | 4 |
| D5 | 0.773554844 | 0.772151007 | 0.054385249 | 0.710206631 | 0.839710730 | 4 |
| DALL | 0.718969899 | 0.709924001 | 0.035758053 | 0.680230646 | 0.775800945 | 4 |

| Contraste | Média delta | Mediana | Fold0 | Fold1 | Fold2 | Fold3 |
| --- | --- | --- | --- | --- | --- | --- |
| D3_MINUS_D1 | -0.008956763 | -0.003964784 | 0.011952333 | -0.010175329 | -0.039849819 | 0.002245762 |
| D5_MINUS_D1 | -0.005114365 | 0.009714446 | 0.008971214 | 0.010457678 | -0.050553157 | 0.010666805 |
| DALL_MINUS_D1 | -0.059699310 | -0.057033918 | -0.001809018 | -0.122920387 | -0.005445514 | -0.108622322 |
| DALL_MINUS_D5 | -0.054584945 | -0.065034679 | -0.010780232 | -0.133378065 | 0.045107643 | -0.119289126 |

| Nível | Rows treino fold0 | fold1 | fold2 | fold3 | Rows/grupo mín–máx |
| --- | --- | --- | --- | --- | --- |
| D1 | 48 | 48 | 48 | 48 | 1–1 |
| D3 | 143 | 140 | 139 | 139 | 1–3 |
| D5 | 239 | 231 | 230 | 230 | 1–5 |
| DALL | 7776 | 7981 | 8478 | 8486 | 1–395 |

DALL−D1 tem média **−0,059699310144642304**, e os quatro deltas globais são negativos: **NON_POSITIVE**. D5−D1 tem três folds positivos, mas sua média é negativa devido à queda maior no fold2. Assim, três sinais positivos isoladamente não garantem benefício médio. Não se identifica uma curva crescente que satura: os níveis oscilam e DALL cai. Esses resultados condicionais não provam que mais frames sempre prejudiquem outros desenhos.

## Part C — ponderação no mesmo corpus denso

| Ponderação | GMBA médio | Mediana | DP | Mín | Máx |
| --- | --- | --- | --- | --- | --- |
| GROUP_EQUAL | 0.718969899 | 0.709924001 | 0.035758053 | 0.680230646 | 0.775800945 |
| OBSERVATION_EQUAL | 0.733556801 | 0.736549871 | 0.040676826 | 0.684256983 | 0.776870478 |

| Contraste | Média | Mediana | Fold0 | Fold1 | Fold2 | Fold3 |
| --- | --- | --- | --- | --- | --- | --- |
| GROUP_EQUAL−OBSERVATION_EQUAL | -0.014586902 | -0.003641384 | -0.003256430 | -0.004026337 | -0.001069533 | -0.049995309 |

A diferença média é **−0,014586902176019961**, com0/4 positivos e4/4 negativos: **NO_GROUP_EQUAL_BENEFIT**. O resultado não modifica os pesos usados no pipeline final C, nem autoriza adotar outra opção. Trata-se exclusivamente da atribuição pós-hoc congelada.

## Diagnóstico por aquisição e métricas secundárias

| Contraste | Aquisição | Delta médio | Mediana | Positivos/zeros/negativos |
| --- | --- | --- | --- | --- |
| K24−K17 | bottom_up_anti_parallel | 0.007198771 | 0.003750974 | 13/0/7 |
| K24−K17 | top_down_parallel | -0.005978989 | -0.009059440 | 6/0/14 |
| K24−K4 | bottom_up_anti_parallel | -0.003644170 | -0.004712406 | 9/0/11 |
| K24−K4 | top_down_parallel | 0.025235709 | 0.018670886 | 11/0/9 |
| DALL−D1 | bottom_up_anti_parallel | -0.077861336 | -0.078354999 | 2/0/2 |
| DALL−D1 | top_down_parallel | -0.005213231 | -0.007043845 | 2/0/2 |
| DALL−D5 | bottom_up_anti_parallel | -0.069674399 | -0.081403598 | 2/0/2 |
| DALL−D5 | top_down_parallel | -0.009316582 | -0.002705242 | 2/0/2 |
| GROUP_EQUAL−OBSERVATION_EQUAL | bottom_up_anti_parallel | -0.015911887 | -0.003754215 | 1/0/3 |
| GROUP_EQUAL−OBSERVATION_EQUAL | top_down_parallel | -0.010611948 | -0.011478546 | 1/0/3 |

K24−K17 é positivo em bottom_up e negativo em top_down. DALL−D1 tem dois folds positivos e dois negativos **em cada aquisição**, apesar de os quatro deltas globais serem negativos. GROUP_EQUAL−OBSERVATION_EQUAL tem1/3 sinais positivos/negativos por aquisição. A composição global é3:1 por grupos de cada classe; top_down tem apenas2 sites+2 tracks em cada validação. Não se estende a consistência global automaticamente aos estratos, nem se obtêm novas aquisições independentes.

Médias descritivas por condição das métricas secundárias, sem substituir a GMBA primária:

| Condição | Obs.BA | Accuracy | Precision | Recall | F1 | Macro recall site | Macro especificidade track |
| --- | --- | --- | --- | --- | --- | --- | --- |
| K4/D1/GE | 0.729669164 | 0.683005037 | 0.543855499 | 0.912338161 | 0.675036061 | 0.882288677 | 0.667898140 |
| K8/D1/GE | 0.737300365 | 0.700608340 | 0.556721911 | 0.874903839 | 0.676316305 | 0.834747619 | 0.703047278 |
| K12/D1/GE | 0.751067187 | 0.719026026 | 0.573375458 | 0.875951239 | 0.689964740 | 0.834270573 | 0.722721799 |
| K17/D1/GE | 0.749550087 | 0.721960063 | 0.575608357 | 0.857429091 | 0.686529073 | 0.813735502 | 0.735794254 |
| K24/D1/GE | 0.742991813 | 0.705672013 | 0.559091495 | 0.887804159 | 0.683214468 | 0.854304157 | 0.703034261 |
| K24/D3/GE | 0.751121870 | 0.722090550 | 0.575063148 | 0.865041339 | 0.688434854 | 0.810759888 | 0.728665004 |
| K24/D5/GE | 0.757116632 | 0.724196896 | 0.579225325 | 0.888649889 | 0.698237998 | 0.824863724 | 0.722245963 |
| K24/DALL/GE | 0.743122944 | 0.762391096 | 0.654909207 | 0.689736465 | 0.670077936 | 0.589614464 | 0.848325333 |
| K24/DALL/OE | 0.749491652 | 0.765665959 | 0.655419589 | 0.709356080 | 0.678895125 | 0.621306376 | 0.845807226 |

| Condição | GMBA bottom_up | GMBA top_down |
| --- | --- | --- |
| K4/D1/GE | 0.798509162 | 0.704846148 |
| K8/D1/GE | 0.782931727 | 0.726794613 |
| K12/D1/GE | 0.792057082 | 0.737813497 |
| K17/D1/GE | 0.787666222 | 0.736060845 |
| K24/D1/GE | 0.794864993 | 0.730081857 |
| K24/D3/GE | 0.777457258 | 0.746478008 |
| K24/D5/GE | 0.786678056 | 0.734185208 |
| K24/DALL/GE | 0.717003656 | 0.724868625 |
| K24/DALL/OE | 0.732915543 | 0.735480573 |

Os100 registros em FIT_RESULTS.json preservam confusion matrices, cinco métricas por observação, recalls/especificidades por grupo, maioria e diagnósticos por aquisição. GROUP_DIVERSITY_RESULTS.json, TEMPORAL_DENSITY_RESULTS.json e GROUP_WEIGHTING_RESULTS.json contêm todos os deltas pareados, estatísticas e referências aos fits. Nenhuma predição ou métrica de TEST foi carregada para esta auditoria.

## Ponte narrativa para o relatório

| Condição | O que muda | O que fica fixo | GMBA médio |
| --- | --- | --- | --- |
| K4/D1/GE | Número de grupos e exemplos representativos | RF/LBP/folds/validação; densidade1 e peso/grupo | 0.775093408673069 |
| K8/D1/GE | Número de grupos e exemplos representativos | RF/LBP/folds/validação; densidade1 e peso/grupo | 0.7688974484656079 |
| K12/D1/GE | Número de grupos e exemplos representativos | RF/LBP/folds/validação; densidade1 e peso/grupo | 0.7784961861373184 |
| K17/D1/GE | Número de grupos e exemplos representativos | RF/LBP/folds/validação; densidade1 e peso/grupo | 0.7747648777763951 |
| K24/D1/GE | Referência de48grupos/48rows | RF/LBP/folds/validação; densidade1 e peso/grupo | 0.7786692086875789 |
| K24/D3/GE | Observações temporais nos mesmos grupos | RF/LBP/folds/validação/grupos/peso total por grupo | 0.7697124456485938 |
| K24/D5/GE | Observações temporais nos mesmos grupos | RF/LBP/folds/validação/grupos/peso total por grupo | 0.7735548436540266 |
| K24/DALL/GE | Observações temporais nos mesmos grupos | RF/LBP/folds/validação/grupos/peso total por grupo | 0.7189698985429366 |
| K24/DALL/OE | Ponderação das mesmas rows densas | RF/LBP/folds/validação/grupos/rows | 0.7335568007189566 |

GE=GROUP_EQUAL; OE=OBSERVATION_EQUAL. O TEST Study2-C não integra essa tabela porque não é a mesma avaliação. A tabela canônica gerada pela CLI permanece byte a byte em RESULTS_TABLES.md; a versão didática acima traduz os rótulos, sem alterar valores.

## Respostas interpretativas obrigatórias

1. **A diversidade ajudou?** Houve vantagem média pequena para K24 sobre K17 e K4, com11/20 deltas positivos em cada contraste. É evidência descritiva mista, não benefício uniforme.
2. **O benefício cresce consistentemente?** Não. As médias diminuem deK4 paraK8 e deK12 paraK17; a curva não é monotônica.
3. **O que ocorre próximo deK17?** K24 supera K17 em0,0039043309111838507 GMBA, ou0,39043309111838507 ponto percentual. K17 é apenas ponte de escala numérica. Os17 grupos por classe com mediana por grupo não reproduzem os17 samples por classe do Experimento1.
4. **Mais frames acrescentam benefício?** Neste protocolo, os níveisD3,D5,DALL não superamD1 na média global. DALL−D1 cai5,9699310144642304 pontos percentuais, com quatro folds globais negativos. Isso não equivale a provar ausência de informação física nos frames adicionais.
5. **Há saturação?** Não foi estabelecida. Os níveis oscilam e DALL cai; o desenho não identifica uma curva crescente com platô nem um ponto ótimo.
6. **A ponderação por grupo ajuda?** Não apresentou benefício no cenário denso fixo: GROUP_EQUAL ficou1,4586902176019961 ponto percentual abaixo de OBSERVATION_EQUAL em média, negativo nos quatro folds globais.
7. **Qual padrão é mais consistente?** A diversidade é o único contraste principal de média positiva, mas é misto. As quedas globais com DALL e GROUP_EQUAL são os padrões direcionais mais consistentes, ambas4/4 negativas. DALL−D1 tem a maior queda média absoluta entre esses contrastes principais, sem tornar os fatores intercambiáveis ou conferir significância.
8. **O que não pode ser atribuído causalmente?** Nenhum resultado identifica a causa total da diferença Experimento1→Study2-C, nem permite somar deltas ou dividir a melhoria em percentuais causais. A muda simultaneamente quantidade de grupos e de rows; C muda pesos por grupo e totais de classe. Os efeitos dependem dos demais fatores fixados.

O Experimento1 teve TRAIN17+17 samples e FINAL3+3, com BA2/3, usados apenas como referências textuais. Study2-C TEST GMBA0,8449139278495638 e seu efeito DEV de SILVER(+0,0016093220301962585) também são referências históricas textuais. D não usa SILVER, não reexecuta métricas antigas e não reabre a escolha RF_REFERENCE+GOLD_PLUS_SILVER. Diferenças de domínio, split, exemplos, pesos e avaliação impedem uma equivalência direta entre a ponte e o ganho histórico total.

As weak labels são evidência gráfica publicada de localizações; não são confirmação humana de eventos físicos. Background não prova ausência física. As validações são TRAIN-only, com exposição histórica declarada, duas aquisições e grupos correlacionados no tempo/contexto espacial. Os quatro folds compartilham dados de treinamento; replicates compartilham grupos e baselines. Não há p-value, significância universal, causalidade física, generalização externa, onset exato, forecasting, recall físico exaustivo, Bi absoluto ou temperatura. Nenhum novo modelo foi selecionado.

## Auditoria posterior, publicação e encerramento

A verificação posterior usa apenas textos e Git. POST_RUN_CUSTODY_AUDIT.json confere10.907 records de acesso com manifesto/offsets/três hashes,72 hashes operacionais,52 blobs do freeze original,ancestralidade e a ordem CI→receipt. Os hashes de payload são os registrados no acesso dirigido, não um rehash posterior dos containers. Os arquivos físicos dos caches não foram reabertos para a auditoria.

POST_RUN_METRIC_AUDIT.json registra a conferência aritmética independente das272.675 predições e dos agregados, sem chamar scorer/modelo/reader/planner. CLAIM_REVIEW.json registra revisão textual independente assistida por IA, sem alegar certificação humana. Logs, recibos, resultados e código permanecem intactos. Os relatórios de falha da CI original não foram convertidos retroativamente em PASS.

O checkpoint posterior contém somente novas evidências textuais nesta pasta. post-run-hashes.sha256 e VERIFICATION_TERMINAL.json delimitam a custódia. SHA do checkpoint, conclusão remota da CI final e estado local/remoto pertencem ao retorno após as operações efetivas; não são antecipados nem inseridos autorreferencialmente aqui. Nenhum novo teste científico local, extração ou fit ocorre depois da execução. A CI posterior usa fixtures sintéticas, sem fontes experimentais. Não há merge automático de D.

```text
STUDY2_D=PASS
STUDY2_D_METHOD=CONTROLLED_DATA_CENTRIC_BRIDGE_ATTRIBUTION
SCIENTIFIC_STUDY2D_RUNS=1
RF_MODEL=RF_REFERENCE
FEATURES=LBP20_MULTIMODAL
TRAIN_POSITIVE_GROUPS_AVAILABLE=32
TRAIN_BACKGROUND_GROUPS_AVAILABLE=32
CV_FOLDS=4
DISTINCT_RF_FITS=100
DEV_GROUPS_READ=0
TEST_GROUPS_READ=0
DEV_ROWS_READ=0
TEST_ROWS_READ=0
TEST_CACHE_ROWS_READ=0
TEST_FEATURES_COMPUTED=0
EXPERIMENTAL_SOURCE_OPENS=0
FFMPEG_RUNS=0
TEST_STATE=UNCHANGED_CONSUMED
NEW_MODEL_SEARCH=false
MODEL_SELECTION_REOPENED=false
STUDY2_ATTRIBUTION_ANALYSIS_COMPLETE=true
SCIENTIFIC_PROGRAM_READY_FOR_FINAL_CLOSEOUT=true
STATE=CLOSED_CONSUMED
MERGE_AUTHORIZED=false
CURRENT_AUTHORIZED_ACTIVITY=NONE_AWAITING_AUTHOR_DECISION
ESM1_OPENS=0
ESM2_OPENS=0
ESM3_OPENS=0
ESM4_OPENS=0
ESM5_OPENS=0
ESM6_OPENS=0
GROUP_DIVERSITY_DESCRIPTOR=MIXED_POSITIVE
GROUP_DIVERSITY_DELTA_K24_K17=0.0039043309111838507
GROUP_DIVERSITY_DELTA_K24_K4=0.0035758000145099554
TEMPORAL_DENSITY_DESCRIPTOR=NON_POSITIVE
TEMPORAL_DENSITY_DELTA_ALL_1=-0.059699310144642304
GROUP_WEIGHTING_DESCRIPTOR=NO_GROUP_EQUAL_BENEFIT
GROUP_WEIGHTING_DELTA=-0.014586902176019961
```
