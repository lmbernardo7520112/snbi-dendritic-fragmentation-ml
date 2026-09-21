# Study2-D — proposta limitada de reparo de compatibilidade CI

**PROPOSTA NÃO APLICADA; aguarda decisão autoral.** O freeze
`21400de67d21901aeb8e5abac528689fc39169fa` permanece intacto local/remoto.
A seção 51 da [autorização](AUTHORIZATION.md) exige: “Se qualquer falha: STOP.”
Esse gate impede continuar automaticamente após o erro remoto.

## Falha comprovada

O job `deterministic-contracts`, run 35649522192, executa
`PYTHONPATH=src python -S -B -m unittest discover -s tests -v` sem pacotes
de site. Quatro testes novos de I/O chamam `TrainCorpusAccess.load`, que usa
NumPy, mas não declaram essa dependência opcional. Resultam quatro
`ModuleNotFoundError: No module named 'numpy'`. A suíte dedicada com pins
instalados passou em todos os 107 testes. A omissão é da preparação dos testes,
sem evidência de defeito nos dados ou de execução científica.

## Escopo concreto para uma decisão complementar

1. Aplicar exclusivamente aos quatro testes identificados a declaração
   `unittest.skipUnless(importlib.util.find_spec("numpy") is not None, ...)`.
   Os outros 25 testes de I/O continuam no perfil stdlib. Os 29 continuam
   obrigatórios no job dedicado, que rejeita qualquer skip. Nenhum workflow,
   dependência, reader científico, modelo, feature, peso ou desenho muda.
2. Admitir um único commit corretivo filho direto do freeze preservado.
   O preflight atual exige que HEAD seja filho direto do merge C; portanto,
   essa admissão também precisa de autorização explícita. O guard proposto
   exige precisamente `HEAD^=21400de67d21901aeb8e5abac528689fc39169fa` e
   `HEAD^^=ec97cb5041ef35d4f6c9a79b54d756d6fbee674f`. Não aceita ancestrais
   arbitrários ou bypass da CI. O diff das duas fontes está em
   [PROPOSED_REPAIR_SOURCE_DIFF.txt](PROPOSED_REPAIR_SOURCE_DIFF.txt).
3. Ajustar somente as fixtures/asserts sintéticas de ancestralidade afetadas
   em `tests/test_study2d_execution.py`, com casos de cadeia aceita e recusada.
4. Atualizar os blobs correspondentes em `configs/governance/phase-scope-v1.json`
   e os hashes/provas de `METHOD_FREEZE.json` e `SYNTHETIC_TESTS.json`.
   Preservar as versões anteriores no Git e em evidência aditiva do reparo.
   Registrar a decisão complementar e o diff integral antes de publicar.
5. Verificar o perfil stdlib e o perfil dedicado antes do commit. As verificações
   usam somente fixtures sintéticas; não reexecutam a ciência de C. Não refazer
   o planner, a autenticação material de integração, rankings, quantis ou
   `TRAIN_INPUT_MANIFEST.json`.
6. Criar um único commit corretivo, sem amend/rebase/force, publicar por push
   fast-forward na mesma branch e exigir dez jobs/todos os passos SUCCESS no
   novo SHA. Somente então fazer preflight real e a única CLI científica de D,
   com os mesmos 100 fits, seguido do checkpoint exclusivamente documental
   e da CI final já previstos no anexo. Nenhum merge de D.

O plano, seus 10.907 IDs TRAIN, quatro folds, 100 condições, oito reutilizações,
parâmetros e os hashes por row permanecem idênticos. DEV/TEST continuam com zero
acesso material. Nenhum TEST binário, índice TEST, MP4, decoder ou fonte nova
entra no reparo. Não há instalação local, tentativa científica, retry ou novo
model search. A proposta não é autorização para aplicar essas mudanças.
