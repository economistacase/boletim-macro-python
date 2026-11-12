"""Descobre se o IPCA ganhou mês novo desde o último boletim.

O boletim é semanal, mas o IPCA é mensal e sai em dia variável (o IBGE divulgou
em 12/11 em novembro/2026). Sem este gatilho, um boletim gerado na segunda fica
com o mês anterior até a segunda seguinte — e, como o Painel IPCA do mesmo autor
atualiza no dia da divulgação, os dois produtos assinados passam dias dizendo
coisas diferentes sobre a inflação corrente.

Mesmo padrão do workflow do `relatorio-ipca`: consulta barata à série 433,
compara com o mês registrado em `referencia_ipca.txt` e devolve se mudou.

Uso:
    python ipca_referencia.py referencia_ipca.txt
        -> imprime, em formato key=value para o GITHUB_OUTPUT:
             ipca_atual=AAAA-MM
             ipca_novo=true|false

    python ipca_referencia.py --valor
        -> imprime apenas AAAA-MM (para gravar o arquivo após publicar)

Avisos vão para stderr, nunca para stdout, que é consumido pelo workflow.
Somente biblioteca padrão.
"""

import json
import os
import sys
import time
import urllib.request

URL = ("https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados/ultimos/1"
       "?formato=json")


def mes_publicado():
    """Mês de referência do último IPCA na série 433, como 'AAAA-MM'."""
    req = urllib.request.Request(URL, headers={"User-Agent": "BoletimMacro/1.0"})
    for tentativa in range(1, 4):
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                d = json.loads(r.read().decode("utf-8"))
            # A API devolve a data como "01/10/2026" (dd/mm/aaaa)
            dia, mes, ano = d[0]["data"].split("/")
            return f"{ano}-{mes}"
        except Exception as e:
            print(f"AVISO: consulta à série 433 falhou "
                  f"(tentativa {tentativa}/3): {e}", file=sys.stderr)
            if tentativa < 3:
                time.sleep(10 * tentativa)
    return None


def main(argv):
    if "--valor" in argv:
        atual = mes_publicado()
        if atual is None:
            return 1
        print(atual)
        return 0

    caminho = argv[0] if argv else "referencia_ipca.txt"
    atual = mes_publicado()

    if atual is None:
        # Indisponibilidade da API não pode disparar nem travar o boletim:
        # a regra semanal segue valendo por conta própria.
        print("ipca_atual=")
        print("ipca_novo=false")
        print("AVISO: sem resposta da API; o gatilho do IPCA fica inativo "
              "nesta rodada e vale apenas a regra semanal.", file=sys.stderr)
        return 0

    anterior = ""
    if os.path.exists(caminho):
        try:
            with open(caminho, encoding="utf-8") as f:
                anterior = f.read().strip()
        except OSError as e:
            print(f"AVISO: não foi possível ler {caminho}: {e}", file=sys.stderr)

    novo = atual != anterior
    print(f"ipca_atual={atual}")
    print(f"ipca_novo={'true' if novo else 'false'}")
    print(f"IPCA publicado: {atual} | registrado no repositório: "
          f"{anterior or '(nenhum)'} | mês novo: {novo}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
