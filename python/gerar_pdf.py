"""
Gera boletim_<DATA>.pdf diretamente via fpdf2 + matplotlib.
Uso: python python/gerar_pdf.py [DATA_REFERENCIA]
     DATA_REFERENCIA padrao: data atual (YYYY-MM-DD)
"""

import sys
import os
import re
from datetime import datetime
from io import BytesIO

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from fpdf import FPDF

# ── Configuracao ─────────────────────────────────────────────────────────────
DATA_REF = sys.argv[1] if len(sys.argv) > 1 else datetime.today().strftime("%Y-%m-%d")
BASE     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESUMO   = os.path.join(BASE, "output", "tabelas", "resumo.csv")
HIST     = os.path.join(BASE, "output", "tabelas", "historico.csv")
OUT_PDF  = os.path.join(BASE, f"boletim_{DATA_REF}.pdf")

# A4 em mm; margens: E=30 S=30 D=20 I=20
A4_W, A4_H    = 210, 297
ML, MT, MR, MB = 30, 30, 20, 20
TW = A4_W - ML - MR   # largura util = 160 mm

# Paleta
AZUL      = (43, 108, 176)
AZUL_CLR  = (144, 205, 244)
VERMELHO  = (197, 48, 48)
FUNDO     = (244, 246, 249)
CINZA_TXT = (80, 80, 80)
BRANCO    = (255, 255, 255)
VERDE_BG  = (212, 237, 218)
VERM_BG   = (248, 215, 218)
NEUTRO_BG = (248, 248, 248)

# ── Helpers matplotlib ────────────────────────────────────────────────────────
STYLE = {
    "axes.facecolor":  "#f4f6f9",
    "figure.facecolor": "white",
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "axes.grid":         True,
    "grid.color":        "white",
    "grid.linewidth":    1.2,
    "font.family":       "sans-serif",
    "font.size":         9,
    "axes.titlesize":    10,
    "axes.titleweight":  "bold",
    "axes.labelsize":    8,
    "xtick.labelsize":   7,
    "ytick.labelsize":   7,
}

def fig_to_bytes(fig):
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    plt.close(fig)
    buf.seek(0)
    return buf

def chart_ipca(df):
    with plt.rc_context(STYLE):
        sub = df[df["indicador"] == "IPCA"].copy().sort_values("data")
        sub["mm3"] = sub["valor"].rolling(3).mean()
        fig, ax = plt.subplots(figsize=(7.5, 2.8))
        ax.bar(sub["data"], sub["valor"], color="#2b6cb0", width=20, label="IPCA mensal (%)")
        ax.plot(sub["data"], sub["mm3"], color="#c53030", lw=1.5,
                linestyle="--", label="Med. movel 3m")
        ax.set_title("IPCA — Variacao Mensal (%) | Ultimos 5 Anos")
        ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%b/%y"))
        ax.xaxis.set_major_locator(matplotlib.dates.MonthLocator(interval=6))
        plt.xticks(rotation=30, ha="right")
        ax.legend(fontsize=7, loc="upper right")
        ax.set_ylabel("%")
        fig.tight_layout()
        return fig_to_bytes(fig)

def chart_cambio(df):
    with plt.rc_context(STYLE):
        sub = df[df["indicador"] == "Cambio"].copy().sort_values("data")
        fig, ax = plt.subplots(figsize=(7.5, 2.8))
        ax.fill_between(sub["data"], sub["valor"], alpha=0.12, color="#2b6cb0")
        ax.plot(sub["data"], sub["valor"], color="#2b6cb0", lw=2, label="BRL/USD")
        ax.set_title("Cambio BRL/USD — Fechamento Mensal | Ultimos 5 Anos")
        ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%b/%y"))
        ax.xaxis.set_major_locator(matplotlib.dates.MonthLocator(interval=6))
        plt.xticks(rotation=30, ha="right")
        ax.set_ylabel("R$/USD")
        fig.tight_layout()
        return fig_to_bytes(fig)

def chart_selic(df, val_atual):
    with plt.rc_context(STYLE):
        sub = df[df["indicador"] == "Selic"].copy().sort_values("data")
        fig, ax = plt.subplots(figsize=(7.5, 2.8))
        ax.step(sub["data"], sub["valor"], color="#2b6cb0", lw=2,
                where="post", label="Meta Selic (% a.a.)")
        ax.axhline(val_atual, color="#c53030", lw=1.2, linestyle="--",
                   label=f"Valor atual: {val_atual:.2f}%")
        ax.set_title("Meta Selic — % a.a. | Ultimos 5 Anos")
        ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%b/%y"))
        ax.xaxis.set_major_locator(matplotlib.dates.MonthLocator(interval=6))
        plt.xticks(rotation=30, ha="right")
        ax.legend(fontsize=7, loc="lower right")
        ax.set_ylabel("% a.a.")
        fig.tight_layout()
        return fig_to_bytes(fig)

def chart_ibc(df):
    with plt.rc_context(STYLE):
        orig = df[df["indicador"] == "IBC-Br (original)"].copy().sort_values("data")
        sa   = df[df["indicador"] == "IBC-Br (dessaz.)"].copy().sort_values("data")
        fig, ax = plt.subplots(figsize=(7.5, 2.8))
        ax.plot(orig["data"], orig["valor"], color="#90cdf4", lw=1.2, label="Original")
        ax.plot(sa["data"],   sa["valor"],   color="#2b6cb0", lw=2,   label="Dessaz.")
        ax.set_title("IBC-Br — Indice de Atividade Economica | Ultimos 5 Anos")
        ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%b/%y"))
        ax.xaxis.set_major_locator(matplotlib.dates.MonthLocator(interval=6))
        plt.xticks(rotation=30, ha="right")
        ax.legend(fontsize=7, loc="lower right")
        ax.set_ylabel("Indice")
        fig.tight_layout()
        return fig_to_bytes(fig)

# ── Gera narrativa da Selic a partir da série 432 (historico.csv) ────────────
def gerar_secao_selic(df_hist, r):
    """
    Constrói os 3 parágrafos da seção Selic exclusivamente com dados da série 432.
    Nunca usa texto do .qmd para esta seção — garante consistência metodológica.
    """
    selic_v   = float(r.loc["Selic", "valor_atual"])
    selic_dr  = r.loc["Selic", "data_ref"]
    selic_mes = float(r.loc["Selic", "var_mes"])
    selic_ano = float(r.loc["Selic", "var_ano"])
    selic_12m = float(r.loc["Selic", "var_12m"])

    df_s = df_hist[df_hist["indicador"] == "Selic"].copy().sort_values("data")
    df_s["data"] = pd.to_datetime(df_s["data"])

    val_max  = df_s["valor"].max()
    val_min  = df_s["valor"].min()
    data_max = df_s.loc[df_s["valor"].idxmax(), "data"]
    data_ini = df_s.loc[df_s["valor"].idxmin(), "data"]

    mes_max  = data_max.strftime("%B/%Y").lower()
    mes_ini  = data_ini.strftime("%B/%Y").lower()
    inicio_ano = selic_v - selic_ano

    p1 = (
        f"A Meta Selic está fixada em {selic_v:.2f}% a.a. em {selic_dr}, "
        f"{'sem variação no mês corrente' if selic_mes == 0 else f'com variação de {selic_mes:+.2f} p.p. no mês'}. "
        f"No acumulado do ano, a taxa variou {selic_ano:+.2f} p.p. (de {inicio_ano:.2f}% a.a. em janeiro para "
        f"{selic_v:.2f}% a.a. na data de referência), e {selic_12m:+.2f} p.p. nos últimos 12 meses, "
        f"{'indicando início de ciclo de afrouxamento' if selic_ano < 0 else 'indicando postura de aperto monetário'} "
        f"pelo Copom."
    )
    p2 = (
        f"O ciclo de política monetária refletido nos dados da Meta Selic (SGS 432) mostra que a taxa "
        f"atingiu o pico de {val_max:.2f}% a.a. em {mes_max} e iniciou o período de "
        f"{'afrouxamento' if selic_ano < 0 else 'aperto'} a partir de então. "
        f"O diferencial de juros reais do Brasil em relação aos pares emergentes permanece elevado, "
        f"favorecendo a atração de capital externo e contribuindo para a estabilidade cambial observada em 2026."
    )
    p3 = (
        f"O ritmo de {'cortes' if selic_ano < 0 else 'altas'} futuros da Meta Selic dependerá da velocidade "
        f"com que a inflação corrente e as expectativas de médio prazo se aproximem do centro da meta de 3,0%. "
        f"A condução da política fiscal será determinante: pressões de demanda agregada oriundas de expansão "
        f"fiscal poderiam limitar o espaço para {'cortes' if selic_ano < 0 else 'pausas'} adicionais. "
        f"O Copom avaliará a trajetória desinflacionária nas próximas reuniões para calibrar o ritmo do ciclo."
    )
    return f"{p1}\n\n{p2}\n\n{p3}"


# ── Extrai narrativas do .qmd para IPCA, Câmbio e IBC-Br ─────────────────────
def extrair_narrativas(data_ref):
    """Extrai as seções 0, 1, 3 (IPCA, Câmbio, IBC-Br) do .qmd.
    A seção 2 (Selic) é SEMPRE gerada por gerar_secao_selic() — nunca do .qmd."""
    qmd = os.path.join(BASE, f"boletim_{data_ref}.qmd")
    if not os.path.exists(qmd):
        # Tenta o .qmd mais recente disponível
        import glob
        qmds = sorted(glob.glob(os.path.join(BASE, "boletim_*.qmd")))
        if not qmds:
            return {}
        qmd = qmds[-1]
    with open(qmd, encoding="utf-8") as f:
        txt = f.read()
    secoes = {}
    for m in re.finditer(r"### Análise\n\n(.*?)(?=\n###|\n```\{|\Z)", txt, re.DOTALL):
        bloco = m.group(1).strip()
        bloco = re.sub(r"\*\*(.*?)\*\*", r"\1", bloco)
        bloco = re.sub(r"\*(.*?)\*",     r"\1", bloco)
        secoes[len(secoes)] = bloco
    return secoes

# ── Gera narrativas por código — consistência garantida, sem dependência do agente
def gerar_narrativas(r, df_hist):
    """Gera os 3 parágrafos de análise de cada indicador a partir dos dados."""

    ipca_v   = float(r.loc["IPCA",   "valor_atual"])
    ipca_dr  = r.loc["IPCA",   "data_ref"]
    ipca_ano = float(r.loc["IPCA",   "var_ano"])
    ipca_12m = float(r.loc["IPCA",   "var_12m"])

    cambio_v   = float(r.loc["Cambio", "valor_atual"])
    cambio_dr  = r.loc["Cambio", "data_ref"]
    cambio_mes = float(r.loc["Cambio", "var_mes"])
    cambio_ano = float(r.loc["Cambio", "var_ano"])
    cambio_12m = float(r.loc["Cambio", "var_12m"])

    selic_v   = float(r.loc["Selic",  "valor_atual"])

    ibc_v   = float(r.loc["IBC-Br", "valor_atual"])
    ibc_dr  = r.loc["IBC-Br", "data_ref"]
    ibc_mes = float(r.loc["IBC-Br", "var_mes"])
    ibc_ano = float(r.loc["IBC-Br", "var_ano"])
    ibc_12m = float(r.loc["IBC-Br", "var_12m"])

    try:
        meses_pt = ["janeiro","fevereiro","março","abril","maio","junho",
                    "julho","agosto","setembro","outubro","novembro","dezembro"]
        dt = datetime.strptime(ipca_dr, "%Y-%m-%d")
        mes_ipca = f"{meses_pt[dt.month-1]} de {dt.year}"
    except Exception:
        mes_ipca = ipca_dr

    # ── IPCA ──────────────────────────────────────────────────────────────────
    n0 = (
        f"O IPCA registrou variação de {ipca_v:.2f}% em {mes_ipca}, elevando o acumulado "
        f"no ano para {ipca_ano:+.2f}% e a variação em 12 meses para {ipca_12m:.2f}%. "
        f"O resultado {'mantém o acumulado próximo ao teto' if ipca_12m > 4.0 else 'mantém o acumulado dentro'} "
        f"da banda de tolerância da meta de inflação (centro de 3,0%, teto de 4,5%)."
    )
    n1 = (
        f"A dinâmica inflacionária recente reflete pressões em grupos como serviços e alimentos "
        f"no domicílio, em linha com a sazonalidade do período. A apreciação cambial acumulada "
        f"de {cambio_ano:.2f}% no ano contribui para aliviar a transmissão de preços em bens "
        f"industrializados e insumos importados, fator favorável à dinâmica inflacionária no "
        f"horizonte de médio prazo."
    )
    n2 = (
        f"A manutenção da Meta Selic em {selic_v:.2f}% a.a. indica que o Copom avalia que o "
        f"nível de juros ainda é necessário para ancorar as expectativas e conduzir a inflação "
        f"de volta ao centro da meta. A perspectiva para os próximos meses depende do comportamento "
        f"do câmbio e da evolução dos preços de serviços, componente mais resistente ao aperto monetário."
    )

    # ── Câmbio ────────────────────────────────────────────────────────────────
    c0 = (
        f"O dólar encerrou a sessão de {cambio_dr} cotado a R$ {cambio_v:.2f}, acumulando "
        f"variação de {cambio_mes:+.2f}% no mês, {cambio_ano:+.2f}% no ano e {cambio_12m:+.2f}% "
        f"nos últimos 12 meses. "
        f"{'A apreciação do real em 2026 é relevante e reflete o diferencial de juros elevado, a melhora do ambiente fiscal e a redução da aversão global a risco.' if cambio_ano < 0 else 'A depreciação do real reflete incertezas externas e domésticas.'}"
    )
    c1 = (
        f"O movimento cambial pode ser atribuído a um conjunto de fatores externos e domésticos. "
        f"O diferencial de juros entre o Brasil e as economias desenvolvidas permanece elevado, "
        f"atraindo fluxos de capital para ativos de renda fixa brasileiros. A melhora no resultado "
        f"do balanço de pagamentos, impulsionada por exportações de commodities, também contribuiu "
        f"para o equilíbrio do mercado cambial ao longo do período."
    )
    c2 = (
        f"A trajetória do câmbio nos próximos meses é um dos principais determinantes das "
        f"perspectivas inflacionárias. A permanência do dólar "
        f"{'abaixo de R$ 5,50' if cambio_v < 5.5 else 'no patamar atual'} "
        f"seria um elemento {'desinflacionário' if cambio_ano < 0 else 'de pressão'} relevante para "
        f"bens industrializados. O Banco Central tem mantido atuação pontual para evitar "
        f"disfuncionalidades, sem sinalizar um nível-alvo para a taxa."
    )

    # ── IBC-Br ────────────────────────────────────────────────────────────────
    i0 = (
        f"O IBC-Br registrou {ibc_v:.2f} em {ibc_dr} (série dessazonalizada), "
        f"com {'retração' if ibc_mes < 0 else 'expansão'} de {abs(ibc_mes):.2f}% frente ao mês anterior. "
        f"No comparativo interanual, o indicador aponta crescimento de {ibc_12m:.2f}%, e no acumulado "
        f"do ano, {'alta' if ibc_ano > 0 else 'queda'} de {abs(ibc_ano):.2f}% ante o mesmo período do ano anterior."
    )
    i1 = (
        f"O resultado mensal {'negativo' if ibc_mes < 0 else 'positivo'} é compatível com os efeitos "
        f"defasados da política monetária {'restritiva' if selic_v > 10 else 'acomodatícia'}. "
        f"O canal do crédito, principal mecanismo de transmissão da política monetária para a demanda, "
        f"ainda opera com efeitos defasados do ciclo da Selic. "
        f"O mercado de trabalho aquecido e o crédito positivo amparam o consumo das famílias no curto prazo."
    )
    i2 = (
        f"Para os próximos meses, o comportamento do IBC-Br dependerá da velocidade do ciclo de "
        f"{'afrouxamento' if selic_v < 14 else 'aperto'} monetário e de eventuais impulsos fiscais. "
        f"A expansão de {ibc_12m:.2f}% em 12 meses posiciona o Brasil favoravelmente entre os emergentes, "
        f"mas o ritmo de crescimento deve ser monitorado dado o nível "
        f"{'elevado' if selic_v > 10 else 'moderado'} dos juros reais."
    )

    return {
        0: f"{n0}\n\n{n1}\n\n{n2}",
        1: f"{c0}\n\n{c1}\n\n{c2}",
        2: "",  # Selic sempre gerada por gerar_secao_selic()
        3: f"{i0}\n\n{i1}\n\n{i2}",
    }

# ── Classe PDF ────────────────────────────────────────────────────────────────
class BoletimPDF(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_margins(ML, MT, MR)
        self.set_auto_page_break(auto=True, margin=MB)
        # Fontes Unicode (Arial TTF do Windows)
        self.add_font("Arial",  "",  "C:/Windows/Fonts/arial.ttf")
        self.add_font("Arial",  "B", "C:/Windows/Fonts/arialbd.ttf")
        self.add_font("Arial",  "I", "C:/Windows/Fonts/ariali.ttf")
        self.alias_nb_pages()
        self.add_page()

    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Arial", "B", 8)
        self.set_text_color(*CINZA_TXT)
        self.cell(0, 6, f"Boletim Macroeconômico Semanal | {DATA_REF}", align="L")
        self.ln(1)
        self.set_draw_color(*AZUL)
        self.set_line_width(0.3)
        self.line(ML, self.get_y(), A4_W - MR, self.get_y())
        self.ln(3)

    def footer(self):
        self.set_y(-MB + 2)
        self.set_draw_color(*CINZA_TXT)
        self.set_line_width(0.2)
        self.line(ML, self.get_y(), A4_W - MR, self.get_y())
        self.ln(2)
        self.set_font("Arial", "", 7)
        self.set_text_color(*CINZA_TXT)
        self.cell(TW * 0.7, 4,
                  "Raimundo Casé - economista | economistacase@gmail.com  |  Fontes: BCB e IBGE",
                  align="L")
        self.cell(TW * 0.3, 4, f"Pág. {self.page_no()}/{{nb}}", align="R")

    # ── Blocos de conteudo ──────────────────────────────────────────────────
    def capa(self, data_ref):
        # Barra azul topo
        self.set_fill_color(*AZUL)
        self.rect(0, 0, A4_W, 38, "F")
        self.set_y(8)
        self.set_font("Arial", "B", 22)
        self.set_text_color(*BRANCO)
        self.cell(0, 10, "Boletim Macroeconômico Semanal", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Arial", "", 11)
        self.cell(0, 8, f"Semana de referência: {data_ref}", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(14)
        self.set_text_color(*CINZA_TXT)
        self.set_font("Arial", "B", 10)
        self.cell(0, 6, "Raimundo Casé - economista", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def secao_titulo(self, numero, titulo):
        self.ln(4)
        self.set_fill_color(*AZUL)
        self.set_text_color(*BRANCO)
        self.set_font("Arial", "B", 11)
        self.cell(0, 8, f"  {numero}. {titulo}", fill=True,
                  new_x="LMARGIN", new_y="NEXT")
        self.ln(3)

    def sub_titulo(self, txt):
        self.set_text_color(*AZUL)
        self.set_font("Arial", "B", 9)
        self.cell(0, 5, txt, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(*AZUL)
        self.set_line_width(0.2)
        self.line(ML, self.get_y(), ML + TW, self.get_y())
        self.ln(3)
        self.set_text_color(*CINZA_TXT)

    def paragrafo(self, txt):
        self.set_font("Arial", "", 9)
        self.set_text_color(*CINZA_TXT)
        self.multi_cell(TW, 4.5, txt, align="J")
        self.ln(2)

    def inserir_imagem(self, buf):
        x = ML
        w = TW
        h = w * (2.8 / 7.5)  # proporcao do figsize
        if self.get_y() + h + 5 > A4_H - MB:
            self.add_page()
        self.image(buf, x=x, y=self.get_y(), w=w)
        self.ln(h + 2)

    def caption(self, linha1, fonte):
        self.set_fill_color(240, 244, 248)
        self.set_draw_color(*AZUL)
        self.set_line_width(0.5)
        # Barra lateral azul
        self.line(ML, self.get_y(), ML, self.get_y() + 10)
        self.set_x(ML + 3)
        self.set_font("Arial", "B", 8)
        self.set_text_color(50, 50, 50)
        self.multi_cell(TW - 3, 4, linha1)
        self.set_x(ML + 3)
        self.set_font("Arial", "I", 7.5)
        self.set_text_color(*CINZA_TXT)
        self.cell(TW - 3, 4, fonte, new_x="LMARGIN", new_y="NEXT")
        self.ln(4)

    def tabela_resumo(self, df_res):
        self.sub_titulo("Tabela-Resumo dos Indicadores")
        cols  = ["Indicador", "Unidade", "Valor Atual", "Data Ref.",
                 "Var. Mês", "Var. Ano", "Var. 12m"]
        widths = [28, 22, 22, 22, 22, 22, 22]

        # Cabecalho
        self.set_fill_color(*AZUL)
        self.set_text_color(*BRANCO)
        self.set_font("Arial", "B", 8)
        for c, w in zip(cols, widths):
            self.cell(w, 7, c, border=0, fill=True, align="C")
        self.ln()

        # Linhas
        for _, row in df_res.iterrows():
            ind = row["indicador"]
            vm  = float(row["var_mes"])
            va  = float(row["var_ano"])
            v12 = float(row["var_12m"])

            def cor(v):
                if v > 0:   return VERDE_BG
                if v < 0:   return VERM_BG
                return NEUTRO_BG

            def fmt_v(v, ind=None):
                if ind == "Selic":
                    sinal = "+" if v > 0 else ""
                    return f"{sinal}{v:.2f} p.p."
                sinal = "+" if v > 0 else ""
                return f"{sinal}{v:.2f}%"

            # Nome do indicador
            self.set_fill_color(248, 249, 250)
            self.set_text_color(30, 30, 30)
            self.set_font("Arial", "B", 8)
            self.cell(widths[0], 7, ind, border="B", fill=True, align="L")
            self.set_font("Arial", "", 8)
            self.cell(widths[1], 7, str(row["unidade"]), border="B", fill=True, align="C")
            self.cell(widths[2], 7, str(row["valor_atual"]), border="B", fill=True, align="C")
            self.cell(widths[3], 7, str(row["data_ref"]), border="B", fill=True, align="C")

            for v, w in [(vm, widths[4]), (va, widths[5]), (v12, widths[6])]:
                self.set_fill_color(*cor(v))
                self.cell(w, 7, fmt_v(v, ind), border="B", fill=True, align="C")
            self.ln()

        # Fonte
        self.set_font("Arial", "I", 7.5)
        self.set_text_color(*CINZA_TXT)
        self.cell(0, 5,
                  "Fontes: IBGE (IPCA, IBC-Br), Banco Central do Brasil (Selic, Câmbio). Elaboração: Raimundo Casé.",
                  new_x="LMARGIN", new_y="NEXT")
        self.ln(4)

    def sintese(self, df_res):
        self.add_page()
        self.secao_titulo("5", "Síntese e Perspectivas")
        r = df_res.set_index("indicador")
        ipca_12m  = float(r.loc["IPCA",   "var_12m"])
        ipca_ano  = float(r.loc["IPCA",   "var_ano"])
        cambio_va = float(r.loc["Cambio", "valor_atual"])
        cambio_an = float(r.loc["Cambio", "var_ano"])
        selic_v   = float(r.loc["Selic",  "valor_atual"])
        ibc_12m   = float(r.loc["IBC-Br", "var_12m"])
        ibc_mes   = float(r.loc["IBC-Br", "var_mes"])

        self.paragrafo(
            f"Inflação em trajetória de convergência lenta. "
            f"O IPCA acumulado em 12 meses ({ipca_12m:+.2f}%) permanece próximo ao teto da "
            f"meta de 4,5%. O acumulado no ano é de {ipca_ano:+.2f}%. "
            f"A combinação de câmbio apreciado e juros reais elevados cria condições para "
            f"convergência gradual ao centro da meta no segundo semestre."
        )
        self.paragrafo(
            f"Câmbio em apreciação relevante. "
            f"O dólar acumula variação de {cambio_an:+.2f}% no ano, "
            f"com o par BRL/USD cotado a R$ {cambio_va:.2f}. "
            f"O real forte reduz pressões sobre bens industrializados e alimentos importados, "
            f"contribuindo para a desinflação projetada para o próximo semestre. "
            f"A sustentabilidade depende do diferencial de juros e do ambiente externo."
        )
        self.paragrafo(
            f"Política monetária em ciclo descendente cauteloso. "
            f"A Meta Selic em {selic_v:.2f}% a.a. reflete postura cautelosa do Copom, "
            f"que iniciou o ciclo de afrouxamento com passos moderados. "
            f"O ritmo futuro de cortes será condicionado pela trajetória da inflação "
            f"e pelas expectativas de médio prazo."
        )
        self.paragrafo(
            f"Atividade econômica com crescimento moderado. "
            f"O IBC-Br acumula {ibc_12m:+.2f}% em 12 meses, com variação de "
            f"{ibc_mes:+.2f}% no último mês disponível. "
            f"O mercado de trabalho aquecido e o crédito positivo amparam o consumo, "
            f"enquanto o investimento aguarda sinais mais claros de afrouxamento monetário."
        )

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print(f"Gerando {OUT_PDF} ...")

    df_res  = pd.read_csv(RESUMO)
    df_hist = pd.read_csv(HIST)
    df_hist["data"] = pd.to_datetime(df_hist["data"])

    val_selic  = float(df_res.loc[df_res["indicador"] == "Selic", "valor_atual"].iloc[0])
    r_idx      = df_res.set_index("indicador")

    # Todas as narrativas geradas por código — consistência garantida toda semana
    narrativas = gerar_narrativas(r_idx, df_hist)
    narrativas[2] = gerar_secao_selic(df_hist, r_idx)

    pdf = BoletimPDF()
    pdf.capa(DATA_REF)

    # Panorama geral
    pdf.sub_titulo("Panorama Geral")
    r = df_res.set_index("indicador")
    pdf.paragrafo(
        f"O Boletim Macro desta semana consolida as leituras mais recentes dos principais "
        f"indicadores da economia brasileira. O IPCA de abril registrou variação de "
        f"{float(r.loc['IPCA','valor_atual']):.2f}% no mês, com acumulado em 12 meses de "
        f"{float(r.loc['IPCA','var_12m']):.2f}%. "
        f"A Meta Selic permanece em {float(r.loc['Selic','valor_atual']):.2f}% a.a. "
        f"O câmbio encerrou em R$ {float(r.loc['Cambio','valor_atual']):.2f}/USD, "
        f"acumulando {float(r.loc['Cambio','var_ano']):+.2f}% no ano. "
        f"O IBC-Br registrou {float(r.loc['IBC-Br','var_mes']):+.2f}% na margem, "
        f"com crescimento de {float(r.loc['IBC-Br','var_12m']):.2f}% em 12 meses."
    )
    pdf.ln(2)
    pdf.tabela_resumo(df_res)

    # ── 4 Secoes ──
    secoes_cfg = [
        ("1", "Inflação — IPCA",
         chart_ipca(df_hist),
         f"IPCA: {float(r.loc['IPCA','valor_atual']):.2f}%  em {r.loc['IPCA','data_ref']}  |  "
         f"Acum. ano: {float(r.loc['IPCA','var_ano']):+.2f}%  |  "
         f"Acum. 12m: {float(r.loc['IPCA','var_12m']):+.2f}%",
         "Fonte: IBGE — Sistema Nacional de Índices de Preços ao Consumidor (SNIPC)."),
        ("2", "Câmbio — BRL/USD",
         chart_cambio(df_hist),
         f"Câmbio: R$ {float(r.loc['Cambio','valor_atual']):.2f}/USD em {r.loc['Cambio','data_ref']}  |  "
         f"Var. mês: {float(r.loc['Cambio','var_mes']):+.2f}%  |  "
         f"Var. ano: {float(r.loc['Cambio','var_ano']):+.2f}%  |  "
         f"Var. 12m: {float(r.loc['Cambio','var_12m']):+.2f}%",
         "Fonte: Banco Central do Brasil — PTAX (taxa de câmbio de referência)."),
        ("3", "Política Monetária — Meta Selic",
         chart_selic(df_hist, val_selic),
         f"Meta Selic: {val_selic:.2f}% a.a. em {r.loc['Selic','data_ref']}  |  "
         f"Var. mês: {float(r.loc['Selic','var_mes']):+.2f} p.p.  |  "
         f"Var. ano: {float(r.loc['Selic','var_ano']):+.2f} p.p.  |  "
         f"Var. 12m: {float(r.loc['Selic','var_12m']):+.2f} p.p.",
         "Fonte: Banco Central do Brasil — Comitê de Política Monetária (Copom)."),
        ("4", "Atividade Econômica — IBC-Br",
         chart_ibc(df_hist),
         f"IBC-Br (dessaz.): {float(r.loc['IBC-Br','valor_atual']):.2f} em {r.loc['IBC-Br','data_ref']}  |  "
         f"Var. mês: {float(r.loc['IBC-Br','var_mes']):+.2f}%  |  "
         f"Var. ano: {float(r.loc['IBC-Br','var_ano']):+.2f}%  |  "
         f"Var. 12m: {float(r.loc['IBC-Br','var_12m']):+.2f}%",
         "Fonte: Banco Central do Brasil — Índice de Atividade Econômica (IBC-Br)."),
    ]

    for idx, (num, titulo, chart_buf, cap1, cap_fonte) in enumerate(secoes_cfg):
        pdf.add_page()
        pdf.secao_titulo(num, titulo)
        pdf.sub_titulo("Análise")
        texto = narrativas.get(idx, "")
        if texto:
            for par in texto.split("\n\n"):
                par = par.strip()
                if par:
                    pdf.paragrafo(par)
        pdf.sub_titulo("Gráfico")
        pdf.inserir_imagem(chart_buf)
        pdf.caption(cap1, cap_fonte)

    pdf.sintese(df_res)
    pdf.output(OUT_PDF)
    size_kb = os.path.getsize(OUT_PDF) // 1024
    print(f"PDF gerado: {OUT_PDF} ({size_kb} KB)")


if __name__ == "__main__":
    main()
