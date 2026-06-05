"""
Uso: python python/registrar_erro.py "agente" "mensagem de erro"
Append-only em logs/erros.md. Chamado pelos agentes quando algo falha.
"""
import sys
import os
from datetime import datetime, timezone

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG  = os.path.join(BASE, "logs", "erros.md")
os.makedirs(os.path.join(BASE, "logs"), exist_ok=True)

agente  = sys.argv[1] if len(sys.argv) > 1 else "desconhecido"
mensagem = sys.argv[2] if len(sys.argv) > 2 else "erro sem descrição"
ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

linha = f"- **{ts}** | `{agente}` | {mensagem}\n"
with open(LOG, "a", encoding="utf-8") as f:
    f.write(linha)

print(f"Erro registrado em logs/erros.md: {linha.strip()}")
