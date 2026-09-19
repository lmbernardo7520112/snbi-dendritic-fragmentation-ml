# TI2R-SOLUTE-V2-D — execução única e encerramento de desenvolvimento

**TI2R_SOLUTE_V2_DEV=PASS_PROTOCOL_FROZEN_READY_FOR_HOLDOUT_DECISION.**
**G2_SOLUTE=BLOCKED_PENDING_LOCKED_HOLDOUT; HOLDOUT_SOLUTE=SEALED.**

Os quatro positivos passaram individualmente. A autoridade específica está CLOSED_CONSUMED. Este PASS de desenvolvimento não certifica G2_SOLUTE nem autoriza holdout, metrologia, concentração absoluta ou TI-3+.

## Custódia Git e CI

PR #9: merge governado PASS, SHA `fcfc5e1445467248566e881c61929d4d3da7b1d8`, preservando ambos os pais e a branch. A árvore integrada é igual ao head auditado `fef9aa5437c6b39fa29f085498551a208982f9de`. CI pós-merge [35377213285](https://github.com/lmbernardo7520112/snbi-dendritic-fragmentation-ml/actions/runs/35377213285) SUCCESS em ambos os jobs e todos os passos. A main foi sincronizada exclusivamente por fast-forward.

Branch: `feat/ti2r-solute-v2-calibration`; [Draft PR #10](https://github.com/lmbernardo7520112/snbi-dendritic-fragmentation-ml/pull/10).
C1: `e1a98917a20431ecc1c758f210b5e974b3533734`. O commit e sua publicação antecederam os pixels.
- CI C1 push: [35397978695](https://github.com/lmbernardo7520112/snbi-dendritic-fragmentation-ml/actions/runs/35397978695), SUCCESS; deterministic-contracts e scientific-synthetic-contracts e todos os seus passos aprovados.
- CI C1 pull_request: [35398305900](https://github.com/lmbernardo7520112/snbi-dendritic-fragmentation-ml/actions/runs/35398305900), SUCCESS; deterministic-contracts e scientific-synthetic-contracts e todos os seus passos aprovados.

C2 contém somente este encerramento e evidências. Seu SHA e a CI final são observações posteriores, registradas no corpo efetivo do Draft PR e no retorno ao autor; não se inventa autorreferência. O PR deve permanecer OPEN/DRAFT, sem Ready ou merge.

## Invocação e fronteira experimental

Comando executado exatamente uma vez, no sandbox padrão, exit 0:

```bash
PYTHONPATH=src /usr/bin/python3 -B scripts/run_ti2r_solute_v2.py
```

A evidência sanitizada das duas CIs foi fornecida via stdin e está integralmente no receipt. Receipt O_EXCL com fsync e contador 1 antecedeu qualquer byte; contém C1, 25 hashes de textos, allowlist e exposição. Não houve retry. terminal-state.json foi gravado antes de result.json; seu tombstone impede nova execução.

Foram abertos uma vez cada os seguintes 12 buffers existentes, totalizando **23.349.060 bytes**:

- `data/derived/ti2-pilot/ESM1-0000.raw`: 1951506 bytes; hash nativo validado, PASS, uma abertura.
- `data/derived/ti2-pilot/ESM2-0000.raw`: 1951506 bytes; hash nativo validado, PASS, uma abertura.
- `data/derived/ti2-pilot/ESM1-0146.raw`: 1951506 bytes; hash nativo validado, PASS, uma abertura.
- `data/derived/ti2-pilot/ESM2-0146.raw`: 1951506 bytes; hash nativo validado, PASS, uma abertura.
- `data/derived/ti2-pilot/ESM1-0293.raw`: 1951506 bytes; hash nativo validado, PASS, uma abertura.
- `data/derived/ti2-pilot/ESM2-0293.raw`: 1951506 bytes; hash nativo validado, PASS, uma abertura.
- `data/derived/ti2-pilot/ESM4-0000.raw`: 1940004 bytes; hash nativo validado, PASS, uma abertura.
- `data/derived/ti2-pilot/ESM5-0000.raw`: 1940004 bytes; hash nativo validado, PASS, uma abertura.
- `data/derived/ti2-pilot/ESM4-0197.raw`: 1940004 bytes; hash nativo validado, PASS, uma abertura.
- `data/derived/ti2-pilot/ESM5-0197.raw`: 1940004 bytes; hash nativo validado, PASS, uma abertura.
- `data/derived/ti2-pilot/ESM4-0394.raw`: 1940004 bytes; hash nativo validado, PASS, uma abertura.
- `data/derived/ti2-pilot/ESM5-0394.raw`: 1940004 bytes; hash nativo validado, PASS, uma abertura.

Oito holdouts: ESM1/ESM2:73/219 e ESM4/ESM5:98/295. **open_count=0; content_bytes_read=0 para cada um e para o conjunto.** Nenhum quartil foi aberto, revalidado por hash ou inspecionado nesta fase. As referências tiveram exposição histórica em FRAG-DIRECT; as modalidades móveis soluto não foram analisadas em holdout. SEALED qualifica esta fase, sem alegar virgindade global das referências.

Não houve MP4/ZIP, FFmpeg/FFprobe, novo frame, redecodificação, visualização, instalação, credenciais ou alteração do sistema. Nenhum dado binário foi versionado.

## Critérios e alcance

V1 permanece byte a byte preservado: código, configuração, resultado e receipt. Seus pisos SS8>=0,90/NGF>=0,80 são históricos e continuam não atingidos. V2 não baixou nem substituiu esses pisos: usa discriminação relativa e recuperação discreta, com margens mínimas de 0,005. SS8/NGF, eta, máscaras, identificabilidade, grade, controles e resíduos V1 permanecem inalterados.

As 16 translações autorizadas e a grade fixa de 81 correções foram congeladas em C1. O suporte comum exclui deslocamento líquido até oito pixels mais footprint do descritor. Translações inteiras são avaliadas por pullback exato dos descritores, sem interpolação, wrap ou pixels de padding. O teste sintético confronta isso com luminância efetivamente traduzida e kernels V1 recalculados.

A correção verdadeira é o inverso -p da perturbação p; correção não significa transformação experimental certificada. Erro discreto zero mede a recuperação do deslocamento conhecido neste benchmark. Não é incerteza metrológica, validação independente da referência ou generalização. A unidade experimental permanece a aquisição, aproximadamente uma corrida por condição; nenhum p-valor ou pseudorreplicação.

## Resultados originais por positivo

| Par / índice | SS8 | Margem espacial SS8 | NGF | Margem espacial NGF | Mediana / P95 / máximo px | Estado |
|---|---:|---:|---:|---:|---|---|
| ESM2-to-ESM1:146 | 0.775895387 | 0.011709334 | 0.537644136 | 0.018070786 | 0.050202212 / 0.197726255 / 0.256089614 | PASS |
| ESM2-to-ESM1:293 | 0.756524568 | 0.010596962 | 0.531850393 | 0.021633445 | 0.069905842 / 0.183257778 / 0.218738483 | PASS |
| ESM5-to-ESM4:197 | 0.783139952 | 0.012550034 | 0.573308729 | 0.024322978 | 0.059563271 / 0.133393748 / 0.139277576 | PASS |
| ESM5-to-ESM4:394 | 0.748236337 | 0.010994075 | 0.532965831 | 0.019902340 | 0.059664113 / 0.120851133 / 0.130072638 | PASS |

Em cada positivo, cada métrica contou com 18 blocos e quatro quadrantes; os 18 resíduos NGF originais foram mantidos, sem censura, ambiguidade ou rejeição por erro. Identidade foi máximo único, rank 1, em ambos os descritores. Os limites geométricos 1/2/3 px foram atendidos em cada instante, não apenas no agregado.

Os dois instantes iniciais são NON_IDENTIFIABLE, preservados como controles de observabilidade. Não receberam calibração positiva nem PASS/FAIL. Informação individual completa está em result.json.

## Controles temporais preservados

| Par | Referência | Móvel | SS8 | Margem SS8 | NGF | Margem NGF | Estado |
|---|---:|---:|---:|---:|---:|---:|---|
| ESM2-to-ESM1 | 0 | 146 | null | null | null | null | NOT_MEASURABLE_CORRECT_PAIR_NON_IDENTIFIABLE |
| ESM2-to-ESM1 | 0 | 293 | null | null | null | null | NOT_MEASURABLE_CORRECT_PAIR_NON_IDENTIFIABLE |
| ESM2-to-ESM1 | 146 | 0 | 0.676211220 | 0.099684167 | 0.480878462 | 0.056765674 | MEASURED |
| ESM2-to-ESM1 | 146 | 293 | 0.653999668 | 0.121895719 | 0.404473825 | 0.133170312 | MEASURED |
| ESM2-to-ESM1 | 293 | 0 | 0.675915981 | 0.080608586 | 0.484553627 | 0.047296766 | MEASURED |
| ESM2-to-ESM1 | 293 | 146 | 0.665549563 | 0.090975005 | 0.409740701 | 0.122109691 | MEASURED |
| ESM5-to-ESM4 | 0 | 197 | null | null | null | null | NOT_MEASURABLE_CORRECT_PAIR_NON_IDENTIFIABLE |
| ESM5-to-ESM4 | 0 | 394 | null | null | null | null | NOT_MEASURABLE_CORRECT_PAIR_NON_IDENTIFIABLE |
| ESM5-to-ESM4 | 197 | 0 | 0.675198769 | 0.107941184 | 0.480925532 | 0.092383198 | MEASURED |
| ESM5-to-ESM4 | 197 | 394 | 0.649635457 | 0.133504495 | 0.402775256 | 0.170533473 | MEASURED |
| ESM5-to-ESM4 | 394 | 0 | 0.677888677 | 0.070347661 | 0.489776426 | 0.043189405 | MEASURED |
| ESM5-to-ESM4 | 394 | 197 | 0.655526613 | 0.092709724 | 0.411361191 | 0.121604640 | MEASURED |

Todas as oito comparações mensuráveis tiveram margens >0,005 nas duas métricas. Quatro controles com referência inicial não identificável permanecem não mensuráveis, sem conversão em evidência favorável. Todos os controles originais e seus scores por bloco são preservados.

## Matriz das perturbações

Cada linha reporta as duas métricas separadamente. Δ é score verdadeiro menos o melhor concorrente; como todos os inversos verdadeiros venceram de forma única, equivale à margem para o segundo colocado. O segundo score, a margem do vencedor, todos os 81 candidatos e a matriz 17x81 de cada bloco constam em result.json. Valores abaixo arredondados apenas para apresentação; decisões usaram precisão integral.

### ESM2-to-ESM1:146 — PASS

SS8: 16/16; NGF: 16/16. Ambos concordam em todos os inversos. Cobertura por métrica: 18 blocos, quatro quadrantes.

| p=(dx,dy) | Inverso | SS8 | Δ SS8 | Rank SS8 | Erro SS8 px | NGF | Δ NGF | Rank NGF | Erro NGF px |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| (1, 0) | (-1, 0) | 0.775869196 | 0.011708436 | 1 | 0.0 | 0.537644136 | 0.018070786 | 1 | 0.0 |
| (-1, 0) | (1, 0) | 0.775869196 | 0.011708436 | 1 | 0.0 | 0.537644136 | 0.018070786 | 1 | 0.0 |
| (0, 1) | (0, -1) | 0.775869196 | 0.011708436 | 1 | 0.0 | 0.537644136 | 0.018070786 | 1 | 0.0 |
| (0, -1) | (0, 1) | 0.775869196 | 0.011708436 | 1 | 0.0 | 0.537644136 | 0.018070786 | 1 | 0.0 |
| (2, 0) | (-2, 0) | 0.775869196 | 0.011708436 | 1 | 0.0 | 0.537644136 | 0.018070786 | 1 | 0.0 |
| (-2, 0) | (2, 0) | 0.775869196 | 0.011708436 | 1 | 0.0 | 0.537644136 | 0.018070786 | 1 | 0.0 |
| (0, 2) | (0, -2) | 0.775869196 | 0.011708436 | 1 | 0.0 | 0.537644136 | 0.018070786 | 1 | 0.0 |
| (0, -2) | (0, 2) | 0.775869196 | 0.011708436 | 1 | 0.0 | 0.537644136 | 0.018070786 | 1 | 0.0 |
| (4, 0) | (-4, 0) | 0.775869196 | 0.011708436 | 1 | 0.0 | 0.537644136 | 0.018746563 | 1 | 0.0 |
| (-4, 0) | (4, 0) | 0.775869196 | 0.011866207 | 1 | 0.0 | 0.537644136 | 0.018070786 | 1 | 0.0 |
| (0, 4) | (0, -4) | 0.775869196 | 0.011708436 | 1 | 0.0 | 0.537644136 | 0.018070786 | 1 | 0.0 |
| (0, -4) | (0, 4) | 0.775869196 | 0.011708436 | 1 | 0.0 | 0.537644136 | 0.018070786 | 1 | 0.0 |
| (2, 2) | (-2, -2) | 0.775869196 | 0.011708436 | 1 | 0.0 | 0.537644136 | 0.018070786 | 1 | 0.0 |
| (2, -2) | (-2, 2) | 0.775869196 | 0.011708436 | 1 | 0.0 | 0.537644136 | 0.018070786 | 1 | 0.0 |
| (-2, 2) | (2, -2) | 0.775869196 | 0.011708436 | 1 | 0.0 | 0.537644136 | 0.018070786 | 1 | 0.0 |
| (-2, -2) | (2, 2) | 0.775869196 | 0.011708436 | 1 | 0.0 | 0.537644136 | 0.018070786 | 1 | 0.0 |

Controle positivo identidade SS8: score 0.775869196, margem 0.011708436, rank 1, erro 0.0 px, PASS; suporte comum 258530 pixels nos blocos desse papel.

Controle positivo identidade NGF: score 0.537644136, margem 0.018070786, rank 1, erro 0.0 px, PASS; suporte comum 258530 pixels nos blocos desse papel.

### ESM2-to-ESM1:293 — PASS

SS8: 16/16; NGF: 16/16. Ambos concordam em todos os inversos. Cobertura por métrica: 18 blocos, quatro quadrantes.

| p=(dx,dy) | Inverso | SS8 | Δ SS8 | Rank SS8 | Erro SS8 px | NGF | Δ NGF | Rank NGF | Erro NGF px |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| (1, 0) | (-1, 0) | 0.756425917 | 0.010568424 | 1 | 0.0 | 0.531850393 | 0.021633445 | 1 | 0.0 |
| (-1, 0) | (1, 0) | 0.756425917 | 0.010568424 | 1 | 0.0 | 0.531850393 | 0.021633445 | 1 | 0.0 |
| (0, 1) | (0, -1) | 0.756425917 | 0.010568424 | 1 | 0.0 | 0.531850393 | 0.021633445 | 1 | 0.0 |
| (0, -1) | (0, 1) | 0.756425917 | 0.010568424 | 1 | 0.0 | 0.531850393 | 0.021633445 | 1 | 0.0 |
| (2, 0) | (-2, 0) | 0.756425917 | 0.010568424 | 1 | 0.0 | 0.531850393 | 0.021633445 | 1 | 0.0 |
| (-2, 0) | (2, 0) | 0.756425917 | 0.010568424 | 1 | 0.0 | 0.531850393 | 0.021633445 | 1 | 0.0 |
| (0, 2) | (0, -2) | 0.756425917 | 0.010568424 | 1 | 0.0 | 0.531850393 | 0.021633445 | 1 | 0.0 |
| (0, -2) | (0, 2) | 0.756425917 | 0.010568424 | 1 | 0.0 | 0.531850393 | 0.021633445 | 1 | 0.0 |
| (4, 0) | (-4, 0) | 0.756425917 | 0.010568424 | 1 | 0.0 | 0.531850393 | 0.021633445 | 1 | 0.0 |
| (-4, 0) | (4, 0) | 0.756425917 | 0.010568424 | 1 | 0.0 | 0.531850393 | 0.021633445 | 1 | 0.0 |
| (0, 4) | (0, -4) | 0.756425917 | 0.010568424 | 1 | 0.0 | 0.531850393 | 0.021716747 | 1 | 0.0 |
| (0, -4) | (0, 4) | 0.756425917 | 0.010946064 | 1 | 0.0 | 0.531850393 | 0.021633445 | 1 | 0.0 |
| (2, 2) | (-2, -2) | 0.756425917 | 0.010568424 | 1 | 0.0 | 0.531850393 | 0.021633445 | 1 | 0.0 |
| (2, -2) | (-2, 2) | 0.756425917 | 0.010568424 | 1 | 0.0 | 0.531850393 | 0.021633445 | 1 | 0.0 |
| (-2, 2) | (2, -2) | 0.756425917 | 0.010568424 | 1 | 0.0 | 0.531850393 | 0.021633445 | 1 | 0.0 |
| (-2, -2) | (2, 2) | 0.756425917 | 0.010568424 | 1 | 0.0 | 0.531850393 | 0.021633445 | 1 | 0.0 |

Controle positivo identidade SS8: score 0.756425917, margem 0.010568424, rank 1, erro 0.0 px, PASS; suporte comum 258530 pixels nos blocos desse papel.

Controle positivo identidade NGF: score 0.531850393, margem 0.021633445, rank 1, erro 0.0 px, PASS; suporte comum 258530 pixels nos blocos desse papel.

### ESM5-to-ESM4:197 — PASS

SS8: 16/16; NGF: 16/16. Ambos concordam em todos os inversos. Cobertura por métrica: 18 blocos, quatro quadrantes.

| p=(dx,dy) | Inverso | SS8 | Δ SS8 | Rank SS8 | Erro SS8 px | NGF | Δ NGF | Rank NGF | Erro NGF px |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| (1, 0) | (-1, 0) | 0.783151896 | 0.012552306 | 1 | 0.0 | 0.573308729 | 0.024322978 | 1 | 0.0 |
| (-1, 0) | (1, 0) | 0.783151896 | 0.012552306 | 1 | 0.0 | 0.573308729 | 0.024322978 | 1 | 0.0 |
| (0, 1) | (0, -1) | 0.783151896 | 0.012552306 | 1 | 0.0 | 0.573308729 | 0.024322978 | 1 | 0.0 |
| (0, -1) | (0, 1) | 0.783151896 | 0.012552306 | 1 | 0.0 | 0.573308729 | 0.024322978 | 1 | 0.0 |
| (2, 0) | (-2, 0) | 0.783151896 | 0.012552306 | 1 | 0.0 | 0.573308729 | 0.024322978 | 1 | 0.0 |
| (-2, 0) | (2, 0) | 0.783151896 | 0.012552306 | 1 | 0.0 | 0.573308729 | 0.024322978 | 1 | 0.0 |
| (0, 2) | (0, -2) | 0.783151896 | 0.012552306 | 1 | 0.0 | 0.573308729 | 0.024322978 | 1 | 0.0 |
| (0, -2) | (0, 2) | 0.783151896 | 0.012552306 | 1 | 0.0 | 0.573308729 | 0.024322978 | 1 | 0.0 |
| (4, 0) | (-4, 0) | 0.783151896 | 0.013515684 | 1 | 0.0 | 0.573308729 | 0.024354964 | 1 | 0.0 |
| (-4, 0) | (4, 0) | 0.783151896 | 0.012552306 | 1 | 0.0 | 0.573308729 | 0.024322978 | 1 | 0.0 |
| (0, 4) | (0, -4) | 0.783151896 | 0.012552306 | 1 | 0.0 | 0.573308729 | 0.024322978 | 1 | 0.0 |
| (0, -4) | (0, 4) | 0.783151896 | 0.012552306 | 1 | 0.0 | 0.573308729 | 0.024322978 | 1 | 0.0 |
| (2, 2) | (-2, -2) | 0.783151896 | 0.012552306 | 1 | 0.0 | 0.573308729 | 0.024322978 | 1 | 0.0 |
| (2, -2) | (-2, 2) | 0.783151896 | 0.012552306 | 1 | 0.0 | 0.573308729 | 0.024322978 | 1 | 0.0 |
| (-2, 2) | (2, -2) | 0.783151896 | 0.012552306 | 1 | 0.0 | 0.573308729 | 0.024322978 | 1 | 0.0 |
| (-2, -2) | (2, 2) | 0.783151896 | 0.012552306 | 1 | 0.0 | 0.573308729 | 0.024322978 | 1 | 0.0 |

Controle positivo identidade SS8: score 0.783151896, margem 0.012552306, rank 1, erro 0.0 px, PASS; suporte comum 256470 pixels nos blocos desse papel.

Controle positivo identidade NGF: score 0.573308729, margem 0.024322978, rank 1, erro 0.0 px, PASS; suporte comum 256470 pixels nos blocos desse papel.

### ESM5-to-ESM4:394 — PASS

SS8: 16/16; NGF: 16/16. Ambos concordam em todos os inversos. Cobertura por métrica: 18 blocos, quatro quadrantes.

| p=(dx,dy) | Inverso | SS8 | Δ SS8 | Rank SS8 | Erro SS8 px | NGF | Δ NGF | Rank NGF | Erro NGF px |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| (1, 0) | (-1, 0) | 0.748161463 | 0.010995033 | 1 | 0.0 | 0.532965831 | 0.019902340 | 1 | 0.0 |
| (-1, 0) | (1, 0) | 0.748161463 | 0.010995033 | 1 | 0.0 | 0.532965831 | 0.019902340 | 1 | 0.0 |
| (0, 1) | (0, -1) | 0.748161463 | 0.010995033 | 1 | 0.0 | 0.532965831 | 0.019902340 | 1 | 0.0 |
| (0, -1) | (0, 1) | 0.748161463 | 0.010995033 | 1 | 0.0 | 0.532965831 | 0.019902340 | 1 | 0.0 |
| (2, 0) | (-2, 0) | 0.748161463 | 0.010995033 | 1 | 0.0 | 0.532965831 | 0.019902340 | 1 | 0.0 |
| (-2, 0) | (2, 0) | 0.748161463 | 0.010995033 | 1 | 0.0 | 0.532965831 | 0.019902340 | 1 | 0.0 |
| (0, 2) | (0, -2) | 0.748161463 | 0.010995033 | 1 | 0.0 | 0.532965831 | 0.019902340 | 1 | 0.0 |
| (0, -2) | (0, 2) | 0.748161463 | 0.010995033 | 1 | 0.0 | 0.532965831 | 0.019902340 | 1 | 0.0 |
| (4, 0) | (-4, 0) | 0.748161463 | 0.010995033 | 1 | 0.0 | 0.532965831 | 0.022236816 | 1 | 0.0 |
| (-4, 0) | (4, 0) | 0.748161463 | 0.011118817 | 1 | 0.0 | 0.532965831 | 0.019902340 | 1 | 0.0 |
| (0, 4) | (0, -4) | 0.748161463 | 0.010995033 | 1 | 0.0 | 0.532965831 | 0.019902340 | 1 | 0.0 |
| (0, -4) | (0, 4) | 0.748161463 | 0.010995033 | 1 | 0.0 | 0.532965831 | 0.019902340 | 1 | 0.0 |
| (2, 2) | (-2, -2) | 0.748161463 | 0.010995033 | 1 | 0.0 | 0.532965831 | 0.019902340 | 1 | 0.0 |
| (2, -2) | (-2, 2) | 0.748161463 | 0.010995033 | 1 | 0.0 | 0.532965831 | 0.019902340 | 1 | 0.0 |
| (-2, 2) | (2, -2) | 0.748161463 | 0.010995033 | 1 | 0.0 | 0.532965831 | 0.019902340 | 1 | 0.0 |
| (-2, -2) | (2, 2) | 0.748161463 | 0.010995033 | 1 | 0.0 | 0.532965831 | 0.019902340 | 1 | 0.0 |

Controle positivo identidade SS8: score 0.748161463, margem 0.010995033, rank 1, erro 0.0 px, PASS; suporte comum 256470 pixels nos blocos desse papel.

Controle positivo identidade NGF: score 0.532965831, margem 0.019902340, rank 1, erro 0.0 px, PASS; suporte comum 256470 pixels nos blocos desse papel.

São 64 perturbações por descritor, 128 avaliações com SS8/NGF separados. Não são 128 réplicas experimentais. Cada um dos quatro positivos passou 16/16 em cada métrica; não houve arredondamento de 15/16 nem resgate por média.

## Verificação e preservação

Pré-registro: 423 testes stdlib, 337 passes e 86 skips opcionais; suites científicas separadas 5/16/26/27/18, todas PASS sem skips/falhas/erros. Após o encerramento, o mesmo perfil stdlib passou 423 testes, 337 passes e 86 skips. As versões NumPy1.26.4/SciPy1.11.4 permaneceram fixas.

Os 25 textos congelados correspondem simultaneamente aos hashes do receipt e aos bytes de C1. O guard de tombstone foi verificado após o fechamento e negou antes de qualquer caminho experimental. Não houve segunda invocação do runner. Nenhum código, parâmetro, critério ou máscara foi alterado depois de C1.

Os 95 checksums textuais legados permanecem válidos. O checksum próprio desta fase cobre textos autorizados, nunca dados experimentais. A revisão staged verifica UTF-8, identidade dos bytes e padrões delimitados de caminhos privados/tokens; não constitui prova universal de ausência de segredos.

A implementação teve quatro erros transitórios de integração antes de C1 (API ausente), posteriormente corrigidos e cobertos pelo GREEN completo; não foram execuções experimentais. A revisão independente textual não identificou bloqueios restantes antes do congelamento.

## Arquivos e comandos

Lista completa de caminhos alterados na fase, incluindo os sete caminhos exclusivamente documentais de C2:

- `.github/workflows/ci.yml`
- `AGENTS.md`
- `README.md`
- `artifacts/evidence/TI2/checksums.sha256`
- `docs/decisions/AUTHORIZATION-TI2R-SOLUTE-V2-D-2026-09-18.md`
- `docs/protocols/TI2R_SOLUTE_V2_PROTOCOL.md`
- `configs/authority/ti2r-solute-v2.json`
- `configs/registration/ti2r-solute-v2-method.json`
- `src/snbi_fragmentation/ti2r_solute_v2_authority.py`
- `src/snbi_fragmentation/ti2r_solute_v2_calibration.py`
- `scripts/run_ti2r_solute_v2.py`
- `scripts/run_ti2r_solute_v2_synthetic.py`
- `tests/test_ti2r_solute_v2_authority.py`
- `tests/test_ti2r_solute_v2_calibration.py`
- `tests/test_ti2r_solute_v2_execution.py`
- `artifacts/evidence/TI2R_SOLUTE_V2/exposure.json`
- `artifacts/evidence/TI2R_SOLUTE_V2/preflight.json`
- `artifacts/evidence/TI2R_SOLUTE_V2/verification-preregister.json`
- `artifacts/evidence/TI2R_SOLUTE_V2/commands.json`
- `artifacts/evidence/TI2R_SOLUTE_V2/receipt.json`
- `artifacts/evidence/TI2R_SOLUTE_V2/result.json`
- `artifacts/evidence/TI2R_SOLUTE_V2/terminal-state.json`
- `artifacts/evidence/TI2R_SOLUTE_V2/verification.json`
- `artifacts/evidence/TI2R_SOLUTE_V2/execution-report.md`
- `artifacts/evidence/TI2R_SOLUTE_V2/checksums.sha256`

O inventário sanitizado está em commands.json: comandos locais, testes sintéticos, leituras de revisão e operações Git/GitHub individualmente aprovadas. Corpos textuais longos e o caminho privado do anexo são identificados como sanitizados; o inventário não é um audit log do sistema operacional. Os comandos do commit/push C2 e a CI final, posteriores a este texto, pertencem ao PR efetivo e retorno terminal.

A árvore/index estavam limpos em C1 antes da execução. A limpeza final e igualdade local/remoto após C2 serão verificadas e reportadas no retorno; este relatório não presume sucesso futuro. Nenhuma branch será excluída.

## Estado terminal

```text
TI2R_SOLUTE_V2_DEV=PASS_PROTOCOL_FROZEN_READY_FOR_HOLDOUT_DECISION
V2_RULE=FROZEN
G2_FRAG=PASS_DIRECT_RASTER_MAPPING
G2_SOLUTE=BLOCKED_PENDING_LOCKED_HOLDOUT
HOLDOUT_SOLUTE=SEALED
CURRENT_AUTHORIZED_ACTIVITY=NONE_AWAITING_AUTHOR_DECISION
TI2R_SOLUTE_HOLDOUT_AUTHORIZED=false
TI3_PLUS_AUTHORIZED=false
MERGE_AUTHORIZED=false
STATE=CLOSED_CONSUMED
NO_AUTOMATIC_V3=true
```

Qualquer avaliação confirmatória lacrada depende de nova decisão explícita do autor.
