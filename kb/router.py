"""Routing heurístico por fonte nativa para perguntas do kb."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from kb.config import RAW_DIR
from kb.search import find_relevant
from kb.state import discover_raw_sources, load_knowledge, load_learnings, search_structured_entries


@dataclass(frozen=True)
class RouteDecision:
    route: str
    reason: str


def decide_route(question: str) -> RouteDecision:
    lower = question.lower()

    if any(term in lower for term in ["aprendeu", "aprendi", "learning", "lição", "licao", "correção", "correcao", "preferência", "preferencia"]):
        return RouteDecision("learnings", "Pergunta sobre padrões, correções ou preferências aprendidas.")

    if any(term in lower for term in ["fonte original", "texto original", "documento bruto", "raw", "capítulo", "capitulo"]):
        return RouteDecision("raw", "Pergunta pede acesso ao material bruto de origem.")

    if any(term in lower for term in ["resumo compilado", "summary", "manifesto", "knowledge", "index", "índice", "indice", "compilado"]):
        return RouteDecision("knowledge", "Pergunta pede metadados compilados ou sumários do pipeline.")

    return RouteDecision("wiki", "Pergunta geral deve priorizar a wiki compilada.")


def _build_wiki_context(question: str, top_k: int) -> list[str]:
    relevant = find_relevant(question, top_k=top_k)
    return [f"# {path.stem}\n{path.read_text(encoding='utf-8', errors='replace')}" for path in relevant]


def _build_raw_context(question: str, top_k: int) -> list[str]:
    terms = set(question.lower().split())
    scored: list[tuple[int, Path]] = []

    for path in discover_raw_sources(RAW_DIR):
        text = path.read_text(encoding="utf-8", errors="replace")
        score = sum(text.lower().count(term) for term in terms)
        if score > 0:
            scored.append((score, path))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [f"# {path.name}\n{path.read_text(encoding='utf-8', errors='replace')}" for _, path in scored[:top_k]]


def _build_structured_context(route: str, question: str, top_k: int) -> list[str]:
    if route == "knowledge":
        entries = search_structured_entries(load_knowledge(), question, top_k=top_k)
    else:
        entries = search_structured_entries(load_learnings(), question, top_k=top_k)

    context = []
    for entry in entries:
        title = entry.get("title") or entry.get("kind") or entry.get("source") or route
        body = "\n".join(f"- {key}: {value}" for key, value in entry.items())
        context.append(f"# {title}\n{body}")
    return context


def build_context(question: str, top_k: int = 5) -> tuple[RouteDecision, list[str]]:
    decision = decide_route(question)

    if decision.route == "wiki":
        context = _build_wiki_context(question, top_k)
    elif decision.route == "raw":
        context = _build_raw_context(question, top_k)
    else:
        context = _build_structured_context(decision.route, question, top_k)

    if context or decision.route == "wiki":
        return decision, context

    fallback = RouteDecision("wiki", f"{decision.reason} Nenhum contexto encontrado; fallback para wiki.")
    return fallback, _build_wiki_context(question, top_k)
