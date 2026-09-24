# Study4 — registro de riscos S4-0

Riscos pré-registrados; nenhum foi quantificado no corpus nesta fase.
Autoridade: [authority.json](../../configs/study4/authority.json).
Falha de identidade, custódia ou escopo exige STOP_AND_REPORT, sem reparo
automático ou retry. Falta de suporte e neutralização falha são saídas
científicas legítimas conforme o [plano de gates](STUDY4_GATE_PLAN.md).

| Risco | Controle futuro e consequência |
| --- | --- |
| Insufficient common support | Pelo menos oito frames comuns por edge e 16 pares; abaixo disso, INSUFFICIENT_COVERAGE_OVERLAP, nenhum modelo. |
| Acquisition imbalance | Ambas as aquisições devem estar representadas; documentar composição sob autorização futura, sem nova quota adaptativa. |
| Weak-label dependence | Papéis já existentes, sem mineração; discriminação de weak labels não é validação física. |
| Pair reuse/leakage | Matching um-para-um, grupos únicos e par inteiro em um fold; violação bloqueia. |
| Frame-index mismatch | Exigir frames selecionados exatamente iguais para os dois membros e identidade autenticada; divergência bloqueia antes de payload. |
| Temporal coverage leakage | Mesmo suporte T=8 para condições e controle; congelar gate metadata antes de ciência e bloquear modelos visuais se falhar. |
| Target-construction shortcut | Matching de cobertura não elimina todos os mecanismos de construção de target; claims limitados, sem inferência causal. |
| Low effective sample size | Pares/grupos são dependentes; não tratar quantidade de frames como tamanho amostral independente. |
| Only two physical acquisitions | Não alegar replicação experimental independente ou generalização externa. |
| Model-shopping risk | Exatamente seis condições e cinco contrastes; parâmetros herdados, até 20 fits, nenhuma seed/modelo adicional. |
| Post-hoc threshold choice | Critério operacional pendente deverá ser deliberado e congelado antes de execução; nenhum threshold inventado agora ou após scores. |
| Accidental DEV/TEST reopening | Allowlist futura restrita a TRAIN; DEV, TEST e caches/índices correspondentes negados. |
| Accidental reuse of Study3 scientific authority | Study3 CLOSED_CONSUMED; configuração/receipt futuro Study4 separados e decisão explícita. |
| Treating frames as independent experimental units | Unidade primária é par, divisão por par e custódia de grupo; frames não são réplicas físicas. |
| Reuse of full original trajectories | Adaptação futura usa apenas oito frames comuns selecionados; mean e metadata não podem recuperar cobertura desigual excluída. |
| Historical folds incompatible with pairs | Não dividir um par para conservar automaticamente folds antigos; regra operacional futura congelada sem performance. |
| Automated progression despite a failed gate | Um gate por prompt, decisão explícita antes de cada gate, encerramento sem forçar CNN. |
| Missing/ambiguous provenance or authority | Ausência, valor desconhecido ou divergência bloqueia; sem fallback de corpus, reinterpretação de permissão ou retry. |
| Scope creep through implementation | S4-0 cria dez arquivos documentais/JSON; não implementa matching, leitor, runner ou validador científico. |
