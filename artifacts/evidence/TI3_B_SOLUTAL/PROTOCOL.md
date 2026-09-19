# TI3-B — ablação incremental solutal congelada antes dos pixels

Autoridade: [decisão integral](authorization.md). A integração TI3-A foi
concluída no PR #11, merge `7a205327b363f8cdbba99c5e58bf2f1e5d1253d3`, com
os três jobs pós-merge SUCCESS. A branch `feat/ti3b-solutal-ablation` nasce
exatamente desse merge. As autoridades científicas anteriores permanecem
consumidas; somente a autoridade nova condiciona uma invocação ao B1 publicado
e a todos os quatro jobs obrigatórios verdes nesse SHA.

## Pergunta, dados e representação fixos

Pergunta única: acrescentar a representação registrada do campo solutal
relativo aumenta a discriminação de PUBLISHED_FRAGMENTATION_LOCATION_PRESENT
no DEVELOPMENT interno, sob o mesmo LBP/RF?

Manifesto TI3-A imutável: 52 sites, 108 observações e 383 IGNORE; 34 samples
TRAIN (17/17), 16 DEVELOPMENT (8/8) e seis FINAL documentais (3/3).
Os mesmos sample_id, sites, contextos, rótulos, backgrounds, centros e patches
65×65 permanecem. Reutilizam-se os guards de anti-leakage TI3-A. Componentes
estrutural e solutal pertencem ao mesmo sample_id, instante e split.

ESM1→ESM2 e ESM4→ESM5 usam a identidade aceita pelo autor e G2_SOLUTE, sem
estimar offset, transformação ou novo registro. Os inputs solutais autorizados
são ESM2:73/146 e ESM5:98 em TRAIN; ESM2:219 e ESM5:197 em DEVELOPMENT.
Cinco buffers estruturais correspondentes são necessários para reconstruir
suas features, que não foram persistidas em TI3-A. Isso não reexecuta o fit
ou a avaliação do baseline estrutural. Seus hashes de patch devem reproduzir
os registros textuais de materialização TI3-A.

Cada um dos dez buffers permite uma única abertura read-only após receipt:
cinco estruturais/9.734.526 bytes e cinco solutais/9.734.526 bytes, total
19.469.052 bytes. Tamanho/hash nativo são autenticados durante essa leitura.
Nenhum buffer será reaberto para conferência. A fonte é o piloto existente;
não há vídeo, ZIP, decodificação, FFmpeg/FFprobe ou novo frame.

Representação científica: Y nativa uint8, sem mudança de contraste, escala,
normalização entre modalidades, cor alternativa ou ajuste de coordenadas.
ESM2/5 são RELATIVE_SOLUTE_FIELD, não concentração absoluta de Bi, temperatura,
campo térmico ou precursor causal. Y caracteriza a representação visual
disponível, não mede quantitativamente toda a concentração física.

## Suporte previamente definido

Estrutural: reutilizar `ti3_support.checked_native_luminance` intacta, incluindo
suas exclusões cromáticas, halo e erosão. Nenhum sample pode ser substituído.

Solutal: a seção Máscaras, partição e representação do protocolo histórico
`docs/protocols/TI2R_SOLUTE_DIRECT_PROTOCOL.md` estabelece exclusão geométrica
de 12% superiores, 15% inferiores e borda de quatro pixels. Ela explicitamente
não transfere o filtro cromático FRAG ao campo solutal. Aplicar U/V como
exclusão removeria a própria representação física visualizada. Não se usa U/V
como feature ou critério de seleção nesta ablação.

O patch inteiro deve pertencer ao retângulo `ti3_dataset.support_xyxy`, que
conserva aquelas exclusões e uma margem adicional de um pixel, correspondente
à guarda LBP R1 usada em TI3-A. Essa margem é do suporte do patch TI3, não a
guarda de 20 pixels do antigo descritor de registro SOLUTE. Não se reexecutam
SS8/NGF nem seus testes experimentais. Nenhuma ROI metrológica é certificada.

Validar toda a lista congelada e o pareamento antes de examinar cada buffer.
Qualquer patch solutal inválido resulta em BLOCKED_SOLUTAL_SUPPORT, sem mover
centro, substituir sample, relaxar critério ou continuar para fit parcial.
Todo suporte TRAIN/DEV passa antes do único fit; FINAL não participa dessa
verificação, inclusive seu suporte cromático/geométrico experimental.

## Features, modelo e decisão

Por patch e modalidade: LBP P=8/R=1/uniform, dez bins, range=(0,10),
density=True. Concatenar exatamente [STRUCTURAL_LBP_10, SOLUTAL_LBP_10].
Dimensão 20; cada metade tem soma um. Sem estatísticas adicionais, PCA,
feature selection, scaling aprendido, augmentation ou CNN.

RF: 100 árvores, random_state=42, todos os demais parâmetros idênticos ao
`RF_PARAMETERS` de TI3-A e versões já pinadas. Uma chamada fit em TRAIN;
predições TRAIN e DEVELOPMENT pela regra padrão sklearn. Não ajustar pesos,
threshold, seed ou hiperparâmetros. Resultados absolutos de TRAIN são ressubstituição.

Primária: balanced_accuracy. Secundárias: accuracy, precision, recall, F1,
matriz de confusão na ordem [0,1] e TP/FP/TN/FN. Relatar predições individuais,
probabilidades, IDs/ordem e parâmetros completos. A referência estrutural
consumida é BA=0,6875, TN3/FP5/FN0/TP8; não é treinada ou avaliada novamente.

Delta descritivo = BA multimodal DEV − 0,6875. Se BA multimodal for estritamente
maior, DEV_MODALITY_PREFERENCE=STRUCTURAL_PLUS_RELATIVE_SOLUTE; caso contrário,
STRUCTURAL_ONLY. Empate favorece simplicidade. A regra é congelada antes dos
pixels e não depende de escolher uma representação após observar DEV.

## Custódia, testes e execução única

B1 é filho direto do merge TI3-A, contém protocolo/configuração/código/testes,
inventário de escopo e freeze textual. Nenhuma ciência anterior é editada.
O manifesto de escopo recebe somente os cinco novos paths TI3_ACTIVE; 75 LEGACY,
quatro A0 e 15 TI3 anteriores mantêm modos/blobs. A cópia histórica no merge
permanece verificável; o freeze anterior não é reescrito.

O workflow TI3-A permanece intacto. Um workflow TI3-B separado executa testes
sintéticos novos; os três jobs históricos continuam obrigatórios. Dependências
locais existentes: NumPy1.26.4/SciPy1.11.4/scikit-image0.24.0/scikit-learn1.5.2.
Sem instalação local. Testes stdlib informam skips opcionais; CI multimodal
exige sua suíte completa sem skip/falha/erro. Smokes/fits sintéticos são
separados da única invocação científica experimental.

Antes dos pixels: data guard, phase scope, testes legados/TI3/multimodais,
revisão textual independente, commit B1, push FF e CI completa verde no SHA
exato. Preflight read-only valida tipos/configuração serializada real,
hashes/blobs congelados, inventário, versões, branch/parent e evidências CI.
O receipt exclusivo O_EXCL+fsync nasce antes do primeiro open experimental.
Receipt ou resultado existente impede repetir a execução. Todo symlink ou
divergência bloqueia; não há fallback ou reparo após B1.

Depois, executar uma vez `PYTHONPATH=src .venv/bin/python -B scripts/run_ti3b_ablation.py`.
Após a execução, somente evidências textuais e B2 documental. Não exportar
imagens, patches, arrays de features, modelo, pickle ou checkpoint científico.
Revisão final usa apenas textos, sem reabrir imagens ou chamar kernels.

## FINAL e limites da inferência

ESM1:293, ESM4:295, ESM2:293 e ESM5:295 permanecem proibidos para ML, antes de
stat, abertura, hash, suporte, feature ou avaliação. Seu estado continua
SEALED_WITH_HISTORICAL_NON_ML_EXPOSURE; reserva ML não significa virgindade
global. Nenhuma nova partição ou sample é criado.

TRAIN ESM1 tem 16 positivos/6 backgrounds; ESM4 tem 1/11. Essa confusão possível
classe/aquisição permanece; não há reequilíbrio. DEV16, oito por classe,
oferece métricas granulares; FINAL6 tem baixa potência e não será usado.
Sites/patches não equivalem a aquisições experimentais independentes.
Background candidato não comprova ausência física; FP contra weak label não
comprova falsa fragmentação física. Não se inventa significância estatística.

Se houver melhora, ela é informação discriminativa incremental observada
somente no DEVELOPMENT interno sob este protocolo. Sem melhora, não se observou
benefício incremental desta representação sob este LBP/RF; não se conclui
irrelevância física do soluto. DETECTION != FORECASTING != CAUSALITY.
Não há claim externo, onset exato, inventário físico exaustivo ou previsão futura.

PASS significa execução conforme protocolo, independentemente de melhora.
Após PASS ou BLOCKED, encerrar a autoridade. TI3-C, CNN, FINAL, retry, tuning,
nova ciência e merge TI3-B continuam não autorizados.
