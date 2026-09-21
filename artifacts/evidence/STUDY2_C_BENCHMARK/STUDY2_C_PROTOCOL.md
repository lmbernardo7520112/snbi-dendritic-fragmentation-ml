# Study2-C — protocolo do benchmark agrupado

Autoridade: AUTHORIZATION.md, SHA-256 59405ea29a29039246e090e6fa5f72a580a7c183af0dbd1d324d341eb8b05450.
Base: merge Study2-B de7670bb8491d2ef01809b33aa326aa3a264324c, PR #17.
Branch: feat/study2c-group-aware-benchmark. Estudo 1 e Study2-A/B permanecem consumidos.

## Domínio e desenho anterior aos pixels

Somente os 52 sites com suporte válido entram no benchmark: 40 bottom_up e 12
top_down. Os 35 sites sem suporte não são erros do classificador. O target é
PUBLISHED_FRAGMENTATION_LOCATION_PRESENT sob supervisão fraca publicada;
BACKGROUND_CANDIDATE não comprova ausência física. GOLD é DIRECT_VALID automático,
sem revisão humana. Nenhuma identidade, coordenada ou admissibilidade B é alterada.

O planner puro autentica os dois JSONL existentes; não abre container ou vídeo.
Seleciona 40/12 tracks de background por SHA-256 textual, sem usar número de frames,
intensidade, textura ou desempenho. Prefixos exatos:
STUDY2C_BACKGROUND_SELECTION_V1|acquisition|track;
STUDY2C_SPLIT_V1|acquisition|class|group;
STUDY2C_CV_V1|acquisition|class|group. Class é POSITIVE ou BACKGROUND.
Desempate de hashes pelo identificador literal. Nenhuma nova seed.

Por classe, bottom_up tem 24/8/8 grupos TRAIN/DEVELOPMENT/TEST; top_down 8/2/2.
São 64/20/20 grupos totais e classes equilibradas por grupos, não por rows.
Cada grupo inteiro pertence a uma partição. TRAIN recebe quatro folds por rank
em cada estrato aquisição/classe, índice módulo quatro. O manifesto contém IDs,
tiers, frame, centro, proveniência B e hashes; conserva SILVER de TEST apenas como
metadado, nunca input ou target. Os 7.595 pares não rotulados são excluídos do
benchmark e não passam a negativos. Capacidade insuficiente encerra a operação.

TEST é GROUP_HELD_OUT_INTERNAL_TEST, com exposição histórica conhecida. A reserva
é lógica por grupo, não virgindade global de pixels nem independência de aquisições.
O desenho solicitado não impõe nova separação espacial de contextos entre grupos.
Patches próximos podem compartilhar contexto; duas aquisições não viram milhares
de réplicas independentes. Nenhum resultado pode alterar o split.

## Materialização controlada

Positivos são lidos exclusivamente nas rows selecionadas do container B, após uma
autenticação opaca integral. O descritor fica retido e cada row admitida é lida uma
vez; reuso em RAM para modelos/CV/final. Nenhuma duplicação positiva em disco.
O hash integral opaco cobre bytes já existentes, sem gerar arrays TEST antes da
fase final. Isso é declarado separadamente de acesso semântico ao TEST.

Backgrounds dos 42 tracks TRAIN+DEV são materializados após freeze e CI. Os dez
tracks TEST só entram após fit final concluído e registro durável. Cada passagem
reutiliza o leitor streaming B e os predicados de suporte B, sem chamar seu runner.
Os quatro MP4 ESM1/2/4/5 são autenticados, os 1.378 frames nativos conferem o ledger
de hashes B; somente crops selecionados são entregues ao benchmark. A análise de
suporte usa planos nativos necessários. A leitura global para suporte não é
descrita como acesso apenas aos pixels de patch. ESM3/6 não são abertos.

Cache agregado uint8, canais STRUCTURAL_Y/RELATIVE_SOLUTE_FIELD_Y, 2×65×65,
sem shift, padding, resize, substituição ou exportação de full frames.
Teto conjunto de caches: 2 GiB; temporários/metadados de cache 256 MiB;
reserva de disco 50 GiB. Sem features persistidas, tensores float32 ou modelos
binários. Hashes de caches são calculados durante append e sincronizados.

## Modelos e pesos

MODEL_CONTRACT.json congela todos os parâmetros, grids e ordem de desempates.
Clássicos: LBP uniform P8/R1, dez bins, range(0,10), density=True por canal,
concatenação de 20 features. Nenhuma feature adicional. LR e SVM usam
StandardScaler ajustado exclusivamente no subconjunto de treino, com os mesmos
pesos por grupo do classificador. Durante CV e comparações de desenvolvimento,
o scaler usa apenas treino. No ajuste final usa TRAIN+DEVELOPMENT conforme o
regime selecionado; TEST nunca participa.

Peso de cada row de ajuste: 1/número de rows daquele grupo no ajuste corrente.
O total por grupo é um, e as classes têm grupos igualmente numerosos.
Não há class_weight, reescala global de pesos ou peso arbitrário para SILVER.
CV recalcula os denominadores depois de separar cada fold.

LR: L2/lbfgs, C=0.1/1/10, max_iter=10000, tol=1e-4, seed42.
SVC: RBF, probability=false, C=0.1/1/10 e gamma=scale/0.01/0.1,
tol=0.001, cache_size=200, max_iter=-1, demais defaults registrados.
RF_REFERENCE: 100 árvores, seed42, 19 defaults históricos idênticos.
RF_TUNED: 100/300 árvores × depth None/8 × leaf1/3, demais parâmetros históricos.
São 12+36+32=80 fits CV. A média dos quatro GMBA escolhe a configuração.
Empate exato: C crescente; para SVM gamma na ordem declarada scale/0.01/0.1;
para RF árvores crescentes, depth8 antes de None, leaf3 antes de1. A ordem gamma
é convenção prévia, não alegação universal de complexidade física. Warning de
não convergência ou fit_status SVC não zero encerra a execução, sem reparo/tuning.

CNN_V2: Conv2→16k3pad1/ReLU/MaxPool2; Conv16→32k3pad1/ReLU/MaxPool2;
AdaptiveAvgPool1/Flatten/Linear32→2; exatamente 5.010 parâmetros.
CPU, uma thread, deterministic algorithms, seeds Python/NumPy/Torch42,
Generator42, workers0, batch32, shuffle TRAIN, vinte épocas, Adam lr0.001,
weight_decay0 e defaults explícitos. uint8→float32/255 por minibatch.
CE reduction=none; sum(loss_i*w_i)/sum(w_i) por batch. Os pesos de dataset
somam um por grupo; a normalização por minibatch não implica contribuição
efetiva idêntica nos passos SGD. Loss de época é soma de perdas ponderadas/
soma de pesos, com estados sucessivos do modelo. Sem DEV durante treino,
scheduler, early stopping, augmentation ou escolha de época.

## Métricas, decisões e ordem terminal

GMBA=.5×(média dos recalls entre sites positivos + média das especificidades
entre tracks background). Avaliação usa GOLD e BACKGROUND somente. Métricas
secundárias: BA/accuracy/precision/recall/F1/confusão por observação, recalls e
especificidades por grupo, maioria por grupo (empate classe0) e GMBA por aquisição.
Precisão/F1 com denominador nulo são zero. TRAIN é ressubstituição.

Após CV, exatamente um ajuste TRAIN e uma avaliação DEV por família:
LR, SVM, RF_REFERENCE, RF_TUNED, CNN_V2. Maior DEV GMBA vence; empate exato
usa observation BA; persistindo, a ordem anterior. A família fica fechada.
Somente a vencedora recebe um ajuste adicional TRAIN GOLD+SILVER+BG, mesmos
hiperparâmetros, pesos recalculados, e uma avaliação no mesmo DEV GOLD+BG.
Usa a referência GOLD já produzida, sem refit. Apenas melhora estrita de GMBA
seleciona GOLD_PLUS_SILVER; empate/queda mantém GOLD_ONLY.

FINAL_PIPELINE registra decisão, hiperparâmetros e IDs de TRAIN+DEV antes de
um único ajuste final. FINAL_FIT_FREEZE registra a conclusão e configuração do
fit com fsync antes de abrir TEST; não é serialização do estado aprendido.
Somente então se materializam TEST GOLD e os dez tracks TEST. A inferência não
recebe labels. TEST_PREDICTIONS é durável antes de scoring; o registro final
liga predições, métricas e hashes. TEST é consumido, mesmo em falha parcial de
acesso. Não se alega cegamento humano dos IDs ou metadados históricos.

Orçamento total: 80 CV + cinco comparações + uma ablação SILVER + um fit final
= 87 invocações de ajuste. Treinos CNN de vinte épocas e seus passos são
reportados separadamente. Uma invocação CLI, receipt exclusivo anterior aos
inputs, sem retry. Contadores de início e conclusão são distintos. Falha preserva
evidências e fecha autoridade; nenhum desempenho mínimo é gate de PASS.

## Custódia, ambiente e limites

Antes da ciência: testes sintéticos, desenho, commit de freeze filho do merge,
nove jobs e todos os passos SUCCESS no SHA exato. As 22 dependências existentes
permanecem pinadas; nenhuma instalação local. Mudanças anteriores permitidas:
admissão Torch apenas no novo módulo CNN/teste e extensão explícita do manifesto
de escopo. Nenhum workflow histórico, checksum95 ou algoritmo A/B é alterado.

Depois da ciência: somente textos, aritmética de predições e Git; nenhuma nova
feature, inferência, fit ou leitura de pixels para auditoria. Publicação por
checkpoint de evidências e CI no novo SHA, sem PR/Ready/merge Study2-C.
Os inventários de I/O são instrumentação delimitada, não monitor universal.

PASS certifica execução do protocolo, não superioridade, significância ou
generalização externa. Top_down TEST tem dois sites e dois tracks. Comparações
com Estudo1 são descritivas: dataset, split e métrica primária mudaram.
CNN2 não é retry da CNN1; mudanças não podem ser atribuídas só à arquitetura.
Sem onset exato, forecasting, causalidade, fragmentação física exaustiva,
concentração absoluta de Bi ou temperatura. FINAL do Estudo1 continua consumido.
