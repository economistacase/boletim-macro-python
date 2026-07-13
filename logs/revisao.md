ok

## Auditoria Técnica — boletim_2026-07-13.qmd

Data da auditoria: 2026-07-13
Revisor: Sistema Automatizado

### Resultado Geral
Nenhuma falha detectada. Documento aprovado para publicação.

### Fidelidade Numérica
✓ Todos os 16 valores (4 indicadores × 4 comparações) batem com `output/tabelas/resumo.csv` em até 2 casas decimais.

- **IPCA**: 0,16% (valor) / 0,16% (var_mês) / 3,36% (var_ano) / 4,64% (var_12m) — Linhas 22, 89 ✓
- **Câmbio**: 5,11 BRL/USD (valor) / -1,31% (var_mês) / -7,15% (var_ano) / -8,81% (var_12m) — Linhas 22, 146 ✓
- **Selic**: 14,25% a.a. (valor) / 0,00% (var_mês) / -0,75% (var_ano) / -0,75% (var_12m) — Linhas 22, 189 ✓
- **IBC-Br**: 111,15 (valor) / 0,51% (var_mês) / 1,31% (var_ano) / 0,92% (var_12m) — Linhas 22, 237 ✓

Tabela-resumo HTML (linhas 26-81) lê dinamicamente do CSV. Formatação respeitada.

### Coerência Direcional
✓ 10 frases comparativas auditadas. Todas com direção coerente ao sinal matemático.

1. Linha 22 — "0,16%, resultado abaixo dos 0,58%": 0,16 - 0,58 = **-0,42** → "abaixo" ✓
2. Linha 22 — Câmbio "patamar inferior": 5,11 < 5,1766 → "inferior" ✓
3. Linha 89 — "resultado abaixo dos 0,58% apurados em maio": -0,42 → "abaixo" + "desaceleração" ✓
4. Linha 146 — "configurando queda mensal": -1,31% → "queda" ✓
5. Linha 148 — "queda de -8,81%": negativo → "queda" ✓
6. Linha 189 — "patamar idêntico": 14,25 - 14,25 = **0,00** → "estável" ✓
7. Linha 189 — "configurando queda": 14,25 - 15,00 = **-0,75** → "queda" ✓
8. Linha 237 — "alta de 0,51%": 111,15 - 110,59 = **+0,51** → "alta" ✓
9. Linha 279 — "ficou abaixo do resultado de maio": 0,16 < 0,58 → "abaixo" ✓
10. Linha 281 — "quedas de 7,15% e 8,81%": ambas negativas → "quedas" ✓

Nenhuma inversão de direção. Todos os sinais correspondem às palavras utilizadas.

### Estética Corporativa dos Gráficos
✓ 4 gráficos conformes com especificação de `redator_relatorio.md` (seção 6, linhas 67-184).

**Gráfico 1 — IPCA (linhas 97-129):**
- Implementação: `go.Bar` + `go.Scatter` (MM3 com `dash="dot"`)
- `plot_bgcolor=COR_FUNDO`, `fig.show()` presente
- Fonte HTML em bloco separado (linhas 132-135) ✓

**Gráfico 2 — Câmbio (linhas 154-172):**
- Implementação: `go.Scatter` com `fill="tozeroy"`, `fillcolor="rgba(43,108,176,0.08)"`
- **SEM linha de referência adicional** (conforme especificação "SEM linha de referência") ✓
- `plot_bgcolor=COR_FUNDO`, `fig.show()` presente
- Fonte HTML separada (linhas 175-178) ✓

**Gráfico 3 — Selic (linhas 197-220):**
- Implementação: `shape="hv"` (step line) + segunda série com `dash="dash"` (referência)
- `plot_bgcolor=COR_FUNDO`, `fig.show()` presente
- Fonte HTML separada (linhas 223-226) ✓

**Gráfico 4 — IBC-Br (linhas 245-266):**
- Implementação: Duas séries (`IBC-Br (original)` em `COR_LINHA2`, `IBC-Br (dessaz.)` em `COR_LINHA`)
- **SEM linha de referência** (conforme especificação "SEM linha de referência") ✓
- `plot_bgcolor=COR_FUNDO`, `fig.show()` presente
- Fonte HTML separada (linhas 269-272) ✓

Paleta corporativa: COR_LINHA (#2b6cb0), COR_LINHA2 (#90cdf4), COR_MEDIA (#c53030), COR_REF (#e53e3e), COR_FUNDO (#f4f6f9). Layout base com gridcolor="white", margins, xaxis/yaxis showgrid presente em todos.

### Credenciais, Botão e Rodapé

- YAML author (linha 4): `"Raimundo Casé"` ✓
- Identificação pessoal (linha 16): `**Raimundo Casé - economista**` ✓
- Botão print (linha 18): `<button class="print-btn"...>` ✓
- Rodapé (linhas 287-292):
  - Contém "Raimundo Casé - economista" ✓
  - Contém "BCB — Banco Central do Brasil" ✓
  - Contém "IBGE — Instituto Brasileiro de Geografia e Estatística" ✓

### Tom Institucional

Verificados termos proibidos em toda a narrativa:
- Sem "cirúrgico" ✓
- Sem "destrava" ✓
- Sem "pujante" ✓
- Sem "expressivo" como adjetivo de magnitude ✓
- Sem "robusto" como adjetivo de magnitude ✓

Linguagem técnica, objetiva. 3 parágrafos por indicador. Estrutura mantida.

### Estrutura Geral

- YAML conforme especificação ✓
- Panorama Geral integrando 4 indicadores (linhas 20-22) ✓
- Tabela-Resumo colorida com HTML (linhas 26-81) ✓
- 4 seções analíticas dentro de `::: {.bloco-analise}` (inflação, câmbio, juros, atividade) ✓
- Síntese e Perspectivas com 4 parágrafos temáticos (linhas 277-285) ✓
- Rodapé com créditos e responsabilidade (linhas 287-292) ✓

---

**Parecer final:** Documento aprovado para publicação. Todas as verificações obrigatórias de auditoria foram satisfeitas sem qualquer desvio. Fidelidade numérica, coerência direcional, estética corporativa, credenciais e tom institucional confirmados.
