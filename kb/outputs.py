"""Store de outputs: respostas de QA arquivadas fora da wiki."""

import re
from datetime import date

import kb.config as _config
from kb.git import commit


def write_output(question: str, answer: str, topic: str, no_commit: bool = False):
    """Grava resposta de QA em outputs/<topic>/<YYYY-MM-DD>-<slug>.md.

    Retorna (answer, path).
    """
    today = date.today().isoformat()
    slug = re.sub(r"[^a-z0-9]+", "-", question.lower())[:60].strip("-")

    folder = _config.OUTPUTS_DIR / topic
    folder.mkdir(parents=True, exist_ok=True)

    out = folder / f"{today}-{slug}.md"
    content = (
        f"---\n"
        f"title: {question[:80]}\n"
        f"source_question: {question}\n"
        f"date: {today}\n"
        f"topic: {topic}\n"
        f"---\n\n"
        f"{answer}\n"
    )
    out.write_text(content, encoding="utf-8")

    if not no_commit:
        commit(f"feat(outputs): file back — {question[:50]}", [out])

    return answer, out
