"""
Coleta dados macroeconômicos do BCB (api.bcb.gov.br) e IBGE.
Gera 5 arquivos CSV em output/dados/:
  - ipca.csv         (IPCA mensal - BCB série 433)
  - cambio.csv       (USD/BRL diário - BCB série 1)
  - selic.csv        (Meta Selic - BCB série 432)
  - ibcbr_orig.csv   (IBC-Br original - BCB série 24363)
  - ibcbr_sa.csv     (IBC-Br dessaz. - BCB série 24364)
"""

import sys
import urllib.request
import json
import csv
import os
from datetime import datetime, timedelta

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output", "dados")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def fetch_bcb(serie_id: int, data_inicio: str, data_fim: str) -> list[dict]:
    """Busca série temporal do BCB SGS."""
    url = (
        f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{serie_id}/dados"
        f"?formato=json&dataInicial={data_inicio}&dataFinal={data_fim}"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "BoletimMacro/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"  AVISO: Falha ao buscar série {serie_id}: {e}", file=sys.stderr)
        return []


def save_csv(rows: list[dict], filename: str, fieldnames: list[str]):
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  Salvo: {path} ({len(rows)} linhas)")
    return path


def main():
    today = datetime.today()
    start_7y = (today - timedelta(days=365 * 7)).strftime("%d/%m/%Y")
    start_5y = (today - timedelta(days=365 * 5 + 2)).strftime("%d/%m/%Y")
    end = today.strftime("%d/%m/%Y")

    print(f"Periodo de coleta: {start_5y} ate {end}")
    print()

    # --- IPCA (série 433 — variação % mensal) ---
    print("Coletando IPCA (série 433)...")
    ipca_data = fetch_bcb(433, start_7y, end)
    if ipca_data:
        save_csv(ipca_data, "ipca.csv", ["data", "valor"])
    else:
        print("  AVISO: IPCA sem dados.", file=sys.stderr)

    # --- Câmbio (série 1 — R$/US$ diário, PTAX venda) ---
    print("Coletando Câmbio USD/BRL (série 1)...")
    cambio_data = fetch_bcb(1, start_5y, end)
    if cambio_data:
        save_csv(cambio_data, "cambio.csv", ["data", "valor"])
    else:
        print("  AVISO: Câmbio sem dados.", file=sys.stderr)

    # --- Meta Selic (série 432 — Meta definida pelo Copom) ---
    print("Coletando Meta Selic (série 432)...")
    selic_data = fetch_bcb(432, start_5y, end)
    if selic_data:
        save_csv(selic_data, "selic.csv", ["data", "valor"])
    else:
        print("  AVISO: Meta Selic sem dados.", file=sys.stderr)

    # --- IBC-Br original (série 24363) ---
    print("Coletando IBC-Br original (série 24363)...")
    ibcbr_orig = fetch_bcb(24363, start_7y, end)
    if ibcbr_orig:
        save_csv(ibcbr_orig, "ibcbr_orig.csv", ["data", "valor"])
    else:
        print("  AVISO: IBC-Br original sem dados.", file=sys.stderr)

    # --- IBC-Br dessaz. (série 24364) ---
    print("Coletando IBC-Br dessaz. (série 24364)...")
    ibcbr_sa = fetch_bcb(24364, start_7y, end)
    if ibcbr_sa:
        save_csv(ibcbr_sa, "ibcbr_sa.csv", ["data", "valor"])
    else:
        print("  AVISO: IBC-Br dessaz. sem dados.", file=sys.stderr)

    # Validação final
    expected = ["ipca.csv", "cambio.csv", "selic.csv", "ibcbr_orig.csv", "ibcbr_sa.csv"]
    missing = [f for f in expected if not os.path.exists(os.path.join(OUTPUT_DIR, f))]
    if missing:
        print(f"\nERRO: Arquivos ausentes: {missing}", file=sys.stderr)
        sys.exit(1)
    else:
        print("\n5 arquivos coletados com sucesso em output/dados/")


if __name__ == "__main__":
    main()
