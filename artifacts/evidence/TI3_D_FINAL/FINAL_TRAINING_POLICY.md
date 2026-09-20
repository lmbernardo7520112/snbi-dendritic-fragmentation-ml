# Política final de treinamento

TRAIN ∪ DEVELOPMENT contém exatamente 50 samples, 25 POSITIVE e 25 BACKGROUND_CANDIDATE. A ordem é a concatenação das ordens TRAIN e DEVELOPMENT de TI3-B; training-plan.json enumera cada ID, label, centro, patch, aquisição e contexto. Para FINAL, a ordem explícita de execução agrupa a source_inventory original e ordena sample_id dentro de cada frame; o plano registra os seis IDs nessa ordem antes dos pixels. Isso só determina a apresentação/inferência, preservando o vínculo ID/label e sem alterar o manifesto original ou seu hash. Não há rematerialização de ledger, deduplicação, replanejamento, seleção de backgrounds ou novo split.

Composição congelada: bottom_up_anti_parallel = 19 positivos / 8 backgrounds; top_down_parallel = 6 positivos / 17 backgrounds. Essa associação classe/aquisição permanece como limitação, sem rebalanceamento ou alteração de pesos. As modalidades do mesmo sample não são réplicas independentes.

DEVELOPMENT já encerrou a escolha de modalidade e família. Agora integra somente FINAL_TRAINING_SET; nenhuma nova decisão ou comparação é baseada nesses 50 samples. Métricas de ressubstituição são exclusivamente descritivas, não estimativas de generalização. FINAL possui seis IDs separados, três por classe; não participa do fit, hash lógico, parâmetros ou escolha.
