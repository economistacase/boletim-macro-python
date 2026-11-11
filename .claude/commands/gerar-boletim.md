---
description: Orquestra toda a pipeline do Boletim Macro em Python para a data informada.
---
Coordene a geração do Boletim Macro Semanal. A data de referência é `$ARGUMENTS` (use a data atual do sistema se o argumento vier vazio).

## Sequência de Execução
1. Execute `python python/coleta.py` diretamente via Bash (não existe subagente para esta etapa — coleta.py é um script fixo e determinístico). Aguarde a confirmação de que os 5 arquivos brutos estão em `output/dados/`.
2. Execute `python python/cambio_pares.py` via Bash. Ele grava `output/tabelas/contexto_cambio.md` com a decomposição da variação do real entre dólar global e resíduo. **Se falhar** (a API PTAX do BCB pode estar indisponível), execute `python python/registrar_erro.py "cambio_pares" "<erro>"` e **siga a pipeline normalmente**: é um enriquecimento da análise de câmbio, não um pré-requisito. O boletim sai sem a decomposição, e a falha fica registrada em `erros.md` e no log do run. Não tente contornar nem editar o script.
3. Chame o subagente `analista_quant`. Aguarde a confirmação de que `resumo.csv`, `historico.csv` e `contexto.md` foram gerados.
4. Chame o subagente `redator_relatorio` passando a data `$ARGUMENTS`. Ele deve gerar o `boletim_<DATA>.qmd`.
5. Chame o subagente `revisor_tecnico`. Leia a primeira linha de `logs/revisao.md`: ela trará `ok`, `falha_dados` ou `falha_estilo`. O significado de cada veredito e a classificação das falhas estão definidos em `.claude/agents/revisor_tecnico.md` — não mantenha critério próprio aqui.
6. Ponto de Decisão:
   - `ok` → chame o `publicador` para renderizar o HTML e gerar o PDF.
   - `falha_dados` ou `falha_estilo` → devolva o trabalho ao `redator_relatorio` com as críticas do revisor e repita o ciclo a partir do passo 5. **Limite de 2 rodadas de revisão.**
7. Esgotadas as 2 rodadas sem `ok` (regra de desempate — esta pipeline roda sem supervisão):
   - Se o veredito final for `falha_estilo`, **publique**: chame o `publicador` normalmente. As falhas remanescentes já estão registradas em `logs/revisao.md`, que é commitado junto com o boletim, e devem ser repetidas no sumário final como ressalvas. Um boletim publicado com uma frase imprecisa serve mais que nenhum boletim.
   - Se o veredito final for `falha_dados`, **não publique**. Execute `python python/registrar_erro.py "revisor_tecnico" "Veredito falha_dados após 2 rodadas: <resumo das falhas bloqueantes>"` e encerre relatando o bloqueio. A ausência do HTML/PDF faz o workflow falhar e abrir uma issue, que é o comportamento desejado para erro de dado.
8. Finalização: Apresente um sumário dizendo qual foi o HTML gerado, as ressalvas remanescentes (se houver) e exiba uma mensagem de conclusão.

## Proibição de Esperar Decisão Humana
Esta pipeline é executada por `claude -p` no GitHub Actions, sem ninguém para
responder. **Nunca** encerre o turno pedindo autorização, confirmação ou escolha
entre alternativas — isso equivale a um travamento: nenhum produto é gerado e o
boletim da semana é perdido. Toda bifurcação já está decidida acima; em qualquer
situação não prevista, escolha a opção que entrega o boletim e registre a ressalva
no sumário. A única parada legítima sem produto é o `falha_dados` do passo 7 e a
falha de script da regra de segurança abaixo — e ambas exigem
`registrar_erro.py` antes de encerrar.

## Regra de Segurança (PROIBIÇÃO ABSOLUTA DE EDITAR CÓDIGO)
`coleta.py`, `analise.py` e `gerar_pdf.py` são scripts fixos, já testados — NUNCA os edite, reescreva ou "corrija" em tempo de execução, mesmo que o erro pareça trivial (isso já causou regressões graves de metodologia e dados no passado). Se qualquer script falhar:
1. Execute `python python/registrar_erro.py "<etapa>" "<descrição do erro, com traceback>"`.
2. Pare a operação e reporte ao usuário exatamente o que falhou e em qual comando — não tente contornar com patches.