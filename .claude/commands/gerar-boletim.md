---
description: Orquestra toda a pipeline do Boletim Macro em Python para a data informada.
---
Coordene a geração do Boletim Macro Semanal. A data de referência é `$ARGUMENTS` (use a data atual do sistema se o argumento vier vazio).

## Sequência de Execução
1. Execute `python python/coleta.py` diretamente via Bash (não existe subagente para esta etapa — coleta.py é um script fixo e determinístico). Aguarde a confirmação de que os 5 arquivos brutos estão em `output/dados/`.
2. Chame o subagente `analista_quant`. Aguarde a confirmação de que `resumo.csv` e `historico.csv` foram gerados.
3. Chame o subagente `redator_relatorio` passando a data `$ARGUMENTS`. Ele deve gerar o `boletim_<DATA>.qmd`.
4. Chame o subagente `revisor_tecnico`. Leia a primeira linha do log que ele gerar.
5. Ponto de Decisão:
   - Se o log iniciar com `ok`, chame o `publicador` para renderizar o HTML e gerar o PDF.
   - Se o log iniciar com `falha`, devolva o trabalho para o `redator_relatorio` com as críticas do revisor e repita o ciclo (limite de 2 tentativas).
6. Finalização: Apresente um sumário dizendo qual foi o HTML gerado e exiba uma mensagem de conclusão.

## Regra de Segurança (PROIBIÇÃO ABSOLUTA DE EDITAR CÓDIGO)
`coleta.py`, `analise.py` e `gerar_pdf.py` são scripts fixos, já testados — NUNCA os edite, reescreva ou "corrija" em tempo de execução, mesmo que o erro pareça trivial (isso já causou regressões graves de metodologia e dados no passado). Se qualquer script falhar:
1. Execute `python python/registrar_erro.py "<etapa>" "<descrição do erro, com traceback>"`.
2. Pare a operação e reporte ao usuário exatamente o que falhou e em qual comando — não tente contornar com patches.