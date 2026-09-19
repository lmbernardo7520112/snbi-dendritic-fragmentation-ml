# TI2R-SOLUTE — auditoria anterior ao locked holdout

## Identidade, autoridade e custódia

Repositório: `lmbernardo7520112/snbi-dendritic-fragmentation-ml`.
Branch: `feat/ti2r-solute-v2-calibration`.
HEAD local, tracking e branch remota:
`0b820bc61e6dae3b7a98654a3b7d5cd292ca925e` (C2).
C1 científico: `e1a98917a20431ecc1c758f210b5e974b3533734`.
Base: `fcfc5e1445467248566e881c61929d4d3da7b1d8`.
O PR #10 foi consultado: OPEN/DRAFT, não integrado, head/base correspondentes.

Worktree e index estavam limpos na entrada. A preparação acrescenta somente
os arquivos novos anunciados; nenhuma alteração rastreada preexistente.
Os 250 itens do index são arquivos regulares, sem symlinks versionados.
A decisão específica do operador está preservada integralmente em
`authorization.md`; ela autoriza somente este gate, uma vez.
As autoridades históricas continuam consumidas. Não se modifica o estado
estático nem se chama o runner de desenvolvimento novamente.

## Freeze comprovado

Os 25 caminhos e hashes do receipt V2 foram comparados com os arquivos locais
e com os blobs de C1 e C2: igualdade exata. C2 tem C1 como pai e alterou somente
sete arquivos de evidência V2, enumerados em `verification.json`.
`frozen-manifest.json` registra os 25 hashes científicos, as configurações
completas V1/V2, os oito assets, a exposição e a consulta de CI.
`frozen-hashes.sha256` também autentica a orquestração e o próprio manifesto.

O matcher preservado está em
`src/snbi_fragmentation/ti2r_solute_direct_registration.py`; os critérios V2
em `src/snbi_fragmentation/ti2r_solute_v2_calibration.py`.
Configurações:
`configs/registration/ti2r-solute-direct-method.json` e
`configs/registration/ti2r-solute-v2-method.json`.
Protocolo: `docs/protocols/TI2R_SOLUTE_V2_PROTOCOL.md`.
Nenhum desses arquivos é editado.

## Aplicação mecânica aos casos reservados

V2-D possui wrapper exclusivo de três instantes DEV; ele não é invocado.
O adaptador operacional novo
`scripts/ti2r_solute_locked_evaluator.py` importa os kernels congelados.
Não se alega que esse adaptador estava em C1.
O caminho V1 `evaluate_series(..., holdout=True)` já define dois instantes
e controles temporais recíprocos. Seus resultados brutos alimentam exatamente
`_relative_original` e `calibrate_role` de V2, sem alterações.
A conjunção por positivo de V2 se aplica separadamente a todos os quatro
casos: ESM2→ESM1:73/219 e ESM5→ESM4:98/295.
Não se aplica a exceção DEV do índice zero, nem a antiga tolerância V1 de
um entre dois holdouts. NON_IDENTIFIABLE em qualquer caso resulta FAIL.

Preservados: Y nativo, SS8 e NGF, eta individual original, máscaras/grade/
checkerboard, 512 pixels por bloco, oito blocos por papel, quatro quadrantes;
49 offsets originais em [-3,3]², identidade única e margens espacial/temporal
>=0,005; tolerância de empate 1e-9; resíduos NGF mediana<=1, P95<=2,
máximo<=3 px, sem picos ambíguos/censurados ou descarte.
Os controles temporais brutos são preservados; a regra V2 condiciona o gate
à identificabilidade individual do moving temporal.

Para cada caso e métrica: identidade mais as mesmas 16 perturbações,
81 correções em [-4,4]², suporte comum com erosão oito, eta preservado,
máximo único no inverso verdadeiro, margem>=0,005, erro<=0,5 px,
16/16 recuperações e concordância SS8/NGF. Os pisos absolutos históricos
0,90/0,80 permanecem registrados, sem decidir V2.
Nenhuma matriz é ajustada ou escala física inferida.

## Inventário e exposição

| Fontes | Índices reservados por fonte | Bytes por buffer | Total |
| --- | --- | ---: | ---: |
| ESM1, ESM2 | 73, 219 | 1.951.506 | 7.806.024 |
| ESM4, ESM5 | 98, 295 | 1.940.004 | 7.760.016 |

Exatamente oito buffers existentes, total esperado 15.566.040 bytes.
Paths, dimensões, formato YUV420p/8 bits e hashes provêm exclusivamente do
manifesto textual piloto congelado. Nenhum path experimental foi examinado
na preparação. Não há DEV no allowlist desta execução.

Os receipts/resultados V1/V2 registram zero opens e zero bytes destes oito
buffers na avaliação solutal anterior. A ausência de exposição científica
solutal é documental, não uma prova forense universal. Os quatro buffers
de referência ESM1/ESM4 já foram abertos em FRAG-DIRECT, fato explicitamente
declarado em C1; os buffers móveis ESM2/ESM5 não foram analisados como holdout.
Todos tiveram decodificação/custódia mecânica histórica TI-2.
Logo, SEALED é específico à fase solutal e não significa virgindade global.
Trata-se de validação temporal interna nas mesmas aquisições.

## Verificação operacional e encerramento

Os dois arquivos novos de orquestração são congelados por hash antes dos
pixels. O runner admite somente HEAD C2, branch correta, textos idênticos,
configurações exatas, dependências NumPy 1.26.4/SciPy 1.11.4 e os oito IDs.
Receipt O_EXCL com fsync é criado antes dos bytes com timestamp, contador 1,
configurações e hashes; sua presença impede segunda invocação.
Cada ID é marcado como tentado antes de abrir, uma vez, com O_NOFOLLOW,
diretórios seguros, tamanho/hash conferidos e contador de bytes por chunk.
Nenhuma exceção tem retry ou fallback adaptativo.

A revisão independente e as verificações com mocks estão em
`verification.json`. A suíte stdlib passou 423 testes (337 passes e
86 skips opcionais). Guard de dados: PASS, 250 entradas, zero bytes.
CI C2 consultada: runs 35399554524 (push) e 35399558120 (pull_request);
ambos SUCCESS, dois jobs obrigatórios e todos os passos em sucesso.
Isso não representa CI de um futuro commit nem autorização adicional.

Antes da invocação: zero opens/bytes experimentais nesta tarefa.
A avaliação executará cada par uma única vez; os resultados desfavoráveis
serão preservados e todos os quatro casos serão julgados individualmente.
O primeiro resultado válido encerrará a ciência. Nenhuma mudança científica
posterior, nova tentativa, Ready, merge ou TI-3+ é autorizada.

PRE_HOLDOUT_GATE=PASS
