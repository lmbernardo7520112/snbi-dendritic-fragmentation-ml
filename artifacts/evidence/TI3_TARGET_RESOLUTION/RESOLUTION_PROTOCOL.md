# TI3_TARGET_RESOLUTION — protocolo da resolução textual

Escopo: decisão de suficiência estrutural dos rótulos fracos A0 existentes.
O checkpoint A0 é 0f1284e86052e505e8ccfc9ceaecb58cb41065f2. Não há execução do extrator,
leitura de pixels, treinamento, seleção de modelo ou materialização de split.

## Regras fixadas antes de contar sites

- Entrada exclusiva: componentes e metadados textuais de
  artifacts/evidence/TI3_A0/extraction-results.json e development-manifest.json,
  autenticados contra os blobs do checkpoint.
- VALID_GRAPHICAL_CIRCLE gera POSITIVE de PUBLISHED_FRAGMENTATION_LOCATION.
  AMBIGUOUS_OR_NONCIRCULAR e SMALL_COMPONENT geram IGNORE. Nenhuma nova
  seleção por raio, score, aparência, dispersão, frequência ou desempenho.
- Tolerância autoral de associação: exatamente 3 px, distância euclidiana,
  inclusão da fronteira (distância ao quadrado <=9), sem ajuste posterior.
  Este é um parâmetro operacional fixado pelo autor, não nova certificação
  metrológica nem tolerância aprendida com estes resultados.
- Grafo separado por source/acquisition. Toda dupla de centros positivos
  na distância permitida recebe aresta. Cada componente conexo é um site.
  A transitividade preserva todas as ligações; o diâmetro de um site pode
  exceder 3 px. Nenhum segundo limite ou corte será introduzido.
- Identificador estável: source e hash dos annotation_ids ordenados.
  Centro representativo: medoid observado, mínimo da soma de distâncias
  quadráticas, desempate por annotation_id. Dispersão: diâmetro máximo,
  distância máxima e RMS ao medoid, sem interpretação de incerteza física.
- FIRST_CONFIDENT_OBSERVATION: menor frame aceito entre os realmente
  analisados, com tempo documental. Não é onset nem nascimento físico.
- Registrar cada observação e todos os IGNORE, inclusive repetição temporal.
  Centro de site, marca repetida e evento físico independente são distintos.
- Gate estrutural único: pelo menos três sites para três partições futuras
  não vazias sem dividir site. Estratificação por aquisição é possível quando
  a contagem permitir, não requisito adicional de PASS.
- Nenhum background patch, tensor, split ou ID de FINAL_TEST será produzido.
  O resultado não depende de desempenho, balanceamento escolhido ou tuning.

## Separação futura

Todo annotation_site_id, suas observações, modalidades e derivados pertencem
a uma única partição. O protocolo futuro deve impedir que contexto de um
patch atravesse sites reservados. Tamanho, contexto temporal, validação de
input limpo e regiões utilizáveis são decisões de materialização posterior,
antes de qualquer avaliação. Não se escolhem agora usando pixels.

Background candidato deve estar em suporte válido e limpo, suficientemente
distante do suporte de POSITIVE e IGNORE, excluindo overlays, bordas inválidas
e estado incerto. Suporte e distância de segurança precisam ser explícitos
na futura geração; a tolerância de associação 3 px não os certifica.
Ausência física de fragmentação não é uma classe negativa comprovada.

## Autoridade e exposição

A nova decisão autoral substitui a exigência anterior de recuperar todas as
marcações para este target limitado. O bloqueio A0 permanece histórico.
Os dez ativos A0 continuam ANNOTATION_CONTRACT_DEVELOPMENT_ONLY; não são
promovidos a FINAL_TEST nem poderão entrar como features. Seus sites e
anotações já foram expostos durante a definição do target. O futuro teste
interno agrupado não será apresentado como globalmente virgem ou externo.

A rejeição acidental do staging é ocorrência administrativa. Staging teve
duas solicitações: uma recusada antes de iniciar o comando e uma aprovada;
o único commit teve uma solicitação aprovada. Nenhuma dessas operações conta
como resolução do target, ciência, ML ou acesso experimental.

O protocolo, código e testes serão autenticados antes da primeira resolução
dos registros reais. Não haverá nova rodada para alterar a decisão obtida.
Somente artefatos desta pasta serão produzidos após o checkpoint.
