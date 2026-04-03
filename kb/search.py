"""Busca simples por palavra-chave na wiki."""

from pathlib import Path
from kb.config import WIKI_DIR


def find_relevant(query: str, top_k: int = 5) -> list[Path]:
    """Retorna os artigos mais relevantes para a query (TF-IDF simples via contagem)."""
    terms = set(query.lower().split())
    scored: list[tuple[int, Path]] = []

    for md in WIKI_DIR.rglob("*.md"):
        if md.name == "_index.md":
            continue
        text = md.read_text(encoding="utf-8", errors="replace").lower()
        score = sum(text.count(term) for term in terms)
        if score > 0:
            scored.append((score, md))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in scored[:top_k]]


def search(query: str, top_k: int = 10) -> list[dict]:
    """Retorna resultados com snippet para exibição no CLI."""
    terms = set(query.lower().split())
    results = []

    for md in WIKI_DIR.rglob("*.md"):
        if md.name == "_index.md":
            continue
        text = md.read_text(encoding="utf-8", errors="replace")
        lower = text.lower()
        score = sum(lower.count(term) for term in terms)
        if score == 0:
            continue

        # Snippet: primeira linha que contenha um dos termos
        snippet = ""
        for line in text.splitlines():
            if any(term in line.lower() for term in terms):
                snippet = line.strip()
                break

        results.append({"path": md, "score": score, "snippet": snippet})

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]
