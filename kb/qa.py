"""Q&A contra a wiki. Com --file-back, a resposta é arquivada de volta na wiki."""

import re
from pathlib import Path
from kb.client import chat
from kb.config import WIKI_DIR, TOPICS
from kb.search import find_relevant
from kb.git import commit


SYSTEM = """Você é um assistente de knowledge base. Responda perguntas com base nos artigos fornecidos.
- Cite os artigos que embasaram a resposta usando [[wikilink]]
- Se a informação não estiver nos artigos, diga explicitamente
- Seja direto e preciso
"""

FILE_BACK_SYSTEM = """Dado uma pergunta e sua resposta, gere um artigo wiki em markdown para arquivar na knowledge base.
Formato obrigatório (apenas o markdown, sem explicações):
---
title: <título conciso>
topic: <cybersecurity|ai|python|typescript|general>
tags: [tag1, tag2]
source: qa
---

# <título>

<conteúdo da resposta, expandido e estruturado>

## Conceitos Relacionados
- [[conceito1]]
"""


def answer(question: str, top_k: int = 5) -> str:
    relevant = find_relevant(question, top_k=top_k)

    if not relevant:
        return "Nenhum artigo relevante encontrado na wiki. Use `kb compile` para adicionar conteúdo."

    context = "\n\n---\n\n".join(
        f"# {p.stem}\n{p.read_text(encoding='utf-8')}" for p in relevant
    )

    return chat(
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": f"Artigos relevantes:\n\n{context}\n\nPergunta: {question}"},
        ]
    )


def answer_and_file(question: str, top_k: int = 5) -> tuple[str, Path | None]:
    """Responde e arquiva a resposta de volta na wiki."""
    response = answer(question, top_k=top_k)

    article = chat(
        messages=[
            {"role": "system", "content": FILE_BACK_SYSTEM},
            {"role": "user", "content": f"Pergunta: {question}\n\nResposta:\n{response}"},
        ]
    )

    # Extrai topic e title do frontmatter
    topic = "general"
    title = question[:50]
    for line in article.splitlines():
        if line.startswith("topic:"):
            t = line.split(":", 1)[1].strip()
            if t in TOPICS:
                topic = t
        if line.startswith("title:"):
            title = line.split(":", 1)[1].strip()

    slug = re.sub(r"[^a-z0-9-]", "-", title.lower())[:60].strip("-")
    folder = WIKI_DIR / topic if topic in TOPICS else WIKI_DIR
    folder.mkdir(parents=True, exist_ok=True)
    out = folder / f"{slug}.md"
    out.write_text(article, encoding="utf-8")
    commit(f"feat(wiki): file back answer — {title[:50]}", [out])

    return response, out
