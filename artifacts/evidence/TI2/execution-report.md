# TI-2 — Resultado científico e reconciliação documental de closeout

**G2_SPATIAL = BLOCKED_METHOD_V1. G3 = BLOCKED_DEPENDENCY_G2.** E0 e E1 passaram; o método
congelado não reuniu correspondências suficientes nos três instantes de cada
par. A seleção de classes não foi alcançada. Nenhuma matriz, inversa ou ROI
experimental foi certificada. Isso não demonstra impossibilidade física de
registro. O autor aprovou a classificação terminal e autorizou exclusivamente
o closeout documental/publicação; nenhuma nova análise científica foi executada
para esta reconciliação.

```text
TI2_EXECUTION = TERMINAL_BLOCKED_PENDING_CLOSEOUT
METHOD_V1 = INSUFFICIENT_EVIDENCE
G2_SPATIAL = BLOCKED_METHOD_V1
TRANSFORM_EXISTENCE = UNDETERMINED
G3 = BLOCKED_DEPENDENCY_G2
E7 = PASS_DOCUMENTARY
TI3_PLUS_AUTHORIZED = false
```

## Estado atual após aprovação do closeout

O autor aceitou `TI2_CLOSEOUT_1=PASS` e encerrou
`TI2_EXECUTION=TERMINAL_BLOCKED_CLOSED`. A fonte canônica ativa é
`pyproject.toml [tool.snbi]`: `NONE_AWAITING_AUTHOR_DECISION`, com
`TI2_EXECUTION_AUTHORIZED=false`, `TI2R_AUTHORIZED=false` e `TI3_PLUS_AUTHORIZED=false`.
O bloco e a narrativa de closeout abaixo são históricos, preservados como
evidência do checkpoint anterior. A remediação não reexecuta ciência.
A publicação já concluída e os limites de reprodutibilidade estão em
`artifacts/evidence/TI2_PR6_REMEDIATION_1/`.

## Estado e autoridade históricos

Branch: `feat/ti2-registration-calibration`, repositório standalone autorizado.
Base preservada: `f7818c17c18ba9e4306696ea61b427864cf7deb6`.
Checkpoints da execução científica preservados:

- `7e2223dd84346beebbccefe51afcead66a02d339` — recuperação E0-R e contratos;
- `5e1c4dc2406e1b6fbcf71bd8d86d6d842f3af3ad` — runtime, journal, registro,
  metrologia e controles sintéticos.
- `f3c6da78b04299475c7bb85e986eb7435b08bd22` — resultado científico/evidências;
  este é `TI2_EXECUTION_RESULT_COMMIT`.

O SHA do novo commit de closeout será informado somente depois de sua criação,
no retorno terminal e no Draft PR; não é inserido no próprio commit. Nenhum
histórico foi reescrito. O estado inicial
parcial foi preservado; o snapshot `execution-state.json` é histórico e não é
substituído pelo resultado científico em `terminal-state.json`.

LB0 permanece PASS; SDR-2-A permanece RESOLVED. Na execução preservada, foram aplicadas as decisões de
execução de 17/09/2026 e de aprovações Git individuais. Cada staging e commit
teve sua própria aprovação interativa. Escrita científica ocorreu apenas no
repositório, no sandbox padrão. Não houve instalação, acesso a credenciais,
rede, mudança do sistema operacional, Full Access, bypass, push ou merge.

No commit do resultado científico, Draft PR não havia sido aberto e CI remota
era `NOT_VERIFIED`; a condição de publicação então vigente exigia conclusão
científica de E0–E7. A nova
[autorização de TI2-CLOSEOUT-1](../../../docs/decisions/AUTHORIZATION-TI2-CLOSEOUT-1-2026-09-17.md)
supre explicitamente essa restrição para publicar o resultado bloqueado.
Ela permite reconciliação textual, testes determinísticos, checkpoint, push,
Draft PR e verificação da CI remota, com aprovações Git pontuais. Não permite
TI-2R, pixels, nova análise científica ou merge. Estados de publicação/CI serão
registrados somente após as respectivas operações, sem antecipar sucesso.

## E0–E7

| Etapa | Resultado real |
|---|---|
| E0 | PASS: fonte autenticada, ferramentas disponíveis, RED histórico preservado, guardrails e preflight antes dos pixels |
| E1 | PASS histórico: exatamente 30 frames-piloto dos MP4 sem perdas adicionais, preservando resolução/formato de pixels dos vídeos, lineage e fonte imutável |
| E2 | PARTIAL: canvas, overlays e metadados auditados; orientação física e interpretação das diferenças de borda não comprovadas |
| E3 | INSUFFICIENT_EVIDENCE do método v1; insuficiência de correspondências antes da seleção de transformações |
| E4 | BLOCKED_DEPENDENCY: sem matriz aprovada; quartis permanecem sem análise de pixels |
| E5 | BLOCKED_DEPENDENCY: suporte comum e ROI não certificáveis sem registro |
| E6 | escala nominal X/Y DOCUMENTED; verificação raster compatível; incerteza metrológica completa UNRESOLVED; nenhuma conversão |
| E7 | PASS_DOCUMENTARY: evidências, contratos, limitações e classificação terminal reconciliados |

Não se alega conclusão científica integral de E0–E7. Nenhum novo frame será
selecionado, redecodificado ou analisado implicitamente após este bloqueio.

## Fonte, manifesto e integridade

Na execução científica histórica, foi utilizado somente o ZIP expressamente indicado pelo operador, aberto com
`O_RDONLY|O_NOFOLLOW`. Caminho privado omitido; sua impressão SHA-256 é
`412b123e5dfa9b70f6d81560dbb9b2f4adda2662794050e25344bc7d783d9b44`.
O ZIP de 116199497 bytes e os seis membros MP4 correspondem a G0 antes,
depois e na verificação final. Hash do ZIP:
`9512a2e6d0ce397f9de8ae71cbf3cb759651df8e8793542a7c99cfe9d102d8f1`.
Documentos/PDFs e locais vizinhos não foram acessados.

O manifesto `artifacts/metadata/ti2-pilot-manifest.json` registra source_id,
experiment_id, condição, modalidade, índice, tempos explicitamente distinguidos, codec, dimensões,
planos, profundidade, hashes, comando e lineage de cada item.

- ESM1–3: 0, 73, 146, 219, 293; 15 frames-piloto.
- ESM4–6: 0, 98, 197, 295, 394; 15 frames-piloto.
- Formato nativo dos vídeos preservado: 8 bits, YUV420p, resolução original e três componentes.
- O campo histórico `physical_time_s` registrava tempo decorrido `i×1,18 s`,
  sem derivação dos 5 fps; o modelo reconciliado abaixo explicita os offsets.
- Buffers `.raw` de pixels sem cabeçalho, decodificados dos MP4 sem perdas
  adicionais, em `data/derived/ti2-pilot/`, ignorados pelo Git;
  nenhum ZIP, MP4, raw, PNG ou outro binário experimental foi staged.
- A prancha local `data/derived/ti2-diagnostics/central-estimation.png` é
  visualização de luminância dos seis frames centrais já autorizados, sem
  extração de qualquer frame adicional; não substitui revisão do autor.

O decoder atravessou referências internas do codec, mas exportou somente os
30 frames/itens permitidos. Nenhum vídeo foi copiado para disco. Os hashes dos
30 buffers decodificados e da prancha estão em `integrity-report.json`. Esses
buffers **não são dados brutos do detector**. O inventário histórico do destino
registra os 30 arquivos `.raw`, `attempt.json` e `lineage.json`; nenhuma nova
inspeção de pixels foi usada no closeout.

## Registro e métricas

O método foi congelado em `method-freeze.json` antes da inspeção de pixels.
Usa gradientes, fase FFT, NCC local, reciprocidade, unicidade e informação
mútua descritiva. Os cantos com texto/barra foram excluídos em E2, somente com
base nos frames de estimação e antes do ajuste. Overlay cromático foi usado
apenas como exclusão transitória da métrica; não foram detectados objetos,
contados/diferenciados círculos ou exportadas máscaras de eventos.

Estimação: 0/146/293 e 0/197/394. Validação reservada: 73/219 e 98/295.
O método exigia pelo menos 12 correspondências distribuídas em cada instante.
A máscara excluiu 20 dos 35 centros da grade em todos os instantes, limitando
os candidatos a 15. Essa limitação do desenho da grade foi documentada sem
reajustar o método após seus resultados.

| Par | Correspondências inicial/central/final | Matriz/inversa | Validação |
|---|---:|---|---|
| ESM2→ESM1 | 0 / 2 / 0 | null / null | não avaliada |
| ESM3→ESM1 | 2 / 7 / 7 | null / null | não avaliada |
| ESM5→ESM4 | 0 / 1 / 0 | null / null | não avaliada |
| ESM6→ESM4 | 0 / 13 / 13 | null / null | não avaliada |

Nenhuma classe foi refutada experimentalmente. As configurações preservam
`NO_ADMISSIBLE_FIT` por insuficiência de entrada e não uma alegação de inexistência
de transformação. Não houve afim sem evidência, projetiva ou não rígida.

Distâncias sob identidade, apenas nas correspondências sobreviventes, sem
aceitar/ajustar identidade e sem alegação de precisão global:

| Par | n agregado | Mediana px | P95 px | Máximo px |
|---|---:|---:|---:|---:|
| ESM2→ESM1 | 2 | 0,367167 | 0,493685 | 0,507743 |
| ESM3→ESM1 | 16 | 0,211270 | 0,500302 | 0,582172 |
| ESM5→ESM4 | 1 | 0,343483 | 0,343483 | 0,343483 |
| ESM6→ESM4 | 26 | 0,270659 | 0,714000 | 0,861839 |

Esses diagnósticos são condicionados à seleção por confiança. Frames sem
correspondências têm métricas nulas. Não há resíduos certificados de validação,
roundtrip experimental ou estabilidade temporal comprovada. Limiares
1/2/3/0,25 px foram preservados. A análise dos quartis não ocorreu; apenas a
extração autorizada e verificação de seus bytes ocorreram em E1/integridade.

O runner usado em E3 está preservado exatamente em `runner-at-estimation.txt`,
com SHA correspondente a `estimation-audit.json`. Depois de E3 corrigiu-se
somente o controle que impediria análise futura de quartis sem matriz aprovada;
cinco testes sintéticos verificam esse controle. Não houve reexecução científica.

## ROI, escala, orientação e incerteza

Há registros separados para bottom-up e top-down em `configs/calibration/`.
As ROIs e transformações de retorno permanecem nulas; não se adotou o canvas
inteiro como ROI nem se forçou igualdade entre condições.

As barras com inscrição visual de 500 µm nas referências ESM1/ESM4 mediram
357 pixels nos seis instantes de estimação. Centros extremos x=859/1215;
bordas convencionais 858,5/1215,5. O limite raster conservador é ±3 px.
Razão horizontal candidata: 1,40056022409 µm/px, intervalo raster
[1,38888888889; 1,41242937853] µm/px, não intervalo estatístico de confiança.

A tentativa v1 usou janela que cortava o extremo da barra; permanece registrada
como UNRESOLVED. A v2 corrigiu janela e comprimento admissível após inspeção
somente da estimação, preservando limiares e regra de incerteza; ambas as
versões estão documentadas. Isso não alterou critérios de registro/validação.

No closeout, o autor documentou a escala nominal de **1,40 µm/pixel em X e Y**.
Essa declaração e a verificação raster de 1,40056022409 µm/pixel são registros
distintos. `SPATIAL_SCALE_NOMINAL_STATUS=DOCUMENTED` não constitui certificado
de incerteza metrológica completa; essa incerteza permanece `UNRESOLVED`.
A razão da barra não foi propagada para outras modalidades. Coordenadas ficam
em pixels, nenhuma conversão física foi realizada e G3 permanece bloqueado
por dependência de G2-SPATIAL, ROI e incerteza.

Os cinco componentes estão declarados. Registro, variação temporal, escala e
ROI permanecem sem incerteza total quantificada. A discretização por eixo tem
valor analítico 1/√12 = 0,2886751345948129 px, classificado como
`MODELLED` e `evidence_kind=ANALYTICAL_ASSUMPTION`, sob hipótese explícita de quantização
uniforme em ±0,5 px; não é uma medida experimental nem incerteza combinada.

Gravidade, gradiente térmico e crescimento não têm vetores comprovados nos
eixos nativos. Preservar x/y, os planos nativos e ausência de autorrotação não
supre essa evidência. A revisão visual do autor permanece PENDING.

## Modelo temporal reconciliado no closeout

A diferença observada historicamente foi reconciliada documentalmente pelo
autor, sem reabrir imagens ou MP4. A referência experimental zero é a entrada
da frente de solidificação no campo de visão:

```text
delta_t_s = 1.18
elapsed_from_first_frame_s = 1.18 * frame_index
ESM1–3: experimental_time_s = -25.96 + 1.18 * frame_index
ESM4–6: experimental_time_s = -34.22 + 1.18 * frame_index
time_zero_reference = solidification_front_entry_into_field_of_view
time_model_status = DOCUMENTED_AND_RECONCILED
```

| Grupo | Índice | Tempo decorrido (s) | Tempo experimental (s) |
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

As verificações determinísticas usam cálculo decimal, sem igualdade binária
ingênua. O nome histórico `physical_time_s` é depreciado por ambiguidade: seu
valor significava tempo decorrido desde o primeiro frame, e não tempo
experimental relativo à entrada da frente. O significado anterior é preservado
explicitamente na migração textual; não houve reindexação ou mudança de bytes.

O autor forneceu e aprovou o modelo temporal e a escala nominal X/Y, citando
Gibbs et al., *JOM* 68, 170–177 (2016),
[DOI 10.1007/s11837-015-1646-7](https://doi.org/10.1007/s11837-015-1646-7).
A atribuição é documental, baseada na declaração do autor neste closeout;
o artigo não foi consultado novamente pelo agente e nenhum pixel foi lido.

## Testes, guardrails e proveniência

Os três RED históricos e as saídas originais foram preservados. As execuções
com e sem site-packages são distintas e não devem ter suas contagens mescladas:

| Execução histórica | Descobertos/executados | Aprovados | Ignorados | Falhas | Erros |
|---|---:|---:|---:|---:|---:|
| `green-recovery.txt` | 75 | 75 | 0 | 0 | 0 |
| `green-final.txt` | 97 | 97 | 0 | 0 | 0 |
| `green-final-control.txt`, execução normal | 102 | 102 | 0 | 0 | 0 |
| Perfil histórico isolado com `-S`, relatado separadamente | 102 | 97 | 5 | 0 | 0 |
| Nova verificação da suíte histórica no closeout, com `-S` | 102 | 97 | 5 | 0 | 0 |
| Suíte final do closeout, incluindo 11 testes documentais novos, com `-S` | 113 | 108 | 5 | 0 | 0 |

Os cinco skips da execução `-S` correspondem às rotinas sintéticas opcionais
que dependem de NumPy/SciPy, indisponíveis quando site-packages é desabilitado.
O log normal preservado não contém esses skips. O stdout da execução histórica
com `-S` não havia sido salvo em arquivo separado: a nova execução de
verificação no closeout não é uma reconstrução daquele stdout.
[tests-history.json](../TI2_CLOSEOUT_1/tests-history.json) registra explicitamente
essa proveniência. A saída final está em
[tests-final.json](../TI2_CLOSEOUT_1/tests-final.json) e
[tests-final.txt](../TI2_CLOSEOUT_1/tests-final.txt): 113 executados, 108 aprovados,
5 ignorados, zero falhas e zero erros.

Os cinco métodos ignorados da classe `SyntheticImageMatchingTests` são:
`test_masks_exclude_overlay_and_input_arrays_are_unchanged`,
`test_mismatched_dimensions_preserve_native_coordinates`,
`test_native_coordinates_recover_translation_and_inverted_contrast`,
`test_subpixel_correspondences_are_not_integer_rounded` e
`test_uniform_and_periodic_content_are_ambiguous`. Todos registram o motivo
`optional NumPy/SciPy runtime is absent from dependency-free CI`.
Nenhum log histórico foi sobrescrito. Nenhuma contagem de testes ou resultado
de CI aprova os gates científicos.

Guard de dados, autoridade local, escopo TI-2 e AST passaram. A revisão staged
confere identidade dos bytes, UTF-8 e padrões de caminhos privados/chaves/tokens;
é uma verificação delimitada, não prova universal de ausência de segredos.
O único aviso de whitespace no primeiro checkpoint pertencia ao RED histórico
de governança e foi preservado. Houve uma invocação de teste sem PYTHONPATH que
falhou por importação; a invocação corrigida passou. Ela não foi tratada como
RED científico original.

Ambiente preexistente: Python3.12.3, NumPy1.26.4, SciPy1.11.4, Pillow10.2.0,
FFmpeg/FFprobe6.1.1. Nenhuma instalação. Os contratos de CI permanecem stdlib.
`commands.json` contém inventário sanitizado dos comandos, distinção entre
sandbox e aprovações Git pontuais, códigos de saída e limites do registro.
Os comandos Git dos checkpoints posteriores constam no histórico e no retorno
ao operador; este arquivo não inventa execução futura. O inventário histórico
não substitui o registro separado de comandos, testes e publicação do closeout.

## Decisões, riscos e retomada

G2-SPATIAL `BLOCKED_METHOD_V1`: evidência insuficiente no método v1, nenhuma
validação espacial certificada e orientação física não comprovada. Existência
da transformação: `UNDETERMINED`. G3 `BLOCKED_DEPENDENCY_G2`: registro e ROI não
certificados, orientação e incerteza completas não resolvidas. A exceção PARTIAL
por ausência de escala não se aplica sem registro/ROI válidos.

A matriz de 20 contratos está em `contract-results.json`. O autor aprovou a
classificação terminal bloqueada e `E7=PASS_DOCUMENTARY`; isso não concede
PASS científico a G2-SPATIAL/G3 nem autoriza TI-2R ou TI-3.

Retomada científica exige nova decisão autoral sobre revisão do método,
documentação da orientação/incerteza e revisão visual. O modelo temporal foi
reconciliado neste closeout. Qualquer futura análise deve declarar como
preservará a independência dos quartis, os limites observados e os 30 frames-piloto.
Não há autorização implícita para novos frames, nova decodificação, novos
limiares, labels, ledger, dataset, splits, baseline, CNN, treinamento, avaliação
de modelos ou TI-3–TI-8. Nenhuma dessas atividades foi executada.

O closeout corrente permite apenas alterações textuais e testes semânticos
determinísticos. Seu SHA, allowlist efetiva, testes finais, guards, checksums,
push, Draft PR, CI e estado final serão registrados após as operações. Não há
autorreferência ao SHA do novo commit. Os binários ignorados são preservados.

## Inventário histórico dos arquivos da execução até TI2_EXECUTION_RESULT_COMMIT

- `.github/workflows/ci.yml`
- `AGENTS.md`
- `Makefile`
- `README.md`
- `artifacts/evidence/G2_SPATIAL/registration-report.json`
- `artifacts/evidence/G3/calibration-report.json`
- `artifacts/evidence/TI2/checksums.sha256`
- `artifacts/evidence/TI2/commands.json`
- `artifacts/evidence/TI2/contract-results.json`
- `artifacts/evidence/TI2/e0r-recovery.json`
- `artifacts/evidence/TI2/estimation-audit.json`
- `artifacts/evidence/TI2/execution-report.md`
- `artifacts/evidence/TI2/execution-state.json`
- `artifacts/evidence/TI2/green-final-control.txt`
- `artifacts/evidence/TI2/green-final.txt`
- `artifacts/evidence/TI2/green-geometry.txt`
- `artifacts/evidence/TI2/green-governance.txt`
- `artifacts/evidence/TI2/green-recovery.txt`
- `artifacts/evidence/TI2/integrity-report.json`
- `artifacts/evidence/TI2/method-freeze.json`
- `artifacts/evidence/TI2/preflight.json`
- `artifacts/evidence/TI2/red-geometry.txt`
- `artifacts/evidence/TI2/red-governance.txt`
- `artifacts/evidence/TI2/red-pilot.txt`
- `artifacts/evidence/TI2/runner-at-estimation.txt`
- `artifacts/evidence/TI2/scale-estimation-audit-v2.json`
- `artifacts/evidence/TI2/scale-estimation-audit.json`
- `artifacts/evidence/TI2/terminal-state.json`
- `artifacts/evidence/TI2/validation-audit.json`
- `artifacts/metadata/ti2-pilot-manifest.json`
- `configs/calibration/bottom-up.json`
- `configs/calibration/top-down.json`
- `configs/registration/ESM2-to-ESM1.json`
- `configs/registration/ESM3-to-ESM1.json`
- `configs/registration/ESM5-to-ESM4.json`
- `configs/registration/ESM6-to-ESM4.json`
- `docs/decisions/AUTHORIZATION-TI2-TARGETED-GIT-APPROVALS-2026-09-17.md`
- `docs/gates/LOCAL_BOOTSTRAP.md`
- `docs/protocols/LOCAL_DEVELOPMENT.md`
- `docs/protocols/TI2_CONTRACT_MATRIX.md`
- `docs/protocols/TI2_EXECUTION_PLAN.md`
- `docs/risks/TI2_RISK_REGISTER.md`
- `docs/security/LOCAL_SANDBOX.md`
- `pyproject.toml`
- `scripts/check_local_bootstrap.py`
- `scripts/check_ti2_scope.py`
- `scripts/run_ti2.py`
- `src/snbi_fragmentation/ti2_calibration.py`
- `src/snbi_fragmentation/ti2_geometry.py`
- `src/snbi_fragmentation/ti2_pilot.py`
- `src/snbi_fragmentation/ti2_registration.py`
- `tests/test_local_bootstrap.py`
- `tests/test_scope_guard.py`
- `tests/test_ti2_calibration.py`
- `tests/test_ti2_execution.py`
- `tests/test_ti2_geometry.py`
- `tests/test_ti2_pilot.py`
- `tests/test_ti2_registration.py`

SHA-256 histórico do manifesto-piloto no commit de resultado científico:
`278c38ba507d8afe6d21936872e1e17831670e53c23955c392686a9e9e5a5fa3`.
A reconciliação textual do manifesto altera seu hash atual; os checksums do
closeout registram essa atualização sem alterar os buffers experimentais.
SHA-256 do manifesto textual reconciliado neste closeout:
`4f84a50e65e7541729d9a6c58e2649a872d6a92e55b305a66a0ce4e9f63a09a9`.
