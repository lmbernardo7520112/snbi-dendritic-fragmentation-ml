# TI3-A0 — contrato de target bloqueado após exame finito

**TI3_A0=BLOCKED_TARGET_CONTRACT.** A localização cumulativa está documentada,
mas o protótipo não certificou extração completa ou persistência global.
Tolerância do target, supervisão de casos UNKNOWN e separação temporal/exposição
também permanecem pendentes. A condição para novos frames não foi satisfeita.
Não houve ML, dataset, split ou abertura de FINAL_TEST.

## Preservação e autoridade

O único commit desta tarefa, `1e7f5e8b382e84fd1259637722ce9774ffed7df3`,
preservou os seis textos de TI3-A com a mensagem
`docs(ti3): record target-contract precondition block`.
Seu parent é a baseline `67786bd4e23406e7f19860a53fe237e6d7b648cb`.
Branch: `feat/ti3-canonical-dataset-baseline`. A decisão nova está em
[authorization.md](authorization.md); nenhum poder histórico foi reativado.

Os artefatos A0 e quatro arquivos novos de código/testes ficam locais,
não staged e sem commit adicional. Não houve push, PR, Ready, merge, exclusão
de branch, instalação, alteração do sistema, acesso a credenciais ou bypass.
A autorização encerra com este resultado. A presença de `results.json`
bloqueia o preflight de qualquer nova passagem do protótipo.

## Vinte pontos do retorno autoral

1. **Checkpoint anterior:** SHA completo acima; seis textos TI3-A preservados
   sem alteração retroativa.
2. **Evidência primária:** Gibbs et al., DOI
   [10.1007/s11837-015-1646-7](https://link.springer.com/article/10.1007/s11837-015-1646-7).
   O trecho do manuscrito aceito indexado pelo
   [registro LANL](https://laro.lanl.gov/esploro/outputs/journalArticle/In-Situ-X-Ray-Observations-of-Dendritic/9916361515603761)
   documenta localizações cumulativas circundadas. Verificação limitada a
   `VERIFIED_SEARCH_INDEX_TEXT`; o PDF retornou HTTP 403 e não foi lido
   integralmente. Completude, negativos e onset exato não foram comprovados.
3. **Arquivos efetivamente abertos:** ESM3:0/73/146/219/293 e
   ESM6:0/98/197/295/394, somente os dez buffers nativos já expostos.
   [development-manifest.json](development-manifest.json) identifica caminhos,
   hashes, tempos e exclusão permanente de FINAL_TEST.
4. **I/O nativo:** duas passagens previamente declaradas, uma de caracterização
   e outra de extração; dez opens e 19.545.600 bytes em cada uma.
   Total: **20 opens, 39.091.200 bytes, dez arquivos distintos**, cada um
   autenticado nas duas leituras. ESM3: 1.966.080 bytes/buffer; ESM6:
   1.943.040. As dez PNGs derivadas tiveram uma gravação, uma leitura para
   hash e uma chamada view_image por arquivo; bytes e opens internos da
   ferramenta não foram instrumentados e não integram o total nativo.
5. **Representação:** anéis vermelhos sobre imagem radiográfica visível no
   interior. U≈90/V≈240 nos traços fortes, cinza próximo de 128/128;
   exibição BT.601 ilustrativa, análise em chroma nativa. Nos candidatos
   aceitos: raio gráfico 10,607489–10,846570 px e espessura radial P05–P95
   6,891819–7,047511 px. Não são medidas do fragmento.
6. **Método:** limiar fixo de chroma 20, componentes com conectividade 8,
   topologia e ajuste algébrico de círculo. Parâmetros congelados antes da
   única extração; nenhum ajuste após resultados ou segunda execução.
7. **Currículo:** thresholding e análise binária/componentes foram pertinentes.
   Contornos e Hough foram deliberados; não executados como métodos adicionais.
   Hough/Canny não foram impostos ao futuro input ML. Sobel→NGF e
   descritores locais→SS8 foram preservados sem executar ou editar G2.
8. **Extração:** 491 componentes, 108 círculos aceitos geometricamente,
   380 ambíguos e três pequenos. Incluem repetições entre frames, não eventos
   independentes ou targets ML validados. Sete dos nove anéis visualmente
   isolados de ESM6:98 falharam somente pelo limite radial de 4 px
   (aproximadamente 4,02–4,25 px); essa limitação do protótipo foi preservada.
9. **Cumulatividade:** a documentação e a inspeção são compatíveis com
   persistência parcial. Correspondências entre centros aceitos:
   ESM3 8/9/12 e ESM6 2/10/9 nas transições não iniciais. A prova global
   permaneceu `UNRESOLVED_GRAPHICAL_AMBIGUITY` nas duas fontes.
10. **First appearance:** primeira observação amostrada é distinta de primeira
    anotação e onset físico. Ambiguidades e rejeições variáveis impedem inferir
    novos eventos de componentes sem correspondência. Onset exato:
    `NOT_VERIFIED`.
11. **Target principal candidato:** localização pontual das posições publicadas,
    `PROPOSED_NOT_FROZEN`. Não houve substituição por classificação ou máscara.
12. **Positivos:** exigem validação semântica e tolerância espacial rastreável;
    aceitação geométrica isolada não certifica positivo ML.
13. **Negativos:** ausência de círculo permanece `UNLABELED/UNKNOWN`.
    Completude e protocolo quantitativo compatível não foram demonstrados.
14. **Unidade amostral candidata:** um frame estrutural de uma aquisição/instante
    e seu conjunto de pontos; modalidades correspondentes não são réplicas
    independentes. Nenhum sample ML foi materializado.
15. **Split candidato:** blocos temporais internos TRAIN/DEV/FINAL_TEST em cada
    aquisição, sem IDs, seed ou fronteiras escolhidas. Duas aquisições não
    sustentam três partições não vazias disjuntas por aquisição.
    Frames finais cumulativos já expostos podem revelar eventos anteriores;
    reservar outros IDs não apaga essa exposição.
16. **Embargo:** valor numérico `NOT_VERIFIED`. Para suporte inclusivo
    [i−L,i+R], q−p>L+R é condição de não sobreposição direta entre blocos.
    Contexto, horizonte, histórico das anotações e dependência/evento adicionais
    precisam ser justificados; a desigualdade não garante independência.
17. **Novos acessos:** zero novos frames, nenhuma janela, ZIP/MP4,
    FFmpeg/FFprobe ou outros buffers. A fase 8 não se aplica porque
    persistência/onset não é o único obstáculo restante.
18. **ML:** zero runs técnicos e científicos, baseline, treinamento ou seleção
    de modelo. Houve 18 testes sintéticos do extrator, aprovados sem skips,
    falhas ou erros antes da extração. Eles não são ML nem validam o target.
19. **FINAL_TEST:** `NOT_DEFINED_NOT_OPENED`; os dez ativos A0 são
    `ANNOTATION_CONTRACT_DEVELOPMENT_ONLY`. Holdout SOLUTE histórico permanece
    `CONSUMED`.
20. **Próximo estado:** nenhuma atividade autorizada; TI3-A não está pronta
    para retomada. Não houve A0.1, tuning, baseline, TI3-B ou nova ciência G2.

## Evidências, verificação e limites

As tabelas por frame, ambiguidade e persistência estão em
[ANNOTATION_SEMANTICS.md](ANNOTATION_SEMANTICS.md), com registros completos
em [extraction-results.json](extraction-results.json) e
[temporal-results.json](temporal-results.json). O contrato e seus bloqueios
estão em [TARGET_CONTRACT.md](TARGET_CONTRACT.md); as condições de separação,
em [SPLIT_FEASIBILITY.md](SPLIT_FEASIBILITY.md).

[verification.json](verification.json) registra a custódia dos seis textos
TI3-A, dos 25 textos G2 congelados e dos quatro arquivos de código/testes A0.
A verificação final usa textos e histórico Git, sem reabrir buffers ou PNGs.
[io-audit.json](io-audit.json) distingue bytes nativos instrumentados de I/O
das visualizações. [commands.json](commands.json) preserva comandos,
fronteiras, resultados e limites do inventário, incluindo falhas operacionais
de leitura/auditoria e de acesso web. Não constitui monitoramento universal
de syscalls. CI A0 não foi acionada.

Não se conclui impossibilidade de registro, extração ou aprendizado com
essas fontes. O resultado encerra este método e este contrato incompleto,
sem promover autorização a evidência ou testes sintéticos a validade científica.

```text
TI3_A0=BLOCKED_TARGET_CONTRACT
TI3_A0_TARGET_CONTRACT=BLOCKED
TARGET_CONTRACT=BLOCKED
CIRCLE_IS_FRAGMENT_MASK=false
FINAL_TEST=NOT_DEFINED_NOT_OPENED
ML_RUNS=0
G2_SOLUTE=PASS
HOLDOUT_SOLUTE=CONSUMED
TI3_A_READY_TO_RESUME=false
TI3_B_AUTHORIZED=false
MERGE_AUTHORIZED=false
CURRENT_AUTHORIZED_ACTIVITY=NONE_AWAITING_AUTHOR_DECISION
```
