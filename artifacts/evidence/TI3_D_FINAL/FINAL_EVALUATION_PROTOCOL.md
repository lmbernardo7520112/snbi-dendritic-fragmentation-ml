# TI3-D — protocolo final congelado

Esta autoridade permite somente a avaliação final do pipeline MULTIMODAL_LBP_RF já selecionado. TI3-C foi integrado no PR #13, merge a8227901506c3de6fe4a5a4bd19021be3f39b2e8, após todos os cinco jobs verdes. A branch TI3-D nasce nesse merge. Autoridades anteriores permanecem consumidas.

D1 registra protocolo, configuração, código, testes, hashes textuais e os IDs. D1 deve ser publicado por fast-forward e os seis jobs devem terminar SUCCESS, com todos os passos aprovados, antes do receipt exclusivo O_EXCL + fsync. O preflight verifica branch, parent, SHA local/remoto, bytes comprometidos, autoridade, configuração, inventário, dependências e prova CI real. Verificação prévia de textos não consome ciência.

Ordem obrigatória: receipt; dez buffers TRAIN+DEV; 50 pares de patches e vetores LBP20; um fit RF; registro textual durável do hash/configuração lógica do modelo; quatro buffers FINAL com autenticação e suporte completo; seis vetores; seis predições/probabilidades; congelamento textual exclusivo e durável dessas predições; somente então associação dos weak labels e métricas finais. Nenhuma avaliação DEVELOPMENT separada.

A execução admite uma CLI, um fit e uma avaliação FINAL. Presença do receipt ou resultado fecha a autoridade a novas execuções. Uma falha interrompe sem reparo, retry, substituição ou avaliação parcial. Após a primeira leitura FINAL, CONSUMED é irreversível. Falha anterior é reportada com contadores reais e sem inventar consumo.

PASS certifica cumprimento do protocolo, sem piso de desempenho. Mesmo desempenho baixo encerra modelagem e seleção. D2 contém exclusivamente evidências textuais; sem alteração científica, merge de TI3-D ou nova modelagem. As fases anteriores e seus resultados permanecem intactos.
