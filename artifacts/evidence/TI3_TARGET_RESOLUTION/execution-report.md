# TI3_TARGET_RESOLUTION — PASS do target restrito de localização publicada

**52 sites operacionais únicos sustentam o gate estrutural. TARGET_CONTRACT=FROZEN.**
A resolução usou somente JSON A0 já materializado. Os 108 aceites geraram
38 sites ESM3 e 14 ESM6; 383 componentes permaneceram IGNORE.
Não houve imagem, patch, split ou ML. A autoridade encerra após este relatório.

## Retomada e checkpoint

A primeira solicitação de staging foi recusada antes do comando; o autor
declarou a rejeição acidental e autorizou retomar exatamente desse ponto.
A integridade dos mesmos 26 arquivos foi reconfirmada. O staging seguinte
passou e o index foi comparado byte a byte aos hashes já auditados.
Diff --check e guard de dados passaram. O único commit da tarefa é
`0f1284e86052e505e8ccfc9ceaecb58cb41065f2`, mensagem
`docs(ti3): preserve blocked annotation target audit`; parent
`1e7f5e8b382e84fd1259637722ce9774ffed7df3`.

GIT_APPROVAL_ATTEMPTS: staging=2 (uma rejeição administrativa e uma aprovação);
commit=1 aprovado; total=3. Isso não conta como ciência, ML ou avaliação.
Após o commit, worktree e index estavam limpos. Nenhuma nova validação
científica A0/G2 foi executada. A0 permanece historicamente BLOCKED.

## Trinta itens do retorno autoral

1. SHA do checkpoint A0: `0f1284e86052e505e8ccfc9ceaecb58cb41065f2`.
2. HEAD final: o mesmo SHA, branch feat/ti3-canonical-dataset-baseline.
   main e origin/main permanecem na baseline 67786bd4e23406e7f19860a53fe237e6d7b648cb.
3. Novos arquivos: exclusivamente nesta pasta, inventariados abaixo.
   Nenhum conteúdo A0/G2 foi alterado após o checkpoint.
4. Círculos aceitos brutos: 108, todos aproveitados como observações positivas.
5. Sites únicos: 52, segundo associação espacial fixa de 3 px.
6. Fontes: ESM3 tem 71 observações/38 sites; ESM6, 37/14.
7. Aquisições: bottom_up_anti_parallel=38 sites; top_down_parallel=14.
8. Repetição: 19 sites têm uma observação, 16 têm duas, 11 têm três, seis
   têm quatro. São 19 singletons e 33 repetidos; N de grupos não é 108.
9. FIRST_CONFIDENT_OBSERVATION: ESM3 73/146/219/293 → 14/10/8/6 sites;
   ESM6 98/197/295/394 → 2/10/2/0. Índices iniciais 0 → zero. Esses
   atributos não são nascimento ou instante físico de fragmentação.
10. IGNORE: 383 regiões por observação, 357 ESM3 e 26 ESM6; compreendem
    380 ambíguos e três pequenos. Bboxes e razões originais foram preservados.
11. Target final: PUBLISHED_FRAGMENTATION_LOCATION_PRESENT.
12. POSITIVE: centro aceito pelo extrator congelado, com semântica restrita
    de localização cumulativa publicada; não fragmento físico confirmado.
13. BACKGROUND_CANDIDATE: região válida sem localização publicada utilizável
    e longe de POSITIVE/IGNORE; não ausência física de fragmentação.
    Nenhum background foi materializado.
14. IGNORE: componente rejeitado, ambíguo ou pequeno e regiões de estado
    indeterminado; jamais convertido em NEGATIVE.
15. Sample: candidato espacial de uma imagem/instante, futuramente um patch.
    Não há tensor ou sample ML materializado.
16. TRAIN/DEV/FINAL_TEST: viáveis por contagem de sites não vazios e disjuntos.
    Ambas as aquisições permitem estratificação por contagem. Nenhum ID
    foi atribuído; isolamento de contexto e backgrounds ainda não é certificado.
17. Anti-leakage: site inteiro em uma partição, observações/modalidades/derivados
    juntos; futuro suporte de patch não pode conter site de outra partição.
    ESM3/6 nunca são features; exposição A0 permanece declarada.
18. LBP/RF: candidato apropriado ao baseline clássico futuro, não executado
    ou selecionado nesta tarefa.
19. CNN: candidato futuro, nenhuma arquitetura selecionada ou treinada.
20. Hough: não executado, sem tuning retrospectivo de labels.
21. Solutal: futura comparação STRUCTURAL_ONLY versus
    STRUCTURAL_PLUS_RELATIVE_SOLUTE, não executada. ESM2/5 significam
    exclusivamente campo solutal relativo/normalizado.
22. Claims: weak supervision de localização publicada; viabilidade de
    validação interna agrupada; hipótese futura de informação incremental.
23. Proibidos: máscara/extensão física, inventário exaustivo, onset exato,
    forecasting, causalidade, Bi absoluto, temperatura e generalização externa.
24. Acessos experimentais/pixels: zero; nenhum buffer A0, PNG, ESM1/2/4/5,
    novo ESM3/6, vídeo, ZIP ou fonte externa foi aberto.
25. ML_RUNS=0. A resolução textual ocorreu uma única vez, com exit 0.
26. FINAL_TEST=NOT_DEFINED_NOT_OPENED, nunca chamado SEALED.
27. Testes: 16 casos sintéticos únicos, duas invocações aprovadas (32 resultados
    PASS), zero skips/falhas/erros. A segunda sucedeu inclusão dos campos
    obrigatórios do schema antes da primeira resolução real. Invariantes
    dos registros produzidos foram auditados sem chamar novamente o resolver.
28. CI: não acionada; nenhum push, PR, Ready ou merge.
29. Worktree/index: checkpoint preservado, sem diff versionado ou staging
    posterior; novos documentos locais desta pasta. Os três scripts Python
    locais são ignorados pela regra artifacts/** existente; seus hashes estão
    congelados e eles não foram movidos nem houve alteração de .gitignore.
30. Estado: PASS e target FROZEN; prontidão para a próxima decisão TI3-A,
    sem iniciar treinamento ou TI3-B; atividade atual NONE_AWAITING_AUTHOR_DECISION.

## Reprodução e custódia

O protocolo e os 11 textos de entrada/código/contratos foram autenticados
antes da resolução em method-freeze.json. O runner abriu somente textos de
allowlist fixa; a função de resolução não tem I/O. Receipt exclusivo registra
uma tentativa textual. O ledger mantém os 491 registros, ligações de
proveniência e semântica A0 original; somente o campo de supervisão novo
aplica a decisão autoral. Nenhuma coordenada foi ajustada.

A definição de site usa componentes conexos de arestas <=3 px, por
aquisição/source. Por transitividade, o diâmetro pode exceder 3 px; isso é
documentado, sem outro limite. O centro representativo é uma coordenada
observada selecionada por medoid quadrático determinístico. Dispersões são
descritores, não incerteza metrológica. Nenhum site é chamado evento físico.

Os dez arquivos de anotações A0 continuam DEVELOPMENT_ONLY. A exposição
prévia e cumulativa não é apagada por agrupar sites. PASS certifica o
contrato restrito e a possibilidade combinatória, não poder estatístico,
adequação de backgrounds, isolamento efetivo de pixels futuros ou
generalização externa. Materialização de inputs e teste exige contexto,
suporte válido e exposição explicitamente tratados na próxima fase autorizada.

## Inventário desta pasta

- authorization.md — anexo original; retomada administrativa registrada neste relatório;
- RESOLUTION_PROTOCOL.md — critérios fixados antes da contagem;
- TARGET_CONTRACT.md, SPLIT_CONTRACT.md, COURSE_ALIGNMENT.md, CLAIM_SCOPE.md;
- resolve.py, test_resolution.py, run_resolution.py — textos locais ignorados;
- method-freeze.json, resolution-receipt.json, resolution-summary.json;
- WEAK_LABEL_LEDGER.json, SITE_DEDUPLICATION.json, DATASET_FEASIBILITY.md;
- results.json, commands.json, verification.json, execution-report.md.

verification.json registra integridade e limites das verificações. O journal
separa a rejeição Git e os testes de leitura de schema das execuções científicas.
A emissão dos metadados finais e sua checagem read-only são relatadas ao
operador, sem commit autorreferente.

```text
TI3_TARGET_RESOLUTION=PASS
TARGET_CONTRACT=FROZEN
WEAK_LABEL_STRATEGY=HIGH_CONFIDENCE_PLUS_IGNORE
PUBLISHED_FRAGMENTATION_LOCATION_TARGET=VALID_FOR_INTERNAL_ML
CIRCLE_IS_FRAGMENT_MASK=false
EXACT_ONSET_AVAILABLE=false
SOLUTAL_INPUT_SEMANTICS=RELATIVE_SOLUTE_FIELD
FORECASTING_AUTHORIZED=false
CAUSALITY_CLAIM_AUTHORIZED=false
EXTERNAL_GENERALIZATION_CLAIM=false
FINAL_TEST=NOT_DEFINED_NOT_OPENED
ML_RUNS=0
TI3_A_READY_TO_RESUME=true
TI3_B_AUTHORIZED=false
MERGE_AUTHORIZED=false
CURRENT_AUTHORIZED_ACTIVITY=NONE_AWAITING_AUTHOR_DECISION
```
