ok

# Parecer de Revisão Técnica — Boletim Macroeconômico 2026-06-04

**Arquivo auditado:** `boletim_2026-06-04.qmd`
**Fonte de dados:** `output/tabelas/resumo.csv`
**Data do parecer:** 2026-06-04

---

## 1. Fidelidade Numérica

### Valores do CSV (referência)

| Indicador | valor_atual               | var_mes | var_ano | var_12m |
|-----------|--------------------------|---------|---------|---------|
| IPCA      | 0.67                     | 0.67    | 2.6     | 4.39    |
| Cambio    | 5.0415                   | -0.3    | -8.38   | -7.62   |
| Selic     | 14.400136155785216       | 0.0     | -0.5    | -0.25   |
| IBC-Br    | 110.24204                | -0.67   | 1.41    | 3.07    |

### Tabela HTML (codigo Python — funcao fmt_valor_atual)

- IPCA: f"{v}%" exibe 0.67%. Exato. CONFORME.
- Cambio: f"R$ {v}" exibe R$ 5.0415. Exato. CONFORME.
- Selic: f"{v:.6f}% a.a." exibe 14.400136% a.a. (6 casas decimais, cobrindo os primeiros 8 digitos significativos). CONFORME.
- IBC-Br: f"{v}" exibe 110.24204. Exato. CONFORME.
- Variacoes (var_mes, var_ano, var_12m): formatadas com {:+.2f}% — arredondamento a 2 casas permitido. CONFORME.

### Narrativa textual

- Linha 22: Selic 14,40% (arredondado de 14.400136) — permitido. CONFORME.
- Linha 22: IBC-Br 110,24 (arredondado de 110.24204) — permitido. CONFORME.
- Linha 22: Cambio 5,0415 — exato. CONFORME.
- Linha 195: Cambio 5,0415, var_ano -8,38%, var_12m -7,62% — exatos. CONFORME.
- Linha 195: var_mes -0,30% (CSV: -0.3) — arredondamento permitido. CONFORME.
- Linha 258: Selic var_ano -0,50 pp (CSV: -0.5), var_12m -0,25 pp (CSV: -0.25) — corretos. CONFORME.
- Linha 319: IBC-Br 110,24, var_mes -0,67%, var_ano 1,41%, var_12m 3,07% — corretos. CONFORME.

**Resultado: APROVADO**

---

## 2. Estetica Corporativa dos Graficos

### IPCA (linhas 161-184)
- go.Bar presente. CONFORME.
- go.Scatter com dash="dot" (media movel sobreposta) presente. CONFORME.
- plot_bgcolor definido (COR_FUNDO). CONFORME.
- fig.show() presente. CONFORME.

### Cambio (linhas 221-247)
- go.Scatter com fill="tozeroy" presente. CONFORME.
- add_hline presente. CONFORME.
- plot_bgcolor definido. CONFORME.
- fig.show() presente. CONFORME.

### Selic (linhas 284-308)
- go.Scatter com line=dict(shape="hv") (degrau) presente. CONFORME.
- add_hline presente. CONFORME.
- plot_bgcolor definido. CONFORME.
- fig.show() presente. CONFORME.

### IBC-Br (linhas 341-377)
- Duas series presentes: dados filtrados por "IBC-Br (original)" e "IBC-Br (dessaz.)" no historico.csv; exibidas como "IBC-Br Original" e "IBC-Br Dessaz." na legenda. CONFORME.
- add_hline presente. CONFORME.
- plot_bgcolor definido. CONFORME.
- fig.show() presente. CONFORME.

**Resultado: APROVADO**

---

## 3. Credenciais, Botao e Rodape

- YAML author (linha 4): "Raimundo Case". CONFORME.
- Botao print (linha 18): <button class="print-btn" onclick="window.print()">. CONFORME.
- Rodape com nome (linha 397): "Raimundo Case - economista". CONFORME.
- Fontes BCB e IBGE no rodape (linha 397): presentes explicitamente. CONFORME.

**Resultado: APROVADO**

---

## 4. Tom Institucional

Adjetivos vedados ("cirurgico", "destrava", "pujante", "expressivo" como magnitude) ausentes. Linguagem tecnica e objetiva em todo o documento. CONFORME.

**Resultado: APROVADO**

---

## Conclusao Geral

Todos os quatro itens de auditoria foram aprovados. O boletim esta em conformidade com os padroes de fidelidade numerica, estetica de graficos, credenciais institucionais e tom editorial.
