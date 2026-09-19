# Contrato futuro de partições internas por site

Unidade obrigatória de agrupamento: annotation_site_id. Cada site pertence
integralmente a uma única partição; todas as observações temporais, modalidades
correspondentes, versões e augmentations herdam essa atribuição.

A estratégia futura será determinística e independente de desempenho:
ordenar IDs pelo SHA-256 UTF-8 de "TI3_SITE_SPLIT_V1|" + annotation_site_id,
com desempate pelo ID. Na lista ordenada, a atribuição cíclica futura
TRAIN / DEVELOPMENT / FINAL_TEST reserva três partes aproximadamente iguais.
Quando cada aquisição tiver pelo menos três sites, executar a mesma regra
separadamente por aquisição para representá-las nas três partes.
Caso contrário, usar a lista global; não alegar estratificação impossível.

Esta regra é apenas especificação. **Nenhum ranking aplicado a partições,
ID de split, seed escolhida por desempenho ou FINAL_TEST foi materializado.**
O gate atual pergunta somente se existem ao menos três sites. A suficiência
estatística para estimativas precisas e a quantidade de backgrounds válidos
não foram certificadas por esse gate combinatório.

## Invariantes obrigatórios antes da materialização futura

- TRAIN, DEVELOPMENT e FINAL_TEST devem ser não vazios e disjuntos por site.
- Nenhuma observação do mesmo site pode atravessar partições.
- Um patch/contexto não pode conter localização reservada a outro split.
  É necessário definir suporte espacial e temporal e testar interseções;
  partições de IDs por si sós não garantem isolamento de pixels ou contexto.
- Se o contexto tornar sites inseparáveis, mantê-los em grupo maior ou
  excluir a interseção por regra geométrica declarada antes da avaliação.
  Não escolher exclusões por performance; não certificar antecipadamente
  que três grupos de contexto ainda existirão.
- Inputs somente ESM1/4 e opcionalmente ESM2/5 limpos; ESM3/6 são fonte de
  rótulo e nunca feature. Background também respeita suportes e IGNORE.
- Primeiro frame observado do site não é evento NEW nem onset. O target
  não é NEW_EVENTS(t) ou forecasting; nenhuma diferença temporal é calculada.
- Todos os parâmetros de geração e IDs devem ser congelados antes de avaliar
  o futuro FINAL_TEST. Seu estado atual é NOT_DEFINED_NOT_OPENED.

## Exposição e interpretação

Os dez ativos A0 permanecem ANNOTATION_CONTRACT_DEVELOPMENT_ONLY, não virgens
e não promovidos a FINAL_TEST. Os sites e seus rótulos foram examinados nesta
definição do target. A separação futura por site não apaga essa história nem
a exposição das marcações cumulativas finais.

O novo gate aprova, quando suficiente, a viabilidade estrutural dos weak
labels para propor avaliação interna agrupada. Não certifica ausência de
exposição histórica, independência de aquisições ou separação efetiva dos
futuros contextos. A autorização do teste e a elegibilidade dos inputs terão
de preservar essas limitações. Não há generalização experimental externa.
