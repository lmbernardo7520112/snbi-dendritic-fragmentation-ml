# TI-1 — Especificação de execução da auditoria determinística

## Autorização e propósito

A TI-1 foi autorizada exclusivamente para leitura *read-only* de metadados, formalização da regra de tempo físico, verificação da correspondência entre modalidades e testes determinísticos dos contratos. A etapa produz evidências para G1 (semântica das modalidades) e G2-TEMP (correspondência temporal em nível de índice).

## Operações permitidas

- verificar novamente os hashes congelados em G0;
- ler metadados dos seis membros MP4 diretamente do ZIP, por fluxo;
- registrar codec, dimensões, contagem de frames, cadência e duração do arquivo;
- aplicar a regra física previamente aprovada, com índice de frame iniciado em zero;
- verificar completude das tríades e igualdade de contagem, cadência e duração por condição;
- executar testes unitários, validações e guardrails de escopo.

## Operações proibidas

Permanecem proibidos: extração massiva ou persistente de frames, análise pixel a pixel, registro espacial, ledger de eventos, definição de splits, criação de dataset, baseline, CNN, treinamento e avaliação. Nenhum artefato de imagem ou modelo pode ser produzido.

## Contratos

| ID | Contrato | Evidência |
|---|---|---|
| TI1-META-001 | Metadados são lidos sem extrair frames para disco | `acquisition_metadata.json` |
| TIME-001 | FPS do MP4 não representa tempo físico | `time_rule.json` e teste unitário |
| TIME-002 | `t(i) = i × 1,18 s`, com `i` iniciado em zero | relatório G2-TEMP |
| MOD-001 | Cada condição contém radiografia, soluto relativo e anotação cumulativa | relatório G1 |
| SYNC-001 | As três modalidades da condição têm mesma contagem, cadência e duração do arquivo | relatório G2-TEMP |
| SCOPE-001 | Nenhum artefato ou módulo TI-2+ existe | auditor de escopo |

## Critério de encerramento

A TI-1 somente pode ser proposta para encerramento se todos os testes passarem, G1 e G2-TEMP forem avaliados, a limitação de proveniência de 1,18 s estiver explícita e não houver violação de escopo. O encerramento e qualquer início de TI-2 dependem de autorização posterior do autor.
