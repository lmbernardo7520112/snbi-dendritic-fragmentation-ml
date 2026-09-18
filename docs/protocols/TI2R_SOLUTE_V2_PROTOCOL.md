# TI2R-SOLUTE-V2-D — pré-registro de desenvolvimento

Este protocolo é congelado em C1, publicado como Draft PR e submetido à CI
antes de qualquer nova leitura experimental. A decisão autoral de 18/09/2026
autoriza somente esta fase. O PR #9 foi integrado em
`fcfc5e1445467248566e881c61929d4d3da7b1d8`, com CI pós-merge verde.

## Pergunta e limites

Avaliar discriminação relativa e recuperação de perturbações conhecidas pelos
SS8 e NGF já implementados. Não se calibra concentração, intensidade,
instrumento, escala física, incerteza metrológica ou generalização.
Proveniência primária completa está indisponível; o autor não exige nova busca.
O resultado V1, seu código, configuração, máscaras e evidências são imutáveis.
Os pisos históricos SS8 >= 0,90 e NGF >= 0,80 não foram atingidos e não possuem
calibração externa neste domínio. A decisão V2 deixa de usá-los como gates;
não altera seus valores históricos nem os substitui por outros pisos.

## Dados, unidade e observabilidade

Somente 12 buffers existentes DEV: ESM1/ESM2 em 0,146,293 e ESM4/ESM5 em
0,197,394. Cada arquivo será aberto uma vez e autenticado no receipt antes
da interpretação do Y nativo. Dimensões, formato YUV420p, hashes, lineage e
exposição anterior constam em exposure.json, derivados somente de textos.
Nenhuma nova decodificação, visualização, fonte ou arquivo experimental.

Quatro positivos, sem resgate por média: ESM2→ESM1:146/293 e
ESM5→ESM4:197/394. Os dois instantes 0 permanecem controles NON_IDENTIFIABLE;
a informação individual efetivamente calculada deve ser registrada, inclusive
qualquer divergência desse pressuposto. Nunca serão convertidos em positivos.
Os controles temporais do V1 são preservados e reportados com a
identificabilidade individual; comparações não mensuráveis não viram PASS.

Os oito holdouts ESM1/ESM2:73/219 e ESM4/ESM5:98/295 permanecem proibidos,
com open_count=0 e content_bytes_read=0 nesta fase. Não se podem abrir sequer
as referências. A exposição histórica das referências em FRAG-DIRECT é
declarada separadamente; SEALED não significa virgindade global das imagens.

A unidade experimental continua a aquisição, aproximadamente uma corrida
por condição. Frames, blocos, candidatos e perturbações não são réplicas físicas.
Não há p-valores, estimativa de generalização ou intervalos de confiança.

## Componentes preservados

Importar a implementação V1; não copiar um descritor alterado. Preservar as
dependências NumPy 1.26.4 e SciPy 1.11.4, Y nativo, exclusões geométricas,
grade 6x6, separação checkerboard seleção/auditoria, margem de bloco 20 px,
identificabilidade individual, mínimo 512 pixels/bloco, oito blocos/papel,
quatro quadrantes, SS8 com raio três e NGF com raio um. O eta de NGF é o do
bloco original de cada imagem, não recalculado numa janela ampliada.

A comparação original chama o V1 inalterado: 49 posições [-3,3]^2, sendo
48 controles não nulos; controles temporais; suporte comum e resíduos NGF
locais com refinamento parabólico diagnóstico. Nenhum residual é descartado.
A nova decisão usa os resultados brutos e ignora apenas os gates dos pisos
absolutos. Exige máximo único da identidade nas duas métricas, concordância,
margens espacial/temporal >=0,005, suporte suficiente e quatro quadrantes.
Resíduos originais: mediana <=1, P95 <=2, máximo <=3 px; ambiguidades e picos
censurados na borda da busca original continuam bloqueantes.

## Matriz de perturbações, congelada antes dos pixels

Identidade (0,0) como controle positivo; exatamente 16 perturbações não nulas:

```text
(+1,0),(-1,0),(0,+1),(0,-1)
(+2,0),(-2,0),(0,+2),(0,-2)
(+4,0),(-4,0),(0,+4),(0,-4)
(+2,+2),(+2,-2),(-2,+2),(-2,-2)
```

Convenção física: T_p M(x)=M(x-p), p=(dx,dy). Correção c desloca o raster
perturbado; a amostragem correspondente usa M(x-p-c). A correção verdadeira
é c=-p. Reportar perturbação, correção e offset de amostragem explicitamente.

A busca do benchmark contém exatamente 81 correções inteiras [-4,4]^2 em
ordem raster; não é uma ampliação dos controles ou do cálculo residual V1.
Todos os candidatos serão avaliados sem usar o inverso conhecido para limitar
ou ordenar a busca. O inverso conhecido só fornece a referência de avaliação.
O máximo na borda +/-4 pode ser o inverso discreto exato; não equivale ao
resíduo V1 censurado em +/-3. Não há interpolação, wrap ou inferência subpixel.

O acesso líquido ao raster original alcança +/-8 (perturbação quatro mais
correção quatro). O suporte de cada bloco é comum à identidade e a todos os
16x81 candidatos, derivado exclusivamente das máscaras V1, erodidas por oito
pixels adicionais: footprint total 11 para SS8 e nove para NGF. A máscara
científica original não é retocada; esta interseção adicional elimina suporte
artificial do benchmark. Bordas, padding, barras e timestamps não entram no
score. A separação existente entre papéis acomoda esses footprints.

A implementação pode reutilizar resultados dos deslocamentos líquidos
inteiros coincidentes; isso não acrescenta perturbações. Tradução por slices
dos campos de descritores equivale à translação inteira sem interpolação nos
pixels de suporte completo; testes sintéticos devem comprovar equivalência
com a transformação do raster, inclusive eta NGF preservado. Todos os scores
de candidatos e blocos necessários à auditoria são retidos.

## Decisão por positivo

Além dos critérios originais relativos, exigir, separadamente para SS8 e NGF,
em cada uma das 16 perturbações: máximo único no inverso verdadeiro, margem
>=0,005 para o melhor concorrente, erro de recuperação <=0,5 px, cobertura
dos quatro quadrantes e concordância das métricas. Na grade inteira isso
exige recuperação exata. Registrar rank verdadeiro (1 + número de scores
superiores além da tolerância numérica V1 de 1e-9), multiplicidade do máximo, margem verdadeira contra
melhor concorrente, margem do vencedor contra segundo colocado e erro.
Empate é bloqueante mesmo com rank 1. Nenhum resultado desfavorável é removido.

O requisito é 16/16 por positivo e por métrica; 15/16=93,75%, jamais 95%.
Executar a matriz inteira dos quatro positivos, inclusive depois de falha.
Resultados agregados são descritivos e não substituem aprovação individual.
Não há gate baseado em ruído, contraste, saturação ou translação subpixel.

## Autoridade, CI e execução única

C1 contém protocolo, configuração, código, testes, decisão e exposição.
O estado estático PREREGISTERED_CI_GATED não concede acesso genérico. O runner
exige HEAD C1, pai igual à base acima, branch correta, tracking remoto igual
ao HEAD, árvore/index limpos, textos congelados iguais ao Git, versões exatas
e evidência GitHub consultada pelo operador desta execução: push e PR no SHA
C1, ambos concluídos, jobs deterministic-contracts e
scientific-synthetic-contracts e seus passos em SUCCESS. O PR deve ser Draft.
A evidência sanitizada de CI é fornecida por stdin e incorporada ao receipt;
é um registro da consulta autenticada, não uma assinatura criptográfica.

begin_session grava receipt O_EXCL com fsync, contador 1, C1, hashes e custódia
antes dos pixels. IDs fora dos 12 DEV, incluindo todos os holdouts, são
negados antes de qualquer operação sobre seus caminhos. Não há API de
abertura condicional de holdout nesta fase. Uma segunda invocação é proibida.
Ao terminar, a sessão fecha, grava terminal-state.json como tombstone e então
result.json. A presença do tombstone, mesmo inválido, impede reativação.

Após a invocação, nenhum código/configuração/máscara/critério pode mudar.
C2 admite somente resultados/evidências/receipt/estado terminal/relatório/
checksums, seguido de push fast-forward e CI. O PR permanece OPEN/DRAFT.
Nenhuma terceira tentativa, correção científica pós-publicação ou merge.

## Terminais e publicação

- Quatro positivos aprovados: PASS_PROTOCOL_FROZEN_READY_FOR_HOLDOUT_DECISION;
  G2_SOLUTE=BLOCKED_PENDING_LOCKED_HOLDOUT; HOLDOUT_SOLUTE=SEALED.
- Qualquer falha científica: BLOCKED_METHOD_NOT_DISCRIMINATIVE;
  G2_SOLUTE=BLOCKED_FINAL_WITH_AVAILABLE_DATA; HOLDOUT_SOLUTE=SEALED_NOT_NEEDED;
  NO_AUTOMATIC_V3=true.
- Falha operacional antes de resultado científico:
  BLOCKED_OPERATIONAL_REQUIRES_AUTHOR_DECISION; holdout permanece SEALED.

Em todos os casos G2_FRAG=PASS_DIRECT_RASTER_MAPPING, execução encerrada,
CURRENT_AUTHORIZED_ACTIVITY=NONE_AWAITING_AUTHOR_DECISION, permissões de
holdout/TI-3+/merge falsas. PASS de desenvolvimento não certifica G2_SOLUTE.
O relatório final inclui matrizes por perturbação, rank, scores, margens,
erros, controles temporais, cobertura, resíduos, contadores e comandos.
SHAs/URLs produzidos por C1/C2 e sua publicação pertencem ao PR e retorno
final; não são inventados antecipadamente nem exigem commits autorreferentes.
