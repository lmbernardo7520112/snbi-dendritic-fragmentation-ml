# Study3-CNN — especificações verificáveis

As especificações implementam o protocolo autoral anterior à exposição a
metadados. A recuperação permite testes exclusivamente sintéticos; nenhuma
especificação, fixture ou CI concede autoridade experimental. O status efetivo
dos testes pertence aos relatórios de verificação, não a esta matriz normativa.

## Modelo de domínio

`AcquisitionId`, `GroupId`, `PositiveSiteId`, `BackgroundTrackId`,
`ObservationId`, `FrameIndex`, `FoldId` e `WeakLabel` explicitam identidade e
semântica. `TrajectoryObservation` e `TrajectoryGroup` organizam observações;
`TemporalSelection`, `TemporalRepresentation` e `RepresentationKind` tornam
seleção e representação verificáveis. `Study3FitSpec`, `Study3MetricBundle`,
`Study3Result` e `Study3TerminalState` expressam budget, saída e encerramento.

GroupId identifica uma única acquisition e uma única class. Cada grupo ocupa
TRAIN xor VALIDATION no fold; as duas funções são partes do TRAIN histórico.
Rows são ordenadas por `(frame_index, sample_id)`. Site≠evento físico,
track≠ausência física e trajectory≠experimento independente.

## Contratos e critérios de aceitação

| Especificação | Regra | Verificação sintética exigida |
| --- | --- | --- |
| S3-SPEC-001 | Exatamente 64 grupos TRAIN históricos, 32 positivos/32 backgrounds; contrato documental de 10.907 rows, 3.858 GOLD/7.049 BG. | Admitir contrato correto; negar populações, contagens, tiers e grupos divergentes sem I/O experimental. |
| S3-SPEC-002 | Nenhuma identidade de grupo cruza lados do fold; preservação de quatro folds históricos. | Fixtures com overlap, fold inválido, aquisição/classe inconsistente e identidade duplicada são negadas. |
| S3-SPEC-003 | DEV/TEST negados antes de acesso ao path. | Path sentinela que falha ao ser inspecionado; solicitação proibida é negada sem acionar a sentinela. |
| S3-SPEC-004 | Ordem temporal determinística `(frame_index, sample_id)`. | Permutações sintéticas de entrada produzem ordem/representação idênticas; tie de frame é resolvido por sample_id. |
| S3-SPEC-005 | A0 D1 seleciona rank `(n-1)//2`. | Casos par/ímpar distinguem lower median de upper median e de média. |
| S3-SPEC-006 | A1 mean por feature sobre todas as rows. | Valores sintéticos conhecidos e dimensão 20; nenhuma seleção de subset implícita. |
| S3-SPEC-007 | A2 median numérica por feature. | Fixtures pares/ímpares; caso par usa média dos dois valores centrais, distinguindo A2 da seleção temporal A0. |
| S3-SPEC-008 | A3 quantis 0.25/0.50/0.75 lineares, concatenação q25→q50→q75, dimensão 60. | Valores conhecidos distinguem interpolação linear de nearest rank; método e ordem fixos. |
| S3-SPEC-009 | T=8 usa ranks reais mais próximos, tie inferior, repeats determinísticos. | Endpoints, rank fracionário, desempate exato do helper, n=1/n<8, oito posições; nenhum pixel/frame sintético na seleção científica. |
| S3-SPEC-010 | Inputs CNN provêm exclusivamente do TRAIN histórico GOLD/BACKGROUND. | Negar tiers/splits proibidos antes de materialização; distinguir fold VALIDATION de C DEVELOPMENT. |
| S3-SPEC-011 | Scalers são fitados somente no lado TRAIN do fold. | Sentinelas/extremos na validação não alteram mean/std; std=0→1; mesmo princípio no StandardScaler metadata. |
| S3-SPEC-012 | Plano imutável com 16 RF + 4 CNN1D + 4 CNN espacial-temporal + 4 LOGREG = 28 fits. | Verificar todas as identidades previstas, unicidade, contagens por família/fold e callbacks de começo/fim. |
| S3-SPEC-013 | Fit 29, fit duplicado, omitido ou fora da ordem são negados. | Ledger e callbacks sentinela; tentativa rejeitada não executa learner. |
| S3-SPEC-014 | Zero adaptive tuning. | Contratos alterados, família/seed/T/epoch/arquitetura extra e modelo não previsto são negados. |
| S3-SPEC-015 | Receipt durable O_EXCL+fsync antecede primeiro binário em eventual fase autorizada. | Sequência de callbacks sintéticos; receipt duplicado negado; grant ausente/inválido nega antes de path. Nesta fase nenhuma receipt científica real é criada. |
| S3-SPEC-016 | TEST C permanece CONSUMED. | Leitura/predição/extrator TEST e cache/index TEST não possuem rota admitida; código não reabre autoridade histórica. |
| S3-SPEC-017 | Exposição de metadados não altera desenho. | Conferir contratos contra declaração pré-exposição e prompt; nenhuma distribuição nova justifica alteração. |
| S3-SPEC-018 | CNN1D input B×20×8 e output B×2; arquitetura fixa de 5.122 parâmetros. | Shapes, camadas, contagem e inicialização determinística seed=42. |
| S3-SPEC-019 | CNN espacial-temporal input B×8×2×65×65 e output B×2; 2.138 parâmetros. | Encoder espacial único compartilhado; head Conv1d; ausência Conv3d/GRU/LSTM/attention/BatchNorm/Dropout. |
| S3-SPEC-020 | Coverage features têm ordem e denominadores 293/394 fixos; aquisição-only não fita learner. | Features manuais sintéticas, majority por aquisição somente TRAIN e tie classe 0. |
| S3-SPEC-021 | Uma predição por grupo; GMBA é primária. | Confusões conhecidas, classes[0,1], recalls por classe, métricas secundárias e diagnósticos por aquisição. |
| S3-SPEC-022 | Sete contrastes fixos, quatro deltas pareados, descritores exatos sem p-values. | Deltas positivos/mistos/não positivos, zero exato e std ddof=0. |
| S3-SPEC-023 | Acesso dirigido a offsets, sem mmap, scan, symlink ou decodificação. | Fixtures descartáveis de bytes sintéticos; symlinks/path inválido/MP4/SILVER/TEST cache negados; nenhum FFmpeg. |
| S3-SPEC-024 | Result schema e terminal distinguem sucesso, falha consumida e autorização fechada. | Saídas sintéticas completas; falha não vira PASS e não permite segunda invocação. |
| S3-SPEC-025 | Recuperação termina em freeze+CI; código científico permanece desautorizado. | Autoridade atual false, gates negam receipt/load/fit; nenhuma execução do runner científico para testar sua negação. |

Para q=i/7, um meio-rank exato não ocorre com n inteiro; o teste de empate do
helper usa uma fração sintética apropriada para verificar a regra geral.
Essa fixture não muda as oito posições científicas.

## Alocação da implementação e testes

| Camada | Responsabilidade | Arquivo de testes |
| --- | --- | --- |
| `study3_domain.py` | Entidades, tipos e invariantes locais. | `test_study3_domain.py` |
| `study3_design.py` | População, folds, plano e contratos invariáveis. | `test_study3_design.py` |
| `study3_io.py` | Admissão TRAIN e delegação do reader dirigido histórico. | `test_study3_io.py` |
| `study3_temporal_features.py` | A0–A3, T8 e alinhamento por grupo. | `test_study3_temporal_features.py` |
| `study3_cnn.py` | Duas arquiteturas, scaler CNN1D TRAIN-only e treino congelado. | `test_study3_cnn.py` |
| `study3_models.py` | RF_REFERENCE, quatro features metadata, scaler/LOGREG, acquisition-only e callbacks. | `test_study3_models.py` |
| `study3_metrics.py` | GMBA, secundárias e contrastes. | `test_study3_metrics.py` |
| `study3_execution.py` | Autoridade, receipt ordering, budget, outputs e terminal. | `test_study3_execution.py` |

O perfil Study3 deve terminar com zero skips/failures/errors; o número efetivo
de testes/passes deve ser reportado. Regressões C/D usam somente fixtures
sintéticos. Dados reais, manifests usados como fixtures de performance,
learner experimental e runner científico são proibidos nesta fase.
