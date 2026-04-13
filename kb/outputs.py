"""Store de outputs: respostas de QA arquivadas fora da wiki."""

import re
from datetime import date

import kb.config as _config
from kb.git import commit


def _build_content(answer: str, question: str, today: str, topic: str) -> str:
    lines = answer.splitlines()
    if lines and lines[0].strip() == "---":
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == "---":
                front_lines = lines[1:i]
                body_lines = lines[i + 1 :]
                front_keys = {
                    front_line.split(":", 1)[0].strip()
                    for front_line in front_lines
                    if ":" in front_line
                }
                extra = []
                if "source_question" not in front_keys:
                    extra.append(f"source_question: {question}")
                if "date" not in front_keys:
                    extra.append(f"date: {today}")
                merged = "\n".join(front_lines + extra)
                body = "\n".join(body_lines).lstrip("\n")
                return f"---\n{merged}\n---\n\n{body}\n"
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
    out.write_text(content, encoding="utf-8")

    if not no_commit:
        commit(f"feat(outputs): file back — {question[:50]}", [out])

    return answer, out
