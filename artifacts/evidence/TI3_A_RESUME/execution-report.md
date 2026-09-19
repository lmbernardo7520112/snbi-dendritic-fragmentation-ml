# TI3-A — recuperação concluída; bloqueio local de compatibilidade da CI

**TI3_PREFLIGHT_RECOVERY=PASS. TI3_A=BLOCKED_CI_SCOPE_CONTRACT.**
O checkpoint e o ambiente foram recuperados. O planejamento geométrico passou
sem pixels, mas o guard global legado de TI-2 rejeita o código TI3 autorizado.
A operação termina antes de C1, publicação, CI remota e execução experimental.
Não é falha científica do baseline nem falha de uma CI remota executada.

## Recuperação e preservação

HEAD inicial: `0f1284e86052e505e8ccfc9ceaecb58cb41065f2`.
Único commit desta retomada:
`41d523e038e844588ee7724e07b00f75bdf29fdc`,
`docs(ti3): freeze fragmentation target resolution`.
Branch: `feat/ti3-canonical-dataset-baseline`.

Somente os três .py históricos da TARGET_RESOLUTION saíram do index.
Permanecem locais, ignorados, byte-idênticos. Foram versionados os 16 textos
anteriores, três snapshots textuais e script-snapshots.sha256, total de 20.
Hashes, tamanhos e lista exata desses 20 paths estão em
[preflight-recovery/verification.json](preflight-recovery/verification.json).
O data guard passou com 329 entradas no checkpoint. Nenhuma regra do data guard
ou .gitignore mudou. Os 25 textos científicos G2 foram reconferidos sem divergência.

Python 3.12.3 na .venv criada no repositório. Top-level exatamente:
NumPy 1.26.4, SciPy 1.11.4, scikit-image 0.24.0, scikit-learn 1.5.2.
Transitivas: joblib 1.6.0, threadpoolctl 3.7.0, cloudpickle 3.1.2,
imageio 2.37.4, lazy-loader 0.5, networkx 3.6.1, packaging 26.3,
Pillow 12.3.0 e tifffile 2026.3.3; pip 24.0.
[environment.json](environment.json) registra versões e fingerprint
`4629f874e0104bb9edec803c986c786764c9837fa2bc5634223f4a1141923979`.

A instalação inicial falhou por DNS no sandbox. A aprovação pontual posterior
permitiu o mesmo comando de instalação exclusivamente na .venv. Não houve
instalação global, sudo, Full Access, alteração do sistema ou acesso a credenciais.
As aprovações Git se limitaram à retirada exata do index, staging dos snapshots
e commit. Não houve push, PR, Ready, merge, force ou exclusão de branch.

## Pré-registro documental e resultado geométrico

Os 15 textos de entrada, código, testes e protocolos foram autenticados antes
da única chamada do planner. O freeze é documental, distinto do C1 científico
não criado. Receipt: metadata-preflight-receipt.json. Nenhum resolver histórico,
extrator A0 ou matcher G2 foi chamado.

Mantidos 52 sites, 108 observações positivas e 383 IGNORE. Positivo canônico:
a coordenada da própria FIRST_CONFIDENT_OBSERVATION, não o medoid posterior.
Arredondamento ao pixel mais próximo com empate para cima, offset(0,0),
patch65×65, raio32, margem3. Sem deslocar centro, padding ou alterar critérios.
FCO é observação documental, não onset físico.

| Split | Frames estruturais | Sites candidatos | Positivos válidos | Backgrounds | Excluídos | Samples planejados |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| TRAIN | ESM1:73/146; ESM4:98 |26|17|17|9|34|
| DEVELOPMENT | ESM1:219; ESM4:197 |18|8|8|10|16|
| FINAL_TEST | ESM1:293; ESM4:295 |8|3|3|5|6|

As 24 exclusões incluem 19 UNAVAILABLE e 8 INVALID_CONTEXT, com três em ambas.
Razões e IDs permanecem no manifesto; não são exclusões por desempenho.
Backgrounds foram selecionados em grid65, seed42, por hash textual, sem intensidade,
textura ou modelo. Respeitam a união temporal dos centros POSITIVE, bboxes IGNORE
e proibição de reutilizar suporte espacial na mesma aquisição.

A auditoria independente conferiu o resultado sem chamar novamente o planner.
Site e context_group não cruzam splits; zonas incompatíveis respeitam a
interseção literal patch/área expandida35, incluindo contatos.

**Limitação relevante:** em TRAIN, ESM1 possui 16 positivos/6 backgrounds;
ESM4 possui 1 positivo/11 backgrounds. A classe pode se confundir com aquisição/
condição. A quota 1:1 por split autorizada foi satisfeita; não houve reseleção.
Os sites e patches também não constituem aquisições independentes.

Suporte geométrico: bandas textuais, bordas e erosão histórica. Não é ROI
científica ou máscara cromática certificada. Um guard separado preparado antes
de C1 reutiliza chroma>=20, halo5 e erosão1 históricos para interromper se algum
patch TRAIN/DEV não tiver suporte integral, sem substituí-lo. Foi testado apenas
com bytes sintéticos; não foi aplicado a inputs experimentais. O suporte
cromático de FINAL permanece não inspecionado.

Manifesto completo:
[dataset_manifest.json](dataset_manifest.json), SHA-256
`c8e82b72ff5dc51d188a764c577c11d514474b14d90aea6292c1439e776fb487`.
Manifesto dos seis samples finais:
[final-test-manifest.json](final-test-manifest.json), SHA-256
`985af14d0d6a74298bbc0380767f900d264f544303e46ecd8ed4dc0eb1ab649f`.

ML_FINAL_TEST=SEALED_WITH_HISTORICAL_NON_ML_EXPOSURE.
Isso significa reserva de acesso para ML com histórico declarado, não holdout
globalmente virgem. Opens/bytes de FINAL, TRAIN e DEVELOPMENT nesta retomada:0.
Nenhum patch, tensor, feature experimental ou modelo foi materializado.

## Bloqueio concreto anterior a C1

A auditoria local usou inventário prospectivo, sem staging. O data guard passou
com 361 paths nesse momento, zero bytes experimentais. O guard global TI-2
retornou BLOCKED/exit1 com oito ocorrências, preservadas integralmente em
[local-scope-preflight.json](local-scope-preflight.json):

- três caminhos históricos de código A0 com annotations;
- sklearn no checker de dependências;
- caminhos de runner/core baseline;
- sklearn no core;
- caminho dataset do planner.

A autorização nova é válida para TI3; não se interpretou o antigo
TI3_PLUS_AUTHORIZED=false como revogação da decisão atual. O problema concreto
é que a CI ainda executa esse verificador global, incompatível com os novos
caminhos/imports legítimos. O workflow também verifica os checksums históricos
do próprio workflow e dos verificadores.

O anexo permite compatibilidade mínima de CI. A composição operacional dos
controles, porém, não possui mecanismo aprovado/implementado para separar o
corpus histórico TI2 do código TI3 sem alterar o alcance do guard e a custódia.
Não removi checks, usei continue-on-error, filtrei silenciosamente o inventário,
renomeei código para enganar regras ou substituí hashes históricos.
A análise independente confirmou essa incompatibilidade.

CI_PREPIXEL=NOT_RUN_BLOCKED_BY_LOCAL_SCOPE_PREFLIGHT.
Não houve C1, push, rerun de CI ou alteração remota. O novo workflow TI3 está
local, com versões pinadas e68testes configurados; não se alega execução remota.
Os jobs G2 e seus bytes permanecem intactos. Na verificação final, os 95
checksums textuais históricos TI2 passaram (95/95), sem reescrever o manifesto.

Retomada exige uma decisão explícita sobre a composição dos verificadores
TI2/TI3 e a preservação verificável de seus checksums históricos. Isso não
requer reabrir target, alterar split/modelo ou repetir o planejamento geométrico.

## Testes e estado das entregas

O smoke de ambiente passou 12 verificações e realizou dois fits RF sintéticos.
Novas suítes: dataset 18, baseline 13, suporte 6 e execução 13 — **50 testes PASS**,
uma invocação por suíte, zero skips/falhas/erros. A suíte de baseline fez mais
um fit sintético: total 3, separados de SCIENTIFIC_ML_RUNS=0.
A suíte completa do repositório e CI remota não foram executadas após o bloqueio.

| Entrega | Estado terminal |
| --- | --- |
| Target resolution checkpoint |COMMITTED; SHA completo acima|
| C1 method-freeze / SHA |NOT_CREATED|
| Dataset e split |PASS documental;56 samples planejados; sem materialização|
| Guards site/context/background |PASS na auditoria textual e testes sintéticos|
| Guard de suporte cromático real |NOT_EXECUTED|
| FINAL_TEST |Manifestado e reservado;0 opens/0 bytes|
| TRAIN/DEV |0 opens/0 bytes|
| LBP |P8/R1/uniform;10bins/range(0,10)/densityTrue; só sintético|
| RF |100 árvores/seed42;defaults integrais registrados; só sintético|
| Runs científicos baseline |0|
| Métricas TRAIN/DEVELOPMENT e confusão DEV |NOT_EVALUATED|
| C1 CI / publicação |NOT_RUN / NOT_STARTED|
| G2_FRAG / G2_SOLUTE |Preservados; nenhuma reexecução|
| Solutal |NOT_USED; ESM2/5 fechados|
| Próxima fase TI3-B / merge |false / false|

A4: LBP/RF usados somente nos smokes desta preparação; SIFT e ORB/FAST/BRIEF
não usados. A5: CNN adiada e não autorizada; Sobel/NGF e threshold/components
são históricos; Canny não é input; Hough deliberadamente não usado.
Claims permanecem localização publicada sob supervisão fraca. Nenhuma
alegação de forecasting, causalidade, onset exato, fragmento físico exaustivo,
Bi absoluto, temperatura ou generalização externa.

## Arquivos, custódia e encerramento

Além do único checkpoint, ficaram locais os requisitos, workflow TI3,
quatro módulos/quatro testes novos, checker de ambiente, builder documental,
runner ainda não executado, configuração de autoridade e esta pasta de evidências.
A lista final consta em verification.json. Nenhum conteúdo versionado anterior
foi alterado; index vazio. .venv e os três .py históricos permanecem ignorados.
Nenhum binário experimental foi criado, aberto ou staged.

A autoridade nova foi fechada como CLOSED_BLOCKED_BEFORE_C1.
results.json impede armar uma execução futura nesta passagem.
Não existe execution-receipt.json científico; o receipt documental não o substitui.
Não foi criado method-freeze.json científico nem inventada CI verde.

commands.json distingue comandos do agente principal, resumos dos delegados,
aprovações pontuais e falhas operacionais. Limites: não é monitoramento universal
de syscalls; alguns comandos auxiliares de leitura foram agregados; stdout das
suítes delegadas foi reportado por seus agentes, sem reexecutá-las para gerar logs.
Houve uma busca inicial de nome de módulo inexistente e um helper de leitura
que omitiu artifacts/metadata na sua allowlist local. A leitura corrigida
confirmou 25 hashes G2; não houve divergência científica nem mudança de guard.
A falha final de escopo é preservada, não corrigida automaticamente.

```text
TI3_PREFLIGHT_RECOVERY=PASS
BLOCKED_STAGED_DATA_GUARD=RESOLVED
TI3_ML_ENVIRONMENT=READY
TI3_A=BLOCKED_CI_SCOPE_CONTRACT
C1=NOT_CREATED
CI_PREPIXEL=NOT_RUN_BLOCKED_BY_LOCAL_SCOPE_PREFLIGHT
EXPERIMENTAL_OPENS=0
EXPERIMENTAL_BYTES=0
SCIENTIFIC_ML_RUNS=0
ML_FINAL_TEST=SEALED_WITH_HISTORICAL_NON_ML_EXPOSURE
ML_FINAL_TEST_EXECUTED=false
TI3_B_AUTHORIZED=false
MERGE_AUTHORIZED=false
CURRENT_AUTHORIZED_ACTIVITY=NONE_AWAITING_AUTHOR_DECISION
```
