# C1 — vínculos operacionais da continuação autorizada

C0R1 aba4fb6d66fd6bf640b3cd6adad07b2d60dfe49a e seus três jobs SUCCESS
encerram a governança. As seções 11–12 da decisão TI3-C0R1 autorizam continuar
a fase C1 já planejada. A restrição de edição da seção 3 foi aplicada ao
reparo C0R1, cujo único código alterado foi a representação YAML do comando.

Antes desta continuação foram reconferidos os hashes científicos preparados
e os 15 hashes do planejamento documental. Não houve nova construção do
manifesto, deduplicação, seleção de backgrounds, split ou extração de labels.

As adaptações abaixo pertencem exclusivamente ao C1 operacional:

- parent exato do C1 vinculado ao C0R1 verde, em vez do checkpoint anterior
  41d523e que antecedia os commits de governança;
- manifesto original lido de TI3_A_RESUME/dataset_manifest.json, sem alterar
  seus bytes ou SHA;
- nova autoridade configs/authority/ti3-a-c0r1-resume.json e namespace fixo
  TI3_A_RESUME/c0r1-resume para freeze, prova CI, receipt e resultados;
- somente as duas constantes de namespace do leitor mudam; sua admissão,
  I/O, hashes, contadores, bloqueio de repetição e O_EXCL/fsync não mudam;
- os onze ativos científicos passam de PLANNED para TRACKED no staging C1,
  transição já expressa no anexo semântico. A enumeração, classes, 75+4 e
  checkers permanecem iguais; só os dois blobs operacionais adaptados mudam.

Não se aceita ancestral arbitrário e não se reativa a autoridade anterior
fechada. Seu results.json continua intacto. As cópias .py.snapshot.txt nesta
pasta preservam exatamente os dois textos operacionais preparados antes da
adaptação. Hashes anteriores e finais ficam em operational-changes.json.

O novo receipt continua exclusivo e anterior aos pixels. Results/receipt
novos fecham definitivamente esta execução. A prova CI de C1 nasce depois
do commit e não entra retroativamente no freeze; deve autenticar o SHA exato
e os três jobs. Código científico, geometria, suporte, parâmetros e métricas
não mudam. Nenhum ajuste é permitido após C1 ou após exposição dos buffers.
