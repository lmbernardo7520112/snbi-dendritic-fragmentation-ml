# Authorization — TI2-PR6-REMEDIATION-2

Date: 2026-09-17. Decision owner: Leonardo Maximino Bernardo.
Status: APPROVED by the explicit operator instruction, single-use operational
authority for this corrective review of Draft PR #6.

The author partially accepts REMEDIATION-1: its preserved scientific result and
completed checks remain historical evidence, while an independent audit found
three remaining gaps: obsolete active authority in LOCAL_BOOTSTRAP.md, an
incomplete MEASURED empirical-evidence contract and direct experimental I/O APIs
without a canonical guard before path access. Code/document inspection during
the required preflight confirmed all three gaps. This decision permits only
their bounded correction, synthetic verification and single-commit publication.
It does not grant continuing scientific or local-write authority.

The complete instruction below preserves its scope, prohibitions, one-commit
limit, required Draft state, unchanged scientific gates and requirement for a
new express author decision before Ready for Review or merge. The sole redaction
is the private repository path. Prior authorizations remain historical records.

Original instruction SHA-256: `81c61962e4b99138a6e55c268c8623a4f61ebcbd6356d1e8cbdd098f4a1cfa4e`.

## Complete operator instruction

Execute integralmente a microetapa **TI2-PR6-REMEDIATION-2 — fechamento final das lacunas fail-closed** no repositório:

`<repository-root>`

Não se limite a elaborar um plano. Implemente, teste, publique o único commit autorizado, atualize o Draft PR #6 e verifique a CI, respeitando estritamente as fronteiras abaixo.

## 1. Autoridade temporária e resultado esperado

Esta mensagem constitui autorização operacional única e consumível para executar exclusivamente a TI2-PR6-REMEDIATION-2.

Ela não deve ser registrada como autorização científica contínua. Ao final, a autoridade canônica versionada deverá permanecer fechada:

```text
TI2_EXECUTION=TERMINAL_BLOCKED_CLOSED
TI2_CLOSEOUT_1=PASS
CURRENT_AUTHORIZED_ACTIVITY=NONE_AWAITING_AUTHOR_DECISION
TI2_EXECUTION_AUTHORIZED=false
TI2R_AUTHORIZED=false
TI3_PLUS_AUTHORIZED=false
CODEX_LOCAL_WRITE_READINESS=BLOCKED_AWAITING_AUTHOR_DECISION
MERGE_AUTHORIZED=false
G2_SPATIAL=BLOCKED_METHOD_V1
TRANSFORM_EXISTENCE=UNDETERMINED
G3=BLOCKED_DEPENDENCY_G2
```

O resultado terminal admissível, se todos os critérios forem satisfeitos, será:

```text
TI2_PR6_REMEDIATION_2=PASS_READY_FOR_FINAL_MERGE_DECISION
```

Isso significa apenas “pronto para decisão final do autor”. Não significa autorização para Ready for Review ou merge.

## 2. Preflight obrigatório e fail-closed

Antes de editar qualquer arquivo, confirme:

```text
repository=lmbernardo7520112/snbi-dendritic-fragmentation-ml
branch=feat/ti2-registration-calibration
initial_head=af5deb3f80e5ef0b326131c44d1f30a169b65194
```

Verifique também:

* clone standalone, com `.git` real e não symlink;
* worktree e index integralmente limpos;
* `origin` correspondente ao repositório esperado;
* upstream correspondente à branch esperada;
* branch remota no mesmo SHA, usando `git ls-remote`, sem `fetch` ou `pull`;
* PR #6 existente, `OPEN`, `DRAFT`, não merged, base `main`, head `feat/ti2-registration-calibration` e `headRefOid` igual ao SHA inicial;
* runs anteriores `35276612925` e `35276608001` concluídos com sucesso;
* existência das três lacunas auditadas:

  1. estado obsoleto em `LOCAL_BOOTSTRAP.md`;
  2. contrato insuficiente para incerteza `MEASURED`;
  3. APIs diretas de I/O experimental sem guarda canônica anterior ao acesso ao caminho.

Leia primeiro `AGENTS.md` e as instruções versionadas aplicáveis.

Não execute `checkout`, `switch`, `reset`, `clean`, `stash`, `rebase`, `merge`, `fetch` ou `pull`.

Qualquer divergência deve interromper imediatamente a execução com:

```text
TI2_PR6_REMEDIATION_2=BLOCKED_PREFLIGHT
```

Não tente reconciliar divergências automaticamente.

## 3. Registro da decisão

Crie:

`docs/decisions/AUTHORIZATION-TI2-PR6-REMEDIATION-2-2026-09-17.md`

O documento deverá registrar fielmente:

* resultado da auditoria independente;
* aceitação parcial da REMEDIATION-1;
* revisão corretiva do PR #6;
* escopo autorizado nesta microetapa;
* proibições;
* requisito de commit único;
* manutenção obrigatória do PR como Draft;
* estados científicos preservados;
* necessidade de nova decisão expressa para Ready for Review ou merge.

Não altere retrospectivamente os documentos históricos de autorização. Registros históricos claramente identificados podem conservar os estados válidos à época.

## 4. Fechamento documental e autoridade canônica

### 4.1 `LOCAL_BOOTSTRAP.md`

Atualize `docs/gates/LOCAL_BOOTSTRAP.md` para:

* declarar a autorização anterior de E0–E7 como histórica, consumida, encerrada e superada;
* remover qualquer formulação que a apresente como autorização atual;
* remover do estado corrente qualquer literal equivalente a:

  * `TI2_EXECUTION_AUTHORIZED=true`;
  * `AUTHORIZED_E0_E7`;
  * “supplies the current bounded authorization”;
  * “Separately authorized” quando usado como estado vigente;
* registrar um único bloco normativo atual, determinístico e machine-readable;
* apontar explicitamente para `pyproject.toml [tool.snbi]` como autoridade atual canônica.

O bloco atual deverá representar exatamente:

```json
{
  "authority_source": "pyproject.toml [tool.snbi]",
  "current_authorized_activity": "NONE_AWAITING_AUTHOR_DECISION",
  "ti2_execution_authorized": false,
  "ti2r_authorized": false,
  "ti3_plus_authorized": false,
  "codex_local_write_readiness": "BLOCKED_AWAITING_AUTHOR_DECISION"
}
```

Use delimitadores inequívocos, garantindo exatamente um bloco atual. A narrativa histórica não pode ser interpretada como autoridade ativa.

### 4.2 Autoridade em `pyproject.toml`

Preserve `pyproject.toml [tool.snbi]` como fonte única da autoridade atual.

Além dos estados fechados, represente explicitamente como bloqueadas:

```text
TI-2
TI-2R
TI-3
TI-4
TI-5
TI-6
TI-7
TI-8
```

Remova da autoridade ativa os nomes ambíguos:

```text
authorized_branch
pilot_image_limit
```

Se esses metadados forem necessários para custódia histórica, mova-os para namespace inequivocamente não autorizativo, preferencialmente:

```toml
[tool.snbi_history.ti2_e0_e7]
status = "HISTORICAL_CONSUMED_NON_AUTHORIZING"
execution_branch = "feat/ti2-registration-calibration"
frozen_pilot_image_count = 30
```

Não permita que metadados históricos alterem ou ampliem a autoridade corrente. A presença futura dos aliases antigos na autoridade ativa deverá ser rejeitada em modo fail-closed.

### 4.3 Validação dos documentos de gate

Implemente validação determinística para que documentos atuais de gate:

* possuam exatamente um bloco atual válido;
* correspondam integralmente ao estado canônico;
* não contenham autorização científica verdadeira, conflitante ou residual fora de bloco histórico explicitamente identificado;
* falhem quando o bloco estiver ausente, duplicado, malformado, incompleto ou possuir chaves desconhecidas;
* não rejeitem documentos históricos claramente identificados como históricos e não autorizativos.

Não implemente busca ingênua em todo o repositório. Use uma lista explícita de documentos de gate atuais e parsing dos blocos normativos.

Adicione testes sintéticos demonstrando:

* documento atual correto: PASS;
* autorização `true` no bloco atual: FAIL;
* autorização corrente contraditória fora do bloco histórico: FAIL;
* bloco atual ausente: FAIL;
* bloco atual duplicado ou malformado: FAIL;
* ponte para a autoridade canônica ausente: FAIL;
* registro histórico claramente delimitado contendo estado verdadeiro válido à época: não é tratado como autoridade atual.

## 5. Contrato de incerteza `MEASURED`

Corrija `validate_uncertainty_budget` em `src/snbi_fragmentation/ti2_geometry.py`.

Um componente com:

```text
status=MEASURED
```

somente poderá ser aceito se possuir obrigatoriamente:

```text
evidence_kind=EMPIRICAL_MEASUREMENT
provenance=<texto empírico não vazio>
value=<número finito, não booleano e não negativo>
unit=<texto não vazio>
method=<texto não vazio>
```

Preserve a rejeição de:

* `ANALYTICAL_ASSUMPTION` rotulada como `MEASURED`;
* campo `analytical_assumption` em componente medido;
* proveniência analítica apresentada como empírica;
* valor ausente, booleano, negativo, infinito ou NaN;
* unidade ou método ausentes ou vazios.

Preserve integralmente o contrato já existente para:

```text
MODELLED + ANALYTICAL_ASSUMPTION
```

Não altere valores científicos, configurações, orçamento atual, escala ou resultados do método v1.

Adicione testes sintéticos para:

* registro empírico completo: PASS;
* `evidence_kind` ausente: FAIL;
* `evidence_kind` vazio: FAIL;
* `evidence_kind` incorreto: FAIL;
* `ANALYTICAL_ASSUMPTION` rotulada como `MEASURED`: FAIL;
* proveniência ausente: FAIL;
* proveniência vazia ou composta apenas por espaços: FAIL;
* componente modelado atual: continua PASS.

## 6. Guarda anterior a qualquer I/O experimental

Audite as APIs públicas que possam tocar caminhos ou bytes experimentais.

Obrigatoriamente devem estar protegidas:

```text
open_readonly()
verify_archive()
extract_pilot()
```

Inclua qualquer outra API pública equivalente encontrada por inspeção exclusiva do código.

Cada API pública de I/O deverá consultar a mesma autoridade canônica como sua primeira operação executável, depois de eventual docstring e antes de:

* `Path(source)` ou `Path(output)`;
* `os.fspath`;
* `str`, `repr` ou interpolação do caminho fornecido;
* `resolve`, `absolute`, `exists`, `is_file`, `stat`;
* leitura de manifesto-fonte;
* abertura de ZIP, MP4 ou derivado;
* `open`, `ZipFile` ou equivalente;
* FFmpeg, FFprobe ou qualquer subprocesso;
* criação de diretório;
* arquivo temporário;
* escrita ou materialização.

A exceção de bloqueio não poderá incluir, converter ou registrar o caminho recebido.

Use uma única implementação de autoridade. Não duplique parsing ou regras entre `scripts/` e `src/`. Se necessário, mova a implementação compartilhada para o pacote e preserve `scripts/ti2_authority.py` apenas como fachada compatível.

Estado ausente, malformado, desconhecido ou conflitante deverá bloquear.

Funções puras de cálculo, validação de metadados sintéticos ou construção de comandos podem continuar acessíveis desde que não toquem caminhos ou bytes experimentais.

## 7. Testes de zero acesso

Teste o bloqueio exclusivamente com mocks e fixtures sintéticas.

Inclua:

1. teste estrutural/AST comprovando que a guarda é a primeira chamada executável das APIs públicas de I/O;
2. objeto sintético `ExplodingPath`, cujos `__fspath__`, `__str__` e `__repr__` geram erro se forem chamados;
3. chamada das APIs com a autoridade canônica fechada, esperando a exceção de autorização antes de qualquer método de `ExplodingPath`;
4. mocks para abertura de arquivo, ZIP, subprocesso, FFmpeg/FFprobe, criação de diretório, arquivo temporário e escrita;
5. comprovação de zero chamadas downstream;
6. teste de ausência, malformação e valor desconhecido da autoridade, todos fail-closed.

Se testes legados de `open_readonly()` precisarem exercitar seu comportamento interno, a liberação deverá ocorrer somente por mock explícito da guarda e usando arquivo temporário integralmente sintético.

Não use, mencione como argumento operacional, abra, normalize, liste, leia ou faça hash de ZIP, MP4, frames ou caminhos experimentais reais.

Não execute `run_ti2.py`.

## 8. Escopo de arquivos

Altere somente:

* novo documento de decisão;
* `docs/gates/LOCAL_BOOTSTRAP.md`;
* documentação corrente diretamente afetada;
* `pyproject.toml`;
* implementação canônica da autoridade;
* validadores de bootstrap/escopo;
* APIs públicas de I/O;
* validador de incerteza;
* testes diretamente correspondentes;
* manifesto de checksums;
* artefatos textuais mínimos de verificação, caso exigidos pela convenção existente.

Não altere:

* `.github/workflows/ci.yml`, salvo se houver impossibilidade objetiva de descobrir os testes — a expectativa é não alterá-lo;
* Actions, versões de Actions, wheels, hashes de dependências ou timeouts;
* configuração ou proteção da branch `main`;
* parâmetros, matcher, grade, máscaras ou limiares do método v1;
* matrizes, transformações, ROI, escala ou conversões físicas;
* artefatos científicos históricos.

Não crie artefato versionado que dependa do futuro SHA do commit ou das futuras URLs de CI. Esses dados deverão constar apenas no corpo do PR e no relatório terminal, evitando autorreferência e segundo commit.

## 9. Verificações locais

Antes do commit, execute, sem instalar dependências:

* guardrail de dados, exigindo `content_bytes_read=0`;
* validação do bootstrap;
* validação da autoridade e do escopo;
* compilação dos módulos Python afetados;
* suíte determinística completa;
* testes novos de documentação, autoridade, incerteza e I/O;
* suíte científica sintética com dependências já disponíveis, se presentes;
* verificação dos checksums;
* auditoria do diff;
* verificação de zero binários ou dados experimentais rastreados.

Use temporários somente dentro da área segura/ignorada já prevista pelo projeto.

Não execute FFmpeg ou FFprobe, nem mesmo para consultar versão.

Registre as contagens reais de:

* testes executados;
* aprovados;
* skips;
* falhas;
* erros;
* checksums listados;
* checksums únicos;
* checksums verificados.

Preserve separadamente as contagens históricas de 70 e 84 checksums; não force a nova contagem a permanecer 84.

## 10. Checksums e diff

Finalize todos os bytes antes do staging final.

Atualize o manifesto de checksums somente para os arquivos textuais diretamente afetados, conforme a convenção vigente. O manifesto não deve incluir seu próprio hash.

Mostre antes do commit:

* lista exata, ordenada, de arquivos alterados;
* `git status`;
* diff stat;
* diff integral relevante;
* resultado de todos os testes;
* resultado dos guardrails;
* resultado do verificador de checksums;
* confirmação de inexistência de conteúdo experimental rastreado.

Qualquer arquivo fora do allowlist autorizado deverá causar:

```text
TI2_PR6_REMEDIATION_2=BLOCKED_SCOPE
```

## 11. Git: commit único

Solicite aprovação pontual apenas para comandos Git exatos.

Use staging explícito:

```bash
git add -- <lista-exata-de-arquivos>
```

São proibidos:

```text
git add .
git add -A
globs amplos
commit --amend
segundo commit
force-push
```

Após revisar o diff staged e reconfirmar testes/checksums, crie exatamente um commit:

```text
fix(ti2): close final fail-closed gaps
```

Se qualquer problema for encontrado antes do commit, corrija-o ainda no worktree e repita as verificações. Depois do commit, não faça nova correção nem segundo commit.

Faça push exclusivamente fast-forward:

```bash
git push origin HEAD:feat/ti2-registration-calibration
```

Falha de non-fast-forward ou divergência remota deve bloquear, sem force-push.

## 12. CI e Draft PR #6

Após o push:

* determine o SHA final completo;
* confirme que local, remoto e PR #6 apontam para esse SHA;
* identifique separadamente os novos runs acionados por `push` e `pull_request`;
* confirme que cada run corresponde ao SHA final;
* exija sucesso de `deterministic-contracts`;
* exija sucesso de `scientific-synthetic-contracts`;
* confirme que o job científico executou os testes sintéticos esperados sem skips;
* confirme nos logs os guardrails e a verificação de checksums.

Não faça rerun de CI.

Se a CI falhar depois do commit, não corrija nem crie segundo commit. Retorne:

```text
TI2_PR6_REMEDIATION_2=BLOCKED_CI
```

Se permanecer pendente sem resultado terminal:

```text
TI2_PR6_REMEDIATION_2=BLOCKED_CI_PENDING
```

Com a CI verde, atualize somente o corpo do PR #6, mediante aprovação remota pontual, incluindo:

* resultado da auditoria independente;
* escopo e resultado da REMEDIATION-2;
* SHA inicial e SHA final;
* commit corretivo único;
* URLs dos runs;
* jobs e contagens;
* contagem real dos checksums;
* estado fail-closed atual;
* gates científicos preservados;
* declaração de zero acesso experimental;
* `MERGE_AUTHORIZED=false`.

O PR deverá permanecer:

```text
state=OPEN
isDraft=true
merged=false
```

Não execute:

* `gh pr ready`;
* solicitação de reviewers;
* merge;
* fechamento do PR;
* alteração de base;
* alteração de título fora do necessário;
* alteração de labels não autorizada.

## 13. Condições de interrupção

Interrompa sem ampliação do escopo diante de:

```text
BLOCKED_PREFLIGHT
BLOCKED_SCOPE
BLOCKED_GIT_APPROVAL
BLOCKED_REMOTE_DIVERGENCE
BLOCKED_REMOTE_TOOL
BLOCKED_CI
BLOCKED_CI_PENDING
BLOCKED_PR_STATE
```

Depois do fechamento delimitado, não transforme achados estilísticos, hardening adicional ou melhorias opcionais em nova remediação. Somente falha real de um critério autorizado poderá produzir bloqueio.

## 14. Proibições permanentes nesta execução

Permanecem proibidos:

* leitura, listagem detalhada ou hashing de conteúdo experimental;
* acesso a ZIP, MP4, frames, imagens ou datasets científicos;
* FFmpeg ou FFprobe;
* redecodificação ou criação de frames;
* alteração do método v1;
* correspondências, transformações, matrizes ou ROI;
* conversão física;
* TI-2R;
* TI-3 a TI-8;
* instalação local;
* `sudo`;
* alteração do sistema operacional;
* full access, danger-full-access, `--yolo` ou bypass;
* acesso ou inspeção de tokens e credenciais;
* force-push;
* segundo commit;
* Ready for Review;
* merge do PR #6.

## 15. Relatório terminal obrigatório

Se todos os critérios passarem, retorne exatamente:

```text
TI2_PR6_REMEDIATION_2=PASS_READY_FOR_FINAL_MERGE_DECISION
PR6_STATE=DRAFT_AWAITING_FINAL_AUTHOR_DECISION
PR6_MERGE_READINESS=READY_FOR_FINAL_AUTHOR_DECISION
MERGE_AUTHORIZED=false
CURRENT_AUTHORIZED_ACTIVITY=NONE_AWAITING_AUTHOR_DECISION
TI2_EXECUTION_AUTHORIZED=false
TI2R_AUTHORIZED=false
TI3_PLUS_AUTHORIZED=false
G2_SPATIAL=BLOCKED_METHOD_V1
TRANSFORM_EXISTENCE=UNDETERMINED
G3=BLOCKED_DEPENDENCY_G2
```

Apresente também:

1. branch;
2. SHA inicial e SHA final completos;
3. sequência de commits;
4. mensagem do único commit;
5. lista exata de arquivos alterados;
6. testes locais, com executados/aprovados/skips/falhas/erros;
7. guardrails;
8. checksums listados/únicos/verificados;
9. URLs e resultados das CIs no SHA final;
10. estado final do PR #6;
11. confirmação de local e remoto no mesmo SHA;
12. confirmação de worktree e index limpos;
13. operações realizadas no sandbox;
14. operações Git/remotas realizadas mediante aprovação pontual;
15. declaração expressa de que não houve acesso experimental, FFmpeg, alteração científica, instalação, alteração do sistema, Ready for Review ou merge.

Não declare PASS caso qualquer uma dessas evidências esteja ausente.


## End of operator instruction
