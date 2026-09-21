# Decisão complementar — decoder do gate histórico

Pergunta apresentada ao autor antes de abrir fontes nesta fase:

> O gate histórico exige reproduzir dez frames a partir dos MP4, mas o FFmpeg precisa decodificar internamente frames intermediários antes de selecionar esses dez. As seções 10–11 vedam acesso a frames inéditos antes do gate. Autoriza, somente para esse gate, essa decodificação interna, entregando ao detector apenas os dez frames históricos, sem visualizar, analisar ou salvar os intermediários? Ainda não abri os vídeos nesta fase.

Resposta explícita do autor:

> Autorizar apenas a decodificação interna descrita

A exceção é restrita ao gate histórico. Somente os dez outputs históricos
podem chegar ao detector; intermediários permanecem internos ao decoder.
Não há autorização para inspeção visual, análise ou gravação desses
intermediários. Não altera o requisito de freeze e CI antes da mineração
integral, nem os parâmetros A0. Aprovação recebida nesta mesma sessão.
