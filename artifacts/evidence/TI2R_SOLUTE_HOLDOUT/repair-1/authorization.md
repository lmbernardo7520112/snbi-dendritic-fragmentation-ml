# TI2R_SOLUTE — PREFLIGHT REPAIR + LOCKED HOLDOUT EXECUTION
# Correção operacional única seguida da primeira execução científica
# Convergência obrigatória — sem recalibração, sem tuning, sem retry científico

Repositório:
snbi-dendritic-fragmentation-ml

Branch:
feat/ti2r-solute-v2-calibration

PR:
#10 — permanecer OPEN/DRAFT

============================================================
ESTADO CANÔNICO
============================================================

V2-D development foi concluído e congelado.

C1 científico:
e1a98917a20431ecc1c758f210b5e974b3533734

C2 evidência:
0b820bc61e6dae3b7a98654a3b7d5cd292ca925e

Checkpoint local do preflight encerrado:
7994771e239afdb998a644626c423c1c627f80a0

Estado atual:

PRE_HOLDOUT_GATE=FAIL
TI2R_SOLUTE_HOLDOUT=BLOCKED_PRE_EXECUTION_CONFIGURATION_DIVERGENCE
G2_SOLUTE=BLOCKED_PENDING_LOCKED_HOLDOUT
HOLDOUT_SOLUTE=SEALED
HOLDOUT_RUN_ATTEMPT=NOT_ARMED
SCIENTIFIC_INVOCATIONS=0
RETRIES=0
STATE=BLOCKED_PRE_EXECUTION
TI3_PLUS_AUTHORIZED=false
MERGE_AUTHORIZED=false

Na tentativa anterior:

CLI_INVOCATIONS=1
SCIENTIFIC_EXECUTIONS=0
HOLDOUT_FILES_OPENED=0
HOLDOUT_BYTES_READ=0

Nenhum pixel do holdout foi observado.

Portanto o holdout permanece cientificamente SEALED.

============================================================
INCIDENTE JÁ CLASSIFICADO
============================================================

O preflight anterior detectou:

CONFIGURATION_DIVERGENCE

Causa localizada:

o manifesto serializado converteu seis valores originalmente float
em int, embora os valores numéricos fossem equivalentes:

minimum_entropy_bits:
1.0 → 1

saturation_low_y:
16.0 → 16

saturation_high_y:
235.0 → 235

median_limit_px:
1.0 → 1

p95_limit_px:
2.0 → 2

maximum_limit_px:
3.0 → 3

O contrato `_exact` exige identidade de valor E tipo.

A configuração científica congelada permanece correta.

A falha pertence exclusivamente à camada de
serialização/preparação/orquestração.

============================================================
AUTORIZAÇÃO DESTA TAREFA
============================================================

Está autorizado SOMENTE:

1. corrigir de forma mínima a preservação dos tipos no manifesto;
2. validar essa correção SEM acesso a pixels experimentais;
3. repetir o preflight operacional;
4. se e somente se o novo preflight for integralmente PASS,
   armar e realizar a PRIMEIRA execução científica do locked holdout;
5. registrar PASS ou FAIL científico;
6. parar.

Não está autorizado qualquer desenvolvimento científico.

============================================================
REGRA FUNDAMENTAL
============================================================

NÃO altere o contrato `_exact` para fazê-lo aceitar int/float equivalentes.

NÃO relaxe a validação.

NÃO mude a configuração científica.

O reparo deve fazer o MANIFESTO preservar fielmente os tipos existentes
na configuração congelada.

Exemplo desejado:

float(1.0) -> JSON/manifesto representando 1.0 -> float(1.0)

e não:

float(1.0) -> int(1)

============================================================
INVARIANTES CIENTÍFICOS IMUTÁVEIS
============================================================

É proibido modificar:

- algoritmos;
- kernels;
- descritores;
- preprocessing científico;
- máscaras;
- transformações;
- thresholds;
- pesos;
- scores;
- margens;
- critérios PASS/FAIL;
- índices DEV;
- índices HOLDOUT;
- residual limits;
- regras de identificabilidade;
- seleção de frames;
- SS8;
- NGF;
- qualquer arquivo científico congelado em C1/C2.

Os 25 arquivos congelados devem permanecer byte-identical.

============================================================
FASE A — REPARO ULTRACIRÚRGICO
SEM PIXELS
============================================================

Inspecione somente o caminho responsável por produzir o manifesto.

Identifique exatamente onde ocorre a coerção float -> int.

Faça a MENOR modificação possível para preservar os tipos originais.

Evite refatoração.

Evite cleanup não relacionado.

Evite novos abstractions.

Evite alterar formato além do necessário.

O diff deve ser pequeno, explicável e diretamente ligado ao incidente.

============================================================
FASE B — TESTES DO REPARO
SEM PIXELS
============================================================

Antes de qualquer acesso ao holdout, prove com fixtures/mocks/dados sintéticos
que:

1. 1.0 permanece float;
2. 16.0 permanece float;
3. 235.0 permanece float;
4. 2.0 permanece float;
5. 3.0 permanece float;
6. ints genuínos permanecem ints;
7. strings permanecem strings;
8. bools permanecem bools;
9. listas/maps preservam tipos recursivamente quando aplicável;
10. `_exact` continua rigoroso e inalterado.

Adicione apenas testes mínimos necessários para evitar regressão do incidente.

Não use imagens experimentais nesses testes.

============================================================
FASE C — AUDITORIA DE FREEZE
============================================================

Verifique novamente:

- C1 existente;
- C2 existente;
- 25 arquivos congelados byte-identical;
- hashes científicos iguais;
- nenhum threshold modificado;
- nenhum índice modificado;
- nenhum kernel modificado;
- nenhuma regra de decisão modificada.

Produza um novo manifesto de preflight.

Confirme explicitamente os tipos dos seis campos.

O gate somente pode continuar se:

PRE_HOLDOUT_GATE=PASS

Caso qualquer divergência permaneça:

STOP.

Não faça nova correção nesta mesma autorização.

Não abra pixels.

Reporte o novo bloqueio.

============================================================
CONTADORES — NÃO CONFUNDIR
============================================================

A invocação anterior foi operacional.

Portanto mantenha separados:

TOTAL_CLI_INVOCATIONS

e

SCIENTIFIC_HOLDOUT_EXECUTIONS

O histórico deve registrar:

PREVIOUS_CLI_INVOCATIONS=1
PREVIOUS_SCIENTIFIC_HOLDOUT_EXECUTIONS=0

Se o preflight atual passar, a execução seguinte será:

SCIENTIFIC_HOLDOUT_EXECUTION=1

Não a chame de retry científico.

============================================================
FASE D — ARMING
============================================================

Somente após PRE_HOLDOUT_GATE=PASS:

registre:

HOLDOUT_RUN_ATTEMPT=1

Congele:

- HEAD;
- manifesto;
- hashes;
- configuração;
- índices;
- critérios;
- timestamp.

Confirme que:

- não existe auto-retry;
- não existe fallback adaptativo;
- exceção não dispara segunda tentativa;
- nenhum parâmetro pode ser alterado durante a execução.

============================================================
FASE E — LOCKED HOLDOUT
============================================================

Execute UMA ÚNICA VEZ os quatro casos reservados:

ESM2→ESM1:73
ESM2→ESM1:219
ESM5→ESM4:98
ESM5→ESM4:295

Buffers previstos:

ESM1:73
ESM1:219
ESM2:73
ESM2:219
ESM4:98
ESM4:295
ESM5:98
ESM5:295

Total previsto:
8 buffers

Nenhuma segunda execução científica é autorizada.

Registre:

- opens;
- bytes;
- scores;
- margens;
- ranks;
- erro discreto;
- máximo único;
- quadrantes;
- resíduos;
- identificabilidade;
- SS8;
- NGF;
- todos os critérios congelados.

============================================================
FASE F — RESULTADO
============================================================

Aplicar mecanicamente os critérios previamente congelados.

Resultado científico permitido:

G2_SOLUTE=PASS

ou

G2_SOLUTE=FAIL

Não existem:

NEAR_PASS
SOFT_PASS
PASS_WITH_EXCEPTION
PASS_AFTER_FIX
RETRY
TUNING

============================================================
SE PASS
============================================================

Registrar:

PRE_HOLDOUT_GATE=PASS
TI2R_SOLUTE_HOLDOUT=PASS
G2_SOLUTE=PASS
HOLDOUT_SOLUTE=CONSUMED
SCIENTIFIC_HOLDOUT_EXECUTIONS=1
STATE=CLOSED
TI3_PLUS_AUTHORIZED=false
MERGE_AUTHORIZED=false
CURRENT_AUTHORIZED_ACTIVITY=NONE_AWAITING_AUTHOR_DECISION

STOP.

============================================================
SE FAIL CIENTÍFICO
============================================================

Registrar:

PRE_HOLDOUT_GATE=PASS
TI2R_SOLUTE_HOLDOUT=FAIL
G2_SOLUTE=FAIL
HOLDOUT_SOLUTE=CONSUMED
SCIENTIFIC_HOLDOUT_EXECUTIONS=1
STATE=CLOSED_FAILED
TI3_PLUS_AUTHORIZED=false
MERGE_AUTHORIZED=false
CURRENT_AUTHORIZED_ACTIVITY=NONE_AWAITING_AUTHOR_DECISION

Não corrigir.

Não executar novamente.

Produzir somente post-mortem descritivo.

STOP.

============================================================
SE O PREFLIGHT FALHAR NOVAMENTE
============================================================

Registrar:

PRE_HOLDOUT_GATE=FAIL
TI2R_SOLUTE_HOLDOUT=BLOCKED_PRE_EXECUTION
G2_SOLUTE=BLOCKED_PENDING_LOCKED_HOLDOUT
HOLDOUT_SOLUTE=SEALED
SCIENTIFIC_HOLDOUT_EXECUTIONS=0
STATE=BLOCKED_PRE_EXECUTION
TI3_PLUS_AUTHORIZED=false
MERGE_AUTHORIZED=false
CURRENT_AUTHORIZED_ACTIVITY=NONE_AWAITING_AUTHOR_DECISION

STOP.

Não faça segunda correção nesta autorização.

============================================================
COMMITS
============================================================

Busque convergência.

No máximo:

1 commit pequeno para o reparo/teste operacional,
e, se a execução científica ocorrer,
1 commit final exclusivamente de evidência.

Não faça commits cosméticos.

Não faça refatoração adjacente.

Não faça merge.

Não marque PR ready.

Não delete branches.

============================================================
EVIDÊNCIA
============================================================

Atualize/crie de forma auditável:

artifacts/evidence/TI2R_SOLUTE_HOLDOUT/

Preserve integralmente a evidência histórica do incidente anterior.

NÃO reescreva o passado como se ele não tivesse ocorrido.

O relatório final deve distinguir:

1. tentativa operacional anterior;
2. incidente CONFIGURATION_DIVERGENCE;
3. reparo autorizado;
4. novo preflight;
5. eventual primeira execução científica;
6. resultado científico.

============================================================
CRITÉRIO DE CONVERGÊNCIA
============================================================

Esta autorização possui no máximo dois resultados úteis:

A)
preflight corrigido + primeira execução científica concluída

ou

B)
novo bloqueio de preflight sem exposição do holdout.

Não existe terceiro ciclo de reparo nesta tarefa.

Não criar V2-E.

Não recalibrar V2-D.

Não abrir novo ciclo de tuning.

============================================================
REPORT FINAL NO CHAT
============================================================

Informe:

- HEAD inicial;
- HEAD final;
- commits criados;
- tamanho/escopo do diff de reparo;
- confirmação de 25 arquivos científicos intactos;
- resultado dos testes sintéticos;
- tipos finais dos seis campos;
- PRE_HOLDOUT_GATE;
- total de CLI invocations;
- scientific holdout executions;
- retries científicos;
- buffers abertos;
- bytes lidos;
- tabela dos quatro casos, se executados;
- G2_SOLUTE;
- HOLDOUT_SOLUTE;
- CI;
- worktree/index;
- estado do PR;
- autorizações finais.

Termine exatamente com o bloco de estado correspondente.

EXECUTE AGORA SOMENTE ESTA AUTORIZAÇÃO LIMITADA.
