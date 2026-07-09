"""Store de outputs: respostas de QA arquivadas fora da wiki."""

import re
from datetime import date

import kb.config as _config
from kb.frontmatter import parse, serialize
from kb.fsutil import atomic_write_text
from kb.git import commit


def _build_content(answer: str, question: str, today: str, topic: str) -> str:
    meta, body = parse(answer)
    if meta or body != answer:
        if "source_question" not in meta:
            meta["source_question"] = question
        if "date" not in meta:
            meta["date"] = today
        body = "\n".join(body.splitlines()).lstrip("\n")
        return serialize(meta, f"\n{body}\n")
    return (
        f"---\n"
        f"title: {question[:80]}\n"
        f"source_question: {question}\n"
        f"date: {today}\n"
        f"topic: {topic}\n"
        f"---\n\n"
        f"{answer}\n"
    )


def write_output(question: str, answer: str, topic: str, no_commit: bool = True):
    """Grava resposta de QA em outputs/<topic>/<YYYY-MM-DD>-<slug>.md.

    Retorna (answer, path).
    """
    today = date.today().isoformat()
    slug = re.sub(r"[^a-z0-9]+", "-", question.lower())[:60].strip("-")

    topic = _config.canonical_topic(topic)
    folder = _config.OUTPUTS_DIR / topic
    folder.mkdir(parents=True, exist_ok=True)

    out = folder / f"{today}-{slug}.md"
    content = _build_content(answer, question, today, topic)
    atomic_write_text(out, content)

    if not no_commit:
        commit(f"feat(outputs): file back — {question[:50]}", [out])

    return answer, out
