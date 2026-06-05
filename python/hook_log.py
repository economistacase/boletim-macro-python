"""
Hook PostToolUse — loga cada chamada de ferramenta em logs/execucao.jsonl.
Recebe JSON via stdin com os campos do Claude Code hook.
"""
import sys
import json
import os
from datetime import datetime, timezone

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG  = os.path.join(BASE, "logs", "execucao.jsonl")
os.makedirs(os.path.join(BASE, "logs"), exist_ok=True)

try:
    payload = json.load(sys.stdin)
    entry = {
        "ts":        datetime.now(timezone.utc).isoformat(),
        "tool":      payload.get("tool_name", ""),
        "input":     {k: str(v)[:120] for k, v in (payload.get("tool_input") or {}).items()},
        "exit_code": payload.get("tool_response", {}).get("exit_code") if isinstance(payload.get("tool_response"), dict) else None,
    }
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
except Exception:
    pass  # hook nunca deve interromper o agente
