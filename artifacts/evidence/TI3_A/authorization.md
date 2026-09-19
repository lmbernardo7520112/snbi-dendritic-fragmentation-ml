# TI3-A — CANONICAL ML DATASET + LEAKAGE-SAFE SPLIT + BASELINE
# + CURRICULAR ALIGNMENT WITH TRILHA 2 IMAGE-PREPROCESSING CONTENT
# Início controlado da fase de modelagem
# DDD + SDD + evidence-first + bounded experimentation + convergence governance

Repositório:
snbi-dendritic-fragmentation-ml

============================================================
BASELINE CANÔNICA
============================================================

A baseline integrada é:

main remote:
67786bd4e23406e7f19860a53fe237e6d7b648cb

Estado científico encerrado:

TI2R_SOLUTE=COMPLETE
G2_SOLUTE=PASS
HOLDOUT_SOLUTE=CONSUMED
SOLUTAL_INTERNAL_VALIDATION=PASS
SOLUTAL_EXTERNAL_GENERALIZATION=NOT_CLAIMED
PR_10=MERGED
POST_MERGE_CI=PASS

Os 25 arquivos científicos de TI2R permanecem congelados.

G2_SOLUTE NÃO deve ser reaberto.

============================================================
CONTEXTO CURRICULAR — NÃO CONFUNDIR COM AUTORIZAÇÃO CIENTÍFICA
============================================================

A Trilha 2 da especialização em IA apresentou notebooks de visão
computacional e pré-processamento contendo, entre outras técnicas:

A4:
- SIFT;
- ORB;
- FAST;
- BRIEF;
- LBP;
- matching de descritores;
- combinação de características;
- Random Forest.

A5:
- thresholding;
- threshold adaptativo;
- Otsu;
- Gaussian Blur;
- Sobel;
- Laplaciano;
- Canny;
- magnitude/orientação de gradiente;
- contornos;
- Hough;
- CNN simples;
- feature maps;
- t-SNE;
- matriz de confusão.

O projeto científico atual já emprega conceitos diretamente relacionados
a esse conteúdo:

1. Sobel / gradientes
   ->
   gradientes gx/gy utilizados pelo componente NGF;

2. descritores locais / representação estrutural
   ->
   descritor SS8 de auto-similaridade local;

3. literatura científica de registro multimodal
   ->
   NGF e princípios de self-similarity relacionados conceitualmente
   aos trabalhos:

   "Intensity gradient based registration and fusion of multi-modal images"

   e

   "MIND: modality independent neighbourhood descriptor for
   multi-modal deformable registration".

IMPORTANTE:

O SS8 atual NÃO deve ser declarado como implementação exata de MIND ou
MIND-SSC.

Usar formulações como:

"local self-similarity descriptor inspired by the modality-independent
self-similarity principle"

ou equivalente tecnicamente correto.

============================================================
MISSÃO
============================================================

Iniciar TI3 de forma convergente.

Esta autorização deve:

1. sincronizar a baseline local com a main remota integrada;
2. criar uma nova branch específica para TI3-A;
3. definir formalmente a unidade amostral do problema de ML;
4. construir/inventariar o dataset canônico;
5. definir splits TRAIN/DEVELOPMENT/FINAL_TEST protegidos contra leakage;
6. congelar métricas antes dos experimentos;
7. implementar UM baseline simples e adequado à tarefa;
8. executar apenas TRAIN/DEVELOPMENT;
9. manter FINAL_TEST lacrado;
10. produzir evidência para a decisão sobre o modelo principal;
11. mapear de forma tecnicamente honesta quais conteúdos A4/A5
    são pertinentes ao problema;
12. preparar evidência reutilizável no notebook final da Trilha 2;
13. parar.

============================================================
REGRA CENTRAL DE ALINHAMENTO CURRICULAR
============================================================

NÃO introduzir uma técnica porque ela apareceu no curso.

A ordem obrigatória é:

PROBLEMA CIENTÍFICO
        ↓
REQUISITO DO DADO/TARGET
        ↓
TÉCNICA ADEQUADA
        ↓
eventual correspondência com conteúdo da disciplina

É proibida a lógica inversa:

"Técnica foi ensinada"
        ↓
"precisamos colocá-la em algum lugar".

Cada técnica A4/A5 deve receber uma decisão explícita:

USED_ALREADY
USEFUL_FOR_TI3
OPTIONAL_EXPLORATORY
NOT_APPROPRIATE_FOR_CURRENT_TASK

com justificativa técnica.

============================================================
TÉCNICAS JÁ INCORPORADAS — SOMENTE DOCUMENTAR
============================================================

Não alterar G2_SOLUTE.

Documentar apenas a relação conceitual existente:

A5 Sobel
   ↓
gx / gy
   ↓
normalização
   ↓
NGF
   ↓
registro/auditoria multimodal já validado.

Também documentar:

A4 conceito de descritores/características locais
   ↓
representações estruturais
   ↓
self-similarity
   ↓
SS8 utilizado no projeto.

Isso é ALINHAMENTO DIDÁTICO.

NÃO é autorização para modificar os kernels já validados.

============================================================
TÉCNICAS QUE NÃO DEVEM SER INTRODUZIDAS NO REGISTRO VALIDADO
============================================================

Não substituir ou complementar G2_SOLUTE agora com:

- SIFT;
- ORB;
- FAST;
- BRIEF;
- Canny;
- Otsu;
- LBP;
- Hough;
- novas métricas de registro.

Não executar:

SS8 vs SIFT
NGF vs Canny
MIND vs ORB
ou qualquer benchmark retrospectivo semelhante.

G2_SOLUTE está CLOSED.

============================================================
FASE 0 — SINCRONIZAÇÃO E ISOLAMENTO
============================================================

O clone pode ainda estar em:

feat/ti2r-solute-v2-calibration

e a main local pode estar desatualizada.

Antes de desenvolver:

1. confirmar worktree/index limpos;
2. fetch do remoto;
3. verificar remote main =
   67786bd4e23406e7f19860a53fe237e6d7b648cb;
4. sincronizar main local por fast-forward;
5. criar nova branch exatamente dessa baseline.

Nome sugerido:

feat/ti3-canonical-dataset-baseline

Não desenvolver TI3 na branch TI2R.

============================================================
FASE 1 — APROPRIAÇÃO DO DOMÍNIO
============================================================

Inspecione o repositório e determine com evidência:

- modalidades disponíveis;
- dimensões;
- frame numbering;
- timestamps;
- relações ESM1/2/3 e ESM4/5/6;
- annotations/labels;
- artefatos G2_FRAG;
- artefatos G2_SOLUTE;
- transformações existentes;
- inputs potenciais;
- targets;
- frames com labels;
- agrupamentos experimentais.

Preservar:

ESM1 / ESM4:
radiografia / informação estrutural;

ESM2 / ESM5:
campo solutal relativo;

ESM3 / ESM6:
informação/anotação de fragmentação conforme contratos existentes.

NÃO reinterpretar ESM2/ESM5 como concentração absoluta de Bi.

============================================================
FASE 2 — DEFINIR A UNIDADE AMOSTRAL
============================================================

Formalizar:

WHAT_IS_ONE_SAMPLE

Possibilidades incluem:

- frame;
- patch;
- evento;
- par temporal;
- outra unidade sustentada pelos dados.

Não escolher arbitrariamente.

Derivar de:

1. objetivo científico;
2. natureza dos labels;
3. resolução espacial;
4. estrutura temporal;
5. tarefa de ML.

Registrar:

INPUT
TARGET
GROUP_ID
TIME_ID
ACQUISITION_ID

quando aplicável.

============================================================
FASE 3 — LEAKAGE THREAT MODEL
============================================================

Produzir threat model específico de leakage.

Avaliar:

- frames adjacentes;
- mesma aquisição;
- patches do mesmo frame;
- augmentations do mesmo original;
- versões registradas;
- uso de informação futura;
- annotations derivadas do target;
- solutal do mesmo evento;
- metadados que codifiquem label.

Dados fortemente correlacionados da mesma unidade física não podem ser
separados ingenuamente entre TRAIN/DEV/FINAL_TEST.

O split deve ser GROUP-AWARE e TIME-AWARE quando necessário.

============================================================
FASE 4 — DATASET CANÔNICO
============================================================

Construir manifesto reproduzível.

Preferir CSV/JSON/Parquet com metadados, sem duplicação desnecessária
das imagens.

Cada sample deve incluir conforme aplicável:

sample_id
acquisition_id
frame_id
timestamp
input_structural
input_solutal
target
group_id
split
provenance

Registrar hashes/identificadores fortes.

Gerar:

- número de samples;
- distribuição dos labels;
- distribuição temporal;
- distribuição por aquisição;
- dados ausentes;
- exclusões;
- motivos.

Nenhuma exclusão pode depender do desempenho posterior do modelo.

============================================================
FASE 5 — SPLIT CONGELADO
============================================================

Definir:

TRAIN
DEVELOPMENT
FINAL_TEST

FINAL_TEST permanece lacrado.

Split determinístico.

Registrar:

- seed;
- regras de agrupamento;
- regra temporal;
- hashes;
- IDs por split.

Criar guards:

TRAIN ∩ DEV = ∅
TRAIN ∩ FINAL_TEST = ∅
DEV ∩ FINAL_TEST = ∅

e também por:

group
acquisition
time-neighborhood

quando aplicável.

============================================================
FASE 6 — DEFINIR TAREFA E MÉTRICAS
============================================================

Determinar a tarefa a partir do target real:

- classificação;
- detecção;
- segmentação;
- regressão;
- outra.

NÃO force classificação se o target for espacial.

Definir antes do treinamento:

PRIMARY_METRIC
SECONDARY_METRICS
ERROR_ANALYSIS_METRICS

Não mudar métrica após observar desempenho.

============================================================
FASE 7 — DELIBERAÇÃO CURRICULAR FORMAL
============================================================

Antes de escolher o baseline, gerar:

artifacts/evidence/TI3_A/COURSE_ALIGNMENT.md

O documento deve conter uma matriz semelhante a:

Technique
Source_Notebook
Already_Used
Potential_TI3_Use
Decision
Technical_Rationale

Avaliar explicitamente:

Sobel
gradient magnitude/orientation
Gaussian Blur
Canny
Laplacian
global threshold
adaptive threshold
Otsu
SIFT
ORB
FAST
BRIEF
LBP
Random Forest
simple CNN
feature maps
t-SNE
confusion matrix
contours
Hough

Não basta marcar "useful".

Justificar com base na tarefa real.

============================================================
DECISÃO ESPECIAL — LBP + RANDOM FOREST
============================================================

Avaliar LBP + Random Forest como candidato a baseline clássico SOMENTE SE:

- a unidade amostral for patch/frame compatível;
- o target for classificatório ou agregável sem destruir a informação espacial;
- a representação textural tiver sentido físico;
- não houver leakage;
- não exigir redesign artificial do problema.

Se essas condições forem satisfeitas:

é permitido escolher:

LBP + Random Forest

como UM baseline clássico.

Se não forem satisfeitas:

registrar:

LBP_RF_BASELINE=REJECTED_AS_TASK_INCOMPATIBLE

e seguir com outro baseline simples.

A rejeição não é falha.

============================================================
DECISÃO ESPECIAL — CNN DO CURSO
============================================================

A CNN simples do A5 pode servir como referência pedagógica.

Não copiar cegamente arquitetura de FashionMNIST.

Se a tarefa for compatível, adaptar somente os princípios:

- convolução;
- pooling;
- representação aprendida;
- classificação/saída apropriada.

A arquitetura concreta deve respeitar:

- resolução;
- número de canais;
- target;
- tamanho do dataset;
- risco de overfitting.

============================================================
DECISÃO ESPECIAL — CANNY
============================================================

Canny NÃO é entrada obrigatória.

Não substituir imagem científica original por edge map sem justificativa.

Canny pode ser classificado como:

OPTIONAL_EXPLORATORY

ou

NOT_APPROPRIATE_FOR_CURRENT_TASK.

Só usar se houver hipótese clara e benefício metodológico.

============================================================
DECISÃO ESPECIAL — SIFT / ORB
============================================================

Não introduzir SIFT/ORB no registro multimodal já validado.

Podem ser mencionados como descritores clássicos abordados no curso.

Somente considerar como baseline ML se a tarefa real exigir
keypoint-based representation e houver justificativa clara.

Caso contrário:

NOT_APPROPRIATE_FOR_CURRENT_TASK.

============================================================
DECISÃO ESPECIAL — t-SNE
============================================================

t-SNE pode ser preparado apenas como visualização exploratória futura
do espaço latente.

Não usar como:

- métrica;
- evidência de generalização;
- critério de escolha de modelo;
- substituto de avaliação quantitativa.

============================================================
DECISÃO ESPECIAL — MATRIZ DE CONFUSÃO
============================================================

Se a tarefa for classificatória:

planejar matriz de confusão para DEVELOPMENT e posteriormente FINAL_TEST.

Ela deverá complementar, não substituir, as métricas congeladas.

Se a tarefa não for classificatória:

registrar explicitamente que não se aplica.

============================================================
FASE 8 — BASELINE
============================================================

Implementar UM baseline simples.

A escolha deve ser condicionada pela tarefa.

Possibilidades legítimas incluem:

A)
LBP + Random Forest
se a tarefa for classificatória e compatível com features texturais;

B)
CNN pequena
se representação espacial aprendida for mais apropriada;

C)
baseline simples específico de segmentação/regressão/detecção
se a tarefa exigir.

Não implementar A + B + C em TI3-A.

Escolher UMA opção principal após a análise.

O objetivo do baseline é validar:

- loading;
- target;
- loss/fit;
- treinamento;
- avaliação;
- reprodutibilidade.

Não buscar SOTA.

============================================================
FASE 9 — ESTRUTURAL VS MULTIMODAL
============================================================

Preparar o pipeline para permitir posteriormente comparar:

A) estrutural:
radiografia

B) multimodal:
radiografia + campo solutal relativo

Mas NÃO executar architecture shopping nesta etapa.

A comparação futura deverá responder:

"O campo solutal relativo acrescenta informação preditiva mensurável
além da radiografia estrutural?"

============================================================
FASE 10 — EXECUÇÃO AUTORIZADA
============================================================

Autorizado:

TRAIN
+
DEVELOPMENT

Proibido:

FINAL_TEST

Permitir somente:

1. smoke test;
2. correções técnicas necessárias antes da execução científica válida;
3. UMA execução baseline válida.

Distinguir:

TECHNICAL_RUN
SCIENTIFIC_RUN

Após uma execução científica baseline válida:

STOP.

Não fazer tuning.

============================================================
FASE 11 — EVIDÊNCIA
============================================================

Criar:

artifacts/evidence/TI3_A/

incluindo:

DATASET_SPEC.md
dataset_manifest.*
SPLIT_PROTOCOL.md
LEAKAGE_THREAT_MODEL.md
COURSE_ALIGNMENT.md
MODEL_BASELINE_SPEC.md
execution-report.md
results.json
commands.json
environment.json

COURSE_ALIGNMENT.md deve ser reutilizável posteriormente para a
construção do notebook acadêmico da Trilha 2.

============================================================
CONEXÃO DIDÁTICA OBRIGATÓRIA PARA O FUTURO NOTEBOOK
============================================================

Registrar material que permita explicar futuramente:

1. Sobel ensinado no curso:
   imagem -> gx/gy;

2. extensão usada no projeto:
   gx/gy -> gradientes normalizados -> NGF;

3. descritores locais ensinados no curso:
   representação manual de estrutura/textura;

4. extensão usada no projeto:
   local self-similarity -> SS8;

5. literatura:
   NGF como método especializado de registro multimodal;
   MIND como referência de self-similarity multimodal;

6. distinção rigorosa:
   SS8 != MIND-SSC exato.

Não gerar afirmações de equivalência inexistentes.

============================================================
GATES
============================================================

Antes de encerrar:

[ ] branch nasceu da main 67786bd4...
[ ] TI2R não foi alterado
[ ] unidade amostral definida
[ ] dataset manifesto criado
[ ] provenance definida
[ ] threat model concluído
[ ] split determinístico
[ ] group/time leakage bloqueado
[ ] FINAL_TEST identificado
[ ] FINAL_TEST não aberto
[ ] métricas congeladas
[ ] COURSE_ALIGNMENT.md produzido
[ ] Sobel -> NGF documentado corretamente
[ ] descritores locais -> SS8 documentado corretamente
[ ] SS8 não chamado de MIND/MIND-SSC exato
[ ] LBP/RF deliberado, não imposto
[ ] Canny não imposto
[ ] SIFT/ORB não introduzidos no G2 validado
[ ] baseline executável
[ ] uma execução baseline válida
[ ] TRAIN/DEV registrados
[ ] zero uso de FINAL_TEST
[ ] CI aplicável verde
[ ] worktree/index controlados

============================================================
ANTI-REFINAMENTO
============================================================

NÃO:

- comparar várias CNNs;
- executar LBP/RF e CNN apenas para escolher o melhor;
- grid search amplo;
- random search;
- dezenas de seeds;
- alterar split por resultado;
- abrir FINAL_TEST;
- mudar PRIMARY_METRIC;
- reabrir G2_SOLUTE;
- trocar NGF;
- trocar SS8;
- inserir técnica por obrigação curricular.

TI3-A responde somente:

"Temos um dataset ML canônico, sem leakage conhecido,
um baseline end-to-end funcional e uma conexão curricular
tecnicamente legítima com o conteúdo da Trilha 2?"

============================================================
ESTADO FINAL ESPERADO
============================================================

Se concluído:

TI3_A_DATASET=PASS
TI3_A_SPLIT=FROZEN
TI3_A_LEAKAGE_GUARDS=PASS
TI3_A_CURRICULAR_ALIGNMENT=PASS
TI3_A_BASELINE=PASS
FINAL_TEST=SEALED
MODEL_SELECTION=NOT_STARTED
TI3_B_READY_FOR_AUTHOR_DECISION=true
TI3_B_AUTHORIZED=false
MERGE_AUTHORIZED=false
CURRENT_AUTHORIZED_ACTIVITY=NONE_AWAITING_AUTHOR_DECISION

Se houver bloqueio metodológico:

não improvisar workaround;
não abrir FINAL_TEST;
não alterar ciência anterior;
registrar bloqueio;
STOP.

============================================================
REPORT FINAL
============================================================

Fornecer:

1. branch e HEAD;
2. baseline de origem;
3. unidade amostral;
4. input;
5. target;
6. número de samples;
7. distribuição;
8. split;
9. política anti-leakage;
10. métricas congeladas;
11. matriz de alinhamento curricular;
12. técnicas A4/A5 aceitas;
13. técnicas A4/A5 rejeitadas;
14. justificativas;
15. decisão LBP/RF;
16. baseline escolhido;
17. parâmetros principais;
18. runs técnicos;
19. runs científicos;
20. resultados TRAIN/DEV;
21. confirmação FINAL_TEST=SEALED;
22. arquivos criados/modificados;
23. testes;
24. CI;
25. worktree/index;
26. próximos estados de autorização.

EXECUTE SOMENTE TI3-A.