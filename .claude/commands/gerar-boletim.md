---
description: Orquestra toda a pipeline do Boletim Macro em Python para a data informada.
---
Coordene a geração do Boletim Macro Semanal. A data de referência é `$ARGUMENTS` (use a data atual do sistema se o argumento vier vazio).

## Sequência de Execução
1. Chame o subagente `pesquisador-dados`. Aguarde a confirmação de que os 5 arquivos brutos estão em `output/dados/`.
2. Chame o subagente `analista_quant`. Aguarde a confirmação de que `resumo.csv` e `historico.csv` foram gerados.
3. Chame o subagente `redator_relatorio` passando a data `$ARGUMENTS`. Ele deve gerar o `boletim_<DATA>.qmd`.
4. Chame o subagente `revisor_tecnico`. Leia a primeira linha do log que ele gerar.
5. Ponto de Decisão:
   - Se o log iniciar com `ok`, chame o `publicador` para renderizar o HTML.
   - Se o log iniciar com `falha`, devolva o trabalho para o `redator_relatorio` com as críticas do revisor e repita o ciclo (limite de 2 tentativas).
6. Finalização: Apresente um sumário dizendo qual foi o HTML gerado e exiba uma mensagem de conclusão.

## Regra de Segurança
Se em qualquer etapa um script de Python apresentar erro de sintaxe ou de biblioteca, tente corrigir o código (caso seja trivial) ou pare a operação e mostre o erro.