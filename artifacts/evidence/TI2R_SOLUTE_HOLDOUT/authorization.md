# TI2R_SOLUTE — LOCKED HOLDOUT GATE
# Execução científica única, congelada e irreversível
# Método: DDD + SDD + evidence-first + no-retry + convergence governance

Você está trabalhando no repositório:

snbi-dendritic-fragmentation-ml

CONTEXTO CANÔNICO

O estágio V2-D de desenvolvimento do eixo solutal foi concluído com sucesso.

Estado conhecido:

TI2R_SOLUTE_V2_DEV=PASS_PROTOCOL_FROZEN_READY_FOR_HOLDOUT_DECISION
G2_SOLUTE=BLOCKED_PENDING_LOCKED_HOLDOUT
HOLDOUT_SOLUTE=SEALED
STATE=CLOSED_CONSUMED
TI2R_SOLUTE_HOLDOUT_AUTHORIZED=false
TI3_PLUS_AUTHORIZED=false
MERGE_AUTHORIZED=false

PR atual:
#10
branch:
feat/ti2r-solute-v2-calibration

Commits relevantes:

C1 científico/congelado:
e1a98917a20431ecc1c758f210b5e974b3533734

C2 evidência:
0b820bc61e6dae3b7a98654a3b7d5cd292ca925e

PR #9 já integrado:
fcfc5e1445467248566e881c61929d4d3da7b1d8

O desenvolvimento V2-D teve:

- uma única execução;
- zero retries;
- 12 buffers de desenvolvimento abertos exatamente uma vez;
- 23.349.060 bytes lidos;
- zero abertura dos oito holdouts;
- zero bytes lidos dos oito holdouts;
- quatro positivos aprovados;
- máximo único;
- rank 1;
- erro discreto zero;
- quatro quadrantes preservados;
- limites residuais satisfeitos;
- instantes iniciais corretamente NON_IDENTIFIABLE.

O protocolo está CONGELADO.

==================================================
MISSÃO
==================================================

Executar UMA ÚNICA avaliação LOCKED HOLDOUT para G2_SOLUTE, preservando integralmente o protocolo científico V2-D.

Esta tarefa NÃO é desenvolvimento.

Esta tarefa NÃO autoriza:

- melhorar algoritmo;
- recalibrar;
- mudar thresholds;
- mudar pesos;
- mudar métricas;
- mudar índices;
- escolher novos frames;
- alterar preprocessing;
- modificar transformações;
- modificar residual limits;
- modificar critérios PASS/FAIL;
- tentar configurações alternativas;
- executar novamente após observar resultado;
- iniciar TI3+;
- fazer merge do PR;
- transformar FAIL em PASS por refinamento.

O objetivo é descobrir se o protocolo congelado generaliza.

O resultado legítimo é somente:

PASS

ou

FAIL.

==================================================
PRINCÍPIO DE CONVERGÊNCIA
==================================================

Não procure fazer o holdout passar.

Procure medir corretamente o que o protocolo congelado faz.

FAIL é um resultado científico válido.

PASS é um resultado científico válido.

A tarefa termina imediatamente após a primeira execução válida e produção das evidências.

É expressamente proibido entrar em ciclos de:

executar
→ observar
→ corrigir
→ executar novamente.

==================================================
FASE 0 — AUDITORIA PRÉ-EXECUÇÃO
NÃO ABRA PIXELS DE HOLDOUT AINDA
==================================================

Antes de qualquer acesso ao holdout:

1. verificar branch atual;
2. verificar HEAD local/remoto;
3. confirmar worktree e index limpos;
4. confirmar existência de C1 e C2;
5. demonstrar que C2 não alterou ciência em relação a C1;
6. identificar exatamente:
   - arquivos científicos congelados;
   - configuração;
   - thresholds;
   - métricas;
   - regras de decisão;
   - índices;
   - residual limits;
   - código de matching/alinhamento;
7. registrar hashes SHA-256 dos artefatos relevantes;
8. criar manifesto pré-execução;
9. confirmar que os holdouts continuam sem acesso prévio;
10. verificar que não existe mecanismo automático de retry.

Criar, preferencialmente em:

artifacts/evidence/TI2R_SOLUTE_HOLDOUT/

os arquivos:

PRE_EXECUTION_AUDIT.md
frozen-manifest.json
frozen-hashes.sha256

O PRE_EXECUTION_AUDIT.md deve concluir explicitamente uma de duas formas:

PRE_HOLDOUT_GATE=PASS

ou

PRE_HOLDOUT_GATE=FAIL

Se PRE_HOLDOUT_GATE=FAIL:

PARE.

Não abra nenhum holdout.

Produza relatório explicando a inconsistência e aguarde decisão humana.

==================================================
FASE 1 — ARMAR A EXECUÇÃO
==================================================

Somente se:

PRE_HOLDOUT_GATE=PASS

prepare uma execução determinística e única.

Antes de abrir qualquer buffer do holdout:

- registrar timestamp;
- registrar commit;
- registrar branch;
- registrar hashes;
- registrar configuração congelada;
- registrar lista exata de holdouts autorizados;
- inicializar contador de:
  - arquivos abertos;
  - número de opens;
  - bytes lidos;
- garantir que não haja fallback adaptativo;
- garantir que nenhuma exceção provoque retry automático.

Defina:

HOLDOUT_RUN_ATTEMPT=1

Não poderá existir HOLDOUT_RUN_ATTEMPT=2.

==================================================
FASE 2 — EXECUÇÃO LOCKED HOLDOUT
==================================================

Execute exatamente UMA VEZ o protocolo V2-D congelado sobre o conjunto holdout previamente reservado.

Não altere qualquer parâmetro antes, durante ou depois da execução.

Registre integralmente:

- cada holdout acessado;
- quantidade de opens;
- bytes lidos;
- resultados por caso;
- scores;
- margens;
- ranks;
- erro discreto;
- máximo único ou não;
- cobertura de quadrantes;
- resíduos;
- controles temporais;
- identificabilidade;
- todos os critérios individuais usados pelo gate.

Não esconda resultados desfavoráveis.

Não arredonde métricas com finalidade de satisfazer thresholds.

Não reexecute qualquer caso.

Se ocorrer erro técnico real antes de obtenção de qualquer resultado científico, interrompa e classifique o incidente SEM reexecutar automaticamente.

==================================================
FASE 3 — DECISÃO MECÂNICA
==================================================

Aplicar EXATAMENTE os critérios PASS/FAIL já congelados.

Não interpretar subjetivamente.

Não mudar threshold depois de observar números.

Resultado final permitido:

G2_SOLUTE=PASS

ou

G2_SOLUTE=FAIL

Se qualquer condição obrigatória pré-especificada falhar, o resultado formal é FAIL.

Não existe:

NEAR_PASS
SOFT_PASS
PASS_WITH_TUNING
RETRY_RECOMMENDED

==================================================
FASE 4 — SE PASS
==================================================

Se e somente se todos os critérios congelados forem satisfeitos:

registrar:

TI2R_SOLUTE_HOLDOUT=PASS
G2_SOLUTE=PASS
HOLDOUT_SOLUTE=CONSUMED
SOLUTAL_PROTOCOL=VALIDATED_ON_LOCKED_HOLDOUT
STATE=CLOSED
CURRENT_AUTHORIZED_ACTIVITY=NONE_AWAITING_AUTHOR_DECISION
TI3_PLUS_AUTHORIZED=false
MERGE_AUTHORIZED=false

IMPORTANTE:

PASS não autoriza automaticamente:

- TI3+;
- modelagem;
- merge;
- mudança de PR;
- novos experimentos.

Apenas informe que G2_SOLUTE está apto para decisão humana subsequente.

==================================================
FASE 5 — SE FAIL
==================================================

Se qualquer critério congelado falhar:

registrar:

TI2R_SOLUTE_HOLDOUT=FAIL
G2_SOLUTE=FAIL
HOLDOUT_SOLUTE=CONSUMED
STATE=CLOSED_FAILED
CURRENT_AUTHORIZED_ACTIVITY=NONE_AWAITING_AUTHOR_DECISION
TI3_PLUS_AUTHORIZED=false
MERGE_AUTHORIZED=false

PARE.

NÃO:

- altere algoritmo;
- ajuste thresholds;
- investigue uma nova configuração;
- rode novamente;
- use o mesmo holdout como teste cego novamente.

Depois do FAIL, faça somente uma análise POST-MORTEM DESCRITIVA, sem desenvolvimento.

Classifique a falha, quando possível, entre:

A. implementação/pipeline;
B. aquisição/dados;
C. registro/alinhamento;
D. identificabilidade insuficiente;
E. generalização insuficiente;
F. critério congelado não satisfeito;
G. hipótese metodológica possivelmente inadequada.

Essa classificação NÃO autoriza correção.

Ela apenas subsidia decisão humana futura.

O holdout passa a ser CONSUMED.

==================================================
FASE 6 — EVIDÊNCIA FINAL
==================================================

Gerar:

artifacts/evidence/TI2R_SOLUTE_HOLDOUT/execution-report.md
artifacts/evidence/TI2R_SOLUTE_HOLDOUT/commands.json
artifacts/evidence/TI2R_SOLUTE_HOLDOUT/io-audit.json
artifacts/evidence/TI2R_SOLUTE_HOLDOUT/results.json
artifacts/evidence/TI2R_SOLUTE_HOLDOUT/post-run-hashes.sha256

O execution-report.md deve conter, no mínimo:

1. objetivo;
2. commit e branch;
3. auditoria pré-execução;
4. demonstração do freeze;
5. manifesto;
6. inventário exato do holdout;
7. contador de I/O;
8. confirmação de uma única execução;
9. confirmação de zero retries;
10. resultados completos por caso;
11. critérios congelados;
12. decisão mecânica PASS/FAIL;
13. estado final;
14. limitações;
15. declaração explícita de que nenhum desenvolvimento foi realizado após observação do holdout.

==================================================
COMMITS
==================================================

Evite commits cosméticos ou fragmentação desnecessária.

Objetivo: no máximo UM commit final de evidência para esta execução, salvo necessidade técnica incontornável.

Nenhuma alteração científica é permitida.

Mensagem sugerida:

test(solute): execute locked holdout gate without retry

Se houver apenas documentação/evidência, use mensagem semanticamente adequada.

Não faça merge.

Não marque PR como ready sem autorização.

==================================================
GATES AUTOMÁTICOS
==================================================

Antes de encerrar, verificar:

[ ] worktree consistente;
[ ] protocolo idêntico ao freeze;
[ ] hashes registrados;
[ ] PRE_HOLDOUT_GATE=PASS;
[ ] exatamente uma execução científica;
[ ] HOLDOUT_RUN_ATTEMPT=1;
[ ] zero retries;
[ ] todo I/O contabilizado;
[ ] nenhuma alteração científica após observação;
[ ] resultado final PASS ou FAIL;
[ ] holdout marcado CONSUMED;
[ ] TI3_PLUS_AUTHORIZED=false;
[ ] MERGE_AUTHORIZED=false;
[ ] evidência completa;
[ ] CI aplicável verde.

==================================================
REGRA ANTI-DERIVA
==================================================

Se durante a tarefa você identificar qualquer melhoria possível, NÃO a implemente.

Registre-a apenas como observação futura.

Esta missão não é melhorar o método.

É TESTAR o método congelado.

==================================================
REGRA ANTI-REFINAMENTO INFINITO
==================================================

Após a primeira execução válida:

STOP.

Não proponha V2-E.
Não proponha tuning.
Não proponha novo threshold.
Não tente elevar score.
Não execute de novo.

Se PASS:
feche o gate e aguarde decisão humana.

Se FAIL:
feche o gate, classifique a falha em nível alto e aguarde decisão humana.

==================================================
REPORT FINAL NO CHAT
==================================================

Ao terminar, responda de forma objetiva com:

1. commit/HEAD;
2. PR/branch;
3. resultado da auditoria pré-execução;
4. número de execuções;
5. número de retries;
6. arquivos/buffers de holdout abertos;
7. total de bytes lidos;
8. tabela compacta dos resultados;
9. resultado G2_SOLUTE;
10. estado do holdout;
11. CI;
12. arquivos de evidência;
13. worktree/index;
14. estado de autorização.

Termine obrigatoriamente com UM dos dois blocos:

SE PASS:

TI2R_SOLUTE_HOLDOUT=PASS
G2_SOLUTE=PASS
HOLDOUT_SOLUTE=CONSUMED
STATE=CLOSED
TI3_PLUS_AUTHORIZED=false
MERGE_AUTHORIZED=false
CURRENT_AUTHORIZED_ACTIVITY=NONE_AWAITING_AUTHOR_DECISION

SE FAIL:

TI2R_SOLUTE_HOLDOUT=FAIL
G2_SOLUTE=FAIL
HOLDOUT_SOLUTE=CONSUMED
STATE=CLOSED_FAILED
TI3_PLUS_AUTHORIZED=false
MERGE_AUTHORIZED=false
CURRENT_AUTHORIZED_ACTIVITY=NONE_AWAITING_AUTHOR_DECISION

EXECUTE AGORA SOMENTE ESTE GATE.