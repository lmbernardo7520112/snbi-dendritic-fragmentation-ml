# TI2R-FRAG — encerramento da única tentativa de 2026-09-18

**TI2R_FRAG=BLOCKED_REFERENCE_INSUFFICIENT; G2_FRAG=BLOCKED.**
Autoridade específica: **CLOSED_CONSUMED**. Não houve retry, ajuste posterior,
novos frames ou abertura dos quartis. Este resultado não demonstra inexistência
física de uma transformação. A fase termina aguardando decisão do autor.

## Commits e execução

Branch: `feat/ti2r-frag-registration`; base
`0245faf74aa15424d95d43f92e87b32a06ac987b`.
C1: `5f9c22a0cfc75622614734e8eb288104f04da827`, protocolo e implementação
inativos, com testes sintéticos anteriores aos pixels.
C2: `40874c92e65fbd13a05be7b8d98aa17fadd1f79c`, somente autoridade e decisão.
C3 contém este encerramento; seu SHA e a publicação pertencem ao histórico
Git, ao corpo do Draft PR e ao retorno ao operador, evitando autorreferência.

O comando `PYTHONPATH=src /usr/bin/python3 -B scripts/run_ti2r_frag.py` foi
invocado **exatamente uma vez**, no sandbox padrão; retornou código 2, resultado
científico terminal previsto. `receipt.json` foi criado com O_EXCL e fsync antes
dos bytes, contendo SHA C2, oito hashes de textos congelados, allowlist, custódia
e contador 1. Nenhum código, parâmetro, máscara, métrica, limiar ou ordem de
modelos mudou depois de C2. Não houve execução de `scripts/run_ti2.py`.

## Acesso efetivo e validação

Autorizados: 20 buffers nativos existentes. Abertos e autenticados: **12 buffers
de desenvolvimento, 23.401.890 bytes**, exatamente ESM1/ESM3 nos índices
0/146/293 e ESM4/ESM6 em 0/197/394. Cada um foi aberto uma única vez para leitura,
com tamanho e SHA-256 correspondentes ao manifesto congelado.

Os oito buffers de validação — ESM1/ESM3:73/219; ESM4/ESM6:98/295 — tinham
custódia documental positiva, mas permaneceram **NOT_OPENED**, pois nenhum
candidato passou desenvolvimento. Não houve nova exposição de validação,
visualização experimental, acesso a ESM2/ESM5, ZIP/MP4, FFmpeg/FFprobe,
redecodificação, instalação, alteração do sistema, conversão física, labels,
ledger de eventos, dataset ML, splits, treinamento ou TI-3+.

## Resultado por par

Ambos avaliaram somente **M0_IDENTITY**. Nenhum primeiro modelo aprovado;
matriz e inversa selecionadas são `null`. Identidade aparece no histórico de
avaliação como hipótese testada, sem certificação. M1–M3 não foram executados,
porque a regra congelada interrompe o par quando não há referência independente
com cobertura suficiente. A falha de cobertura não foi contornada por médias.

| Par | Índice | Tiles válidos | Quadrantes | Suporte | Mediana px | P95 px | Máximo px | Estado do instante |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| ESM3-to-ESM1 | 0 | 0 | 0 | 99.7861% | null | null | null | BLOCKED_REFERENCE_INSUFFICIENT |
| ESM3-to-ESM1 | 146 | 9 | 4 | 79.7373% | 0.221076 | 0.987795 | 1.015915 | FAIL_ABSOLUTE_SUPPORT |
| ESM3-to-ESM1 | 293 | 9 | 4 | 79.4594% | 0.209944 | 0.586855 | 0.694281 | FAIL_ABSOLUTE_SUPPORT |
| ESM6-to-ESM4 | 0 | 1 | 1 | 99.6496% | 10.129615 | 10.129615 | 10.129615 | BLOCKED_REFERENCE_INSUFFICIENT |
| ESM6-to-ESM4 | 197 | 14 | 4 | 97.1965% | 0.285760 | 0.745947 | 0.851860 | PASS |
| ESM6-to-ESM4 | 394 | 14 | 4 | 97.1952% | 0.131437 | 0.283365 | 0.314637 | PASS |

ESM3→ESM1: o índice 0 apresentou 16 tiles indisponíveis por textura de referência;
nenhum residual foi medido nesse instante. Nos índices 146 e 293, sete tiles
falharam suporte e o suporte global ficou abaixo de 90%. Os 18 resíduos
sobreviventes têm mediana 0,212087, P95 0,956159 e máximo 1,015915 px. O PASS
numérico desse agregado não passa o par nem substitui cobertura por instante.

ESM6→ESM4: o índice 0 teve 12 tiles indisponíveis por textura de referência e
três por textura móvel. O único residual válido, **10,129615 px**, foi preservado;
nenhum descarte por erro alto ocorreu. Os 29 resíduos agregados têm mediana
0,213231, P95 0,786683 e máximo 10,129615 px. Os instantes 197 e 394 passaram seus
critérios isolados, mas não certificam a transformação estática para o par.

Determinante de M0=1 e roundtrip=0 px: apenas verificações numéricas.
Métricas de validação: **não medidas**. Não houve retorno à estimação.

## Suporte, ROI e limites

Sob a hipótese identidade, a interseção das máscaras de desenvolvimento contém
745.211 pixels para ESM3→ESM1, bounding box [6,125,1273,864], e 907.040 para
ESM6→ESM4, bounding box [6,124,1273,858], em coordenadas xyxy com limite superior
exclusivo. São diagnósticos da hipótese testada; **não são ROI certificada**.
ROI retangular permanece `null`; nenhuma máscara experimental foi exportada.
O suporte ≥90% usa como denominador pixels elegíveis da referência após as
exclusões congeladas, não o canvas completo. Cada tile exige suporte integral.

O bloqueio é específico ao método, à grade, às máscaras, à cobertura e aos
instantes congelados. As métricas não são ground truth metrológico. Não se
infere impossibilidade de registro, orientação física, escala, comparação
entre condições ou validade de outros frames. G2_SOLUTE=NOT_EXECUTED.
G2_SPATIAL=BLOCKED_METHOD_V1 e G3=BLOCKED_DEPENDENCY_G2 permanecem históricos;
nenhum gate científico é aberto por testes ou CI verdes.

## Fechamento e publicação

`verification.json` registra os testes e guardrails reais. O perfil stdlib tem
261 testes, 240 passes e 21 skips opcionais; os cinco testes científicos legados
e os 16 novos são executados separadamente com zero skips/falhas/erros.
Os 95 checksums textuais históricos permanecem verificáveis. Os hashes dos
textos congelados e o receipt preservam a proveniência desta tentativa.
A revisão textual independente não encontrou divergência restante de custódia,
autoridade ou referência antes de C1; isso não substitui a avaliação científica.

C3 fecha definitivamente a autoridade antes de qualquer push. Publicação
limitada a fast-forward da branch e Draft PR contra main, seguida de CI
automática no SHA C3. Sem Ready, merge, rerun ou novo commit corretivo.
O resultado remoto efetivamente observado será comunicado no PR/retorno final.

```text
TI2R_FRAG=BLOCKED_REFERENCE_INSUFFICIENT
G2_FRAG=BLOCKED
G2_SOLUTE=NOT_EXECUTED
STATE=CLOSED_CONSUMED
CURRENT_AUTHORIZED_ACTIVITY=NONE_AWAITING_AUTHOR_DECISION
TI2R_EXECUTION_AUTHORIZED=false
TI3_PLUS_AUTHORIZED=false
MERGE_AUTHORIZED=false
```
