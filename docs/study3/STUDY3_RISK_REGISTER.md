# Study3 — registro pré-ciência de riscos

Os riscos e respostas abaixo derivam do desenho autoral e das limitações
canônicas; não foram selecionados após inspecionar features ou scores Study3.
A fase atual não executa ciência. Nenhuma mitigação altera as escolhas fixadas
antes da exposição operacional de metadados.

| ID | Descrição | Impacto | Mitigação congelada | Risco residual |
| --- | --- | --- | --- | --- |
| R1 | Somente duas aquisições. | Confundir discriminação interna com transferência externa. | Escopo INTERNAL_EXPLORATORY; negar claims externos e preservar necessidade de novas aquisições. | Dois contextos físicos não identificam população ampla. |
| R2 | Weak labels automáticas e background candidato. | Erros frente ao overlay serem tratados como detecção física verdadeira/falsa. | Somente GOLD/BACKGROUND históricos; sem relabel ou promoção de unknown; linguagem física restrita. | Verdade física e recall exaustivo desconhecidos. |
| R3 | Correlação temporal dentro de trajetórias. | Pseudorreplicação e peso excessivo de grupos longos. | Uma representação e predição por grupo, folds agrupados, resumos fixos/T8. | Frames selecionados continuam correlacionados; quatro folds compartilham dados. |
| R4 | Possível correlação espacial entre grupos. | Contexto local compartilhado entre treino/validação. | Preservar identidade e folds; declarar limitação sem alegar isolamento espacial. | Folds históricos não são holdout espacial independente. |
| R5 | Aquisição↔classe e aparência de aquisição. | CNN/RF memorizar contexto e aparentar discriminação de interesse. | Controle ACQUISITION_ONLY TRAIN-fold, diagnósticos por aquisição e interpretação cautelosa. | Controle simples não exclui confundimento não linear ou latente. |
| R6 | Comprimento/suporte temporal como proxy de classe. | Seleção/representação refletir cobertura de anotação. | Controle log1p(n_rows), início, fim, span; T8 fixo e repeats explícitos. | Coverage LOGREG não identifica causalidade; resumos ainda incorporam trajetória observada. |
| R7 | Sobreajuste ou colapso de CNN com poucos grupos. | Resultados instáveis ou todos os grupos na mesma classe. | Duas arquiteturas fixas, seed=42, 30 epochs, sem search/early stopping; preservar negativos. | Seed única não quantifica variabilidade de inicialização; tamanho pequeno limita interpretação. |
| R8 | Apenas 64 grupos e quatro folds históricos. | Deltas parecerem confirmação precisa. | GMBA e contrastes descritivos; sem p-values; não tratar folds como experimentos. | Incerteza sobre novos grupos/aquisições não estimada externamente. |
| R9 | Exposição prévia a metadados TRAIN. | Alegação indevida de zero acesso ou adaptação encoberta. | Incidente e declaração pré-exposição; desenho autoral antecedente preservado; nenhuma estatística exploratória nova. | Exposição existe e deve permanecer declarada. |
| R10 | TEST C consumido e DEV usado historicamente. | Reutilizar reservas como confirmação nova ou para decisão Study3. | Negar materialização/índices/predições DEV/TEST antes de paths; nenhum novo holdout alegado. | Conhecimento histórico de resultados não desaparece com novo estudo. |
| R11 | Tentação de ajustar após resultado desfavorável. | Model shopping, fit 29 ou retry. | Budget de 28 fits, ordem única, receipt exclusivo e terminal; nenhuma etapa adaptada ao score anterior. | Governança e trilha de evidências devem ser cumpridas na execução futura. |
| R12 | Ambiente, dependências e guards históricos. | Determinismo operacional falhar; freeze publicado sem validação compatível. | Interpretador explícito, pins históricos, testes sintéticos/CI em SHA exato, zero skips Study3, registrar qualquer bloqueio. | Variação entre ambientes e incompatibilidade de guard com linked worktree não são resolvidas por método científico. |

## Regras operacionais de bloqueio

Os guards históricos exigem `.git` como diretório e rejeitam o linked
worktree autorizado. A execução efetiva única de cada guard, com interpretador
explícito, retornou exit 1 no requisito de standalone checkout; o
[incidente](STUDY3_PRE_SCIENCE_INCIDENT.md) registra a evidência e a proposta
delimitada de reparo. Isso bloqueia o freeze, sem constituir resultado
científico ou permissão para bypass. Após essa falha, nenhuma segunda execução
efetiva ou reparo desses guards foi autorizado. Preservar os scripts históricos
e não substituir o guard silenciosamente ou declarar seu gate PASS por inferência.

Há também uma dependência estática: `check_phase_scope.py` exige classificação
dos códigos Python versionados no manifesto histórico de três domínios. Os
novos arquivos Study3 precisarão de uma integração de governança explicitamente
autorizada antes de serem aceitos nessa verificação. Isso não altera o método
científico, mas não pode ser omitido do reparo operacional proposto. O guard
de imports também admite Torch somente em paths CNN históricos; uma extensão
deverá enumerar explicitamente os paths CNN Study3, sem abrir Torch globalmente.

Nenhuma falha autoriza instalação global, alteração do ambiente original,
abertura de cache, mudança de pin para contornar erro, retry científico ou
segunda arquitetura. Uma falha na CI remota encerra esta fase com proposta
limitada de reparo. Mesmo CI verde encerra sem receipt ou ciência.

Os controles de confundimento são diagnósticos; nenhum risco observado autoriza
rebalancear, excluir grupo, mudar fold ou retreinar. Extensões que precisem
dessas mudanças pertencem a outra decisão e permanecem NOT_CURRENT_WORK.
