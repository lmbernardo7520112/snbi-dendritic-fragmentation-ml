# ADR-0004 — Regra relativa de tempo físico

## Decisão

O tempo físico relativo será calculado por

\[
t_i = i\,\Delta t, \qquad \Delta t=1{,}18\;\mathrm{s}, \qquad i\in\{0,\ldots,N-1\}.
\]

O primeiro frame define `t = 0`. A cadência declarada no MP4, 5 fps, é metadado de reprodução e não substitui a regra física. A aceleração de reprodução resultante é `5 × 1,18 = 5,90`.

## Proveniência e limitação

O intervalo de 1,18 s foi congelado no protocolo científico aprovado e na auditoria forense precedente. A TI-1 não localizou, entre os documentos fornecidos, uma declaração primária independente desse intervalo. A regra é válida como asserção protocolar aprovada, mas sua cadeia documental deverá ser fortalecida quando a fonte original de aquisição estiver disponível.

## Consequência

O último índice de ESM1–3 corresponde a 345,74 s e o de ESM4–6 a 464,92 s. Não se confunde duração entre centros de frames com duração de reprodução do contêiner.
