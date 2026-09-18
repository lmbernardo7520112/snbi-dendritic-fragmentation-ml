# TI2R-SOLUTE-DIRECT — decisão integrada do autor

Autor: Leonardo Maximino Bernardo. Data: 2026-09-18.

## Estado desta autorização

Estado: `CLOSED_CONSUMED`. A única invocação retornou código 2 e
`TI2R_SOLUTE_DIRECT=BLOCKED_IDENTITY_NOT_DISCRIMINATIVE`. Foram abertos uma
vez os 12 ativos de desenvolvimento; nenhum holdout foi aberto nesta fase.
Nenhum código ou critério mudou depois de C2. Não haverá retry ou outro
registrador; G2_FRAG permanece PASS_DIRECT_RASTER_MAPPING.
Base pós-merge PR #8: `db03183e1456f67b5b663a4cb71361cad1404dcb`.
Autoridade independente: `configs/authority/ti2r-solute-direct.json`.
Todas as autoridades anteriores permanecem CLOSED_CONSUMED; o PASS de
fragmentação não é reaberto nem rebaixado. C2 ativa uma execução; C3 consome.

## Instrução autoral integral

SHA-256 do texto recebido: `dbc2c607a3a5ef5f8980ae4dc87f6a4bf425976e618e9d1e3d487d9b8568f540`.

APROVO O RESULTADO DA AUDITORIA INDEPENDENTE DO PR #8 E REGISTRO:

```text
PR8_INDEPENDENT_AUDIT=PASS;
TI2R_FRAG_DIRECT_RESULT=ACCEPTED;
G2_FRAG=PASS_DIRECT_RASTER_MAPPING;
PR8_MERGE_READINESS=READY_EXACT_SHA;
PR8_ONE_TIME_MERGE_AUTHORIZATION=GRANTED_EXACT_SHA;
TI3_PLUS_AUTHORIZED=false;
```

AUTORIZO UMA ÚNICA FASE INTEGRADA E TERMINAL:

**TI2R-SOLUTE-DIRECT — CERTIFICAÇÃO MULTIMODAL DA CONGRUÊNCIA RASTER DOS CAMPOS RELATIVOS DE SOLUTO.**

## 1. Merge governado do PR #8

Realize preflight read-only confirmando:

* repositório `lmbernardo7520112/snbi-dendritic-fragmentation-ml`;
* PR #8 `OPEN`, `DRAFT`, mergeável e sem conflitos;
* base `main` no SHA `b7bbb6a1f0d3eaa43866027762eb2ed061c3d7c6`;
* head `feat/ti2r-frag-direct-mapping`;
* head SHA exatamente `6905d17a39853cbb80666194f3a32542a3b82f42`;
* cadeia C1→C2→C3 preservada;
* runs `35357545606` e `35357710250` em `SUCCESS`;
* jobs `deterministic-contracts` e `scientific-synthetic-contracts` aprovados;
* branch local e remota no SHA C3;
* worktree e index limpos.

Qualquer divergência deverá interromper:

```text
PR8_MERGE=BLOCKED_REQUIRES_NEW_AUTHOR_DECISION
```

Se tudo estiver correto:

1. publique um único comentário conciso registrando esta autorização e o SHA exato;
2. torne o PR #8 Ready for Review;
3. se surgir nova CI, aguarde e exija sucesso no mesmo SHA;
4. faça merge exclusivamente por merge commit, protegido pelo SHA autorizado;
5. não use squash, rebase, auto-merge, force-push ou exclusão de branch;
6. confirme dois pais, ancestralidade de C3 e conteúdo integrado;
7. aguarde eventual CI pós-merge;
8. se a CI pós-merge falhar, interrompa sem correção;
9. sincronize a `main` local exclusivamente por fast-forward;
10. preserve as branches anteriores.

Não altere nem remedeie o PR #8. O PASS de fragmentação fica definitivamente encerrado.

## 2. Nova branch e autoridade

Somente após merge e CI pós-merge verdes, crie da `main` atualizada:

```text
feat/ti2r-solute-direct-mapping
```

Crie autoridade independente e one-shot para `TI2R-SOLUTE-DIRECT`.

Não reutilize autoridades anteriores.

## 3. Hipótese científica única

Testar somente:

```text
ESM2→ESM1 = identidade raster
ESM5→ESM4 = identidade raster
```

ESM2 e ESM5 são campos radiográficos relativos/normalizados de enriquecimento e depleção, não mapas quantitativos de concentração absoluta.

Como referência e móvel possuem dimensões idênticas, somente `(0,0)` será transformação admissível.

Deslocamentos inteiros:

```text
dx,dy ∈ {-3,-2,-1,0,1,2,3}
```

poderão ser avaliados exclusivamente como controles negativos. Um deslocamento não nulo nunca poderá ser adotado como transformação alternativa. Se superar a identidade, o resultado será bloqueado.

Não estão autorizados:

* ajuste de translação;
* rotação, escala, similaridade, afim ou homografia;
* deformação não rígida;
* ECC;
* correlação bruta de intensidades como prova;
* SSIM, histogram matching ou CLAHE como prova geométrica;
* seleção oportunista de método;
* nova tentativa caso a identidade falhe.

## 4. Ativos permitidos

Desenvolvimento:

```text
ESM1/ESM2: 0, 146, 293
ESM4/ESM5: 0, 197, 394
```

Holdout temporal interno:

```text
ESM1/ESM2: 73, 219
ESM4/ESM5: 98, 295
```

Antes dos pixels, confirme dimensões idênticas às registradas no manifesto. Divergência bloqueia a fase.

É proibido:

* acessar ESM3 ou ESM6 nesta execução;
* selecionar novos frames;
* abrir ZIP ou MP4;
* executar FFmpeg/FFprobe;
* redecodificar;
* criar labels ou ledger;
* criar dataset ML ou splits;
* executar baseline, CNN ou treinamento;
* executar TI-3 a TI-8;
* versionar binários experimentais.

## 5. Método multimodal congelado

Antes de qualquer acesso experimental desta fase, congele em C1:

* máscaras de bordas, timestamps, textos, barra e camada de apresentação;
* grade e separação espacial irrevogável entre seleção e auditoria;
* critérios de identificabilidade;
* quantidade mínima absoluta de pixels;
* cobertura espacial;
* descritores;
* controles negativos espaciais e temporais;
* margens;
* métricas;
* limiares;
* regras de parada.

Utilize exatamente:

### Seleção

`MIND-SSC`, ou implementação explicitamente documentada do descritor de auto-semelhança multimodal, para avaliar se a identidade preserva estrutura local melhor que todos os deslocamentos-controle.

### Auditoria independente

`NGF` sign-invariant — produto normalizado de gradientes elevado ao quadrado — em blocos espacialmente disjuntos dos blocos de seleção.

MIND-SSC e NGF deverão ser implementados e calibrados somente com phantoms sintéticos antes de C1.

Não substituir essas métricas depois de observar os dados.

## 6. Controles obrigatórios

A identidade deverá superar:

1. todos os deslocamentos inteiros de `[-3,+3]²`, exceto `(0,0)`;
2. pares temporais incorretos entre os instantes de desenvolvimento;
3. controles sintéticos de:

   * inversão de contraste;
   * transformação monotônica e não linear de intensidade;
   * regiões uniformes;
   * textura periódica;
   * saturação;
   * conteúdo espacialmente independente;
   * deslocamentos conhecidos.

Os controles temporais não poderão ser usados para escolher frames favoráveis.

A comparação correta precisa demonstrar que o método responde à correspondência estrutural do mesmo instante, e não apenas à moldura ou a estruturas estáticas.

## 7. Identificabilidade

Classifique cada imagem como:

```text
IDENTIFIABLE
NON_IDENTIFIABLE
```

A classificação deverá utilizar somente propriedades individuais das imagens:

* energia e distribuição de gradientes;
* entropia ou informação estrutural;
* quantidade absoluta de pixels válidos;
* cobertura por quadrantes;
* ausência de saturação dominante.

Ela não poderá consultar:

* offset vencedor;
* score comparativo;
* residual;
* resultado esperado.

O índice 0 poderá ser `NON_IDENTIFIABLE`, sem PASS nem falha.

Exigir por par:

* pelo menos dois instantes identificáveis no desenvolvimento;
* pelo menos oito blocos válidos em cada papel;
* cobertura dos quatro quadrantes;
* pelo menos um holdout identificável.

## 8. Critérios de desenvolvimento

Um par passa somente se, em todos os instantes identificáveis:

* identidade for única e superior aos controles com margem congelada;
* pares temporais corretos superarem os controles temporais;
* MIND-SSC e NGF concordarem;
* não houver contradição temporal;
* nenhum bloco ou residual for descartado por erro elevado;
* os resíduos dos blocos de auditoria satisfizerem:

```text
mediana ≤ 1 px
P95 ≤ 2 px
máximo ≤ 3 px
```

Não usar:

* suporte integral de 100% por bloco;
* suporte global arbitrário de 90%;
* trimming;
* descarte de outliers;
* média agregada para ocultar falha de um instante.

## 9. Holdout único

Para cada par aprovado no desenvolvimento:

1. congele a identidade e todos os parâmetros;
2. abra seus holdouts uma única vez;
3. aplique o método sem refit;
4. não altere máscara, descritor, margem ou limiar;
5. não retorne ao desenvolvimento;
6. não execute retry.

Todos os holdouts identificáveis deverão passar. Ao menos um holdout por par deverá ser identificável.

## 10. Execução one-shot

Utilize no máximo três commits:

### C1 — método inativo e congelado

* protocolo;
* configuração;
* código;
* testes sintéticos;
* guardrails;
* autoridade `PREPARED_INACTIVE`.

Nenhum pixel ESM2/ESM5 poderá ser aberto antes de C1.

### C2 — ativação

C2 poderá modificar somente autoridade e decisão:

```text
ACTIVE_ONE_SHOT
```

Após C2:

* nenhuma alteração científica será permitida;
* execute o runner exatamente uma vez.

### C3 — resultado e encerramento

C3 poderá conter somente:

* resultados;
* evidências;
* relatório conciso;
* autoridade `CLOSED_CONSUMED`.

Resultado bloqueado não autoriza correção, segundo runner ou novo registrador.

Não crie commit pós-publicação: PR e GitHub Actions constituem a evidência dinâmica de push e CI.

## 11. Estados terminais

Ambos os pares aprovados:

```text
TI2R_SOLUTE_DIRECT=PASS_DIRECT_MULTIMODAL_MAPPING;
G2_FRAG=PASS_DIRECT_RASTER_MAPPING;
G2_SOLUTE=PASS_INTERNAL_DIRECT_RASTER_IDENTITY;
G2_SPATIAL=PASS_WITHIN_SAMPLED_ACQUISITIONS;
G3=PENDING_SEPARATE_DECISION;
```

Somente um par aprovado:

```text
TI2R_SOLUTE_DIRECT=PARTIAL_ONE_PAIR;
G2_FRAG=PASS_DIRECT_RASTER_MAPPING;
G2_SOLUTE=PARTIAL_ONE_PAIR;
G2_SPATIAL=PARTIAL;
```

Custódia ou dimensão divergente:

```text
TI2R_SOLUTE_DIRECT=BLOCKED_CUSTODY_OR_DIMENSION_DIVERGENCE;
```

Informação insuficiente:

```text
TI2R_SOLUTE_DIRECT=BLOCKED_MODALITY_INFORMATION_INSUFFICIENT;
```

Identidade não discriminativa:

```text
TI2R_SOLUTE_DIRECT=BLOCKED_IDENTITY_NOT_DISCRIMINATIVE;
```

Métricas multimodais discordantes:

```text
TI2R_SOLUTE_DIRECT=BLOCKED_MULTIMODAL_METRIC_DISCORDANCE;
```

Holdout reprovado:

```text
TI2R_SOLUTE_DIRECT=BLOCKED_INTERNAL_VALIDATION;
```

Em qualquer bloqueio:

```text
G2_FRAG=PASS_DIRECT_RASTER_MAPPING;
G2_SOLUTE=BLOCKED;
G2_SPATIAL=PARTIAL_FRAG_ONLY;
```

O PASS da fragmentação nunca poderá ser rebaixado por falha solutal.

Se houver `PARTIAL` ou `BLOCKED`, encerre o registro automático solutal. Alternativas futuras ficam limitadas a:

* scripts ou coordenadas originais dos autores;
* documentação da produção dos vídeos normalizados;
* landmarks humanos independentes sob protocolo próprio;
* rederivação a partir dos dados radiográficos originais;
* nova aquisição.

## 12. Limites das alegações

Mesmo em PASS, declarar somente:

> Nos instantes amostrados das duas aquisições, os campos radiográficos relativos de soluto são espacialmente congruentes com as radiografias correspondentes, dentro do protocolo multimodal e das tolerâncias pré-registradas.

Não alegar:

* concentração absoluta ou wt.% de Bi;
* calibração de intensidade;
* ground truth metrológico;
* detecção ou prova de convecção;
* causalidade entre orientação e transporte;
* generalização para novos experimentos;
* independência estatística entre frames;
* escala física ou incerteza completa.

## 13. Publicação

Após C3:

* execute testes e guardrails;
* faça push fast-forward;
* abra um novo Draft PR contra `main`;
* aguarde CI;
* mantenha o PR `OPEN/DRAFT`;
* não faça Ready ou merge;
* não crie remediações adicionais;
* não produza inventário narrativo exaustivo de comandos.

Retorne com:

* resultado terminal;
* SHA do merge do PR #8;
* branch e SHAs C1/C2/C3;
* Draft PR;
* CI no SHA C3;
* frames identificáveis e não identificáveis;
* métricas MIND-SSC e NGF por instante;
* controles espaciais e temporais;
* resíduos por instante e agregados;
* ativos de holdout efetivamente abertos;
* confirmação de uma única execução;
* confirmação de ausência de dados novos e TI-3+;
* worktree final limpo.

Estados finais obrigatórios:

```text
STATE=CLOSED_CONSUMED;
CURRENT_AUTHORIZED_ACTIVITY=NONE_AWAITING_AUTHOR_DECISION;
TI2R_EXECUTION_AUTHORIZED=false;
TI3_PLUS_AUTHORIZED=false;
MERGE_AUTHORIZED=false.
```
