"""
Analise Quantitativa - Boletim Macroeconomico
Uso: python python/analise.py [DATA_REFERENCIA]
     DATA_REFERENCIA (YYYY-MM-DD) padrao: data atual. Usada apenas como corte
     dos 5 anos do historico.csv.
Gera: output/tabelas/resumo.csv, output/tabelas/historico.csv e
      output/tabelas/contexto.md (fatos historicos ja calculados para o redator)
"""

import sys
import pandas as pd
import numpy as np
import os
import warnings

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# Configuracoes
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DADOS_DIR = os.path.join(BASE_DIR, "output", "dados")
TABELAS_DIR = os.path.join(BASE_DIR, "output", "tabelas")
os.makedirs(TABELAS_DIR, exist_ok=True)

DATA_REF = pd.Timestamp(sys.argv[1]) if len(sys.argv) > 1 else pd.Timestamp.today()
ALERTAS = []

# ---------------------------------------------------------------------------
# Leitura dos CSVs
# ---------------------------------------------------------------------------
def ler_csv(nome):
    path = os.path.join(DADOS_DIR, nome)
    df = pd.read_csv(path, dtype={"valor": float})
    df["data"] = pd.to_datetime(df["data"], dayfirst=True)
    df = df.sort_values("data").reset_index(drop=True)
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
    return df


ipca      = ler_csv("ipca.csv")
cambio    = ler_csv("cambio.csv")
selic_raw = ler_csv("selic.csv")  # Serie 432: Meta Selic em % a.a. (valor exato do Copom)
ibc_orig  = ler_csv("ibcbr_orig.csv")
ibc_sa    = ler_csv("ibcbr_sa.csv")

# ---------------------------------------------------------------------------
# Funcoes auxiliares
# ---------------------------------------------------------------------------
def produto_composto(series_pct):
    """Produtorio composto de variacoes percentuais -> retorna em %."""
    fatores = 1 + series_pct / 100
    return (fatores.prod() - 1) * 100


def var_pct(atual, anterior):
    """Variacao percentual simples."""
    if pd.isna(atual) or pd.isna(anterior) or anterior == 0:
        return np.nan
    return (atual / anterior - 1) * 100


def ultimo_valor(df, antes_de=None):
    """Ultimo valor nao-nulo, opcionalmente antes de uma data (exclusive)."""
    d = df.dropna(subset=["valor"])
    if antes_de is not None:
        d = d[d["data"] < antes_de]
    if d.empty:
        return np.nan, pd.NaT
    row = d.iloc[-1]
    return row["valor"], row["data"]


def ultimo_do_mes(df, ano, mes):
    """Ultimo valor disponivel no mes/ano indicados."""
    d = df[(df["data"].dt.year == ano) & (df["data"].dt.month == mes)]
    d = d.dropna(subset=["valor"])
    if d.empty:
        return np.nan, pd.NaT
    row = d.iloc[-1]
    return row["valor"], row["data"]


def primeiro_do_mes(df, ano, mes):
    """Primeiro valor disponivel no mes/ano indicados."""
    d = df[(df["data"].dt.year == ano) & (df["data"].dt.month == mes)]
    d = d.dropna(subset=["valor"])
    if d.empty:
        return np.nan, pd.NaT
    row = d.iloc[0]
    return row["valor"], row["data"]


# ---------------------------------------------------------------------------
# IPCA
# ---------------------------------------------------------------------------
ipca_clean = ipca.dropna(subset=["valor"]).copy()

# valor_atual e data_ref: ultimo mes disponivel
ipca_atual_val, ipca_atual_data = ultimo_valor(ipca_clean)

# var_mes: ultima variacao mensal (a serie ja e variacao mensal em %)
var_mes_ipca = ipca_atual_val

# var_ano: produto composto desde janeiro do ano corrente ate o mes atual
ano_corrente = ipca_atual_data.year
ipca_ano = ipca_clean[
    (ipca_clean["data"].dt.year == ano_corrente) &
    (ipca_clean["data"] <= ipca_atual_data)
]
if ipca_ano.empty:
    var_ano_ipca = np.nan
    ALERTAS.append("IPCA: sem dados no ano corrente para var_ano.")
else:
    var_ano_ipca = produto_composto(ipca_ano["valor"])

# var_12m: produto composto dos ultimos 12 meses ate o mes atual
ipca_12m = ipca_clean[ipca_clean["data"] <= ipca_atual_data].tail(12)
if len(ipca_12m) < 12:
    ALERTAS.append(f"IPCA: apenas {len(ipca_12m)} meses disponíveis para var_12m (esperado 12).")
var_12m_ipca = produto_composto(ipca_12m["valor"]) if not ipca_12m.empty else np.nan

# ---------------------------------------------------------------------------
# Cambio
# ---------------------------------------------------------------------------
cambio_clean = cambio.dropna(subset=["valor"]).copy()

# valor_atual: ultimo fechamento disponivel
cambio_atual_val, cambio_atual_data = ultimo_valor(cambio_clean)

# var_mes: atual vs ultimo dia util do mes anterior
mes_ant = cambio_atual_data.replace(day=1) - pd.DateOffset(days=1)
cambio_mes_ant_val, _ = ultimo_do_mes(cambio_clean, mes_ant.year, mes_ant.month)
var_mes_cambio = var_pct(cambio_atual_val, cambio_mes_ant_val)
if pd.isna(var_mes_cambio):
    ALERTAS.append("Cambio: nao foi possivel calcular var_mes.")

# var_ano: atual vs ultimo fechamento de dezembro do ano anterior
ano_ant = cambio_atual_data.year - 1
cambio_dez_val, _ = ultimo_do_mes(cambio_clean, ano_ant, 12)
var_ano_cambio = var_pct(cambio_atual_val, cambio_dez_val)
if pd.isna(var_ano_cambio):
    ALERTAS.append("Cambio: nao foi possivel calcular var_ano (sem dados de dez do ano anterior).")

# var_12m: atual vs ultimo dia util disponivel do mesmo mes do ano passado
mes_12m_ano = cambio_atual_data.year - 1
mes_12m_mes = cambio_atual_data.month
cambio_12m_val, _ = ultimo_do_mes(cambio_clean, mes_12m_ano, mes_12m_mes)
var_12m_cambio = var_pct(cambio_atual_val, cambio_12m_val)
if pd.isna(var_12m_cambio):
    ALERTAS.append("Cambio: nao foi possivel calcular var_12m.")

# ---------------------------------------------------------------------------
# Selic (% a.a.)
# Serie 432 do BCB (Meta Selic): valor exato cravado pelo Copom em % a.a.
# Ja vem na unidade correta - sem conversao necessaria.
# ---------------------------------------------------------------------------
selic_clean = selic_raw.dropna(subset=["valor"]).copy()
print("INFO: Meta Selic (serie 432) carregada diretamente em % a.a.")

selic_atual_val, selic_atual_data = ultimo_valor(selic_clean)

# var_mes: atual vs primeiro valor disponivel do mes atual (diferenca em p.p.)
selic_ini_mes_val, _ = primeiro_do_mes(selic_clean, selic_atual_data.year, selic_atual_data.month)
var_mes_selic = (selic_atual_val - selic_ini_mes_val) if not pd.isna(selic_ini_mes_val) else np.nan

# var_ano: atual vs primeiro valor disponivel do ano corrente (diferenca em p.p.)
selic_ini_ano_val, _ = primeiro_do_mes(selic_clean, selic_atual_data.year, 1)
var_ano_selic = (selic_atual_val - selic_ini_ano_val) if not pd.isna(selic_ini_ano_val) else np.nan

# var_12m: atual vs primeiro valor disponivel de 12 meses atras (diferenca em p.p.)
data_12m_atras = selic_atual_data - pd.DateOffset(months=12)
selic_12m_val, _ = primeiro_do_mes(selic_clean, data_12m_atras.year, data_12m_atras.month)
var_12m_selic = (selic_atual_val - selic_12m_val) if not pd.isna(selic_12m_val) else np.nan

# ---------------------------------------------------------------------------
# IBC-Br
# ---------------------------------------------------------------------------
ibc_orig_clean = ibc_orig.dropna(subset=["valor"]).copy()
ibc_sa_clean   = ibc_sa.dropna(subset=["valor"]).copy()

# valor_atual: ultimo valor da serie dessaz.
ibc_sa_atual_val, ibc_sa_atual_data = ultimo_valor(ibc_sa_clean)

# data_ref: data do ultimo dado da serie original
_, ibc_orig_ultima_data = ultimo_valor(ibc_orig_clean)

# var_mes: variacao % da serie dessaz. contra o mes anterior
ibc_sa_sorted = ibc_sa_clean.sort_values("data")
if len(ibc_sa_sorted) >= 2:
    ibc_sa_mes_ant_val = ibc_sa_sorted.iloc[-2]["valor"]
    var_mes_ibc = var_pct(ibc_sa_atual_val, ibc_sa_mes_ant_val)
else:
    ibc_sa_mes_ant_val = np.nan
    var_mes_ibc = np.nan
    ALERTAS.append("IBC-Br: serie dessaz. com menos de 2 observacoes.")

# var_ano: media da serie original no ano corrente (ate mes mais recente)
#          vs media do mesmo periodo do ano anterior
ano_ibc = ibc_orig_ultima_data.year
mes_ibc = ibc_orig_ultima_data.month

ibc_orig_ano_atual = ibc_orig_clean[
    (ibc_orig_clean["data"].dt.year == ano_ibc) &
    (ibc_orig_clean["data"].dt.month <= mes_ibc)
]
ibc_orig_ano_ant = ibc_orig_clean[
    (ibc_orig_clean["data"].dt.year == ano_ibc - 1) &
    (ibc_orig_clean["data"].dt.month <= mes_ibc)
]

if ibc_orig_ano_atual.empty or ibc_orig_ano_ant.empty:
    var_ano_ibc = np.nan
    ALERTAS.append("IBC-Br: dados insuficientes para calcular var_ano.")
else:
    media_atual = ibc_orig_ano_atual["valor"].mean()
    media_ant   = ibc_orig_ano_ant["valor"].mean()
    var_ano_ibc = var_pct(media_atual, media_ant)

# var_12m: serie original - ultimo mes disponivel vs mesmo mes do ano passado
ibc_orig_atual_val, _ = ultimo_valor(ibc_orig_clean)
ibc_orig_12m_val, _   = ultimo_do_mes(ibc_orig_clean, ibc_orig_ultima_data.year - 1, ibc_orig_ultima_data.month)
var_12m_ibc = var_pct(ibc_orig_atual_val, ibc_orig_12m_val)
if pd.isna(var_12m_ibc):
    ALERTAS.append("IBC-Br: nao foi possivel calcular var_12m (sem dado do mesmo mes no ano anterior).")

# ---------------------------------------------------------------------------
# Montagem do resumo.csv
# Regra critica: todas as colunas numericas com no maximo 2 casas decimais.
# Unidade do Cambio: BRL/USD (sem cifrao para evitar bugs no Markdown).
# ---------------------------------------------------------------------------
resumo = pd.DataFrame([
    {
        "indicador":   "IPCA",
        "unidade":     "%",
        "valor_atual": ipca_atual_val,
        "data_ref":    ipca_atual_data.strftime("%Y-%m-%d"),
        "var_mes":     var_mes_ipca,
        "var_ano":     var_ano_ipca,
        "var_12m":     var_12m_ipca,
    },
    {
        "indicador":   "Cambio",
        "unidade":     "BRL/USD",
        "valor_atual": cambio_atual_val,
        "data_ref":    cambio_atual_data.strftime("%Y-%m-%d"),
        "var_mes":     var_mes_cambio,
        "var_ano":     var_ano_cambio,
        "var_12m":     var_12m_cambio,
    },
    {
        "indicador":   "Selic",
        "unidade":     "% a.a.",
        "valor_atual": selic_atual_val,
        "data_ref":    selic_atual_data.strftime("%Y-%m-%d"),
        "var_mes":     var_mes_selic,
        "var_ano":     var_ano_selic,
        "var_12m":     var_12m_selic,
    },
    {
        "indicador":   "IBC-Br",
        "unidade":     "indice",
        "valor_atual": ibc_sa_atual_val,
        "data_ref":    ibc_orig_ultima_data.strftime("%Y-%m-%d"),
        "var_mes":     var_mes_ibc,
        "var_ano":     var_ano_ibc,
        "var_12m":     var_12m_ibc,
    },
])

# Exporta com float_format='%.2f' para garantir exatamente 2 casas decimais em todos os valores
resumo_path = os.path.join(TABELAS_DIR, "resumo.csv")
resumo.to_csv(resumo_path, index=False, float_format="%.2f")
print(f"Gravado: {resumo_path}")

# ---------------------------------------------------------------------------
# Montagem do historico.csv  (formato longo, ultimos 5 anos)
# ---------------------------------------------------------------------------
corte = DATA_REF - pd.DateOffset(years=5)  # 2021-06-04

# IPCA: mensal - usa diretamente
ipca_h = ipca_clean[ipca_clean["data"] >= corte][["data", "valor"]].copy()
ipca_h["indicador"] = "IPCA"

# Cambio: diario -> resample mensal (ultimo valor do mes)
cambio_h = (
    cambio_clean[cambio_clean["data"] >= corte]
    .set_index("data")["valor"]
    .resample("ME")
    .last()
    .reset_index()
)
cambio_h.columns = ["data", "valor"]
cambio_h["indicador"] = "Cambio"

# Selic: diario -> resample mensal (ultimo valor do mes), ja convertida para % a.a.
selic_h = (
    selic_clean[selic_clean["data"] >= corte]
    .set_index("data")["valor"]
    .resample("ME")
    .last()
    .reset_index()
)
selic_h.columns = ["data", "valor"]
selic_h["indicador"] = "Selic"

# IBC-Br original: mensal
ibc_orig_h = ibc_orig_clean[ibc_orig_clean["data"] >= corte][["data", "valor"]].copy()
ibc_orig_h["indicador"] = "IBC-Br (original)"

# IBC-Br dessaz.: mensal
ibc_sa_h = ibc_sa_clean[ibc_sa_clean["data"] >= corte][["data", "valor"]].copy()
ibc_sa_h["indicador"] = "IBC-Br (dessaz.)"

# Empilha
historico = pd.concat(
    [ipca_h, cambio_h, selic_h, ibc_orig_h, ibc_sa_h],
    ignore_index=True
)

# Padroniza data para YYYY-MM-DD e remove nulos
historico["data"] = pd.to_datetime(historico["data"]).dt.strftime("%Y-%m-%d")
historico = historico.dropna(subset=["valor"])
historico = historico.sort_values(["indicador", "data"]).reset_index(drop=True)

historico_path = os.path.join(TABELAS_DIR, "historico.csv")
historico.to_csv(historico_path, index=False)
print(f"Gravado: {historico_path}")

# ---------------------------------------------------------------------------
# Montagem do contexto.md
# Fatos historicos ja calculados (com a direcao de cada comparacao) para o
# redator citar sem fazer contas nem recorrer a memoria. Toda afirmacao
# historica do boletim deve sair daqui, do resumo.csv ou do historico.csv.
# ---------------------------------------------------------------------------
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
         "agosto", "setembro", "outubro", "novembro", "dezembro"]


def fmt(v, casas=2):
    return f"{v:.{casas}f}".replace(".", ",")


def mes_ano(d):
    return f"{MESES[d.month - 1]}/{d.year}"


def dia_mes_ano(d):
    return f"{d.day:02d}/{d.month:02d}/{d.year}"


def direcao(diff, alta="alta", queda="queda", estavel="estável"):
    d = round(diff, 2)
    return alta if d > 0 else queda if d < 0 else estavel


def cmp_txt(atual, anterior, sufixo="", alta="alta", queda="queda", unid_diff="p.p."):
    # diferenca calculada sobre os valores ja arredondados, para o texto ser conferivel
    atual, anterior = round(atual, 2), round(anterior, 2)
    diff = atual - anterior
    return (f"{fmt(atual)}{sufixo} vs. {fmt(anterior)}{sufixo} → diferença "
            f"{'+' if diff >= 0 else ''}{fmt(diff)} {unid_diff} → **{direcao(diff, alta, queda)}**")


ctx = [f"# Contexto histórico calculado — referência {DATA_REF.strftime('%Y-%m-%d')}", "",
       "Fatos gerados por `python/analise.py` a partir das séries oficiais. "
       "A direção de cada comparação já está calculada: use exatamente a palavra indicada.", ""]

# --- IPCA ---
ipca_s = ipca_clean.set_index("data")["valor"]
ipca_12m_s = ((1 + ipca_s / 100).rolling(12).apply(np.prod, raw=True) - 1) * 100
d_ant = ipca_s.index[-2]
ctx += ["## IPCA", "",
        f"- Mês de referência: {mes_ano(ipca_atual_data)}.",
        f"- Variação mensal {mes_ano(ipca_atual_data)} vs. {mes_ano(d_ant)}: "
        + cmp_txt(ipca_s.iloc[-1], ipca_s.iloc[-2], "%", "aceleração", "desaceleração"),
        f"- Acumulado em 12 meses {mes_ano(ipca_atual_data)} vs. {mes_ano(d_ant)}: "
        + cmp_txt(ipca_12m_s.iloc[-1], ipca_12m_s.iloc[-2], "%", "alta", "queda")]
d_12 = ipca_atual_data - pd.DateOffset(years=1)
if d_12 in ipca_s.index:
    ctx.append(f"- Variação mensal {mes_ano(ipca_atual_data)} vs. mesmo mês de {d_12.year} "
               f"({mes_ano(d_12)}): " + cmp_txt(ipca_s.iloc[-1], ipca_s[d_12], "%", "maior", "menor"))
# Meta de inflacao do CMN (regime de meta continua desde 2025): 3,0% +/- 1,5 p.p.
v12 = ipca_12m_s.iloc[-1]
pos_meta = "acima do teto (4,50%)" if v12 > 4.5 else "abaixo do piso (1,50%)" if v12 < 1.5 else "dentro do intervalo de tolerância (1,50% a 4,50%)"
ctx.append(f"- Meta de inflação (CMN, meta contínua): 3,00% com tolerância de 1,5 p.p. "
           f"O acumulado em 12 meses ({fmt(v12)}%) está **{pos_meta}**.")
s5 = ipca_12m_s[ipca_12m_s.index >= corte].dropna()
ctx += [f"- Acumulado em 12 meses nos últimos 5 anos: máximo {fmt(s5.max())}% ({mes_ano(s5.idxmax())}), "
        f"mínimo {fmt(s5.min())}% ({mes_ano(s5.idxmin())}).", "",
        "| Mês | Variação mensal (%) | Acumulado 12 meses (%) |", "|---|---|---|"]
for d in ipca_s.index[-12:]:
    ctx.append(f"| {mes_ano(d)} | {fmt(ipca_s[d])} | {fmt(ipca_12m_s[d])} |")
ctx.append("")

# --- Selic ---
sel = selic_clean.set_index("data")["valor"]
mudancas = sel[sel.diff().fillna(0) != 0]
ctx += ["## Selic (Meta, % a.a.)", "", f"- Nível atual: {fmt(selic_atual_val)}% a.a."]
if not mudancas.empty:
    d_ult = mudancas.index[-1]
    nivel_ant = sel[sel.index < d_ult].iloc[-1]
    ctx.append(f"- Vigente desde {dia_mes_ano(d_ult)}; nível anterior {fmt(nivel_ant)}% → "
               f"última decisão foi de **{direcao(mudancas.iloc[-1] - nivel_ant, 'alta', 'corte')}** "
               f"de {fmt(abs(mudancas.iloc[-1] - nivel_ant))} p.p.")
else:
    ctx.append(f"- Sem mudanças desde o início da série ({dia_mes_ano(sel.index[0])}).")
ctx += [f"- Início do ano corrente ({selic_atual_data.year}): {fmt(selic_ini_ano_val)}% → hoje: "
        + cmp_txt(selic_atual_val, selic_ini_ano_val, "%", "alta", "queda"),
        f"- 12 meses atrás ({mes_ano(data_12m_atras)}): " + cmp_txt(selic_atual_val, selic_12m_val, "%", "alta", "queda")]
s5 = sel[sel.index >= corte]
d_max = s5[s5 == s5.max()].index
ctx += [f"- Últimos 5 anos: máximo {fmt(s5.max())}% (primeira vez em {dia_mes_ano(d_max[0])}, "
        f"último dia em {dia_mes_ano(d_max[-1])}), mínimo {fmt(s5.min())}% (último dia em "
        f"{dia_mes_ano(s5[s5 == s5.min()].index[-1])}).", "",
        "Trajetória completa da Meta Selic nos últimos 5 anos (cada linha = nova decisão do Copom em vigor):", "",
        "| Vigente desde | Nível (% a.a.) | Mudança (p.p.) |", "|---|---|---|",
        f"| {dia_mes_ano(s5.index[0])} (início da janela) | {fmt(s5.iloc[0])} | — |"]
for d, v in mudancas[mudancas.index >= corte].items():
    ant = sel[sel.index < d].iloc[-1]
    ctx.append(f"| {dia_mes_ano(d)} | {fmt(v)} | {'+' if v > ant else ''}{fmt(v - ant)} |")
ctx.append("")

# --- Cambio ---
ctx += ["## Câmbio (BRL/USD, PTAX)", "",
        f"- Último fechamento: {fmt(cambio_atual_val, 4)} em {dia_mes_ano(cambio_atual_data)}.",
        f"- Vs. fim do mês anterior ({fmt(cambio_mes_ant_val, 4)}): variação {fmt(var_mes_cambio)}% → "
        f"real **{direcao(var_mes_cambio, 'se desvalorizou', 'se valorizou')}**.",
        f"- Vs. fim de dezembro/{ano_ant} ({fmt(cambio_dez_val, 4)}): variação {fmt(var_ano_cambio)}% → "
        f"real **{direcao(var_ano_cambio, 'se desvalorizou', 'se valorizou')}** no ano.",
        f"- Vs. {mes_ano(pd.Timestamp(mes_12m_ano, mes_12m_mes, 1))} ({fmt(cambio_12m_val, 4)}): variação "
        f"{fmt(var_12m_cambio)}% → real **{direcao(var_12m_cambio, 'se desvalorizou', 'se valorizou')}** em 12 meses."]
s5 = cambio_clean[cambio_clean["data"] >= corte].set_index("data")["valor"]
ctx += [f"- Últimos 5 anos (diário): máximo {fmt(s5.max(), 4)} ({dia_mes_ano(s5.idxmax())}), "
        f"mínimo {fmt(s5.min(), 4)} ({dia_mes_ano(s5.idxmin())}).", "",
        "| Fim do mês | BRL/USD |", "|---|---|"]
for _, r in cambio_h.dropna().tail(7).iterrows():
    parcial = f" (parcial, até {dia_mes_ano(cambio_atual_data)})" if r["data"] >= cambio_atual_data else ""
    ctx.append(f"| {mes_ano(r['data'])}{parcial} | {fmt(r['valor'], 4)} |")
ctx.append("")

# --- IBC-Br ---
sa = ibc_sa_clean.set_index("data")["valor"]
orig = ibc_orig_clean.set_index("data")["valor"]
ctx += ["## IBC-Br", "",
        "- ATENÇÃO À METODOLOGIA: a variação mensal usa a série **dessazonalizada**; "
        "as variações no ano e em 12 meses usam a série **original** (sem ajuste). "
        "Não aplique as variações no ano/12 meses ao nível dessazonalizado.",
        f"- Mês de referência: {mes_ano(ibc_sa_atual_data)}. Nível dessazonalizado: {fmt(ibc_sa_atual_val)}.",
        f"- Mensal (dessaz.) vs. {mes_ano(sa.index[-2])}: variação {fmt(var_mes_ibc)}% → **{direcao(var_mes_ibc, 'alta', 'queda')}**.",
        f"- 12 meses (original, {mes_ano(ibc_orig_ultima_data)} vs. mesmo mês de {ibc_orig_ultima_data.year - 1}): "
        f"variação {fmt(var_12m_ibc)}% → **{direcao(var_12m_ibc, 'crescimento', 'retração')}**.",
        f"- No ano (original, média jan–{MESES[mes_ibc - 1][:3]}/{ano_ibc} vs. média jan–{MESES[mes_ibc - 1][:3]}/{ano_ibc - 1}): "
        f"variação {fmt(var_ano_ibc)}% → **{direcao(var_ano_ibc, 'crescimento', 'retração')}**."]
s5 = sa[sa.index >= corte]
ctx += [f"- Últimos 5 anos (dessaz.): máximo {fmt(s5.max())} ({mes_ano(s5.idxmax())}), "
        f"mínimo {fmt(s5.min())} ({mes_ano(s5.idxmin())}). Nível atual está "
        f"{fmt((ibc_sa_atual_val / s5.max() - 1) * 100)}% em relação ao máximo.", "",
        "| Mês | Dessaz. | Var. mensal dessaz. (%) | Original |", "|---|---|---|---|"]
var_sa = sa.pct_change() * 100
for d in sa.index[-7:]:
    ctx.append(f"| {mes_ano(d)} | {fmt(sa[d])} | {fmt(var_sa[d])} | {fmt(orig.get(d, np.nan))} |")
ctx.append("")

contexto_path = os.path.join(TABELAS_DIR, "contexto.md")
with open(contexto_path, "w", encoding="utf-8") as f:
    f.write("\n".join(ctx))
print(f"Gravado: {contexto_path}")

# ---------------------------------------------------------------------------
# Resumo no terminal
# ---------------------------------------------------------------------------
print("\n========== RESUMO.CSV ==========")
print(resumo.to_string(index=False))

print("\n========== HISTORICO.CSV (cobertura por indicador) ==========")
for ind in historico["indicador"].unique():
    sub = historico[historico["indicador"] == ind]
    print(f"  {ind}: {len(sub)} linhas | {sub['data'].min()} a {sub['data'].max()}")

if ALERTAS:
    print("\n========== ALERTAS ==========")
    for a in ALERTAS:
        print(f"  [ALERTA] {a}")
else:
    print("\nNenhum alerta: todos os dados foram encontrados e calculados corretamente.")
