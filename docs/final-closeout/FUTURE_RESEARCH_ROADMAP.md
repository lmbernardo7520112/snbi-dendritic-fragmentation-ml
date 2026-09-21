# Agenda futura após o encerramento científico

Este roadmap é planejamento documental derivado das [limitações registradas](SCIENTIFIC_LIMITATIONS.md) e da [atribuição D](../../artifacts/evidence/STUDY2_D_ATTRIBUTION/EXECUTION_REPORT.md). Nenhum item foi executado neste fechamento. As ideias abaixo não são resultados, nem prometem melhoria. O pipeline final RF_REFERENCE + GOLD_PLUS_SILVER e os conjuntos finais consumidos permanecem preservados.

## A. Possibilidades de investigação com os dados atuais

| Direção | Pergunta futura | Condição metodológica para uma decisão posterior |
| --- | --- | --- |
| Representação temporal por site | Uma trajetória pode ser representada como unidade de informação, em vez de várias rows isoladas? | Definir previamente unidade, tarefa e avaliação, reconhecendo correlação e exposição histórica. |
| Agregação temporal | Estatísticas ou resumos ao longo da trajetória reduzem redundância sem apagar variações relevantes? | Congelar regras de agregação e evitar usar grupos de avaliação para defini-las. |
| Sequence embeddings | Uma representação de sequência captura estrutura temporal ausente no LBP por patch? | Especificar um estudo separado, orçamento e controles antes de qualquer ajuste. |
| Self-supervised representation learning | Os dados não rotulados podem apoiar representações úteis sob avaliação agrupada? | Definir fronteiras de acesso e pré-treino, sem contaminação dos conjuntos reservados do novo desenho. |
| Verificação de anotação assistida por humanos | Especialistas conseguem esclarecer ambiguidades da evidência gráfica? | Registrar protocolo, discordâncias e proveniência; não converter verificação gráfica em confirmação física automática. |
| Formulações positive-unlabeled | Tratar backgrounds como candidatos, em vez de ausência física comprovada, melhora a adequação da tarefa? | Estabelecer hipóteses de identificação e novos critérios de avaliação explícitos. |
| Augmentation fisicamente restrita | Transformações justificáveis preservam a semântica experimental? | Justificação física e contrato próprio antes da execução; nenhuma transformação arbitrária retrospectiva. |

Essas possibilidades são internas ao mesmo domínio limitado. Não tornam os dados atuais novas aquisições independentes e não autorizam reabrir DEV/TEST consumidos. Um estudo futuro precisaria declarar seu caráter exploratório, sua exposição histórica e sua nova governança; o fechamento atual não escolhe arquitetura, seed, threshold ou novos backgrounds.

## B. Evidência necessária para generalização externa

| Necessidade | O que acrescentaria |
| --- | --- |
| Novas aquisições independentes | Avaliação da transferência além das duas aquisições atuais. |
| Novas réplicas experimentais | Unidades experimentais adicionais, distinguindo repetição física de repetição temporal de rows. |
| Novas composições e condições | Teste explícito do domínio de validade e de mudanças de distribuição. |
| Ground truth independente | Validação do significado físico, com critérios e incertezas separados dos overlays publicados. |
| Holdout experimental externo | Confirmação com novas unidades reservadas antes das decisões de modelagem, sem reutilizar o TEST já consumido. |

Representações mais complexas ou mais frames das mesmas fontes não substituem esses requisitos. O estudo presente não estabelece causalidade física ou validação externa.

## C. Próxima possibilidade editorial

O programa dispõe de evidências canônicas para uma entrega acadêmica futura que abranja Experimento 1 + Study2-A/B/C/D. A entrega anterior em `academic-deliverable-build/` foi preservada. `ACADEMIC_DELIVERABLE_READY_FOR_BUILD=true` expressa prontidão documental; não autoriza construir, executar ou modificar um notebook agora. Nenhuma Generation 5, nova compilação ou atividade científica foi iniciada neste fechamento.
