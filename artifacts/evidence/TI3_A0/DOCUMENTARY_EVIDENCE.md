# TI3-A0 — evidência documental da semântica das anotações

Esta auditoria é documental. O checkpoint histórico TI3-A está preservado em
`1e7f5e8b382e84fd1259637722ce9774ffed7df3`. Nenhuma conclusão abaixo resulta de
nova observação de frames, extração de anotações ou execução científica.

## Fonte primária e acesso efetivo

Publicação: Gibbs et al., *In Situ X-Ray Observations of Dendritic Fragmentation
During Directional Solidification of a Sn-Bi Alloy*, JOM 68, 170–177 (2016),
DOI 10.1007/s11837-015-1646-7.

| Fonte | Evidência acessível | Limite |
| --- | --- | --- |
| [Página editorial Springer](https://link.springer.com/article/10.1007/s11837-015-1646-7) | Identificação bibliográfica e resumo | Preview; leitura integral não realizada |
| [Registro institucional LANL](https://laro.lanl.gov/esploro/outputs/journalArticle/In-Situ-X-Ray-Observations-of-Dendritic/9916361515603761) | Manuscrito aceito LA-UR-15-24719 vinculado ao DOI | O link PDF indexado retornou HTTP 403; o registro não substitui seu texto integral |
| Índice textual do manuscrito aceito vinculado ao registro LANL | Seção Results, página impressa 4, referência à Figura 2 | `VERIFIED_SEARCH_INDEX_TEXT`; paginação observada no texto indexado, sem inspeção visual da página |

O trecho primário acessível declara:

> “The locations of cumulative fragmentation events are circled.”

Esta é a única citação literal do manuscrito neste documento: **oito palavras**.
Ela sustenta localização cumulativa dos eventos. Não fornece um contrato de
segmentação da extensão física do fragmento. A declaração autoral que cita a
publicação é registrada como autoridade documental; não substitui evidência
ausente nem autoriza automaticamente acesso a pixels ou execução posterior.

Não foram acessados links de suplementos, vídeos ou imagens experimentais.
As tentativas de leitura textual das rotas editoriais `/figures/2` e
`/figures/6` foram indisponíveis; suas legendas integrais não foram verificadas.
Não se alega ausência absoluta de informação no artigo integral inacessível.

## Alegações e limites

| Alegação | Estado da evidência | Consequência para um contrato futuro |
| --- | --- | --- |
| Os círculos indicam localizações cumulativas de eventos | `VERIFIED_SEARCH_INDEX_TEXT` | Pode fundamentar a semântica documental de localização cumulativa |
| O círculo delimita fisicamente o fragmento | `NOT_VERIFIED` | Não usar seu interior, raio ou contorno como máscara física |
| Todas as ocorrências foram anotadas | `NOT_VERIFIED` | Não assumir exaustividade ou converter falta de anotação em negativo |
| Cada marca persiste em todos os frames posteriores | `NOT_VERIFIED` | Cumulatividade textual não certifica persistência operacional frame a frame |
| Primeira aparição da marca coincide com onset físico | `NOT_VERIFIED` | Separar primeira observação, primeira anotação e instante físico |
| Latência de anotação e regra de associação temporal | `NOT_VERIFIED` | Exigir definição explícita antes de atribuir instante e identidade de evento |
| Tratamento de sobreposição, ambiguidade e casos incompletos | `NOT_VERIFIED` | Não resolver por conveniência do classificador |
| Legenda integral da Figura 2 | `NOT_VERIFIED` | A frase citada está no trecho de Results, não foi apresentada como legenda |

As consequências da última coluna são limites de inferência desta auditoria,
não afirmações adicionais atribuídas aos autores da publicação.

## Coerência com a documentação existente do projeto

Os registros abaixo já integravam a base documental da fase TI3-A; não são
resultados de uma nova leitura de conteúdo experimental.

| Registro do projeto | Informação documental | Alcance |
| --- | --- | --- |
| [Manifesto de fontes](../../../configs/sources/source_manifest.json) | ESM1/4: radiografias; ESM2/5: campo solutal relativo; ESM3/6: anotações cumulativas de localização | Descreve papéis das modalidades; não certifica targets ML nem concentração absoluta de Bi |
| [Contrato ANN-201](../../../docs/protocols/TI2_CONTRACT_MATRIX.md) | A anotação circular não equivale a máscara de fragmento | Impede promover a geometria gráfica a extensão física sem evidência independente |
| [Relatório histórico TI3-A](../TI3_A/execution-report.md) | Target, split e FINAL_TEST não definidos na parada anterior | Preserva o bloqueio anterior; esta auditoria não o reescreve como execução bem-sucedida |

Nenhum evento, label, negativo, amostra, distribuição ou split foi materializado
por esta auditoria. Validação científica de qualquer contrato proposto e
viabilidade empírica do split permanecem pendentes das condições e decisões
da fase correspondente. Este documento não declara resultado de ML nem abre
FINAL_TEST, treinamento ou nova execução científica.

## Proveniência operacional

A coleta anterior usou dez chamadas da ferramenta web: quinze consultas de
busca, seis aberturas de páginas e dois cliques textuais. Resultados secundários
apareceram nas buscas, mas não fundamentam as alegações acima. O inventário
detalhado de consultas e falhas foi entregue ao agente responsável pelo journal.

Houve uma busca textual local, com código de saída 0:

```text
rg -n -i 'LA-UR-15-24719|cumulative fragmentation|s11837-015-1646-7|Gibbs' docs artifacts/metadata configs/sources README.md
```

A redação deste documento reutilizou somente a evidência já coletada. Não houve
nova busca web, abertura de frames, download local, cálculo científico ou
alteração de outros arquivos por este agente.
