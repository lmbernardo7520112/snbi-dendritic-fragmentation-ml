# Aprovação do LB0-STATIC e autorização do diagnóstico local read-only

- **Responsável:** Leonardo Maximino Bernardo
- **Data:** 17 de setembro de 2026
- **Repositório:** `lmbernardo7520112/snbi-dendritic-fragmentation-ml`
- **Baseline da `main`:** `e511249`
- **Natureza:** decisão de governança com escopo documental e diagnóstico
  read-only limitado

## Decisões do autor

O autor:

1. confirmou, por inspeção humana, que não foram colocados no clone local
   vídeos, arquivos ZIP experimentais, frames, imagens experimentais ou
   datasets científicos;
2. aprovou formalmente `LB0-STATIC`;
3. registrou `LB0-LOCAL-ACCEPTANCE = PARTIAL` porque os preflights manuais
   passaram, mas o sandbox real do Codex permaneceu bloqueado;
4. autorizou tornar o PR #4 pronto para revisão e autorizou seu merge na
   `main`, concluído pelo commit `e511249`;
5. preservou `CODEX_LOCAL_WRITE = BLOCKED` e
   `TI2_EXECUTION_AUTHORIZED=false`;
6. autorizou exclusivamente a reconciliação documental do LB0, a criação de
   um protocolo determinístico de diagnóstico read-only, a coleta manual pelo
   próprio autor e a abertura de um Draft PR para revisão;
7. não autorizou o merge do novo PR sem decisão expressa posterior.

## Evidência consolidada

| Evidência | Resultado |
|---|---|
| branch/commit local revisado | `chore/local-vscode-bootstrap` / `d29dfe2` |
| Git status antes dos preflights | limpo |
| checkout standalone | `STANDALONE_OK` |
| tracked-repository data guard | `PASS`; 85 entradas; zero bytes de conteúdo lidos; zero violações |
| governed local bootstrap | `PASS`; TI-2 falsa; escrita bloqueada |
| local environment diagnostic | `COLLECTED`; zero mutações; sem rede; probe não executada |
| confirmação humana de sanitização | `CONFIRMED_BY_AUTHOR` |
| sandbox real do Codex | `BLOCKED` |
| assinatura da falha | `bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted` |
| fallback ou elevação | não ocorreu |
| PR #4 | merged em `main` como `e511249` |

O primeiro relato documental do Codex permaneceu `NOT_VERIFIED` porque o prompt
proibia comandos e aquela sessão não dispunha de leitura textual independente
do shell. Esse comportamento foi fail-closed e não invalida as evidências
manuais, a CI ou a decisão posterior do autor.

## Escopo autorizado nesta etapa

- atualizar o gate LB0 com os estados formais acima;
- atualizar a postura documental do sandbox com a falha exata;
- criar o protocolo manual de diagnóstico read-only;
- registrar resultados sanitizados na mesma branch documental;
- abrir um Draft PR para revisão do autor.

O operador humano poderá executar somente os comandos read-only expressamente
listados no protocolo. O Codex local não poderá executar comandos nem escrever.

## Entregáveis autorizados

1. atualização de `docs/gates/LOCAL_BOOTSTRAP.md`;
2. atualização da postura em `docs/security/LOCAL_SANDBOX.md`;
3. este registro formal de decisão;
4. protocolo determinístico read-only;
5. registro sanitizado das evidências;
6. Draft PR, sem autorização de merge.

## Proibições preservadas

- execução de comandos ou escrita pelo Codex local;
- full access, danger-full-access, `--yolo` ou fallback fora do sandbox;
- `sudo`, `su`, `doas`, instalação ou reinstalação de pacotes;
- alterações de AppArmor, `sysctl`, namespaces, serviços, kernel ou editor;
- acesso a credenciais, tokens, autenticação ou dados experimentais;
- extração de frames, acesso a pixels, registro, calibração, labels, dataset,
  baseline, treinamento ou avaliação;
- execução da TI-2 ou das fases TI-3 a TI-8;
- merge do Draft PR sem nova autorização expressa.

Qualquer necessidade de privilégio, modificação do host ou ampliação de escopo
interrompe o diagnóstico com resultado `BLOCKED` e exige nova deliberação.

## Critério de conclusão

A etapa documental termina quando os estados estiverem reconciliados, o
protocolo estiver limitado a comandos read-only, os resultados conhecidos
estiverem sanitizados, a CI estiver disponível para revisão e o Draft PR tiver
sido aberto. `CODEX_LOCAL_WRITE = BLOCKED` e
`TI2_EXECUTION_AUTHORIZED=false` permanecem invariantes.
