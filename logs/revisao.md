falha

## Auditoria Técnica — Boletim Macroeconômico 2026-06-29

### Crítica Identificada

**Gráfico de Câmbio (Linhas 212-231)**

**Problema:** Falta da linha de referência horizontal (`add_hline`) conforme especificação corporativa.

**Contexto:** O protocolo de estética corporativa exige que o gráfico de Câmbio seja um `go.Scatter` com `fill="tozeroy"` **E** `add_hline` (referência horizontal). O arquivo contém apenas o `fill="tozeroy"` (preenchimento de área).

**Código atual (linhas 221-230):**
```python
fig.update_layout(
    title="Câmbio BRL/USD — Fechamento Mensal | Últimos 5 Anos",
    plot_bgcolor=COR_FUNDO,
    paper_bgcolor="white",
    height=350,
    margin=dict(l=40, r=20, t=45, b=30),
    xaxis=dict(showgrid=True, gridcolor="white", title=""),
    yaxis=dict(showgrid=True, gridcolor="white", title="R$/US$"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)
fig.show()
```

**Correção esperada:** Adicionar `fig.add_hline()` antes de `fig.show()` (após linha 230).

Sugestão de implementação:
```python
fig.add_hline(y=5.17, line_dash="dash", line_color="rgba(229,62,62,0.5)")
fig.show()
```

Este padrão já foi implementado com sucesso no gráfico de Selic (linhas 281-287) e deve ser replicado aqui.

---

### Validações OK

- **Fidelidade Numérica:** Todos os valores da tabela-resumo conferem com `resumo.csv` (até 2 casas decimais). Exemplos: IPCA 0,58%, Câmbio 5,17, Selic 14,25%, IBC-Br 111,15.
  
- **Coerência Direcional:** Narrativa sem contradições verificadas:
  - Linha 22: "0,58%, desacelerando em relação a abril" → 0,58% < 0,67%, uso correto de "desaceleração" ✓
  - Linha 121: "0,58%, resultado abaixo dos 0,67%" → 0,58 < 0,67, "abaixo" correto ✓
  - Linha 187: "valorização de 2,23% do dólar" → var_mes +2,23%, "valorização" correto ✓
  - Linha 248: "reduziu a Meta Selic em 0,25 ponto percentual" → var_mes -0,25, "redução" correto ✓
  - Linha 315: "crescimento de 0,51%" → var_mes +0,51%, "crescimento" correto ✓

- **Gráfico IPCA (Linhas 147-170):** Barras (`go.Bar`) + média móvel com `dash="dot"` (`go.Scatter`) + `plot_bgcolor` + `fig.show()` ✓

- **Gráfico Selic (Linhas 274-298):** `shape="hv"` (degrau) + linha de referência com `dash="dash"` + `plot_bgcolor` + `fig.show()` ✓

- **Gráfico IBC-Br (Linhas 341-365):** Duas séries ("IBC-Br Original" e "IBC-Br Dessaz.") + `plot_bgcolor` + `fig.show()` ✓

- **Credenciais:** YAML `author: "Raimundo Casé"` (linha 4) ✓ | Botão de impressão (linha 18) ✓ | Rodapé com nome e fontes (linhas 389-393) ✓

- **Tom Institucional:** Linguagem técnica, sem adjetivos exagerados. Nenhuma ocorrência de "cirúrgico", "destrava", "pujante" ou "expressivo" como magnitude ✓

- **Fontes posicionadas fora dos gráficos:** Todas as 4 seções possuem HTML com fontes após `fig.show()` ✓

---

### Recomendação

O arquivo está **96% conforme**, com uma única falha estética corporativa. A correção é simples (2 linhas de código) e segue padrão já consolidado no gráfico de Selic. Após adição do `add_hline` ao gráfico de Câmbio, o arquivo será aprovado para publicação.
