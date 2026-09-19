# Preflight autorizado — reparo operacional 1

HEAD inicial: `7994771e239afdb998a644626c423c1c627f80a0`.
Commit único de reparo: `febaa56efdcec210f6efb0d456ab1558bce7fe43`, filho direto do checkpoint.
Branch `feat/ti2r-solute-v2-calibration`; PR #10 confirmado OPEN/DRAFT,
head remoto C2 `0b820bc61e6dae3b7a98654a3b7d5cd292ca925e`,
base `fcfc5e1445467248566e881c61929d4d3da7b1d8`.
A diferença local/remota é conhecida e autorizada: checkpoint anterior e
commit de reparo locais. Não se alega publicação desses commits.

A decisão específica está em `authorization.md`. Ela permite uma correção
operacional, novo preflight e somente a primeira execução científica se todos
os contratos passarem. O incidente anterior permanece integralmente em
`../`, com seu manifesto divergente, relatórios e estado sem pixels.
Nenhum receipt anterior existia. Histórico: uma CLI, zero execução científica,
zero opens e zero bytes. Nenhuma autoridade científica antiga é reativada.

## Reparo mínimo e testes

A coerção ocorreu ao serializar a estrutura do manifesto usando
`JSON.stringify` na preparação anterior: JavaScript não preservou a distinção
lexical Python 1.0/1. O produtor agora lê os JSON congelados diretamente em
Python e chama `encode_manifest`, que usa `safe._encoded` e exige roundtrip
tipado com `_exact` inalterado. A configuração não passa por JavaScript.
O novo manifesto deve preservar float em minimum_entropy_bits,
saturation_low_y, saturation_high_y, median_limit_px, p95_limit_px e
maximum_limit_px, com valores 1.0, 16.0, 235.0, 1.0, 2.0, 3.0.

Três testes de regressão passaram: configurações reais textuais, fixtures
recursivas e recusa de substituições float/int, bool/int e string/int.
Inteiros genuínos, strings, bools, listas e maps mantêm tipos.
Suíte stdlib: 426 testes, 340 passes, 86 skips opcionais, zero falhas/erros.
A revisão independente do diff passou. Reparo restrito a dois arquivos:
runner e teste; 83 inserções/15 remoções. Não houve pixels nesses testes.

O runner separa C2 (CI/custódia remota) do HEAD de execução, exige parent
exato e diff limitado aos dois caminhos, e usa apenas o namespace fixo
`repair-1`. Isso preserva os terminais antigos e registra a nova autorização.
Os hashes históricos do runner continuam verificáveis em 7994771;
a evidência antiga não é editada para fingir que o reparo já existia.

## Congelamento e gate

Os 25 arquivos científicos são byte-idênticos a C1
`e1a98917a20431ecc1c758f210b5e974b3533734` e C2.
O avaliador também permanece byte-idêntico ao checkpoint anterior.
Não mudaram kernels, thresholds, índices, SS8/NGF, máscaras, preprocessing,
identificabilidade, critérios ou resíduos. Configurações completas, seis
tipos, hashes e HEAD são conferidos no manifesto serializado antes do runner.
O runner repetirá todos os contratos antes de criar receipt e abrir pixels.

Reservados: ESM1/ESM2:73/219 e ESM4/ESM5:98/295, oito buffers,
15.566.040 bytes previstos. Cada caso continua obrigado a passar todos os
critérios V2 individualmente, sem alteração do avaliador ou acesso a DEV.
A custódia histórica inclui exposição das referências em FRAG-DIRECT;
SEALED refere-se ao holdout solutal e não a virgindade global.

CI C2 reconfirmada: 35399554524 e 35399558120, SUCCESS, ambos os jobs e
todos os passos aprovados. Não representa CI do commit local de reparo.
O namespace novo admite apenas uma criação O_EXCL de receipt, com fsync,
timestamp, HEAD, manifesto, configurações, hashes e os oito IDs antes dos
bytes. Não existe retry científico ou fallback. Exceção encerra a tentativa.

Esta conclusão documental depende dos contratos exatos sobre o manifesto
final, conferidos na sua geração e novamente pelo runner. Se qualquer
contrato falhar, parar sem segunda correção nem acesso ao holdout.

PRE_HOLDOUT_GATE=PASS
