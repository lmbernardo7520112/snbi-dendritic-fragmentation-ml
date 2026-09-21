# Decisão complementar — custódia restrita Study2-D

O autor respondeu à incompatibilidade concreta das seções 2, 12–13 e 39:

> Autorizo a alternativa restritiva: autentique materialmente somente as rows TRAIN necessárias ao Study2-D e faça a verificação dos caches que contêm DEV/TEST exclusivamente por evidências documentais já produzidas no Study2-C.
> Para o cache compartilhado TRAIN+DEV, é permitido abrir o container apenas para acessos direcionados aos offsets/rows pertencentes ao TRAIN, conforme o manifesto congelado. Não faça varredura sequencial, rehash integral do container, leitura de rows DEV ou qualquer operação que materialize bytes DEV.
> Para caches TEST, não abrir o arquivo binário nem o índice para inspeção de rows. Validar sua custódia apenas pelos hashes, tamanhos, manifests e evidências textuais já registrados no checkpoint Study2-C.

A precedência explícita é DEV_ROWS_READ=0, TEST_ROWS_READ=0,
TEST_CACHE_ROWS_READ=0 e TEST_FEATURES_COMPUTED=0. A integridade atual dos
bytes proibidos não será alegada como revalidada materialmente.

Para TRAIN, verificar identidades group_id/row_id, offsets, shape e hashes
disponíveis. Caso falte hash por row suficiente, registrar a limitação e
usar a cadeia histórica, sem ampliar o acesso. Após essa verificação, o autor
autoriza prosseguir com PR/merge de C e D conforme o anexo, sem acesso
científico a DEV/TEST. Nenhuma autorização anterior consumida é reaberta.
