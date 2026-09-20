# Limitações do estudo científico 1

- **Somente duas aquisições experimentais.** A confirmação é temporal interna
  às aquisições existentes; não existe validação externa por aquisição.
- **Supervisão fraca e localizações cumulativas publicadas.** O target descreve
  presença da localização publicada, sem assegurar evento físico exaustivo,
  identidade física individual, extensão do fragmento ou onset exato.
- **BACKGROUND_CANDIDATE não é ausência física.** FP/FN são relativos às weak
  labels; não demonstram falso evento físico ou perda definitiva de fragmentação.
- **FINAL de seis samples, três por classe.** A granularidade é alta: um erro
  muda sensitivity/specificity da classe em 33,333… pontos percentuais e
  accuracy/balanced accuracy em 16,666… pontos percentuais neste desenho 3/3.
  Esses limites são transcritos do relatório final, sem nova análise estatística.
- **Confusão potencial entre aquisição e classe.** O fit final mantém
  bottom_up com 19 positivos/8 backgrounds e top_down com 6/17. Não houve
  rebalanceamento posterior. O desempenho não isola um efeito físico da condição.
- **Patches não são réplicas experimentais independentes.** Agrupar sites,
  contextos e modalidades e separar tempos não cria novas aquisições.
- **Exposição histórica não ML.** FINAL permaneceu reservado para ML até TI3-D,
  mas não era globalmente virgem. Prediction-first documenta ordem computacional,
  sem cegamento humano, pois metadados e IDs históricos podem revelar classes.
- **Seleção interna limitada.** A/B/C e a escolha pré-FINAL são comparações
  delimitadas; não sustentam significância, utilidade externa ou impossibilidade
  de outras famílias. Nenhuma escolha pode ser revista usando FINAL consumido.
- **Sem generalização externa ou estimativa populacional precisa.** 4/6 é o
  resultado descritivo deste conjunto, não a acurácia populacional do método.
- **Sem inferência causal ou forecasting.** Detection != forecasting != causality.
  Presença de localização publicada não é previsão de fragmentação futura.
- **Sem interpretação física absoluta do campo solutal.** ESM2/ESM5 representam
  campo relativo/normalizado, não concentração absoluta de Bi ou temperatura.
  Círculo não é máscara do fragmento; não há claim de recall físico exaustivo.

O estudo está encerrado. Estas limitações não autorizam repetição, tuning,
nova seed, labels/split/patches alternativos ou FINAL2. Pesquisa posterior
exige novo estudo e nova autorização. Fonte principal:
[relatório TI3-D](../TI3_D_FINAL/execution-report.md).
