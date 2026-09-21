# Study2-D — protocolo congelado de atribuição interna

Natureza: POST_HOC_CONTROLLED_ATTRIBUTION_ANALYSIS. A autorização principal e
a decisão complementar de custódia estão preservadas nesta pasta. O único
modelo é RF_REFERENCE: os 19 parâmetros totais de Study2-C, incluindo
100 árvores e random_state=42. Nenhum parâmetro, família, feature, época ou
threshold é selecionado nesta análise. O TEST anterior permanece consumido.

## Domínio, custódia e representação

Usar somente as 10.907 rows TRAIN originais: 3.858 GOLD e 7.049 backgrounds,
32 sites e 32 tracks, sem SILVER ou não rotulados. TRAIN_INPUT_MANIFEST.json
vincula identidades, offsets, shape uint8 (2,65,65) e três hashes por row ao
manifesto C e à autenticação restrita de integração. O campo histórico
pixels_materialized=false herdado de B não representa o estado atual do cache
C; o descriptor storage e a custódia canônica atual são explícitos.

Positivos: container B; backgrounds: cache compartilhado TRAIN/DEV C, com
pread de exatamente 8.450 bytes por offset TRAIN autorizado. Não há scan,
rehash integral, mmap, leitura do índice TEST, vídeo, FFmpeg ou nova extração
de patches. Metadados históricos de splits podem ser lidos exclusivamente
para provar exclusão e custódia. Isso não autoriza bytes de payload DEV/TEST.

A integração já autenticou opacamente as mesmas rows TRAIN uma vez, sem arrays
ou features. A leitura científica posterior, contada separadamente, autentica
cada row ao carregá-la uma única vez. Nenhum acesso posterior para hash ou
inspeção é permitido. Caches restritos têm somente custódia documental, conforme
a decisão explícita: sua integridade atual não é alegada como rehash material.

Uma única extração LBP20 percorre todos os pares TRAIN: P8/R1/uniform,
10 bins/range(0,10)/density=True por modalidade, estrutural antes de campo
solutal relativo. Matriz float64 em memória; sem scaler, novos descritores,
exportação de features, novos caches, modelos ou tensores float persistidos.

## Folds, amostragem e ordem

Os quatro folds são os mesmos de C, hash
85edac3d7da06994d7b16c4fa50e2aeb806abd7743a1d471842f54fdcf049ef2.
Validação por fold: 6+2 sites e 6+2 tracks bottom_up/top_down. Treino por fold:
18+6 por classe. Todas as observações GOLD/background dos grupos de validação
permanecem idênticas em todas as condições daquele fold.

Ordenar dentro de cada grupo por (frame_index,sample_id); a identidade serve
apenas de desempate determinístico. D1 seleciona índice floor((n-1)/2), a
mediana temporal inferior. D3 usa q={1/4,1/2,3/4}; D5 usa
q={0,1/4,1/2,3/4,1}. Aplicar q*(n-1), inteiro mais próximo com empate para
baixo, calculado racionalmente. Se n for menor que 3 ou 5, usar todas as rows.
Remover duplicatas e registrar effective_rows_per_group: até D3/D5, jamais
duplicar observações. DALL usa todas as rows elegíveis do grupo.

O ranking escolhe a inclusão. A matriz de cada fit conserva a ordem original
das rows TRAIN no manifesto C. Não reordenar por intensidade, desempenho ou
comprimento de trajetória. A agenda completa fica em STUDY2_D_ATTRIBUTION_DESIGN.json.

## A — diversidade de grupos

Uma observação D1 por grupo, GROUP_EQUAL (peso1 nesse caso). K por classe:
4,8,12,17,24; quotas bottom_up/top_down respectivamente3/1,6/2,9/3,13/4,18/6.
Para K<24, cinco salts STUDY2D_GROUP_R1 até R5. Ranking hexadecimal SHA256
do texto UTF-8 salt|fold_id|class|acquisition|group_id, classe POSITIVE/BACKGROUND;
desempate por group_id. Cada ranking ordena separadamente cada estrato;
prefixos das quotas produzem subconjuntos aninhados. K24 usa todo o pool uma
única vez por fold: 84 fits distintos. O saldo de classes por número de grupos
fica fixo; aumentar K também aumenta observações totais, sob D1 constante.

Comparar K24 menos K4/K8/K12/K17, pareando cada réplica ao K24 do mesmo fold.
K24 tem4 resultados; níveis menores têm20. Reportar média, mediana, desvio
padrão populacional (ddof=0), min/max/n, global e por aquisição. Deltas têm
média, mediana e contagens >0/=0/<0 sem tolerância retrospectiva.

Descriptor principal da diversidade aplica-se especificamente a K24−K17:
CONSISTENT_POSITIVE se média>0 e pelo menos15/20 deltas>0;
MIXED_POSITIVE se média>0 e menos15; NON_POSITIVE se média<=0.

## B — densidade temporal

K24, grupos e validação idênticos. D1/D3/D5/DALL; GROUP_EQUAL com peso
1/n_selected_rows de cada grupo em cada fit, sem class_weight. Reutilizar
os quatro K24/D1 de A, sem novo fit ou avaliação. Executar12 novos fits.
Contrastes D3−D1, D5−D1, DALL−D1 e DALL−D5, com quatro deltas pareados.
Descriptor de DALL−D1: CONSISTENT_POSITIVE se média>0 e >=3/4 positivos;
MIXED_POSITIVE se média>0 e menos3; NON_POSITIVE se média<=0.

## C — pesos

K24/DALL, grupos, observações e validação idênticos. Reutilizar GROUP_EQUAL/DALL
de B. Executar somente quatro fits OBSERVATION_EQUAL (peso1 por row). Grupo
com mais rows tem mais peso; os pesos totais por classe também podem mudar.
Esse braço não separa o efeito de equilíbrio entre grupos do equilíbrio de
classes. Bootstrap RF não implica influência efetiva exatamente igual por grupo.

Contraste GROUP_EQUAL−OBSERVATION_EQUAL por fold. Descriptor:
CONSISTENT_GROUP_EQUAL_BENEFIT se média>0 e >=3/4 positivos;
MIXED_GROUP_EQUAL_BENEFIT se média>0 e menos3;
NO_GROUP_EQUAL_BENEFIT se média<=0.

## Métricas, budget e encerramento

Reutilizar metric_bundle de C sem alteração: GMBA=0,5*(média dos recalls por
site GOLD + média das especificidades por track). Também BA/accuracy/precision/
recall/F1 por observação, detalhes por grupo e GMBA por aquisição. Secundárias
não substituem a primária. Sem p-values, intervalos inferenciais ou seleção.

Uma CLI científica, ordem A→B→C, exatamente84+12+4=100 fits, com contadores
de chamadas iniciadas e concluídas junto ao fit efetivo. As oito referências
reutilizadas não são fits. O orçamento não admite retry ou ramificação adaptativa.
Código/configurações/manifests/contratos são congelados antes da ciência em
commit filho direto do merge C; todos os dez jobs devem passar no SHA exato.
Receipt O_EXCL+fsync antecede bytes científicos. Falha após receipt consome
permanentemente a tentativa e preserva evidência parcial. Terminal fecha a
autoridade. Pós-run somente texto, aritmética independente e Git; nenhum refit.

PASS significa cumprimento do protocolo, qualquer que seja o sinal dos efeitos.
K17 é NUMERICAL_SCALE_BRIDGE, não reconstrução do Experimento1. TEST C não
aparece como condição comparável na tabela-ponte. Resultados finais de C e do
Estudo1 são somente referências históricas já fornecidas pelo autor.
