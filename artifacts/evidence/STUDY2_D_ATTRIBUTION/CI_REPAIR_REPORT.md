# Study2-D — reparo CI aprovado; liberação condicional para preflight real

**CI_REPAIR=PASS; CI_JOBS=10/10_SUCCESS; 110/110 passos SUCCESS; SCIENTIFIC_STUDY2D_RUNS=0 neste marco.** O método científico original permanece intacto. A seção 16 da autorização complementar permite prosseguir com a única CLI científica somente após o preflight real aprovado.

| Item autoral | Verificação efetiva |
| --- | --- |
| 1. Freeze original | `21400de67d21901aeb8e5abac528689fc39169fa`; 52 hashes autenticados nos blobs originais; snapshots originais preservados |
| 2. Quatro testes | `test_exact_directed_reads_and_hashes`, `test_short_read_closes`, `test_hash_mismatch_closes`, `test_fingerprint_change_denied` |
| 3. Diff exato | [CI_REPAIR_SOURCE_DIFF.txt](CI_REPAIR_SOURCE_DIFF.txt), [CI_REPAIR_DIFF.json](CI_REPAIR_DIFF.json) e diff Git original→reparo; 27 paths, 6 M + 21 A |
| 4. Arquivos existentes alterados | tests/test_study2d_io.py; tests/test_study2d_execution.py; src/snbi_fragmentation/study2d_execution.py; configs/governance/phase-scope-v1.json; METHOD_FREEZE.json; SYNTHETIC_TESTS.json. As 21 adições são somente provas textuais delimitadas no JSON |
| 5. Ciência | SCIENTIFIC_METHOD_CHANGED=false; dataset, allowlist, folds, grupos, features, modelo, RF, métricas, budget e proibições DEV/TEST preservados |
| 6. Stdlib local | 1.139 testes: 868 passes, zero erros/falhas |
| 7. Skips stdlib | 271 = 267 opcionais anteriores + exatamente os quatro novos autorizados. Log final após acrescentar assert literal BASE; primeira passagem preservada |
| 8. Dedicado | 116/116 PASS local e remoto; remoto run 35654208330 |
| 9. Skips dedicado | Zero; os quatro testes corrigidos terminaram `ok` no log remoto |
| 10. CI_REPAIR_SHA | `8c6221da3d03a498158d812be5c08848c37c2247` |
| 11. Ancestralidade | Parent `21400de67d21901aeb8e5abac528689fc39169fa`; grandparent `ec97cb5041ef35d4f6c9a79b54d756d6fbee674f`; exatamente um filho corretivo, sem amend/rebase/force |
| 12. Dez jobs | Listados na tabela abaixo, todos no SHA do reparo |
| 13. CI | Nove workflows, dez jobs, 110 passos SUCCESS; respostas integrais em CI_PROOF.json; nenhum rerun do SHA falho |
| 14. Ciência neste marco | SCIENTIFIC_STUDY2D_RUNS=0; zero fits científicos; zero extração experimental |
| 15. DEV | DEV_ROWS_READ=0 |
| 16. TEST | TEST_ROWS_READ=0; TEST_CACHE_ROWS_READ=0; TEST_FEATURES_COMPUTED=0 |
| 17. Liberação | Gate de reparo PASS; autorizado executar preflight real, depois uma CLI/100 fits apenas se esse preflight passar. Nenhuma permissão adicional inferida |

| Job | Run | Estado |
| --- | --- | --- |
| study2b-synthetic-contracts | [35654208340](https://github.com/lmbernardo7520112/snbi-dendritic-fragmentation-ml/actions/runs/35654208340) | SUCCESS; todos os passos SUCCESS |
| study2a-synthetic-contracts | [35654208413](https://github.com/lmbernardo7520112/snbi-dendritic-fragmentation-ml/actions/runs/35654208413) | SUCCESS; todos os passos SUCCESS |
| ti3d-final-synthetic-contracts | [35654208339](https://github.com/lmbernardo7520112/snbi-dendritic-fragmentation-ml/actions/runs/35654208339) | SUCCESS; todos os passos SUCCESS |
| study2d-synthetic-contracts | [35654208330](https://github.com/lmbernardo7520112/snbi-dendritic-fragmentation-ml/actions/runs/35654208330) | SUCCESS; todos os passos SUCCESS |
| study2c-synthetic-contracts | [35654208346](https://github.com/lmbernardo7520112/snbi-dendritic-fragmentation-ml/actions/runs/35654208346) | SUCCESS; todos os passos SUCCESS |
| ti3c-synthetic-contracts | [35654208399](https://github.com/lmbernardo7520112/snbi-dendritic-fragmentation-ml/actions/runs/35654208399) | SUCCESS; todos os passos SUCCESS |
| ti3b-synthetic-contracts | [35654208320](https://github.com/lmbernardo7520112/snbi-dendritic-fragmentation-ml/actions/runs/35654208320) | SUCCESS; todos os passos SUCCESS |
| scientific-synthetic-contracts | [35654208372](https://github.com/lmbernardo7520112/snbi-dendritic-fragmentation-ml/actions/runs/35654208372) | SUCCESS; todos os passos SUCCESS |
| deterministic-contracts | [35654208372](https://github.com/lmbernardo7520112/snbi-dendritic-fragmentation-ml/actions/runs/35654208372) | SUCCESS; todos os passos SUCCESS |
| ti3-synthetic-contracts | [35654208382](https://github.com/lmbernardo7520112/snbi-dendritic-fragmentation-ml/actions/runs/35654208382) | SUCCESS; todos os passos SUCCESS |

Os 72 hashes operacionais e as 47 entradas originais não modificadas foram conferidos independentemente. O preflight preparatório usa textos reais e Git/CI futuros explicitamente simulados; não substitui a prova real. A revisão operacional adicional não executou testes, fit ou pixels. O scope guard aprovou 776 entradas, 146 Python classificados; 95 checksums históricos passaram.

A autenticação dirigida TRAIN da integração C já estava concluída e não foi repetida durante o reparo. Os dois fits RF locais deste reparo são exclusivamente sintéticos; acumulado local sintético de oito, distinto dos 100 fits científicos ainda não iniciados neste marco.

O relatório local do bloqueio foi preservado byte a byte como CI_BLOCKED_REPORT.md para reservar EXECUTION_REPORT.md ao resultado científico. O catálogo antigo foi preservado e o catálogo corrente altera somente esse path. `git diff --check` integral sinalizou espaços das linhas de contexto dos dois diffs brutos e do log GH original; essas evidências foram conservadas. Os demais 24 arquivos passaram a conferência de whitespace. Nenhuma ciência foi alterada para resolver esse detalhe documental.

Publicação: um commit corretivo, push fast-forward. Index e tracked limpos; academic-deliverable-build/ preservado. Este documento registra a liberação anterior ao preflight e não antecipa o resultado científico.
