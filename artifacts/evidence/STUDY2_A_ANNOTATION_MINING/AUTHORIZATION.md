# STUDY2-A — FULL-SEQUENCE AUTOMATED ANNOTATION MINING
#
# Reconstrução temporal automatizada e densa das
# anotações publicadas de fragmentação dendrítica.
#
# OBJETIVO PRIMÁRIO:
#
# aproveitar integralmente ESM3 e ESM6 para construir
# um corpus longitudinal de sites de anotação e suas
# observações temporais.
#
# NÃO É UM EXPERIMENTO DE ACURÁCIA.
# NÃO TREINAR MODELOS.
# NÃO USAR ESM1/2/4/5 COMO EVIDÊNCIA DE LABEL.
# NÃO USAR REVISÃO HUMANA.
# NÃO EXECUTAR HOUGH NESTA FASE.
#
# O produto central é um CORPUS/Ledger,
# não um classificador.
#
# DDD + SDD + data-centric design
# + frozen label semantics
# + temporal consistency
# + deterministic streaming
# + provenance
# + fail-closed
# + convergence.

Repositório:

/home/leonardomaximinobernardo/My_projects/snbi-dendritic-fragmentation-ml

Fontes completas verificadas:

/home/leonardomaximinobernardo/Downloads/trabalho_Final_IfGoiano/videos_trabalho_Final_IfGoiano/

ESM1:
11837_2015_1646_MOESM1_ESM.mp4

ESM2:
11837_2015_1646_MOESM2_ESM.mp4

ESM3:
11837_2015_1646_MOESM3_ESM.mp4

ESM4:
11837_2015_1646_MOESM4_ESM.mp4

ESM5:
11837_2015_1646_MOESM5_ESM.mp4

ESM6:
11837_2015_1646_MOESM6_ESM.mp4

============================================================
1. ESTADO CANÔNICO
============================================================

EXPERIMENT_1=
COMPLETE_WITH_FINAL_EVALUATION

MODEL_SELECTION=
COMPLETE

SELECTED_MODEL=
MULTIMODAL_LBP_RF

FINAL_TEST_STATE=
CONSUMED

STUDY2_STORAGE_AUDIT=PASS

STUDY2_SOURCE_CUSTODY_AUDIT=PASS

SOURCE_SCENARIO=B

VERIFIED_ESM_COUNT=6

FULL_SOURCE_CURRENT_AVAILABILITY=VERIFIED

STUDY2_PROVISIONAL_ARCHITECTURE=
HYBRID_STREAM_LEDGER_SELECTIVE_CACHE

O Estudo 1 é IMUTÁVEL.

Não reexecutar nenhuma ciência TI3-A/B/C/D.

============================================================
2. NOVO ESTUDO
============================================================

Criar Study 2 completamente separado.

Sincronizar main somente por fast-forward seguro.

Base esperada:

origin/main contendo o encerramento final
do Estudo 1.

Criar branch:

feat/study2a-dense-annotation-ledger

Não reutilizar uma branch científica do Estudo 1.

============================================================
3. QUESTÃO CIENTÍFICA
============================================================

Responder exclusivamente:

"Quanto da informação temporal presente nas
anotações cumulativas publicadas ESM3/ESM6 pode ser
reconstruída automaticamente, de maneira determinística,
rastreável e sem revisão humana?"

Não responder nesta fase:

- qual modelo é melhor;
- qual accuracy conseguimos;
- se CNN supera RF;
- se SVM supera RF;
- se soluto melhora classificação;
- forecasting;
- causalidade.

============================================================
4. SEMÂNTICA DO CORPUS
============================================================

Preservar:

CIRCLE ->
PUBLISHED_FRAGMENTATION_LOCATION

NÃO:

CIRCLE ->
PHYSICAL_FRAGMENT_MASK

NÃO:

CIRCLE ->
PHYSICAL_FRAGMENT_EXTENT

NÃO:

FIRST_APPEARANCE ->
EXACT_FRAGMENTATION_ONSET

TARGET SEMANTICS HISTÓRICA:

PUBLISHED_FRAGMENTATION_LOCATION_PRESENT

Nesta fase, contudo, não reduzir todo o corpus
imediatamente a target binário.

Construir estados de evidência mais ricos.

============================================================
5. SOURCES
============================================================

ESTUDO 2A pode decodificar somente:

ESM3
ESM6

ESM1/2/4/5:

PROIBIDOS como fonte de decisão de label nesta fase.

Razão:

a definição da anotação deve depender exclusivamente
dos marcadores publicados pelos autores.

Nenhuma textura estrutural ou solutal pode influenciar
a aceitação de um marcador.

============================================================
6. COBERTURA
============================================================

Processar exatamente:

ESM3:
frames 0..293
294 frames

ESM6:
frames 0..394
395 frames

TOTAL:
689 frames.

Cada frame deve possuir:

FRAME_PROCESSING_STATUS.

Nenhum frame pode desaparecer silenciosamente.

Estados possíveis:

PROCESSED
DECODE_FAILED
INTEGRITY_FAILED

A execução não deve simplesmente pular falhas.

============================================================
7. ARQUITETURA DE I/O
============================================================

Usar streaming.

Não exportar todos os frames.

Não salvar PNG/JPEG por frame.

Não materializar dataset full-frame.

Preferência:

decoder
→ frame YUV420p em memória
→ processamento
→ metadados
→ liberar frame.

Manter:

MAX_TEMP_BYTES <= 268435456

MAX_PATCH_CACHE_BYTES <= 2147483648

MIN_FREE_DISK_RESERVE_BYTES >= 53687091200

Nesta fase:

PATCH_CACHE_BYTES esperado = 0.

============================================================
8. INTEGRIDADE DAS FONTES
============================================================

Antes de qualquer frame:

confirmar hashes:

ESM3 =
d76a6466e50480a2116bc545a0ee2b8095cc14c54f861ecebee87de5b64e35be

ESM6 =
5b8747758afde34fb626f3c4ffbd0b49ba6ca6f6b49bfa81b8cf9ee8459280ea

Se divergirem:

STOP.

Não usar ZIP como fallback silencioso.

============================================================
9. REUTILIZAR O DETECTOR A0
============================================================

O detector primário deve ser o detector histórico
já validado.

NÃO reimplementar sua ciência se puder reutilizar
diretamente:

src/snbi_fragmentation/ti3_a0_annotations.py

Método histórico:

CHROMA_THRESHOLD_CONNECTED_COMPONENTS_ALGEBRAIC_CIRCLE

Configuração congelada:

chroma_distance = 20

minimum_component_pixels = 32

minimum_radius = 8.0

maximum_radius = 16.0

maximum_axis_ratio = 1.2

maximum_radial_p95 = 4.0

minimum_angular_coverage = 0.9

persistence_tolerance_px = 2.0

Não alterar esses valores após observar
os vídeos completos.

============================================================
10. HISTORICAL REPRODUCTION GATE
============================================================

Antes da mineração inédita, validar a implementação
utilizando SOMENTE os dez frames historicamente
já expostos:

ESM3:
0,73,146,219,293

ESM6:
0,98,197,295,394

Esses frames são DEVELOPMENT histórico,
portanto podem ser usados como compatibility fixture.

O decoder + detector deve reproduzir o resultado
histórico A0.

Exigir:

- mesmos raw frame hashes, se os hashes históricos
  correspondentes estiverem disponíveis;

- mesmos counts de VALID/AMBIGUOUS/SMALL;

- mesmos VALID centers dentro da tolerância
  numérica estritamente necessária;

- total histórico:
  108 VALID observations;

- 380 AMBIGUOUS;

- 3 SMALL.

Não alterar thresholds para fazer o teste passar.

Se houver divergência:

STUDY2_A=
BLOCKED_LEGACY_REPRODUCTION

STOP antes de qualquer frame novo.

============================================================
11. DESENVOLVIMENTO ANTES DO FREEZE
============================================================

Antes de acessar frames inéditos é permitido:

- implementar streaming;
- implementar ledger;
- implementar tracker;
- executar testes sintéticos;
- executar o gate dos dez frames históricos;
- corrigir bugs de implementação.

Não é permitido:

- alterar os parâmetros científicos do A0;
- testar valores alternativos;
- usar novos frames para escolher tolerâncias;
- avaliar Hough;
- olhar visualmente novos frames para tuning.

============================================================
12. TRACKING TEMPORAL
============================================================

Depois do gate histórico:

associar observações VALID entre frames
da mesma fonte.

Nunca misturar:

ESM3
e
ESM6.

Cada site pertence exatamente a uma aquisição.

Usar como distância máxima histórica:

2.0 px.

Evitar drift transitivo.

Cada site deve possuir um:

CANONICAL_CENTER

ancorado à sua primeira observação direta válida.

Uma observação futura só pode ser associada
se estiver dentro da tolerância do site canônico
e a associação for não ambígua.

Se um candidato puder pertencer a mais de um site:

CONFLICT.

Não escolher arbitrariamente o mais próximo.

============================================================
13. CRIAÇÃO DE NOVO SITE
============================================================

Uma observação DIRECT_VALID cria novo site somente se:

- não corresponde de maneira única
  a site existente;

- não está em conflito espacial;

- passa integralmente pelo detector A0 congelado.

Site ID deve ser determinístico.

Construir a identidade a partir de informações
imutáveis, por exemplo:

source_id
+
first_direct_frame
+
first_direct_component_id
+
canonical center

e produzir hash/ID estável.

============================================================
14. NATUREZA CUMULATIVA
============================================================

Usar a propriedade documental:

as localizações publicadas são cumulativas.

Isso permite interpretar:

site identificado anteriormente
+
componente posteriormente sobreposto/ambíguo

como:

KNOWN_SITE_GRAPHICAL_AMBIGUITY

e não:

NOVO EVENTO.

Porém a natureza cumulativa NÃO autoriza criar
fragmentação física onde nenhum marcador foi observado.

============================================================
15. ESTADOS DE OBSERVAÇÃO
============================================================

Não usar apenas POSITIVE/NEGATIVE.

Cada site × frame deve poder receber um
estado documental como:

DIRECT_VALID

= detector A0 reconheceu diretamente
um círculo válido naquele frame.

TEMPORAL_SUPPORTED_AMBIGUOUS

= há evidência cromática/componente ambíguo
na região de um site já estabelecido,
e a identidade é sustentada temporalmente.

PERSISTENCE_EXPECTED_UNRESOLVED

= site já foi diretamente estabelecido,
mas naquele frame não existe evidência gráfica
suficiente para classificação direta.

PRE_FIRST_CONFIDENT_ANNOTATION

= frame anterior à primeira observação direta
do site.

CONFLICT

= identidade temporal não resolvida.

INVALID_FRAME

= frame não processável.

Esses estados são DOCUMENTAIS.

Não são classes físicas.

============================================================
16. NÃO PROPAGAR POSITIVO CEGAMENTE
============================================================

A regra:

"círculo apareceu uma vez
→ todos os frames futuros são positivos"

é PROIBIDA como label científico automático.

A cumulative semantics pode gerar:

PERSISTENCE_EXPECTED_UNRESOLVED

mas somente evidência gráfica/temporal suficiente
pode gerar:

DIRECT_VALID
ou
TEMPORAL_SUPPORTED_AMBIGUOUS.

Preservar diferença entre:

observado
e
inferido.

============================================================
17. PRIMEIRA APARIÇÃO
============================================================

Para cada site registrar:

FIRST_DIRECT_VALID_FRAME

e, quando possível:

LAST_CONFIDENT_MARKER_ABSENCE_FRAME

TRANSITION_INTERVAL.

Não chamar:

FRAGMENTATION_ONSET.

Termo permitido:

FIRST_CONFIDENT_ANNOTATION_FRAME.

O intervalo entre ausência e primeira presença
é incerteza documental,
não incerteza sobre instante físico de ruptura.

============================================================
18. COMPONENTES AMBÍGUOS
============================================================

Não transformar automaticamente os componentes
históricos ou novos AMBIGUOUS em negativos.

Registrar:

component_id
frame
bbox
reasons
proximidade a sites existentes
temporal context.

Um componente ambíguo pode ser classificado como:

EXPLAINED_BY_KNOWN_SITE

EXPLAINED_BY_MULTIPLE_KNOWN_SITES

POTENTIAL_NEW_SITE_UNRESOLVED

NON_SITE_GRAPHICAL_AMBIGUITY

somente quando as regras determinísticas permitirem.

Não usar interpretação visual humana.

============================================================
19. SOBREPOSIÇÕES
============================================================

Esta é uma questão central do Study 2A.

Exemplo:

frame t:
círculo A é válido.

frame t+k:
círculo A + círculo B aparecem sobrepostos
e formam componente ambíguo.

Se A já é conhecido:

não apagar A.

Se B ainda não possui observação direta válida:

não criar B apenas porque o componente ficou maior.

Registrar:

OVERLAP_WITH_KNOWN_TRACKS

e manter a incerteza sobre eventual novo site.

============================================================
20. HOUGH
============================================================

HOUGH=NOT_EXECUTED

nesta fase.

Razão:

o novo eixo de informação é a temporalidade,
não um novo ajuste geométrico.

A execução integral dos frames deve primeiro mostrar
quanto o detector A0 + tracking temporal conseguem
recuperar.

Se permanecerem potenciais novos sites irrecuperáveis,
Hough poderá ser deliberado futuramente como um
segundo método automatizado.

Nenhum resultado desta fase autoriza Hough
automaticamente.

============================================================
21. TEMPORAL DELTA — SOMENTE EVIDÊNCIA
============================================================

É permitido calcular, se implementado
deterministicamente, mudanças da máscara cromática
entre frames consecutivos.

Mas nesta fase o TEMPORAL DELTA:

- pode gerar evidência auxiliar;
- pode indicar nova tinta gráfica;
- pode apoiar classification status;
- NÃO pode sozinho criar AUTO-GOLD site.

Qualquer site AUTO-GOLD exige pelo menos
uma observação DIRECT_VALID.

Isso mantém alta precisão sem revisão humana.

============================================================
22. AUTO-GOLD SITE
============================================================

Definir:

AUTO_GOLD_SITE

somente se:

- possui pelo menos uma DIRECT_VALID observation;
- possui identidade temporal não conflituosa;
- canonical center está definido;
- source/acquisition está definido;
- provenance completa;
- nenhuma incompatibilidade estrutural do track.

AUTO_GOLD não significa:

evento físico completamente validado.

Significa:

site de marcador publicado recuperado
automaticamente com alta confiança.

============================================================
23. AUTO-SILVER OBSERVATION
============================================================

TEMPORAL_SUPPORTED_AMBIGUOUS pode formar:

AUTO_SILVER_OBSERVATION.

AUTO_SILVER:

não deve ser confundido com AUTO_GOLD.

Não utilizar automaticamente em treinamento
nesta fase.

Sua utilidade será deliberada em Study 2B.

============================================================
24. LEGACY CONSISTENCY
============================================================

Os 52 sites históricos do Estudo 1
devem ser mapeáveis aos novos tracks.

Exigir relatório:

LEGACY_SITE_COUNT=52

LEGACY_SITE_MAPPED=<n>

LEGACY_SITE_UNMAPPED=<n>

Ideal esperado:

52/52.

Se não for 52/52:

não excluir silenciosamente.

Registrar divergência e seus IDs.

Uma divergência de legado pode bloquear
a promoção do corpus, mesmo que a mineração termine.

============================================================
25. EVIDÊNCIA DE DENSIDADE
============================================================

Medir separadamente:

UNIQUE_AUTO_GOLD_SITES

DIRECT_VALID_OBSERVATIONS

AUTO_SILVER_OBSERVATIONS

AMBIGUOUS_OBSERVATIONS

SITE_FRAME_RECORDS

PRE_ANNOTATION_RECORDS

PERSISTENCE_EXPECTED_RECORDS

CONFLICT_RECORDS

Nunca usar apenas:

N_SAMPLES

sem dizer qual unidade está sendo contada.

============================================================
26. PSEUDO-REPLICAÇÃO
============================================================

Registrar permanentemente:

N_ACQUISITIONS ≈ 2.

Nunca escrever:

8.000 observations
=
8.000 independent experiments.

Distinguir sempre:

N_ACQUISITIONS

N_SITES

N_SITE_FRAME_OBSERVATIONS.

============================================================
27. FRAME/TIME
============================================================

Preservar:

ESM3:
experimental_time_s =
-25.96 + 1.18 * frame_index

ESM6:
experimental_time_s =
-34.22 + 1.18 * frame_index

5 fps é playback.

Não usar:

frame/5

como tempo físico experimental.

============================================================
28. OUTPUT PRINCIPAL
============================================================

Criar estrutura Study 2 própria, sem sobrescrever
artefatos TI3.

Sugestão:

artifacts/evidence/STUDY2_A_ANNOTATION_MINING/

TRACKED / textual e compacto:

PROTOCOL.md
METHOD_FREEZE.json
SOURCE_CUSTODY.json
LEGACY_REPRODUCTION.json
FRAME_SUMMARY.json
SITE_LEDGER.json
CORPUS_SUMMARY.json
QUALITY_REPORT.md
IO_AUDIT.json
results.json
terminal-state.json

Se OBSERVATION_LEDGER for razoavelmente pequeno:

OBSERVATION_LEDGER.jsonl

pode ser versionado.

Se for grande:

armazenar em:

data/derived/study2/

como artefato local ignorado,
com:

path
size
sha256
record_count

registrados em um manifesto textual versionado.

Não adicionar dezenas de milhares de arquivos
individuais ao Git.

============================================================
29. RAW CANDIDATE RECORDS
============================================================

Se for útil conservar todos os componentes
por frame:

usar UM ou poucos containers textuais agregados.

Não criar:

689 diretórios
ou
centenas de milhares de JSONs individuais.

Preferir:

candidate-components.jsonl

ou formato textual agregado equivalente.

Respeitar orçamento de armazenamento.

============================================================
30. NENHUM PATCH NESTA FASE
============================================================

PATCHES_CREATED=0

Não abrir:

ESM1
ESM2
ESM4
ESM5

Não gerar:

65×65 patches.

Não calcular:

LBP
CNN tensor
SVM features.

Study 2A termina antes disso.

============================================================
31. TESTES SINTÉTICOS
============================================================

Antes do full run, testar:

- círculo isolado;
- dois círculos;
- círculo persistente;
- novo círculo;
- desaparecimento do detector;
- componente ambíguo;
- dois sites em overlap;
- associação 2px;
- conflito de associação;
- não drift transitive;
- FIRST_DIRECT;
- PRE_FIRST;
- temporal-supported ambiguity;
- source isolation ESM3/ESM6;
- frame-order enforcement;
- no duplicate frame;
- no duplicate site identity;
- no human-review path;
- Hough disabled;
- ESM1/2/4/5 forbidden.

============================================================
32. FREEZE
============================================================

Depois de:

- testes sintéticos PASS;
- legacy reproduction PASS;

congelar o método.

Commit sugerido:

feat(study2a): freeze dense annotation mining protocol

Registrar:

STUDY2_A_METHOD_FREEZE_SHA

Depois disso:

não alterar parâmetros científicos.

============================================================
33. CI
============================================================

Push somente depois do freeze.

Adicionar CI Study2A apenas para:

- synthetic contracts;
- phase scope;
- data guard;
- historical regression;
- no source video requirement.

GitHub CI não deve depender dos MP4 locais.

Exigir:

todos os jobs históricos continuam verdes
+
Study2A synthetic PASS.

Se CI falhar:

STOP.

Não executar full sequence.

============================================================
34. FULL-SEQUENCE EXECUTION
============================================================

Somente depois do freeze + CI verde.

Executar exatamente UMA mineração integral:

ESM3 294 frames
+
ESM6 395 frames.

SCIENTIFIC_STUDY2A_RUNS=1

Embora não seja ML,
tratar como uma execução científica do corpus.

Não tuning.

Não retry por resultado insatisfatório.

Falha técnica parcial deve ser registrada
e deliberada separadamente.

============================================================
35. I/O
============================================================

Registrar:

compressed source opens

decoded frames

decoded bytes

maximum resident frame window

temporary bytes

ledger bytes

candidate records

peak cache usage

remaining disk space.

Confirmar:

ESM1_OPENS=0
ESM2_OPENS=0
ESM4_OPENS=0
ESM5_OPENS=0

============================================================
36. QUALITY METRICS
============================================================

O Study2A NÃO possui accuracy.

Suas métricas são:

FRAME_COVERAGE

LEGACY_REPRODUCTION

LEGACY_SITE_MAPPING

UNIQUE_SITE_COUNT

DIRECT_OBSERVATION_COUNT

TEMPORAL_SUPPORTED_COUNT

AMBIGUITY_COUNT

CONFLICT_COUNT

TRACK_PERSISTENCE_DISTRIBUTION

TRANSITION_INTERVAL_DISTRIBUTION

UNEXPECTED_GRAPHICAL_DISAPPEARANCE_COUNT

SOURCE_PROVENANCE_COMPLETENESS

DETERMINISTIC_ID_COMPLETENESS

STORAGE_BUDGET_COMPLIANCE.

============================================================
37. NÃO DEFINIR META DE NÚMERO DE SITES
============================================================

Não declarar:

PASS somente se > X sites.

O número encontrado é resultado científico.

Study2A PASS significa:

- protocolo executado integralmente;
- proveniência íntegra;
- frames contabilizados;
- corpus consistente;
- resultados preservados.

Não significa:

muitos sites foram encontrados.

============================================================
38. COMPARAÇÃO COM ESTUDO 1
============================================================

Reportar descritivamente:

Study 1:
10 annotation frames examined.

Study 2A:
689 annotation frames examined.

Study 1:
108 direct valid observations.
52 unique historical sites.

Study 2A:
<resultados reais>.

Não chamar aumento de observações
de aumento de experimentos independentes.

============================================================
39. CLAIMS
============================================================

Permitido:

"full-sequence automated reconstruction
of published cumulative annotation locations"

"longitudinal annotation corpus"

"automatic high-confidence annotation sites"

"temporal evidence"

Proibido:

"complete physical fragmentation inventory"

"exact fragmentation onset"

"all fragmentation events"

"causal precursor"

"external validation"

"new independent experiments".

============================================================
40. HUMAN REVIEW
============================================================

HUMAN_REVIEW_USED=false

Não pedir confirmação visual durante a execução.

Não produzir manual corrections.

Não editar centers manualmente.

Não excluir sites manualmente.

Casos não resolvidos permanecem:

AMBIGUOUS / CONFLICT / UNRESOLVED.

Isso é intencional.

============================================================
41. CARTADA FUTURA
============================================================

Preservar explicitamente os casos:

AMBIGUOUS
CONFLICT
POTENTIAL_NEW_SITE_UNRESOLVED

para futuro:

HUMAN_IN_THE_LOOP_STUDY

Esse futuro estudo NÃO é autorizado aqui.

============================================================
42. TERMINAL
============================================================

Ao concluir:

STUDY2_A=PASS

STUDY2_A_METHOD=
FULL_SEQUENCE_TEMPORAL_ANNOTATION_MINING

ANNOTATION_FRAMES_EXPECTED=689

ANNOTATION_FRAMES_PROCESSED=<real>

UNIQUE_AUTO_GOLD_SITES=<real>

DIRECT_VALID_OBSERVATIONS=<real>

AUTO_SILVER_OBSERVATIONS=<real>

AMBIGUOUS_OBSERVATIONS=<real>

CONFLICT_RECORDS=<real>

LEGACY_SITES_EXPECTED=52

LEGACY_SITES_MAPPED=<real>

HUMAN_REVIEW_USED=false

HOUGH_EXECUTED=false

ESM1_OPENS=0
ESM2_OPENS=0
ESM4_OPENS=0
ESM5_OPENS=0

PATCHES_CREATED=0

ML_RUNS=0

STUDY2_B_READY_FOR_AUTHOR_DECISION=true

STUDY2_B_AUTHORIZED=false

CURRENT_AUTHORIZED_ACTIVITY=
NONE_AWAITING_AUTHOR_DECISION

============================================================
43. REPORT AO OPERADOR
============================================================

Informar:

1. branch/base;
2. source hashes;
3. detector parameters;
4. legacy reproduction;
5. method-freeze SHA;
6. CI;
7. full run command;
8. frames processed;
9. I/O;
10. sites únicos;
11. direct observations;
12. temporal-supported observations;
13. ambiguity;
14. conflicts;
15. mapping dos 52 sites históricos;
16. sites novos em relação ao Estudo 1;
17. distribuição temporal por site;
18. first-confidence intervals;
19. overlaps conhecidos;
20. unresolved candidates;
21. corpus storage;
22. storage guardrails;
23. human review confirmation;
24. Hough confirmation;
25. claim scope;
26. evidence checkpoint;
27. final CI;
28. Git status;
29. terminal state.

STOP.

NÃO INICIAR STUDY2-B.
NÃO TREINAR RF.
NÃO TREINAR SVM.
NÃO TREINAR CNN.