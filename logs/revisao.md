ok

## Auditoria Técnica — boletim_2026-07-20.qmd

Data da auditoria: 2026-07-20  
Revisor Técnico: Sistema de Auditoria Automática

---

### Resultado Geral
✓ **DOCUMENTO APROVADO PARA PUBLICAÇÃO**

Todas as auditorias obrigatórias foram executadas com sucesso. Nenhuma falha detectada.

---

### 1. Fidelidade Numérica ✓

**Validação contra `output/tabelas/resumo.csv`:**

- **IPCA**: 0,16% (valor) / 0,16% (var_mês) / 3,36% (var_ano) / 4,64% (var_12m) — Linhas 56, 94 ✓
- **Câmbio**: 5,12 BRL/USD (valor) / -1,14% (var_mês) / -6,99% (var_ano) / -8,65% (var_12m) — Linhas 56, 151 ✓
- **Selic**: 14,25% a.a. (valor) / 0,00% (var_mês) / -0,75% (var_ano) / -0,75% (var_12m) — Linhas 56, 194 ✓
- **IBC-Br**: 111,04 (valor) / 0,07% (var_mês) / 1,24% (var_ano) / 0,80% (var_12m) — Linhas 56, 242 ✓

Tabela-resumo HTML (linhas 28-85) lê dinamicamente do CSV com formatação `:.2f` nas variações. Todos os 16 valores batem com precisão de 2 casas decimais.

---

### 2. Coerência Direcional ✓

**8 frases comparativas auditadas. Todas com direção coerente ao sinal matemático:**

1. **Linha 94:** "0,16%, resultado **abaixo** dos 0,58%... **desaceleração**"
   - Cálculo: 0.16 - 0.58 = **-0,42** → "abaixo" + "desaceleração" ✓

2. **Linha 151:** "patamar **abaixo** do fechamento de junho de R$ 5,1766... **recuo** mensal de 1,14%"
   - Cálculo: 5.12 - 5.1766 = **negativo** → "abaixo" + "recuo" ✓

3. **Linha 152:** "**queda** acumulada no ano chega a 6,99%"
   - Verificação: var_ano = **-6,99** → "queda" ✓

4. **Linha 152:** "**recuo** em 12 meses é de 8,65%"
   - Verificação: var_12m = **-8,65** → "recuo" ✓

5. **Linha 194:** "patamar **idêntico**... **sem variação** mensal"
   - Verificação: var_mês = **0,00** → "idêntico" ✓

6. **Linha 194:** "taxa acumula **queda** de 0,75 pp no ano"
   - Verificação: var_ano = **-0,75** → "queda" ✓

7. **Linha 242:** "111,04 pontos ante 110,96... uma **alta** de 0,07%"
   - Cálculo: 111.04 - 110.96 = **+0,08** (absoluto) / **+0,07%** (percentual) → "alta" ✓

8. **Linha 284:** "acumulado de 4,64% permanece 0,14 pp **acima** do teto de 4,50%"
   - Cálculo: 4.64 - 4.50 = **+0,14** → "acima" ✓

Nenhuma inversão de direção. Todos os sinais correspondem exatamente às palavras utilizadas.

---

### 3. Estética Corporativa dos Gráficos ✓

**4 gráficos validados contra especificação de `redator_relatorio.md` (seção 6, linhas 67-184):**

**Gráfico 1 — IPCA (linhas 102-141):**
- Implementação: `go.Bar` (IPCA mensal) + `go.Scatter` (Média móvel 3m com `dash="dot"`)
- Cores: COR_LINHA (#2b6cb0) para barras, COR_MEDIA (#c53030) para MM3
- Layout base: `plot_bgcolor=COR_FUNDO`, `paper_bgcolor="white"`, height=350, margins, gridlines ✓
- Fonte HTML em bloco separado (linhas 137-141) — padrão obrigatório respeitado ✓

**Gráfico 2 — Câmbio (linhas 159-183):**
- Implementação: `go.Scatter` com `fill="tozeroy"`, `fillcolor="rgba(43,108,176,0.08)"`
- Cor: COR_LINHA (#2b6cb0)
- **SEM linha de referência adicional** (conforme especificação) ✓
- Layout base presente ✓
- Fonte HTML separada (linhas 180-183) ✓

**Gráfico 3 — Selic (linhas 202-231):**
- Implementação: Step line (`shape="hv"`) + segunda série (linha de referência com `dash="dash"`)
- Cores: COR_LINHA para série principal, COR_REF (#e53e3e) para referência
- Layout base presente ✓
- Fonte HTML separada (linhas 228-231) ✓

**Gráfico 4 — IBC-Br (linhas 250-277):**
- Implementação: Duas séries (IBC-Br Original em COR_LINHA2 #90cdf4, IBC-Br Dessaz. em COR_LINHA #2b6cb0)
- **SEM linha de referência** (conforme especificação) ✓
- Layout base presente ✓
- Fonte HTML separada (linhas 274-277) ✓

**Resumo de estética:**
- Paleta corporativa completa e uniforme ✓
- Nenhuma fonte em `add_annotation` ou `fig.update_layout(annotations=...)` ✓
- Padrão obrigatório "bloco Python + fig.show() + bloco HTML com fonte" em todos os 4 gráficos ✓

---

### 4. Credenciais, Botão e Rodapé ✓

- **YAML author (linha 4):** `"Raimundo Casé"` ✓
- **Identificação pessoal (linha 16):** `**Raimundo Casé - economista**` ✓
- **Botão print (linhas 18-20):** `<button class="print-btn" onclick="window.print()">Imprimir / Salvar PDF</button>` ✓
- **Rodapé (linhas 292-298):**
  - Contém "Raimundo Casé - economista" ✓
  - Contém "BCB — Banco Central do Brasil (Selic, Câmbio, IBC-Br)" ✓
  - Contém "IBGE — Instituto Brasileiro de Geografia e Estatística (IPCA)" ✓

---

### 5. Tom Institucional ✓

Verificação de termos proibidos em toda a narrativa:
- Sem "cirúrgico" ✓
- Sem "destrava" ✓
- Sem "robusto" como adjetivo de magnitude ✓
- Sem "pujante" ✓
- Sem "expressivo" como adjetivo de magnitude ✓
- Sem uso indevido de "—" como separador de ideias ✓

Linguagem técnica, objetiva e apropriada ao público institucional. 3 parágrafos por indicador conforme especificação. Estrutura de narrativa mantida.

---

### 6. Estrutura Geral ✓

- **YAML de cabeçalho:** Conforme especificação (linhas 1-14) ✓
- **Panorama Geral:** Parágrafo introdutório integrando 4 indicadores (linhas 22-24) ✓
- **Tabela-Resumo:** Renderizada em HTML colorido com cores dinâmicas de variação (linhas 28-85) ✓
- **4 seções analíticas:** Cada uma dentro de `::: {.bloco-analise}`
  - 1. Inflação — IPCA (linhas 88-142)
  - 2. Câmbio — BRL/USD (linhas 145-186)
  - 3. Juros — Meta Selic (linhas 188-234)
  - 4. Atividade Econômica — IBC-Br (linhas 236-280)
  - Cada seção com 3 parágrafos de análise + gráfico ✓
- **Síntese e Perspectivas:** 4 parágrafos temáticos com negrito (linhas 282-290) ✓
- **Rodapé HTML:** Com créditos e responsabilidade (linhas 292-298) ✓

---

### Conclusão

✓ **DOCUMENTO APROVADO PARA PUBLICAÇÃO SEM RESSALVAS**

Todas as verificações obrigatórias foram satisfeitas:
- Fidelidade numérica: 16/16 valores conformes
- Coerência direcional: 8/8 frases críticas validadas
- Estética corporativa: 4/4 gráficos conformes a especificação
- Credenciais e identidade: Completas e corretas
- Tom institucional: Apropriado, sem termos proibidos
- Estrutura: Integral e conforme padrão

O boletim `boletim_2026-07-20.qmd` está pronto para renderização e publicação.
