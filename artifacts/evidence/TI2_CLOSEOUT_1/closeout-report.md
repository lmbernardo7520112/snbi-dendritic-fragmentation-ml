# TI2-CLOSEOUT-1 — Reconciliação documental anterior à publicação

Este registro contém a evidência concluída antes do checkpoint. O resultado
terminal da publicação, o SHA completo do closeout, a URL do Draft PR e a CI
serão informados depois do commit ao operador e no PR. Não há autorreferência
ao SHA do commit que contém este arquivo.

## Autoridade e commits

- Branch: `feat/ti2-registration-calibration`.
- `TI2_EXECUTION_RESULT_COMMIT`: `f3c6da78b04299475c7bb85e986eb7435b08bd22`.
- Commits anteriores: `7e2223dd84346beebbccefe51afcead66a02d339`,
  `5e1c4dc2406e1b6fbcf71bd8d86d6d842f3af3ad`, seguidos pelo resultado acima.
- Autoridade integral: `docs/decisions/AUTHORIZATION-TI2-CLOSEOUT-1-2026-09-17.md`.
- Preflight: branch e remoto corretos, worktree inicialmente limpo, commits
  presentes, checkout standalone, sem `index.lock` e zero binários experimentais
  rastreados. Hooks ativos ausentes; configurações opcionais não definidas.
- Escopo: documentação, metadados, testes determinísticos, checkpoint, push,
  Draft PR e verificação da CI. TI-2R e TI-3–TI-8 permanecem proibidas.

```text
TI2_EXECUTION = TERMINAL_BLOCKED_PENDING_CLOSEOUT
METHOD_V1 = INSUFFICIENT_EVIDENCE
G2_SPATIAL = BLOCKED_METHOD_V1
TRANSFORM_EXISTENCE = UNDETERMINED
G3 = BLOCKED_DEPENDENCY_G2
E7 = PASS_DOCUMENTARY
TI3_PLUS_AUTHORIZED = false
```

Esses estados não aprovam registro, ROI ou uso científico posterior. CI verde
e documentação completa não aprovam G2-SPATIAL nem G3.

## Reconciliação temporal

`elapsed_from_first_frame_s = 1.18 × frame_index`.
`experimental_time_s = offset_s + elapsed_from_first_frame_s`.
Offsets: ESM1–3 = −25,96 s; ESM4–6 = −34,22 s. O zero experimental refere-se
à entrada da frente de solidificação no campo de visão.

| Fontes | Índice | Decorrido (s) | Experimental (s) |
|---|---:|---:|---:|
| ESM1–3 | 0 | 0,00 | −25,96 |
| ESM1–3 | 73 | 86,14 | 60,18 |
| ESM1–3 | 146 | 172,28 | 146,32 |
| ESM1–3 | 219 | 258,42 | 232,46 |
| ESM1–3 | 293 | 345,74 | 319,78 |
| ESM4–6 | 0 | 0,00 | −34,22 |
| ESM4–6 | 98 | 115,64 | 81,42 |
| ESM4–6 | 197 | 232,46 | 198,24 |
| ESM4–6 | 295 | 348,10 | 313,88 |
| ESM4–6 | 394 | 464,92 | 430,70 |

Os dez pontos e os 30 itens do manifesto foram verificados com `Decimal`.
O campo histórico `physical_time_s` conserva integralmente seus valores,
depreciado como alias de tempo decorrido. A API legada continua com sua
semântica original; nenhuma implementação foi alterada. As duas grandezas
explícitas foram acrescentadas aos metadados e seu modelo está
`DOCUMENTED_AND_RECONCILED`.

A reconciliação foi fornecida e aprovada pelo autor, citando Gibbs et al.,
JOM 68, 170–177 (2016), DOI `10.1007/s11837-015-1646-7`. Não se alega consulta
independente ao texto primário, nova observação ou análise de imagens.

## Escala e terminologia

A escala nominal documentada é **1,40 µm/pixel em X e Y**. O resultado raster
histórico, 500 µm/357 px = 1,40056022409 µm/px, é uma verificação compatível;
não foi recalculado a partir de pixels. Preserva-se o intervalo raster
[1,38888888889; 1,41242937853] µm/px, que não é intervalo estatístico de confiança.
A comparação decimal arredondada usa tolerância explícita de 10⁻¹¹.

A incerteza metrológica completa permanece `UNRESOLVED`; não existe certificado
de incerteza completa, conversão de coordenadas ou propagação para modalidades
sem registro certificado. G3 continua bloqueado por G2-SPATIAL, ROI e incerteza.

O piloto contém **30 frames-piloto decodificados dos MP4 sem perdas adicionais,
preservando a resolução e o formato de pixels nativos dos vídeos**. Arquivos
`.raw` são buffers de pixels sem cabeçalho decodificados dos MP4; **não são dados
brutos do detector**. Não se afirma que os MP4 originais sejam lossless.

Todos os valores originais dos 30 registros, hashes, índices, paths e tempos
legados foram preservados. Matrizes, ROI e configurações de registro não foram
alteradas. O SHA do manifesto textual muda por adição semântica; os hashes dos
frames permanecem iguais. Seu histórico anterior está preservado no commit de
resultado, sem reescrita de histórico.

## Testes e guardrails

| Execução | Executados | Aprovados | Ignorados | Falhas | Erros |
|---|---:|---:|---:|---:|---:|
| Histórico local, log `green-final-control.txt` | 102 | 102 | 0 | 0 | 0 |
| Histórico sem pacotes externos, documentado e reconfirmado no closeout | 102 | 97 | 5 | 0 | 0 |
| Closeout final, com 11 testes documentais novos | 113 | 108 | 5 | 0 | 0 |

Os cinco skips pertencem a `SyntheticImageMatchingTests`: ausência do runtime
opcional NumPy/SciPy no perfil sem dependências (`python -S`). Seus IDs e a
mensagem exata constam em `tests-final.json`. Nenhum teste foi apresentado como
aprovado quando ignorado. A nova verificação da suíte histórica está claramente
separada dos logs originais em `tests-history.json`. Um erro inicial de
serialização do coletor foi corrigido e documentado; não alterou testes ou logs
históricos nem constitui erro científico.

Passaram o guard de dados, o bootstrap/sanitização estático, o escopo TI-2, a
validação do manifesto de fontes, o manifesto-piloto e os novos contratos de
tempo/escala. O guard não varre diretórios ignorados. Não houve nova inspeção
do workspace experimental; a afirmação de sanitização preserva a atestação
histórica do autor e a exceção anterior do piloto ignorado.

`src/`, `scripts/` e `configs/registration/` têm diff vazio em relação ao commit
de resultado. A suíte usa somente fixtures sintéticas e texto. Não foram
executados FFmpeg, decodificação, leitura de pixels experimentais, observação
dos quartis, cálculo de correspondências, ajuste de parâmetros ou TI-2R.

Os checksums textuais são atualizados em `artifacts/evidence/TI2/checksums.sha256`,
sem hash circular do próprio arquivo. Hashes experimentais anteriores permanecem
como evidência histórica; nenhum arquivo experimental precisou ser reaberto.

## Publicação e pendências

O novo ato autoriza publicar este resultado terminal bloqueado apesar das
dependências científicas de E4/E5. Staging, commit, consulta remota e push
requerem aprovações pontuais; não há permissão para force-push, rebase ou merge.
O corpo preparado em `draft-pr-body.md` receberá o SHA real do closeout somente
após o commit, em cópia textual local ignorada.

O fechamento operacional só receberá PASS após commit, push, Draft PR aberto,
CI remota concluída com sucesso e worktree limpo. As verificações remotas ainda
não ocorreram no instante de criação deste registro. Permanecem para decisão
autoral: eventual TI-2R, revisão do método v1, orientação física, registro/ROI,
incerteza metrológica e revisão científica. Nenhum merge é autorizado.

## Allowlist exata do checkpoint

`CHECKPOINT_ID=TI2-CLOSEOUT-1`; `BASE_HEAD` é o commit de resultado acima.
Mensagem proposta: `docs(ti2): reconcile terminal blocked closeout`.
São 27 arquivos textuais; os 11 testes novos protegem somente as correções
documentais. Ficam bloqueados `src/`, `scripts/`, `configs/registration/`,
dados experimentais, credenciais e qualquer caminho fora desta allowlist.

- `AGENTS.md`
- `README.md`
- `artifacts/evidence/G2_SPATIAL/registration-report.json`
- `artifacts/evidence/G3/calibration-report.json`
- `artifacts/evidence/TI2/checksums.sha256`
- `artifacts/evidence/TI2/contract-results.json`
- `artifacts/evidence/TI2/execution-report.md`
- `artifacts/evidence/TI2/terminal-state.json`
- `artifacts/evidence/TI2_CLOSEOUT_1/closeout-report.md`
- `artifacts/evidence/TI2_CLOSEOUT_1/commands.json`
- `artifacts/evidence/TI2_CLOSEOUT_1/draft-pr-body.md`
- `artifacts/evidence/TI2_CLOSEOUT_1/preflight.json`
- `artifacts/evidence/TI2_CLOSEOUT_1/tests-final.json`
- `artifacts/evidence/TI2_CLOSEOUT_1/tests-final.txt`
- `artifacts/evidence/TI2_CLOSEOUT_1/tests-history.json`
- `artifacts/metadata/ti2-pilot-manifest.json`
- `configs/calibration/bottom-up.json`
- `configs/calibration/top-down.json`
- `configs/time_rule.json`
- `docs/decisions/AUTHORIZATION-TI2-CLOSEOUT-1-2026-09-17.md`
- `docs/gates/TI2_GATE_PLAN.md`
- `docs/protocols/LOCAL_DEVELOPMENT.md`
- `docs/protocols/TI2_CONTRACT_MATRIX.md`
- `docs/protocols/TI2_EXECUTION_PLAN.md`
- `docs/risks/TI2_RISK_REGISTER.md`
- `docs/security/LOCAL_SANDBOX.md`
- `tests/test_ti2_closeout.py`
