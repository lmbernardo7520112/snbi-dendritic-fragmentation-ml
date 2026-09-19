# Guard de execução — antes de C1 e dos pixels

O resultado do planner não certifica ausência de overlays cromáticos nos inputs.
Antes das features, conferir o suporte completo de cada patch TRAIN/DEVELOPMENT
na única leitura do seu buffer. Reutilizar exatamente a regra já documentada
de G2_FRAG_DIRECT: max(abs(U−128),abs(V−128))>=20, expansão YUV420p2×,
halo5 por maximum_filter(size11, mode=constant, cval=0), bandas geométricas
12%/15%, borda4 e erosão1 com estrutura3×3. Não executar matcher/kernel G2.
Esse guard não altera luminância nem seleciona pixels/features para o modelo.

Qualquer patch sem suporte integral interrompe a execução sem substituir,
deslocar, excluir ou resselecionar amostras. FINAL_TEST não é aberto nem
inspecionado; sua verificação cromática fica pendente para eventual futura
autorização. O selo declara exposição histórica e reservas de acesso,
não qualidade de pixels que não foram examinados nesta fase.

Antes de qualquer caminho experimental: manifesto e textos autenticados,
HEAD C1 filho direto do checkpoint, branch exata, index/worktree versionados
sem alterações, todos os jobs de CI exigidos SUCCESS no C1, versões exatas e
uma autorização condicional específica. O receipt exclusivo O_EXCL+fsync
consome uma invocação antes do primeiro open. Receipt ou resultado preexistente
impedem nova execução. Somente os cinco buffers TRAIN/DEVELOPMENT documentados,
cada um no máximo uma vez, O_RDONLY|O_NOFOLLOW; sem fontes ESM2/3/5/6 ou FINAL.

Hashes nativos são conferidos durante a leitura única. Dados, patches, features
e modelo ficam em memória, sem exportar binário experimental ao Git.
Resultados textuais incluem métricas, labels/predições, hashes de patches,
proveniência e contadores. Não se preserva objeto pickle nem checkpoint ML.

A construção documental única produziu 17/8/3 positivos e backgrounds1:1 por
split. Em TRAIN, ESM1 tem16positivos/6backgrounds e ESM4 tem1positivo/11backgrounds.
Esse desequilíbrio por aquisição permite confusão entre condição e classe.
Será declarado na interpretação; não gera nova seleção, tuning ou outra
seed. Sites e patches não equivalem a aquisições independentes.

Em caso de erro após abrir um input, registrar estágio, contadores disponíveis
e exceção sanitizada. Nenhum retry. Uma avaliação válida, independentemente
de desempenho, encerra a autorização. Os 25 textos G2 permanecem intactos.
