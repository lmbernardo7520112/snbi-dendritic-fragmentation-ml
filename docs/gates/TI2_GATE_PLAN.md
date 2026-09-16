# TI-2 — Plano dos gates G2-SPATIAL e G3

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
