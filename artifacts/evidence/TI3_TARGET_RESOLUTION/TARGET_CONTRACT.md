# Contrato de localização publicada com supervisão fraca

A decisão autoral define o target **PUBLISHED_FRAGMENTATION_LOCATION_PRESENT**.
Sua suficiência estrutural é decidida em results.json; não é avaliação de modelo.

| Elemento | Regra normativa |
| --- | --- |
| LABEL_SOURCE | ESM3_ESM6_PUBLISHED_CIRCLES, somente registros produzidos pelo extrator A0 congelado |
| TARGET_SEMANTICS | PUBLISHED_FRAGMENTATION_LOCATION |
| POSITIVE | Centro de VALID_GRAPHICAL_CIRCLE já aceito em A0, sem novo filtro; semântica documental de localização cumulativa publicada |
| IGNORE | Todo componente ambíguo, rejeitado ou pequeno; regiões sobrepostas, cortadas ou de estado indeterminado continuam excluídas |
| BACKGROUND_CANDIDATE | Região válida sem localização publicada utilizável, suficientemente distante dos suportes POSITIVE e IGNORE |
| NEGATIVE_SEMANTICS | NO_PUBLISHED_ANNOTATION_IN_VALID_CANDIDATE_REGION; não significa ausência física |
| WHAT_IS_ONE_SAMPLE | Um candidato espacial de uma imagem em um instante, posteriormente materializável como patch |
| INPUT principal | Radiografia limpa ESM1 ou ESM4 |
| INPUT opcional | Radiografia ESM1/ESM4 + campo solutal relativo ESM2/ESM5 |
| INPUT proibido | ESM3/ESM6, círculos, overlays, máscaras gráficas, canais de rótulo ou metadados que revelem o target |
| FIRST_CONFIDENT_OBSERVATION | Menor frame entre os efetivamente analisados em que o marcador foi aceito; atributo da observação |
| Identidade | annotation_site_id operacional por fonte/aquisição e associação espacial de 3 px; todas as repetições permanecem juntas |
| Claim | Detecção/associação a localizações publicadas; não previsão de evento futuro ou causalidade |

O círculo marca uma localização publicada. Seu raio e interior não são
extensão física ou máscara de fragmento. O target aceita a incompletude da
extração; não busca inventário exaustivo. A classe positiva é definida pela
regra operacional publicada, sujeita à qualidade dos weak labels.
HIGH_CONFIDENCE é a aceitação geométrica congelada, não probabilidade
calibrada de evento físico verdadeiro. Não se mediu taxa de erro dos labels.

O ledger novo conserva ligação a cada registro A0. O semantic_label=UNKNOWN
histórico continua intocado no arquivo original; esta decisão dá uma
interpretação nova e restrita aos aceitos, sem reescrever A0 como PASS.

## Segurança espacial e background

Nenhum patch ou background candidato foi materializado. Antes da geração,
o suporte completo do futuro candidato precisa estar dentro de região de
input limpo validada e longe das áreas de segurança POSITIVE/IGNORE.
Essas áreas devem incluir o suporte do marcador gráfico ou bbox disponível,
a margem espacial pré-especificada e o contexto completo do patch. A mera
distância do centro não garante essa condição. Bordas inválidas, overlays
e regiões sem estado determinável devem ser excluídas.

Os 3 px de associação de sites não são tamanho de patch nem margem de
segurança automaticamente certificada. Tamanho/contexto e regras de contato
serão declarados antes da materialização futura, sem consulta a desempenho
ou pixels de FINAL_TEST. IGNORE jamais vira NEGATIVE para preencher quotas.

## Tempo, limites e autoridade

O frame e o tempo experimental são os do registro A0. Marcador cumulativo
observado em t não prova fragmentação física em t. Exato onset não é
necessário nem disponível para este target contemporâneo restrito.
Não se exige nem se infere permanência física do fragmento nessa coordenada.

Só existem duas aquisições documentadas. Repetições do site não aumentam N
independente; sites também não são réplicas experimentais independentes.
O futuro teste agrupado será interno e terá exposição histórica declarada.
A0 permanece desenvolvimento de anotações; nenhuma imagem é promovida a
FINAL_TEST por esta decisão.

G2_FRAG e G2_SOLUTE continuam fechados. Nenhum input estrutural ou solutal foi
aberto nesta resolução. PASS de target não autoriza treinamento nesta tarefa.

CIRCLE_IS_FRAGMENT_MASK=false; FRAGMENT_EXTENT_AVAILABLE=false.
EXACT_ONSET_REQUIRED=false; EXACT_ONSET_AVAILABLE=false.
FORECASTING_AUTHORIZED=false; CAUSALITY_CLAIM_AUTHORIZED=false.
EXTERNAL_GENERALIZATION_CLAIM=false.
