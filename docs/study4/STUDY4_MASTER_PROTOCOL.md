# Study4 — protocolo mestre S4-0

Study4 investiga COVERAGE_CONTROLLED_TEMPORAL_REPRESENTATION. Esta fase
congela somente protocolo e governança; não implementa matching, leitores,
features, modelos, métricas ou runner. Nenhuma propriedade de suporte comum
do corpus foi examinada ou inferida nesta fase.

## Autoridade e proveniência

Decisão: `/STUDY4-S4-0-PROTOCOL-BOOTSTRAP`, de Leonardo Maximino Bernardo.
Base documental: `7ba1786948f39ca164c20d991d7525c18f7138e0`.
Branch independente: `feat/study4-coverage-controlled-temporal-representation`.
[authority.json](../../configs/study4/authority.json) registra as proibições
atuais. A presença destes contratos não concede autoridade científica.

Study1, Study2 e Study3 permanecem preservados. Study3 está CLOSED_CONSUMED,
não é reaberto e seus resultados são imutáveis. Seu
[closeout](../study3/STUDY3_CLOSEOUT.md) registra sinal temporal interno
positivo, controle de cobertura temporal perfeito e acquisition-only no
nível de chance. Esse diagnóstico motiva controlar cobertura; não justifica
buscar score maior, provar causalidade ou atribuir às CNNs um mecanismo.

## Pergunta e desenho conceitual

> After temporal-coverage neutralization by matched positive-background
> observations at identical frame indices, do visual temporal representations
> retain internal discrimination beyond a single representative observation?

A [pergunta científica](STUDY4_SCIENTIFIC_QUESTION.md) delimita a interpretação.
A unidade primária é MATCHED_POSITIVE_BACKGROUND_PAIR. Cada par futuro deve
conter grupos da mesma aquisição e receber exatamente os mesmos oito frames
reais selecionados de sua interseção válida. O controle primário é
COVERAGE_METADATA_LOGREG; o contraste visual primário é CNN1D_MINUS_D1.

A [especificação](STUDY4_DESIGN_SPECIFICATION.md) e os contratos de
[viabilidade](../../configs/study4/feasibility-contract.json),
[matching](../../configs/study4/matching-contract.json) e
[avaliação](../../configs/study4/evaluation-contract.json) são conceituais.
Reutilização futura significa preservar arquiteturas, hiperparâmetros e LBP
congelados de Study3, adaptando a governança de suporte e pares somente sob
autorização específica posterior. Não reutilizar sua autoridade consumida.

## Resultados legítimos e progressão

1. SUFFICIENT_COMMON_SUPPORT, seguido de neutralização de cobertura aceita
   por critério operacional previamente congelado, poderá permitir benchmark
   visual futuro mediante autorização explícita.
2. INSUFFICIENT_COVERAGE_OVERLAP encerra o estudo sem execução de modelos.
3. COVERAGE_NEUTRALIZATION_FAIL encerra a etapa sem executar modelos visuais.

Não forçar progressão até CNN. Sucesso operacional não exige delta positivo.
O [plano de gates](STUDY4_GATE_PLAN.md) exige uma decisão por gate e nenhuma
continuação automática. O threshold de neutralização permanece não definido:
deve ser deliberado e congelado antes de qualquer execução científica futura,
sem escolha posterior à observação de scores.

## Fronteiras atuais e custódia

Nesta fase são proibidos leitura de rows/metadados experimentais do corpus,
overlap real, pares reais, payloads .bin, pixels, LBP, CNN, RF, LogReg, fits,
métricas, receipts científicos, DEV, TEST, SILVER, MP4 e FFmpeg. Não criar
labels, backgrounds ou modelos; não modificar Study3 nem o HANDOFF.
As leituras de S4-0 limitam-se a documentos, contratos e código versionados
necessários. Números herdados não demonstram viabilidade de Study4.

Repository is source of truth. Prompt does not redefine scientific
implementation. Este protocolo especifica um estudo futuro; não altera a
semântica nem o código histórico de Study3. Divergências, dados ausentes,
paths desconhecidos ou autoridade ambígua exigem STOP_AND_REPORT,
DO_NOT_REPAIR_AUTOMATICALLY e DO_NOT_RETRY.

O [escopo de claims](STUDY4_CLAIM_SCOPE.md) e o
[registro de riscos](STUDY4_RISK_REGISTER.md) são obrigatórios.
S4-0 cria apenas seis documentos e quatro contratos JSON Study4. Validar
sintaxe, referências, whitespace e inventário; confirmar zero alterações
históricas, payloads e fits; mostrar os dez paths staged. Somente após esses
checks, criar um commit documental e publicar a nova branch normalmente.
Não fazer amend, force, rebase, PR ou iniciar S4-A.

Após push bem-sucedido: STUDY4_S4_0=PASS e
NEXT_AUTHORIZED_ACTIVITY=NONE_AWAITING_S4_A_AUTHOR_DECISION. STOP.
