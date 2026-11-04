"""Marca o diretório de trabalho como confiável para o Claude Code.

Sem isso, o Claude Code em CI ignora as entradas de `permissions` do
`.claude/settings.json` (o log avisa "this workspace has not been trusted")
porque o diálogo de confiança nunca foi aceito — ele é interativo e não há
terminal no runner. O efeito é que as regras de permissão do projeto, incluindo
a lista `deny`, não valem durante a execução da pipeline.

A própria mensagem do Claude Code indica o remédio: gravar
`projects["<caminho>"].hasTrustDialogAccepted = true` em `~/.claude.json`.

Uso: python confiar_workspace.py [caminho]
Sem argumento, usa $GITHUB_WORKSPACE e, na falta dele, o diretório atual.
Somente biblioteca padrão. Idempotente.
"""
import json
import os
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1]:
        alvo = sys.argv[1]
    else:
        alvo = os.environ.get("GITHUB_WORKSPACE") or os.getcwd()
    # O Claude Code indexa os projetos pelo caminho absoluto resolvido.
    alvo = str(Path(alvo).resolve())

    lar = os.environ.get("HOME") or os.path.expanduser("~")
    config = Path(lar) / ".claude.json"

    dados = {}
    if config.exists():
        try:
            dados = json.loads(config.read_text(encoding="utf-8")) or {}
        except (json.JSONDecodeError, OSError) as e:
            print(f"AVISO: {config} ilegivel ({e}); sera reescrito.", file=sys.stderr)
            dados = {}
    if not isinstance(dados, dict):
        print(f"AVISO: {config} nao contem um objeto JSON; sera reescrito.", file=sys.stderr)
        dados = {}

    projetos = dados.setdefault("projects", {})
    if not isinstance(projetos, dict):
        projetos = {}
        dados["projects"] = projetos
    entrada = projetos.setdefault(alvo, {})
    if not isinstance(entrada, dict):
        entrada = {}
        projetos[alvo] = entrada

    if entrada.get("hasTrustDialogAccepted") is True:
        print(f"Workspace ja estava confiavel: {alvo}")
        return 0

    entrada["hasTrustDialogAccepted"] = True
    config.parent.mkdir(parents=True, exist_ok=True)
    config.write_text(json.dumps(dados, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Workspace marcado como confiavel em {config}: {alvo}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
