# Study4 — plano de gates e decisões

A fonte de autoridade é [authority.json](../../configs/study4/authority.json).
Cada gate futuro exige prompt específico e termina em STOP. Uma aprovação
não autoriza automaticamente o gate seguinte, nem o orçamento futuro
autoriza ciência agora.

| Gate conceitual | Pré-condições e escopo | Saída e parada |
| --- | --- | --- |
| S4-0 — atual | Base e branch/worktree corretos; apenas seis docs e quatro JSONs; validação textual e custódia histórica. | Um commit de dez adições, push normal, NONE_AWAITING_S4_A_AUTHOR_DECISION. |
| S4-A — futuro | Nova decisão explicita allowlist de metadados TRAIN, definição de frames válidos, implementação determinística autorizada e seu freeze. | Examinar suporte/matching somente quando autorizado; >=16 pares, T=8, quatro folds e ambas aquisições. Suporte insuficiente: INSUFFICIENT_COVERAGE_OVERLAP e nenhum modelo. Mesmo com suporte suficiente: STOP. |
| Freeze operacional futuro | Decisão própria após S4-A; completar contratos de folds pair-aware, interfaces, custódia, receipt e avaliação do controle. | Deliberar e congelar regra/threshold de neutralização antes de toda execução científica futura; implementação e testes sintéticos somente sob autorização específica. STOP. |
| Controle de cobertura futuro | Suporte suficiente, freeze operacional e decisão científica explícita para uma invocação consumível, sem retry. | Executar somente o controle antes de modelos visuais. Falha: COVERAGE_NEUTRALIZATION_FAIL, encerrar sem benchmark visual. Sucesso: STOP aguardando gate visual. |
| Benchmark visual futuro | Controle aceito e autorização específica do gate; continuidade governada da mesma invocação lógica e mesmo orçamento, sem refit do controle. | Quatro condições visuais, até 16 fits visuais, cinco contrastes congelados. Preservar qualquer resultado e encerrar autoridade. |
| Auditoria/closeout futuro | Nova decisão limitada à evidência já emitida. | Verificar e relatar sem recalcular ciência, modificar método ou repetir execução. |

A articulação operacional de uma única invocação científica com a parada entre
controle e visual deverá ser congelada antes de ciência: uma mesma identidade
de execução/receipt, orçamento persistente e continuidade condicionada a nova
decisão, sem segunda tentativa ou ajuste de modelos. S4-0 não implementa essa
continuidade, não cria receipt e não presume que o runner Study3 a suporte.
Se essa governança não estiver resolvida no freeze operacional, ciência
permanece bloqueada.

## Critério do controle primário

COVERAGE_METADATA_LOGREG deve avaliar exclusivamente a cobertura dos frames
comuns selecionados, antes de qualquer RF ou CNN. O benchmark visual somente
poderá ocorrer se o controle não conservar discriminação relevante.
O alvo conceitual é desempenho compatível com chance. Threshold operacional,
estatística de decisão e tratamento de bordas permanecem pendentes; não há
novo threshold numérico, p-value ou exceção adaptativa em S4-0.

## Validação documental e publicação S4-0

Validar os quatro JSONs, consistência de referências entre dez arquivos,
inventário exato e whitespace. Git deve demonstrar que nenhum arquivo tracked
herdado foi modificado. Zero leitura experimental, matching real, feature,
fit ou receipt. Mostrar exatamente dez paths staged, todos adições sob
docs/study4 e configs/study4; nenhum outro arquivo.

Commit autorizado: `docs(study4): freeze coverage-controlled study protocol`.
Push normal da nova branch, sem force ou rebase. Após sucesso, STOP; não
acionar S4-A, criar PR ou interpretar CI como autoridade científica.

## Parada por estado inesperado

```text
STOP_AND_REPORT
DO_NOT_REPAIR_AUTOMATICALLY
DO_NOT_RETRY
```

Aplica-se a divergência de HEAD/branch, arquivo extra, alteração histórica,
falha de custódia, escopo ou validação, permissão científica ausente/ambígua e
tentativa de reabrir Study3. Não reduzir T, mínimo de pares, número de folds,
modelo ou exigência de aquisições para forçar progressão.
