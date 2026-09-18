# TI2R-FRAG — decisão autoral de execução pontual

Autor: Leonardo Maximino Bernardo. Data: 2026-09-18.

## Registro de transição

Estado: `ACTIVE_ONE_SHOT`. C1 foi commitado integralmente antes de pixels.
C2 ativa exatamente uma invocação; publicação permanece proibida até C3.
O receipt atômico deve preceder todo byte experimental; interrupção não permite retry.
A autoridade específica canônica é `configs/authority/ti2r-frag.json`;
`pyproject.toml [tool.snbi]` conserva a TI-2 histórica fechada.
C2 alterará somente este registro e a autoridade específica.
C3 consumirá a autorização mesmo se a tentativa ficar bloqueada.

## Instrução autoral integral e preservada

SHA-256 do texto recebido: `4bfecc8b08df0463b9de9e54d1cb343c18160f30fde665a7f0a98312390d8af3`.

APROVO A DELIBERAÇÃO DE CONVERGÊNCIA E CONSIDERO SUPERADO O PROCEDIMENTO EXTENSO TI2R-P0 ANTERIORMENTE PROPOSTO.

AUTORIZO EXCLUSIVAMENTE A EXECUÇÃO INTEGRADA DA:

# TI2R-FRAG — Recuperação do registro dos overlays de fragmentação

## 1. Objetivo único

Resolver exclusivamente o registro espacial:

```text
ESM3 → ESM1  — bottom-up
ESM6 → ESM4  — top-down
```

A fase deverá terminar obrigatoriamente em:

```text
TI2R_FRAG=PASS
```

ou:

```text
TI2R_FRAG=PARTIAL_*
```

ou:

```text
TI2R_FRAG=BLOCKED_*
```

Não é autorizada nova rodada automática de refinamento.

## 2. Base e branch

Executar preflight read-only e confirmar:

```text
repository=lmbernardo7520112/snbi-dendritic-fragmentation-ml
base_branch=main
base_sha=0245faf74aa15424d95d43f92e87b32a06ac987b
new_branch=feat/ti2r-frag-registration
```

Exigir:

* checkout standalone;
* worktree e index limpos;
* `main == origin/main == base_sha`;
* branch nova inexistente local e remotamente;
* nenhuma operação Git em andamento;
* guardrail de dados com `content_bytes_read=0`;
* ambiente sem instalação adicional.

Qualquer divergência deve retornar:

```text
TI2R_FRAG=BLOCKED_PREFLIGHT
```

Esta decisão explícita do autor supera exclusivamente as restrições antigas de branch e escrita referentes ao encerramento da TI-2. Todos os demais guardrails continuam válidos.

## 3. Escopo experimental fechado

Usar somente os 20 ativos já decodificados do piloto:

| Condição  | Par       | Desenvolvimento | Validação condicional |
| --------- | --------- | --------------- | --------------------- |
| bottom-up | ESM3→ESM1 | 0, 146, 293     | 73, 219               |
| top-down  | ESM6→ESM4 | 0, 197, 394     | 98, 295               |

Isso corresponde a:

* 12 imagens de desenvolvimento;
* 8 imagens de validação;
* nenhuma imagem nova.

Permanecem proibidos:

* ESM2 e ESM5;
* ZIP, MP4, FFmpeg e FFprobe;
* redecodificação;
* novos frames;
* extração massiva;
* labels ou ledger de eventos;
* dataset ML e splits;
* baseline de detecção;
* CNN e treinamento;
* conversão para unidades físicas;
* TI-3 a TI-8.

Se os ativos já decodificados não estiverem disponíveis ou não corresponderem ao manifesto congelado, retornar:

```text
TI2R_FRAG=BLOCKED_PILOT_UNAVAILABLE
```

Não procurar outra fonte e não redecodificar.

## 4. Autoridade canônica

Não reativar a autoridade histórica da TI-2 e não reutilizar `scripts/run_ti2.py`.

Criar:

* autoridade específica e namespaced para `TI2R-FRAG`;
* novo runner, por exemplo `scripts/run_ti2r_frag.py`;
* validador que impeça duas autoridades científicas simultaneamente ativas.

A autoridade histórica da TI-2 deve permanecer fechada.

A nova autoridade deve registrar, no mínimo:

```text
phase=TI2R_FRAG
state=PREPARED_INACTIVE | ACTIVE_ONE_SHOT | CLOSED_CONSUMED
authorization_id=TI2R-FRAG-2026-09-18
authorized_branch=feat/ti2r-frag-registration
base_sha=0245faf74aa15424d95d43f92e87b32a06ac987b
allowed_pairs=[ESM3-to-ESM1, ESM6-to-ESM4]
allowed_frame_indices=<índices congelados acima>
max_invocations=1
validation_policy=OPEN_ONCE_AFTER_FREEZE
ti3_plus_authorized=false
```

Toda autorização de I/O deve ser verificada antes de normalizar caminho, executar `stat`, abrir arquivo, calcular hash, criar diretório ou ler qualquer byte experimental.

## 5. Modelo obrigatório de três commits

Esta autorização cobre branch, staging explícito, três commits, execução única, push, Draft PR e consulta da CI. Não solicitar novas autorizações metodológicas entre essas atividades.

### C1 — protocolo e implementação congelados

```text
feat(ti2r): freeze integrated fragment registration recovery
```

Antes de qualquer leitura de pixels:

* produzir um único protocolo compacto;
* registrar a exposição dos 20 ativos;
* implementar runner, autoridade, algoritmo e testes;
* congelar métodos, máscaras, métricas, parâmetros e stop rules;
* executar somente testes sintéticos;
* manter a autoridade `PREPARED_INACTIVE`.

O protocolo deve declarar:

* transformação móvel → referência;
* `x=coluna`, `y=linha`;
* origem no centro do pixel superior esquerdo;
* transformação única e estática por par;
* ausência de reflexão e inversão de eixos;
* ausência de transformação por frame;
* proibição de modelos projetivos ou não rígidos;
* limites das alegações.

C1 deve estar integralmente commitado antes de abrir qualquer pixel experimental.

### C2 — ativação pontual

```text
chore(authority): activate one-shot TI2R-FRAG execution
```

C2 pode alterar somente a autoridade canônica e seu registro de decisão.

Exigir:

```text
state=ACTIVE_ONE_SHOT
max_invocations=1
```

Não publicar nem fazer push enquanto C2 for o tip da branch.

### Execução única entre C2 e C3

Executar o novo runner exatamente uma vez.

Antes do primeiro byte experimental, o runner deve criar atomicamente um receipt/lock contendo:

* SHA de C2;
* hashes do protocolo, runner, configuração e código científico;
* assets permitidos;
* estado de exposição;
* contador de invocações;
* confirmação de que nenhum receipt anterior existe.

Depois de C2:

* não editar código;
* não mudar máscara;
* não mudar métrica;
* não mudar limiar;
* não mudar parâmetros;
* não mudar ordem dos modelos;
* não realizar retry.

Se houver interrupção, registrar resultado terminal `BLOCKED_INTERRUPTED` e seguir diretamente para C3.

### C3 — consumo e fechamento

```text
chore(authority): consume TI2R-FRAG authorization and close phase
```

C3 deve conter somente:

* autoridade fechada;
* receipt;
* configurações/matrizes resultantes;
* métricas;
* relatório terminal;
* documentação de encerramento.

Exigir:

```text
state=CLOSED_CONSUMED
current_authorized_activity=NONE_AWAITING_AUTHOR_DECISION
ti2r_execution_authorized=false
ti3_plus_authorized=false
merge_authorized=false
```

O diff C2→C3 não pode alterar código, algoritmo, máscara, parâmetros ou configuração científica previamente congelada.

Se não for possível produzir C3 após a ativação, não fazer push e retornar:

```text
AUTHORITY_ACTIVE_LOCAL_REQUIRES_MANUAL_CLOSEOUT
```

## 6. Registro de exposição e validação

Distinguir:

* materialização mecânica;
* inspeção visual;
* leitura algorítmica;
* uso em estimação;
* influência sobre método ou parâmetros;
* uso em validação.

A ausência de log não comprova lacre.

Os frames de validação somente podem ser abertos se houver evidência textual positiva de que não foram anteriormente usados em:

* matching;
* estimação;
* escolha de máscara;
* escolha de método;
* ajuste de parâmetros;
* inspeção visual orientada ao desenvolvimento.

Se essa condição não puder ser demonstrada:

* não abrir os frames de validação;
* permitir apenas o resultado de desenvolvimento;
* retornar:

```text
TI2R_FRAG=PARTIAL_DEVELOPMENT_ONLY
```

ou, se nem o desenvolvimento for válido:

```text
TI2R_FRAG=BLOCKED_VALIDATION_CUSTODY
```

## 7. Método científico congelado

Usar raster nativo, sem redimensionamento.

É permitido:

* luminância;
* gradiente determinístico;
* normalização robusta fixa;
* mascaramento dos círculos coloridos e halos;
* exclusão determinística de textos, timestamps, barra de escala e bordas;
* interpolação bilinear para imagem;
* vizinho mais próximo para máscaras.

É proibido:

* usar círculos como fiduciais;
* CLAHE;
* escolha visual de ROI;
* recorte oportunista;
* exclusão de regiões de erro alto;
* ajuste após observar validação.

A regra que deriva máscaras e parâmetros pode usar os frames de desenvolvimento somente se a própria regra algorítmica tiver sido congelada em C1. Não é permitido ajuste humano iterativo.

## 8. Hierarquia única e terminal

Executar sequencialmente:

```text
M0 — identidade
M1 — translação
M2 — rígida
M3 — afim
```

Regras:

1. M0 é sempre avaliado.
2. Um único transform é estimado conjuntamente nos três tempos de desenvolvimento de cada par.
3. O modelo seguinte só é executado quando o anterior falhar algum critério absoluto.
4. O primeiro modelo que passar é congelado.
5. Modelos posteriores não são executados.
6. Falha de M3 produz `BLOCKED_METHOD_HIERARCHY`.
7. Depois da validação não existe retorno à estimação.

A função de ajuste deve usar correlação normalizada de gradientes no suporte mascarado ou formulação equivalente previamente justificada e congelada.

## 9. Referência independente e métricas

A função usada para estimar não pode validar o próprio resultado.

Congelar em C1 uma referência independente automática baseada em regiões espaciais disjuntas das usadas no ajuste, preferencialmente deslocamentos residuais por correlação de fase local em tiles fixos e distribuídos pelo campo.

Exigir:

* tiles de avaliação não usados no fitting;
* cobertura dos quatro quadrantes, quando houver suporte;
* pelo menos oito tiles válidos por par;
* nenhum descarte por erro alto;
* suporte válido pós-transformação ≥ 90%.

Se não for possível construir referência independente com cobertura adequada:

```text
TI2R_FRAG=BLOCKED_REFERENCE_INSUFFICIENT
```

Métrica primária:

```text
erro residual espacial em pixels
```

Critérios por par, tanto no desenvolvimento quanto na validação:

```text
mediana ≤ 1 px
P95 ≤ 2 px
máximo ≤ 3 px
roundtrip matriz–inversa ≤ 0,25 px
determinante linear positivo
sem reflexão
nenhum frame individual fora dos limites
```

O roundtrip é apenas teste numérico, não evidência experimental.

Permanecer em pixels. Não realizar conversão para micrômetros.

## 10. Testes obrigatórios antes dos dados

Usar somente fixtures sintéticas para demonstrar:

* identidade;
* translação;
* rígida;
* afim;
* máscara de overlay;
* rejeição de reflexão;
* ordem da hierarquia;
* parada no primeiro PASS;
* bloqueio de validação sem lacre;
* invocação única;
* allowlist exata de assets;
* zero acesso a ESM2/ESM5;
* autoridade verificada antes de I/O;
* consumo definitivo da autorização.

Não instalar dependências. Usar apenas o ambiente existente.

É permitida alteração mínima da CI para incluir esses testes no job científico existente, sem mudar versões de dependências ou realizar hardening adicional.

## 11. Estados terminais

```text
TI2R_FRAG=PASS
G2_FRAG=PASS
```

Somente se os dois pares passarem desenvolvimento e validação.

```text
TI2R_FRAG=PARTIAL_ONE_CONDITION
G2_FRAG=PARTIAL
```

Se apenas um par passar. Isso não autoriza comparação entre condições.

```text
TI2R_FRAG=PARTIAL_DEVELOPMENT_ONLY
G2_FRAG=NOT_VALIDATED
```

Se houver candidato de desenvolvimento, mas nenhuma validação lacrada utilizável.

Ou um dos bloqueios:

```text
BLOCKED_PREFLIGHT
BLOCKED_PILOT_UNAVAILABLE
BLOCKED_VALIDATION_CUSTODY
BLOCKED_REFERENCE_INSUFFICIENT
BLOCKED_METHOD_HIERARCHY
BLOCKED_VALIDATION
BLOCKED_INTERRUPTED
BLOCKED_SCOPE_OR_DEPENDENCY
```

Qualquer bloqueio encerra a execução sem segunda tentativa.

Sempre preservar:

```text
G2_SOLUTE=NOT_EXECUTED
TI3_PLUS_AUTHORIZED=false
```

## 12. Publicação

Somente depois de C3:

1. confirmar autoridade `CLOSED_CONSUMED`;
2. executar guardrails e suítes;
3. confirmar nenhum binário experimental rastreado;
4. confirmar worktree e index limpos;
5. fazer push fast-forward da branch;
6. abrir um Draft PR contra `main`;
7. aguardar a CI automática no SHA de C3.

Não usar:

* force-push;
* squash;
* rebase;
* Ready for Review;
* merge;
* workflow manual;
* nova execução científica.

Uma CI verde no SHA final é suficiente. Runs automáticos adicionais podem ser reportados, mas não são requisito duplicado.

Se a CI final falhar, não alterar ciência nem executar novamente. Retornar:

```text
TI2R_FRAG=BLOCKED_CI_REQUIRES_AUTHOR_DECISION
```

## 13. Relatório terminal

Retornar relatório conciso contendo:

* estado terminal;
* branch e três SHAs;
* Draft PR;
* CI;
* autoridade final;
* 20 ativos autorizados e ativos efetivamente abertos;
* confirmação de que ESM2/ESM5 não foram acessados;
* confirmação de ausência de FFmpeg/redecodificação;
* modelo testado e primeiro modelo aprovado por par;
* matrizes produzidas, quando aplicável;
* métricas de desenvolvimento e validação;
* estado de abertura da validação;
* suporte/ROI comum em pixels, se certificado;
* resultado dos testes e guardrails;
* worktree final;
* limitações científicas.

Não produzir inventário narrativo exaustivo de comandos.

O PR deverá permanecer:

```text
PR_STATE=OPEN_DRAFT
MERGE_AUTHORIZED=false
CURRENT_AUTHORIZED_ACTIVITY=NONE_AWAITING_AUTHOR_DECISION
TI2R_EXECUTION_AUTHORIZED=false
TI3_PLUS_AUTHORIZED=false
```
