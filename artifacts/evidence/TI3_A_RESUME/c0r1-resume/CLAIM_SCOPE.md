# Limites da primeira execução TI3-A

Target e contratos científicos permanecem os já preparados: concordância com
localização cumulativa publicada, sob HIGH_CONFIDENCE_PLUS_IGNORE. Ausência de
localização utilizável produz BACKGROUND_CANDIDATE, não ausência física de
fragmentação. A0 não fornece máscara de fragmento, onset físico exato ou
inventário exaustivo. Detecção/classificação associativa não é forecasting
nem causalidade. Não há generalização externa ou comparação independente de
aquisições; patches, sites e instantes não são réplicas experimentais.

TRAIN mantém ESM1:16 positivos/6 backgrounds versus ESM4:1 positivo/11
backgrounds. Classe pode se confundir com aquisição/condição. Nenhum balanceamento
por aquisição, reseleção ou ajuste adaptativo é permitido após esta constatação.
TRAIN17+17, DEVELOPMENT8+8 e FINAL3+3 permanecem como planejados.

Os seis samples FINAL têm baixa potência e métricas com grande granularidade;
não sustentam inferência externa. Seu estado é
SEALED_WITH_HISTORICAL_NON_ML_EXPOSURE: exposição histórica declarada, reserva
de acesso para ML, não virgindade global. Nenhum FINAL será aberto nesta tarefa.

Uma única execução estrutural LBP/RF, sem mínimo de desempenho para PASS.
O suporte integral de todos os patches TRAIN/DEV deve passar antes do fit.
Falha de suporte não permite excluir, substituir ou deslocar um sample.

SOLUTAL_MODEL_INPUT=NOT_USED; ESM2/ESM5=RELATIVE_SOLUTE_FIELD.
FORECASTING_AUTHORIZED=false; CAUSALITY_CLAIM_AUTHORIZED=false;
EXTERNAL_GENERALIZATION_CLAIM=false; TI3_B_AUTHORIZED=false;
MERGE_AUTHORIZED=false. Não há CNN, concentração absoluta de Bi ou temperatura.
