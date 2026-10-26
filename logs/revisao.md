ok

# Revisão técnica — boletim_2026-10-26.qmd (referência 2026-10-26)

Referências usadas: `output/tabelas/resumo.csv`, `output/tabelas/historico.csv`, `output/tabelas/contexto.md` e `.claude/agents/redator_relatorio.md` (seção 6 e regras de fonte única, coerência direcional e sinal).

## Itens verificados sem divergência

- **Tabela-resumo:** gerada em tempo de render a partir do `resumo.csv` (IPCA 0.82 / 4.58 em 12m; Câmbio 5.50; Selic 13.75; IBC-Br 110.41). Valores com no máximo 2 casas, cores por sinal, rodapé de fontes correto (IBC-Br atribuído ao BCB).
- **Coerência direcional:** todas as comparações conferem.
  - IPCA: 0,82 - (-0,32) = +1,14 com "aceleração"; 4,58 - 4,22 = +0,36 com "alta"; 4,58 > 4,50 com "acima do teto"; 0,82 - 0,48 = +0,34 com "maior".
  - Câmbio: 5,5007 > 5,1809 com "se desvalorizou" (6,17%); 5,5007 > 5,3843 com "se desvalorizou" (2,16%); 5,5007 < 5,5024 com "se valorizou" (-0,03%).
  - Selic: 13,75 - 15,00 = -1,25 com "queda"; 13,75 - 14,00 = -0,25 com corte.
  - IBC-Br: 110,41 - 110,03 > 0 com "alta" (0,34%); 110,41 abaixo de 111,25 com "0,76% abaixo do máximo"; 1,21% e 1,55% com "crescimento" (série original).
  - Não há sinal duplo ("queda de -x" ou "alta de +x").
- **Fatos numéricos:** IPCA (mensal, 12m, máx./mín. de 5 anos, meta 3,00% com tolerância de 1,5 p.p., teto 4,50%), Câmbio (fechamentos de 26/10, 30/09, 31/10/2025, 31/12/2025; PTAX diária máx. 6,2086 e mín. 4,6175; mensais abr-set/2026 entre 4,9886 e 5,1816), Selic (vigência 17/09/2026, 15,00% desde 19/06/2025 até 18/03/2026, cinco cortes com datas e níveis, mín. 6,25% em 27/10/2021) e IBC-Br (110,41; 110,03; máx. 111,25 em maio/2026; mín. 97,42 em janeiro/2022; variações mensais dessazonalizadas de maio a agosto) conferem com `contexto.md` e `historico.csv`.
- **Metodologia do IBC-Br:** variações no ano e em 12 meses atribuídas à série original, conforme nota do `contexto.md`.
- **Termos de fonte:** nenhuma menção a Focus, PIB, desemprego, Fed, fiscal ou outros dados externos. Não há rótulos de política ("restritiva", "expansionista", "neutra") nem posicionamento em faixas.
- **Gráficos:** os quatro seguem a seção 6 do `redator_relatorio.md`. IPCA com barras e média móvel 3m; Câmbio com área e sem linha de referência; Selic em step line com linha de referência; IBC-Br com duas séries e sem referência. Todos têm `plot_bgcolor`, `fig.show()` e parágrafo de fonte separado após o gráfico. Não há `add_annotation` nem `update_layout(annotations=...)`.
- **Credenciais:** `author: "Raimundo Casé"` (YAML); botão `print-btn` presente (linha 18); rodapé com "Raimundo Casé - economista" e fontes BCB e IBGE ao final.
- **Tom:** sem "cirúrgico", "destrava", "robusto", "pujante" ou "expressivo". Sem "—" como separador de ideias no corpo do texto. O uso em títulos, gráficos e rodapé segue a especificação.
- **Estrutura:** quatro seções H2, cada uma com `### Análise` de três parágrafos, `### Gráfico` e bloco `bloco-analise`. Síntese com quatro eixos em negrito.

## Ressalvas (não bloqueiam publicação)

R1. Síntese, eixo "Política monetária em calibragem", e Selic, parágrafo 2 ("calibragem gradual" em "O ritmo de cortes de 0,25 p.p. por reunião mostra uma calibragem gradual"): "gradual" é adjetivo qualitativo sobre a política, sem palavra correspondente no `contexto.md`. Não é rótulo de postura ("restritiva" ou "expansionista"), então não é falha. Recomenda-se remover o adjetivo e manter o fato ("cinco cortes consecutivos de 0,25 p.p."), que já está no texto.

R2. Síntese, eixo "O equilíbrio entre desinflação e atividade": o termo "desinflação" aparece no mesmo bloco em que se afirma "Inflação em reaceleração". Não é número nem direção comparada, então não é falha, mas é incoerente com o diagnóstico. Sugestão: "entre o controle da inflação e a atividade".

R3. Caracterização da atividade: o Panorama fala em "atividade em alta moderada" e a Síntese em "atividade em expansão" e "crescimento moderado". A análise do IBC-Br descreve "oscilação em torno de um patamar estável". Os dados sustentam as duas leituras (alta mensal de 0,34% e crescimento de 1,21% em 12m, de um lado, e variações mensais alternadas de maio a agosto, do outro). Sugere-se padronizar a caracterização nos três trechos.

R4. Câmbio, parágrafo 1: "a variação é de -0,03%, e o real se valorizou no ano". A palavra de direção e o sinal aparecem na mesma frase, mas não há sinal duplo ("queda de -x"). Pela regra de sinal, o número poderia ir sem sinal ("a variação é de 0,03%"). Sem impacto factual.

R5. Câmbio, parágrafo 2: "o movimento do mês foi atípico no recorte recente" é julgamento qualitativo derivado da faixa de fechamentos de abril a setembro (4,9886 a 5,1816) frente a 5,5007. Os números sustentam a leitura, mas o adjetivo "atípico" não consta do `contexto.md`.

R6. Tabela-resumo: o câmbio aparece como 5.50 (CSV, 2 casas) e o texto cita 5,5007 (`contexto.md`). Não é divergência, pois a tabela segue o CSV. O leitor, porém, verá duas precisões para o mesmo valor.

R7. Gráfico de câmbio: o título diz "Fechamento Mensal", mas os extremos de 5 anos citados no texto são diários (máx. 02/01/2025, mín. 04/04/2022). O gráfico plota a série de `historico.csv`, que é mensal. Não há contradição com o texto, mas o título deve refletir o que é plotado.

R8. Gráfico Selic: a legenda da linha de referência segue o código da especificação ("Valor atual: 13.75%" no formato da seção 6). A descrição textual da seção 6 fala em "Meta Selic". A especificação é ambígua nesse ponto. Reportado ao orquestrador, sem ação no `.qmd`.
