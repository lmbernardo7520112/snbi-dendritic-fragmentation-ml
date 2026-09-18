# Authorization record — TI2-CLOSEOUT-1 terminal BLOCKED

- Date: 2026-09-17
- Decision owner: Leonardo Maximino Bernardo
- Decision status: APPROVED by the current operator instruction
- TI2_EXECUTION_RESULT_COMMIT: `f3c6da78b04299475c7bb85e986eb7435b08bd22`
- Operator instruction SHA-256: `9e9a86a2ef5f1d971344e7afdf89b1a73d600aaa775ce3f05b7e9957b218fed0`

This record preserves the complete supplied authorization below. It supersedes
the earlier publication prerequisite for this documentary closeout only.
No TI-2R, scientific reanalysis or downstream execution is authorized. The
nominal scale and time offsets are author-provided documentary reconciliation
citing Gibbs et al.; no independent primary-text retrieval is claimed.
The closeout commit SHA belongs in the later operator report and Draft PR,
not in this self-containing commit.

## Complete operator authorization

MODO OPERACIONAL: `TI2_CLOSEOUT_1_TERMINAL_BLOCKED`

AUTORIZAÇÃO

O autor aprovou formalmente:

```text
TI2_EXECUTION = TERMINAL_BLOCKED_PENDING_CLOSEOUT
METHOD_V1 = INSUFFICIENT_EVIDENCE
G2-SPATIAL = BLOCKED_METHOD_V1
TRANSFORM_EXISTENCE = UNDETERMINED
G3 = BLOCKED_DEPENDENCY_G2
TI3_PLUS_AUTHORIZED = false
```

Está autorizada exclusivamente a etapa `TI2-CLOSEOUT-1`: reconciliação documental, checkpoint Git, push, abertura de Draft PR e verificação da CI remota.

Não execute TI-2R, TI-3 ou qualquer nova análise científica.

## 1. Preflight fail-closed

Confirme inicialmente, sem modificar o worktree:

* repositório `lmbernardo7520112/snbi-dendritic-fragmentation-ml`;
* branch `feat/ti2-registration-calibration`;
* worktree limpo;
* ausência de `.git/index.lock`;
* commits locais:

  * `7e2223d`;
  * `5e1c4dc`;
  * `f3c6da7`;
* nenhum dado experimental rastreado pelo Git.

Resolva e registre o SHA completo iniciado por `f3c6da7`. Esse será denominado:

```text
TI2_EXECUTION_RESULT_COMMIT
```

Não tente inserir no próprio commit de closeout o SHA desse novo commit, pois isso produziria autorreferência impossível. O SHA do closeout deverá constar no relatório terminal e no Draft PR após o commit.

Interrompa se:

* a branch for diferente;
* o worktree não estiver limpo;
* algum commit estiver ausente;
* houver ZIP, MP4, frame, imagem ou dataset rastreado;
* existir divergência não explicada.

Não execute `pull`, `merge`, `rebase`, `reset`, `clean`, `restore`, `stash`, `checkout` ou `switch`.

## 2. Registrar a autorização

Crie:

```text
docs/decisions/AUTHORIZATION-TI2-CLOSEOUT-1-2026-09-17.md
```

Registre integralmente a autorização do autor, os limites do escopo e as proibições.

## 3. Corrigir o modelo temporal

A reconciliação deve distinguir duas grandezas:

```text
elapsed_from_first_frame_s = 1.18 × frame_index
```

e o tempo experimental relativo à entrada da frente de solidificação no campo de visão:

```text
ESM1–3:
experimental_time_s = -25.96 + 1.18 × frame_index

ESM4–6:
experimental_time_s = -34.22 + 1.18 × frame_index
```

Inclua, quando pertinente:

```text
delta_t_s = 1.18
time_zero_reference = solidification_front_entry_into_field_of_view
time_model_status = DOCUMENTED_AND_RECONCILED
```

Verifique deterministicamente os pontos:

```text
ESM1–3:
i=0   → elapsed=0.00     experimental=-25.96
i=73  → elapsed=86.14    experimental=60.18
i=146 → elapsed=172.28   experimental=146.32
i=219 → elapsed=258.42   experimental=232.46
i=293 → elapsed=345.74   experimental=319.78

ESM4–6:
i=0   → elapsed=0.00     experimental=-34.22
i=98  → elapsed=115.64   experimental=81.42
i=197 → elapsed=232.46   experimental=198.24
i=295 → elapsed=348.10   experimental=313.88
i=394 → elapsed=464.92   experimental=430.70
```

Use cálculo decimal ou tolerância explicitamente documentada. Não dependa de igualdade binária ingênua de ponto flutuante.

Não apague silenciosamente o significado histórico de campos existentes. Se houver um campo ambíguo como `physical_time_s`, migre-o de forma documentada ou marque-o como depreciado, distinguindo inequivocamente:

* tempo decorrido desde o primeiro frame;
* tempo experimental com offset.

Fontes:

```text
Gibbs et al., JOM 68, 170–177 (2016)
DOI: 10.1007/s11837-015-1646-7
https://link.springer.com/article/10.1007/s11837-015-1646-7
```

Essa correção é exclusivamente semântica e determinística. Não abra, decodifique nem examine imagens para realizá-la.

## 4. Corrigir a escala

Registre separadamente:

```text
SPATIAL_SCALE_NOMINAL_STATUS = DOCUMENTED
NOMINAL_PIXEL_SIZE_X_UM = 1.40
NOMINAL_PIXEL_SIZE_Y_UM = 1.40
SCALE_BAR_VALUE_UM = 500
SCALE_BAR_LENGTH_PX = 357
RASTER_CROSSCHECK_UM_PER_PX = 1.40056022409
METROLOGICAL_UNCERTAINTY_STATUS = UNRESOLVED
```

Preserve, quando aplicável, o intervalo raster já calculado:

```text
[1.38888888889, 1.41242937853] µm/px
```

Deixe explícito que:

* `1,40 µm/px` é escala nominal documentada;
* `1,40056022409 µm/px` é uma verificação raster compatível;
* o intervalo raster não é intervalo estatístico de confiança;
* não existe certificado de incerteza metrológica completa;
* nenhuma coordenada será convertida;
* a escala não será propagada para modalidades sem registro certificado;
* G3 permanece bloqueado por dependência de G2-SPATIAL, ROI e incerteza.

## 5. Corrigir a terminologia

Substitua formulações ambíguas em todos os artefatos afetados:

```text
“30 imagens nativas”
```

por formulação equivalente a:

```text
“30 frames-piloto decodificados dos MP4 sem perdas adicionais,
preservando a resolução e o formato de pixels nativos dos vídeos”
```

Quando mencionar arquivos `.raw`, use:

```text
“buffers de pixels sem cabeçalho, decodificados dos MP4”
```

e deixe explícito:

```text
“não são dados brutos do detector”
```

Corrija:

```text
“30 pares permitidos”
```

para:

```text
“30 frames/itens permitidos”
```

Nenhum binário experimental pode ser incluído no Git.

## 6. Corrigir testes e estados

Não escreva genericamente “102 testes GREEN”.

Leia a saída real do runner e registre separadamente:

```text
tests_discovered_or_run
tests_passed
tests_skipped
failures
errors
```

Para a execução histórica descrita no relatório, confirme antes de registrar:

```text
102 testes executados
97 aprovados
5 ignorados explicitamente
0 falhas
0 erros
```

Se a suíte final, após os testes documentais, tiver nova contagem, registre:

* a contagem histórica;
* a contagem final;
* os motivos de cada skip;
* zero falhas e zero erros como condição de publicação.

Defina:

```text
E7 = PASS_DOCUMENTARY
TI2_EXECUTION = TERMINAL_BLOCKED_PENDING_CLOSEOUT
METHOD_V1 = INSUFFICIENT_EVIDENCE
G2_SPATIAL = BLOCKED_METHOD_V1
TRANSFORM_EXISTENCE = UNDETERMINED
G3 = BLOCKED_DEPENDENCY_G2
TI3_PLUS_AUTHORIZED = false
```

Não transforme CI verde, testes verdes ou documentação completa em aprovação de G2-SPATIAL ou G3.

## 7. Limites de arquivos

Modifique somente:

* documentos;
* registros de decisão;
* manifestos textuais;
* metadados textuais;
* configurações documentais;
* testes determinísticos da semântica temporal e da escala;
* relatórios e checksums afetados.

Não modifique o algoritmo científico de registro.

Se a correção exigir alteração em:

* `src/`;
* implementação do matcher;
* extração/decodificação;
* cálculo de correspondências;
* matrizes;
* ROI;
* análise de pixels;

interrompa e retorne:

```text
SOURCE_OR_SCIENTIFIC_CHANGE_REQUIRED
```

Não amplie o escopo implicitamente.

## 8. Proibição absoluta de pixels

Não:

* abra imagens;
* leia valores de pixels;
* gere visualizações;
* execute FFmpeg;
* redecodifique vídeos;
* acesse novamente membros MP4;
* examine os quartis;
* crie novos frames;
* recalcule correspondências;
* ajuste parâmetros científicos.

É permitido somente recalcular hashes criptográficos dos arquivos já existentes quando necessário à integridade. O hash deve tratar os arquivos como bytes opacos, sem decodificação ou interpretação de pixels.

## 9. Testes e guardrails

Execute, no mínimo, os validadores e testes já existentes relacionados a:

* governança;
* sanitização;
* escopo TI-2;
* ausência de dados experimentais rastreados;
* manifesto;
* semântica temporal;
* escala;
* checksums;
* suíte completa autorizada.

Não instale dependências.

Registre comandos, códigos de saída e contagens exatas.

Atualize checksums conforme o protocolo existente. Não crie hash circular do próprio arquivo de checksums.

Condições para prosseguir:

```text
TESTS = PASS
FAILURES = 0
ERRORS = 0
DATA_GUARD = PASS
SCOPE_GUARD = PASS
CHECKSUMS = PASS
EXPERIMENTAL_BINARIES_TRACKED = 0
```

## 10. Checkpoint Git pontual

Antes de staging, apresente:

```text
CHECKPOINT_ID
BASE_HEAD
STAGE_ALLOWLIST
BLOCKED_PATHS
DIFF_SUMMARY
TEST_RESULTS
GUARDRAILS
PROPOSED_COMMIT_MESSAGE
```

É proibido:

```text
git add .
git add -A
git commit -a
git commit --no-verify
```

Solicite aprovação interativa para executar fora da fronteira de escrita do sandbox exatamente:

```text
git add -- <LISTA_EXATA_DE_CAMINHOS>
```

Depois revise integralmente:

```text
git diff --cached --check
git diff --cached --name-status
git diff --cached --stat
git diff --cached
```

Rerode guardrails relevantes.

Solicite aprovação interativa separada para:

```text
git commit -m "docs(ti2): reconcile terminal blocked closeout"
```

Se o conteúdo incluir testes ou metadados cuja classificação torne essa mensagem inadequada, proponha uma mensagem Conventional Commit mais precisa antes de solicitar aprovação.

Depois do commit, registre:

* SHA completo do closeout;
* lista exata de arquivos;
* worktree limpo;
* sequência de commits desde `f7818c1`.

## 11. Verificação remota antes do push

Sem modificar a história local, verifique a referência remota usando comando read-only de rede e aprovação pontual.

Confirme que o push será fast-forward. Se a branch remota tiver avançado de forma incompatível, interrompa. Não faça rebase, merge ou force-push.

Solicite aprovação específica para:

```text
git push origin HEAD:feat/ti2-registration-calibration
```

É proibido qualquer `--force` ou `--force-with-lease`.

## 12. Abrir Draft PR

Abra Draft PR contra `main`, sem merge.

Título recomendado:

```text
TI-2: terminal BLOCKED result for registration and calibration method v1
```

O corpo deve conter:

* objetivo da TI-2;
* commits;
* exatamente 30 frames-piloto;
* nenhuma extração massiva;
* nenhuma imagem experimental versionada;
* resultados de E0–E7;
* método v1 com evidência insuficiente;
* G2-SPATIAL bloqueado;
* existência da transformação indeterminada;
* G3 bloqueado por dependência;
* modelo temporal reconciliado;
* escala nominal documentada;
* incerteza metrológica não resolvida;
* contagem exata dos testes e skips;
* guardrails;
* limitações;
* confirmação de que TI-3+ não foi executada;
* checklist de revisão;
* aviso explícito de que CI verde não aprova os gates científicos.

Utilize autenticação GitHub já configurada. Não procure, leia ou imprima credenciais ou tokens.

Se `gh` não estiver disponível ou autenticado, não solicite token. Retorne instrução humana mínima para abertura do Draft PR.

## 13. CI remota

Após o push e a abertura do Draft PR:

* identifique o run associado;
* aguarde sua conclusão;
* registre URL, jobs e estado;
* não declare CI verificada antes da conclusão.

Se a CI falhar:

* diagnostique somente a falha;
* faça correções apenas se forem determinísticas e estiverem estritamente dentro de TI2-CLOSEOUT-1;
* qualquer correção deverá ter testes, staging explícito, commit e push aprovados separadamente;
* se exigir pixels, algoritmo científico ou ampliação do escopo, interrompa.

## 14. Estado terminal obrigatório

Retorne somente em um destes estados:

```text
TI2_CLOSEOUT_1 = PASS
TI2_CLOSEOUT_1 = PARTIAL
TI2_CLOSEOUT_1 = BLOCKED
```

`PASS` exige:

* reconciliação concluída;
* testes sem falhas ou erros;
* guardrails PASS;
* checksums PASS;
* commit criado;
* push concluído;
* Draft PR aberto;
* CI remota verde;
* worktree limpo;
* nenhum binário experimental rastreado.

O Draft PR deve permanecer aberto, em rascunho e sem merge.

## 15. Relatório final

Apresente:

1. estado TI2-CLOSEOUT-1;
2. branch;
3. SHA completo de `TI2_EXECUTION_RESULT_COMMIT`;
4. SHA completo do commit de closeout;
5. lista de commits;
6. arquivos modificados;
7. modelo temporal final;
8. estado da escala;
9. contagem histórica e final dos testes;
10. skips, falhas e erros;
11. guardrails;
12. checksums;
13. confirmação de zero binários experimentais rastreados;
14. URL do Draft PR;
15. URL e resultado da CI;
16. estado do worktree;
17. comandos executados dentro do sandbox;
18. comandos executados mediante aprovação pontual;
19. confirmação de ausência de leitura de pixels;
20. confirmação de que TI-2R e TI-3–TI-8 não foram executadas;
21. pendências para decisão autoral;
22. confirmação de que nenhum merge foi realizado.

Inicie agora pelo preflight.

## End of operator authorization
