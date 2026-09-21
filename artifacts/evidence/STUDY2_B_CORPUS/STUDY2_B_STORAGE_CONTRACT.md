# Study2-B — HYBRID_STREAM_LEDGER_SELECTIVE_CACHE

Limites congelados: MAX_PATCH_CACHE_BYTES=2147483648;
MAX_TEMP_BYTES=268435456; MIN_FREE_DISK_RESERVE_BYTES=53687091200.
Pré-flight exige ainda espaço para o limite superior de231496200 bytes de
payload (27396×8450) e256MiB de metadados além da reserva. Antes de cada
escrita verifica-se tamanho projetado e disco livre; durante o streaming,
cada append revalida esses limites. Violação interrompe, preserva parcial,
sem limpeza automática/retry. Nenhum temporário de pixels é criado.

Formato equivalente a array memory-mappable:
`data/derived/study2b/multimodal_patches_uint8.bin`, payload C-contiguous sem
header, shape(N,2,65,65), uint8, offset0,8450bytes/row. A dimensão N depende
do suporte observado; formato sem header permite append sequencial sem arquivo
temporário ou reescrita do corpus. O manifesto fornece shape, dtype, ordem e
hash. `numpy.memmap(...,dtype='uint8',mode='r',shape=(N,2,65,65))` é uma
descrição de uso futuro, não uma segunda leitura experimental nesta tarefa.

`corpus-index.jsonl` contém todos os27396 registros; válidos mapeiam exatamente
para row_index contíguo e inválidos têm null. `background-pool.jsonl` guarda
somente metadados dos candidatos admissíveis. Os dois ledgers têm budget
agregado adicional de256MiB para impedir crescimento não delimitado.
Views lógicas somente rowindices ficam no manifesto textual versionado.

Cada arquivo é criado exclusivamente, com no-follow, sem overwrite. Hashes
do payload e ledgers são incrementais durante sua única escrita, seguidos de
flush/fsync; nada é reaberto para uma segunda inspeção de pixels. Cada patch
é hash de bytesY65×65 em ordemC; pairhash é SHA256 dos dois canais concatenados
estrutural primeiro. Não persistir float32, fullframes, PNG/JPEG, modelos ou
um arquivo por patch. Todos os grandes arquivos permanecem ignorados.

Registrar CORPUS_CONTAINER_BYTES, CORPUS_INDEX_BYTES, BACKGROUND_LEDGER_BYTES,
TEMP_PEAK_BYTES (zero por construção), FREE_DISK_AFTER, hashes e contagens.
RSS medido é pico do processo Python, não soma com decoders. Source auth
opens/bytes são separados de decoder opens, bytes nativos e comprimidos
internos não instrumentados; nenhum contador equivale a syscall global.
