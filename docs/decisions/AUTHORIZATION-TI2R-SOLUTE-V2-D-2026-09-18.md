# Decisão autoral — TI2R-SOLUTE-V2-D

Texto integral recebido do autor nesta sessão. A aceitação do PR #9 e a fase V2-D têm escopos distintos; nenhuma autoridade histórica é reativada.

APROVO A CONCLUSÃO DE QUE OS DADOS NATIVOS, SCRIPTS ORIGINAIS E ARTEFATOS COMPLETOS DE PROVENIÊNCIA NÃO ESTÃO DISPONÍVEIS ALÉM DO MATERIAL JÁ FORNECIDO PELOS AUTORES.

REGISTRO:

```text
AUTHORITATIVE_PROVENANCE_UNAVAILABLE=CONFIRMED_CONSTRAINT;
PROVENANCE_AUDIT=NOT_REQUIRED_NO_EXPECTED_INFORMATION_GAIN;
SOLUTE_V1=VALID_BLOCKED_RESULT;
IDENTITY_SOLUTE=COMPARATIVELY_SUPPORTED_NOT_CERTIFIED;
ABSOLUTE_FLOORS_V1=NOT_EXTERNALLY_CALIBRATED;
THRESHOLD_DIRECT_LOWERING=REJECTED;
G2_FRAG=PASS_DIRECT_RASTER_MAPPING;
G2_SOLUTE=BLOCKED_PENDING_V2;
HOLDOUT_SOLUTE=SEALED;
TI3_PLUS_AUTHORIZED=false;
```

AUTORIZO UMA ÚNICA ETAPA CONVERGENTE:

# TI2R-SOLUTE-V2-D — RECALIBRAÇÃO CONTROLADA DO CRITÉRIO DE ACEITAÇÃO SOMENTE NO DESENVOLVIMENTO

ESTA AUTORIZAÇÃO COMPREENDE:

1. O MERGE GOVERNADO DO PR #9 NO SHA EXATO AUDITADO;
2. A PRÉ-REGISTRAÇÃO, IMPLEMENTAÇÃO E EXECUÇÃO ÚNICA DA CALIBRAÇÃO V2-D;
3. O USO EXCLUSIVO DOS BUFFERS DE DESENVOLVIMENTO JÁ EXPOSTOS;
4. A MANUTENÇÃO INTEGRAL DO HOLDOUT LACRADO;
5. A PUBLICAÇÃO DOS RESULTADOS EM UM NOVO DRAFT PR.

A EXECUÇÃO DEVERÁ PARAR ANTES DE QUALQUER ABERTURA DO HOLDOUT.

## PARTE A — MERGE GOVERNADO DO PR #9

REALIZAR PREFLIGHT READ-ONLY E CONFIRMAR:

* repositório `lmbernardo7520112/snbi-dendritic-fragmentation-ml`;
* PR #9 ainda `OPEN`, `DRAFT` e não merged;
* base `main`;
* head `feat/ti2r-solute-direct-mapping`;
* head SHA exatamente:

```text
fef9aa5437c6b39fa29f085498551a208982f9de
```

* base auditada:

```text
db03183e1456f67b5b663a4cb71361cad1404dcb
```

* CI de push `35364371535` em `SUCCESS`;
* CI do PR `35365201447` em `SUCCESS`;
* jobs `deterministic-contracts` e `scientific-synthetic-contracts` aprovados;
* local, remoto e PR no mesmo SHA;
* worktree e index limpos;
* PR mergeável e sem conflitos;
* ausência de novos commits ou alteração da base.

SE QUALQUER CONDIÇÃO DIVERGIR, INTERROMPER E RETORNAR:

```text
PR9_MERGE=BLOCKED_REQUIRES_NEW_AUTHOR_DECISION
```

SE TODAS AS CONDIÇÕES FOREM SATISFEITAS:

1. publicar um único comentário registrando a autorização e o SHA;
2. tornar o PR Ready for Review;
3. aguardar eventual CI no mesmo SHA;
4. fazer merge exclusivamente por merge commit;
5. preservar a branch e todo o histórico;
6. aguardar e verificar eventual CI pós-merge;
7. sincronizar `main` exclusivamente por fast-forward.

NÃO USAR SQUASH, REBASE, AUTO-MERGE, FORCE-PUSH OU EXCLUSÃO DE BRANCH.

SE A CI PÓS-MERGE FALHAR, NÃO CORRIGIR E RETORNAR:

```text
PR9_MERGE=MERGED_POSTMERGE_CI_FAILED_REQUIRES_AUTHOR_DECISION
```

## PARTE B — BRANCH V2-D

SOMENTE APÓS MERGE E CI VERDE, CRIAR A PARTIR DA `main`:

```text
feat/ti2r-solute-v2-calibration
```

## OBJETIVO CIENTÍFICO

DETERMINAR SE SS8 E NGF, NAS IMPLEMENTAÇÕES JÁ EXISTENTES, CONSEGUEM:

1. identificar a correspondência correta como máximo único;
2. distinguir a identidade de deslocamentos espaciais conhecidos;
3. recuperar o inverso de perturbações sintéticas controladas;
4. manter concordância entre os dois descritores;
5. sustentar uma regra de aceitação relativa e operacional.

ESTA ETAPA CALIBRA O CRITÉRIO DE DECISÃO DO REGISTRO.

ELA NÃO CALIBRA:

* concentração de Bi;
* instrumento radiográfico;
* escala física;
* incerteza metrológica;
* causalidade convectiva;
* generalização para outros experimentos.

## DADOS AUTORIZADOS

AUTORIZO A LEITURA EXCLUSIVA DOS 12 BUFFERS DE DESENVOLVIMENTO JÁ EXPOSTOS:

```text
ESM1/ESM2: índices 0, 146 e 293;
ESM4/ESM5: índices 0, 197 e 394.
```

OS QUATRO PARES INFORMATIVOS PARA CALIBRAÇÃO POSITIVA SÃO:

```text
ESM2→ESM1: índices 146 e 293;
ESM5→ESM4: índices 197 e 394.
```

OS ÍNDICES INICIAIS:

```text
ESM2→ESM1: índice 0;
ESM5→ESM4: índice 0;
```

DEVEM PERMANECER REGISTRADOS COMO `NON_IDENTIFIABLE`, SERVINDO COMO CONTROLE DE OBSERVABILIDADE. NÃO DEVEM SER EXCLUÍDOS SILENCIOSAMENTE NEM CONVERTIDOS EM PASS OU FAIL.

PERMANECEM LACRADOS E PROIBIDOS:

```text
ESM1/ESM2: índices 73 e 219;
ESM4/ESM5: índices 98 e 295.
```

OITO BUFFERS DE HOLDOUT DEVEM PERMANECER COM:

```text
content_bytes_read=0
open_count=0
HOLDOUT_SOLUTE=SEALED
```

## PRINCÍPIO DA RECALIBRAÇÃO

O RESULTADO V1 NÃO DEVE SER REESCRITO.

OS PISOS:

```text
SS8 ≥ 0,90
NGF ≥ 0,80
```

PERMANECEM REGISTRADOS COMO CRITÉRIOS HISTÓRICOS DO V1 QUE NÃO FORAM ATINGIDOS.

NA V2-D:

* eles deixam de ser gates por não possuírem calibração externa para este domínio;
* não devem ser reduzidos para valores próximos dos resultados observados;
* não devem ser substituídos por novos pisos absolutos;
* os valores brutos SS8 e NGF continuam obrigatoriamente reportados.

O ENDPOINT V2-D SERÁ A DISCRIMINAÇÃO RELATIVA E A RECUPERAÇÃO DE PERTURBAÇÕES CONHECIDAS.

## ELEMENTOS QUE DEVEM PERMANECER INALTERADOS

MANTER EXATAMENTE:

* implementações atuais de SS8 e NGF;
* versões das dependências;
* máscaras científicas já congeladas;
* regras de identificabilidade;
* margens e exclusões existentes;
* suporte raster;
* raio dos descritores;
* controles temporais;
* convenções de coordenadas;
* cálculo dos resíduos;
* limites geométricos:

```text
mediana ≤ 1 px;
P95 ≤ 2 px;
máximo ≤ 3 px.
```

NÃO AUTORIZO:

* novo descritor;
* seleção entre múltiplos algoritmos;
* ajuste de pesos;
* score composto;
* alteração de máscara;
* novo pré-processamento;
* remoção de outliers;
* descarte de resultados desfavoráveis;
* metric shopping.

SS8 E NGF DEVEM SER AVALIADOS E REPORTADOS SEPARADAMENTE.

## PERTURBAÇÕES PRIMÁRIAS CONGELADAS

PARA CADA UM DOS QUATRO PARES IDENTIFICÁVEIS, APLICAR EXATAMENTE AS 16 TRANSLAÇÕES INTEIRAS NÃO NULAS:

```text
(+1, 0), (-1, 0), (0, +1), (0, -1);
(+2, 0), (-2, 0), (0, +2), (0, -2);
(+4, 0), (-4, 0), (0, +4), (0, -4);
(+2, +2), (+2, -2), (-2, +2), (-2, -2).
```

CONVENÇÃO:

```text
(dx, dy), em pixels.
```

AS TRANSLAÇÕES INTEIRAS DEVEM:

* evitar interpolação;
* não utilizar wrap-around;
* mascarar as regiões sem suporte;
* usar interseção comum erodida pelo deslocamento máximo e pelo suporte do descritor;
* impedir que bordas, padding, barras, timestamps ou áreas artificiais revelem o deslocamento.

A IDENTIDADE `(0,0)` É O CONTROLE POSITIVO.

NÃO ADICIONAR OUTRAS PERTURBAÇÕES APÓS O CONGELAMENTO.

TESTES SUBPIXEL, RUÍDO, SATURAÇÃO OU TRANSFORMAÇÕES DE CONTRASTE NÃO DEVEM DECIDIR O GATE NESTA ETAPA.

## CRITÉRIOS DE ACEITAÇÃO V2-D

CADA UM DOS QUATRO PARES IDENTIFICÁVEIS DEVE PASSAR INDIVIDUALMENTE.

NÃO É PERMITIDO RESGATAR UM PAR POR MÉDIA GLOBAL.

PARA CADA PAR, EXIGIR:

1. a identidade original `(0,0)` como máximo único separadamente em SS8 e NGF;
2. identidade superior a todos os deslocamentos espaciais não nulos;
3. identidade superior a todos os controles temporais identificáveis;
4. margem mínima já congelada de `0,005` sobre o melhor controle concorrente;
5. concordância entre SS8 e NGF quanto ao melhor deslocamento;
6. cobertura válida dos quatro quadrantes;
7. atendimento aos limites geométricos `1/2/3 px`;
8. recuperação correta do inverso conhecido das 16 perturbações primárias;
9. deslocamento verdadeiro como máximo único em SS8 e NGF;
10. erro máximo de recuperação ≤ `0,5 px`;
11. margem mínima de `0,005` entre o deslocamento verdadeiro e o segundo colocado;
12. nenhuma remoção ou truncamento de resultado desfavorável.

O CRITÉRIO DE RECUPERAÇÃO SERÁ:

```text
16/16 perturbações corretamente recuperadas por par,
separadamente em SS8 e NGF.
```

COMO `15/16 = 93,75%`, NÃO ARREDONDAR PARA 95%.

AS PERTURBAÇÕES, TILES E FRAMES NÃO DEVEM SER TRATADOS COMO RÉPLICAS EXPERIMENTAIS.

NÃO CALCULAR P-VALORES COMO SE HOUVESSE REPLICAÇÃO FÍSICA.

A UNIDADE EXPERIMENTAL CONTINUA SENDO A AQUISIÇÃO, COM APROXIMADAMENTE UMA CORRIDA POR CONDIÇÃO.

## FLUXO IRREVOGÁVEL

### C1 — PRÉ-REGISTRO

ANTES DE QUALQUER NOVA LEITURA DOS BUFFERS EXPERIMENTAIS:

1. implementar o calibrador;
2. criar testes exclusivamente sintéticos;
3. criar guardrail que bloqueie todos os holdouts;
4. congelar protocolo, configuração, versões, máscaras, perturbações, métricas e critérios;
5. executar testes sintéticos, guardrails e checksums;
6. criar o commit C1;
7. fazer push;
8. abrir Draft PR;
9. aguardar CI verde no SHA C1.

SE C1 OU A CI FALHAREM, NÃO ACESSAR OS BUFFERS EXPERIMENTAIS.

### EXECUÇÃO ÚNICA

SOMENTE APÓS C1 E CI VERDE:

1. criar receipt atômico com contador de execução;
2. permitir exatamente uma invocação;
3. abrir somente os 12 buffers de desenvolvimento autorizados;
4. executar toda a matriz congelada;
5. registrar resultados brutos e agregados por par;
6. encerrar a autoridade de execução antes do closeout.

APÓS A PRIMEIRA INVOCAÇÃO:

* nenhuma segunda execução;
* nenhum retry;
* nenhuma alteração de código;
* nenhuma alteração de configuração;
* nenhuma alteração de máscara;
* nenhum novo frame;
* nenhum retorno oportunista ao desenvolvimento.

### C2 — ENCERRAMENTO

O COMMIT C2 PODERÁ ALTERAR SOMENTE:

* resultados e evidências textuais;
* receipt e contador;
* estado terminal;
* relatório de execução;
* checksums;
* corpo do Draft PR.

C2 NÃO PODERÁ ALTERAR CÓDIGO, MÉTRICAS, PARÂMETROS OU CRITÉRIOS.

APÓS C2:

1. fazer push fast-forward;
2. aguardar CI;
3. manter o PR `OPEN/DRAFT`;
4. não tornar Ready;
5. não realizar merge.

## RESULTADOS TERMINAIS

SE TODOS OS QUATRO PARES IDENTIFICÁVEIS PASSAREM TODOS OS CRITÉRIOS:

```text
TI2R_SOLUTE_V2_DEV=PASS_PROTOCOL_FROZEN_READY_FOR_HOLDOUT_DECISION;
V2_RULE=FROZEN;
G2_SOLUTE=BLOCKED_PENDING_LOCKED_HOLDOUT;
HOLDOUT_SOLUTE=SEALED;
```

SE QUALQUER PAR FALHAR, HOUVER DISCORDÂNCIA ENTRE SS8 E NGF OU A DISCRIMINAÇÃO FOR INSUFICIENTE:

```text
TI2R_SOLUTE_V2_DEV=BLOCKED_METHOD_NOT_DISCRIMINATIVE;
G2_SOLUTE=BLOCKED_FINAL_WITH_AVAILABLE_DATA;
HOLDOUT_SOLUTE=SEALED_NOT_NEEDED;
NO_AUTOMATIC_V3=true;
```

SE OCORRER FALHA OPERACIONAL ANTES DA PRODUÇÃO DE RESULTADO CIENTÍFICO:

```text
TI2R_SOLUTE_V2_DEV=BLOCKED_OPERATIONAL_REQUIRES_AUTHOR_DECISION;
HOLDOUT_SOLUTE=SEALED;
```

UM PASS EM DESENVOLVIMENTO:

* não aprova `G2_SOLUTE`;
* não autoriza abertura do holdout;
* não certifica concentração absoluta;
* não certifica metrologia;
* não autoriza TI-3+;
* apenas permite posterior deliberação sobre uma única avaliação confirmatória lacrada.

## PROIBIÇÕES

PERMANECEM PROIBIDOS:

* acesso aos oito buffers de holdout;
* novos frames;
* MP4, ZIP, FFmpeg ou FFprobe;
* redecodificação;
* dados experimentais adicionais;
* redução dos pisos absolutos;
* modificação retrospectiva do v1;
* novo método de registro;
* novo descritor ou pré-processamento;
* correspondências manuais ou oportunistas;
* conversão física;
* concentração absoluta de Bi;
* labels ou ledger de eventos;
* dataset ML ou splits;
* baseline, CNN ou treinamento;
* TI-3 a TI-8;
* segundo teste experimental;
* v3 automática;
* Ready ou merge do novo PR.

## RETORNO OBRIGATÓRIO

RETORNAR UM ÚNICO RELATÓRIO CONTENDO:

* resultado do merge do PR #9;
* SHA do merge e CI pós-merge;
* branch e Draft PR da V2-D;
* SHA C1 e CI de pré-registro;
* SHA C2 e CI final;
* confirmação da única execução;
* lista exata dos buffers abertos;
* confirmação de zero bytes lidos do holdout;
* resultados SS8 e NGF por par e perturbação;
* rank do deslocamento correto;
* margens para o segundo colocado;
* erros de recuperação;
* controles temporais;
* cobertura e resíduos;
* resultado individual de cada par;
* estado terminal global;
* arquivos alterados;
* comandos executados;
* worktree e index finais;
* confirmação de inexistência de retry ou alteração pós-C1.

AO FINAL, MANTER:

```text
CURRENT_AUTHORIZED_ACTIVITY=NONE_AWAITING_AUTHOR_DECISION;
TI2R_SOLUTE_HOLDOUT_AUTHORIZED=false;
TI3_PLUS_AUTHORIZED=false;
MERGE_AUTHORIZED=false;
```
