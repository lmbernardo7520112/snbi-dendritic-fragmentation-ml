# TI-2 — Matriz de contratos

**Status:** testes e implementação TI-2 autorizados; contratos científicos preservados

Autoridade: [execução E0–E7](../decisions/AUTHORIZATION-LB0-SDR2A-CLOSURE-PR5-MERGE-TI2-EXECUTION-2026-09-17.md)
e [retomada com aprovações Git pontuais](../decisions/AUTHORIZATION-TI2-TARGETED-GIT-APPROVALS-2026-09-17.md).
A coluna de testes RED conserva a especificação aprovada. Autorização de
execução não equivale à satisfação dos contratos; G2-SPATIAL/G3 estavam
`NOT_EVALUATED` na retomada.

| ID | Contrato bloqueante | Teste RED futuro | Evidência esperada | Gate |
|---|---|---|---|---|
| SRC-201 | Todo derivado referencia fonte, índice, hash e tempo físico | derivado sem lineage deve falhar | manifesto-piloto | G2-SPATIAL |
| PILOT-201 | Somente 30 frames da lista congelada podem ser decodificados | índice adicional deve falhar | relatório de escopo | G2-SPATIAL |
| RAW-201 | Fontes nativas nunca são sobrescritas | tentativa de escrita no raw deve falhar | verificador de imutabilidade | G2-SPATIAL |
| GEO-201 | Coordenadas usam origem superior esquerda, `x` coluna e `y` linha | troca de eixos deve falhar | schema e teste sintético | G2-SPATIAL |
| GEO-202 | Toda transformação possui matriz 3×3 e inversa | matriz singular deve falhar | arquivo de registro | G2-SPATIAL |
| GEO-203 | A classe de transformação segue a hierarquia mínima | afim sem evidência deve falhar | relatório de seleção | G2-SPATIAL |
| GEO-204 | Transformações projetivas e não rígidas são proibidas | configuração proibida deve falhar | guardrail de configuração | G2-SPATIAL |
| GEO-205 | Orientação física não pode ser invertida | flip horizontal/vertical deve falhar | teste de orientação | G2-SPATIAL |
| REG-201 | Parâmetros são estimados em três frames e congelados antes da validação | reajuste em quartis deve falhar | log de estimação/validação | G2-SPATIAL |
| REG-202 | Erro mediano ≤1 px, P95 ≤2 px e máximo ≤3 px | resíduo sintético excessivo deve bloquear | relatório métrico | G2-SPATIAL |
| REG-203 | Erro de ida e volta ≤0,25 px | composição inconsistente deve falhar | teste de inversa | G2-SPATIAL |
| ANN-201 | Overlay pode ser mascarado para registro, mas círculo não é máscara de fragmento | exportação como label deve falhar | auditor de finalidade | G2-SPATIAL |
| ROI-201 | ROI possui suporte válido em 100% da amostra-piloto | pixel sem suporte deve falhar | manifesto de ROI | G3 |
| ROI-202 | ROI é definida por condição, sem igualar artificialmente experimentos | ROI global forçada deve falhar | revisão de configuração | G3 |
| CAL-201 | Unidade física requer fonte rastreável | `µm/pixel` sem fonte deve falhar | registro de calibração | G3 |
| CAL-202 | Escala não resolvida mantém resultados em pixels | conversão implícita deve falhar | teste de unidade | G3 |
| UNC-201 | Escala, registro e ROI possuem incerteza ou status explícito | campo ausente deve falhar | orçamento de incerteza | G3 |
| IMG-201 | Frames-piloto são lossless e não recebem CLAHE, resize ou correção de contraste | transform proibida deve falhar | lineage de decodificação | G2-SPATIAL |
| SCOPE-201 | Não existem labels, ledger, dataset, splits, baseline ou modelos | caminho/módulo proibido deve falhar | auditor de escopo | G2-SPATIAL/G3 |
| CLAIM-201 | G2-SPATIAL não implica escala física e G3 não implica ground truth | alegação indevida deve falhar | gate de claims | G3 |

## Estados de resolução

- `PASS`: contrato satisfeito com evidência verificável;
- `PARTIAL`: evidência suficiente apenas para uso restrito explicitamente delimitado;
- `BLOCKED`: ausência ou falha que impede o avanço;
- `NOT_APPLICABLE`: permitido somente com justificativa formal.

Contratos `RAW-201`, `GEO-205`, `CAL-201`, `CAL-202` e `SCOPE-201` são *fail-closed*: sua violação bloqueia imediatamente a fase.
