"""Decompõe a variação do real entre dólar global e resíduo.

Gera `output/tabelas/contexto_cambio.md` com fatos já calculados, no mesmo
formato do `contexto.md`, para o redator citar sem fazer contas.

Método
------
O serviço PTAX do Banco Central publica, para dez moedas, a cotação em reais e
a `paridadeVenda` contra o dólar. Seis dessas moedas são as que compõem o índice
do dólar de referência de mercado (EUR, JPY, GBP, CAD, SEK, CHF), com os pesos
abaixo. Com elas monta-se um índice de força do dólar — média geométrica
ponderada das paridades, normalizadas no sentido "unidades da moeda por dólar",
de modo que o índice sobe quando o dólar se fortalece.

Comparando a variação do real por dólar com a variação desse índice, separa-se
o que é movimento global do dólar do que não é.

LIMITE IMPORTANTE, que o redator é obrigado a respeitar: o resíduo é "o que não
é explicado pelo dólar global", e NADA além disso. Não é componente doméstico.
A cesta é de moedas de mercados desenvolvidos — o BCB não publica paridades de
emergentes — logo uma aversão a risco que atinja emergentes em bloco apareceria
no resíduo sem ter nada de brasileira. Chamar o resíduo de "doméstico" é
afirmação não sustentada pelos dados.

Fonte única: Banco Central do Brasil (PTAX). Somente biblioteca padrão.
"""

import json
import os
import sys
import time
import urllib.request
from datetime import date, datetime, timedelta

BASE = "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata"
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TABELAS_DIR = os.path.join(RAIZ, "output", "tabelas")

# Moeda -> (tipo PTAX, peso no índice do dólar)
#   tipo A: paridadeVenda = unidades da moeda por dólar
#   tipo B: paridadeVenda = dólares por unidade da moeda (precisa inverter)
CESTA = {
    "EUR": ("B", 0.576),
    "JPY": ("A", 0.136),
    "GBP": ("B", 0.119),
    "CAD": ("A", 0.091),
    "SEK": ("A", 0.042),
    "CHF": ("A", 0.036),
}

DIAS_JANELA = 500
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
         "agosto", "setembro", "outubro", "novembro", "dezembro"]


def fmt(v, casas=2):
    return f"{v:.{casas}f}".replace(".", ",")


def mes_ano(d):
    return f"{MESES[d.month - 1]}/{d.year}"


def dia_mes_ano(d):
    return f"{d.day:02d}/{d.month:02d}/{d.year}"


def buscar(url):
    """GET com retentativa: a API do BCB tem instabilidade esporádica."""
    req = urllib.request.Request(url, headers={"User-Agent": "BoletimMacro/1.0"})
    for tentativa in range(1, 5):
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            print(f"  AVISO: falha na consulta (tentativa {tentativa}/4): {e}", file=sys.stderr)
            if tentativa < 4:
                time.sleep(15 * tentativa)
    return None


def fechamentos(simbolo, d_ini, d_fim):
    """Cotações de fechamento de `simbolo`. Devolve {data_iso: (brl, paridade)}."""
    url = (
        f"{BASE}/CotacaoMoedaPeriodo(moeda=@moeda,dataInicial=@dataInicial,"
        f"dataFinalCotacao=@dataFinalCotacao)"
        f"?@moeda='{simbolo}'"
        f"&@dataInicial='{d_ini.strftime('%m-%d-%Y')}'"
        f"&@dataFinalCotacao='{d_fim.strftime('%m-%d-%Y')}'"
        f"&$top=10000&$format=json"
    )
    d = buscar(url)
    if d is None:
        return None
    out = {}
    for x in d.get("value", []):
        if x.get("tipoBoletim") != "Fechamento":
            continue
        try:
            out[x["dataHoraCotacao"][:10]] = (
                float(x["cotacaoVenda"]),
                float(x["paridadeVenda"]),
            )
        except (KeyError, TypeError, ValueError):
            continue
    return out


def var_pct(novo, antigo):
    return (novo / antigo - 1.0) * 100.0


def main():
    hoje = date.today()
    d_ini = hoje - timedelta(days=DIAS_JANELA)
    print(f"Janela: {d_ini} a {hoje}")

    # --- dólar/real ---
    print("Coletando USD (PTAX)...")
    usd = fechamentos("USD", d_ini, hoje)
    if not usd:
        print("ERRO: sem cotações de fechamento do dólar.", file=sys.stderr)
        return 1
    brl = {k: v[0] for k, v in usd.items()}

    # --- paridades da cesta ---
    paridades = {}
    for simbolo, (tipo, _) in CESTA.items():
        print(f"Coletando {simbolo} (paridade)...")
        d = fechamentos(simbolo, d_ini, hoje)
        if not d:
            print(f"ERRO: sem paridade para {simbolo}.", file=sys.stderr)
            return 1
        # normaliza para "unidades da moeda por dólar"
        paridades[simbolo] = {
            k: (p if tipo == "A" else 1.0 / p) for k, (_, p) in d.items() if p > 0
        }

    # --- datas com dado completo em todas as séries ---
    comuns = set(brl)
    for d in paridades.values():
        comuns &= set(d)
    datas = sorted(comuns)
    if len(datas) < 30:
        print(f"ERRO: apenas {len(datas)} datas completas na janela.", file=sys.stderr)
        return 1
    print(f"{len(datas)} datas com dado completo em todas as 7 séries.")

    def indice(dt):
        v = 1.0
        for simbolo, (_, peso) in CESTA.items():
            v *= paridades[simbolo][dt] ** peso
        return v

    ref = datas[-1]
    ref_d = datetime.strptime(ref, "%Y-%m-%d").date()

    def ancora(cond, rotulo):
        """Última data da janela que satisfaz `cond`, ou None."""
        for dt in reversed(datas[:-1]):
            if cond(datetime.strptime(dt, "%Y-%m-%d").date()):
                return dt, rotulo
        return None, rotulo

    # fechamento do mês anterior ao de referência
    a_mes, _ = ancora(lambda d: (d.year, d.month) != (ref_d.year, ref_d.month), "mês")
    # último fechamento de dezembro do ano anterior
    a_ano, _ = ancora(lambda d: d.year < ref_d.year and d.month == 12, "ano")
    # último fechamento do mesmo mês, um ano antes
    a_12m, _ = ancora(
        lambda d: (d.year, d.month) == (ref_d.year - 1, ref_d.month), "12 meses"
    )

    linhas = [
        "# Decomposição da variação do real: dólar global e resíduo",
        "",
        "Fonte: Banco Central do Brasil (PTAX). Índice de força do dólar calculado",
        "como média geométrica ponderada das paridades de EUR (57,6%), JPY (13,6%),",
        "GBP (11,9%), CAD (9,1%), SEK (4,2%) e CHF (3,6%) contra o dólar.",
        "",
        f"Data de referência: **{dia_mes_ano(ref_d)}**, com o real a "
        f"**R$ {fmt(brl[ref], 4)}** por dólar.",
        "",
        "## Limite de interpretação (obrigatório)",
        "",
        "O resíduo abaixo é **o que não é explicado pelo dólar global**, e nada mais.",
        "**Não** é componente doméstico: a cesta é de moedas de mercados",
        "desenvolvidos, porque o BCB não publica paridades de emergentes. Uma",
        "aversão a risco que atinja emergentes em bloco apareceria no resíduo sem",
        "ter nada de brasileira. Escrever que o resíduo é \"doméstico\", \"interno\"",
        "ou equivalente não é sustentado por estes dados.",
        "",
        "## Variações até a data de referência",
        "",
        "| Janela | Partida | Real por dólar | Índice do dólar | Resíduo |",
        "|---|---|---|---|---|",
    ]

    fatos = []
    for anc, rotulo in [(a_mes, "No mês"), (a_ano, "No ano"), (a_12m, "Em 12 meses")]:
        if anc is None:
            linhas.append(f"| {rotulo} | sem dado na janela | — | — | — |")
            continue
        d0 = datetime.strptime(anc, "%Y-%m-%d").date()
        v_brl = var_pct(brl[ref], brl[anc])
        v_dol = var_pct(indice(ref), indice(anc))
        resid = v_brl - v_dol
        linhas.append(
            f"| {rotulo} | {dia_mes_ano(d0)} (R$ {fmt(brl[anc], 4)}) "
            f"| {fmt(v_brl)}% | {fmt(v_dol)}% | {fmt(resid)} p.p. |"
        )
        fatos.append((rotulo, d0, v_brl, v_dol, resid))

    linhas += ["", "## Leitura de cada janela", ""]
    for rotulo, d0, v_brl, v_dol, resid in fatos:
        dir_brl = "desvalorizou" if v_brl > 0 else "valorizou"
        dir_dol = "fortaleceu" if v_dol > 0 else "enfraqueceu"
        # O resíduo tem o mesmo sinal da desvalorização quando excede o global.
        if abs(resid) < 0.1:
            juizo = (
                "o movimento do real foi praticamente todo explicado pelo dólar global"
            )
        elif (v_brl > 0) == (resid > 0):
            juizo = (
                f"o real {dir_brl} **{fmt(abs(resid))} p.p. além** do que o dólar "
                f"global explicaria"
            )
        else:
            juizo = (
                f"o real {dir_brl} **{fmt(abs(resid))} p.p. menos** do que o dólar "
                f"global explicaria"
            )
        linhas.append(
            f"- **{rotulo}** (desde {dia_mes_ano(d0)}, {mes_ano(d0)}): o real "
            f"**{dir_brl} {fmt(abs(v_brl))}%** e o dólar global **{dir_dol} "
            f"{fmt(abs(v_dol))}%**, de modo que {juizo}."
        )

    os.makedirs(TABELAS_DIR, exist_ok=True)
    destino = os.path.join(TABELAS_DIR, "contexto_cambio.md")
    with open(destino, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas) + "\n")
    print(f"Gravado: {destino}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
