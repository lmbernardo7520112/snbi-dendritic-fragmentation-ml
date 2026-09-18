# TI2R-SOLUTE-DIRECT — resultado terminal de 2026-09-18

**TI2R_SOLUTE_DIRECT=BLOCKED_IDENTITY_NOT_DISCRIMINATIVE; G2_SOLUTE=BLOCKED.**
A identidade venceu os controles relativos nos instantes identificáveis, mas
nenhum bloco alcançou os pisos absolutos congelados das duas métricas. Esse é
o motivo específico do estado terminal; não houve deslocamento-controle
vencedor no score agregado. Nenhum mapeamento solutal foi certificado.
**G2_FRAG=PASS_DIRECT_RASTER_MAPPING permanece aceito e preservado.**

## Proveniência, acesso e autoridade

PR #8 integrado por merge commit `db03183e1456f67b5b663a4cb71361cad1404dcb`,
com dois pais, conteúdo igual ao head auditado, histórico e branches
preservados; CI pós-merge 35360692165 SUCCESS. Main sincronizada por fast-forward.
Nova branch: `feat/ti2r-solute-direct-mapping`.

- C1: `45c5acbcfbc33e4a1af1d35fc2ef961d6bd15ad1`, método inativo congelado.
- C2: `8b5d286e227d896eb639a743c26da4c4fe6ec582`, somente autoridade e decisão.
- C3 contém o resultado e encerramento; SHA efetivo, push e CI serão registrados
  no histórico, Draft PR e retorno ao autor, sem commit pós-publicação.

O runner `PYTHONPATH=src /usr/bin/python3 -B scripts/run_ti2r_solute_direct.py`
foi invocado **exatamente uma vez**, no sandbox padrão, e retornou código **2**,
resultado científico bloqueado previsto. Receipt O_EXCL/fsync criado antes dos
bytes: contador 1, SHA C2, 14 hashes textuais e allowlist. Os 14 textos continuam
idênticos a C1. Nenhum código, máscara, parâmetro, descritor, limiar ou regra
mudou após C2. Autoridade fechada como **CLOSED_CONSUMED** antes de publicação.

Foram abertos e autenticados uma vez cada **12 buffers de desenvolvimento,
23.349.060 bytes**: ESM1/ESM2:0/146/293 e ESM4/ESM5:0/197/394. Dimensões,
formato e hashes corresponderam ao manifesto. **Zero holdouts abertos** nesta
fase: ESM1/ESM2:73/219 e ESM4/ESM5:98/295 permaneceram NOT_OPENED. Nenhum
par passou desenvolvimento; não houve freeze de identidade ou validação.
As referências dos holdouts já haviam sido expostas em FRAG-DIRECT, conforme
registro de exposição; NOT_OPENED aqui não significa ausência de acesso histórico.

## Identificabilidade e métricas

Referências ESM1:0 e ESM4:0: NON_IDENTIFIABLE, zero blocos individuais
qualificados. As outras quatro referências de desenvolvimento são IDENTIFIABLE.
Todas as seis imagens móveis ESM2/ESM5 são individualmente IDENTIFIABLE.
Assim, os pares no índice 0 são NON_IDENTIFIABLE, sem PASS nem residual;
os índices 146/293 e 197/394 são IDENTIFIABLE, mas reprovados nos scores.
Cada instante identificável possui 18 blocos por papel e quatro quadrantes.

Seleção: variante explicitamente documentada de auto-semelhança local de oito
canais, **LOCAL_SELF_SIMILARITY_8**, não implementação exata MIND-SSC.
Auditoria independente: NGF sign-invariant em blocos distintos. Os scores
abaixo são médias dos blocos; a regra exige piso em **cada** bloco medido:
SS8≥0,90 e NGF≥0,80. Em cada instante, todos os 18 blocos de cada papel ficaram
abaixo do respectivo piso. Os limiares não foram relaxados após os dados.

| Par | Índice | SS8 identidade | NGF identidade | Estado |
| --- | ---: | ---: | ---: | --- |
| ESM2-to-ESM1 | 0 | — | — | NON_IDENTIFIABLE |
| ESM2-to-ESM1 | 146 | 0,775895 | 0,537644 | BLOCKED_IDENTITY_NOT_DISCRIMINATIVE |
| ESM2-to-ESM1 | 293 | 0,756525 | 0,531850 | BLOCKED_IDENTITY_NOT_DISCRIMINATIVE |
| ESM5-to-ESM4 | 0 | — | — | NON_IDENTIFIABLE |
| ESM5-to-ESM4 | 197 | 0,783140 | 0,573309 | BLOCKED_IDENTITY_NOT_DISCRIMINATIVE |
| ESM5-to-ESM4 | 394 | 0,748236 | 0,532966 | BLOCKED_IDENTITY_NOT_DISCRIMINATIVE |

## Controles negativos espaciais e temporais

Somente identidade `(0,0)` era admissível. Os 48 deslocamentos não nulos de
[-3,+3]² foram comparados em cada métrica nos quatro instantes identificáveis,
com os mesmos pixels da identidade. Nenhum foi adotado como transformação.
As menores margens abaixo são contra o melhor controle de cada família;
todas superaram 0,005. Esse sucesso relativo não elimina a falha do piso absoluto.

| Par | Índice | Margem espacial SS8 | Margem espacial NGF | Menor margem temporal SS8 | Menor margem temporal NGF |
| --- | ---: | ---: | ---: | ---: | ---: |
| ESM2-to-ESM1 | 146 | 0,011709 | 0,018071 | 0,099684 | 0,056766 |
| ESM2-to-ESM1 | 293 | 0,010597 | 0,021633 | 0,080609 | 0,047297 |
| ESM5-to-ESM4 | 197 | 0,012550 | 0,024323 | 0,107941 | 0,092383 |
| ESM5-to-ESM4 | 394 | 0,010994 | 0,019902 | 0,070348 | 0,043189 |

Todos os seis pares temporais dirigidos de cada aquisição ficaram registrados:
quatro medidos e dois inconclusivos por referência inicial NON_IDENTIFIABLE.
Não foram escolhidos frames a partir dos scores. Os oito controles medidos:

| Par | Índice referência→móvel incorreto | SS8 controle | Margem SS8 | NGF controle | Margem NGF |
| --- | --- | ---: | ---: | ---: | ---: |
| ESM2-to-ESM1 | 146→0 | 0,676211 | 0,099684 | 0,480878 | 0,056766 |
| ESM2-to-ESM1 | 146→293 | 0,654000 | 0,121896 | 0,404474 | 0,133170 |
| ESM2-to-ESM1 | 293→0 | 0,675916 | 0,080609 | 0,484554 | 0,047297 |
| ESM2-to-ESM1 | 293→146 | 0,665550 | 0,090975 | 0,409741 | 0,122110 |
| ESM5-to-ESM4 | 197→0 | 0,675199 | 0,107941 | 0,480926 | 0,092383 |
| ESM5-to-ESM4 | 197→394 | 0,649635 | 0,133504 | 0,402775 | 0,170533 |
| ESM5-to-ESM4 | 394→0 | 0,677889 | 0,070348 | 0,489776 | 0,043189 |
| ESM5-to-ESM4 | 394→197 | 0,655527 | 0,092710 | 0,411361 | 0,121605 |

## Resíduos preservados e limites

Os 72 resíduos de auditoria foram preservados, sem trimming ou rejeição por
erro alto. Não houve pico censurado na fronteira nem pico ambíguo. Cada instante
identificável tem 18 resíduos. Seus valores satisfazem numericamente 1/2/3 px,
mas são diagnósticos sob identidade e não uma certificação, pois os scores
multimodais reprovaram. Agregados não substituíram nenhum gate por instante.

| Par | Índice/conjunto | n | Mediana px | P95 px | Máximo px |
| --- | --- | ---: | ---: | ---: | ---: |
| ESM2-to-ESM1 | 146 | 18 | 0,050202 | 0,197726 | 0,256090 |
| ESM2-to-ESM1 | 293 | 18 | 0,069906 | 0,183258 | 0,218738 |
| ESM2-to-ESM1 | agregado desenvolvimento | 36 | 0,065163 | 0,195255 | 0,256090 |
| ESM5-to-ESM4 | 197 | 18 | 0,059563 | 0,133394 | 0,139278 |
| ESM5-to-ESM4 | 394 | 18 | 0,059664 | 0,120851 | 0,130073 |
| ESM5-to-ESM4 | agregado desenvolvimento | 36 | 0,059664 | 0,130643 | 0,139278 |

Matriz, inversa, offset certificado e ROI retangular permanecem `null` nos dois
pares. Valores de roundtrip da identidade são apenas numéricos. Métricas de
holdout não foram medidas. Os resultados completos, scores de cada controle,
blocos, classes e resíduos constam de `result.json` em precisão integral.

O bloqueio decorre do protocolo congelado e não demonstra desalinhamento ou
impossibilidade física de congruência. Campos solutais são relativos/normalizados;
não se alega concentração absoluta/wt.% Bi, calibração de intensidade,
ground truth metrológico, convecção, causalidade, generalização, independência
entre frames, escala física ou incerteza completa.

## Verificação e fechamento

Antes de C1: 372 testes stdlib (298 passes, 74 skips opcionais, zero falhas/erros)
e suítes científicas separadas 5/16/26/27 passes, sem skips/falhas/erros.
Guardrails e 95 checksums textuais passaram; os RED reais anteriores à
implementação foram preservados. Revisão textual independente examinou
método, autoridade e integração antes de C1. `verification.json` registra a
custódia e conferência do resultado. Verificações após C3 e CI remota serão
registradas no Draft PR e retorno final; não há alegação antecipada de CI.

Não houve acesso a ESM3/ESM6, novos dados/frames, ZIP/MP4, FFmpeg/FFprobe,
redecodificação, labels, ledger, dataset ML, splits, baseline, CNN, treinamento,
TI-3+, instalação ou alteração do sistema. Nenhum binário experimental foi
escrito ou versionado. O PASS de fragmentação permanece intacto.

O registro solutal automático está encerrado: sem retry, correção de método
ou outro registrador. Alternativas futuras, dependentes de nova decisão:
scripts/coordenadas originais, documentação da produção dos vídeos normalizados,
landmarks humanos sob protocolo próprio, rederivação radiográfica ou nova aquisição.
Publicação somente por push fast-forward e Draft PR; sem Ready ou merge.

```text
TI2R_SOLUTE_DIRECT=BLOCKED_IDENTITY_NOT_DISCRIMINATIVE
G2_FRAG=PASS_DIRECT_RASTER_MAPPING
G2_SOLUTE=BLOCKED
G2_SPATIAL=PARTIAL_FRAG_ONLY
G3=PENDING_SEPARATE_DECISION
STATE=CLOSED_CONSUMED
CURRENT_AUTHORIZED_ACTIVITY=NONE_AWAITING_AUTHOR_DECISION
TI2R_EXECUTION_AUTHORIZED=false
TI3_PLUS_AUTHORIZED=false
MERGE_AUTHORIZED=false
```
