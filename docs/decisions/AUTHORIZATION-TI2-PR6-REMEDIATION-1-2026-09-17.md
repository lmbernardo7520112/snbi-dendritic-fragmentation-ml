# Authorization — TI2-PR6-REMEDIATION-1

Date: 2026-09-17. Decision owner: Leonardo Maximino Bernardo.
Decision status: APPROVED by the explicit operator attachment.

Original instruction SHA-256: `aaf476eec0f82b56ce2cb320c1cc1b183a8dfe6d715204081660a21c6830bf2d`.
The faithful transcription below redacts only the private repository-root path.
It supersedes current activity while preserving historical decisions.

## Operator decision

EXECUTE INTEGRALMENTE A MICROETAPA AUTORIZADA
`TI2-PR6-REMEDIATION-1 — FECHAMENTO FAIL-CLOSED E PRONTIDÃO PARA REVISÃO FINAL`.

NÃO SE LIMITE A APRESENTAR UM PLANO. REALIZE A IMPLEMENTAÇÃO, OS TESTES, O COMMIT, O PUSH, A ATUALIZAÇÃO DO DRAFT PR #6 E A VERIFICAÇÃO DA NOVA CI, RESPEITANDO ESTRITAMENTE OS LIMITES ABAIXO.

## 1. AUTORIZAÇÃO VIGENTE

O AUTOR APROVOU O ENCERRAMENTO DA `TI2-CLOSEOUT-1` COM STATUS `PASS`.

O PR #6 ESTÁ PUBLICADO EM RASCUNHO, COM A CI ANTERIOR VERDE, MAS NÃO ESTÁ AUTORIZADO PARA READY FOR REVIEW NEM PARA MERGE.

ESTÁ AUTORIZADA EXCLUSIVAMENTE A MICROETAPA:

```text
TI2-PR6-REMEDIATION-1
```

Estado final obrigatório:

```text
TI2_EXECUTION=TERMINAL_BLOCKED_CLOSED
TI2_CLOSEOUT_1=PASS
CURRENT_AUTHORIZED_ACTIVITY=NONE_AWAITING_AUTHOR_DECISION
TI2_EXECUTION_AUTHORIZED=false
TI2R_AUTHORIZED=false
TI3_PLUS_AUTHORIZED=false

METHOD_V1=INSUFFICIENT_EVIDENCE
G2_SPATIAL=BLOCKED_METHOD_V1
TRANSFORM_EXISTENCE=UNDETERMINED
G3=BLOCKED_DEPENDENCY_G2
E7=PASS_DOCUMENTARY
```

A autorização para realizar esta remediação decorre desta decisão autoral. Contudo, depois de concluído o commit, o estado ativo deverá retornar obrigatoriamente a `NONE_AWAITING_AUTHOR_DECISION`.

## 2. PRECONDIÇÕES BLOQUEANTES

Trabalhe exclusivamente em:

```text
<repository-root>
```

Repositório esperado:

```text
lmbernardo7520112/snbi-dendritic-fragmentation-ml
```

Branch esperada:

```text
feat/ti2-registration-calibration
```

HEAD inicial obrigatório:

```text
a1d675f5dbbe3862621aebad2bcb80ab7584858d
```

Antes de editar:

1. Confirme que o diretório é um clone standalone e que `.git` é diretório real, não symlink.
2. Confirme branch, HEAD e `origin`.
3. Confirme index e worktree completamente limpos.
4. Confirme, preferencialmente com `git ls-remote`, que o head remoto da branch é igual ao HEAD local, sem executar `git fetch`.
5. Confirme que o PR #6:

   * está `OPEN`;
   * permanece `DRAFT`;
   * não foi merged;
   * tem base `main`;
   * tem head `feat/ti2-registration-calibration`;
   * aponta para o SHA inicial esperado.
6. Confirme que a execução anterior de CI `35265631917` terminou com sucesso.

Se qualquer precondição divergir, encerre imediatamente como:

```text
TI2_PR6_REMEDIATION_1=BLOCKED_PREFLIGHT
```

Não faça checkout, switch, reset, clean, stash, rebase, merge, cherry-pick, amend ou correção automática.

## 3. FRONTEIRA DE SEGURANÇA

Permaneça no sandbox padrão.

A proteção de `.git` pelo sandbox é intencional. Não tente alterar permissões, remontar o filesystem, modificar o sandbox, usar full access, `danger-full-access`, `--yolo`, fallback externo ou qualquer bypass.

São proibidos:

* `sudo`;
* instalação local de pacotes;
* alterações no sistema operacional;
* inspeção de tokens, credenciais, cookies, chaves ou arquivos de autenticação;
* FFmpeg ou FFprobe;
* abertura, leitura, decodificação, hashing de conteúdo ou inspeção de ZIP, MP4, `.raw`, frames ou imagens experimentais;
* acesso a pixels;
* nova extração ou redecodificação;
* recalcular correspondências;
* modificar grade, margem, limiar, matcher ou mínimo de correspondências;
* produzir ou alterar matrizes ou ROIs;
* converter coordenadas para unidades físicas;
* reexecutar E0–E7;
* executar TI-2R ou TI-3–TI-8;
* criar labels, ledger, dataset, splits, baseline, CNN ou treinamento.

Testes poderão utilizar apenas arquivos textuais versionados e dados sintéticos gerados em memória ou em diretórios temporários controlados.

Não invoque `scripts/run_ti2.py`, funções de extração, registro, matching ou calibração científica.

## 4. LEITURA INICIAL OBRIGATÓRIA

Leia integralmente, sem acessar dados experimentais:

* `AGENTS.md`;
* `README.md`;
* `pyproject.toml`;
* o registro de autorização da TI2-CLOSEOUT-1;
* os documentos de aprovações Git pontuais;
* `artifacts/evidence/TI2_CLOSEOUT_1/closeout-report.md`;
* `artifacts/evidence/TI2/terminal-state.json`;
* `artifacts/evidence/TI2/checksums.sha256`;
* os validadores, testes e arquivos de CI pertinentes.

A decisão autoral desta mensagem é mais recente quanto ao estado ativo. Preserve documentos históricos como registros históricos; não os reescreva como se a autorização anterior nunca tivesse existido.

## 5. REGISTRO DA NOVA DECISÃO

Crie:

```text
docs/decisions/AUTHORIZATION-TI2-PR6-REMEDIATION-1-2026-09-17.md
```

Registre fielmente:

* escopo autorizado;
* estados finais obrigatórios;
* proibições;
* exigência de PR em rascunho;
* ausência de autorização de merge;
* ausência de autorização para TI-2R e TI-3–TI-8;
* exigência de CI vinculada ao novo SHA;
* retorno obrigatório para revisão autoral.

Não altere documentos históricos apenas para remover ocorrências antigas de autorização. Validadores atuais nunca poderão inferir autorização vigente pesquisando textos históricos.

## 6. FECHAMENTO FAIL-CLOSED

Utilize `pyproject.toml [tool.snbi]` como fonte canônica do estado ativo, evitando criar outra fonte canônica concorrente.

Faça os documentos, validadores e testes atuais concordarem com:

```text
ti2_execution = "TERMINAL_BLOCKED_CLOSED"
ti2_closeout_1 = "PASS"
current_authorized_activity = "NONE_AWAITING_AUTHOR_DECISION"
ti2_execution_authorized = false
ti2r_authorized = false
ti3_plus_authorized = false
```

Remova ou neutralize qualquer marcador ativo residual que possa ser interpretado como:

```text
TI2_EXECUTION_AUTHORIZED=true
AUTHORIZED_ACTIVITY=TI2_REGISTRATION_CALIBRATION
```

Esses valores poderão permanecer somente dentro de registros históricos imutáveis e claramente identificados como históricos.

Atualize, quando aplicável:

* `AGENTS.md`;
* `README.md`;
* `pyproject.toml`;
* `artifacts/evidence/TI2/terminal-state.json`;
* `scripts/check_local_bootstrap.py`;
* `scripts/check_ti2_scope.py`;
* guardas de entrada de `scripts/run_ti2.py`;
* testes correspondentes.

Requisitos:

1. `check_local_bootstrap.py` deve poder retornar `status=PASS` para a coerência dos guardrails, mas obrigatoriamente:

   * `ti2_execution_authorized=false`;
   * `current_authorized_activity=NONE_AWAITING_AUTHOR_DECISION`;
   * prontidão científica bloqueada até nova decisão autoral.
2. `check_ti2_scope.py` não poderá declarar qualquer fase científica atualmente autorizada.
3. Toda entrada de E0–E7 deverá falhar antes de examinar caminho de fonte, ZIP, MP4, `.raw`, FFmpeg ou pixels quando a autorização estiver falsa.
4. Estado ausente, desconhecido, conflitante ou com valor truthy não canônico deverá falhar fechado.
5. Um registro histórico antigo com autorização verdadeira nunca poderá sobrescrever o estado canônico atual.
6. G2-SPATIAL, G3 e `TRANSFORM_EXISTENCE` não poderão mudar.

## 7. ARTEFATO PÓS-PUBLICAÇÃO SEM AUTORREFERÊNCIA

Crie um artefato textual versionado em:

```text
artifacts/evidence/TI2_PR6_REMEDIATION_1/closeout-publication-record.md
```

Ele deverá registrar exclusivamente a publicação já concluída da TI2-CLOSEOUT-1:

* PR #6 e sua URL;
* estado aberto, draft e não merged no checkpoint;
* base `main`;
* commit de resultado:
  `f3c6da78b04299475c7bb85e986eb7435b08bd22`;
* commit de closeout:
  `a1d675f5dbbe3862621aebad2bcb80ab7584858d`;
* CI anterior:
  `https://github.com/lmbernardo7520112/snbi-dendritic-fragmentation-ml/actions/runs/35265631917`;
* job e conclusão observados;
* contagem histórica:
  `113 executados / 108 aprovados / 5 skips / 0 falhas / 0 erros`;
* 70 checksums verificados no checkpoint anterior;
* `TI2_CLOSEOUT_1=PASS`;
* limites da evidência.

Não tente inserir nesse arquivo o SHA do commit que ainda será criado nem a futura URL da CI. Isso criaria autorreferência infinita.

O novo SHA e a nova CI deverão ser registrados posteriormente somente:

* no corpo efetivo do PR #6;
* no relatório terminal apresentado ao autor.

## 8. VERIFICADOR DETERMINÍSTICO DE CHECKSUMS

Adicione um verificador em Python usando apenas a biblioteca padrão e testes sintéticos correspondentes.

O verificador deverá:

* interpretar `artifacts/evidence/TI2/checksums.sha256`;
* calcular SHA-256 sobre bytes exatos, sem normalização;
* exigir que o número verificado seja igual ao número de entradas únicas;
* rejeitar hashes malformados;
* rejeitar caminhos absolutos;
* rejeitar `..`;
* rejeitar duplicatas;
* rejeitar o próprio manifesto como entrada;
* rejeitar arquivos ausentes;
* rejeitar symlinks;
* rejeitar arquivos não regulares;
* rejeitar caminhos não rastreados;
* rejeitar resolução para fora da raiz do repositório;
* rejeitar previamente caminhos experimentais, `data/`, vídeos, imagens, `.raw`, modelos e datasets, antes de tentar abri-los;
* retornar status não zero em qualquer inconsistência;
* produzir relatório determinístico com quantidade listada, verificada e violações.

Atualize deterministicamente somente os checksums textuais afetados pela remediação. O manifesto não poderá incluir a si próprio.

Registre separadamente:

* `historical_checksum_count=70`;
* nova quantidade efetivamente verificada.

Adicione uma etapa bloqueante de checksum na CI.

## 9. JOB CIENTÍFICO SINTÉTICO SEPARADO

Preserve o job atual `deterministic-contracts` e adicione um job separado, por exemplo:

```text
scientific-synthetic-contracts
```

Requisitos:

* Ubuntu runner;
* Python 3.12;
* permissão somente `contents: read`;
* checkout com `persist-credentials: false`;
* NumPy exatamente `1.26.4`;
* SciPy exatamente `1.11.4`;
* Pillow `10.2.0` somente se a inspeção dos testes demonstrar dependência direta;
* nenhuma instalação local: dependências somente no runner da CI;
* nenhuma dependência não fixada;
* confirmar em log as versões efetivamente importadas.

Execute exatamente:

```text
tests.test_ti2_registration.SyntheticImageMatchingTests
```

Implemente um runner determinístico que falhe se o resultado não for exatamente:

```text
testsRun=5
passed=5
skipped=0
failures=0
errors=0
expectedFailures=0
unexpectedSuccesses=0
```

Um exit code zero do `unittest` com skips não é suficiente.

Os cinco comportamentos obrigatórios são:

* tradução com contraste invertido;
* tradução subpixel;
* rejeição de ambiguidade;
* tratamento da máscara de overlay;
* tratamento de dimensões incompatíveis.

Somente matrizes sintéticas geradas em memória poderão ser utilizadas.

O job determinístico sem dependências poderá continuar mostrando cinco skips transparentes, desde que o job científico execute obrigatoriamente os cinco testes com zero skips.

## 10. SEMÂNTICA TEMPORAL OPERACIONAL

Atualize:

* `src/snbi_fragmentation/timebase.py`;
* `src/snbi_fragmentation/ti2_pilot.py`;
* o validador do manifesto;
* testes temporais e do piloto;
* somente metadados textuais estritamente necessários.

Não execute extração nem gere novamente arquivos experimentais.

Implemente com `Decimal`:

```text
elapsed_from_first_frame_s = 1.18 × frame_index

ESM1–ESM3:
experimental_time_s = -25.96 + elapsed_from_first_frame_s

ESM4–ESM6:
experimental_time_s = -34.22 + elapsed_from_first_frame_s
```

Requisitos:

1. Criar mapeamento único `source_id → offset` a partir de `configs/time_rule.json`.
2. Rejeitar source IDs ausentes, duplicados, desconhecidos ou sem cobertura.
3. Rejeitar índice booleano, não inteiro ou negativo.
4. Preservar `physical_time()` e `physical_time_s` somente como alias depreciado do tempo decorrido.
5. `frozen_plan()` deverá gerar:

   * `elapsed_from_first_frame_s`;
   * `experimental_time_s`;
   * `physical_time_s`, exatamente igual ao tempo decorrido.
6. `validate_pilot_manifest()` deverá exigir e recalcular os três campos para os 30 registros.
7. Usar `Decimal(str(valor))`; não aceitar aproximação silenciosa por tolerância float.
8. Rejeitar campo ausente, offset incorreto, condição trocada ou alias divergente.
9. Validar o manifesto textual existente, sem abrir os `.raw`.
10. FPS de reprodução não poderá participar do cálculo.

Preserve hashes, paths, metadados de decodificação e resultados científicos existentes.

## 11. INCERTEZA ANALÍTICA

Nos dois arquivos de calibração e em qualquer resumo textual atual que reproduza o mesmo componente, altere a classificação de:

```text
status=MEASURED
```

para:

```text
status=MODELLED
evidence_kind=ANALYTICAL_ASSUMPTION
```

para:

```text
1/sqrt(12) = 0.2886751345948129 px
```

A validação deverá exigir, para um componente `MODELLED`:

* valor finito e não negativo;
* unidade;
* método;
* proveniência;
* hipótese analítica explícita.

`MEASURED` deverá permanecer reservado a medição empírica.

Não altere:

```text
metrological_uncertainty_status=UNRESOLVED
scale_status=UNRESOLVED
coordinate_unit=pixel
physical_coordinate_conversions_performed=0
```

Não faça propagação de incerteza nem conversão física.

## 12. ADDENDUM DE LIMITAÇÕES DO MÉTODO V1

Crie um addendum textual na pasta de evidências da remediação, sem alterar os resultados científicos do método v1.

Registre explicitamente:

1. A síntese terminal de E6 dependeu parcialmente de um driver Python inline não versionado e, portanto, não é end-to-end reexecutável a partir de um único entry point versionado.
2. O `roundtrip` calculado com uma matriz e sua própria inversa demonstra fechamento algébrico/numerical, não validação independente de registro bidirecional.
3. A interação grade–máscara reduziu deterministicamente 35 candidatos para 15, constituindo limitação importante do método v1.
4. Essa limitação não demonstra impossibilidade de registro e mantém:
   `TRANSFORM_EXISTENCE=UNDETERMINED`.
5. “27 arquivos” referia-se apenas ao commit de closeout; no checkpoint `a1d675f`, o PR completo continha 69 arquivos alterados. A remediação poderá aumentar esse total.
6. A aprovação autoral do resultado terminal não equivale à verificação da orientação física, que permanece pendente.

Não recrie o driver inline, não recalcule E6 e não altere método v1.

## 13. TESTES E GUARDRAILS LOCAIS

Antes do staging, execute somente verificações livres de dados experimentais:

* guardrail de dados rastreados;
* validação fail-closed da autorização;
* validação de escopo;
* compilação Python;
* suíte unitária determinística;
* testes sintéticos do verificador de checksum;
* validação textual do manifesto;
* verificação dos checksums;
* `git diff --check`;
* auditoria do diff e da lista exata de arquivos.

Não instale NumPy ou SciPy localmente. Caso já não estejam disponíveis, os cinco testes científicos serão confirmados exclusivamente pelo job pinado da CI.

O guardrail de dados deverá continuar indicando:

```text
content_bytes_read=0
violations=[]
status=PASS
```

Confirme:

* zero binários experimentais rastreados;
* nenhuma alteração em método v1;
* nenhuma leitura de pixels;
* nenhuma execução de FFmpeg;
* G2-SPATIAL e G3 inalterados.

## 14. GIT COM APROVAÇÕES PONTUAIS

Todo código e toda documentação deverão ser editados no sandbox padrão.

Quando a implementação estiver completa:

1. Apresente ao operador:

   * `git status --short`;
   * lista exata e ordenada dos arquivos;
   * `git diff --check`;
   * `git diff --stat`;
   * resumo do diff;
   * testes e guardrails.
2. Solicite aprovação pontual para:

```text
git add -- <lista-exata-de-arquivos>
```

É proibido usar `git add .`, `git add -A`, glob ou `git commit -am`.

3. Depois do staging, execute:

   * `git diff --cached --check`;
   * `git diff --cached --stat`;
   * `git diff --cached --name-status`;
   * revisão do conteúdo staged.
4. Solicite aprovação pontual para um único commit:

```text
git commit -m "fix(ti2): close PR6 remediation fail-closed"
```

5. Não use amend.
6. Verifique SHA, árvore e worktree.
7. Solicite aprovação pontual para:

```text
git push origin HEAD:feat/ti2-registration-calibration
```

É proibido force-push.

Se qualquer aprovação for recusada ou indisponível, pare como:

```text
TI2_PR6_REMEDIATION_1=BLOCKED_GIT_APPROVAL
```

Não tente mudar permissões de `.git`.

## 15. CI REMOTA E PR #6

Depois do push:

1. Localize a execução da CI cujo `head_sha` seja exatamente o novo commit.
2. Não aceite como evidência uma execução verde de SHA anterior.
3. Verifique todos os runs relevantes do novo SHA, especialmente o evento do PR #6.
4. Não faça rerun automático.
5. Exija:

   * `deterministic-contracts=SUCCESS`;
   * checksum step `PASS`;
   * `scientific-synthetic-contracts=SUCCESS`;
   * exatamente cinco testes científicos executados e aprovados;
   * zero skips no job científico.
6. Se a CI falhar, for cancelada ou tiver job obrigatório ignorado, retorne `BLOCKED_CI`.
7. Se não terminar no tempo disponível, retorne `BLOCKED_CI_PENDING`.
8. Não produza um segundo commit sem nova autorização.

Somente depois de a CI do novo SHA ficar integralmente verde:

1. Prepare o corpo atualizado do PR #6 em arquivo temporário sanitizado e ignorado pelo Git.
2. Inclua:

   * estado `TERMINAL_BLOCKED_CLOSED`;
   * novo SHA;
   * URL da nova CI;
   * resultados dos dois jobs;
   * contagens exatas;
   * resultado dos checksums;
   * limitações do método v1;
   * `G2_SPATIAL=BLOCKED_METHOD_V1`;
   * `G3=BLOCKED_DEPENDENCY_G2`;
   * `CURRENT_AUTHORIZED_ACTIVITY=NONE_AWAITING_AUTHOR_DECISION`;
   * `MERGE_AUTHORIZED=false`;
   * checklist atualizado.
3. Solicite aprovação pontual para atualizar somente o corpo do PR #6.
4. Não use `gh pr ready`.
5. Não use `gh pr merge`.
6. Não solicite reviewers automaticamente.
7. Confirme novamente que o PR permanece:

   * aberto;
   * draft;
   * não merged;
   * no novo SHA.

Se a ferramenta remota existente estiver indisponível, não instale outra e não examine credenciais. Retorne `BLOCKED_REMOTE_TOOL`.

## 16. CRITÉRIO TERMINAL

Somente declare sucesso se todos os requisitos forem comprovados:

```text
TI2_PR6_REMEDIATION_1=PASS_READY_FOR_AUTHOR_REVIEW
PR6_STATE=DRAFT_AWAITING_AUTHOR_REVIEW
PR6_MERGE_READINESS=READY_FOR_AUTHOR_REVIEW
MERGE_AUTHORIZED=false

TI2_EXECUTION=TERMINAL_BLOCKED_CLOSED
TI2_CLOSEOUT_1=PASS
CURRENT_AUTHORIZED_ACTIVITY=NONE_AWAITING_AUTHOR_DECISION
TI2_EXECUTION_AUTHORIZED=false
TI2R_AUTHORIZED=false
TI3_PLUS_AUTHORIZED=false

G2_SPATIAL=BLOCKED_METHOD_V1
TRANSFORM_EXISTENCE=UNDETERMINED
G3=BLOCKED_DEPENDENCY_G2
```

No relatório final, apresente:

1. branch;
2. SHA inicial e SHA final;
3. sequência de commits;
4. lista exata de arquivos alterados;
5. resumo das correções;
6. resultados locais e suas contagens;
7. contagem histórica e nova contagem de checksums;
8. URL do PR #6;
9. URL da nova CI;
10. jobs e conclusões;
11. confirmação de cinco testes científicos aprovados e zero skips;
12. estado final do PR;
13. confirmação de worktree limpo;
14. confirmação de local e remoto no mesmo SHA;
15. comandos executados, distinguindo sandbox, aprovações Git e operações remotas;
16. confirmação de nenhuma leitura de pixels, FFmpeg, redecodificação ou alteração científica;
17. confirmação expressa de que ready/merge exigem nova autorização do autor.

Qualquer necessidade de tocar em dados experimentais, alterar método v1, produzir um segundo commit corretivo, expandir o escopo ou executar uma nova tentativa científica deverá interromper a microetapa como `BLOCKED` e retornar para deliberação.

## End of operator decision
