# TI3-A0 — TARGET CONTRACT + ANNOTATION SEMANTICS + SPLIT FEASIBILITY
# Resolução finita dos pré-requisitos metodológicos de TI3-A
# Nenhum treinamento autorizado
# DDD + SDD + evidence-first + fail-closed + convergence governance

Repositório:
snbi-dendritic-fragmentation-ml

Branch atual:
feat/ti3-canonical-dataset-baseline

Baseline canônica:
67786bd4e23406e7f19860a53fe237e6d7b648cb

============================================================
ESTADO CANÔNICO
============================================================

TI2R_SOLUTE=COMPLETE
G2_SOLUTE=PASS
HOLDOUT_SOLUTE=CONSUMED
SOLUTAL_INTERNAL_VALIDATION=PASS
SOLUTAL_EXTERNAL_GENERALIZATION=NOT_CLAIMED

TI3-A foi corretamente interrompido:

TI3_A=BLOCKED_METHOD_PRECONDITIONS
TI3_A_DATASET=BLOCKED_TARGET_CONTRACT_NOT_VERIFIED
TI3_A_SPLIT=NOT_DEFINED
TI3_A_LEAKAGE_GUARDS=NOT_IMPLEMENTED
TI3_A_CURRICULAR_ALIGNMENT=NOT_REACHED
TI3_A_BASELINE=NOT_STARTED
FINAL_TEST=NOT_DEFINED_NOT_OPENED
MODEL_SELECTION=NOT_STARTED

Não houve:
- treinamento;
- ML scientific run;
- abertura de FINAL_TEST;
- novo acesso experimental;
- alteração de TI2R.

============================================================
NOVO CONHECIMENTO DOCUMENTAL
============================================================

A publicação primária de Gibbs et al.:

"In Situ X-Ray Observations of Dendritic Fragmentation
During Directional Solidification of a Sn-Bi Alloy"

afirma que as LOCALIZAÇÕES DOS EVENTOS CUMULATIVOS DE FRAGMENTAÇÃO
são circundadas/circled.

Isso é consistente com:

ESM3 / ESM6 =
cumulative_fragmentation_annotation

e com ANN-201:

círculo NÃO é máscara do fragmento.

Portanto é proibido assumir:

pixels internos ao círculo = ground-truth segmentation mask.

Hipótese a verificar:

os círculos podem codificar POINT/EVENT LOCATION annotations
e seu surgimento temporal pode permitir construir eventos discretos.

Essa hipótese NÃO está previamente aprovada.
Ela deve ser testada nesta etapa.

============================================================
MISSÃO
============================================================

Resolver, de forma finita e auditável, os dois bloqueios metodológicos:

B1:
ausência de target ML validado;

B2:
ausência de protocolo de split apropriado ao número de aquisições
e à dependência temporal.

Esta tarefa deve produzir uma DECISÃO METODOLÓGICA.

Não treinar ML.

Não selecionar CNN.

Não executar baseline.

Não abrir FINAL_TEST.

============================================================
FASE 0 — PRESERVAR O BLOQUEIO ANTERIOR
============================================================

Existem seis arquivos novos não staged em:

artifacts/evidence/TI3_A/

Eles registram a parada anterior.

Antes de novo trabalho:

1. validar seu conteúdo;
2. confirmar que correspondem ao report entregue ao autor;
3. fazer UM commit documental preservando esse estado.

Mensagem sugerida:

docs(ti3): record target-contract precondition block

Não modificar retroativamente esses arquivos após o checkpoint,
exceto se necessário criar novos artefatos em subdiretório distinto.

============================================================
FASE 1 — EVIDÊNCIA DOCUMENTAL
SEM PIXELS NOVOS
============================================================

Construir uma tabela de evidência usando somente:

- source_manifest;
- metadata;
- contratos existentes;
- G2_FRAG;
- G2_SOLUTE;
- publicação primária;
- documentos já versionados.

Responder explicitamente:

1. o que ESM3/ESM6 afirmam representar;
2. se os círculos representam:
   a) localização;
   b) extensão;
   c) ambos;
3. o que é cumulativo;
4. o que NÃO está documentado;
5. quais inferências precisam de validação empírica.

A publicação permite afirmar:

"locations of cumulative fragmentation events are circled"

Não extrapolar isso para:

"circle interior is the fragment mask".

============================================================
FASE 2 — MATERIAL DE DESENVOLVIMENTO JÁ EXPOSTO
============================================================

Antes de abrir qualquer novo frame, utilizar SOMENTE os frames de anotação
já previamente expostos nas fases G2:

ESM3:
0, 73, 146, 219, 293

ESM6:
0, 98, 197, 295, 394

Esses ativos devem ser classificados explicitamente como:

ANNOTATION_CONTRACT_DEVELOPMENT_ONLY

Nunca poderão integrar FINAL_TEST futuro.

É autorizado reexaminar SOMENTE esses frames nesta etapa para caracterizar
a representação gráfica das anotações.

Registrar I/O e hashes.

============================================================
FASE 3 — CARACTERIZAÇÃO DAS ANOTAÇÕES
============================================================

Nos frames já expostos, determinar com evidência:

- cor/espaço de cor dos marcadores;
- forma geométrica;
- espessura aproximada;
- raio/diâmetro;
- se o interior do círculo contém imagem original;
- persistência de marcadores entre os instantes disponíveis;
- surgimento de novos marcadores;
- sobreposição;
- marcadores cortados por borda;
- textos/overlays potencialmente confundidores.

Não interpretar círculo como objeto físico.

O objetivo é encontrar:

ANNOTATION_GEOMETRY

e

ANNOTATION_SEMANTICS.

============================================================
FASE 4 — APROVEITAMENTO CURRICULAR REAL
============================================================

Avaliar, SOMENTE para extração do label gráfico:

- thresholding;
- threshold por cor/chroma;
- Otsu, se pertinente;
- connected components;
- contornos;
- Hough Circle Transform.

Essas técnicas derivam do material A4/A5 da Trilha 2.

Não usar uma técnica apenas porque foi ensinada.

Escolher o método MAIS SIMPLES que extraia de forma robusta:

circle center -> (x, y)

Se threshold + connected components for suficiente,
NÃO adicionar Hough.

Se Hough for necessário, justificar.

Não usar Canny/Hough como entrada obrigatória do futuro modelo.

============================================================
FASE 5 — PROTÓTIPO DE LABEL EXTRACTOR
============================================================

Se a representação permitir:

implementar um extrator separado do pipeline ML que produza:

annotation_id
source_id
frame_index
experimental_time_s
center_x
center_y
radius_or_extent_descriptor
provenance
confidence/status

IMPORTANTE:

radius_or_extent_descriptor descreve somente o MARCADOR GRÁFICO.

Não descreve dimensão física do fragmento.

Inicialmente testar com:

1. dados sintéticos;
2. frames já expostos autorizados.

Não acessar frames novos nesta fase.

============================================================
FASE 6 — CONTRATO TEMPORAL
============================================================

Verificar se os cinco instantes já expostos sustentam a propriedade:

annotations(t_i) ⊆ annotations(t_j), para t_j > t_i

dentro de tolerância espacial adequada.

Se sim, documentar:

CUMULATIVE_PERSISTENCE_SUPPORTED_ON_EXPOSED_DEVELOPMENT_FRAMES=true

Se não:

não inventar mecanismo de first appearance.

Registrar bloqueio.

IMPORTANTE:

os frames esparsos podem comprovar persistência parcial,
mas podem NÃO determinar o frame exato de nascimento de um evento.

Distinguir rigorosamente:

EVENT_LOCATION

de:

EVENT_ONSET_FRAME.

============================================================
FASE 7 — DECISÃO SOBRE O TARGET
============================================================

Deliberar entre os targets sustentados pela evidência.

Opções possíveis incluem:

A)
point-event localization;

B)
event/no-event classification em patches definidos em torno de
event locations;

C)
frame-level new-event classification;

D)
outro target demonstravelmente sustentado.

SEGMENTATION MASK derivada do interior dos círculos é PROIBIDA.

Escolher somente UMA definição principal.

O contrato deve especificar:

WHAT_IS_ONE_SAMPLE
INPUT
TARGET
LABEL_SOURCE
POSITIVE_RULE
NEGATIVE_RULE
AMBIGUITY_RULE
SPATIAL_TOLERANCE
TEMPORAL_REFERENCE
PERSISTENCE_RULE

Se algum desses elementos não puder ser justificado:

TARGET_CONTRACT=BLOCKED

============================================================
REGRA SOBRE NEGATIVOS
============================================================

Não assumir automaticamente:

sem círculo = ausência física de fragmentação.

Determinar se a fonte permite tratar regiões/tempos não anotados como
negativos confiáveis.

Se não houver evidência suficiente, usar estado:

UNLABELED / UNKNOWN

em vez de NEGATIVE.

Uma estratégia de ML não pode converter ausência de anotação em
ground truth negativo sem justificativa.

============================================================
FASE 8 — NOVOS FRAMES: ESCALADA ÚNICA E LIMITADA
============================================================

Somente se:

1. a semântica LOCATION estiver sustentada;
2. o único ponto restante for confirmar temporal persistence/onset;
3. os frames já expostos forem insuficientes;

fica autorizada UMA escalada limitada.

Antes de abrir qualquer pixel novo:

- criar manifesto;
- congelar os índices;
- registrar hashes;
- marcar todos como DEVELOPMENT_ONLY;
- excluir permanentemente esses índices de FINAL_TEST.

Escolher a menor janela temporal contígua tecnicamente justificável
em torno de frames de DESENVOLVIMENTO já conhecidos, nunca procurar
adaptativamente até encontrar um resultado favorável.

Preferir centros:

ESM3:146
ESM6:197

Não usar antigos holdouts como centro se desnecessário.

Registrar:

ANNOTATION_TEMPORAL_DEV_WINDOW

Não é permitido expandir a janela depois de observar o resultado.

Se a janela congelada for insuficiente:

STOP.

Não criar segunda janela nesta autorização.

============================================================
FASE 9 — SPLIT FEASIBILITY
============================================================

Há somente duas aquisições independentes documentadas.

Portanto:

3-way split por aquisição é impossível.

Não fingir independência inexistente.

Avaliar uma estratégia de:

BLOCKED TEMPORAL SPLIT

dentro de cada aquisição.

O protocolo candidato deve preservar:

TRAIN
DEVELOPMENT
FINAL_TEST

como intervalos temporais disjuntos.

FINAL_TEST será validação temporal interna,
NÃO validação externa entre experimentos independentes.

O split NÃO deve ainda ser executado se o target não estiver congelado.

Determinar requisitos de:

- contiguous temporal blocks;
- temporal embargo;
- context-window isolation;
- annotation persistence handling;
- group separation;
- boundary handling.

Se o target usar t±k ou horizonte h:

embargo >= dependência temporal necessária.

============================================================
REGRA ESPECIAL PARA ANOTAÇÕES CUMULATIVAS
============================================================

Se o target futuro for baseado em NEW EVENT:

não utilizar diretamente o mapa cumulativo como target.

O conceito correto deve ser algo como:

NEW_EVENTS(t) =
ANNOTATIONS(t) minus persistent annotations from earlier time

com matching espacial tolerante e regra pré-especificada.

Essa fórmula é somente conceitual até ser validada.

O primeiro frame de cada split deve receber tratamento explícito.

Nenhuma informação de um split posterior pode ser utilizada para construir
labels de um split anterior.

============================================================
FASE 10 — FINAL TEST
============================================================

Nesta tarefa:

FINAL_TEST continua:

NOT_DEFINED_NOT_OPENED

Não chamar SEALED antes de existir manifesto de IDs.

Nenhum candidato a FINAL_TEST pode ser aberto apenas para contar eventos
ou escolher um split mais conveniente.

Após TARGET_CONTRACT=PASS, esta tarefa deve apenas propor
o protocolo de congelamento futuro.

============================================================
FASE 11 — ARTEFATOS
============================================================

Criar:

artifacts/evidence/TI3_A0/

DOCUMENTARY_EVIDENCE.md
ANNOTATION_SEMANTICS.md
ANNOTATION_EXTRACTION_SPEC.md
TARGET_CONTRACT.md
SPLIT_FEASIBILITY.md
COURSE_ALIGNMENT_LABEL_EXTRACTION.md
commands.json
io-audit.json
results.json
verification.json

Se houver implementação mínima:

scripts/ ou src/ apropriado
+
testes sintéticos e de desenvolvimento autorizados.

============================================================
ALINHAMENTO CURRICULAR
============================================================

Registrar explicitamente a conexão:

A5:
thresholding / contornos / Hough
          ↓
extração potencial dos centros dos círculos de annotation

Isso é diferente de:

Canny/Hough como input do modelo.

Preservar também:

Sobel -> NGF

descritores locais -> SS8/self-similarity

sem alterar os métodos G2 já validados.

============================================================
CRITÉRIO DE CONVERGÊNCIA
============================================================

Esta autorização termina em exatamente um destes estados:

A)

TI3_A0_TARGET_CONTRACT=PASS
TI3_A0_SPLIT_FEASIBILITY=PASS
TI3_A_READY_TO_RESUME=true

ou:

B)

TI3_A0_TARGET_CONTRACT=BLOCKED
TI3_A_READY_TO_RESUME=false

Não criar A0.1.
Não fazer tuning.
Não treinar modelo.
Não iniciar TI3-B.

============================================================
ESTADO FINAL ESPERADO — PASS
============================================================

TI3_A0=PASS
ANNOTATION_SEMANTICS=VERIFIED_FOR_TARGET_SCOPE
CIRCLE_IS_FRAGMENT_MASK=false
TARGET_CONTRACT=FROZEN
SPLIT_STRATEGY=INTERNAL_TEMPORAL_BLOCKED
EXTERNAL_GENERALIZATION_CLAIM=false
FINAL_TEST=NOT_DEFINED_NOT_OPENED
ML_RUNS=0
TI3_A_READY_TO_RESUME=true
TI3_B_AUTHORIZED=false
MERGE_AUTHORIZED=false
CURRENT_AUTHORIZED_ACTIVITY=NONE_AWAITING_AUTHOR_DECISION

============================================================
ESTADO FINAL — BLOCKED
============================================================

TI3_A0=BLOCKED_TARGET_CONTRACT
CIRCLE_IS_FRAGMENT_MASK=false
FINAL_TEST=NOT_DEFINED_NOT_OPENED
ML_RUNS=0
TI3_A_READY_TO_RESUME=false
TI3_B_AUTHORIZED=false
MERGE_AUTHORIZED=false
CURRENT_AUTHORIZED_ACTIVITY=NONE_AWAITING_AUTHOR_DECISION

============================================================
REPORT FINAL
============================================================

Informar:

1. commit que preservou o bloqueio TI3-A;
2. evidência documental primária;
3. arquivos ESM3/ESM6 realmente abertos;
4. bytes;
5. representação dos círculos;
6. método de extração avaliado;
7. técnica A4/A5 efetivamente pertinente;
8. resultado da extração;
9. evidência de cumulatividade/persistência;
10. possibilidade ou não de obter first appearance;
11. target escolhido;
12. regra de positivos;
13. regra de negativos/unknown;
14. unidade amostral;
15. proposta de split temporal;
16. embargo necessário;
17. acessos novos, se algum;
18. confirmação de zero ML runs;
19. FINAL_TEST;
20. próximo estado autorizado.

EXECUTE SOMENTE TI3-A0.