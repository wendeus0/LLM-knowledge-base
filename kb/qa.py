"""Q&A contra fontes nativas. Com --file-back, a resposta é arquivada no corpus."""

import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from kb import grounding
from kb.claims import find_relevant_claims
from kb.client import chat
from kb.config import WIKI_DIR as CONFIG_WIKI_DIR
from kb.config import canonical_topic, topic_prompt_options, wiki_topic_dir
from kb.frontmatter import parse
from kb.git import commit
from kb.guardrails import (
    assert_safe_for_provider,
    new_sentinel,
    untrusted_policy,
    warn_on_injection,
    wrap_untrusted,
)
from kb.outputs import write_output as _write_output
from kb.router import build_context
from kb.sampling import params
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
    top_k: int | None = None,
    allow_sensitive: bool = False,
    traverse: bool = True,
    depth: int | None = None,
    profile: str = "fast",
    rerank_depth: int | None = None,
    grounding_enabled: bool = True,
) -> str:
    result = answer_with_grounding(
        question,
        top_k=top_k,
        allow_sensitive=allow_sensitive,
        traverse=traverse,
        depth=depth,
        profile=profile,
        rerank_depth=rerank_depth,
        grounding_enabled=grounding_enabled,
    )
    return _AnswerText(result.answer, result.grounding)


def answer_with_grounding(
    question: str,
    top_k: int | None = None,
    allow_sensitive: bool = False,
    traverse: bool = True,
    depth: int | None = None,
    profile: str = "fast",
    rerank_depth: int | None = None,
    grounding_enabled: bool = True,
) -> "QaResult":
    from kb.config import get_retrieval_profile

    resolved = get_retrieval_profile(profile)
    effective_top_k = top_k if top_k is not None else resolved["top_k"]
    effective_traverse = traverse and resolved["traverse"]
    effective_rerank = rerank_depth if rerank_depth is not None else resolved["rerank_depth"]
    decision, context_parts = build_context(
        question,
        top_k=effective_top_k,
        traverse=effective_traverse,
        depth=depth,
        doc_chars=resolved["doc_chars"],
        traversal_budget=resolved["traversal_budget"],
        rerank_depth=effective_rerank,
    )

    if not context_parts:
        return QaResult(
            answer="Nenhum contexto relevante encontrado. Use `kb compile` para adicionar conteúdo ou registre learnings/knowledge.",
            grounding=grounding.GroundingResult(),
        )

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
    assert_safe_for_provider(
        f"Pergunta: {question}\n\n{full_context}",
        source=f"qa:{decision.route}",
        allow_sensitive=allow_sensitive,
    )
    warn_on_injection(full_context, source=f"qa:{decision.route}")
    sentinel = new_sentinel()
    response = chat(
        messages=[
            {"role": "system", "content": f"{SYSTEM}\n{untrusted_policy(sentinel)}"},
            {
                "role": "user",
                "content": (
                    f"Fonte selecionada: {decision.route}\n"
                    f"Motivo do roteamento: {decision.reason}\n\n"
                    f"Contexto relevante:\n\n"
                    f"{wrap_untrusted(full_context, sentinel)}\n\n"
                    f"Pergunta: {question}"
                ),
            },
        ],
        # Responder com base nos artigos fornecidos, sem extrapolar.
        **params("analytical"),
    )
    state_dir = os.getenv("KB_STATE_DIR")
    if state_dir:
        from kb import state

        state.STATE_DIR = Path(state_dir)
        state.LEARNINGS_PATH = state.STATE_DIR / "learnings.json"
    add_learning(
        "retrieval", f"Pergunta '{question}' roteada para {decision.route}", source="qa"
    )
    if not grounding_enabled:
        grounding_result = grounding.GroundingResult()
    else:
        try:
            grounding_result = grounding.verify(response, full_context)
        except Exception:
            grounding_result = grounding.GroundingResult(status="degraded")

    global _grounding_warned
    if grounding_result.status == "degraded" and not _grounding_warned:
        print(
            "aviso: verificação de ancoragem indisponível — resposta exibida sem verificação",
            file=sys.stderr,
        )
        _grounding_warned = True

    return QaResult(answer=response, grounding=grounding_result)


def answer_and_file(
    question: str,
    top_k: int | None = None,
    allow_sensitive: bool = False,
    no_commit: bool = True,
    to_wiki: bool = False,
    traverse: bool = True,
    depth: int | None = None,
    profile: str = "fast",
    index_refresh_enabled: bool = True,
    rerank_depth: int | None = None,
    grounding_enabled: bool = True,
) -> tuple[str, Path | None]:
    """Responde e arquiva a resposta.

    Por padrão grava em outputs/. Com to_wiki=True, arquiva em wiki/ (comportamento anterior).
    """
    result = answer_with_grounding(
        question,
        top_k=top_k,
        allow_sensitive=allow_sensitive,
        traverse=traverse,
        depth=depth,
        profile=profile,
        rerank_depth=rerank_depth,
        grounding_enabled=grounding_enabled,
    )
    response = _AnswerText(result.answer, result.grounding)
    assert_safe_for_provider(
        f"Pergunta: {question}\n\nResposta: {response}",
        source="qa:file_back",
        allow_sensitive=allow_sensitive,
    )

    sentinel = new_sentinel()
    article = chat(
        messages=[
            {
                "role": "system",
                "content": f"{_file_back_system_prompt()}\n{untrusted_policy(sentinel)}",
            },
            {
                "role": "user",
                "content": (
                    f"Pergunta: {question}\n\nResposta:\n"
                    f"{wrap_untrusted(response, sentinel)}"
                ),
            },
        ],
        # Redigir artigo a partir da resposta: prosa, não extração.
        **params("generative"),
    )
    grounding_lines = ["## Verificação de ancoragem da resposta"]
    grounding_lines.extend(
        f"- {claim.verdict}: {claim.evidence}" for claim in result.grounding.claims
    )
    grounding_section = "\n".join(grounding_lines)
    article = f"{article.rstrip()}\n\n{grounding_section}\n"

    topic = "general"
    title = question[:50]
    meta, _ = parse(article)
    topic_value = meta.get("topic", "")
    if isinstance(topic_value, str) and topic_value.strip():
        topic = canonical_topic(topic_value)
    title_value = meta.get("title", "")
    if isinstance(title_value, str) and title_value.strip():
        title = title_value.strip()

    if to_wiki:
        slug = re.sub(r"[^a-z0-9-]", "-", title.lower())[:60].strip("-")
        folder = wiki_topic_dir(topic)
        folder.mkdir(parents=True, exist_ok=True)
        out = folder / f"{slug}.md"
        out.write_text(article, encoding="utf-8")
        from kb.embeddings import refresh_embeddings_index

        refresh_embeddings_index(enabled=index_refresh_enabled)
    else:
        outputs_dir = os.getenv("KB_OUTPUTS_DIR")
        if outputs_dir:
            from kb import config

            config.OUTPUTS_DIR = Path(outputs_dir)
        _, out = _write_output(question, article, topic, no_commit=True)

    if not no_commit:
        commit(f"feat(outputs): file back answer — {title[:50]}", [out])

    return response, out


@dataclass
class QaResult:
    answer: str
    grounding: object
    saved_path: Path | None = None

    def __iter__(self):
        yield self.answer
        yield self.saved_path


class _AnswerText(str):
    def __new__(cls, answer, grounding_result):
        value = super().__new__(cls, answer)
        value.grounding = grounding_result
        return value


_grounding_warned = False
