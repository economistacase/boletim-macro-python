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

# ── Extrai narrativas do .qmd (fonte primaria) ───────────────────────────────
def extrair_narrativas(data_ref, val_selic=None):
    qmd = os.path.join(BASE, f"boletim_{data_ref}.qmd")
    if not os.path.exists(qmd):
        return {}
    with open(qmd, encoding="utf-8") as f:
        txt = f.read()
    secoes = {}
    for m in re.finditer(r"### Análise\n\n(.*?)(?=\n###|\n```\{|\Z)", txt, re.DOTALL):
        bloco = m.group(1).strip()
        bloco = re.sub(r"\*\*(.*?)\*\*", r"\1", bloco)
        bloco = re.sub(r"\*(.*?)\*",     r"\1", bloco)
        secoes[len(secoes)] = bloco
    if val_selic is not None and 2 in secoes:
        paragrafos = secoes[2].split("\n\n")
        if paragrafos:
            paragrafos[0] = re.sub(
                r"\d{1,2}[,\.]\d{2,6}%\s*(?:ao\s+ano|a\.a\.)",
                f"{val_selic:.2f}% a.a.",
                paragrafos[0], flags=re.IGNORECASE
            )
            secoes[2] = "\n\n".join(paragrafos)
    return secoes

# ── Gera narrativas diretamente dos dados (fallback sem .qmd) ─────────────────
def gerar_narrativas(r, df_hist):
    """Gera os 3 paragrafos de analise de cada indicador a partir do resumo.csv."""

    ipca_v   = float(r.loc["IPCA",   "valor_atual"])
    ipca_dr  = r.loc["IPCA",   "data_ref"]
    ipca_mes = float(r.loc["IPCA",   "var_mes"])
    ipca_ano = float(r.loc["IPCA",   "var_ano"])
    ipca_12m = float(r.loc["IPCA",   "var_12m"])

    cambio_v   = float(r.loc["Cambio", "valor_atual"])
    cambio_dr  = r.loc["Cambio", "data_ref"]
    cambio_mes = float(r.loc["Cambio", "var_mes"])
    cambio_ano = float(r.loc["Cambio", "var_ano"])
    cambio_12m = float(r.loc["Cambio", "var_12m"])

    selic_v   = float(r.loc["Selic",  "valor_atual"])
    selic_dr  = r.loc["Selic",  "data_ref"]
    selic_mes = float(r.loc["Selic",  "var_mes"])
    selic_ano = float(r.loc["Selic",  "var_ano"])
    selic_12m = float(r.loc["Selic",  "var_12m"])

    ibc_v   = float(r.loc["IBC-Br", "valor_atual"])
    ibc_dr  = r.loc["IBC-Br", "data_ref"]
    ibc_mes = float(r.loc["IBC-Br", "var_mes"])
    ibc_ano = float(r.loc["IBC-Br", "var_ano"])
    ibc_12m = float(r.loc["IBC-Br", "var_12m"])

    # Mes de referencia do IPCA
    try:
        mes_ref = datetime.strptime(ipca_dr, "%Y-%m-%d").strftime("%B/%Y")
    except Exception:
        mes_ref = ipca_dr

    # Narrativa IPCA
    n0 = (
        f"O IPCA registrou variacao de {ipca_v:.2f}% em {mes_ref}, elevando o acumulado no ano "
        f"para {ipca_ano:+.2f}% e a variacao em 12 meses para {ipca_12m:.2f}%. O resultado "
        f"{'representa aceleracao' if ipca_mes > 0.5 else 'representa desaceleracao'} em relacao "
        f"ao padrao recente e se mantem {'proximo ao teto' if ipca_12m > 4.0 else 'dentro'} "
        f"da banda de tolerancia da meta de inflacao (centro de 3,0%, teto de 4,5%)."
    )
    n1 = (
        f"A dinamica inflacionaria recente reflete pressoes em grupos como servicos e alimentos "
        f"no domicilio, em linha com a sazonalidade do periodo. A apreciacao cambial acumulada "
        f"de {cambio_ano:.2f}% no ano contribui para aliviar a transmissao de precos em bens "
        f"industrializados e insumos importados, fator favoravel a dinamica inflacionaria no "
        f"horizonte de medio prazo."
    )
    n2 = (
        f"A manutencao da Meta Selic em {selic_v:.2f}% a.a. indica que o Copom avalia que o "
        f"nivel de juros ainda e necessario para ancorar as expectativas e conduzir a inflacao "
        f"de volta ao centro da meta. A perspectiva para os proximos meses depende do comportamento "
        f"do cambio e da evolucao dos precos de servicos, componente mais resistente ao aperto monetario."
    )

    # Narrativa Cambio
    c0 = (
        f"O dolar encerrou a sessao de {cambio_dr} cotado a R$ {cambio_v:.2f}, acumulando "
        f"variacao de {cambio_mes:+.2f}% no mes, {cambio_ano:+.2f}% no ano e {cambio_12m:+.2f}% "
        f"nos ultimos 12 meses. "
        f"{'A apreciacao do real em 2026 e relevante e reflete o diferencial de juros elevado, melhora do ambiente fiscal e reducao da aversao global a risco.' if cambio_ano < 0 else 'A depreciacao do real reflete incertezas externas e domesticas.'}"
    )
    c1 = (
        f"O movimento cambial pode ser atribuido a um conjunto de fatores externos e domesticos. "
        f"O diferencial de juros entre o Brasil e as economias desenvolvidas permanece elevado, "
        f"atraindo fluxos de capital para ativos de renda fixa brasileiros. A melhora no resultado "
        f"do balanco de pagamentos, impulsionada por exportacoes de commodities, tambem contribuiu "
        f"para o equilibrio do mercado cambial ao longo do periodo."
    )
    c2 = (
        f"A trajetoria do cambio nos proximos meses e um dos principais determinantes das "
        f"perspectivas inflacionarias. A permanencia do dolar {'abaixo de R$ 5,50' if cambio_v < 5.5 else 'no patamar atual'} "
        f"seria um elemento {'desinflacionario' if cambio_ano < 0 else 'de pressao'} relevante para "
        f"bens industrializados. O Banco Central tem mantido atuacao pontual para evitar "
        f"disfuncionalidades, sem sinalizar um nivel-alvo para a taxa."
    )

    # Narrativa Selic
    s0 = (
        f"A Meta Selic esta fixada em {selic_v:.2f}% a.a. ({selic_dr}), "
        f"{'sem alteracao no mes corrente' if selic_mes == 0 else f'com variacao de {selic_mes:+.2f} p.p. no mes'}. "
        f"No acumulado do ano, a taxa variou {selic_ano:+.2f} p.p. e nos ultimos 12 meses {selic_12m:+.2f} p.p., "
        f"{'indicando inicio de ciclo de afrouxamento' if selic_ano < 0 else 'indicando postura de aperto monetario'} "
        f"pelo Comite de Politica Monetaria (Copom)."
    )
    s1 = (
        f"O Copom calibra o ritmo do ciclo monetario com base na trajetoria da inflacao corrente "
        f"e nas expectativas de medio prazo. O diferencial de juros reais do Brasil em relacao "
        f"aos pares emergentes permanece elevado, o que favorece a atracao de capital externo e "
        f"contribui para a estabilidade cambial. A conducao da politica fiscal sera determinante "
        f"para o espaco de cortes adicionais na Selic."
    )
    s2 = (
        f"O ritmo de {'cortes' if selic_ano < 0 else 'altas'} futuros dependerá da velocidade "
        f"com que a inflacao corrente e as expectativas se aproximem do centro da meta de 3,0%. "
        f"Um cenario de convergencia mais rapida permitiria {'acelerar os cortes' if selic_ano < 0 else 'pausar o ciclo'}, "
        f"mas qualquer deterioracao cambial ou fiscal tenderia a alterar essa trajetoria."
    )

    # Narrativa IBC-Br
    i0 = (
        f"O IBC-Br registrou {ibc_v:.2f} em {ibc_dr} (serie dessazonalizada), "
        f"com {'retração' if ibc_mes < 0 else 'expansão'} de {abs(ibc_mes):.2f}% frente ao mes anterior. "
        f"No comparativo interanual, o indicador aponta crescimento de {ibc_12m:.2f}%, e no acumulado "
        f"do ano, {'alta' if ibc_ano > 0 else 'queda'} de {abs(ibc_ano):.2f}% ante o mesmo periodo do ano anterior."
    )
    i1 = (
        f"O resultado mensal {'negativo' if ibc_mes < 0 else 'positivo'} e compativel com os efeitos "
        f"defasados da politica monetaria {'restritiva' if selic_v > 10 else 'acomodaticia'}. "
        f"O canal do credito, principal mecanismo de transmissao da politica monetaria para a demanda, "
        f"ainda opera com efeitos defasados do ciclo {'de alta' if selic_ano < 0 else 'de cortes'} da Selic. "
        f"O mercado de trabalho aquecido e o credito positivo amparam o consumo das familias no curto prazo."
    )
    i2 = (
        f"Para os proximos meses, o comportamento do IBC-Br dependera da velocidade do ciclo de "
        f"{'afrouxamento' if selic_ano < 0 else 'aperto'} monetario e de eventuais impulsos fiscais. "
        f"A expansao de {ibc_12m:.2f}% em 12 meses posiciona o Brasil favoravelmente entre os emergentes, "
        f"mas o ritmo de crescimento deve ser monitorado dado o nivel {'elevado' if selic_v > 10 else 'moderado'} "
        f"dos juros reais."
    )

    return {
        0: f"{n0}\n\n{n1}\n\n{n2}",
        1: f"{c0}\n\n{c1}\n\n{c2}",
        2: f"{s0}\n\n{s1}\n\n{s2}",
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

    # Tenta extrair narrativa do .qmd (fonte primaria — texto rico com acentuacao correta).
    # Se o .qmd da data exata nao existir, busca o mais recente disponivel.
    narrativas = extrair_narrativas(DATA_REF, val_selic=val_selic)
    if not narrativas:
        import glob
        qmds = sorted(glob.glob(os.path.join(BASE, "boletim_*.qmd")))
        if qmds:
            data_alternativa = os.path.basename(qmds[-1]).replace("boletim_", "").replace(".qmd", "")
            narrativas = extrair_narrativas(data_alternativa, val_selic=val_selic)
    if not narrativas:
        narrativas = gerar_narrativas(r_idx, df_hist)

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
