# TI2R-FRAG-DIRECT — resultado terminal de 2026-09-18

**TI2R_FRAG_DIRECT=PASS; G2_FRAG=PASS_DIRECT_RASTER_MAPPING.**
Ambos os pares certificaram offset inteiro `(0, 0)` no protocolo congelado,
com validação temporal interna à mesma aquisição. A autoridade específica está
**CLOSED_CONSUMED**; TI-3+ e merge deste novo PR permanecem não autorizados.

## Proveniência e execução única

PR #7 integrado por merge commit `b7bbb6a1f0d3eaa43866027762eb2ed061c3d7c6`,
com histórico preservado, branches mantidas e CI pós-merge 35342342511 SUCCESS.
Nova branch: `feat/ti2r-frag-direct-mapping`.

- C1: `cf84c5ef1c5b6f8efb39b87825d9bc08f34014b7`, método congelado e inativo.
- C2: `a91b7093ce7dff530ab9020d5f69c30d365c10f5`, somente autoridade e decisão.
- C3 contém resultados e encerramento; seu SHA efetivo pertence ao histórico,
  ao Draft PR e ao retorno ao autor, sem autorreferência neste arquivo.

`PYTHONPATH=src /usr/bin/python3 -B scripts/run_ti2r_frag_direct.py` foi invocado
**uma única vez**, no sandbox padrão, retornando código **0**. O receipt foi
criado exclusivamente, com fsync, antes dos bytes; contador 1, SHA C2 e 12 hashes
textuais congelados. Esses 12 textos continuam idênticos a C1. Não houve mudança
do método, parâmetros, máscaras ou limiares depois de C2, nem retry.

Os 20 buffers previamente existentes foram autenticados e abertos uma vez
cada: 12 de desenvolvimento (23.401.890 bytes) e oito de holdout (15.601.260
bytes), total 39.003.150 bytes. Os dois desenvolvimentos terminaram antes de
qualquer holdout. Cada par passou e teve seu offset gravado em arquivo exclusivo
de freeze antes de abrir seus quatro ativos reservados.

Holdouts efetivamente abertos: **ESM1/ESM3:73/219; ESM4/ESM6:98/295**.
Nenhum outro ativo foi aberto. Os registros de freeze preservam o estado
`holdout_opened=false` daquele instante anterior à validação; o resultado final
registra os oito acessos posteriores, sem reescrever o freeze.

## Candidatos, identificação e certificação

ESM3→ESM1: 21 candidatos, `offset_x=0..2`, `offset_y=0..6`.
ESM6→ESM4: três candidatos, `offset_x=0..2`, `offset_y=0`.
Todos os candidatos foram comparados nos oito instantes identificáveis.
O único vencedor foi `(0, 0)` em todos; matrizes e inversas certificadas são
identidade. Convenção móvel→referência: `x_ref=x_mov-offset_x`,
`y_ref=y_mov-offset_y`. Não foi estimada transformação subpixel.

Em ambos os pares, o índice 0 foi **NON_IDENTIFIABLE**, exclusivamente por
informação insuficiente da referência; não recebeu PASS nem residual. Foram
IDENTIFIABLE os índices 146/293 e 73/219 de ESM3→ESM1, e 197/394 e 98/295 de
ESM6→ESM4. Cada instante identificável passou com 18 blocos de auditoria e
quatro quadrantes. Nenhum bloco/residual foi descartado por erro alto.

As margens vencedoras variaram de 0,024971 a 0,050537, acima da margem congelada
0,005. A seleção utilizou blocos diferentes dos blocos que mediram os resíduos.
Máscaras parciais foram aceitas; não se aplicou gate global de 90% ou suporte
integral de tile. A correlação local mediu somente erro, sem corrigir o offset.

| Par | Fase | Índice | Estado | n | Mediana px | P95 px | Máximo px |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: |
| ESM3→ESM1 | desenvolvimento | 0 | NON_IDENTIFIABLE | 0 | — | — | — |
| ESM3→ESM1 | desenvolvimento | 146 | PASS | 18 | 0,187071 | 0,297418 | 0,323875 |
| ESM3→ESM1 | desenvolvimento | 293 | PASS | 18 | 0,234550 | 0,384684 | 0,392677 |
| ESM3→ESM1 | holdout | 73 | PASS | 18 | 0,144926 | 0,287942 | 0,323527 |
| ESM3→ESM1 | holdout | 219 | PASS | 18 | 0,213879 | 0,365353 | 0,381952 |
| ESM6→ESM4 | desenvolvimento | 0 | NON_IDENTIFIABLE | 0 | — | — | — |
| ESM6→ESM4 | desenvolvimento | 197 | PASS | 18 | 0,329877 | 0,477883 | 0,542770 |
| ESM6→ESM4 | desenvolvimento | 394 | PASS | 18 | 0,298244 | 0,446363 | 0,472556 |
| ESM6→ESM4 | holdout | 98 | PASS | 18 | 0,358003 | 0,574890 | 0,598701 |
| ESM6→ESM4 | holdout | 295 | PASS | 18 | 0,310345 | 0,429738 | 0,438166 |

| Par | Agregado separado | n | Mediana px | P95 px | Máximo px |
| --- | --- | ---: | ---: | ---: | ---: |
| ESM3→ESM1 | desenvolvimento | 36 | 0,204791 | 0,338725 | 0,392677 |
| ESM3→ESM1 | holdout | 36 | 0,193474 | 0,348816 | 0,381952 |
| ESM6→ESM4 | desenvolvimento | 36 | 0,300419 | 0,467963 | 0,542770 |
| ESM6→ESM4 | holdout | 36 | 0,335231 | 0,545193 | 0,598701 |

Todos os instantes identificáveis e os agregados separados satisfazem
mediana≤1 px, P95≤2 px e máximo≤3 px. Os agregados não substituíram nenhum
critério por instante. `result.json` conserva precisão completa, scores de
todos os candidatos, suporte, classificação de referência e resíduos por bloco.

## Limites e encerramento

A certificação é do mapeamento raster no protocolo e piloto autorizados.
Não é validação experimental externa, ground truth metrológico, determinação
de orientação física, escala ou autorização para novos frames. O índice inicial
não oferece evidência própria de alinhamento. ROI retangular permanece `null`;
nenhuma máscara experimental, imagem ou novo binário foi exportado/versionado.
Determinante 1 e roundtrip 0 px são verificações numéricas, não metrologia.

Os resultados bloqueados anteriores permanecem preservados. Não houve acesso a
ESM2/ESM5, ZIP/MP4, FFmpeg/FFprobe, nova decodificação, dados adicionais,
conversão física, labels, ledger, dataset ML, splits, baseline, CNN, treinamento
ou TI-3+. Nenhuma instalação ou alteração do sistema operacional.

Antes de C1: 313 testes stdlib, 266 passes, 47 skips opcionais e zero falhas/erros;
as suítes científicas separadas tiveram 5, 16 e 26 passes, sem skips/falhas/erros.
Guardrails e os 95 checksums textuais passaram. Os RED preservados são falhas
reais de importação anteriores à implementação, não resultados científicos.
`verification.json` registra a custódia textual e fechamento. As verificações
após C3 e CI remota serão comunicadas no Draft PR e retorno terminal.

C3 fecha a autoridade antes do push. Publicação autorizada somente por push
fast-forward e Draft PR contra main; sem Ready, merge, rerun ou commit corretivo.

```text
TI2R_FRAG_DIRECT=PASS
G2_FRAG=PASS_DIRECT_RASTER_MAPPING
G2_SPATIAL=PARTIAL_PENDING_G2_SOLUTE
G2_SOLUTE=NOT_EXECUTED
G3=BLOCKED_OR_PENDING_G2_COMPLETE
STATE=CLOSED_CONSUMED
CURRENT_AUTHORIZED_ACTIVITY=NONE_AWAITING_AUTHOR_DECISION
TI2R_EXECUTION_AUTHORIZED=false
TI3_PLUS_AUTHORIZED=false
MERGE_AUTHORIZED=false
```
