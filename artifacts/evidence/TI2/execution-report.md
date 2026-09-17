# TI-2 — Execução governada e resultado terminal de 17/09/2026

**G2-SPATIAL = BLOCKED. G3 = BLOCKED.** E0 e E1 passaram; o método
congelado não reuniu correspondências suficientes nos três instantes de cada
par. A seleção de classes não foi alcançada. Nenhuma matriz, inversa ou ROI
experimental foi certificada. Isso não demonstra impossibilidade física de
registro. Encerramento formal permanece pendente do autor.

## Estado e autoridade

Branch: `feat/ti2-registration-calibration`, repositório standalone autorizado.
Base preservada: `f7818c17c18ba9e4306696ea61b427864cf7deb6`.
Checkpoints concluídos antes deste relatório:

- `7e2223dd84346beebbccefe51afcead66a02d339` — recuperação E0-R e contratos;
- `5e1c4dc2406e1b6fbcf71bd8d86d6d842f3af3ad` — runtime, journal, registro,
  metrologia e controles sintéticos.

Este relatório integra um checkpoint documental posterior, cujo SHA deve ser
consultado no histórico Git. Nenhum histórico foi reescrito. O estado inicial
parcial foi preservado; o snapshot `execution-state.json` é histórico e não é
substituído pelo resultado científico em `terminal-state.json`.

LB0 permanece PASS; SDR-2-A permanece RESOLVED. Foram aplicadas as decisões de
execução de 17/09/2026 e de aprovações Git individuais. Cada staging e commit
teve sua própria aprovação interativa. Escrita científica ocorreu apenas no
repositório, no sandbox padrão. Não houve instalação, acesso a credenciais,
rede, mudança do sistema operacional, Full Access, bypass, push ou merge.

**Draft PR: não aberto. CI remota: NOT_VERIFIED.** A instrução mais recente
condicionou publicação à conclusão de E0–E7; E4/E5 estão bloqueadas por
pré-requisitos. Não foi solicitada ampliação da autorização de publicação.

## E0–E7

| Etapa | Resultado real |
|---|---|
| E0 | PASS: fonte autenticada, ferramentas disponíveis, RED histórico preservado, guardrails e preflight antes dos pixels |
| E1 | PASS: exatamente 30 imagens nativas, lineage e fonte imutável |
| E2 | PARTIAL: canvas, overlays e metadados auditados; orientação física e interpretação das diferenças de borda não comprovadas |
| E3 | BLOCKED: insuficiência de correspondências antes da seleção de transformações |
| E4 | BLOCKED_DEPENDENCY: sem matriz aprovada; quartis permanecem sem análise de pixels |
| E5 | BLOCKED_DEPENDENCY: suporte comum e ROI não certificáveis sem registro |
| E6 | PARTIAL: barra horizontal medida; calibração física completa UNRESOLVED |
| E7 | evidências, contratos, limitações e decisões técnicas registradas |

Não se alega conclusão científica integral de E0–E7. Nenhum novo frame será
selecionado, redecodificado ou analisado implicitamente após este bloqueio.

## Fonte, manifesto e integridade

Foi utilizado somente o ZIP expressamente indicado pelo operador, aberto com
`O_RDONLY|O_NOFOLLOW`. Caminho privado omitido; sua impressão SHA-256 é
`412b123e5dfa9b70f6d81560dbb9b2f4adda2662794050e25344bc7d783d9b44`.
O ZIP de 116199497 bytes e os seis membros MP4 correspondem a G0 antes,
depois e na verificação final. Hash do ZIP:
`9512a2e6d0ce397f9de8ae71cbf3cb759651df8e8793542a7c99cfe9d102d8f1`.
Documentos/PDFs e locais vizinhos não foram acessados.

O manifesto `artifacts/metadata/ti2-pilot-manifest.json` registra source_id,
experiment_id, condição, modalidade, índice, tempo normativo, codec, dimensões,
planos, profundidade, hashes, comando e lineage de cada item.

- ESM1–3: 0, 73, 146, 219, 293; 15 imagens.
- ESM4–6: 0, 98, 197, 295, 394; 15 imagens.
- Nativos: 8 bits, YUV420p, dimensões originais e todas as três componentes.
- Tempo registrado: `t(i)=i×1,18 s`, sem derivação dos 5 fps de reprodução.
- Imagens lossless raw em `data/derived/ti2-pilot/`, ignoradas pelo Git;
  nenhum ZIP, MP4, raw, PNG ou outro binário experimental foi staged.
- A prancha local `data/derived/ti2-diagnostics/central-estimation.png` é
  visualização de luminância dos seis frames centrais já autorizados, sem
  extração de qualquer frame adicional; não substitui revisão do autor.

O decoder atravessou referências internas do codec, mas exportou somente os
30 pares permitidos. Nenhum vídeo foi copiado para disco. Os hashes dos 30
nativos e da prancha estão em `integrity-report.json`. O destino do piloto
contém exatamente os 30 raws, `attempt.json` e `lineage.json`.

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

Incerteza metrológica da inscrição/aquisição, escala vertical e orientação
física continuam NOT_VERIFIED/UNRESOLVED. A razão da barra não foi propagada
para outras modalidades. **A escala validada é UNRESOLVED; coordenadas ficam
em pixels e nenhuma conversão física foi realizada.**

Os cinco componentes estão declarados. Registro, variação temporal, escala e
ROI permanecem sem incerteza total quantificada. A discretização por eixo tem
valor analítico 1/√12 = 0,288675 px, sob hipótese explícita de quantização
uniforme em ±0,5 px; não é uma medida experimental nem incerteza combinada.

Gravidade, gradiente térmico e crescimento não têm vetores comprovados nos
eixos nativos. Preservar x/y, os planos nativos e ausência de autorrotação não
supre essa evidência. A revisão visual do autor permanece PENDING.

Os textos dos frames centrais observados indicam 146,32 s em ESM1:146 e
198,24 s em ESM4:197, enquanto a regra aprovada fornece 172,28 e 232,46 s.
A semântica dessa diferença não foi inferida. Requer conciliação primária pelo
autor; não se alterou G2-TEMP, a regra temporal, índices ou fontes.

## Testes, guardrails e proveniência

Os três RED históricos foram preservados. `green-recovery.txt` registra 75
resultados GREEN na retomada. `green-final.txt` registra 97 testes após o
resultado científico. `green-final-control.txt` registra **102 testes GREEN**
após o controle final. Execução sem site-packages: 102 testes, cinco skips
explícitos das rotinas opcionais NumPy/SciPy, nenhum erro. CI remota não foi
executada nesta retomada.

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
Os comandos Git do próprio checkpoint documental posterior constam no histórico
e no retorno ao operador; este arquivo não inventa execução futura.

## Decisões, riscos e retomada

G2-SPATIAL BLOCKED: correspondências insuficientes, nenhuma validação espacial
certificada e orientação física não comprovada. G3 BLOCKED: registro e ROI não
certificados, orientação e calibração completas não resolvidas. A exceção PARTIAL
por ausência de escala não se aplica sem registro/ROI válidos.

A matriz de 20 contratos está em `contract-results.json`. Os relatórios dos
gates são propostas técnicas; não encerram formalmente TI-2 nem autorizam TI-3.

Retomada exige decisão autoral sobre revisão do método, documentação primária
da orientação/tempo e revisão visual. Qualquer nova análise deve declarar como
preservará a independência dos quartis, os limites já observados e as 30 imagens.
Não há autorização implícita para novos frames, nova decodificação, novos
limiares, labels, ledger, dataset, splits, baseline, CNN, treinamento, avaliação
de modelos ou TI-3–TI-8. Nenhuma dessas atividades foi executada.

Ao preparar o checkpoint documental, restavam somente arquivos textuais
explicados abaixo; o estado final após o commit deve ser confirmado por
`git status --short`. Os binários locais ignorados permanecem preservados.

## Inventário dos arquivos alterados nesta retomada

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

SHA-256 do manifesto-piloto: `278c38ba507d8afe6d21936872e1e17831670e53c23955c392686a9e9e5a5fa3`.
