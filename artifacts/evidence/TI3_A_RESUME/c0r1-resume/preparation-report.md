# C1 — preparação após C0R1 verde

C0R1: aba4fb6d66fd6bf640b3cd6adad07b2d60dfe49a. Runs 35457621425 e
35457621439 SUCCESS, todos os passos dos três jobs obrigatórios aprovados.
TI3_GOV_COMPAT=PASS; a governança está encerrada. A prova remota está em
artifacts/evidence/TI3_GOV_COMPAT/c0r1/remote-ci.json.

Os arquivos científicos preparados e os 15 hashes do planejamento foram
revalidados antes da retomada. O manifesto original permanece SHA-256
c8e82b72ff5dc51d188a764c577c11d514474b14d90aea6292c1439e776fb487;
o manifesto FINAL permanece
985af14d0d6a74298bbc0380767f900d264f544303e46ecd8ed4dc0eb1ab649f.
Não houve nova chamada ao planner, resolver ou extrator.

OPERATIONAL_BINDINGS.md explica a única adaptação necessária à sequência
C0→C0R1→C1: parent exato, autoridade condicional e namespace fixo exclusivo.
operational-changes.json e os dois snapshots documentam bytes anteriores e
finais. Não se alega igualdade dos dois arquivos operacionais adaptados;
seu restante e os kernels científicos permanecem intactos. A autoridade e
o resultado bloqueados anteriores não foram apagados nem reativados.

O manifesto de escopo mantém os mesmos 75 LEGACY, quatro A0 e 15 ativos.
O staging C1 muda somente os onze estados PLANNED para TRACKED e os dois
blobs operacionais explicitamente adaptados. Nenhum checker ou workflow
muda neste C1. Os 95 checksums ativos e o snapshot histórico permanecem.

method-freeze.json autentica 45 textos, incluindo código, parâmetros,
contratos, manifestos e nova autoridade. Não inclui a prova CI do próprio C1,
que só pode existir depois do commit. O runner verifica novamente textos,
parent, branch, índice/worktree versionados, runtime e CI antes de armar.

Testes preparatórios: perfil C1 do workflow existente, 109 PASS, zero skips;
suíte completa Python -S, 535 testes, 428 passes e 107 skips opcionais,
zero erros/falhas. O perfil completo realizou três fits RF sintéticos
(dois smoke de ambiente e um teste do baseline), não fits experimentais.
Sete casos do preflight com Git/CI sintéticos passaram: configuração válida
e recusas de parent divergente, worktree/index sujos, autoridade fechada,
SHA de CI divergente, job falho e job ausente. Não armaram receipt nem
abriram buffers. O teste de configuração válida releu somente o manifesto
documental; não reconstruiu samples.

TRAIN permanece 17+17; DEVELOPMENT8+8; FINAL3+3. Patch65, LBP P8/R1/uniform,
histograma10/range(0,10)/density=True; RF100/seed42 e defaults integrais.
Métrica primária balanced_accuracy. Não há threshold de desempenho para PASS.
As limitações de aquisição/classe em TRAIN e de potência em FINAL estão em
CLAIM_SCOPE.md. Nenhuma redistribuição será realizada.

C1 deve ser o filho direto de C0R1. Depois do commit e push, todos os jobs
devem passar no SHA C1 antes da única invocação real. Esse SHA e os runs
serão registrados na prova posterior e no retorno, sem inventar autorreferência.
EXPERIMENTAL_OPENS=0; EXPERIMENTAL_BYTES=0; SCIENTIFIC_ML_RUNS=0.
FINAL_TEST continua reservado com exposição histórica não ML, sem abertura.
