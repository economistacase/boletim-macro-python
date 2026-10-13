"""Decide se o boletim deve ser gerado na data informada.

Regra: gera apenas no PRIMEIRO dia útil da semana (seg, ou ter/qua quando a
segunda — e a terça, no Carnaval — forem feriados). Assim, quando o Banco
Central adia o Focus por feriado, o workflow não roda (nem gasta tokens) no
feriado e roda no dia útil seguinte.

Uso: python dia_util.py [AAAA-MM-DD]   -> imprime "true" ou "false"
Somente biblioteca padrão (roda antes de instalar dependências).
"""
import sys
from datetime import date, timedelta


def pascoa(ano: int) -> date:
    # Algoritmo de Meeus/Jones/Butcher (calendário gregoriano)
    a = ano % 19
    b, c = divmod(ano, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mes = (h + l - 7 * m + 114) // 31
    dia = (h + l - 7 * m + 114) % 31 + 1
    return date(ano, mes, dia)


def feriados(ano: int) -> set[date]:
    """Feriados nacionais + dias sem expediente bancário (calendário ANBIMA)."""
    fixos = [(1, 1), (4, 21), (5, 1), (9, 7), (10, 12), (11, 2), (11, 15), (11, 20), (12, 25)]
    p = pascoa(ano)
    moveis = [
        p - timedelta(days=48),  # segunda de Carnaval
        p - timedelta(days=47),  # terça de Carnaval
        p - timedelta(days=2),   # Sexta-feira Santa
        p + timedelta(days=60),  # Corpus Christi
    ]
    return {date(ano, m, d) for m, d in fixos} | set(moveis)


def dia_util(d: date) -> bool:
    return d.weekday() < 5 and d not in feriados(d.year)


def deve_gerar(d: date) -> bool:
    if not dia_util(d):
        return False
    segunda = d - timedelta(days=d.weekday())
    anteriores = (segunda + timedelta(days=i) for i in range(d.weekday()))
    return not any(dia_util(x) for x in anteriores)


if __name__ == "__main__":
    ref = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1] else date.today()
    print("true" if deve_gerar(ref) else "false")
