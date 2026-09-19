# TI3 — composição semântica de escopos

A decisão em authorization.md substitui somente a classificação cronológica
que bloqueou a tentativa anterior. LEGACY_PRE_TI3 significava já versionado
no baseline, não pertencimento científico à TI2. A tentativa BLOCKED, seus
sete textos e o manifesto cronológico permanecem imutáveis.

O baseline Git 41d523e038e844588ee7724e07b00f75bdf29fdc ancora os 79 Python
originais. A partição normativa em configs/governance/phase-scope-v1.json
enumera 75 LEGACY_TI2, quatro TI3_A0_FROZEN e 15 TI3_ACTIVE. Dos ativos,
quatro são os checkers e testes expressamente autorizados nesta migração;
onze são os arquivos científicos já preparados para C1. Não existe quarta
classe nem exceção por substring do nome.

O compositor executa primeiro o data guard global. Exige cobertura disjunta
e exaustiva do índice, confirma modos/blobs contra o baseline Git e os bytes
do worktree, chama o checker TI2 intacto somente para os 75 legados, valida
a imutabilidade dos quatro A0 e audita somente os ativos TRACKED. PLANNED
não pode estar no índice; TRACKED não pode faltar. Dados e symlinks bloqueiam
antes de leitura de código. O resultado é custódia/escopo, nunca autoridade
para abrir conteúdo experimental.

A0 usa os quatro paths exatos da decisão, com origin_phase=TI3_A0 e
mutable=false. Seu conteúdo não é executado pelo guard. Alterar manifesto
e worktree simultaneamente não substitui a âncora Git do baseline.

O guard TI3 exige as quatro versões em requirements-ti3-ml.txt e dependências
de projeto vazias. A análise AST admite stdlib, módulos locais enumerados e
numpy/scipy/skimage/sklearn; proíbe as outras bibliotecas ML e imports
dinâmicos não resolvidos. É análise estática delimitada, não prova universal
da ausência de I/O em programas Python.

## Sequência de publicação

C0 inclui apenas governança, evidência histórica e CI. Seus quatro Python
novos passam de PLANNED a TRACKED no staging exato; os onze científicos
permanecem PLANNED. O inventário prospectivo é identificado como simulação
textual, separado da verificação efetiva do índice após staging.

O workflow histórico conserva seus controles; a chamada global TI2 torna-se
composição explícita. fetch-depth=0 disponibiliza o commit baseline para
verificar blobs, inclusive em checkout de C0/C1. O job científico G2 não muda.
O novo job TI3 verifica versões, compositor e 59 testes em C0: 41 governança
e 18 A0 sintéticos. Depois de C1, exige os onze paths TRACKED, smoke sintético
e 109 testes: os mesmos 41 e os 68 científicos preparados. Estados mistos,
contagens divergentes, skips, erros ou falhas interrompem a CI.

Somente o hash do workflow histórico muda no manifesto ativo de 95 entradas;
o snapshot histórico permanece byte-idêntico. old_hash/new_hash estão em
active-checksum-changes.json. Os outros 94 textos históricos são preservados.

C0 verde é pré-requisito de C1; C1 e toda sua CI verdes são pré-requisitos
de qualquer buffer TRAIN/DEV. Nenhum gate verde de governança reabre ciência
histórica. Não há retry, tuning, abertura de FINAL_TEST, TI3-B ou merge nesta
decisão. Um eventual C2 contém somente evidência terminal da execução única.
