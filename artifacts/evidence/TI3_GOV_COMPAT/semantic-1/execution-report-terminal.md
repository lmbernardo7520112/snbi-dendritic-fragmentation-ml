# TI3-GOV-COMPAT — partição aprovada; bloqueio na CI de C0

**TI3_GOV_COMPAT=BLOCKED_C0_CI.** A classificação semântica e os guards
passaram. O único C0 foi criado e publicado, mas o workflow TI3 terminou
em FAILURE antes de criar jobs. A seção 25 da autorização manda STOP nesse
caso. C1/C2 não foram criados; nenhum pixel, patch, feature experimental ou
treinamento foi iniciado. Não houve rerun nem commit corretivo.

A causa específica da falha remota é **NOT_VERIFIED**. O comando gh run view
informa apenas provável problema no arquivo de workflow. A API retornou
jobs=[] e check_runs=[], sem mensagem específica de validação. Não se atribui
essa falha a um erro YAML demonstrado, a dependências ou ao baseline científico.
Executar os blocos Python localmente não validou a admissão do workflow pelo
GitHub; essa limitação da verificação preparatória fica explícita.

## Trinta itens do retorno autoral

| Item | Evidência e resultado |
| --- | --- |
| 1. HEAD inicial | 41d523e038e844588ee7724e07b00f75bdf29fdc |
| 2. Snapshot do bloqueio | ../pre-ti3-code-scope.blocked-snapshot.json; cópia exata, 15.859 bytes, SHA-256 3c63b51ff86aeda79244d09e5bc7f5196be01f8aa8672ab3dc2f8fe6d90f9971; sete textos anteriores intactos |
| 3. Corpus cronológico | 79 Python tracked no baseline, enumerados no snapshot; classificação histórica não usada como domínio TI2 |
| 4. LEGACY_TI2 | 75 paths explicitamente enumerados no manifesto normativo; modos/blobs Git e bytes do worktree conferidos |
| 5. A0 congelado | Exatamente quatro paths; listagem e blobs abaixo; nenhum modificado |
| 6. Blobs A0 | Obtidos de git ls-tree no baseline, conferidos com índice e worktree; tabela abaixo |
| 7. TI3_ACTIVE | 15 paths explícitos: quatro de governança TRACKED e onze científicos PLANNED; lista abaixo |
| 8. Unclassified | 0 |
| 9. Duplicate classification | 0 |
| 10. Legacy guard | PASS sobre os 75; check_ti2_scope.py byte-idêntico |
| 11. A0 frozen guard | PASS; remoção, rename, quinto membro, alteração de modo/blob e dupla classe bloqueiam |
| 12. TI3 guard | PASS; quatro pins exatos, dependências do projeto vazias, imports limitados |
| 13. Phase guard | PASS no índice real após staging, além das verificações anteriores explicitamente identificadas |
| 14. Testes | 41 novos testes PASS; perfil CI C0 local: 59 PASS, zero skips; suíte histórica stdlib: 444 testes, 350 passes/94 skips opcionais |
| 15. Snapshot histórico | PASS; 95 entradas, 10.212 bytes; SHA-256 e7d30ca626088e1e3c58c8702b96e9afc388ee75c48011d885393230dc7d245d |
| 16. Checksum ativo | 95/95 PASS; somente hash de .github/workflows/ci.yml alterado; old/new em active-checksum-changes.json |
| 17. C0 | 272695a4420e37fddf6674664d0040ef064c153f, único commit, 29 paths exatos; parent igual ao HEAD inicial |
| 18. CI C0 | FAIL no workflow TI3; dois jobs históricos SUCCESS; runs e passos preservados em remote-ci.json |
| 19. C1 | NOT_CREATED |
| 20. CI C1 | NOT_RUN |
| 21. Real-support | NOT_EXECUTED |
| 22. TRAIN/DEV opens | 0; bytes=0; planos 17+17 e 8+8 preservados |
| 23. FINAL opens | 0; bytes=0; seis samples planejados preservados |
| 24. Scientific ML runs | 0; nenhum fit experimental |
| 25. TRAIN metrics | NOT_EVALUATED |
| 26. DEV metrics | NOT_EVALUATED |
| 27. DEV confusion matrix | NOT_EVALUATED; TP/FP/TN/FN não calculados |
| 28. Limitações | TRAIN confunde potencialmente classe/aquisição; FINAL somente 3 positivos/3 backgrounds, baixa potência e granularidade; exposição histórica declarada; sem generalização externa |
| 29. C2 | NOT_CREATED; estes registros de encerramento ficam locais e não staged |
| 30. Terminal | BLOCKED_C0_CI; CLOSED_BLOCKED_C0_CI; NONE_AWAITING_AUTHOR_DECISION |

O [manifesto normativo](../../../../configs/governance/phase-scope-v1.json)
contém a enumeração completa dos 75 legados e de todas as classes. A classificação
é semântica, exaustiva e disjunta; a âncora de custódia continua o baseline Git.

| A0 — todos mode 100644 | Git blob SHA |
| --- | --- |
| scripts/extract_ti3_a0_annotations.py | edcd947bd4268d89153452b0518130499ef9617d |
| scripts/inspect_ti3_a0_annotations.py | 5600ff86f55b61709b75ad380a287347dd302dbd |
| src/snbi_fragmentation/ti3_a0_annotations.py | 879083a025e8734ac2a066c9457eac8ecb5d8cb2 |
| tests/test_ti3_a0_annotations.py | 222664f90128b7cadb32c31720511563e11b4065 |

TI3_ACTIVE TRACKED no C0:

- scripts/check_phase_scope.py
- scripts/check_ti3_scope.py
- tests/test_phase_scope.py
- tests/test_ti3_scope.py

TI3_ACTIVE PLANNED, preservados localmente e ausentes de C0:

- scripts/build_ti3_manifest.py
- scripts/check_ti3_ml_environment.py
- scripts/run_ti3_baseline.py
- src/snbi_fragmentation/ti3_baseline.py
- src/snbi_fragmentation/ti3_dataset.py
- src/snbi_fragmentation/ti3_execution.py
- src/snbi_fragmentation/ti3_support.py
- tests/test_ti3_baseline.py
- tests/test_ti3_dataset.py
- tests/test_ti3_execution.py
- tests/test_ti3_support.py

## Publicação, CI e parada

Branch local e remota: feat/ti3-canonical-dataset-baseline, ambas no C0.
main remoto permanece 67786bd4e23406e7f19860a53fe237e6d7b648cb.
O primeiro push criou a branch remota sem force; todo o histórico foi preservado.
Não houve PR, Ready, merge, exclusão de branch ou alteração de main.

O run [35455982908](https://github.com/lmbernardo7520112/snbi-dendritic-fragmentation-ml/actions/runs/35455982908)
terminou SUCCESS no SHA C0: deterministic-contracts e
scientific-synthetic-contracts, com todos os passos SUCCESS, inclusive escopo
composto, checksums e testes históricos. O run
[35455982251](https://github.com/lmbernardo7520112/snbi-dendritic-fragmentation-ml/actions/runs/35455982251)
terminou FAILURE no mesmo SHA, sem jobs. Check-suite 96015940253 sem check-runs.
Os dois primeiros jobs verdes não satisfazem a exigência de toda a CI verde.

A consulta remota, staging, commit e push usaram somente aprovações pontuais.
As falhas de DNS/API no sandbox estão registradas; não houve instalação,
alteração do SO, leitura de credenciais, Full Access ou correção do sandbox.
Nenhum runner científico foi chamado. O planejamento e a autoridade anterior
fechada não foram reativados.

O erro de cabeçalho comentado no auxiliar de leitura dos checksums ocorreu
antes de qualquer escrita; sua chamada e a leitura subsequente constam do
journal C0. Não é tratado como falha científica ou tentativa de treinamento.
Os testes de governança foram invocados isoladamente e novamente no perfil
da CI; não se apresentam essas invocações como casos sintéticos adicionais.

TRAIN ESM1 permanece 16 positivos/6 backgrounds; ESM4, 1/11. Nenhum background
foi reselecionado. FINAL permanece reservado com exposição histórica não ML,
nunca chamado globalmente virgem. A tarefa continua restrita à localização
publicada sob supervisão fraca; não demonstra fragmentação física exaustiva,
onset, forecasting, causalidade, Bi absoluto ou benefício solutal.

## Custódia terminal

O relatório de C0 e seus 29 arquivos permanecem byte-idênticos ao commit.
Os históricos TI3-A0, TARGET_RESOLUTION e os terminais bloqueados anteriores
permanecem intactos. Os 39 arquivos locais preparados que restam fora do C0
permanecem preservados; o único workflow preparado alterado pertence ao C0
expressamente autorizado. Não houve alteração de núcleo científico, split,
patch, máscara, limiar, parâmetros LBP/RF ou métricas.

Os únicos novos arquivos após a publicação são remote-ci.json,
terminal-state.json, commands-post-publication.json, este relatório e
post-publication-verification.json, todos nesta pasta e não staged.
O índice e o conteúdo versionado permanecem limpos; o worktree contém os
arquivos científicos previamente preparados e essas evidências locais.
Não se declara o worktree inteiro limpo.

Os inventários de comandos são delimitados e não constituem monitoramento
universal de syscalls. As verificações finais usam exclusivamente textos,
índice e histórico Git, sem abertura de conteúdo experimental.

```text
TI3_GOV_COMPAT=BLOCKED_C0_CI
SEMANTIC_SCOPE_RECLASSIFICATION=PASS
C0=COMMITTED_PUBLISHED
C0_CI=FAIL
C1=NOT_CREATED
C2=NOT_CREATED
EXPERIMENTAL_OPENS=0
EXPERIMENTAL_BYTES=0
SCIENTIFIC_ML_RUNS=0
ML_FINAL_TEST=SEALED_WITH_HISTORICAL_NON_ML_EXPOSURE
ML_FINAL_TEST_EXECUTED=false
SOLUTAL_MODEL_INPUT=NOT_USED
TI3_B_AUTHORIZED=false
MERGE_AUTHORIZED=false
CURRENT_AUTHORIZED_ACTIVITY=NONE_AWAITING_AUTHOR_DECISION
```
