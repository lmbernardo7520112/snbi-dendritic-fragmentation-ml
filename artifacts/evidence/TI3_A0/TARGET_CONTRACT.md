# TI3-A0 — deliberação sobre o target

**TARGET_CONTRACT=BLOCKED. TI3_A0_TARGET_CONTRACT=BLOCKED.**
Uma única candidata principal foi considerada: localização pontual
supervisionada pelas posições de eventos publicadas. Ela não foi congelada
como tarefa ML validada. Não houve mudança para classificação apenas para
contornar as limitações encontradas.

| Elemento exigido | Definição candidata / evidência | Estado |
| --- | --- | --- |
| WHAT_IS_ONE_SAMPLE | Um frame estrutural de uma aquisição e instante, com conjunto de localizações anotadas correspondente; não cada modalidade como amostra independente | PROPOSED_NOT_FROZEN |
| INPUT | ESM1/ESM4 radiografia; canal solutal relativo ESM2/ESM5 apenas em comparação futura autorizada; ESM3/ESM6 nunca como input contendo o target desenhado | PROPOSED_NOT_EXECUTED |
| TARGET | Localizações pontuais publicadas, com identidade da anotação e incerteza espacial explícitas; não máscara, tamanho ou onset físico | BLOCKED |
| LABEL_SOURCE | ESM3/ESM6, anotações cumulativas de localização | DOCUMENTED |
| POSITIVE_RULE | Requer marca validada semanticamente e associação espacial rastreável; círculo geometricamente aceito sozinho continua candidato gráfico | NOT_VERIFIED_FOR_ML |
| NEGATIVE_RULE | Ausência de anotação = UNLABELED/UNKNOWN; não criar negativos por complemento do mapa | FROZEN_PROHIBITION |
| AMBIGUITY_RULE | Preservar marca sobreposta/cortada/confundida e associação incerta como UNKNOWN; não inventar centro aceito ou evento | EXPLICIT |
| SPATIAL_TOLERANCE | Dois pixels foram usados apenas no diagnóstico de matching gráfico; tolerância do target/evento não é certificada por isso | NOT_VERIFIED |
| TEMPORAL_REFERENCE | Tempo experimental normativo do frame; primeira observação amostrada separada de EVENT_ONSET_FRAME | DOCUMENTED_WITH_ONSET_UNKNOWN |
| PERSISTENCE_RULE | Matching recíproco único do protótipo, sem resgate de ambiguidades; prova global não obtida em nenhuma origem | BLOCKED |

## Razões para não congelar

1. O extrator preserva ambiguidades e não recupera de modo certificado todas
   as marcas. Seu critério radial também recusa anéis isolados, limitação
   explicitamente preservada após a única execução.
2. Centro do traço é um descritor gráfico. A relação entre esse centro,
   localização física do evento e tolerância de avaliação não foi validada
   por uma referência independente.
3. Completude e negativos confiáveis não foram comprovados no material
   documental acessível. UNKNOWN é uma decisão válida de semântica, mas
   ainda falta um objetivo e protocolo quantitativo de supervisão/avaliação
   compatíveis com essa incompletude. Não se afirma que toda abordagem
   positive-unlabeled seja impossível; nenhuma foi inventada nesta etapa.
4. A identidade/persistência global e as dependências de exposição do teste
   futuro permanecem sem certificação. Repetições de uma marca não podem
   virar novos eventos ou réplicas independentes.

A localização pontual continua a candidata coerente com a publicação, mas
a hipótese não foi promovida a verdade por autorização. Classificação de
patches ou de frames exigiria negativos ou semântica de NEW_EVENT não
comprovados. Segmentar o interior dos círculos permanece proibido.
Não há baseline, loss, dataset ML, métricas de ML ou treinamento.

## Contrato temporal que não foi ativado

NEW_EVENTS(t) = ANNOTATIONS(t) menos anotações persistentes anteriores é
somente uma definição conceitual. O protótipo não certificou os conjuntos
de eventos individuais necessários. Frame inicial do bloco, marca previamente
ocluída, identidade ambígua e censura temporal precisam de regras antes de
produzir esse target. Sem círculo não se transforma em “nenhum evento”.

Nenhum novo frame foi acessado: onset não é o único requisito pendente.
O contrato encerra bloqueado, sem A0.1 ou nova rodada de calibração.

```text
TI3_A0=BLOCKED_TARGET_CONTRACT
CIRCLE_IS_FRAGMENT_MASK=false
TARGET_CONTRACT=BLOCKED
FINAL_TEST=NOT_DEFINED_NOT_OPENED
ML_RUNS=0
TI3_A_READY_TO_RESUME=false
TI3_B_AUTHORIZED=false
MERGE_AUTHORIZED=false
CURRENT_AUTHORIZED_ACTIVITY=NONE_AWAITING_AUTHOR_DECISION
```
