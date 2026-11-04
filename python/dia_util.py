"""Decide se o boletim deve ser gerado na data informada.

Regra: gera no primeiro dia útil da semana em que a geração **der certo**.
A janela vai de segunda a quinta; dentro dela, o boletim é gerado em qualquer
dia útil enquanto ainda não houver boletim publicado naquela semana. Assim:

- feriado na segunda  -> roda na terça (o Focus do Bacen também é adiado);
- segunda falhou      -> a terça tenta de novo, e assim até quinta;
- segunda deu certo   -> terça a quinta não rodam (nem gastam tokens).

O que delimita "já publicado nesta semana" é a data do último boletim, passada
em `--ultimo-boletim`. Sem esse argumento, cai na regra conservadora antiga
(somente o 1º dia útil da semana), para que uma falha ao descobrir essa data
nunca resulte em execução diária.

Uso:
    python dia_util.py [AAAA-MM-DD] [--ultimo-boletim AAAA-MM-DD]
Imprime "true" ou "false".
Somente biblioteca padrão (roda antes de instalar dependências).
"""
import sys
from datetime import date, timedelta

# Último dia da semana em que o boletim pode ser gerado (0=segunda ... 3=quinta).
# Depois disso o boletim seria tarde demais para a semana de referência.
ULTIMO_DIA_DA_JANELA = 3


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


def segunda_da_semana(d: date) -> date:
    return d - timedelta(days=d.weekday())


def primeiro_dia_util_da_semana(d: date) -> bool:
    """Regra conservadora: nenhum dia útil antes de `d` na mesma semana."""
    segunda = segunda_da_semana(d)
    anteriores = (segunda + timedelta(days=i) for i in range(d.weekday()))
    return not any(dia_util(x) for x in anteriores)


def deve_gerar(d: date, ultimo_boletim: date | None = None) -> bool:
    if not dia_util(d):
        return False
    if d.weekday() > ULTIMO_DIA_DA_JANELA:
        return False
    if ultimo_boletim is None:
        # Não sabemos se a semana já tem boletim: só o 1º dia útil roda.
        return primeiro_dia_util_da_semana(d)
    # Já existe boletim desta semana? Então nada a fazer.
    return ultimo_boletim < segunda_da_semana(d)


def _parse_args(argv: list[str]) -> tuple[date, date | None]:
    ref: date | None = None
    ultimo: date | None = None
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--ultimo-boletim":
            bruto = argv[i + 1] if i + 1 < len(argv) else ""
            if bruto:
                try:
                    ultimo = date.fromisoformat(bruto)
                except ValueError:
                    # Data ilegível: segue sem ela e cai na regra conservadora.
                    print(
                        f"AVISO: --ultimo-boletim ilegivel ({bruto!r}); "
                        "usando a regra do 1o dia util da semana.",
                        file=sys.stderr,
                    )
            i += 2
            continue
        if a and ref is None:
            ref = date.fromisoformat(a)
        i += 1
    return (ref or date.today(), ultimo)


if __name__ == "__main__":
    ref, ultimo = _parse_args(sys.argv[1:])
    print("true" if deve_gerar(ref, ultimo) else "false")
