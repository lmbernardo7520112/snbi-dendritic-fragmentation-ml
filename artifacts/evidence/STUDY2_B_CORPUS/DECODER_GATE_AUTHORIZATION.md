# Study2-B — autorização complementar do gate histórico

Pergunta apresentada antes de qualquer abertura de vídeo Study2-B:

> Para reproduzir os pares históricos no gate Study2-B, o FFmpeg precisa decodificar frames intermediários dos MP4 ESM1/2/4/5 antes de selecionar os cinco índices históricos. A seção 35 limita o gate aos pares já expostos. Autoriza apenas essa decodificação interna, entregando ao código somente ESM1/2:73,146,219 e ESM4/5:98,197, sem analisar, visualizar ou salvar intermediários? Nenhum vídeo foi aberto nesta fase.

Resposta explícita do autor:

> Autorizar apenas a decodificação interna descrita

Essa exceção permite somente a decodificação interna necessária à seleção dos índices históricos. Não autoriza análise, visualização, gravação ou entrega dos intermediários ao código de construção. A construção integral permanece condicionada ao gate, freeze e CI previstos no anexo.
