from __future__ import annotations

from datetime import datetime
from pathlib import Path

from kb.config import DATA_DIR


def _handoff_dir() -> Path:
    return (DATA_DIR / "docs" / "handoffs").resolve()


def _timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d-%H%M")


def create_handoff(
    *,
    scope: str,
    summary: str = "",
    branch: str = "",
    next_steps: str = "",
    evidence: str = "",
    decisions: str = "",
) -> Path:
    handoff_dir = _handoff_dir()
    handoff_dir.mkdir(parents=True, exist_ok=True)

    name = f"{_timestamp()}.md"
    path = handoff_dir / name

    body = (
        "# Handoff de Sessão\n\n"
        "## Contexto\n"
        f"- Data/hora: {datetime.now().isoformat(timespec='seconds')}\n"
        f"- Branch: {branch or '(não informado)'}\n"
        f"- Escopo da sessão: {scope}\n\n"
        "## Decisões\n"
        f"{decisions or '- (preencher)'}\n\n"
        "## Entregas\n"
        f"{summary or '- (preencher)'}\n\n"
        "## Evidências\n"
        f"{evidence or '- (preencher)'}\n\n"
        "## Próximos passos\n"
        f"{next_steps or '- (preencher)'}\n"
    )

    path.write_text(body, encoding="utf-8")
    return path
