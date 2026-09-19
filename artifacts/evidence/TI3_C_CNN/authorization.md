# TI3-B INTEGRATION + TI3-C MINIMAL MULTIMODAL CNN
#
# Objetivo:
# integrar TI3-B e executar UMA ÚNICA comparação de família de modelo
# usando a modalidade já escolhida no desenvolvimento:
#
# STRUCTURAL_PLUS_RELATIVE_SOLUTE
#
# Modelo candidato:
# CNN mínima inspirada nos fundamentos do notebook A5 da Trilha 2.
#
# NÃO abrir FINAL_TEST.
# NÃO fazer architecture search.
# NÃO fazer tuning.
# NÃO fazer data augmentation.
# NÃO mudar weak labels.
# NÃO mudar split.
# CONVERGÊNCIA OBRIGATÓRIA.

Repositório:
snbi-dendritic-fragmentation-ml

Branch TI3-B atual:
feat/ti3b-solutal-ablation

HEAD B2 esperado:
dc9d0bb467bfc3c94302bb59b91db296e788451e

============================================================
1. ESTADO CANÔNICO
============================================================

TI3_A_INTEGRATION=PASS

TI3_B=PASS

SOLUTAL_ABLATION=COMPLETED

SCIENTIFIC_TI3B_RUNS=1

DEV_MODALITY_PREFERENCE=
STRUCTURAL_PLUS_RELATIVE_SOLUTE

Referências consumidas:

STRUCTURAL_LBP_RF_DEV_BA=
0.6875

MULTIMODAL_LBP_RF_DEV_BA=
0.75

MULTIMODAL DEV confusion:

TN=4
FP=4
FN=0
TP=8

TARGET:

PUBLISHED_FRAGMENTATION_LOCATION_PRESENT

WEAK_LABEL_STRATEGY=
HIGH_CONFIDENCE_PLUS_IGNORE

FINAL:

ML_FINAL_TEST=
SEALED_WITH_HISTORICAL_NON_ML_EXPOSURE

ML_FINAL_TEST_EXECUTED=false

============================================================
2. INTERPRETAÇÃO CONGELADA DE TI3-B
============================================================

O ganho multimodal foi:

+0.0625 balanced accuracy

equivalente a:

um BACKGROUND_CANDIDATE adicional corretamente
classificado no DEVELOPMENT.

Não interpretar como:

- significância estatística;
- causalidade;
- forecasting;
- generalização externa;
- prova de relevância física universal do soluto.

A preferência multimodal serve exclusivamente
para a próxima fase de desenvolvimento.

============================================================
PART I — INTEGRAÇÃO TI3-B
============================================================

3. AUDITORIA PRÉ-MERGE

Confirmar:

- HEAD local = B2;
- branch remota = B2;
- worktree/index limpos;
- B2 evidence-only;
- B1 freeze intacto;
- nenhum pixel aberto após B1 fora da única execução;
- FINAL estrutural = 0 opens/bytes;
- FINAL solutal = 0 opens/bytes;
- CI final totalmente verde.

Se divergir:

STOP.

============================================================
4. PR TI3-B

Se ainda não existir PR:

criar Draft PR contra main.

Descrever:

- objetivo da ablação;
- structural reference;
- multimodal result;
- delta +0.0625;
- TN4/FP4/FN0/TP8;
- preferência DEV multimodal;
- interpretação restrita;
- FINAL intacto.

============================================================
5. CI + MERGE TI3-B

Exigir CI completamente verde.

Se PASS:

Ready
+
merge commit.

Não squash.

Registrar:

TI3_B_MERGE_SHA.

Exigir CI pós-merge totalmente verde.

Se falhar:

STOP.

Não iniciar CNN.

============================================================
PART II — TI3-C
============================================================

Somente se integração TI3-B estiver completamente verde.

============================================================
6. NOVA BRANCH

Fast-forward local main.

Criar:

feat/ti3c-minimal-multimodal-cnn

a partir exatamente do TI3_B_MERGE_SHA.

============================================================
7. QUESTÃO CIENTÍFICA

TI3-C responde somente:

“Uma CNN mínima, usando as mesmas modalidades multimodais
já escolhidas em DEVELOPMENT, apresenta balanced accuracy
superior ao LBP/RF multimodal congelado?”

Nada além disso.

============================================================
8. CONEXÃO CURRICULAR

O notebook A5 da Trilha 2 utiliza PyTorch e apresenta:

- Conv2d;
- ReLU;
- MaxPool;
- camada linear;
- CrossEntropyLoss;
- Adam;
- seed 42;
- treinamento em 10 épocas.

TI3-C deve reutilizar esses FUNDAMENTOS.

Não copiar literalmente a escala do modelo FashionMNIST,
porque o dataset atual possui somente 34 exemplos TRAIN.

============================================================
9. FRAMEWORK

Usar PyTorch CPU.

Versão congelada:

torch==2.4.1+cpu

Python:
3.12

A distribuição oficial possui wheel CPU para CPython 3.12.

Não instalar torchvision.

Não instalar torchaudio.

Não usar CUDA.

Criar configuração/requisitos TI3-C explícitos.

Instalação deve ocorrer apenas em ambiente virtual local
e em job CI dedicado.

============================================================
10. GOVERNANÇA DE DEPENDÊNCIAS

TI3-C pode ampliar a allowlist apenas para:

torch

nos paths TI3-C explicitamente enumerados.

Não liberar torch globalmente.

Não modificar LEGACY_TI2.

Não modificar TI3_A0_FROZEN.

Não permitir:

tensorflow
keras
xgboost
lightgbm
transformers
fastai

nesta fase.

============================================================
11. INPUT

Usar exatamente os mesmos samples TRAIN/DEV de TI3-B.

Input shape:

2 × 65 × 65

Canal 0:

STRUCTURAL_LUMINANCE
ESM1 ou ESM4

Canal 1:

RELATIVE_SOLUTE_FIELD_LUMINANCE
ESM2 ou ESM5

Mesmos:

- centers;
- patch coordinates;
- labels;
- split;
- context groups;
- backgrounds.

Nenhum sample pode ser trocado.

============================================================
12. NORMALIZAÇÃO

Cada canal uint8 Y:

x_float = x / 255.0

Não calcular:

- mean DEV;
- std DEV;
- normalization statistics globais;
- histogram equalization;
- CLAHE.

Não aprender normalização.

============================================================
13. SEM CANNY

Não aplicar:

Canny;
GaussianBlur;
Sobel como novo canal;
thresholding;
edge maps.

Razão:

preservar intensidade/textura estrutural e solutal.

Canny permanece conteúdo curricular discutido,
mas conscientemente não utilizado como input científico.

============================================================
14. SEM AUGMENTATION

DATA_AUGMENTATION=NONE

Não aplicar:

- flip;
- rotation;
- crop aleatório;
- elastic deformation;
- color jitter;
- noise augmentation.

Razão:

invariância física/orientacional não demonstrada
e amostra extremamente pequena.

============================================================
15. ARQUITETURA CONGELADA

Implementar exatamente:

class MinimalMultimodalCNN(nn.Module):

Input:
2 × 65 × 65

Layer 1:
Conv2d(
    in_channels=2,
    out_channels=8,
    kernel_size=3,
    padding=1
)

ReLU

MaxPool2d(
    kernel_size=2,
    stride=2
)

AdaptiveAvgPool2d((1,1))

Flatten

Linear(
    in_features=8,
    out_features=2
)

Sem:

- segunda convolution;
- batch normalization;
- dropout;
- residual block;
- attention;
- pretrained backbone.

Parâmetros treináveis esperados:

170.

Verificar automaticamente a contagem.

Se != 170:

BLOCKED_ARCHITECTURE_DIVERGENCE

STOP.

============================================================
16. TREINAMENTO CONGELADO

Seeds:

Python = 42
NumPy = 42
PyTorch = 42

CPU only.

torch.use_deterministic_algorithms(True)

num_workers=0

torch.set_num_threads(1)

Loss:

CrossEntropyLoss()

Optimizer:

Adam(
    lr=0.005
)

Epochs:

10

Batch size:

8

DataLoader TRAIN:

shuffle=True

usar Generator PyTorch com seed42.

Nenhum early stopping.

Nenhum scheduler.

Nenhum weight decay.

Nenhum hyperparameter tuning.

============================================================
17. DEVELOPMENT

Não usar DEVELOPMENT durante treinamento.

Não:

- early stop por DEV;
- escolher época por DEV;
- mudar LR por DEV;
- mudar arquitetura por DEV.

Depois da décima época:

avaliar DEVELOPMENT exatamente uma vez.

============================================================
18. CONFONDER DIAGNOSTIC — METADATA ONLY

Antes dos pixels CNN, calcular e congelar um diagnóstico
não-ML baseado somente na aquisição.

Regra:

para cada aquisição, usar a classe majoritária em TRAIN
como previsão daquela aquisição.

Avaliar essa regra em DEVELOPMENT.

Esse diagnóstico serve apenas para quantificar
o possível confounding aquisição/classe.

Não usar seu resultado para mudar dataset, CNN ou split.

Registrar:

ACQUISITION_ONLY_DEV_BALANCED_ACCURACY

e confusion matrix.

============================================================
19. MÉTRICAS CNN

PRIMARY:

balanced_accuracy

SECONDARY:

accuracy
precision
recall
F1
confusion matrix

Também:

TP
FP
TN
FN

Threshold:

argmax dos dois logits.

Sem threshold tuning.

============================================================
20. REFERÊNCIA PARA SELEÇÃO

Referência congelada:

MULTIMODAL_LBP_RF_DEV_BA =
0.75

Regra definida ANTES dos pixels CNN:

se:

CNN_DEV_BALANCED_ACCURACY > 0.75

então:

FINAL_MODEL_FAMILY_PREFERENCE=
MINIMAL_MULTIMODAL_CNN

senão:

FINAL_MODEL_FAMILY_PREFERENCE=
MULTIMODAL_LBP_RF

Empate favorece LBP/RF.

Não considerar TRAIN score nessa decisão.

============================================================
21. TRAIN SCORE

Calcular TRAIN metrics apenas de forma descritiva.

TRAIN não decide modelo.

Se TRAIN=1.0 e DEV menor:

registrar possível overfit.

Não retreinar.

============================================================
22. DEPENDENCY / SYNTHETIC GATE

Antes de pixels:

- requirements/constrains congelados;
- torch import/version PASS;
- arquitetura parameter_count=170;
- forward shape synthetic PASS;
- deterministic repeated synthetic training PASS;
- guard contra FINAL access PASS;
- data guard PASS;
- phase scope PASS;
- legacy tests PASS;
- TI3 A/B regression PASS.

Criar C1-CNN freeze commit.

Mensagem sugerida:

feat(ti3c): freeze minimal multimodal cnn protocol

============================================================
23. CI PRÉ-PIXEL

Push C1-CNN.

Executar:

historical jobs
+
TI3 jobs
+
TI3-B jobs
+
TI3-C synthetic job.

Exigir todos SUCCESS.

Se qualquer CI falhar:

STOP.

Zero pixels.

============================================================
24. I/O AUTORIZADO

Somente após C1-CNN + CI verde:

abrir exatamente:

TRAIN structural:
ESM1:73
ESM1:146
ESM4:98

DEV structural:
ESM1:219
ESM4:197

TRAIN solutal:
ESM2:73
ESM2:146
ESM5:98

DEV solutal:
ESM2:219
ESM5:197

Nenhum outro buffer.

============================================================
25. FINAL PROIBIDO

Não abrir:

ESM1:293
ESM4:295
ESM2:293
ESM5:295

FINAL:

0 opens
0 bytes

obrigatório.

============================================================
26. UMA EXECUÇÃO CNN

SCIENTIFIC_TI3C_RUNS máximo:

1

Uma execução inclui:

- materializar TRAIN em memória;
- treinar 10 épocas;
- avaliar TRAIN descritivamente;
- avaliar DEV uma vez.

Sem retry.

Sem segunda seed.

Sem arquitetura alternativa.

============================================================
27. RESULTADO BAIXO É VÁLIDO

TI3_C=PASS significa:

CNN executada conforme protocolo.

Não significa:

CNN superior.

Se CNN_DEV_BA <= 0.75:

selecionar RF.

Não tentar melhorar CNN.

Isso encerra a comparação de família de modelo.

============================================================
28. EVIDÊNCIA

Registrar:

- environment;
- torch version;
- architecture;
- 170 parameters;
- seeds;
- loss per epoch;
- TRAIN metrics;
- DEV metrics;
- confusion matrix;
- probabilities/logits;
- acquisition-only diagnostic;
- reference RF;
- selection result;
- I/O;
- FINAL zero access.

Não exportar modelo binário se a política do repositório
não permitir.

Evidência textual apenas.

============================================================
29. CLAIMS

Permitido:

- comparison of model families on internal DEVELOPMENT;
- weak-label classification;
- development preference.

Proibido:

- external generalization;
- forecasting;
- causality;
- physical exhaustive fragmentation recall;
- exact onset;
- claim that CNN superiority is statistically established;
- claim that relative solute is absolute concentration.

============================================================
30. TERMINAL

Após a única execução:

TI3_C=PASS

SCIENTIFIC_TI3C_RUNS=1

MODEL_FAMILY_SELECTION=COMPLETE

FINAL_MODEL_FAMILY_PREFERENCE=
<MINIMAL_MULTIMODAL_CNN ou MULTIMODAL_LBP_RF>

ML_FINAL_TEST_EXECUTED=false

FORECASTING_AUTHORIZED=false

CAUSALITY_CLAIM_AUTHORIZED=false

EXTERNAL_GENERALIZATION_CLAIM=false

FINAL_EVALUATION_READY_FOR_AUTHOR_DECISION=true

FINAL_EVALUATION_AUTHORIZED=false

MERGE_AUTHORIZED=false

CURRENT_AUTHORIZED_ACTIVITY=
NONE_AWAITING_AUTHOR_DECISION

STOP.

============================================================
31. CONVERGÊNCIA

Não executar:

- segunda CNN;
- segunda seed;
- learning-rate search;
- epoch search;
- filter search;
- pretrained network;
- ResNet;
- EfficientNet;
- ViT;
- augmentation;
- Canny variant;
- structural-only CNN;
- solutal-only CNN.

Uma CNN.

Uma execução.

Uma decisão.

============================================================
32. REPORT FINAL

Informar:

1. PR/merge TI3-B;
2. merge SHA;
3. post-merge CI;
4. branch TI3-C;
5. dependency freeze;
6. torch version;
7. architecture;
8. parameter count;
9. C1-CNN SHA;
10. CI pré-pixel;
11. buffers opened;
12. bytes;
13. FINAL opens/bytes;
14. acquisition-only diagnostic;
15. epoch losses;
16. TRAIN metrics;
17. DEV metrics;
18. DEV confusion matrix;
19. RF reference BA;
20. CNN BA;
21. delta;
22. selected family;
23. scientific CNN runs;
24. evidence SHA;
25. terminal state.

EXECUTE SOMENTE:

TI3-B INTEGRATION
+
UMA MINIMAL MULTIMODAL CNN.

NUNCA ABRA ML_FINAL_TEST.