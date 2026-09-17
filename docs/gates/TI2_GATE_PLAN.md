# TI-2 — Plano dos gates G2-SPATIAL e G3

## Classificação terminal e closeout

A [decisão de remediação PR6](../decisions/AUTHORIZATION-TI2-PR6-REMEDIATION-1-2026-09-17.md)
encerra `TI2_EXECUTION=TERMINAL_BLOCKED_CLOSED`, aceita `TI2_CLOSEOUT_1=PASS`
e mantém `NONE_AWAITING_AUTHOR_DECISION` como estado ativo canônico de
`pyproject.toml [tool.snbi]`. Todas as permissões científicas são falsas.

A [decisão autoral de TI2-CLOSEOUT-1](../decisions/AUTHORIZATION-TI2-CLOSEOUT-1-2026-09-17.md)
aprovou `TI2_EXECUTION=TERMINAL_BLOCKED_PENDING_CLOSEOUT`,
`METHOD_V1=INSUFFICIENT_EVIDENCE`, `G2_SPATIAL=BLOCKED_METHOD_V1`,
`TRANSFORM_EXISTENCE=UNDETERMINED`, `G3=BLOCKED_DEPENDENCY_G2` e
`E7=PASS_DOCUMENTARY`. A insuficiência é do método v1; não demonstra a
inexistência de transformação física. Registro/ROI não foram certificados.

A escala nominal X/Y de 1,40 µm/pixel está documentada por declaração do autor,
com verificação raster compatível de 500 µm/357 px. A incerteza metrológica
completa permanece `UNRESOLVED`; nenhuma coordenada é convertida. G3 continua
bloqueado por dependência de G2-SPATIAL, ROI e incerteza. A reconciliação
temporal é documental e não fornece correspondências espaciais.

Os critérios científicos abaixo são preservados. O closeout foi publicado em
Draft PR; a remediação exige dois jobs verdes no novo SHA sem aprovar gates
ou autorizar TI-2R/TI-3+. O PR permanece aberto, draft e sem merge.
Aprovação autoral do resultado terminal não comprova orientação física.

## G2-SPATIAL — Registro entre modalidades

### Pergunta decisória

As coordenadas das modalidades derivadas podem ser transferidas para a radiografia limpa por transformações reproduzíveis, fisicamente admissíveis e estáveis no tempo?

### PASS

- transformação mínima documentada para ESM2→ESM1, ESM3→ESM1, ESM5→ESM4 e ESM6→ESM4;
- matriz, inversa, convenção e domínio válidos;
- critérios de erro atendidos nos frames de validação sem reajuste;
- orientação física preservada;
- fontes nativas imutáveis;
- nenhum artefato TI-3+ produzido.

### PARTIAL

Permitido somente quando uma modalidade puder ser registrada com qualidade suficiente e outra permanecer não resolvida. O uso posterior ficará restrito à modalidade com PASS individual, sem extrapolação.

### BLOCKED

- registro exige transformação proibida;
- erro excede os limiares congelados;
- parâmetros variam no tempo sem regra reproduzível;
- orientação não pode ser comprovada;
- lineage ou imutabilidade falha.

## G3 — Calibração espacial, ROI e incerteza

### Pergunta decisória

A ROI e, quando declarada, a escala física possuem proveniência, estabilidade e incerteza suficientes para sustentar medições posteriores?

### PASS

- ROI canônica definida por condição com suporte válido integral;
- escala espacial apoiada por fonte rastreável;
- unidade, método, incerteza e aplicabilidade documentados;
- razão de aspecto e orientação preservadas;
- conversões testadas sem arredondamento silencioso.

### PARTIAL

Se ROI e registro forem válidos, mas a escala permanecer sem fonte suficiente, o projeto poderá avançar apenas com coordenadas e erros em pixels. Nenhuma medida será apresentada em `µm`, `mm`, área ou comprimento físico.

### BLOCKED

- ROI não é estável ou inclui regiões sem suporte;
- escala foi inferida visualmente ou por hipótese não rastreável;
- incerteza não pode ser declarada;
- metadados físicos contradizem orientação ou geometria.

## Regra de avanço

TI-3 permanece bloqueada independentemente do resultado técnico. O avanço exige decisão formal do autor após leitura das evidências de G2-SPATIAL e G3.
