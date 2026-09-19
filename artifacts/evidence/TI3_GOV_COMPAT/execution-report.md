# TI3-GOV-COMPAT — bloqueio do corpus LEGACY exigido pelo anexo

**TI3_GOV_COMPAT=BLOCKED_LEGACY_BASELINE_CLASSIFICATION.**
O primeiro gate legado falhou antes de qualquer mudança de CI ou implementação
dos novos checkers. Foi aplicado exatamente o corpus de código tracked no
HEAD autorizado, sem omissões. Não houve C0/C1/C2, publicação, CI remota,
acesso experimental ou treinamento.

## Autoridade e integridade inicial

A decisão desta tentativa está em [authorization.md](authorization.md),
cópia byte-idêntica do novo anexo. HEAD inicial e final:
`41d523e038e844588ee7724e07b00f75bdf29fdc`.
Branch: `feat/ti3-canonical-dataset-baseline`.

Os 41 arquivos locais da preparação anterior conferiram byte a byte com a
verificação terminal precedente. Index e conteúdo versionado estavam limpos.
Os 25 textos G2 também mantinham os hashes. Nenhum método, target, ledger,
split, background, patch, LBP, RF ou métrica anterior foi refeito ou modificado.

## Freeze executado antes de mudanças de governança/CI

[pre-ti3-code-scope.json](../../../configs/governance/pre-ti3-code-scope.json)
registra **79 arquivos Python** já tracked no HEAD exato, sob src/scripts/tests.
Cada entrada contém path, git_mode, blob_sha e
classification=LEGACY_PRE_TI3, como exige a seção 6. Nenhum arquivo TI3 ainda
não tracked entrou nesse corpus. SHA-256 do manifesto:

`3c63b51ff86aeda79244d09e5bc7f5196be01f8aa8672ab3dc2f8fe6d90f9971`.

O snapshot [checksums-pre-ti3-41d523e.sha256](../TI2/checksums-pre-ti3-41d523e.sha256)
é cópia byte-for-byte do manifesto ativo no baseline: **95 entradas,
10.212 bytes**, SHA-256:

`e7d30ca626088e1e3c58c8702b96e9afc388ee75c48011d885393230dc7d245d`.

O manifesto ativo permaneceu intacto: zero entradas atualizadas.
Os dois snapshots novos são locais e não staged; não houve commit que
antecipasse aprovação dos gates de C0.

## Gate executado e conflito demonstrado

Primeiro passou o data guard GLOBAL: 329 entradas tracked, zero bytes de conteúdo
experimental. Depois foram autenticados os 79 blobs e modos do corpus contra
o baseline e o worktree. Todos conferiram. A cobertura dos Python relevantes
tracked foi exata: **79 classificados, zero não classificados**.

Foi então executada uma única chamada:

```python
check_ti2_scope.audit(entries=LEGACY_ENTRIES)
```

Resultado: **BLOCKED, comando exit 1**, com exatamente estas três violações:

| Path já tracked em 41d523e | Motivo |
| --- | --- |
| scripts/extract_ti3_a0_annotations.py | componente annotations proibido no escopo LEGACY |
| scripts/inspect_ti3_a0_annotations.py | componente annotations proibido no escopo LEGACY |
| src/snbi_fragmentation/ti3_a0_annotations.py | componente annotations proibido no escopo LEGACY |

A íntegra está em [legacy-scope-gate.json](legacy-scope-gate.json).
O quarto arquivo A0, tests/test_ti3_a0_annotations.py, também foi incluído;
o checker não aplica a regra de nomes aos paths tests/.

O conflito está entre a classificação exigida pela seção 6, a aplicação do
checker imutável exigida pelas seções 11/13 e o PASS obrigatório da seção 19.
Esses três arquivos já pertencem ao HEAD escolhido, portanto continuam
LEGACY_PRE_TI3 quando se cumpre a regra de baseline. A composição com novos
arquivos TI3 não elimina suas violações no domínio legado.

Não se atribuiu o bloqueio ao antigo TI3_PLUS_AUTHORIZED=false: a nova decisão
autoriza a migração e a continuação condicional. O bloqueio é o comportamento
efetivo da classificação e do checker exigidos, confirmado por auditoria
independente somente textual.

A seção 33 determina STOP diante de qualquer gate falho. Não removi membros
do manifesto, reclassifiquei os três silenciosamente, renomeei arquivos,
afrouxei o checker ou tentei uma segunda composição. Os checkers TI3/phase,
a alteração de CI e os testes de migração não foram iniciados após essa falha.

Para retomar, é necessário explicitar o tratamento operacional dos arquivos A0
já versionados dentro da fronteira de baseline. A decisão precisa preservar
sua custódia por blob e definir seu domínio de auditoria sem exclusão silenciosa.
Não é necessário modificar target, dataset planejado ou parâmetros científicos.

## Retorno dos 30 itens solicitados

| Item | Resultado real |
| --- | --- |
| 1. HEAD inicial |41d523e038e844588ee7724e07b00f75bdf29fdc|
| 2. Manifesto pré-TI3 |Criado; 79 entradas; SHA acima|
| 3. Snapshot de checksums |Criado; 95 entradas byte-idênticas; SHA acima|
| 4. Arquivos LEGACY classificados |79, incluindo quatro arquivos A0|
| 5. Arquivos TI3 classificados no novo domínio |NOT_REACHED; nova allowlist não criada|
| 6. Unclassified paths |0 entre os 79 Python relevantes tracked; não afirma cobertura dos arquivos locais untracked|
| 7. Legacy guard |BLOCKED; três violações de paths A0|
| 8. TI3 guard |NOT_IMPLEMENTED_NOT_RUN_STOP|
| 9. Composed guard |NOT_IMPLEMENTED_NOT_RUN_STOP|
| 10. C0 SHA |NOT_CREATED|
| 11. C0 CI |NOT_RUN|
| 12. C1 SHA |NOT_CREATED|
| 13. C1 CI |NOT_RUN|
| 14. Experimental opens |0|
| 15. Bytes experimentais |0|
| 16. Real-support guard |NOT_EXECUTED|
| 17. TRAIN válido |17 positivos +17 backgrounds planejados historicamente; zero materialização/validação de pixels nesta tarefa|
| 18. DEV válido |8 positivos +8 backgrounds planejados; zero materialização/validação de pixels|
| 19. FINAL opens/bytes |0/0; seis samples planejados preservados|
| 20. Scientific ML runs |0|
| 21. LBP |P8/R1/uniform, dez bins, range(0,10), density=True; inalterado e não executado|
| 22. RF |100 árvores, seed42, demais defaults registrados; inalterado e não executado|
| 23. TRAIN metrics |NOT_EVALUATED|
| 24. DEV metrics |NOT_EVALUATED|
| 25. DEV confusion matrix |NOT_EVALUATED|
| 26. Limitações |FINAL com3 positivos/3 backgrounds; baixa potência e alta granularidade; sem claims externos|
| 27. C2 SHA |NOT_CREATED|
| 28. CI final |NOT_RUN; nenhuma CI remota falhou nesta tarefa|
| 29. Worktree/index |Nenhum diff versionado ou staging; 41 arquivos anteriores preservados e nove novos textos locais desta tentativa|
| 30. Terminal |BLOCKED_LEGACY_BASELINE_CLASSIFICATION; aguardando decisão autoral|

O desequilíbrio histórico por aquisição em TRAIN também permanece declarado:
ESM1 tem16 positivos/6 backgrounds e ESM4 tem1 positivo/11 backgrounds.
Não se alterou essa seleção. O futuro FINAL terá interpretação descritiva/interna,
separação já planejada e histórico de exposição declarado; não sustenta
generalização externa. A anotação publicada não é recall físico exaustivo,
onset, forecasting, causalidade ou benefício solutal.

## Arquivos produzidos e limites

Foram criados apenas:

- configs/governance/pre-ti3-code-scope.json;
- artifacts/evidence/TI2/checksums-pre-ti3-41d523e.sha256;
- nesta pasta: authorization.md, preflight.json, legacy-scope-gate.json,
  results.json, commands.json, verification.json e execution-report.md.

Nenhum código, CI, guard, checksum ativo, configuração científica ou evidência
anterior foi alterado. Não houve instalação, rede, acesso a credenciais,
solicitação Git/escalada, pixel, runner científico ou repetição do planner.
A suíte histórica completa e os testes de novos guards não foram executados:
a parada ocorreu no primeiro gate legado antes de implementar a migração.

[commands.json](commands.json) registra comandos, fronteiras, exits e a auditoria
delegada. [verification.json](verification.json) confirma a custódia final.
Esses inventários delimitados não são monitoramento universal de syscalls.

```text
TI3_GOV_COMPAT=BLOCKED_LEGACY_BASELINE_CLASSIFICATION
LEGACY_SCOPE_GUARD=BLOCKED
TI3_SCOPE_GUARD=NOT_IMPLEMENTED_NOT_RUN_STOP
PHASE_SCOPE_GUARD=NOT_IMPLEMENTED_NOT_RUN_STOP
C0=NOT_CREATED
C1=NOT_CREATED
C2=NOT_CREATED
CI=NOT_RUN
EXPERIMENTAL_OPENS=0
EXPERIMENTAL_BYTES=0
SCIENTIFIC_ML_RUNS=0
ML_FINAL_TEST=SEALED_WITH_HISTORICAL_NON_ML_EXPOSURE
ML_FINAL_TEST_EXECUTED=false
TI3_B_AUTHORIZED=false
MERGE_AUTHORIZED=false
CURRENT_AUTHORIZED_ACTIVITY=NONE_AWAITING_AUTHOR_DECISION
```
