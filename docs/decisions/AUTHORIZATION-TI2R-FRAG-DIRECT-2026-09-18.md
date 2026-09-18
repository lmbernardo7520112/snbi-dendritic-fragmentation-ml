# TI2R-FRAG-DIRECT — decisão integrada do autor

Autor: Leonardo Maximino Bernardo. Data: 2026-09-18.

## Estado desta autorização

Estado: `CLOSED_CONSUMED`. A única invocação retornou código 0 e
`TI2R_FRAG_DIRECT=PASS`, com ambos os pares aprovados em desenvolvimento e
holdout temporal interno. Os 20 ativos autorizados foram abertos uma vez cada.
A autoridade foi fechada antes de publicação; nenhum código ou critério mudou
após C2. G2_SOLUTE permanece NOT_EXECUTED e TI-3+ não está autorizada.
Base pós-merge PR #7: `b7bbb6a1f0d3eaa43866027762eb2ed061c3d7c6`.
A autoridade canônica específica é `configs/authority/ti2r-frag-direct.json`.
As autoridades TI-2 e TI2R-FRAG anteriores permanecem fechadas e consumidas.
C2 altera somente autoridade e este registro; C3 fecha e consome, sem retry.

## Instrução autoral integral preservada

SHA-256 do texto recebido: `530cd21748121417e20990c890d61f56130ee1a3bfcf50b8214872df723fa7a3`.

APROVO O RESULTADO DO PR #7 COMO RESULTADO CIENTÍFICO BLOQUEADO VÁLIDO E REGISTRO:

```text
PR7_RESULT_INTEGRITY=PASS;
PR7_SCIENTIFIC_REVIEW=PASS_AS_VALID_BLOCKED_RESULT;
TI2R_FRAG_ATTEMPT_1=ACCEPTED_BLOCKED_REFERENCE_INSUFFICIENT;
BLOCK_CAUSE=OBSERVABILITY_AND_GATE_DESIGN;
IDENTITY_HYPOTHESIS=STRONGLY_SUPPORTED_NOT_CERTIFIED;
G2_FRAG=BLOCKED;
G2_SOLUTE=NOT_EXECUTED;
TI3_PLUS_AUTHORIZED=false;
```

AUTORIZO UMA ÚNICA TRANSIÇÃO INTEGRADA, SEM MICROAUTORIZAÇÕES:

**TI2R-FRAG-DIRECT — CERTIFICAÇÃO TERMINAL DO MAPEAMENTO RASTER DIRETO.**

## 1. Merge governado do PR #7

Realize preflight read-only e confirme:

* repositório `lmbernardo7520112/snbi-dendritic-fragmentation-ml`;
* PR #7 ainda `OPEN`, `DRAFT`, mergeable e sem conflitos;
* base `main`;
* head `feat/ti2r-frag-registration`;
* head SHA exatamente `238be21569c36d62a3d82a27cf1ec3157cdf005c`;
* base SHA exatamente `0245faf74aa15424d95d43f92e87b32a06ac987b`;
* runs `35339501913` e `35339645238` concluídos com `SUCCESS`;
* jobs `deterministic-contracts` e `scientific-synthetic-contracts` aprovados;
* branch local e remota no mesmo SHA;
* worktree e index limpos.

Qualquer divergência deverá interromper a operação:

```text
PR7_MERGE=BLOCKED_PREFLIGHT_REQUIRES_AUTHOR_DECISION
```

Se todas as condições forem satisfeitas:

1. torne o PR #7 Ready for Review;
2. se surgir nova CI, aguarde e exija sucesso no mesmo SHA;
3. faça merge exclusivamente por merge commit;
4. não use squash, rebase, auto-merge ou force-push;
5. preserve a branch de trabalho;
6. aguarde eventual CI pós-merge;
7. sincronize a `main` local exclusivamente por fast-forward;
8. confirme `main == origin/main`.

Não altere arquivos, commits ou o resultado científico do PR #7. Caso a CI falhe, interrompa sem corrigir automaticamente.

## 2. Nova branch e autoridade

A partir da `main` pós-merge, crie:

```text
feat/ti2r-frag-direct-mapping
```

A autoridade consumida anteriormente não poderá ser reutilizada.

A nova autoridade será válida exclusivamente para esta fase integrada e para os ativos explicitamente relacionados abaixo.

## 3. Hipótese científica única

Testar somente a hipótese:

> ESM3 e ESM6 são derivados anotados, no mesmo sistema de coordenadas raster de ESM1 e ESM4, admitindo apenas identidade ou deslocamento inteiro causado por recorte/padding compatível com a diferença conhecida entre os canvases.

Não estão autorizados:

* transformação subpixel estimada;
* rotação;
* escala;
* transformação rígida contínua;
* similaridade;
* afim;
* projetiva;
* não rígida;
* ECC como estimador;
* competição aberta entre algoritmos;
* seleção oportunista de modelos.

## 4. Conjunto finito de candidatos

Determine os candidatos exclusivamente pelas dimensões raster já documentadas.

Para uma imagem móvel maior que a referência, considere somente origens inteiras de recorte:

```text
0 ≤ offset_x ≤ largura_móvel − largura_referência
0 ≤ offset_y ≤ altura_móvel − altura_referência
```

Para as dimensões documentadas, isso deverá resultar em:

* ESM3→ESM1: 21 candidatos, com `offset_x ∈ {0,1,2}` e `offset_y ∈ {0,…,6}`;
* ESM6→ESM4: três candidatos, com `offset_x ∈ {0,1,2}` e `offset_y = 0`.

A identidade deverá estar incluída.

Se as dimensões observadas não coincidirem com as dimensões já documentadas, interrompa sem ampliar a busca:

```text
TI2R_FRAG_DIRECT=BLOCKED_DIMENSION_DIVERGENCE
```

Documente inequivocamente a convenção de coordenadas e o sentido do mapeamento móvel→referência.

## 5. Ativos permitidos

Desenvolvimento:

* ESM1/ESM3: índices `0`, `146` e `293`;
* ESM4/ESM6: índices `0`, `197` e `394`.

Holdout temporal interno:

* ESM1/ESM3: índices `73` e `219`;
* ESM4/ESM6: índices `98` e `295`.

Os 12 ativos de desenvolvimento poderão ser abertos somente durante a execução autorizada.

Os ativos de holdout de cada par somente poderão ser abertos se esse par passar integralmente o desenvolvimento e após o congelamento do mapeamento.

Permanecem proibidos:

* qualquer frame adicional;
* ESM2 e ESM5;
* ZIP, MP4, FFmpeg ou FFprobe;
* redecodificação;
* alteração dos binários experimentais;
* labels ou ledger de eventos;
* dataset ML, splits, baseline de eventos, CNN ou treinamento;
* conversão física;
* TI-3 a TI-8;
* instalação ou alteração do sistema operacional.

Nenhum binário experimental poderá ser versionado.

## 6. Avaliação direta

Preserve integralmente o método anterior como histórico. Não reescreva seus resultados.

Implemente uma avaliação determinística que:

1. remova por máscaras congeladas círculos, halos, textos, timestamps, barra de escala e bordas;
2. compare somente o fundo radiográfico comum;
3. aceite máscaras parciais;
4. não rejeite bloco ou residual por apresentar erro alto;
5. separe deterministicamente blocos espaciais de seleção e blocos de auditoria;
6. utilize os blocos de seleção para escolher o candidato;
7. utilize exclusivamente os blocos de auditoria para calcular as métricas finais;
8. utilize score fixo e testado sinteticamente, baseado em correlação normalizada do gradiente ou representação equivalente previamente especificada;
9. classifique cada frame como `IDENTIFIABLE` ou `NON_IDENTIFIABLE`;
10. determine a identificabilidade exclusivamente pela textura e quantidade de informação da imagem de referência, nunca pelo residual, pela imagem móvel ou pelo resultado desejado;
11. compare o candidato vencedor com todos os demais offsets do conjunto finito;
12. exija candidato único, com margem de separação pré-registrada e validada somente em dados sintéticos.

O instante inicial poderá ser `NON_IDENTIFIABLE`. Isso não constitui PASS nem evidência de desalinhamento.

Não reutilize:

* suporte integral de 100% por tile;
* suporte global ≥90% como requisito isolado;
* média agregada para esconder falhas locais.

Congele, antes de qualquer acesso experimental desta fase:

* particionamento espacial;
* máscaras;
* representação;
* critério de textura;
* quantidade mínima absoluta de pixels válidos;
* cobertura mínima de quadrantes;
* score;
* margem de unicidade;
* controles negativos;
* limiares;
* regras de parada.

## 7. Critérios de desenvolvimento

Um par passará o desenvolvimento somente se:

* pelo menos dois de seus três instantes forem `IDENTIFIABLE`;
* o mesmo offset inteiro único vencer em todos os instantes identificáveis;
* houver evidência nos quatro quadrantes;
* o candidato vencer os demais offsets com a margem congelada;
* nenhum instante identificável contrariar o mapeamento;
* nos blocos espaciais de auditoria:

```text
mediana ≤ 1 px
P95 ≤ 2 px
máximo ≤ 3 px
```

A medição de residual poderá usar correlação de fase local fixa somente como métrica de auditoria, nunca para ampliar ou alterar o conjunto de candidatos.

## 8. Validação interna única

Para cada par que passar o desenvolvimento:

1. congele definitivamente o offset;
2. abra seus quatro ativos de holdout uma única vez;
3. aplique exatamente o método congelado;
4. não reajuste máscara, critério, score, limiar ou offset;
5. não retorne ao desenvolvimento;
6. não faça retry.

O par será certificado se:

* ao menos um dos dois instantes de holdout for `IDENTIFIABLE`;
* todos os instantes identificáveis aprovarem o mesmo offset;
* nenhum instante identificável violar os limiares espaciais.

Essa evidência deverá ser descrita como validação temporal interna à mesma aquisição, não como validação experimental externa ou ground truth metrológico.

## 9. Execução one-shot

Utilize no máximo três commits:

### C1 — método congelado e inativo

* protocolo;
* configuração;
* implementação;
* contratos RED;
* testes sintéticos;
* guardrails;
* autoridade inativa.

Antes de C1:

* nenhum ativo experimental aberto nesta fase;
* todos os testes sintéticos e guardrails verdes.

### C2 — ativação

C2 poderá alterar exclusivamente autoridade e decisão de execução.

Depois de C2:

* nenhum código, máscara, configuração, parâmetro, critério ou limiar poderá mudar;
* execute o runner científico exatamente uma vez.

### C3 — resultado e encerramento

C3 poderá conter somente:

* resultados;
* evidências;
* relatório conciso;
* consumo e fechamento da autoridade.

Um resultado científico bloqueado não autoriza retry ou commit corretivo do método.

## 10. Estados terminais

Se ambos os pares passarem desenvolvimento e holdout:

```text
TI2R_FRAG_DIRECT=PASS;
G2_FRAG=PASS_DIRECT_RASTER_MAPPING;
G2_SPATIAL=PARTIAL_PENDING_G2_SOLUTE;
```

Se apenas um par passar:

```text
TI2R_FRAG_DIRECT=PARTIAL_ONE_PAIR;
G2_FRAG=PARTIAL_ONE_PAIR;
```

Se nenhum offset único e estável puder ser certificado:

```text
TI2R_FRAG_DIRECT=BLOCKED_DIRECT_MAPPING;
G2_FRAG=BLOCKED;
```

Se a referência continuar insuficiente:

```text
TI2R_FRAG_DIRECT=BLOCKED_REFERENCE_STILL_INSUFFICIENT;
G2_FRAG=BLOCKED;
```

Se ocorrer `PARTIAL` ou `BLOCKED`, encerre definitivamente novas tentativas automáticas para o par não aprovado. As únicas alternativas futuras deverão ser:

* coordenadas originais utilizadas para produzir as anotações;
* referência manual independente com protocolo próprio;
* nova anotação;
* nova aquisição experimental;
* abandono justificado desse registro.

Não implementar outro registrador.

Em qualquer resultado:

```text
G2_SOLUTE=NOT_EXECUTED;
G3=BLOCKED_OR_PENDING_G2_COMPLETE;
TI3_PLUS_AUTHORIZED=false;
```

## 11. Publicação

Após C3:

* execute testes, guardrails e CI;
* faça push fast-forward;
* abra um Draft PR contra `main`;
* mantenha-o `OPEN/DRAFT`;
* não faça Ready ou merge;
* não crie remediações adicionais;
* não produza inventário narrativo exaustivo de comandos.

Retorne somente com:

* resultado terminal;
* SHA do merge do PR #7;
* branch e SHAs C1/C2/C3;
* URL do novo Draft PR;
* resultado da CI;
* offset avaliado e certificado por par;
* frames `IDENTIFIABLE` e `NON_IDENTIFIABLE`;
* métricas por instante e por par;
* ativos de holdout efetivamente abertos;
* confirmação de execução única;
* confirmação de ausência de novos dados, ESM2/ESM5 e TI-3+;
* worktree final limpo.

Estados finais obrigatórios:

```text
STATE=CLOSED_CONSUMED;
CURRENT_AUTHORIZED_ACTIVITY=NONE_AWAITING_AUTHOR_DECISION;
TI2R_EXECUTION_AUTHORIZED=false;
TI3_PLUS_AUTHORIZED=false;
MERGE_AUTHORIZED=false.
```
