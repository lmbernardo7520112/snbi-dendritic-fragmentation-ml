# Aprovação do plano TI-2 e autorização do bootstrap local

- **Responsável:** Leonardo Maximino Bernardo
- **Data:** 17 de setembro de 2026
- **Repositório:** `lmbernardo7520112/snbi-dendritic-fragmentation-ml`

## Decisões

O autor:

1. aprovou o plano executivo da TI-2 — Registro e Calibração;
2. autorizou o merge do PR #3 na `main`;
3. não autorizou a execução da TI-2;
4. autorizou exclusivamente o bootstrap governado do ambiente local VS Code.

## Escopo autorizado do bootstrap

- diagnóstico read-only do sandbox;
- criação de `AGENTS.md`;
- configurações do editor;
- guardrails de dados;
- testes exclusivamente sintéticos;
- documentação e evidências do bootstrap.

## Proibições preservadas

- alterações no sistema operacional;
- extração ou decodificação de frames;
- acesso ou processamento de pixels experimentais;
- registro ou calibração material;
- criação de labels, ledger, dataset ou splits;
- baseline, CNN, treinamento ou avaliação;
- execução das fases TI-2 a TI-8.

Qualquer correção de kernel, AppArmor, namespaces, `bubblewrap` ou configuração global do sistema exige autorização separada. O merge do planejamento não libera execução científica.
