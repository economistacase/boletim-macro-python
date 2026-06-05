"""
Analise Quantitativa - Boletim Macroeconomico
Data de referencia: 2026-06-04
Gera: output/tabelas/resumo.csv e output/tabelas/historico.csv
"""

import pandas as pd
import numpy as np
import os
import warnings

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# Configuracoes
# ---------------------------------------------------------------------------
BASE_DIR = "F:/boletim-macro-python"
DADOS_DIR = os.path.join(BASE_DIR, "output", "dados")
TABELAS_DIR = os.path.join(BASE_DIR, "output", "tabelas")
os.makedirs(TABELAS_DIR, exist_ok=True)

DATA_REF = pd.Timestamp("2026-06-04")
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
# A serie bruta (serie 11 do BCB) armazena a taxa Over Selic em % ao dia.
# Exemplo: 0.053400 significa 0.0534% ao dia.
# Conversao para % a.a. por capitalizacao composta com 252 dias uteis:
#   taxa_aa = ((1 + taxa_dia/100)^252 - 1) * 100
# ---------------------------------------------------------------------------
selic_clean = selic_raw.dropna(subset=["valor"]).copy()
# Serie 432 (Meta Selic) ja e % a.a. definida pelo Copom - sem conversao necessaria
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
