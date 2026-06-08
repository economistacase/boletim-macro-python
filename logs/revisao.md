ok

# Parecer de Revisão Técnica — Boletim Macroeconômico 2026-06-08

**Arquivo auditado:** `boletim_2026-06-08.qmd`
**Fonte de dados:** `output/tabelas/resumo.csv`
**Data do parecer:** 2026-06-08

---

## 1. Fidelidade Numérica

### Valores do CSV (referência)

| Indicador | valor_atual | var_mes | var_ano | var_12m |
|-----------|-------------|---------|---------|---------|
| IPCA      | 0.67        | 0.67    | 2.60    | 4.39    |
| Cambio    | 5.12        | 1.33    | -6.87   | -6.10   |
| Selic     | 14.50       | 0.00    | -0.50   | -0.25   |
| IBC-Br    | 110.24      | -0.67   | 1.41    | 3.07    |

### Tabela HTML (código Python — formatação)

- IPCA: "{valor_atual}" exibe 0.67%. Exato. CONFORME.
- Cambio: "{valor_atual}" exibe 5.12. Exato. CONFORME.
- Selic: "{valor_atual}" exibe 14.50. Exato. CONFORME.
- IBC-Br: "{valor_atual}" exibe 110.24. Exato. CONFORME.
- Variações (var_mes, var_ano, var_12m): formatadas com "{:+.2f}%" — arredondamento a 2 casas decimais permitido. CONFORME.

### Narrativa textual

- Linha 22 (Panorama Geral): IPCA "0,67%", acumulado "2,60%", 12m "4,39%", Câmbio "5,12", "1,33%", "-6,87%", "-6,10%", Selic "14,50%", IBC-Br "0,67%" — todos exatos. CONFORME.
- Linha 120 (IPCA): "0,67% em abril", "2,60%", "4,39%" — exatos. CONFORME.
- Linha 187 (Câmbio): "5,12", "1,33%", "6,87%", "6,10%" — exatos. CONFORME.
- Linha 260 (Selic): "14,50%", "0,50 ponto percentual", "-0,25 ponto percentual" — exatos. CONFORME.
- Linha 331 (IBC-Br): "110,24", "0,67%", "1,41%", "3,07%" — exatos. CONFORME.

**Resultado: APROVADO**

---

## 2. Estética Corporativa dos Gráficos

### IPCA (linhas 128-171)
- `go.Bar` presente (linha 147). CONFORME.
- `go.Scatter` com `dash="dot"` para média móvel sobreposta (linha 158). CONFORME.
- `plot_bgcolor=COR_FUNDO` definido (linha 162). CONFORME.
- `fig.show()` presente (linha 170). CONFORME.

### Câmbio (linhas 195-244)
- `go.Scatter` com `fill="tozeroy"` (linha 221). CONFORME.
- `add_hline` presente (linhas 224-231). CONFORME.
- `plot_bgcolor=COR_FUNDO` definido (linha 235). CONFORME.
- `fig.show()` presente (linha 243). CONFORME.

### Selic (linhas 268-315)
- `go.Scatter` com `shape="hv"` (degrau, linha 293). CONFORME.
- `add_hline` presente (linhas 295-302). CONFORME.
- `plot_bgcolor=COR_FUNDO` definido (linha 306). CONFORME.
- `fig.show()` presente (linha 314). CONFORME.

### IBC-Br (linhas 339-384)
- Duas séries presentes: "IBC-Br (original)" (linha 362) e "IBC-Br (dessaz.)" (linha 369). CONFORME.
- Ambas como `go.Scatter` com cores diferenciadas. CONFORME.
- `plot_bgcolor=COR_FUNDO` definido (linha 375). CONFORME.
- `fig.show()` presente (linha 383). CONFORME.

**Resultado: APROVADO**

---

## 3. Credenciais, Botão e Rodapé

- YAML `author` (linha 4): "Raimundo Casé". CONFORME.
- Botão print (linha 18): `<button class="print-btn" onclick="window.print()">Imprimir / Salvar PDF</button>`. CONFORME.
- Rodapé com nome (linha 408): "Raimundo Casé - economista". CONFORME.
- Fontes BCB e IBGE no rodapé (linha 409): presentes explicitamente. CONFORME.

**Resultado: APROVADO**

---

## 4. Tom Institucional

Verificação de adjetivos proibidos ("cirúrgico", "destrava", "pujante", "expressivo" como magnitude): ausentes em toda a narrativa. Linguagem técnica e objetiva mantida. CONFORME.

**Resultado: APROVADO**

---

## Conclusão Geral

Todos os quatro itens obrigatórios de auditoria foram aprovados:
1. Fidelidade numérica: valores do CSV correspondem exatamente à tabela HTML e narrativa textual.
2. Estética corporativa: todos os 4 gráficos seguem os padrões especificados (IPCA com barras+média móvel, Câmbio com fill+hline, Selic com shape=hv+hline, IBC-Br com duas séries).
3. Credenciais: author, botão print e rodapé com fontes presentes e corretos.
4. Tom institucional: linguagem objetiva e sem adjetivos exagerados.

O boletim está em conformidade integral com os padrões de qualidade técnica.
