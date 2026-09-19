# TI3-GOV-COMPAT — gates locais da classificação semântica

**Partição e guards locais PASS; publicação C0 ainda pendente neste registro.**
Este documento integra o checkpoint de governança. SHA e CI efetivos de C0,
assim como etapas condicionais posteriores, pertencem às evidências posteriores
e ao retorno ao operador; não são inventados antecipadamente.

HEAD inicial: 41d523e038e844588ee7724e07b00f75bdf29fdc, branch
feat/ti3-canonical-dataset-baseline. Os 50 arquivos locais anteriores foram
reconferidos antes das mudanças. Index e conteúdo versionado estavam limpos.
Os sete textos do bloqueio anterior permanecem imutáveis.

O manifesto cronológico de 79 paths foi copiado exatamente: 15.859 bytes,
SHA-256 3c63b51ff86aeda79244d09e5bc7f5196be01f8aa8672ab3dc2f8fe6d90f9971.
A nova classificação enumera 75 LEGACY_TI2, quatro A0 congelados e 15 ativos
planejados. C0 versiona quatro ativos de governança; onze científicos aguardam
C1. Paths, modos e blobs completos estão no manifesto normativo versionado.

O guard real do índice original e a simulação explícita do inventário C0
passaram: zero paths não classificados, zero classificações duplicadas,
TI2 sobre 75 PASS, A0 congelado PASS, TI3 PASS e composição PASS. O checker
TI2 permanece byte-idêntico. Não houve alteração de ciência A0 ou G2.

Testes de governança: 26 do compositor e 15 de dependências, todos aprovados,
sem skips. O perfil C0 extraído literalmente do workflow novo também passou:
59 testes, zero skips/falhas/erros. A suíte dos módulos já versionados no
baseline passou 444 testes: 350 passes, 94 skips opcionais em Python -S.
Essas invocações são sintéticas/documentais, não execução experimental.

Depois dos guards locais, a CI histórica recebeu somente o comando composto
e fetch-depth=0 no job que necessita do baseline. O job G2 permanece intacto.
O novo workflow distingue os onze científicos PLANNED/TRACKED explicitamente.
O snapshot histórico conserva 95 entradas/10.212 bytes e SHA-256
e7d30ca626088e1e3c58c8702b96e9afc388ee75c48011d885393230dc7d245d.
O manifesto ativo mantém 95 entradas: apenas o hash de ci.yml mudou.

Um auxiliar de leitura encontrou o cabeçalho comentado do manifesto e saiu
com ValueError antes de qualquer escrita. A leitura que reconhece o cabeçalho
preservou-o e verificou as 95 entradas. Isso não foi falha do guard nem
execução científica. A consulta remota inicial falhou por DNS no sandbox;
a consulta Git pontual aprovada confirmou main=67786bd4e23406e7f19860a53fe237e6d7b648cb
e ausência da branch remota desta tarefa. Não houve acesso a credenciais.

O planejamento permanece 17+17 TRAIN, 8+8 DEV e 3+3 FINAL. Nenhum planner,
resolver, extrator ou baseline foi executado nesta migração. A distribuição
TRAIN ESM1 16/6 versus ESM4 1/11 e a baixa potência dos seis samples FINAL
continuam limitações; não houve reseleção.

EXPERIMENTAL_OPENS=0; EXPERIMENTAL_BYTES=0; SCIENTIFIC_ML_RUNS=0.
ML_FINAL_TEST=SEALED_WITH_HISTORICAL_NON_ML_EXPOSURE;
ML_FINAL_TEST_EXECUTED=false; TI3_B_AUTHORIZED=false; MERGE_AUTHORIZED=false.

O inventário do checkpoint e os limites dos registros estão em verification.json
e commands.json. Staging, commit, SHA e verificações remotas posteriores são
reportados ao operador, sem commit extra apenas para autorreferência.
