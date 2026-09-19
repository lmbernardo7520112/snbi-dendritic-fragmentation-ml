# TI3-C0R1 — correção única da representação YAML

**Validações locais PASS; CI do novo SHA ainda pendente neste checkpoint.**
C0 permanece 272695a4420e37fddf6674664d0040ef064c153f, preservado sem amend.
A autorização nova está em authorization.md. Os 44 arquivos locais anteriores
conferiram, branch e HEAD local/remoto eram os esperados; índice e conteúdo
versionado estavam limpos antes da única alteração autorizada.

PyYAML 6.0.1 já disponível confirmou o ScannerError no YAML de C0:
`mapping values are not allowed here`, linha 28, coluna 111, no `:` final
de `--only-binary=:all:` seguido de espaço. Classificação agora comprovada:
**C0_CI_FAILURE_CAUSE=VERIFIED_YAML_PLAIN_SCALAR_COLON_PARSE_ERROR**.
O relatório histórico que dizia NOT_VERIFIED permanece intacto e correto
quanto à evidência disponível naquela tarefa; a nova confirmação está aqui.

Foi aplicada exclusivamente a substituição literal por `run: >-`, com as
cinco linhas do anexo. O parser aceitou o arquivo novo e o comando resultante
é byte-idêntico à cadeia shell original, incluindo `--only-binary=:all:`.
Nenhum outro step, pin, checker, manifesto semântico ou configuração científica
mudou. O diff integral está em workflow.diff.txt.

Data guard e compositor PASS; partição preservada: 75 LEGACY, quatro A0
imutáveis, quatro ativos TRACKED e onze PLANNED, zero não classificados ou
duplicados. Testes de governança existentes: 41 PASS, zero skips. Perfil C0
extraído do workflow: 59 PASS, zero skips/falhas/erros, quatro versões exatas.
Não houve instalação local. Os testes são sintéticos/documentais e não ML
experimental; as duas invocações compartilham os mesmos casos de governança.

O workflow corrigido não está em manifesto ativo de checksums. Portanto,
zero entradas foram alteradas ou acrescentadas. Seus hashes em verificações
históricas permanecem registros dos bytes anteriores. O snapshot histórico
de 95 entradas continua byte-idêntico. A correção não afeta o workflow
histórico ci.yml nem seu checksum ativo atualizado em C0.

C0R1 deve conter somente o workflow e evidência textual diretamente ligada
ao reparo: os cinco registros locais de encerramento C0 preservados e estes
nove textos. O SHA efetivo e as novas URLs de CI pertencem à evidência posterior
e ao retorno ao operador. Não haverá rerun de 35455982251 nem outro corretivo.

Somente SUCCESS dos três jobs no novo SHA permite continuar a C1. Até lá:
C1=NOT_CREATED; C2=NOT_CREATED; EXPERIMENTAL_OPENS=0;
EXPERIMENTAL_BYTES=0; SCIENTIFIC_ML_RUNS=0. FINAL permanece
SEALED_WITH_HISTORICAL_NON_ML_EXPOSURE, opens=0 e bytes=0.

Plano preservado: TRAIN17+17, DEV8+8, FINAL3+3; patch65; LBP P8/R1/uniform,
dez bins, range(0,10), density=True; RF100/seed42. TRAIN ESM1 16/6 e ESM4 1/11
pode confundir classe e aquisição; seis samples FINAL têm baixa potência.
Nenhuma redistribuição, tuning, modelo solutal, CNN, TI3-B ou merge é autorizado.
