# TI3-C — comparação única de família em DEVELOPMENT

## Autoridade e custódia

A decisão em authorization.md autoriza esta etapa após a integração TI3-B.
PR #12 foi integrado por merge commit 48da1af69ce48b3287f19b26bfbd24b79243d90e,
com quatro jobs pós-merge e todos os passos SUCCESS. A branch nova nasce
exatamente nesse merge. Autoridades anteriores permanecem CLOSED_CONSUMED.
A autoridade nova é configs/authority/ti3c-minimal-cnn.json e termina com
receipt/results; um resultado baixo é válido, nunca motivação para retry.

## Dados e fronteiras

Target PUBLISHED_FRAGMENTATION_LOCATION_PRESENT, supervisão fraca
HIGH_CONFIDENCE_PLUS_IGNORE; backgrounds não provam ausência física.
O manifesto TI3-A c8e82b72ff5dc51d188a764c577c11d514474b14d90aea6292c1439e776fb487
permanece intacto: mesmos 52 sites, 108 observações, 383 IGNORE, centros,
contextos, backgrounds e split. Os 34 TRAIN e 16 DEVELOPMENT são os mesmos
TI3-B. Nada é reconstruído ou substituído por desempenho/suporte.

A única allowlist nativa contém ESM1/2:73,146,219 e ESM4/5:98,197.
Dez buffers, uma abertura cada, 19.469.052 bytes; hashes calculados na própria
leitura, sem reabrir. ESM1/2:293 e ESM4/5:295 são FINAL proibido antes de
qualquer acesso ao path. ESM3/6, novos frames, ZIP/MP4 e decoders são proibidos.
FINAL permanece SEALED_WITH_HISTORICAL_NON_ML_EXPOSURE: não é globalmente
virgem; seis samples documentais, zero opens/bytes, suporte/hash/features nulos.

Patches 65×65 sem deslocamento/padding. Guards estrutural e solutal e extração
são os mesmos de TI3-A/B, sem executar LBP ou RF. O guard cromático estrutural
é somente admissão histórica, não canal ou preprocessing CNN; o campo solutal
usa suporte geométrico, sem tratar sua cor científica como overlay. Ambos os
hashes de cada patch devem corresponder ao registro TI3-B. Uma falha interrompe
sem substituição. Inputs e modelo ficam somente em memória.

## Diagnóstico congelado antes dos pixels

A regra metadata-only usa, em cada aquisição, a classe majoritária em TRAIN
para prever DEVELOPMENT. acquisition-only-diagnostic.json guarda contagens,
ordem, predições, balanced accuracy e confusão; não é fit ML e seu resultado
não altera split, parâmetros ou representação. Não se infere causalidade.

## CNN e treinamento fixos

PyTorch 2.4.1+cpu, Python 3.12, CPU somente; requisitos e constraints explícitos.
Torch só é importável nos dois paths enumerados de núcleo e teste CNN. Os
75 LEGACY_TI2 e quatro A0 permanecem byte-idênticos e sob os mesmos guards.

Input uint8 N×2×65×65: canal0 Y estrutural; canal1 Y do campo solutal relativo.
Normalização float32 x/255.0, sem estatística aprendida ou de DEV. Sem Canny,
blur, novo Sobel, thresholding de input, equalização ou augmentation.

Conv2d(2,8,3,padding=1,bias=True), ReLU, MaxPool2d(2,2),
AdaptiveAvgPool2d((1,1)), Flatten, Linear(8,2,bias=True).
São 152 parâmetros convolucionais +18 lineares =170. Divergência bloqueia.
Sem camada extra, dropout, batch norm, attention ou pretrained.

Seeds Python/NumPy/Torch42, torch.use_deterministic_algorithms(True),
torch.set_num_threads(1). CrossEntropyLoss default; Adam lr0.005, demais
defaults PyTorch congelados, weight_decay0. Dez épocas, batch8,
DataLoader shuffle=True, Generator42, num_workers0. Sem scheduler,
early stopping, checkpoint por DEV, segunda seed ou tuning.

Ordem: autenticar/materializar TRAIN; treinar dez épocas; avaliar TRAIN apenas
descritivamente; então autenticar/materializar DEV e avaliar exatamente uma
vez. DEV não é lido nem usado durante treino. Uma única CLI científica inclui
essas operações; receipt O_EXCL+fsync é anterior a qualquer byte experimental.
Falha parcial registra estágio/contadores e consome a tentativa, sem retry.

## Endpoints e escolha congelados

Predição argmax dos dois logits, sem tuning de threshold. Balanced accuracy
primária; accuracy, precision, recall, F1, confusão [[TN,FP],[FN,TP]], logits,
probabilidades e ordem dos samples preservados. Loss por época é média
ponderada pelo número de samples dos minibatches. TRAIN é ressubstituição,
não estima generalização e não decide família. TRAIN1/DEVmenor implica
registro de possível overfit, nunca retreino.

Referência multimodal LBP/RF DEV BA=0.75, consumida; estrutural=0.6875.
Se CNN DEV BA>0.75: MINIMAL_MULTIMODAL_CNN; caso contrário (incluindo empate):
MULTIMODAL_LBP_RF. Sem seleção por TRAIN ou critérios pós-observação.

## Gates e encerramento

Antes dos pixels: dependências exatas, 170 parâmetros, forward sintético,
treinos sintéticos repetidos determinísticos, FINAL-denial, data/phase guards,
regressões legadas/TI3-A/B. C1 congela código/protocolo/configs/inputs textuais;
push e todos os cinco jobs CI SUCCESS com passos SUCCESS no SHA exato.
A prova real CI e o preflight textual precedem o receipt. Depois de C1,
nenhuma alteração científica. Evidência final exclusivamente textual, sem
modelo, array, imagem, feature binary ou kernel reexecutado para verificação.

A5 fornece fundamentos Conv/ReLU/Pool/Linear/CE/Adam; a escala FashionMNIST
não é copiada. LBP/RF A4 é referência histórica; Canny e augmentation foram
conscientemente excluídos. Não houve consulta ou execução de notebook externo.

DEV16 e FINAL6 são pequenos; TRAIN ESM1 tem16 positivos/6 backgrounds e ESM4
1/11. Aquisição/condição pode confundir classe. Patches não são aquisições
independentes. Só comparação interna de famílias e preferência de desenvolvimento;
sem significância estatística alegada, generalização externa, forecasting,
causalidade, onset exato, recall físico exaustivo ou Bi absoluto. FINAL e
avaliação final permanecem não autorizados; novo PR/merge não são implicados.
