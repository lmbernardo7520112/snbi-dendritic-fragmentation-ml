# TI3-A integrado; TI3-B — ablação incremental solutal concluída

**TI3_A_INTEGRATION=PASS; TI3_B=PASS; SOLUTAL_ABLATION=COMPLETED.**
Uma execução científica multimodal, sem retry ou tuning. DEVELOPMENT atingiu
balanced accuracy 0,75, contra a referência estrutural consumida de 0,6875:
delta +0,0625. Pela regra congelada, a preferência de desenvolvimento é
STRUCTURAL_PLUS_RELATIVE_SOLUTE. FINAL estrutural e solutal continuam com
zero opens/bytes. A autoridade científica está CLOSED_CONSUMED.

## Os 25 itens do retorno autoral

| Item | Resultado comprovado |
| --- | --- |
| 1. TI3-A PR | [#11](https://github.com/lmbernardo7520112/snbi-dendritic-fragmentation-ml/pull/11), criado Draft, CI aprovada, Ready e MERGED |
| 2. Merge TI3-A | `7a205327b363f8cdbba99c5e58bf2f1e5d1253d3`; merge commit, sem squash/rebase ou exclusão de branch |
| 3. CI pós-merge | Runs 35463972857 e 35463972865 SUCCESS; deterministic-contracts, scientific-synthetic-contracts e ti3-synthetic-contracts e todos os passos SUCCESS |
| 4. Branch/base TI3-B | `feat/ti3b-solutal-ablation`, criada exatamente no merge acima após sincronização fast-forward de main |
| 5. B1 freeze | `965e2f10e25eef1fe45ac91c10b8424389f99c10`, filho direto do merge, 18 paths e 67 hashes textuais congelados |
| 6. CI B1 | Runs 35465077671, 35465077653 e 35465077709 SUCCESS; os três jobs anteriores mais ti3b-synthetic-contracts, todos os passos aprovados |
| 7. Buffers solutais | ESM2:73/146/219; ESM5:98/197, exatamente uma abertura cada |
| 8. Bytes | Solutais: 9.734.526; estruturais: 9.734.526; total: 19.469.052 em dez opens |
| 9. FINAL estrutural | ESM1:293 e ESM4:295: zero opens, tentativas e bytes |
| 10. FINAL solutal | ESM2:293 e ESM5:295: zero opens, tentativas e bytes |
| 11. Features | Y nativa, patches 65×65; [STRUCTURAL_LBP_10, SOLUTAL_LBP_10]; dimensão 20; LBP P8/R1/uniform, dez bins/range(0,10)/density=True por modalidade |
| 12. RF | 100 árvores, random_state42, demais parâmetros idênticos a TI3-A, integralmente registrados em results.json e config congelada |
| 13. Runs TI3-B | Uma CLI científica, uma chamada multimodal, um fit TRAIN, uma avaliação DEV; zero retry/tuning; nenhum fit/avaliação estrutural repetido |
| 14. TRAIN | 34 samples, 17/17; BA=accuracy=precision=recall=F1=1; TN17/FP0/FN0/TP17 |
| 15. DEV | 16 samples, 8/8; BA=accuracy=0,75; precision=0,6666666666666666; recall=1; F1=0,8 |
| 16. Confusão DEV | [[4,4],[0,8]], linhas verdadeiro/colunas predito, classes [0,1]; TN4/FP4/FN0/TP8 |
| 17. Referência estrutural BA | 0,6875, consumida e preservada, sem reexecução |
| 18. Multimodal BA | 0,75 em DEVELOPMENT |
| 19. Delta BA | +0,0625, ou +6,25 pontos percentuais; descrição sem teste de significância |
| 20. Preferência DEV | STRUCTURAL_PLUS_RELATIVE_SOLUTE pela regra estrita >0,6875, congelada em B1 |
| 21. Limites | Weak labels, DEV16/FINAL6, exposição histórica, confusão potencial classe/aquisição, patches não são aquisições independentes; sem generalização externa |
| 22. Commit de evidências | B2 será exclusivamente documental; SHA efetivo pertence ao histórico Git e retorno ao operador, sem autorreferência |
| 23. CI final | CI de B2 deve ser consultada após publicação e informada no retorno; este arquivo não antecipa seu resultado |
| 24. Worktree/index | Ciência/versionados B1 intactos; novos textos de evidência na allowlist. Estado final será conferido após B2 e informado no retorno |
| 25. Terminal | PASS; CLOSED_CONSUMED; NONE_AWAITING_AUTHOR_DECISION; TI3-C e merge TI3-B não autorizados |

## Integração e freeze

O pre-merge confirmou HEAD local/remoto TI3-A
`cab4fcd6f2d1fb70027cc6abff2590fae3d7c64b`, worktree/index limpos, C2 somente
12 evidências e filho direto de C1 `e6090121471faa8902f68ddd045ab8b54a2e77fc`.
Auditoria independente conferiu freeze45, hashes finais57, checksums95 e a
geometria do split sem reexecutar o planner. A CI do PR #11 passou nos runs
35463800860/35463800878 antes de Ready/merge. O merge preservou parents
`67786bd4e23406e7f19860a53fe237e6d7b648cb` e o head TI3-A; sua árvore é
idêntica ao head auditado. Os três jobs pós-merge passaram antes da criação
da branch nova. `integration-audit.json` registra essas verificações.

O protocolo, configuração e ordem das features foram fixados antes dos pixels.
Os 52 sites, 108 observações, 383 IGNORE, backgrounds, split, sample_id,
contextos e centros não foram refeitos ou alterados. Manifesto preservado:
`c8e82b72ff5dc51d188a764c577c11d514474b14d90aea6292c1439e776fb487`.

Código e workflow TI3-A ficaram intactos. O único arquivo anterior editado
em B1 é o manifesto de escopo: cinco novos paths foram acrescentados,
preservando todos os modos/blobs 75 LEGACY + quatro A0 + 15 TI3 anteriores.
Um workflow TI3-B adicional não removeu jobs existentes. Nenhum checksum
histórico/ativo foi substituído. A cópia antiga do manifesto está preservada
no Git do merge; o freeze histórico não foi reescrito para fingir igualdade
do manifesto operacional ampliado.

Testes locais: 20 novos do núcleo e 24 de execução, isoladamente aprovados;
perfil combinado 153 PASS/zero skips; stdlib579, 462 passes/117 skips opcionais.
Os cinco fits RF sintéticos locais são separados do único fit experimental.
Sete controles adicionais percorreram o preflight com textos reais e Git/CI
simulados, antes de B1, sem receipt ou buffers. Eles não são prova CI real.
Uma comparação preparatória detectou a diferença factual entre hash planejado
nulo e hash observado TI3-A; foi corrigida antes de B1, com evidência anterior
preservada e nova conferência textual aprovada. Nenhum reparo ocorreu depois
do freeze ou da exposição dos pixels.

`ci-proof.json` preserva as respostas dos três runs de B1, quatro jobs e seus
passos concluídos antes do receipt. O preflight real, com os blobs B1 e a
configuração serializada final, passou com zero opens/bytes e sem armar receipt;
o runner repetiu internamente a validação antes da única execução.

## Execução única e I/O real

Comando no sandbox padrão, exatamente uma invocação, exit 0:

```text
PYTHONPATH=src .venv/bin/python -B scripts/run_ti3b_ablation.py
```

Receipt exclusivo O_EXCL+fsync: **2026-09-19T19:43:30.084477+00:00**, vinculado
ao B1, ao manifesto e ao freeze. O receipt é anterior a qualquer byte
experimental. A prova de CI mais tardia terminou às 19:41:25 UTC.

| Modalidade e buffers | Split | Opens | Bytes |
| --- | --- | ---: | ---: |
| ESM1:73/146 e ESM4:98 | TRAIN estrutural | 3 | 5.843.016 |
| ESM1:219 e ESM4:197 | DEVELOPMENT estrutural | 2 | 3.891.510 |
| ESM2:73/146 e ESM5:98 | TRAIN solutal | 3 | 5.843.016 |
| ESM2:219 e ESM5:197 | DEVELOPMENT solutal | 2 | 3.891.510 |
| ESM1:293/ESM4:295 | FINAL estrutural | 0 | 0 |
| ESM2:293/ESM5:295 | FINAL solutal | 0 | 0 |

Cada hash nativo foi calculado durante sua única leitura e corresponde ao
piloto congelado. Nenhum arquivo foi reaberto para hash ou inspeção. A releitura
estrutural nesta fase reconstruiu componentes LBP antes mantidos em memória;
não chamou o baseline estrutural. Os 50 hashes de patches estruturais são
idênticos aos materializados em TI3-A. Cinquenta pares de patches e vetores
de 20 features foram usados em memória, sem exportar arrays ou modelo.

Suporte estrutural: guard cromático/geometria TI3-A intacto. Suporte solutal:
geometria histórica 12%/15%/borda4, com guarda LBP de um pixel, sem tratar cor
do campo solutal como overlay. Essa distinção é anterior à execução e está
documentada no protocolo. Todos os 50 pares passaram antes do fit; nenhum
sample foi substituído ou removido. A rotina estrutural processou os planos
nativos necessários ao seu guard; não se alega leitura apenas dos pixels dos
patches. Solutal usou somente Y como representação científica.

Os quatro buffers FINAL permaneceram NOT_OPENED, sem tentativas, hash
observado, suporte experimental ou feature; os seis samples finais mantêm
hashes de patches/features nulos. Não houve ESM3/6, fonte externa, novo frame,
ZIP, MP4, FFmpeg/FFprobe, nova decodificação ou novo registro.

## Métricas e interpretação restrita

| Métrica | TRAIN multimodal | DEVELOPMENT multimodal | DEVELOPMENT estrutural histórico |
| --- | ---: | ---: | ---: |
| Balanced accuracy | 1,0 | 0,75 | 0,6875 |
| Accuracy | 1,0 | 0,75 | 0,6875 |
| Precision | 1,0 | 0,666667 | 0,615385 |
| Recall | 1,0 | 1,0 | 1,0 |
| F1 | 1,0 | 0,8 | 0,761905 |

A tabela arredonda somente a apresentação. Decisão e delta usam os valores
integrais de `results.json`, que contém parâmetros RF completos, versões,
predições, probabilidades e ordem dos samples. Não houve segunda seed, modelo,
representação alternativa, otimização de threshold ou estatística adicional.
O desempenho TRAIN é ressubstituição e não estima generalização.

A representação do campo solutal relativo forneceu informação discriminativa
incremental no DEVELOPMENT interno sob o protocolo LBP/RF congelado. A melhora
é descritiva, com oito samples por classe e somente um acerto líquido adicional.
Não se alega significância estatística, utilidade externa ou independência
experimental de patches. A preferência orienta somente a decisão de
desenvolvimento prevista pelo autor; não abre FINAL nem inicia outra fase.

TRAIN preserva ESM1 16 positivos/6 backgrounds e ESM4 1/11: classe e aquisição
podem estar confundidas. FINAL tem apenas 3/3 e permanece com exposição
histórica não ML declarada, sem virgindade global. Weak labels representam
localização cumulativa publicada; background não demonstra ausência física
e FP não comprova falsa fragmentação física. Não há recall físico exaustivo,
onset exato, forecasting, causalidade, concentração absoluta de Bi, temperatura
ou generalização externa. Não houve CNN, augmentation ou alteração de G2.

## Custódia e encerramento

A revisão posterior usa somente JSON, hashes textuais e Git. Nenhum kernel,
feature extractor, runner ou buffer é reexecutado/reaberto. O receipt e
`results.json` fecham permanentemente a autoridade nova. Configurações antigas
continuam consumidas. `post-run-hashes.sha256` e `verification-terminal.json`
registram a integridade final; os inventários de comandos são delimitados e
não constituem monitoramento universal de syscalls.

B2 contém exclusivamente evidência textual. Seu SHA, publicação, CI final e
estado Git após o commit pertencem ao retorno efetivo ao operador. Não haverá
Ready, merge TI3-B, exclusão de branch, tuning, retry ou nova execução.

```text
TI3_A_INTEGRATION=PASS
TI3_B=PASS
SOLUTAL_ABLATION=COMPLETED
SCIENTIFIC_TI3B_RUNS=1
DEV_MODALITY_PREFERENCE=STRUCTURAL_PLUS_RELATIVE_SOLUTE
ML_FINAL_TEST=SEALED_WITH_HISTORICAL_NON_ML_EXPOSURE
ML_FINAL_TEST_EXECUTED=false
FORECASTING_AUTHORIZED=false
CAUSALITY_CLAIM_AUTHORIZED=false
EXTERNAL_GENERALIZATION_CLAIM=false
TI3_C_READY_FOR_AUTHOR_DECISION=true
TI3_C_AUTHORIZED=false
MERGE_AUTHORIZED=false
TI3_B_EXECUTION_AUTHORIZED=false
STATE=CLOSED_CONSUMED
CURRENT_AUTHORIZED_ACTIVITY=NONE_AWAITING_AUTHOR_DECISION
```
