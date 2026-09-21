# Study2-B integrado; Study2-C — benchmark agrupado e TEST único concluídos

**STUDY2_B_INTEGRATION=PASS; STUDY2_C=PASS; TEST_STATE=CONSUMED.**
O pipeline selecionado é **RF_REFERENCE + GOLD_PLUS_SILVER**. No TEST de 20
grupos e 3.257 observações, GMBA=**0,8449139278495638**, balanced accuracy por
observação=0,8525933757278337; TN2172/FP323/FN126/TP636. Foram cumpridos 80 fits
CV, cinco comparações, uma ablação e um fit final: 87 ajustes em uma invocação,
sem retry. A seleção e a autoridade científica estão encerradas.

## Retorno dos 38 itens autorais

| Item | Resultado comprovado |
| --- | --- |
| 1. Study2-B PR/merge | [PR #17](https://github.com/lmbernardo7520112/snbi-dendritic-fragmentation-ml/pull/17), Draft → CI verde → Ready → merge commit; branch preservada |
| 2. Merge SHA | de7670bb8491d2ef01809b33aa326aa3a264324c |
| 3. CI pós-merge | Oito jobs e 90 passos SUCCESS; respostas integrais em INTEGRATION_AUDIT.json |
| 4. Branch C | feat/study2c-group-aware-benchmark, criada no merge exato |
| 5. Grupos | 52 sites +52 tracks; por classe TRAIN32/DEV10/TEST10; bottom_up24/8/8, top_down8/2/2 |
| 6. Capacidade BG | PASS: 75 tracks bottom_up e148 top_down disponíveis |
| 7. Seleção BG | 40 bottom_up +12 top_down, ranking textual fixo;171 tracks UNUSED_BACKGROUND_RESERVE |
| 8. Hashes split | Manifesto74adb4eb…; quatro hashes semânticos integrais abaixo; plano único, só metadados |
| 9. Materialização BG | 8.737 pares TRAIN+DEV e2.495 TEST, todos com suporte; TEST após fit final;11.232 pares persistidos |
| 10. Freeze | 8c38384915807a15062782a4a189601f7c83c8c3; filho direto do merge;40 caminhos e37 hashes textuais |
| 11. CI pré-fit | Oito workflows, nove jobs e100 passos SUCCESS no SHA exato; CI_PROOF.json |
| 12. Pesos | 1/nrows do grupo no ajuste corrente; soma1 por grupo; classes32/32 no benchmark e42/42 no final; sem class_weight |
| 13. LR/CV | L2/lbfgs, scaler ponderado, max_iter=10000;12 fits CV; C=1; GMBA CV0,7801490011428773 |
| 14. SVM/CV | RBF, scaler ponderado, probability=false;36 fits CV; C=0,1/gamma=0,1; GMBA CV0,786217387578764 |
| 15. RF_REFERENCE | 100 árvores, seed=42 e19 defaults históricos integrais, sem tuning; vence DEV |
| 16. RF_TUNED | 32 fits CV;100 árvores, depth=8, leaf=1; GMBA CV0,765637374686184 |
| 17. CNN | Arquitetura exata2→16→32→2;5.010 parâmetros,304+4640+66 |
| 18. Treino CNN | Um treino CPU,20 épocas,6.820 updates, batch=32, Adam=0,001;408,127945s; sem DEV durante treino |
| 19. TRAIN | 10.907 rows/64 grupos, ressubstituição; tabela completa abaixo |
| 20. DEV/modelo | 2.286 rows/20 grupos; cinco avaliações, valores abaixo |
| 21. Primária | GMBA: LR0,845300;SVM0,787188;RFref0,875902;RFtuned0,874898;CNN0,705134 |
| 22. Família | RF_REFERENCE, escolhida somente por maior GMBA DEV, sem empate máximo |
| 23. SILVER | Um fit TRAIN12.844; DEV GOLD+BG inalterado; GMBA=0,8775115148991031 contra0,8759021928689068 |
| 24. Regime | GOLD_PLUS_SILVER, melhora estrita0,0016093220301962585; sem nova CV ou refit GOLD |
| 25. Pipeline | LBP multimodal20 + RF_REFERENCE100/seed=42 + GOLD_PLUS_SILVER, congelado antes do ajuste final |
| 26. Fit final | Um fit,15.949 rows,84 grupos;4.456 GOLD+2.756 SILVER+8.737 BG; sem TEST |
| 27. TEST GMBA | 0,8449139278495638 |
| 28. TEST observações | BA=0,8525933757278337;accuracy=0,8621430764507215;precision=0,6631908237747653;recall=0,8346456692913385;F1=0,7391051714119697 |
| 29. TEST grupos | Macro recall positivo0,7933145536774319;macro especificidade BG0,8965133020216957;maioria BA=0,95;20 registros completos no JSON |
| 30. TEST/aquisição | bottom_up GMBA=0,8575480543482503;top_down0,7943774218548179, este com apenas2 sites+2 tracks |
| 31. Estudo1 | Comparação descritiva; domínio, split, pesos e métrica primária diferentes; não estima efeito causal isolado do corpus ou arquitetura |
| 32. Suporte | Somente52/87 sites;35 sem suporte não são erros do modelo;inventário B intacto |
| 33. Claims | INTERNAL_GROUP_HELD_OUT_TEST de localização publicada; mesmas duas aquisições, sem generalização externa |
| 34. Runtime/storage | 859,882223s; pico Python815.192KiB; caches110.634.358B incluindo metadados;temporários0;reserva666.018.762.752B |
| 35. Evidence SHA | Checkpoint posterior exclusivamente documental; SHA efetivo no Git e retorno ao operador, sem autorreferência |
| 36. CI final | Será conferida no SHA documental após push; este relatório não antecipa sucesso futuro |
| 37. Git | Ciência do freeze intacta; novos textos apenas nesta pasta; arrays/ledgers locais ignorados; estado final após publicação informado ao operador |
| 38. Terminal | PASS;CLOSED_CONSUMED;TEST consumido;sem novo search,augmentation,self-supervised,PR/Ready/merge C |

## Integração, preparação e reserva de grupos

B2 cf5a4b091db52c0fc2f4b532230ed32ee013a2f9 foi conferido contra o remoto,
com index/tracked limpos, freeze B41/41 e hashes pós-run38/38. Seu checkpoint
continha17 adições textuais. A custódia inicial autenticou o container opacamente
(139.425.000 bytes) e os dois JSONL textuais (119.611.080 bytes); três opens,
259.036.080 bytes, separados da execução C. Nenhum array foi interpretado nessa
conferência. O merge preservou parents d4ef00bf1e1d84d49d4e3f2dce0d18f683598a4c
e cf5a4b091db52c0fc2f4b532230ed32ee013a2f9 e árvore
03e40d4a14720ec12148d3f4e1d372dc5167b807, idêntica ao head B. PR e pós-merge
passaram antes de criar C. Nenhuma branch foi excluída.

A implementação tem módulos separados para desenho/métricas, modelos, CNN,
acesso e execução. Só dois arquivos anteriores mudaram: o checker admitiu Torch
exclusivamente no novo módulo CNN/teste, e o manifesto acrescentou11 paths e
atualizou esse blob operacional. Preservados75 LEGACY,4 A0 e todos os outros
paths anteriores;137 Python classificados, zero duplicados/não classificados.
Workflows anteriores,95 checksums e ciência A/B/Estudo1 permaneceram intactos.
Nenhuma instalação local: Python3.12.3,22 pins anteriores, Torch2.4.1+cpu.

137 casos sintéticos únicos PASS, zero skips/falhas/erros: desenho30, I/O31,
modelos25, CNN10, execução41. Foram aprovados isoladamente e no perfil conjunto;
I/O teve passagem preliminar30 antes do último caso. Governança41 PASS.
Os oito fits clássicos e dois treinos CNN sintéticos locais são separados dos
87 ajustes experimentais. As chamadas CV simuladas dos testes não são ciência.
Não foi executada localmente nova regressão científica A/B ou modelo histórico.
Os nove jobs remotos incluem os contratos históricos requeridos.

A revisão anterior ao freeze corrigiu contadores de início/conclusão de fits,
custódia exata das rows, recusa de cache preexistente e redação do scaler final.
O preflight preparatório usou textos reais com Git/CI futuros simulados, declarados
como tais. O real verificou blobs do commit,37 hashes,22 pins e CI real, sem armar
receipt. Nenhuma mudança de código ocorreu após freeze ou exposição científica C.

O plano foi produzido uma vez por metadados. A auditoria independente recalculou
rankings, quotas e hashes e comparou20.137 samples com as duas fontes textuais B,
sem chamar o planner novamente. Destes,11.232 são BG e8.905 GOLD/SILVER.
SILVER em DEV/TEST permanece manifesto, com acessos restritos à fase permitida.

| Split | Sites | Tracks BG | GOLD | SILVER documental | BG | Avaliação primária GOLD+BG |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| TRAIN |32|32|3858|1937|7049|10907|
| DEVELOPMENT |10|10|598|819|1688|2286|
| TEST |10|10|762|931|2495|3257|

SILVER TEST931 nunca foi carregado como tensor/feature ou avaliado. Os7.595
não rotulados e10.896 registros inválidos nunca entraram no benchmark. A seleção
de BG usou rank textual, sem escolher por frame count ou desempenho. Nenhum grupo
cruza split; cada fold de validação tem6 sites+6 tracks bottom_up e2 sites+2 tracks
top_down; os outros48 grupos constituem o treino daquele fold.

Hashes congelados:

- SPLIT_MANIFEST.json: `74adb4eb7acad1e6aa67c4302d9db30d0c22f21fb51bc72aa89f701956d14ec7`.
- group_split_sha256: `0d7554fdb3c6583b508c681c6540e36c535641b25adc18f6f8cf07d5330b06ea`.
- selected_background_tracks_sha256: `cd70198cc9a3b3c3a0ea442ca6dc286a1d02ce6021ab0f5f17d739f9d563a827`.
- sample_manifest_sha256: `9bbd9a93ccc332584108474746019e2747dbae1cc8fd34f3b96ad09a488e50cf`.
- cv_fold_by_group_sha256: `85edac3d7da06994d7b16c4fa50e2aeb806abd7743a1d471842f54fdcf049ef2`.

## Benchmark e decisões congeladas

Cada ajuste usa peso1/n por grupo no subconjunto corrente. Em GOLD+SILVER,
as duas categorias compartilham o mesmo denominador positivo. Scaler ponderado
recebe apenas treino em CV/comparações; no fit final recebe TRAIN+DEV. TEST
nunca entra em scaler, fit ou seleção. Não há class_weight ou peso0,5 para SILVER.
Bootstrap RF e normalização por minibatch CNN não garantem influência efetiva
idêntica por grupo; o contrato é igualdade da soma dos pesos fornecidos.

As features clássicas são LBP P8/R1/uniform, dez bins/range(0,10)/density=True
por canal e concatenação20. CNN usa somente uint8→float32/255. ESM2/5 representam
campo solutal relativo, não concentração absoluta. Não houve novas features,
transformação, augmentation, calibração de probabilidade SVM ou ajuste de threshold.

As tabelas arredondam para seis casas; decisões usaram os valores integrais
preservados em cada JSON e em RESULTS_SUMMARY.json. TRAIN é ressubstituição.

| Modelo | TRAIN GMBA | TRAIN obs.BA | Accuracy | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| LOGISTIC_REGRESSION | 0.793636 | 0.775293 | 0.722747 | 0.563820 | 0.954899 | 0.709007 |
| SVM_RBF | 0.786483 | 0.743727 | 0.673604 | 0.520439 | 0.983411 | 0.680660 |
| RF_REFERENCE | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| RF_TUNED | 0.909497 | 0.872244 | 0.839644 | 0.692392 | 0.983670 | 0.812721 |
| CNN_V2 | 0.770284 | 0.741667 | 0.773998 | 0.700316 | 0.631156 | 0.663940 |

| Modelo | DEV GMBA primária | DEV obs.BA | Accuracy | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| LOGISTIC_REGRESSION | 0.845300 | 0.802242 | 0.723097 | 0.485331 | 0.968227 | 0.646566 |
| SVM_RBF | 0.787188 | 0.680114 | 0.532371 | 0.357704 | 0.989967 | 0.525522 |
| RF_REFERENCE | 0.875902 | 0.840773 | 0.861330 | 0.708767 | 0.797659 | 0.750590 |
| RF_TUNED | 0.874898 | 0.832845 | 0.792213 | 0.563077 | 0.918060 | 0.698029 |
| CNN_V2 | 0.705134 | 0.767956 | 0.867017 | 0.890957 | 0.560201 | 0.687885 |

| Modelo | DEV macro recall site | DEV macro especificidade track | Maioria BA | GMBA bottom_up | GMBA top_down | Tempo fit TRAIN (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| LOGISTIC_REGRESSION | 0.935937 | 0.754662 | 0.900000 | 0.883365 | 0.693038 | 0.036513 |
| SVM_RBF | 0.997273 | 0.577103 | 0.800000 | 0.831453 | 0.610127 | 4.292543 |
| RF_REFERENCE | 0.805369 | 0.946436 | 0.900000 | 0.874783 | 0.880380 | 3.521474 |
| RF_TUNED | 0.863608 | 0.886188 | 0.900000 | 0.908022 | 0.742405 | 1.944727 |
| CNN_V2 | 0.454091 | 0.956178 | 0.750000 | 0.759741 | 0.486709 | 408.127945 |

RF_REFERENCE supera RF_TUNED em0,0010039765221585562 GMBA DEV, apenas0,1004 ponto
percentual. A maior accuracy DEV isolada foi da CNN; a primária prévia escolheu
RF_REFERENCE. Isso não demonstra superioridade estatística universal. O RF tem
TRAIN perfeito e DEV menor; não se usou esse contraste para repetir ou ajustar.

A CV percorreu12 LR,36 SVM e32 RF fits. Média dos quatro folds selecionou C1
para LR, C=0,1/gamma=0,1 para SVM e100/depth=8/leaf=1 para RF_TUNED, sem empate máximo.
Tempos somados dos fits CV:0,552391s/72,031968s/128,027095s. Os parâmetros integrais,
scalers, scores por fold e grupos estão nos três *_CV.json. As predições por fold
não foram persistidas; a auditoria posterior confere médias e escolhas, não
recalcula esses scores individuais. Predições TRAIN/DEV dos cinco modelos foram
persistidas integralmente; SVM registra scores de decisão, não probabilidades.

CNN: Conv2→16/ReLU/MaxPool2,Conv16→32/ReLU/MaxPool2,AdaptiveAvgPool1,Flatten,Linear32→2.
Kernel3/padding1,5.010 parâmetros. CPU/uma thread, seeds e Generator42, workers=0,
batch=32,20 épocas,Adam lr0,001/weight_decay=0,CE reduction=none. Objetivo por batch:
sum(loss×weight)/sum(weight). Nenhuma consulta DEV durante treino. Loss de época
agrega perdas ponderadas de forwards em estados sucessivos, não um novo scoring
em modelo fixo. Todos os6.820 passos previstos foram concluídos.

| Época | Loss ponderada registrada |
| --- | ---: |
| 1 | 0.6224969378550511 |
| 2 | 0.5727601167064051 |
| 3 | 0.5480573522566207 |
| 4 | 0.5330546932051874 |
| 5 | 0.5355446387070801 |
| 6 | 0.5152419581470047 |
| 7 | 0.49553827679794865 |
| 8 | 0.4808697981704214 |
| 9 | 0.4865551078498344 |
| 10 | 0.46959452135205293 |
| 11 | 0.4629216599800025 |
| 12 | 0.4482426260990411 |
| 13 | 0.44550792845336556 |
| 14 | 0.44751168352370335 |
| 15 | 0.43534860975087586 |
| 16 | 0.4302653661414177 |
| 17 | 0.4327642840848629 |
| 18 | 0.4072799996599555 |
| 19 | 0.414365819009274 |
| 20 | 0.40243536810728336 |

Somente RF_REFERENCE recebeu o fit SILVER adicional,12.844 rows/64 grupos,
4,435768s, sem nova CV. GMBA subiu de0,8759021928689068 para0,8775115148991031:
+0,0016093220301962585, ou+0,16093220301962585 ponto percentual. A regra estrita
selecionou GOLD_PLUS_SILVER. Outros critérios não foram usados: a accuracy
DEV caiu de0,861330 para0,828084 e F1 de0,750590 para0,729525, enquanto obs.BA
subiu de0,840773 para0,846876. A confusão SILVER é[[1363,325],[68,530]].
Essa troca não foi ocultada nem usada para mudar a regra. A ablação não prova
benefício causal ou generalização de SILVER.

## Ordem final, TEST e resultados por aquisição

Receipt exclusivo O_EXCL+fsync:2026-09-21T17:25:12.806460+00:00; o último job CI
terminou17:23:58Z. Comando científico único no sandbox padrão, exit0, com TMPDIR
no diretório controlado do repositório:

```text
PYTHONPATH=src .venv/bin/python -B scripts/run_study2c.py run
```

FINAL_PIPELINE foi gravado às17:38:31.756131Z antes do fit final. Registro durável
da conclusão às17:38:39.265439Z; acesso TEST às17:38:39.276162Z, depois do fit.
O fit final consumiu15.949 rows/84 grupos,42 por classe, com4.456 GOLD,
2.756 SILVER e8.737 BG; duração5,586068s. RF preservou os19 parâmetros históricos
incluindo100árvores,seed=42,depth=None,leaf=1,max_features=sqrt,class_weight=None.
Não houve nova avaliação DEV separada ou refit de qualquer família concorrente.

FINAL_FIT_FREEZE é registro durável de conclusão/configuração; não é hash lógico
do estado aprendido nem modelo serializado. Código congelado e estado de execução
mantiveram o modelo em memória. TEST_PREDICTIONS foi sincronizado antes de scoring;
sua função de inferência não recebe labels. Não há timestamp próprio nesse JSON:
a ordem é sustentada pelo código, testes e cadeia de hashes, não por timestamp
independente inexistente, cegamento humano ou monitoramento universal de syscalls.

- FINAL_PIPELINE SHA-256: a5e5ad86e9789147849dfd72f84fbf38065bf385e1c09b00779fba2133d49e5c.
- FINAL_FIT_FREEZE SHA-256: 0ee683a3029c3fc1e9e299bf9fdf9fc461d7ffad240f447760d13160997c4c4c.
- TEST_PREDICTIONS SHA-256:1534fa28050480a005395599b4e0a4ae6dd17dcb984a80dac4520890f4068539.

| Métrica TEST | Global | bottom_up | top_down |
| --- | ---: | ---: | ---: |
| GMBA primária | 0.844913928 | 0.857548054 | 0.794377422 |
| Macro recall sites | 0.793314554 | 0.756796253 | 0.939387755 |
| Macro especificidade tracks | 0.896513302 | 0.958299855 | 0.649367089 |
| Maioria BA | 0.950000000 | 0.937500000 | 1.000000000 |
| Observation BA | 0.852593376 | 0.891233391 | 0.794278139 |
| Accuracy | 0.862143076 | 0.929711082 | 0.695095949 |
| Precision | 0.663190824 | 0.915285451 | 0.334134615 |
| Recall | 0.834645669 | 0.809446254 | 0.939189189 |
| F1 | 0.739105171 | 0.859118410 | 0.492907801 |

Confusão global[[2172,323],[126,636]], classes[0,1], linhas verdadeiro/colunas
predito. Bottom_up[[1659,46],[117,497]];top_down[[513,277],[9,139]].
TEST contém762 observações GOLD e2.495 BG, mas apenas10sites+10tracks, todos nas
mesmas duas aquisições. Bottom_up tem8+8 grupos/2.319rows;top_down2+2/938rows.
Os20 detalhes por grupo, IDs completos, nobs, acertos, recall/especificidade e
voto estão em TEST_METRICS.json. Dezenove grupos têm maioria correta; isso não
apaga erros dentro das trajetórias: um site bottom_up tem recall2/32=0,0625.
Em top_down,277 das790 observações BG foram classificadas positivas; maioria BA1
nesse estrato pequeno não equivale a especificidade1. Nenhuma seleção foi reaberta.

## I/O, armazenamento e limites dos contadores

Positivos vieram exclusivamente do container B. Após receipt houve uma
autenticação opaca139.425.000B e7.974 reads de rows selecionadas/67.380.300B,
no mesmo descritor retido. TRAIN3858,DEV598,SILVER TRAIN1937,SILVER DEV819 e
TEST GOLD762. As rows já carregadas foram reutilizadas em RAM. TEST positivo
teve6.438.900B de acesso semântico somente após finalfit. O hash opaco anterior
cobriu o container inteiro sem formar tensors ou features de TEST.

| Fronteira backgrounds | TRAIN+DEV | TEST após fit | Total |
| --- | ---: | ---: | ---: |
| Autenticações Python MP4 |4|4|8|
| Bytes comprimidos autenticados |108466048|108466048|216932096|
| Requests de input decoder |4|4|8|
| Frames nativos entregues |1378|1378|2756|
| Bytes nativos entregues |2680088688|2680088688|5360177376|
| Pares selecionados materializados |8737|2495|11232|
| Bytes uint8 persistidos |73827650|21082750|94910400|

Somente ESM1/2/4/5, duas passagens. Todos os hashes de frames conferiram com B;
nenhum positivo foi redecodificado como patch. Full frames compartilhados são
necessários ao streaming/suporte; não se alega isolamento físico global de todos
os pixels TEST antes da fase final. A reserva é lógica para tensors/features/
modelagem por grupos. FFmpeg bytes comprimidos internos não são instrumentados.
As fronteiras de autenticação, conteúdo nativo e selected rows não são volume
único somável. Aliases de source_auth_bytes não foram somados.

Nenhuma substituição, novo crop, padding, resize ou alteração de suporte ocorreu.
Patches B positivos não foram persistidos novamente. Os11.232 pares BG equivalem
a22.464 patches de canal. streaming.patches_written=0 descreve o decoder, enquanto
o writer persistiu esses pares. Cache final110.634.358B=94.910.400pixels+
15.723.958metadados; temporários de disco0, abaixo dos budgets2GiB/256MiB.
Pico815.192KiB é somente Python, não a soma de processos FFmpeg. Tempo859,882223s
é o intervalo medido pelo controlador, distinto da duração total da tarefa.

| Cache local ignorado | Bytes | SHA-256 incremental |
| --- | ---: | --- |
| data/derived/study2c/cachetrain_dev.bin | 73827650 | 6c64f8e07ba99d0c2ccd04080031b23fc79d9162db79b2e4560e0cc6c4a49b3d |
| data/derived/study2c/cachetrain_dev.jsonl | 12255617 | 8c20022890b19cab2d0c6aa7825809c575a520415227032de5c72549f863048a |
| data/derived/study2c/cachetest.bin | 21082750 | 051f8cebd628710b00f3c53ebfb18c691acc0df05dfb5a0f89d5d073e74f4576 |
| data/derived/study2c/cachetest.jsonl | 3468341 | bf597f9618b9554b1f58f1a509bda32e99b72c138e4e77755a8f45063a5d9d9d |

**Limitação documental de projeção:** as rows de cache herdaram
pixels_materialized=false do pool de entrada B, embora os patches C tenham sido
materializados. Esse campo não descreve o estado atual C e não deve ser usado por
consumidores como tal. Os manifests completos, cache_path/cache_row_index, shape,
hashes e contadores do writer comprovam o estado atual. IO_ACCOUNTING.json registra
a reconciliação aditiva; nenhum JSONL, resultado ou código consumido foi corrigido.
A decisão de fit/seleção não depende desse campo. Os caches binários não foram
reabertos após a ciência para hash, visualização ou nova feature; conferências de
tamanho usam stat. Não houve imagem exportada, tensor float32, feature array ou
modelo binário persistido.

## Interpretação restrita e custódia

O benchmark descreve52 sites de suporte válido, não os87 AUTO_GOLD originais.
Os35 inválidos permanecem históricos e não contam como erros de classificação.
O teste é interno, agrupado, com exposição histórica declarada. Agrupar sites/
tracks não cria novas aquisições, nem garante ausência de contexto espacial
compartilhado entre grupos próximos. Milhares de frames não são milhares de
réplicas experimentais independentes. A especificidade BG e o recall positivo
referem-se a weak labels gráficas publicadas; FP/FN não estabelecem eventos físicos.

No Estudo1, DEV estrutural/multimodal/CNN1 BA=0,6875/0,75/0,50 e FINAL6 BA=2/3.
Aqui a primária é GMBA e o TEST tem20 grupos/3.257rows. Corpus, split, pesos,
quantidades e avaliação mudaram. RF_REFERENCE mantém os19 parâmetros do algoritmo
anterior, agora com pesos agrupados; a comparação histórica não isola efeito causal
do corpus. CNN2 tem5.010 parâmetros contra170 da CNN1 e usa outro dataset; não é
retry e diferenças não se atribuem exclusivamente à arquitetura. Não foi feita
comparação adicional para melhorar o resultado. FINAL do Estudo1 segue consumido.

Não há claim de significância, generalização externa, onset exato, forecasting,
causalidade, inventário físico exaustivo, temperatura ou Bi absoluto. Nenhuma
revisão humana, Hough, augmentation, ajuste de labels ou estudo self-supervised.
PASS significa cumprimento do protocolo; nenhum score mínimo foi usado como gate.

CLASSICAL_TEXT_AUDIT.json confere52.772 predições e a seleção CV por aritmética
independente. FINAL_TEXT_AUDIT.json e IO_CUSTODY_AUDIT.json documentam a conferência
terminal, seus limites e a custódia. Nenhuma auditoria posterior importa scorer,
modelo, decoder, planner ou runner científico. Histórico acadêmico e resultados
anteriores permaneceram intocados. As novas evidências ficam nesta pasta;
post-run-hashes.sha256 e VERIFICATION_TERMINAL.json autenticam o encerramento.

Publicação posterior: um checkpoint evidence-only, push fast-forward e CI no
SHA documental. SHA, conclusão remota e estado Git pertencem ao retorno efetivo,
sem autorreferência. Não há PR/Ready/merge C, segundo teste ou novo model search.
O inventário de comandos é delimitado, não monitor universal de syscalls.

```text
STUDY2_B_INTEGRATION=PASS
STUDY2_C=PASS
STUDY2_C_METHOD=GROUP_AWARE_MULTIMODAL_BENCHMARK
VALID_SUPPORT_SITES=52
VALID_SUPPORT_SITE_DOMAIN_ONLY=true
SELECTED_BACKGROUND_TRACKS=52
TRAIN_POSITIVE_GROUPS=32
TRAIN_BACKGROUND_GROUPS=32
DEV_POSITIVE_GROUPS=10
DEV_BACKGROUND_GROUPS=10
TEST_POSITIVE_GROUPS=10
TEST_BACKGROUND_GROUPS=10
MODELS_EVALUATED=5
SELECTED_MODEL_FAMILY=RF_REFERENCE
SELECTED_SUPERVISION_REGIME=GOLD_PLUS_SILVER
FINAL_STUDY2_PIPELINE=LBP20_RF_REFERENCE_GOLD_PLUS_SILVER
CV_FITS=80
MODEL_COMPARISON_FITS=5
SILVER_FITS=1
FINAL_FITS=1
SCIENTIFIC_TEST_EVALUATIONS=1
TEST_STATE=CONSUMED
HUMAN_REVIEW_USED=false
AUGMENTATION_USED=false
EXTERNAL_GENERALIZATION_CLAIM=false
STUDY2_CLOSED=true
MERGE_AUTHORIZED=false
CURRENT_AUTHORIZED_ACTIVITY=NONE_AWAITING_AUTHOR_DECISION
```
