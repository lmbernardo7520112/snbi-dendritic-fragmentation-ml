# STUDY2-B — DENSE MULTIMODAL CORPUS CONSTRUCTION
#
# Construção de corpus longitudinal multimodal derivado
# do Study2-A concluído.
#
# OBJETIVO:
#
# transformar os 87 AUTO_GOLD sites e seus registros
# temporais em um corpo de dados multimodal denso,
# rastreável, determinístico e model-ready,
# SEM treinamento ML e SEM otimização de accuracy.
#
# FONTES CIENTÍFICAS:
#
# estrutural:
# ESM1 / ESM4
#
# campo solutal relativo:
# ESM2 / ESM5
#
# LABEL SOURCE:
# somente o ledger congelado do Study2-A.
#
# NÃO reabrir ESM3/ESM6 para redefinir labels.
#
# DDD + SDD
# + data-centric design
# + group-aware corpus
# + multimodal pairing
# + provenance
# + storage caps
# + fail-closed
# + convergence.

Repositório:

/home/leonardomaximinobernardo/My_projects/snbi-dendritic-fragmentation-ml

Fontes completas verificadas:

/home/leonardomaximinobernardo/Downloads/trabalho_Final_IfGoiano/videos_trabalho_Final_IfGoiano/

============================================================
1. ESTADO CANÔNICO
============================================================

EXPERIMENT_1=
COMPLETE_WITH_FINAL_EVALUATION

STUDY2_A=PASS

STUDY2_A_METRIC_RECONCILIATION=PASS

SCIENTIFIC_RESULT_IMPACT=NONE

ANNOTATION_FRAMES_PROCESSED=689

UNIQUE_AUTO_GOLD_SITES=87

DIRECT_VALID_OBSERVATIONS=7941

AUTO_SILVER_OBSERVATIONS=5737

SITE_FRAME_RECORDS=27396

PRE_ANNOTATION_RECORDS=8911

PERSISTENCE_EXPECTED_RECORDS=4807

CONFLICT_RECORDS=0

LEGACY_SITES_MAPPED=52

AMBIGUOUS_COMPONENTS_TOTAL=24246

AMBIGUOUS_UNSUPPORTED_BY_KNOWN_SITE=18670

AMBIGUOUS_EXPLAINED_BY_ONE_KNOWN_SITE=5415

AMBIGUOUS_EXPLAINED_BY_MULTIPLE_KNOWN_SITES=161

SMALL_COMPONENTS_TOTAL=292

UNRESOLVED_SITE_HYPOTHESIS_COMPONENTS=18962

NON_VALID_COMPONENTS_TOTAL=24538

HUMAN_REVIEW_USED=false

HOUGH_EXECUTED=false

Study2-A é imutável.

============================================================
2. INTEGRAÇÃO STUDY2-A
============================================================

Antes de Study2-B:

confirmar branch:

feat/study2a-dense-annotation-ledger

HEAD esperado:

7c192478554ea139752feaaff8cb2d44ff6747f7

Confirmar:

- worktree/index científico limpo;
- reconciliation evidence-only;
- CI final 7/7 jobs, 79 steps SUCCESS;
- ciência Study2-A intacta;
- JSONL locais intactos e hashes correspondentes.

Criar Draft PR para main.

Exigir CI verde.

Ready.

Merge por merge commit.

Não squash/rebase.

Registrar:

STUDY2_A_MERGE_SHA.

Exigir CI pós-merge verde.

Somente depois iniciar Study2-B.

============================================================
3. NOVA BRANCH
============================================================

Fast-forward main.

Criar:

feat/study2b-dense-multimodal-corpus

a partir exatamente de:

STUDY2_A_MERGE_SHA.

============================================================
4. QUESTÃO DO STUDY2-B
============================================================

Responder somente:

"Podemos transformar o corpus longitudinal
de anotações do Study2-A em um corpus multimodal
estrutural + solutal completo, consistente,
reprodutível e adequado a futuros benchmarks?"

Não responder:

- qual modelo é melhor;
- qual accuracy;
- qual classifier;
- causalidade;
- forecasting;
- generalização externa.

============================================================
5. FONTES
============================================================

ESM1:
STRUCTURAL_RADIOGRAPHY
bottom_up_anti_parallel

ESM2:
RELATIVE_SOLUTE_FIELD
bottom_up_anti_parallel

ESM4:
STRUCTURAL_RADIOGRAPHY
top_down_parallel

ESM5:
RELATIVE_SOLUTE_FIELD
top_down_parallel

ESM3/ESM6:

NÃO devem ser reprocessados.

Consumir somente:

SITE_LEDGER
OBSERVATION_LEDGER
candidate-components
canonical metric reconciliation

já congelados no Study2-A.

============================================================
6. SOURCE HASH GATE
============================================================

Antes de qualquer decode:

autenticar:

ESM1 =
4d07ee422e97661b1ee0ae681b7617fd7971476015603f3039c20ddf8b0c5c6d

ESM2 =
4eb1762dc4ee65c3e8b1411d80812a75257b1324d539db4c3dcf6c97c1ed9a0a

ESM4 =
9e6be3e78699d3bdd16fa71d56917479d7e16f7418b857ab3925e1115df91ebe

ESM5 =
c9054d18f330e018e82cc6bd4db2ccfbda7ac76e01326a831857a835d1feade6

Se qualquer hash divergir:

STOP.

============================================================
7. FRAME SYNCHRONIZATION
============================================================

Preservar correspondência:

ESM1 ↔ ESM2 ↔ ESM3
mesmo frame_index

ESM4 ↔ ESM5 ↔ ESM6
mesmo frame_index.

Não estimar novo offset temporal.

Não reexecutar G2.

Usar os mappings históricos certificados.

============================================================
8. COORDENADA CANÔNICA
============================================================

Cada site possui:

CANONICAL_CENTER_X
CANONICAL_CENTER_Y.

Esse centro é a coordenada usada em TODOS os frames
daquele site.

Não usar centro gráfico variável de cada observação
para mover o patch.

Objetivo:

evitar jitter de label/annotation.

============================================================
9. PATCH
============================================================

Congelar:

PATCH_RADIUS=32

PATCH_SIDE=65

Slicing correto:

[y-32:y+33,
 x-32:x+33]

Para cada site×frame elegível:

extrair:

STRUCTURAL patch 65×65 uint8

SOLUTAL patch 65×65 uint8

Ordem canônica:

channel 0 = STRUCTURAL_Y

channel 1 = RELATIVE_SOLUTE_FIELD_Y.

============================================================
10. SEMÂNTICA SOLUTAL
============================================================

ESM2/ESM5 permanecem:

RELATIVE_SOLUTE_FIELD.

Não chamar:

absolute Bi concentration.

Não derivar:

temperature.

Não converter valor de pixel em concentração física.

============================================================
11. STATUS DO CORPUS
============================================================

Preservar quatro grandes tiers:

TIER_GOLD:

observation_state =
DIRECT_VALID

TIER_SILVER:

observation_state =
TEMPORAL_SUPPORTED_AMBIGUOUS

TIER_UNLABELED_PRE:

PRE_FIRST_CONFIDENT_ANNOTATION

TIER_UNLABELED_PERSISTENCE:

PERSISTENCE_EXPECTED_UNRESOLVED.

Não colapsar esses tiers nesta fase.

============================================================
12. GOLD
============================================================

Esperado historicamente:

7941 registros.

Cada GOLD deve possuir:

site_id
acquisition_id
frame_index
experimental_time_s
canonical_center
structural source
solute source
patch coordinates
structural patch hash
solute patch hash
pair hash
provenance.

Se suporte inválido:

não substituir.

Registrar:

GOLD_INVALID_SUPPORT.

============================================================
13. SILVER
============================================================

Esperado historicamente:

5737 registros.

Materializar patches da mesma maneira,
mas manter:

SUPERVISION_TIER=SILVER.

Não promover para GOLD.

Não usar ainda para treinamento.

============================================================
14. UNLABELED LONGITUDINAL
============================================================

Materializar também, se suporte válido:

8911 PRE_FIRST

e

4807 PERSISTENCE_EXPECTED.

Esses patches formam:

LONGITUDINAL_UNLABELED_CORPUS.

Eles NÃO são:

NEGATIVE.

Eles NÃO são:

BACKGROUND.

Eles NÃO entram automaticamente
em supervised training.

============================================================
15. EXPECTED SITE-FRAME TOTAL
============================================================

Study2-A possui:

27396 site×frame records.

Study2-B deve contabilizar todos.

Para cada um produzir exatamente um:

PAIR_STATUS:

VALID_PAIR

INVALID_STRUCTURAL_SUPPORT

INVALID_SOLUTAL_SUPPORT

INVALID_BOTH

DECODE_ERROR.

Nenhum registro pode desaparecer.

============================================================
16. SUPPORT GUARDS
============================================================

Reutilizar os guards geométricos/cromáticos históricos
quando aplicáveis.

Como as dimensões anotadas e científicas não são idênticas,
qualquer patch que ultrapasse o suporte científico deve:

FAIL-CLOSED.

Não:

padding;
resize;
shift center;
crop asymmetric;
replace site/frame.

Registrar explicitamente exclusões.

============================================================
17. REGISTRATION
============================================================

Usar somente:

G2_FRAG histórico
+
G2_SOLUTE histórico.

Nenhum novo:

registration;
offset search;
optical flow;
feature matching;
SIFT;
ORB;
SS8 tuning;
NGF tuning.

Se um par não puder ser materializado
sob os mappings certificados:

INVALID_PAIR.

============================================================
18. STORAGE ARCHITECTURE
============================================================

Usar:

HYBRID_STREAM_LEDGER_SELECTIVE_CACHE.

Streaming dos quatro MP4.

Não exportar full frames.

Não criar PNG/JPEG por frame.

Patches válidos podem ser persistidos
como corpus agregado.

MAX_PATCH_CACHE_BYTES=
2147483648

MAX_TEMP_BYTES=
268435456

MIN_FREE_DISK_RESERVE_BYTES=
53687091200

============================================================
19. FORMATO DO CORPUS
============================================================

Evitar:

um arquivo por patch.

Preferir containers agregados.

Recomendação:

data/derived/study2b/

multimodal_patches_uint8.npy
ou formato equivalente determinístico
e memory-mappable

+
corpus-index.jsonl

O array deve armazenar:

N × 2 × 65 × 65

dtype:

uint8.

Não persistir float32.

Se usar formato diferente:

justificar e registrar.

============================================================
20. ARRAY ORDER
============================================================

Ordem determinística:

acquisition_id
site_id
frame_index
supervision_tier

ou outra ordem explicitamente congelada.

Cada linha do index deve possuir:

row_index

para mapear exatamente:

metadata → tensor row.

Não depender da ordem de filesystem.

============================================================
21. HASHES
============================================================

Para cada patch registrar:

structural_patch_sha256
solute_patch_sha256.

Para cada par registrar:

pair_sha256.

Também registrar:

container SHA256
index SHA256.

Não usar hash como feature.

============================================================
22. SITE GROUP
============================================================

Definir:

GROUP_ID =
acquisition_id + "|" + site_id

Todos os registros daquele site
compartilham GROUP_ID.

GROUP_ID deve ser imutável.

Futuro Study2-C é obrigado a manter
GROUP_ID integral em um split.

============================================================
23. WEIGHTING METADATA
============================================================

Como sites possuem 1–309 observações diretas,
calcular apenas metadados prospectivos:

site_observation_count

e:

candidate_equal_site_weight =
1 / number_of_supervised_observations_for_site

Não aplicar peso a modelo.

Apenas disponibilizar para Study2-C.

============================================================
24. BACKGROUND POOL
============================================================

Construir um pool de BACKGROUND_CANDIDATE
sem materializar pixels.

Usar grid espacial determinístico.

Cada candidato deve ser frame×location.

Excluir qualquer candidato cujo patch/safety area
intersecte:

- qualquer AUTO_GOLD site;
- qualquer known-site temporal footprint;
- qualquer AMBIGUOUS component bbox;
- qualquer SMALL component bbox;
- qualquer unresolved-site hypothesis component;
- qualquer support-invalid region;
- text/overlay/border exclusion histórica.

============================================================
25. FUTURE POSITIVE EXCLUSION
============================================================

Muito importante:

uma região que em frame t ainda não possui marcador,
mas em qualquer frame futuro pertence a um
AUTO_GOLD site,

NÃO pode entrar no background pool.

Isso evita:

pre-fragmentation / pre-annotation
→ falsamente rotulado como background.

Usar união espacial global por aquisição
dos 87 sites.

============================================================
26. AMBIGUITY EXCLUSION
============================================================

Usar:

AMBIGUOUS_COMPONENTS_TOTAL=24246

SMALL_COMPONENTS_TOTAL=292

como regiões de exclusão documental.

Não usar o campo histórico:

potential_new_site_unresolved_components

para decidir background.

Consumir somente os nomes canônicos
da reconciliação.

============================================================
27. BACKGROUND TRACK ID
============================================================

Cada posição espacial candidata deve receber:

BACKGROUND_TRACK_ID =
acquisition_id
+
grid_x
+
grid_y.

O mesmo local em frames diferentes
permanece no mesmo grupo.

Futuro split não pode colocar
o mesmo BACKGROUND_TRACK_ID
em TRAIN e TEST.

============================================================
28. BACKGROUND METADATA ONLY
============================================================

Não materializar todos os patches backgrounds.

Registrar:

frame_index
center_x
center_y
patch bounds
background_track_id
hash rank
exclusion distances/status.

Pixels serão materializados somente
depois da seleção no Study2-C.

============================================================
29. NÃO BALANCEAR
============================================================

Não selecionar:

1:1
2:1
etc.

Study2-B constrói o POOL.

Study2-C decidirá a estratégia de amostragem
antes de qualquer benchmark.

============================================================
30. CORPUS VIEWS
============================================================

Gerar manifests lógicos, SEM ML:

GOLD_VIEW

= somente DIRECT_VALID válidos.

GOLD_PLUS_SILVER_VIEW

= DIRECT_VALID
+
TEMPORAL_SUPPORTED_AMBIGUOUS válidos.

UNLABELED_VIEW

= PRE_FIRST
+
PERSISTENCE_EXPECTED.

FULL_LONGITUDINAL_VIEW

= todos os pares válidos.

Não duplicar pixels entre views.

Views contêm somente row indices.

============================================================
31. QUALITY METRICS
============================================================

Study2-B não usa accuracy.

Reportar:

PAIR_COVERAGE

GOLD_PAIR_COVERAGE

SILVER_PAIR_COVERAGE

UNLABELED_PAIR_COVERAGE

VALID_PAIR_COUNT

INVALID_PAIR_COUNT

VALID_SITE_COUNT

SITES_WITH_COMPLETE_TRAJECTORY

STRUCTURAL_HASH_COMPLETENESS

SOLUTAL_HASH_COMPLETENESS

PAIR_HASH_COMPLETENESS

BACKGROUND_POOL_SIZE

BACKGROUND_TRACK_COUNT

PROVENANCE_COMPLETENESS

STORAGE_BYTES

TEMP_BYTES

PEAK_RSS.

============================================================
32. NÃO DEFINIR PASS POR QUANTIDADE
============================================================

Não exigir:

> X mil patches.

O resultado real é científico.

PASS significa:

- corpus integralmente contabilizado;
- mappings corretos;
- provenance completa;
- tiers preservados;
- storage guardrails cumpridos;
- nenhuma classificação ML.

============================================================
33. HISTORICAL CONSISTENCY
============================================================

Para os 50 TRAIN/DEV pares históricos
do Estudo 1 já materializados anteriormente:

quando os mesmos site/frame/center existirem
no novo corpus,

exigir hashes idênticos.

Isso funciona como compatibility gate
para ESM1/2/4/5.

Não reexecutar modelos.

Registrar:

LEGACY_PATCH_PAIRS_EXPECTED

LEGACY_PATCH_PAIRS_MATCHED

LEGACY_PATCH_PAIR_HASH_MATCHES.

Se houver divergência:

BLOCKED_LEGACY_PAIR_REPRODUCTION.

============================================================
34. TESTES ANTES DOS PIXELS INÉDITOS
============================================================

Testar sinteticamente:

- canonical center fixed;
- patch 65×65;
- paired modalities;
- index↔array row mapping;
- tier preservation;
- site group;
- background track;
- future-positive exclusion;
- ambiguity exclusion;
- support failure;
- no padding;
- no center shift;
- deterministic ordering;
- no duplicate pair;
- no cross-source mixing;
- storage cap;
- no ML import/use;
- no ESM3/6 decode.

============================================================
35. LEGACY GATE
============================================================

Depois dos testes sintéticos:

usar somente os pares históricos
já previamente expostos

para confirmar reprodução.

Se PASS:

congelar método.

Se FAIL:

STOP.

Não acessar todos os frames.

============================================================
36. METHOD FREEZE
============================================================

Criar:

STUDY2_B_PROTOCOL.md
STUDY2_B_CORPUS_SCHEMA.json
STUDY2_B_BACKGROUND_CONTRACT.md
STUDY2_B_STORAGE_CONTRACT.md
STUDY2_B_CLAIM_SCOPE.md

e código/testes.

Commit sugerido:

feat(study2b): freeze dense multimodal corpus protocol

Registrar:

STUDY2_B_METHOD_FREEZE_SHA.

============================================================
37. CI PRÉ-EXECUÇÃO
============================================================

Push.

Exigir:

todos os workflows históricos
+
Study2-A synthetic
+
Study2-B synthetic

SUCCESS.

CI não depende dos vídeos locais.

Se qualquer falha:

STOP.

============================================================
38. EXECUÇÃO CIENTÍFICA
============================================================

Depois de freeze + CI verde:

executar exatamente UMA construção integral.

SCIENTIFIC_STUDY2B_RUNS=1.

Streams esperados:

ESM1
ESM2
ESM4
ESM5.

Não abrir:

ESM3
ESM6.

Nenhum ML.

Nenhum tuning.

Nenhum retry por resultado científico.

============================================================
39. DISCO
============================================================

Antes da execução:

verificar free disk.

Durante:

monitorar orçamento.

Depois:

reportar:

CORPUS_CONTAINER_BYTES

CORPUS_INDEX_BYTES

BACKGROUND_LEDGER_BYTES

TEMP_PEAK_BYTES

FREE_DISK_AFTER.

Se:

free disk < 50 GiB

STOP.

============================================================
40. RESULTADOS ESPERADOS COMO CONTAGENS
============================================================

Não impor valores,
mas reportar:

SITE_FRAME_INPUT_RECORDS=27396

VALID_MULTIMODAL_PAIRS=<real>

INVALID_MULTIMODAL_PAIRS=<real>

GOLD_VALID_PAIRS=<real>

SILVER_VALID_PAIRS=<real>

UNLABELED_VALID_PAIRS=<real>

UNIQUE_SITES_WITH_VALID_PAIRS=<real>

BACKGROUND_CANDIDATES=<real>

BACKGROUND_TRACKS=<real>

============================================================
41. NÃO TREINAR
============================================================

ML_RUNS=0

Não importar/usar para ciência:

sklearn classifier
SVM
LogisticRegression
RandomForestClassifier
torch training.

Feature extraction também fica para Study2-C,
salvo hashes/integridade de patches.

Não calcular LBP nesta fase.

============================================================
42. CLAIMS
============================================================

Permitido:

"dense longitudinal multimodal corpus"

"paired structural and relative-solute patches"

"automatic annotation-derived supervision tiers"

"group-aware corpus"

Proibido:

"independent samples"

"external validation"

"physical event inventory"

"exact onset"

"causal solute effect"

"forecasting".

============================================================
43. HUMAN REVIEW
============================================================

HUMAN_REVIEW_USED=false.

Não abrir imagens manualmente.

Não corrigir site.

Não editar center.

Não remover sample por aparência.

Support failure é determinado por regra congelada.

============================================================
44. OUTPUTS
============================================================

Versionar somente:

protocolos
schema
summary
manifests
hashes
quality reports
terminal state.

Manter grandes arrays/corpus localmente,
ignorados pelo Git.

Registrar:

path
size
record_count
sha256

em manifesto versionado.

============================================================
45. POST-RUN
============================================================

Depois da ciência:

evidence-only.

Não alterar:

code
schema
centers
tiers
background rules
storage rules.

Criar checkpoint documental.

============================================================
46. TERMINAL
============================================================

Ao concluir:

STUDY2_B=PASS

STUDY2_B_METHOD=
DENSE_MULTIMODAL_LONGITUDINAL_CORPUS

SCIENTIFIC_STUDY2B_RUNS=1

SITE_FRAME_INPUT_RECORDS=27396

VALID_MULTIMODAL_PAIRS=<real>

GOLD_VALID_PAIRS=<real>

SILVER_VALID_PAIRS=<real>

UNLABELED_VALID_PAIRS=<real>

INVALID_MULTIMODAL_PAIRS=<real>

UNIQUE_SITES_WITH_VALID_PAIRS=<real>

BACKGROUND_CANDIDATES=<real>

BACKGROUND_TRACKS=<real>

HUMAN_REVIEW_USED=false

ML_RUNS=0

STUDY2_C_READY_FOR_AUTHOR_DECISION=true

STUDY2_C_AUTHORIZED=false

CURRENT_AUTHORIZED_ACTIVITY=
NONE_AWAITING_AUTHOR_DECISION

============================================================
47. REPORT AO OPERADOR
============================================================

Informar:

1. Study2-A PR/merge;
2. Study2-A merge SHA;
3. post-merge CI;
4. Study2-B branch;
5. source hashes;
6. corpus schema;
7. background contract;
8. storage contract;
9. legacy compatibility gate;
10. freeze SHA;
11. CI pré-execução;
12. run command;
13. source opens/bytes;
14. 27396 accounting;
15. valid pair count;
16. invalid support;
17. GOLD count;
18. SILVER count;
19. UNLABELED count;
20. site count;
21. background candidate count;
22. background track count;
23. future-positive exclusion;
24. ambiguity exclusion;
25. container size/hash;
26. index size/hash;
27. storage peak/free;
28. human review;
29. ML confirmation;
30. evidence checkpoint;
31. final CI;
32. Git state;
33. terminal state.

STOP.

NÃO INICIAR STUDY2-C.
NÃO TREINAR MODELOS.