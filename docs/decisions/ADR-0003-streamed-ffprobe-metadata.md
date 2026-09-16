# ADR-0003 — Metadados por fluxo com ffprobe

## Decisão

Os metadados MP4 serão lidos diretamente dos membros do arquivo ZIP e enviados ao `ffprobe` por entrada padrão. Nenhum frame será decodificado ou persistido.

## Justificativa

A abordagem satisfaz a auditoria autorizada, preserva a imutabilidade dos dados brutos e evita antecipar a extração prevista para fase posterior. Os avisos produzidos pelo contêiner MP4 ao operar sobre fluxo não-seekable serão preservados e normalizados como evidência; campos que exigem decodificação, como formato de pixel, não serão inferidos.

## Consequência

Contagem, dimensões, codec, cadência, base temporal e duração podem ser auditados. Correspondência visual ou espacial não pode ser declarada nesta fase.
