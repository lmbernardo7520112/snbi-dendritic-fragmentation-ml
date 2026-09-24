# Study3 — contrato TRAIN-only e proveniência

## Fronteira da fase atual

A recuperação permite leitura textual necessária de contratos, schemas,
identidades, counts canônicos, folds, paths lógicos, hashes, offsets, dtype,
shape e código. Não permite payload binário científico, cache, ndarray real,
pixels, LBP real, fit, performance ou estatísticas novas do corpus. A leitura
antecipada anterior é explicitamente
[TEXTUAL_TRAIN_METADATA_EXPOSURE_ONLY](STUDY3_PRE_SCIENCE_INCIDENT.md), não zero
metadados e não acesso científico a pixels.

Somente uma decisão futura pode autorizar materialização TRAIN. Esta fase não
cria scientific receipt e não executa o preflight científico nem o runner.
Documentação histórica de DEV/TEST não equivale a autorização para seus
payloads, índices ou novas predições.

## Fontes canônicas e hashes textuais

Precedência: FINAL_CLOSEOUT → EVIDENCE_INDEX → evidência da fase → Git → código.
Conflito material de fonte implica SOURCE_CONFLICT e bloqueio da operação
dependente; não conciliar por memória ou nova inspeção de pixels.

| Documento | SHA-256 textual |
| --- | --- |
| `artifacts/evidence/FINAL_CLOSEOUT/FINAL_STATE.json` | `cd601398db7ba26ee2889b0fafb481a8bd855a05ff0368e18c201bca47ee4858` |
| `artifacts/evidence/FINAL_CLOSEOUT/CANONICAL_METRICS.json` | `00ae3fe20053f439d943538489efddb0a79fc375e7d1344d6ac166451078350a` |
| `artifacts/evidence/FINAL_CLOSEOUT/PROVENANCE.json` | `9e12517f94967e93b6d4be5dc76be18448bb5605a0205457d02dd09439b2bb4f` |
| `artifacts/evidence/FINAL_CLOSEOUT/verification.json` | `700ed175a2493e3fcd6b1bc064b61fca81d8b11cd1d573b1bdccd0dd51e861f2` |
| `artifacts/evidence/STUDY2_D_ATTRIBUTION/TRAIN_INPUT_MANIFEST.json` | `6ae3eee8e2fbe2c2e5de55eb84cb35b0ca7b561d37a8426b11125870003de531` |
| `artifacts/evidence/STUDY2_D_ATTRIBUTION/STUDY2_D_ATTRIBUTION_DESIGN.json` | `6db95b662e1e5e429a5cddbbdd8fd67bb4e418d2bef679c9fb56fc74cce81deb` |
| `artifacts/evidence/STUDY2_D_ATTRIBUTION/MODEL_CONTRACT.json` | `18429f2545393957c6430c677c1b6144a6416ed3e5dd1a244322051e04428e22` |
| `artifacts/evidence/STUDY2_C_BENCHMARK/MODEL_CONTRACT.json` | `2f0d73280fe09fdf6b8bb25ba84cb075c9c725e44d6f41cae94d95bb392659df` |

O HANDOFF externo autorizado tem SHA-256
`71bb1bf8f346f445c87561de86329d994354412354b879959f72cb4255bef445` e permanece
imutável. Nenhum hash desta tabela é nova autenticação de cache científico.
Os históricos A/B/C/D, Experiment 1 e entregas acadêmicas são preservados.

O manifesto TRAIN D reúne exatamente a população C TRAIN GOLD/BACKGROUND.
O design D fornece o mapa histórico de folds. Seu hash canônico é
`85edac3d7da06994d7b16c4fa50e2aeb806abd7743a1d471842f54fdcf049ef2`, com JSON
sort_keys=True, separators=(",",":"), ensure_ascii=True, allow_nan=False.
Não reexecutar o planner D nem criar novo split.

## População admitida

Contrato: 10.907 rows, 3.858 GOLD e 7.049 BACKGROUND; 32 grupos positivos e
32 backgrounds; quatro folds; duas aquisições históricas. Admissão requer
`split="TRAIN"` e uma das combinações exatas:

| label | tier | kind |
| ---: | --- | --- |
| 1 | GOLD | positive |
| 0 | BACKGROUND | background |

IDs únicos, uma classe/aquisição por grupo, fold válido e locators históricos
imutáveis são obrigatórios. Negar SILVER, todos os UNLABELED, DEV/DEVELOPMENT,
TEST, reserve tracks, sites inválidos e identidade desconhecida. A validação
de fold usa grupos retidos do TRAIN histórico, não C DEV ou TEST.

## Locators históricos, sem abertura nesta fase

Os paths abaixo provêm de `study2d_io.py`, TRAIN_INPUT_MANIFEST e da custódia
documental D. São paths lógicos, não descoberta por tentativa ou afirmação de
presença local. Não copiar containers compartilhados indiscriminadamente.

| Classe | Container lógico | Tamanho documental | Regra |
| --- | --- | ---: | --- |
| GOLD | `data/derived/study2b/multimodal_patches_uint8.bin` | 139.425.000 bytes | Somente os offsets TRAIN positivos explicitamente admitidos. |
| BACKGROUND | `data/derived/study2c/cachetrain_dev.bin` | 73.827.650 bytes | Container compartilhado não concede acesso DEV; somente offsets TRAIN autorizados. |

Cada row: 8.450 bytes, dois canais de 4.225 bytes, shape[2,65,65], dtype uint8;
offset=row_index×8450. Canal 0 STRUCTURAL_Y, canal 1 RELATIVE_SOLUTE_FIELD_Y.
Validar hash do par e dos dois canais contra os descriptors congelados.
Nunca abrir `cachetest.bin`, `cachetest.jsonl`, índices TEST, MP4 ou vídeos
fonte ESM. Não reconstruir patches nem chamar FFmpeg/FFprobe.

O root admitido pelo reader Study3 é exclusivamente WORKTREE_ROOT, sem
fallback. A presença dos containers locais não foi verificada nesta fase.
O original pode ser consultado somente no escopo textual/localizador e de
interpretador read-only expressamente autorizado; isso não admite abrir seus
payloads. Nenhuma escrita ocorre fora do worktree Study3. Se os recursos
materiais não estiverem disponíveis no root admitido, uma decisão posterior
de custódia será necessária, sem copiar containers compartilhados ou ampliar
paths silenciosamente. Este contrato não afirma disponibilidade operacional
para ciência.

## Ordem de custódia exigida para eventual ciência futura

O código define somente o formato de um documento futuro em
`docs/study3/STUDY3_SCIENCE_AUTHORIZATION.json` e de sua prova operacional de CI
em `.bootstrap-test-tmp/study3/ci-proof.json`. Esses nomes são referências
prospectivas, não grants existentes nem arquivos a criar nesta recuperação.
A decisão futura deve provir do autor; um JSON com formato válido não é,
por si só, comprovação independente de autoria ou assinatura criptográfica.

1. Validar decisão futura separada do autor que vincule exatamente freeze SHA,
   HEAD, branch, hashes imutáveis dos contratos, budget de 28 fits, limites de receipt
   e TEST, além de prova de CI verde no SHA. Nenhuma decisão desse tipo é
   criada nesta fase; nenhuma autoridade Study2 fechada é reativada.
2. Criar receipt científico durável exclusivo antes do primeiro binário;
   receipt duplicado fecha a tentativa.
3. Validar split, tier, identidade, locators e grant antes de examinar paths.
4. Delegar a `study2d_io.TrainCorpusAccess`, preservando walk sem symlink,
   arquivos regulares e descriptors imutáveis.
5. Ler somente `os.pread` dos ranges admitidos. Sem scan integral, hashing
   integral, mmap permissivo ou acesso ao índice do container compartilhado.
6. Autenticar as três hashes de cada row e fingerprint do container antes e
   depois dos ranges; fechar descriptors em sucesso/falha.
7. Reutilizar patches TRAIN em memória para LBP uma vez/row e T=8, sem releitura
   adaptativa ou artefatos de features/modelos fora do contrato.

Os contadores do reader medem operações da aplicação, não monitoramento
universal de syscalls ou controle de páginas do kernel. Esse limite não deve
ser ocultado. Testes desta fase usam bytes sintéticos controlados, nunca os
containers listados.

## Fronteira de publicação

O freeze, quando todos os gates forem aprovados, deverá conter somente
documentação, contratos, código, testes e workflow. Deverá excluir receipt
científico, features, modelos, patches, resultados e
`artifacts/evidence/STUDY3_EXECUTION/`. Todo material experimental continua
fora do Git. A verificação de CI é um gate operacional; não abre TRAIN, DEV
ou TEST. O [claim scope](STUDY3_CLAIM_SCOPE.md) permanece interno/exploratório.
