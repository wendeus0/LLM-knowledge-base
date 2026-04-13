"""Q&A contra fontes nativas. Com --file-back, a resposta é arquivada de volta na wiki."""

import re
from pathlib import Path
from kb.client import chat
from kb.config import WIKI_DIR as CONFIG_WIKI_DIR
from kb.config import is_supported_topic, topic_prompt_options, wiki_topic_dir
from kb.git import commit
from kb.guardrails import assert_safe_for_provider
from kb.outputs import write_output as _write_output
from kb.router import build_context
from kb.claims import find_relevant_claims
from kb.state import add_learning

SYSTEM = """Você é um assistente de knowledge base. Responda perguntas com base nos artigos fornecidos.
- Cite os artigos que embasaram a resposta usando [[wikilink]]
- Se a informação não estiver nos artigos, diga explicitamente
- Seja direto e preciso
"""

WIKI_DIR = CONFIG_WIKI_DIR


def _file_back_system_prompt() -> str:
    return f"""Dado uma pergunta e sua resposta, gere um artigo wiki em markdown para arquivar na knowledge base.
Formato obrigatório (apenas o markdown, sem explicações):
---
title: <título conciso>
topic: <{topic_prompt_options()}>
tags: [tag1, tag2]
source: qa
---

# <título>

<conteúdo da resposta, expandido e estruturado>

## Conceitos Relacionados
- [[conceito1]]
"""


def answer(
    question: str,
    top_k: int = 5,
    allow_sensitive: bool = False,
    traverse: bool = True,
    depth: int | None = None,
) -> str:
    decision, context_parts = build_context(
        question, top_k=top_k, traverse=traverse, depth=depth
    )

    if not context_parts:
        return "Nenhum contexto relevante encontrado. Use `kb compile` para adicionar conteúdo ou registre learnings/knowledge."

    context = "\n\n---\n\n".join(context_parts)
    claims = find_relevant_claims(question, top_k=3)
    claims_block = ""
    if claims:
        lines = ["Claims relevantes (lifecycle):"]
        for claim in claims:
            confidence = claim.get("confidence", 0)
            lines.append(
                f"- [{claim.get('status', 'active')}] confidence={confidence:.2f} :: {claim.get('text', '')}"
            )
        claims_block = "\n".join(lines)

    full_context = (
        context if not claims_block else f"{context}\n\n---\n\n{claims_block}"
    )
    claims_suffix = ""
    if claims_block:
        claims_suffix = claims_block + "\n\n"
    assert_safe_for_provider(
        f"Pergunta: {question}\n\n{full_context}",
        source=f"qa:{decision.route}",
        allow_sensitive=allow_sensitive,
    )
    response = chat(
        messages=[
            {"role": "system", "content": SYSTEM},
            {
                "role": "user",
                "content": (
                    f"Fonte selecionada: {decision.route}\n"
                    f"Motivo do roteamento: {decision.reason}\n\n"
                    f"Contexto relevante:\n\n{context}\n\n"
                    f"{claims_suffix}"
                    f"Pergunta: {question}"
                ),
            },
        ]
    )
    add_learning(
        "retrieval", f"Pergunta '{question}' roteada para {decision.route}", source="qa"
    )
    return response


def answer_and_file(
    question: str,
    top_k: int = 5,
    allow_sensitive: bool = False,
    no_commit: bool = True,
    to_wiki: bool = False,
    traverse: bool = True,
    depth: int | None = None,
) -> tuple[str, Path | None]:
    """Responde e arquiva a resposta.

    Por padrão grava em outputs/. Com to_wiki=True, arquiva em wiki/ (comportamento anterior).
    """
    response = answer(
        question,
        top_k=top_k,
        allow_sensitive=allow_sensitive,
        traverse=traverse,
        depth=depth,
    )
    assert_safe_for_provider(
        f"Pergunta: {question}\n\nResposta: {response}",
        source="qa:file_back",
        allow_sensitive=allow_sensitive,
    )

    article = chat(
        messages=[
            {"role": "system", "content": _file_back_system_prompt()},
            {
                "role": "user",
                "content": f"Pergunta: {question}\n\nResposta:\n{response}",
            },
        ]
    )

    # Extrai topic e title do frontmatter
    topic = "general"
    title = question[:50]
    for line in article.splitlines():
        if line.startswith("topic:"):
            t = line.split(":", 1)[1].strip()
            if is_supported_topic(t):
                topic = t
        if line.startswith("title:"):
            title = line.split(":", 1)[1].strip()

    if to_wiki:
        slug = re.sub(r"[^a-z0-9-]", "-", title.lower())[:60].strip("-")
        folder = wiki_topic_dir(topic)
        folder.mkdir(parents=True, exist_ok=True)
        out = folder / f"{slug}.md"
        out.write_text(article, encoding="utf-8")
    else:
        _, out = _write_output(question, article, topic, no_commit=True)

    if not no_commit:
        commit(f"feat(outputs): file back answer — {title[:50]}", [out])

    return response, out
