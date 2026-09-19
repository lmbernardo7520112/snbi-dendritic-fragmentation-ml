# Split temporal e por grupo — pré-registro

TRAIN: ESM1:73/146 e ESM4:98; esperados 26 sites antes das exclusões.
DEVELOPMENT: ESM1:219 e ESM4:197; esperados 18.
FINAL_TEST: ESM1:293 e ESM4:295; esperados oito.

Todos os membros de um site pertencem ao split de sua FCO. Cada frame inteiro,
identificado por source/acquisition/frame, pertence a somente um split.
Derivados, caches e backgrounds herdam esse grupo. A regra temporal autoral
substitui prospectivamente a proposta cíclica do contrato anterior, que permanece
histórico e inalterado. A0 e o holdout solutal não são reexecutados.

Antes de materializar, comparar cada patch com todas as coordenadas observadas
dos 52 sites da mesma aquisição. Cada centro incompatível com o split recebe
zona quadrada fechada L-infinito de raio 35 px = 32+3. Interseção, inclusive
contato de fronteira, torna o candidato INVALID_CONTEXT. Essa geometria é
conservadora e não estima incerteza física. Conservar todas as razões e IDs.
Não deslocar centros, realocar sites ou ajustar margens após resultados.

Cada split precisa de pelo menos um positivo válido e backgrounds 1:1.
Split vazio: BLOCKED_SPLIT_SUPPORT. Insuficiência de backgrounds:
BLOCKED_BACKGROUND_SUPPORT. Não fabricar partições a partir de exclusões
posteriores ao desempenho.

Somente após manifesto completo válido e freeze:
ML_FINAL_TEST=SEALED_WITH_HISTORICAL_NON_ML_EXPOSURE.
Antes disso: NOT_DEFINED_NOT_OPENED. ESM1:293 e ESM4:295 e seus derivados
permanecem proibidos para leitura, estatísticas, features ou modelo. Hashes
conhecidos e coordenadas textuais não exigem nova abertura dos inputs.
