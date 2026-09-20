# Contrato de I/O de execução única

Nenhum byte experimental antes do D1 publicado, seis jobs CI SUCCESS e receipt exclusivo durável. O leitor usa allowlist exata de metadados, caminhos relativos sem symlinks, abertura O_RDONLY|O_NOFOLLOW e hash na única leitura; nenhuma reabertura para hash ou inspeção. Contadores registram tentativas, opens e bytes reais, inclusive falhas parciais.

FINAL_TRAINING_SET: ESM1/2:73,146,219 e ESM4/5:98,197. Dez buffers, uma leitura adicional cada, 19.469.052 bytes. Não há outros buffers TRAIN/DEV.

Somente após fit único e freeze lógico durável: ESM1/2:293 e ESM4/5:295. Quatro buffers FINAL, 7.783.020 bytes. Total máximo 14 opens e 27.252.072 bytes. ESM1/2 têm 1.951.506 bytes por buffer; ESM4/5 têm 1.940.004.

Suporte estrutural preserva chroma>=20, halo quadrado5, bandas12%/15%, borda4 e erosão3×3 de um pixel. Solutal preserva suporte geométrico12%/15%/borda4/erosão1 sem exclusão cromática, pois cor é campo. Patches65 exigem suporte integral; nenhum centro, margem ou sample é substituído. A admissão FINAL é explícita no novo módulo, preservando o split original; não falseia TRAIN para atravessar guards antigos.

Se qualquer suporte FINAL ou hash falhar, interromper antes de inferência/métricas parciais, registrar BLOCKED_FINAL_SUPPORT_OR_INTEGRITY e contadores reais. O controle consome FINAL conservadoramente já na primeira abertura bem-sucedida, mesmo se uma divergência de tamanho impedir a leitura de bytes; opens e bytes continuam distintos no registro. Portanto, após primeira leitura FINAL, ML_FINAL_TEST=CONSUMED irreversivelmente, inclusive falhas posteriores. Sem retry, novo FINAL ou retorno a DEV.

Nenhum ESM3/6, frame novo, ZIP/MP4, FFmpeg/FFprobe ou fonte externa. Nenhuma exportação de pixel, patch, array de features ou modelo binário; resultados somente textuais. Instrumentação da aplicação não é monitoramento universal de syscalls.
