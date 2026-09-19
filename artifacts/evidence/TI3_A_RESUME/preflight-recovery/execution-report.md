# TI3-A — recuperação operacional concluída antes dos pixels

**BLOCKED_STAGED_DATA_GUARD=RESOLVED; TI3_ML_ENVIRONMENT=READY.**
Checkpoint: `41d523e038e844588ee7724e07b00f75bdf29fdc`, parent `0f1284e86052e505e8ccfc9ceaecb58cb41065f2`.
Branch: feat/ti3-canonical-dataset-baseline. Esta recuperação remove o bloqueio
operacional e permite continuar somente no próximo gate TI3-A, sem reiniciar
resolução de target ou ciência G2/A0.

Somente resolve.py, run_resolution.py e test_resolution.py históricos foram
removidos do index por git rm --cached. Os três continuam locais, ignorados e
inalterados. Os 16 textos previamente staged permaneceram intactos.
Os três .py.snapshot.txt são cópias sem cabeçalho ou alterações. O manifesto
script-snapshots.sha256 é TSV com original_local_path, snapshot_tracked_path,
sha256 e byte_count. Não se alterou o data guard, .gitignore ou suas allowlists.

| Snapshot | Bytes | SHA-256 |
| --- | ---: | --- |
| resolve.py.snapshot.txt | 15204 | f2c78ec49edd3751973b72b22db19f992897410a8a3df3729ebec4623dcb6519 |
| run_resolution.py.snapshot.txt | 4961 | c76ab1f2909865e5f714e981217c21289f94eaf54af25f716089c511d9663f50 |
| test_resolution.py.snapshot.txt | 10440 | 1987618e654f8159fd3f65787da0c688079826cff870062217560973806be197 |

Os 20 paths exatos constam de verification.json. Bytes staged, working tree
e originais foram comparados. Guard: PASS, 329 entradas, zero bytes
experimentais. git diff --cached --check: PASS. Foi criado exatamente um
checkpoint documental da resolução. Index limpo após o commit.

A .venv inexistente foi criada com Python 3.12.3 dentro do repositório.
requirements-ti3-ml.txt contém exatamente NumPy1.26.4, SciPy1.11.4,
scikit-image0.24.0 e scikit-learn1.5.2. A primeira instalação falhou por DNS
no sandbox; após aprovação pontual de rede, o mesmo comando instalou
exclusivamente na .venv, sem alternativa de versões ou instalação global.
O resolver selecionou as dependências transitivas registradas em environment.json.
Não houve alteração do sistema, instalação global ou acesso a credenciais.

Um smoke técnico passou todas as 12 verificações: imports/versões,
LBP uint8 65×65, histograma de dez bins normalizado, RF100/seed42, fit,
predict, predict_proba e determinismo exato. Foram dois fits sintéticos,
zero ML científico, zero opens/bytes experimentais.
Fingerprint reproduzível do Python e versões:
`4629f874e0104bb9edec803c986c786764c9837fa2bc5634223f4a1141923979`.

Criado um workflow TI3 sintético separado; o workflow histórico G2 permanece
intacto. A CI remota não foi executada nesta recuperação. A publicação e
verificação no SHA C1 dependem do pré-registro completo e dos seus gates.
Não se afirma CI verde para arquivos locais.

O próximo gate é a viabilidade geométrica documental de TI3-A RESUME.
Na transição deste gate operacional: FINAL_TEST=NOT_DEFINED_NOT_OPENED.
Os novos arquivos de requisitos, checker, workflow e evidências ficam locais
até eventual C1 autorizado. O estado Git terminal será confirmado no relatório
da continuação; este relatório não antecipa outro commit ou publicação.

```text
BLOCKED_STAGED_DATA_GUARD=RESOLVED
TARGET_RESOLUTION_CHECKPOINT=COMMITTED
TARGET_RESOLUTION_SCRIPTS=PRESERVED_AS_TEXT_SNAPSHOTS
TRACKED_DATA_GUARD=PASS
TI3_ML_ENVIRONMENT=READY
TI3_ML_DEPENDENCIES=PINNED
TI3_SYNTHETIC_DEPENDENCY_TESTS=PASS
EXPERIMENTAL_OPENS=0
SCIENTIFIC_ML_RUNS=0
ML_FINAL_TEST=NOT_DEFINED_NOT_OPENED
TI3_A_RESUME_READY=true
```
