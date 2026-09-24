# Study4 — pergunta científica

## Pergunta primária

"After temporal-coverage neutralization by matched positive-background
observations at identical frame indices, do visual temporal representations
retain internal discrimination beyond a single representative observation?"

"Após neutralizar a cobertura temporal por pareamento de positivos e
backgrounds observados nos mesmos frames, as representações visuais temporais
ainda apresentam discriminação interna superior a uma única observação?"

## Motivação e contraste

O [closeout de Study3](../study3/STUDY3_CLOSEOUT.md) registra simultaneamente:

```text
TEMPORAL_REPRESENTATION_SIGNAL=DESCRIPTIVE_INTERNAL_POSITIVE
COVERAGE_METADATA_LOGREG=PERFECT_INTERNAL_DISCRIMINATION
ACQUISITION_ONLY=CHANCE_LEVEL
```

A cobertura temporal contém informação discriminativa interna suficiente,
mas não está causalmente demonstrado que as CNNs a utilizaram. Study4 testa
persistência de sinal sob controle explícito dessa cobertura. Não procura
maximizar scores nem revisar resultados de Study3.

PRIMARY_UNIT=MATCHED_POSITIVE_BACKGROUND_PAIR; T=8.
PRIMARY_CONTROL=COVERAGE_METADATA_LOGREG.
PRIMARY_VISUAL_CONTRAST=CNN1D_MINUS_D1.
Pareamento: mesma aquisição e frames selecionados idênticos.

A elegibilidade real é desconhecida em S4-0. Pouco suporte comum e falha da
neutralização são resultados legítimos que impedem benchmark visual.
Um resultado visual não positivo, se futuramente autorizado e obtido após
os gates, também deve ser preservado sem retuning, retry ou novo modelo.

Mesmo com neutralização aceita, o estimando é discriminação interna de weak
labels em suporte comum selecionado, não efeito causal da dinâmica
microestrutural. A aplicabilidade permanece limitada aos pares elegíveis,
sem inferência de generalização para grupos excluídos ou novas aquisições.

Ver [protocolo](STUDY4_MASTER_PROTOCOL.md),
[desenho](STUDY4_DESIGN_SPECIFICATION.md) e
[claims](STUDY4_CLAIM_SCOPE.md).
