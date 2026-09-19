# TI3_TARGET_RESOLUTION
# Weakly-Supervised Fragmentation-Location Target
# Resolução terminal do contrato de target antes da retomada de TI3-A
# SEM tuning do extrator
# SEM treinamento ML
# SEM abertura de FINAL_TEST
# DDD + SDD + evidence-first + fail-closed + bounded experimentation
# + convergence governance + scientific claim control

Repositório:
snbi-dendritic-fragmentation-ml

Baseline canônica:
67786bd4e23406e7f19860a53fe237e6d7b648cb

Branch atual:
feat/ti3-canonical-dataset-baseline

============================================================
0. PRINCÍPIO DESTA AUTORIZAÇÃO
============================================================

Esta tarefa NÃO é uma etapa de treinamento de modelo.

Esta tarefa resolve exclusivamente:

“Os rótulos de alta confiança já produzidos a partir das
anotações publicadas de fragmentação são suficientes para
definir um target supervisionado limitado, reproduzível,
anti-leakage e cientificamente honesto?”

O resultado deve ser finito.

Há somente duas saídas legítimas:

PASS
→ contrato de target congelado;
→ TI3-A pode ser retomado.

BLOCKED
→ caminho supervisionado de fragmentação fecha com os
  rótulos atualmente disponíveis;
→ qualquer continuação exigirá pivot metodológico;
→ NÃO haverá nova tentativa de extractor nesta linha.

Esta autorização NÃO permite:

- treinar LBP + Random Forest;
- treinar CNN;
- selecionar arquitetura;
- acessar FINAL_TEST;
- melhorar o detector de círculos;
- fazer tuning de Hough;
- modificar thresholds;
- ajustar raio depois de olhar resultados;
- recalibrar G2;
- reabrir G2_SOLUTE;
- redefinir círculos como máscaras;
- inferir causalidade;
- chamar detecção contemporânea de previsão futura.

============================================================
1. ESTADO CANÔNICO
============================================================

Estados científicos já encerrados:

G2_FRAG=PASS_DIRECT_RASTER_MAPPING
G2_SOLUTE=PASS

TI2R_SOLUTE=COMPLETE
SOLUTAL_INTERNAL_VALIDATION=PASS
SOLUTAL_EXTERNAL_GENERALIZATION=NOT_CLAIMED

Holdout solutal:
CONSUMED

G2_SOLUTE está CLOSED.

NÃO reabrir.

Estado de TI3:

TI3_A=BLOCKED_METHOD_PRECONDITIONS

TI3_A0=BLOCKED_TARGET_CONTRACT

FINAL_TEST=NOT_DEFINED_NOT_OPENED

ML_RUNS=0

MODEL_SELECTION=NOT_STARTED

TI3_B_AUTHORIZED=false

============================================================
2. EVIDÊNCIA PRODUZIDA POR TI3-A0
============================================================

TI3-A0 examinou SOMENTE os seguintes frames previamente expostos:

ESM3:
0 / 73 / 146 / 219 / 293

ESM6:
0 / 98 / 197 / 295 / 394

Não foram abertos novos frames.

O extrator congelado identificou:

- 108 círculos geometricamente aceitos;
- 380 componentes ambíguos;
- 3 componentes pequenos;
- anéis vermelhos;
- raio gráfico aproximadamente 10.61–10.85 px;
- imagem radiográfica visível no interior dos anéis.

O método utilizado foi baseado em:

- threshold de chroma;
- componentes conexos;
- ajuste geométrico de círculo.

A decisão de extração foi congelada antes do uso científico.

Não alterar agora:

- threshold;
- limites geométricos;
- raio;
- critérios de aceitação;
- critérios de rejeição.

TI3-A0 não demonstrou:

- máscara física de fragmento;
- extensão física do fragmento;
- onset físico exato;
- inventário exaustivo de todos os eventos;
- negativos físicos confiáveis;
- generalização externa.

============================================================
3. SEMÂNTICA DOCUMENTAL DOS CÍRCULOS
============================================================

A publicação primária de Gibbs et al.:

"In Situ X-Ray Observations of Dendritic Fragmentation
During Directional Solidification of a Sn-Bi Alloy"

documenta que as LOCALIZAÇÕES DOS EVENTOS CUMULATIVOS
DE FRAGMENTAÇÃO são circundadas.

Portanto, a interpretação autorizada é:

CIRCLE
    ↓
PUBLISHED EVENT LOCATION

Não interpretar:

CIRCLE
    ↓
PHYSICAL FRAGMENT MASK

Não interpretar:

CIRCLE
    ↓
PHYSICAL FRAGMENT EXTENT

Não interpretar:

FIRST OBSERVED CIRCLE
    ↓
EXACT FRAGMENTATION ONSET

O círculo é uma marcação gráfica de LOCALIZAÇÃO publicada.

O raio do círculo descreve o marcador gráfico,
NÃO a dimensão física do fragmento.

============================================================
4. MUDANÇA CONCEITUAL CENTRAL
============================================================

Não exigir que o sistema recupere todas as marcações.

O objetivo NÃO é:

“obter ground truth perfeito e exaustivo.”

O objetivo é:

“obter weak labels de alta confiança,
mantendo como IGNORE tudo que não é suficientemente seguro.”

Adotar:

WEAK_LABEL_STRATEGY=
HIGH_CONFIDENCE_PLUS_IGNORE

Isso significa:

- exemplos de alta confiança podem ser usados;
- casos ambíguos não viram negativos;
- ausência de anotação não vira automaticamente ausência física;
- nenhuma tentativa adicional será feita para forçar cobertura completa.

============================================================
5. CHECKPOINT DO ESTADO TI3-A0
============================================================

Existem arquivos locais produzidos por TI3-A0.

Antes de qualquer nova análise:

1. validar hashes;
2. validar conteúdo;
3. confirmar worktree esperado;
4. confirmar que correspondem ao estado reportado;
5. criar UM checkpoint preservando integralmente o bloqueio anterior.

Mensagem sugerida:

docs(ti3): preserve blocked annotation target audit

Depois do checkpoint:

NÃO reescrever retroativamente os artefatos TI3-A0.

Novas evidências devem ser produzidas em:

artifacts/evidence/TI3_TARGET_RESOLUTION/

============================================================
6. DEFINIÇÃO DO LABEL POSITIVO
============================================================

Definir a classe positiva exclusivamente como:

PUBLISHED_FRAGMENTATION_LOCATION

Definição:

posição central de um círculo geometricamente aceito
pelo extrator congelado de ESM3/ESM6,

cuja semântica documental é:

“localização publicada de evento cumulativo
de fragmentação.”

Não chamar o positivo de:

- physical fragment;
- fragment mask;
- exact onset;
- complete fragmentation event;
- ground truth exhaustivo.

============================================================
7. TRÊS ESTADOS DE SUPERVISÃO
============================================================

Definir exatamente três estados.

------------------------------------------------------------
7.1 POSITIVE
------------------------------------------------------------

POSITIVE =

centro de círculo de alta confiança aceito
pelo extrator congelado.

Sem tuning adicional.

------------------------------------------------------------
7.2 IGNORE
------------------------------------------------------------

IGNORE =

qualquer região associada a:

- componente ambíguo;
- componente rejeitado;
- círculo parcialmente identificado;
- componente sobreposto;
- componente cortado por borda;
- componente geometricamente não certificável;
- componente pequeno rejeitado;
- região em que o estado de anotação não possa ser determinado.

IGNORE nunca pode ser convertido em NEGATIVE.

------------------------------------------------------------
7.3 BACKGROUND_CANDIDATE
------------------------------------------------------------

BACKGROUND_CANDIDATE =

região suficientemente distante de:

- POSITIVE;
- IGNORE;

e sem localização publicada detectada pelo ground truth utilizável.

IMPORTANTE:

BACKGROUND_CANDIDATE significa:

“não contém localização publicada utilizável
de fragmentação nesta região.”

Não significa:

“não houve fragmentação física aqui.”

Não significa:

“fragmentação é impossível nesta região.”

============================================================
8. NÃO ACESSAR NOVOS PIXELS
============================================================

Nesta tarefa:

NÃO abrir novos frames.

NÃO abrir ESM1.

NÃO abrir ESM2.

NÃO abrir ESM4.

NÃO abrir ESM5.

NÃO abrir novos ESM3.

NÃO abrir novos ESM6.

Usar SOMENTE:

- artefatos;
- coordenadas;
- resultados;
- componentes;
- registros;

já materializados por TI3-A0.

Se os artefatos existentes forem insuficientes para esta resolução:

BLOCKED.

Não escalar automaticamente.

============================================================
9. DEDUPLICAÇÃO TEMPORAL
============================================================

As 108 ocorrências aceitas NÃO devem ser tratadas
como 108 eventos independentes.

As anotações são cumulativas.

Um mesmo local pode aparecer repetidamente em vários frames.

Portanto:

agrupar por:

- aquisição/source;
- proximidade espacial.

Usar tolerância de associação congelada:

3 px

Essa tolerância é coerente com o limite máximo de erro de registro
já utilizado/certificado no projeto.

NÃO alterar 3 px depois de observar o número de grupos.

Cada cluster espacial gera:

annotation_site_id

Para cada annotation_site_id registrar:

- source_id;
- aquisição;
- número de observações;
- frames;
- tempos experimentais disponíveis;
- centro representativo;
- dispersão espacial;
- raio gráfico observado;
- FIRST_CONFIDENT_OBSERVATION.

============================================================
10. FIRST_CONFIDENT_OBSERVATION
============================================================

Definir:

FIRST_CONFIDENT_OBSERVATION =

primeiro frame ENTRE OS FRAMES EFETIVAMENTE ANALISADOS
em que o extrator congelado aceitou aquele marcador.

Não chamar:

FRAGMENTATION_ONSET

Não chamar:

EVENT_BIRTH

Não chamar:

PHYSICAL_BREAK_TIME

FIRST_CONFIDENT_OBSERVATION é apenas um atributo
da observação documental disponível.

============================================================
11. UNIDADE AMOSTRAL CANDIDATA
============================================================

Avaliar o seguinte contrato:

WHAT_IS_ONE_SAMPLE =

um candidato espacial derivado de uma imagem em um instante,
posteriormente materializável como patch.

Input futuro principal:

STRUCTURAL_INPUT =
radiografia ESM1 ou ESM4.

Input futuro multimodal opcional:

MULTIMODAL_INPUT =
radiografia ESM1/ESM4
+
campo solutal relativo ESM2/ESM5.

Target:

PUBLISHED_FRAGMENTATION_LOCATION_PRESENT

ESM3/ESM6:

LABEL SOURCE ONLY.

Nunca podem ser input do modelo.

Isso evita target leakage.

============================================================
12. OBJETIVO DO MODELO FUTURO
============================================================

O futuro modelo NÃO será treinado para detectar:

- círculos vermelhos;
- bordas dos círculos;
- overlays;
- cores de anotação.

Os círculos existem SOMENTE para localizar os exemplos supervisionados.

O modelo futuro deverá receber imagem limpa.

Objetivo supervisionado restrito:

aprender padrões visuais associados às localizações
publicadas de fragmentação.

Se o modelo futuramente produzir score elevado
em uma região sem círculo publicado:

isso significa:

“REGIÃO CANDIDATA compatível com o padrão aprendido.”

Não significa automaticamente:

“nova fragmentação física descoberta.”

Uma detecção não anotada precisaria de validação independente
antes de ser considerada evento físico confirmado.

============================================================
13. REGRA SOBRE NEGATIVOS
============================================================

Não assumir automaticamente:

absence of annotation
=
absence of physical fragmentation.

Nesta resolução, definir somente:

NEGATIVE_SEMANTICS =

NO_PUBLISHED_ANNOTATION_IN_VALID_CANDIDATE_REGION

O futuro gerador de exemplos negativos deverá excluir:

- safety area de POSITIVE;
- safety area de IGNORE;
- regiões ambíguas;
- bordas inválidas;
- qualquer região que possa carregar a própria anotação.

Não materializar ainda patches negativos.

============================================================
14. FEASIBILITY DO DATASET
============================================================

Calcular usando apenas os artefatos A0:

- número bruto de círculos aceitos;
- annotation_site_ids únicos;
- distribuição por ESM3;
- distribuição por ESM6;
- distribuição temporal;
- número de observações por site;
- número de sites com uma observação;
- número de sites repetidos;
- FIRST_CONFIDENT_OBSERVATION por site;
- quantidade e distribuição de regiões IGNORE.

Não tratar repetição temporal como aumento do N independente.

============================================================
15. GATE DE SUFICIÊNCIA
============================================================

Pergunta única:

“Existem annotation_site_ids únicos suficientes
para permitir posteriormente TRAIN, DEVELOPMENT e FINAL_TEST
internos, todos não vazios, sem dividir o mesmo site entre partições?”

O gate NÃO depende de:

- accuracy;
- F1;
- AUC;
- desempenho de CNN;
- desempenho de RF;
- performance futura.

É exclusivamente gate de viabilidade estrutural do dataset.

Se NÃO houver sites suficientes:

TI3_TARGET_RESOLUTION=
BLOCKED_INSUFFICIENT_HIGH_CONFIDENCE_LABELS

STOP.

Não melhorar o extractor.

============================================================
16. SPLIT FUTURO POR annotation_site_id
============================================================

Se houver sites suficientes:

definir contrato futuro:

cada annotation_site_id pertence integralmente
a exatamente UM split.

Nenhuma ocorrência temporal daquele site
pode aparecer em outro split.

Portanto:

TRAIN ∩ DEV = ∅ por annotation_site_id

TRAIN ∩ FINAL_TEST = ∅ por annotation_site_id

DEV ∩ FINAL_TEST = ∅ por annotation_site_id

Estratificar por aquisição quando matematicamente possível.

A estratégia deve ser:

- determinística;
- independente de desempenho;
- pré-especificada;
- auditável.

Não materializar FINAL_TEST agora.

============================================================
17. LIMITAÇÃO DE GENERALIZAÇÃO
============================================================

Existem somente duas aquisições/condições documentadas.

Portanto:

EXTERNAL_GENERALIZATION_CLAIM=false

O futuro resultado poderá sustentar apenas algo como:

“validação interna agrupada nas aquisições disponíveis.”

Não sustenta:

“generalização para novos experimentos independentes.”

============================================================
18. RELAÇÃO COM O CAMPO SOLUTAL
============================================================

G2_SOLUTE já está concluído.

NÃO reabrir.

O papel futuro do campo solutal será testar
uma hipótese incremental.

Modelo A:

STRUCTURAL_ONLY

radiografia
    ↓
modelo
    ↓
fragmentation-location score

Modelo B:

STRUCTURAL_PLUS_RELATIVE_SOLUTE

radiografia
+
campo solutal relativo
    ↓
modelo
    ↓
fragmentation-location score

Pergunta futura legítima:

“O campo solutal relativo acrescenta informação
discriminativa/preditiva para identificar localizações
publicadas de fragmentação?”

Não executar essa comparação nesta tarefa.

============================================================
19. SEMÂNTICA CORRETA DE ESM2 / ESM5
============================================================

Descrever ESM2/ESM5 exclusivamente como:

RELATIVE_SOLUTE_FIELD

ou:

campo solutal relativo/normalizado.

Não chamar ESM2/ESM5 de:

- concentração absoluta de Bi;
- mapa absoluto de concentração;
- temperatura;
- campo térmico;
- medição direta de precursor causal.

============================================================
20. CLAIM GUARD
# DETECTION ≠ FORECASTING ≠ CAUSALITY
============================================================

Este bloco é NORMATIVO.

O target:

PUBLISHED_FRAGMENTATION_LOCATION_PRESENT

é um target de:

DETECÇÃO / ASSOCIAÇÃO SUPERVISIONADA.

Ele NÃO é um target de:

FORECASTING.

Ele NÃO é um target causal.

------------------------------------------------------------
20.1 DETECTION
------------------------------------------------------------

Exemplo autorizado:

radiografia(t)
        ↓
modelo
        ↓
score de localização associada
a fragmentação publicada em t/contexto compatível.

------------------------------------------------------------
20.2 MULTIMODAL ASSOCIATION
------------------------------------------------------------

Exemplo futuro autorizado:

radiografia(t)
+
campo solutal relativo(t)
        ↓
modelo
        ↓
score de localização associada
a fragmentação publicada.

Isso poderá testar:

INCREMENTAL INFORMATION

ou:

PREDICTIVE/DISCRIMINATIVE ASSOCIATION.

Não causalidade.

------------------------------------------------------------
20.3 FORECASTING
------------------------------------------------------------

Previsão futura exigiria novo contrato.

Exemplo:

radiografia(t)
+
campo solutal relativo(t)
        ↓
modelo
        ↓
evento em t + Δt

Isso NÃO está autorizado atualmente.

Forecasting futuro só poderá existir se forem definidos:

- input time t;
- prediction horizon Δt;
- target em t+Δt;
- event/onset semantics;
- embargo temporal;
- context window;
- anti-leakage temporal;
- tratamento de persistência;
- tratamento de eventos já existentes.

Como onset físico exato NÃO está validado atualmente:

não transformar FIRST_CONFIDENT_OBSERVATION
em event onset para criar forecasting artificial.

------------------------------------------------------------
20.4 CAUSALITY
------------------------------------------------------------

O presente desenho é observacional.

Portanto:

ASSOCIATION ≠ CAUSATION

Mesmo que:

STRUCTURAL_PLUS_RELATIVE_SOLUTE

supere:

STRUCTURAL_ONLY,

isso NÃO demonstra que o campo solutal
causa a fragmentação.

A conclusão permitida seria algo como:

“o campo solutal relativo forneceu informação incremental
associada ao target de fragmentação definido.”

Nunca:

“o modelo demonstrou que o soluto causou a fragmentação.”

============================================================
21. ALINHAMENTO CURRICULAR — TRILHA 2
============================================================

Registrar:

------------------------------------------------------------
21.1 Thresholding + componentes conexos
------------------------------------------------------------

Já utilizados legitimamente para:

extração das weak labels gráficas.

Isso constitui uso real do conteúdo de pré-processamento.

------------------------------------------------------------
21.2 Hough
------------------------------------------------------------

NÃO executar.

Apesar de pertinente a círculos, foi deliberadamente rejeitado nesta etapa.

Motivo:

evitar tuning retrospectivo do label extractor
depois de observar os resultados A0.

------------------------------------------------------------
21.3 LBP + Random Forest
------------------------------------------------------------

Se TARGET_CONTRACT=PASS
e a unidade amostral patch-level for mantida:

LBP + Random Forest torna-se candidato apropriado
a baseline clássico em TI3-A.

Não executar agora.

------------------------------------------------------------
21.4 CNN
------------------------------------------------------------

Se TARGET_CONTRACT=PASS:

CNN torna-se candidato natural a modelo aprendido.

Não executar agora.

------------------------------------------------------------
21.5 Sobel
------------------------------------------------------------

Preservar conexão didática:

Sobel / gx / gy
        ↓
Normalized Gradient Fields
        ↓
NGF usado no registro multimodal.

Não reabrir G2.

------------------------------------------------------------
21.6 Descritores locais
------------------------------------------------------------

Preservar conexão:

descritores/feature engineering
        ↓
local self-similarity
        ↓
SS8 usado no projeto.

Não declarar SS8 como implementação exata de MIND/MIND-SSC.

Formulação adequada:

“local self-similarity descriptor inspired by the
modality-independent self-similarity principle.”

============================================================
22. CONTRATO FINAL SE PASS
============================================================

Se a evidência estrutural for suficiente, congelar:

LABEL_SOURCE=
ESM3_ESM6_PUBLISHED_CIRCLES

TARGET_SEMANTICS=
PUBLISHED_FRAGMENTATION_LOCATION

TARGET=
PUBLISHED_FRAGMENTATION_LOCATION_PRESENT

CIRCLE_IS_FRAGMENT_MASK=false

FRAGMENT_EXTENT_AVAILABLE=false

EXACT_ONSET_REQUIRED=false

EXACT_ONSET_AVAILABLE=false

POSITIVE_RULE=
HIGH_CONFIDENCE_ACCEPTED_CIRCLE_CENTER

AMBIGUOUS_RULE=
IGNORE

NEGATIVE_SEMANTICS=
NO_PUBLISHED_ANNOTATION_IN_VALID_CANDIDATE_REGION

FIRST_OBSERVATION_SEMANTICS=
FIRST_CONFIDENT_OBSERVATION_ONLY

MODEL_CLAIM_SCOPE=
DETECTION_OF_PUBLISHED_FRAGMENTATION_LOCATIONS

SOLUTAL_INPUT_SEMANTICS=
RELATIVE_SOLUTE_FIELD

FORECASTING_AUTHORIZED=false

CAUSALITY_CLAIM_AUTHORIZED=false

EXTERNAL_GENERALIZATION_CLAIM=false

============================================================
23. ARTEFATOS OBRIGATÓRIOS
============================================================

Criar:

artifacts/evidence/TI3_TARGET_RESOLUTION/

TARGET_CONTRACT.md

WEAK_LABEL_LEDGER.json

SITE_DEDUPLICATION.json

DATASET_FEASIBILITY.md

SPLIT_CONTRACT.md

COURSE_ALIGNMENT.md

CLAIM_SCOPE.md

results.json

commands.json

verification.json

Nenhum arquivo de modelo.

Nenhum checkpoint ML.

Nenhum tensor de treinamento.

Nenhum FINAL_TEST materializado.

============================================================
24. CONTEÚDO MÍNIMO — TARGET_CONTRACT.md
============================================================

Incluir:

1. source of labels;
2. scientific meaning;
3. what a circle means;
4. what a circle does not mean;
5. positive rule;
6. ignore rule;
7. background semantics;
8. one-sample definition;
9. input modalities;
10. forbidden inputs;
11. temporal semantics;
12. FIRST_CONFIDENT_OBSERVATION definition;
13. claim scope;
14. limitations.

============================================================
25. CONTEÚDO MÍNIMO — SITE_DEDUPLICATION.json
============================================================

Para cada annotation_site_id:

- annotation_site_id;
- source_id;
- acquisition_id;
- observations;
- frame_indices;
- experimental_times;
- representative_x;
- representative_y;
- spatial_dispersion_px;
- first_confident_observation;
- number_of_observations;
- status.

============================================================
26. CONTEÚDO MÍNIMO — DATASET_FEASIBILITY.md
============================================================

Registrar:

- 108 accepted detections;
- número real de annotation_site_ids únicos;
- distribuição por aquisição;
- distribuição temporal;
- repetição;
- quantidade de IGNORE;
- viabilidade ou não de três partições internas;
- limitações estatísticas;
- impossibilidade de alegar independência experimental externa.

============================================================
27. CONTEÚDO MÍNIMO — CLAIM_SCOPE.md
============================================================

Separar explicitamente:

CURRENTLY SUPPORTED:

- published-location detection;
- weak supervision;
- internal grouped validation;
- future structural vs multimodal comparison.

NOT CURRENTLY SUPPORTED:

- physical fragment segmentation;
- exhaustive fragmentation inventory;
- exact event onset;
- future-event forecasting;
- absolute Bi concentration;
- temperature inference from ESM2/ESM5;
- causal claims;
- external experimental generalization.

============================================================
28. REGRA DE CONVERGÊNCIA
============================================================

Esta autorização termina em exatamente UM de dois estados.

------------------------------------------------------------
28.1 PASS
------------------------------------------------------------

TI3_TARGET_RESOLUTION=PASS

TARGET_CONTRACT=FROZEN

WEAK_LABEL_STRATEGY=
HIGH_CONFIDENCE_PLUS_IGNORE

PUBLISHED_FRAGMENTATION_LOCATION_TARGET=VALID_FOR_INTERNAL_ML

TI3_A_READY_TO_RESUME=true

FINAL_TEST=NOT_DEFINED_NOT_OPENED

ML_RUNS=0

MODEL_SELECTION=NOT_STARTED

TI3_B_AUTHORIZED=false

MERGE_AUTHORIZED=false

CURRENT_AUTHORIZED_ACTIVITY=
NONE_AWAITING_AUTHOR_DECISION

STOP.

------------------------------------------------------------
28.2 BLOCKED
------------------------------------------------------------

TI3_TARGET_RESOLUTION=
BLOCKED_INSUFFICIENT_HIGH_CONFIDENCE_LABELS

TARGET_CONTRACT=NOT_ESTABLISHED

SUPERVISED_FRAGMENTATION_PATH=
CLOSED_WITH_AVAILABLE_LABELS

TI3_A_READY_TO_RESUME=false

FINAL_TEST=NOT_DEFINED_NOT_OPENED

ML_RUNS=0

MODEL_SELECTION=NOT_STARTED

TI3_B_AUTHORIZED=false

MERGE_AUTHORIZED=false

CURRENT_AUTHORIZED_ACTIVITY=
NONE_AWAITING_AUTHOR_DECISION

STOP.

============================================================
29. SE BLOCKED
============================================================

Se BLOCKED:

NÃO:

- criar novo extractor;
- executar Hough;
- mudar threshold;
- relaxar radius gate;
- reinterpretar IGNORE;
- abrir novos frames;
- criar A0.1;
- criar A0.2;
- repetir TI3_TARGET_RESOLUTION;
- treinar modelo com labels insuficientes.

A próxima ação deverá ser:

PIVOT METODOLÓGICO EXPLÍCITO

submetido a nova decisão autoral.

============================================================
30. FINAL_TEST
============================================================

Nesta tarefa:

FINAL_TEST=
NOT_DEFINED_NOT_OPENED

Não chamar:

SEALED

antes de existir um manifesto formal de IDs.

Nenhum pixel candidato a futuro FINAL_TEST
pode ser aberto para:

- contar eventos;
- escolher split;
- medir distribuição;
- melhorar balanceamento;
- selecionar arquitetura.

============================================================
31. TESTES
============================================================

São permitidos apenas testes:

- sintéticos;
- documentais;
- sobre artefatos A0 já materializados;
- de deduplicação;
- de schema;
- de invariantes;
- de overlap de annotation_site_id;
- de consistência dos contratos.

ML training tests NÃO são autorizados.

============================================================
32. ANTI-LEAKAGE
============================================================

Garantir conceitualmente:

- mesma localização não atravessa split;
- repetição temporal não aumenta N independente;
- ESM3/ESM6 nunca entram como feature;
- informação de anotação não aparece no input;
- futuros patches multimodais usam apenas ESM1/2 ou ESM4/5;
- nenhum FINAL_TEST é consultado nesta fase.

============================================================
33. ANTI-REFINAMENTO INFINITO
============================================================

É proibido responder a um possível BLOCKED com:

“vamos melhorar um pouco o extractor.”

Não.

O extractor já está consumido para esta linha metodológica.

Esta etapa responde somente:

“Os high-confidence labels existentes são suficientes?”

SIM
→ avançar.

NÃO
→ pivot.

============================================================
34. REPORT FINAL
============================================================

Reportar objetivamente:

1. SHA do checkpoint TI3-A0;
2. HEAD final;
3. arquivos criados/modificados;
4. número bruto de círculos aceitos;
5. número de annotation_site_ids únicos;
6. distribuição ESM3/ESM6;
7. distribuição por aquisição;
8. repetição temporal;
9. distribuição de FIRST_CONFIDENT_OBSERVATION;
10. quantidade de IGNORE;
11. target final;
12. interpretação exata de POSITIVE;
13. interpretação exata de BACKGROUND_CANDIDATE;
14. interpretação exata de IGNORE;
15. WHAT_IS_ONE_SAMPLE;
16. viabilidade TRAIN/DEV/FINAL_TEST;
17. regra anti-leakage;
18. decisão LBP/RF;
19. decisão CNN;
20. decisão Hough;
21. papel futuro do solutal;
22. afirmações científicas autorizadas;
23. afirmações explicitamente proibidas;
24. novos pixels acessados;
25. ML runs;
26. FINAL_TEST;
27. testes;
28. CI, se aplicável;
29. worktree/index;
30. estado final.

============================================================
35. BLOCO TERMINAL OBRIGATÓRIO
============================================================

Se PASS, terminar exatamente com:

TI3_TARGET_RESOLUTION=PASS
TARGET_CONTRACT=FROZEN
WEAK_LABEL_STRATEGY=HIGH_CONFIDENCE_PLUS_IGNORE
PUBLISHED_FRAGMENTATION_LOCATION_TARGET=VALID_FOR_INTERNAL_ML
CIRCLE_IS_FRAGMENT_MASK=false
EXACT_ONSET_AVAILABLE=false
SOLUTAL_INPUT_SEMANTICS=RELATIVE_SOLUTE_FIELD
FORECASTING_AUTHORIZED=false
CAUSALITY_CLAIM_AUTHORIZED=false
EXTERNAL_GENERALIZATION_CLAIM=false
FINAL_TEST=NOT_DEFINED_NOT_OPENED
ML_RUNS=0
TI3_A_READY_TO_RESUME=true
TI3_B_AUTHORIZED=false
MERGE_AUTHORIZED=false
CURRENT_AUTHORIZED_ACTIVITY=NONE_AWAITING_AUTHOR_DECISION

Se BLOCKED, terminar exatamente com:

TI3_TARGET_RESOLUTION=BLOCKED_INSUFFICIENT_HIGH_CONFIDENCE_LABELS
TARGET_CONTRACT=NOT_ESTABLISHED
SUPERVISED_FRAGMENTATION_PATH=CLOSED_WITH_AVAILABLE_LABELS
CIRCLE_IS_FRAGMENT_MASK=false
FORECASTING_AUTHORIZED=false
CAUSALITY_CLAIM_AUTHORIZED=false
EXTERNAL_GENERALIZATION_CLAIM=false
FINAL_TEST=NOT_DEFINED_NOT_OPENED
ML_RUNS=0
TI3_A_READY_TO_RESUME=false
TI3_B_AUTHORIZED=false
MERGE_AUTHORIZED=false
CURRENT_AUTHORIZED_ACTIVITY=NONE_AWAITING_AUTHOR_DECISION

EXECUTE SOMENTE TI3_TARGET_RESOLUTION.
