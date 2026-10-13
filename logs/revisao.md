ok

## Auditoria Técnica — Boletim Macroeconômico 2026-10-13

**Arquivo auditado:** `boletim_2026-10-13.qmd`
**Fontes de referência:** `output/tabelas/resumo.csv`, `output/tabelas/historico.csv`, `output/tabelas/contexto.md`
**Especificação:** `.claude/agents/redator_relatorio.md`

---

## Resultado

Nenhuma falha bloqueante. Todos os números, datas e direções de comparação conferem com `resumo.csv` e `contexto.md`. Os pontos abaixo são ressalvas não bloqueantes, com correção sugerida.

## 1. Fidelidade Numérica — APROVADO

- Tabela-resumo é gerada a partir do `resumo.csv` (valores: IPCA 0.82, Câmbio 5.01, Selic 13.75, IBC-Br 109.92).
- Variações: IPCA 0.82 / 3.95 / 4.58; Câmbio -3.31 / -8.96 / -6.96; Selic 0.00 / -1.25 / -1.25; IBC-Br -0.22 / 1.50 / 1.14. Todas batem com a narrativa.
- Séries do texto (IPCA mar/mai/jul/ago 2026, câmbio jun–set 2026, Selic desde 2026, IBC-Br jan–jul 2026) conferem com `historico.csv`.

## 2. Coerência Direcional — APROVADO

Comparações verificadas (valor recente − valor comparado → palavra usada):
- IPCA mensal: 0,82 − (−0,32) = +1,14 → "aceleração" ✓
- IPCA 12m: 4,58 − 4,22 = +0,36 → "alta" ✓
- IPCA 12m vs teto: 4,58 > 4,50 → "acima do teto" ✓
- IPCA set/26 vs set/25: 0,82 − 0,48 = +0,34 → "maior" ✓
- Selic: 13,75 − 14,00 = −0,25 → "corte" ✓; 13,75 − 15,00 = −1,25 → "queda" ✓
- Câmbio: −3,31% (vs set), −8,96% (no ano), −6,96% (12m) → "se valorizou" ✓
- IBC-Br mensal: 109,92 − 110,16 = −0,22 → "queda" ✓; junho −0,88 → "queda" ✓
- IBC-Br 12m (+1,14%) e no ano (+1,50%) → "crescimento" ✓
- IBC-Br nível: 109,92 < 111,14 → "1,10% abaixo do máximo" ✓
- Síntese: "supera o teto", "reverteu a deflação", "cinco cortes consecutivos" (19/03, 30/04, 18/06, 06/08, 17/09) ✓

## 3. Fonte Única dos Fatos — APROVADO

Todas as datas e níveis da Selic (incluindo o ciclo de cortes, 15,00% em 19/06/2025 a 18/03/2026, e o mínimo de 6,25% em 27/10/2021), máximos e mínimos do IPCA (12,13% e 3,16%), câmbio (6,2086 em 02/01/2025 e 4,6175 em 04/04/2022) e IBC-Br (máximo 111,14 em maio/2026 e mínimo 97,42 em jan/2022) estão em `contexto.md` ou `resumo.csv`. Não há afirmações sobre Focus, PIB, desemprego, Fed ou fiscal.

## 4. Estética Corporativa dos Gráficos — APROVADO

Conferido contra a seção 6 de `redator_relatorio.md`:
- Gráfico 1 (IPCA): barras + média móvel 3m em `COR_MEDIA` com dash="dot". Layout base completo. `fig.show()` e fonte separada. ✓
- Gráfico 2 (Câmbio): linha com `fill="tozeroy"`, sem linha de referência. ✓
- Gráfico 3 (Selic): step line `shape="hv"` e linha de referência tracejada, única com referência. ✓
- Gráfico 4 (IBC-Br): duas séries, sem referência. ✓
- Todos os gráficos têm `plot_bgcolor=COR_FUNDO`, `fig.show()` e nenhum `add_annotation`/`annotations` com texto de fonte. ✓

## 5. Credenciais, Botão e Rodapé — APROVADO

- YAML `author: "Raimundo Casé"` (linha 4) ✓
- Identidade `**Raimundo Casé - economista**` (linha 16) ✓
- Botão `<button class="print-btn" ...>` (linha 18) ✓
- Rodapé (linhas 284–289) com "Raimundo Casé - economista", fontes BCB e IBGE ✓

## 6. Tom Institucional — APROVADO

Nenhum dos termos proibidos ("cirúrgico", "destrava", "robusto", "pujante", "expressivo") foi encontrado. Não há "—" como separador de ideias no corpo do texto. Os "—" presentes estão em títulos, títulos de gráficos e fontes, que são padrões do template.

---

## Ressalvas (não bloqueantes)

1. **IBC-Br, Análise, parágrafo 1 (linha 234):** a lista "avanços de 0,55% em janeiro, 0,62% em fevereiro, 0,28% em abril e 0,21% em maio" omite março, que foi −0,13% (`contexto.md`, tabela IBC-Br). A frase não é falsa, mas deixa a trajetória incompleta. Sugestão: incluir "e recuo de 0,13% em março".
2. **Câmbio, Análise, parágrafo 2 (linha 145):** "nível atual está mais próximo da parte inferior dessa faixa do que do pico" é uma inferência derivada, não escrita em `contexto.md`. O fato é verificável (5,0096 está a 0,39 do mínimo e a 1,20 do máximo). Sugestão: acrescentar essa comparação ao `contexto.md` ou reescrever com os números.
3. **IBC-Br, Análise, parágrafo 1 (linha 234):** "Em junho, a queda já havia sido de -0,88%" usa sinal duplo (queda + negativo). Sugestão: "Em junho, a variação já havia sido de -0,88%" ou "a queda já havia sido de 0,88%".
4. **IBC-Br, Análise, parágrafo 3 (linha 238):** "coerente com a leitura de política monetária restritiva" é uma caracterização qualitativa que não consta do `contexto.md`. Está dentro do que a regra permite, mas vale confirmar.
5. **Atribuição de fonte do IBC-Br (inconsistência do template):** a tabela (linha 75) atribui o IBC-Br ao IBGE, enquanto o gráfico 4 (linha 269) e o rodapé (linha 287) atribuem ao BCB. O texto vem da especificação de `redator_relatorio.md`. Recomendo que o orquestrador unifique a atribuição na especificação.
6. **Especificação do Gráfico 3 (`redator_relatorio.md`):** o cabeçalho diz "linha de referência 'Meta Selic'", mas o código da especificação usa o nome "Valor atual: x%". O `.qmd` segue o código. Sugestão: alinhar o texto da especificação ao código.
7. **Gráfico 2 (Câmbio):** `fill="tozeroy"` aplicado a uma série em torno de 5 BRL/USD comprime visualmente as variações. O padrão está prescrito na especificação, então não é falha. Recomendo registrar a observação ao orquestrador.
