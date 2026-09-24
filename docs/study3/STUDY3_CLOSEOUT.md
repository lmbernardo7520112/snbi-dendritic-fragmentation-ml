# Study3 — closeout da representação temporal convolucional

Study3 encerra a comparação interna exploratória de representações de
trajetórias dos grupos TRAIN históricos. A execução científica Recovery 1
terminou em PASS, CLOSED_CONSUMED, com 28 fits e sem retry. A auditoria
pós-run R4A confirmou integridade do método e dos artefatos. Este closeout,
autorizado por `/STUDY3-R5-CLOSEOUT-EVIDENCE-CHECKPOINT`, registra os resultados
existentes e sua interpretação delimitada; nenhum novo cálculo científico,
acesso a payload ou fit foi realizado para produzi-lo.

```text
STUDY3=PASS
STATE=CLOSED_CONSUMED
RECOVERY_ID=STUDY3_EXECUTION_RECOVERY_1
TEMPORAL_REPRESENTATION_SIGNAL=DESCRIPTIVE_INTERNAL_POSITIVE
TEMPORAL_COVERAGE_CONTROL_PERFECT=true
SCIENTIFIC_METHOD_CHANGED=false
RETRY_AUTHORIZED=false
CURRENT_AUTHORIZED_ACTIVITY=NONE_AWAITING_AUTHOR_DECISION
```

O estado acima encerra a autoridade científica. A autorização R5 permite
somente a publicação documental deste checkpoint, sua CI e um Draft PR
condicionado à ancestry; não autoriza novo experimento, Ready ou merge.
PASS é o resultado procedural do controlador, independente de melhoria de
score, e não comprovação de um mecanismo físico.

## Proveniência e integridade

- Freeze científico original: `a3f45b645e9fb3e813a43220351c951698293963`.
- Checkpoint da tentativa original bloqueada antes do payload:
  `8026b821ab113f61d759a2b265ddb567e796c408`.
- Freeze operacional Recovery 1:
  `52de1c8f1e2eaf10e82cc0868d65533b973379f9`.
- Receipt Recovery 1, SHA-256:
  `55b84bef07c8b5c4ad24dab06becec41f9d4ae1f284916104a8775718b3244c1`.
- Invocação única Recovery 1: início `2026-09-24T18:29:36Z`, fim
  `2026-09-24T18:30:10Z`, exit 0. O receipt consumiu sua autoridade.

A tentativa original permanece preservada e consumida, sem leitura científica
de payload, extração ou fit. Recovery 1 teve autoridade separada e não apaga
essa tentativa. O [incidente pré-ciência](STUDY3_PRE_SCIENCE_INCIDENT.md)
também permanece explícito: houve TEXTUAL_TRAIN_METADATA_EXPOSURE_ONLY;
o desenho precedeu essa exposição e não foi adaptado a ela.

Após o run, uma auditoria auxiliar foi interrompida por um filtro de paths
adicionado durante a própria auditoria (`NONDOCUMENTARY_METHOD_PATH`). Isso
não foi uma falha do runner, cujo terminal permaneceu PASS. A nova decisão
R4A resolveu a pendência usando Git e o manifesto existente: tracked tree
sem alterações, diff contra o freeze vazio, os 13 arquivos científicos
byte-idênticos entre os dois freezes e 15/15 checksums válidos cobrindo os
outros 15 arquivos do namespace de 16 artefatos. Nenhum resultado foi reparado.

O HANDOFF permaneceu inalterado, SHA-256
`71bb1bf8f346f445c87561de86329d994354412354b879959f72cb4255bef445`.
Os SHAs de publicação, a CI do checkpoint e a URL do PR serão informados no
relatório terminal e no PR após sua efetiva realização.

## População e resultados registrados

Foram usados exclusivamente 10.907 rows do TRAIN histórico de Study2-C:
3.858 GOLD e 7.049 BACKGROUND, em 64 grupos (32 positivos e 32 background),
duas aquisições e quatro folds históricos. A unidade é GROUP_TRAJECTORY,
com uma predição por grupo e GMBA como métrica primária. GOLD continua sendo
weak label, sem ground truth físico independente.

Os valores por fold abaixo são transcritos de
[results.json](../../artifacts/evidence/STUDY3_EXECUTION_RECOVERY_1/results.json).
As médias explicitamente apresentadas são as fornecidas pelo autor em R5;
o controlador não persistiu médias GMBA por condição. Nenhuma média adicional
foi calculada para este closeout; o travessão indica média não transcrita.

| Representação/controle | Fold 0 | Fold 1 | Fold 2 | Fold 3 | Média fornecida em R5 |
| --- | ---: | ---: | ---: | ---: | ---: |
| D1_LBP20 | 0.75 | 0.8125 | 0.8125 | 0.875 | — |
| TRAJECTORY_MEAN_LBP20 | 0.875 | 0.875 | 1.0 | 1.0 | 0.9375 |
| TRAJECTORY_MEDIAN_LBP20 | 0.75 | 0.875 | 0.8125 | 1.0 | — |
| TRAJECTORY_Q2575_LBP60 | 0.8125 | 0.875 | 0.9375 | 0.9375 | — |
| TEMPORAL_CNN1D_LBP20 | 0.9375 | 1.0 | 1.0 | 1.0 | 0.984375 |
| SPATIOTEMPORAL_CNN_SMALL | 0.9375 | 1.0 | 1.0 | 0.9375 | 0.96875 |
| COVERAGE_METADATA_LOGREG | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| ACQUISITION_ONLY | 0.5 | 0.5 | 0.5 | 0.5 | 0.5 |

A CNN1D tem 5.122 parâmetros; a CNN espaço-temporal tem 2.138 parâmetros,
conforme os registros dos fits. O controle acquisition-only não realiza fit.

Os sete contrastes abaixo são os já emitidos pelo controlador; não houve
novo contraste, p-value ou threshold. Os descritores são transcritos segundo
a regra congelada, sem reinterpretar seu nome como significância estatística
ou positividade em todos os folds.

| Contraste | mean_delta | Folds positivos/zero/negativos | Descritor |
| --- | ---: | --- | --- |
| MEDIAN_MINUS_D1 | +0.046875 | 2/2/0 | MIXED_POSITIVE_INTERNAL |
| CNN1D_MINUS_D1 | +0.171875 | 4/0/0 | CONSISTENT_POSITIVE_INTERNAL |
| SPATIOTEMPORAL_MINUS_D1 | +0.15625 | 4/0/0 | CONSISTENT_POSITIVE_INTERNAL |
| SPATIOTEMPORAL_MINUS_MEDIAN | +0.109375 | 3/0/1 | CONSISTENT_POSITIVE_INTERNAL |
| SPATIOTEMPORAL_MINUS_CNN1D | -0.015625 | 0/3/1 | NON_POSITIVE_INTERNAL |
| MEAN_MINUS_D1 | +0.125 | 4/0/0 | CONSISTENT_POSITIVE_INTERNAL |
| Q2575_MINUS_D1 | +0.078125 | 4/0/0 | CONSISTENT_POSITIVE_INTERNAL |

## Interpretação científica delimitada

Todas as representações temporais relevantes avaliadas superaram D1 em
média, conforme os deltas médios positivos registrados. CNN1D > D1 e CNN
espaço-temporal > D1 consistentemente nos quatro folds. A CNN espaço-temporal
não superou CNN1D: houve três empates e um fold negativo, com delta médio
-0.015625 e descritor NON_POSITIVE_INTERNAL. TRAJECTORY_MEAN apresentou
ganho interno de +0.125 sobre D1. Esses resultados não estabelecem
superioridade universal de CNN sobre Random Forest nem aprendizado de física.

> As representações temporais apresentaram forte discriminação interna das
> weak labels. Entretanto, um controle composto apenas por características de
> cobertura temporal classificou perfeitamente os grupos, mostrando que a
> estrutura temporal/metodológica do corpus contém informação suficiente para
> discriminar as classes. Assim, o ganho das representações visuais não pode ser
> atribuído isoladamente à dinâmica microestrutural.

O controle de cobertura usa `log1p(n_rows)`, primeiro frame normalizado,
último frame normalizado e span normalizado, com StandardScaler e
LogisticRegression ajustados somente no treino de cada fold. Seu GMBA 1.0
nos quatro folds indica forte risco de shortcut/confundimento ligado à
cobertura temporal dos grupos e à construção das weak labels. Esse diagnóstico
não comprova causalmente o confound nem demonstra que as CNNs necessariamente
usaram esse mecanismo. O acquisition-only em 0.5 não elimina o risco de
shortcut de cobertura ou de construção do target. O ganho visual não pode ser
atribuído isoladamente à dinâmica visual ou microestrutural.

## Relação com Study2-D

Em Study2-D, adicionar mais rows correlacionadas a um RF fixo não mostrou
benefício. Em Study3, representar explicitamente a trajetória mostrou ganho
interno sobre D1. Os resultados são compatíveis:

```text
MORE_ROWS != TRAJECTORY_REPRESENTATION
```

Além da diferença de pergunta, Study2-D validava todas as rows dos grupos
retidos, enquanto Study3 produz uma predição por grupo. Seus valores D1 não
devem ser tratados como estimativas diretamente idênticas nem seus deltas
combinados como decomposição causal. O resultado histórico de Study2-D é
preservado. Study3 não substitui o pipeline final de Study2-C.

## Limitações e trabalho futuro

O alcance permanece interno e exploratório: duas aquisições, historical TRAIN
only, weak labels, nenhum fresh DEV, nenhum fresh TEST e ausência de external
validation. Os folds não equivalem a novas aquisições independentes. O metadata
coverage perfect control e o possível target-construction/coverage shortcut
limitam a atribuição dos ganhos. Não há ground truth físico independente,
evidência causal, identificação de onset ou forecasting. O estudo não sustenta
que deep learning resolveu a fragmentação.

Um novo estudo deverá controlar explicitamente a cobertura temporal. São
somente propostas: matching de grupos por n_rows/span, janelas temporais
comuns, equalização de cobertura, representações com suporte temporal
comparável e novas aquisições independentes.

```text
FUTURE_COVERAGE_CONTROL_STUDY=NOT_CURRENT_WORK
NEW_SCIENTIFIC_EXECUTION_AUTHORIZED=false
```

## Contadores e custódia das evidências

O [terminal](../../artifacts/evidence/STUDY3_EXECUTION_RECOVERY_1/terminal-state.json),
o [ledger](../../artifacts/evidence/STUDY3_EXECUTION_RECOVERY_1/FIT_LEDGER.json) e a
[verificação](../../artifacts/evidence/STUDY3_EXECUTION_RECOVERY_1/verification.json)
registram uma execução científica Recovery 1, 10.907 rows lidas e autenticadas,
92.164.150 bytes científicos lidos e 10.907 rows LBP. Houve uma extração em
lote iniciada e concluída. Os 28 fits foram iniciados e concluídos:
16 RF, quatro CNN1D, quatro CNN espaço-temporal e quatro metadata LogReg.
DEV rows, TEST rows, TEST-cache rows, MP4 opens e FFmpeg runs foram todos zero.
Esses são contadores da execução encerrada; este closeout adicionou zero fits.

O [manifesto existente](../../artifacts/evidence/STUDY3_EXECUTION_RECOVERY_1/post-run-hashes.sha256)
foi validado sem reescrita: 15/15 entradas PASS. Os 16 artefatos preservados
em `artifacts/evidence/STUDY3_EXECUTION_RECOVERY_1/` são:

```text
CLASSICAL_TRAJECTORY_RESULTS.json
FIT_LEDGER.json
GROUP_LEDGER.json
METADATA_CONTROL_RESULTS.json
REPRESENTATION_MANIFEST.json
SPATIOTEMPORAL_CNN_RESULTS.json
TEMPORAL_CNN1D_RESULTS.json
TEMPORAL_SELECTION_LEDGER.json
commands.json
environment.json
execution-report.md
post-run-hashes.sha256
results.json
scientific-execution-receipt.json
terminal-state.json
verification.json
```

O checkpoint documental contém somente esses 16 artefatos existentes e este
closeout. Código, configs, testes, workflows, resultados, método e HANDOFF
permanecem preservados. Nenhum payload científico integra este checkpoint.
