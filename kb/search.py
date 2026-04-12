"""Busca na wiki com ranking híbrido (keyword + BM25 + RRF)."""

from __future__ import annotations

import math
import re
from pathlib import Path

from kb.config import WIKI_DIR


def _tokenize(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower())


def _extract_snippet(text: str, terms: set[str]) -> str:
    for line in text.splitlines():
        lower = line.lower()
        if any(term in lower for term in terms):
            return line.strip()
    return ""


def _iter_docs() -> list[tuple[Path, str, list[str]]]:
    docs: list[tuple[Path, str, list[str]]] = []
    for md in WIKI_DIR.rglob("*.md"):
        if md.name == "_index.md":
            continue
        text = md.read_text(encoding="utf-8", errors="replace")
        docs.append((md, text, _tokenize(text)))
    return docs


def _build_rankings(query: str) -> tuple[list[tuple[Path, float]], list[tuple[Path, float]], list[tuple[Path, float]], dict[Path, str]]:
    terms = {term for term in _tokenize(query) if len(term) > 1}
    if not terms:
        return [], [], [], {}

    docs = _iter_docs()
    if not docs:
        return [], [], [], {}

    lengths = {path: max(1, len(tokens)) for path, _, tokens in docs}
    avg_len = sum(lengths.values()) / len(lengths)

    # DF por termo para BM25
    df: dict[str, int] = {term: 0 for term in terms}
    for _, _, tokens in docs:
        token_set = set(tokens)
        for term in terms:
            if term in token_set:
                df[term] += 1

    keyword_scores: list[tuple[Path, float]] = []
    density_scores: list[tuple[Path, float]] = []
    bm25_scores: list[tuple[Path, float]] = []
    snippets: dict[Path, str] = {}

    # BM25 params
    k1 = 1.5
    b = 0.75
    n_docs = len(docs)

    for path, text, tokens in docs:
        tf_total = 0.0
        bm25 = 0.0
        term_freq = {term: 0 for term in terms}
        for tok in tokens:
            if tok in term_freq:
                term_freq[tok] += 1

        for term in terms:
            tf = term_freq[term]
            if tf <= 0:
                continue
            tf_total += tf
            df_t = df.get(term, 0)
            idf = math.log(1 + (n_docs - df_t + 0.5) / (df_t + 0.5))
            denom = tf + k1 * (1 - b + b * (lengths[path] / avg_len))
            bm25 += idf * ((tf * (k1 + 1)) / denom)

        if tf_total <= 0:
            continue

        snippets[path] = _extract_snippet(text, terms)
        keyword_scores.append((path, tf_total))
        density_scores.append((path, tf_total / lengths[path]))
        bm25_scores.append((path, bm25))

    keyword_scores.sort(key=lambda item: (item[1], -len(item[0].name), str(item[0])), reverse=True)
    density_scores.sort(key=lambda item: (item[1], -len(item[0].name), str(item[0])), reverse=True)
    bm25_scores.sort(key=lambda item: (item[1], -len(item[0].name), str(item[0])), reverse=True)

    return keyword_scores, density_scores, bm25_scores, snippets


def _rrf_fuse(rankings: list[list[tuple[Path, float]]], k: int = 60) -> dict[Path, float]:
    fused: dict[Path, float] = {}
    for ranking in rankings:
        for i, (path, _) in enumerate(ranking, start=1):
            fused[path] = fused.get(path, 0.0) + (1.0 / (k + i))
    return fused


def find_relevant(query: str, top_k: int = 5) -> list[Path]:
    """Retorna artigos mais relevantes para a query usando ranking híbrido."""
    results = search(query, top_k=top_k, mode="hybrid")
    return [item["path"] for item in results]


def search(query: str, top_k: int = 10, mode: str = "hybrid") -> list[dict]:
    """Retorna resultados com snippet para exibição no CLI.

    mode:
    - hybrid (default): RRF(keyword + density + bm25)
    - keyword: comportamento legado por contagem de termos
    """
    keyword_rank, density_rank, bm25_rank, snippets = _build_rankings(query)

    if mode == "keyword":
        return [
            {
                "path": path,
                "score": score,
                "snippet": snippets.get(path, ""),
            }
            for path, score in keyword_rank[:top_k]
        ]

    fused = _rrf_fuse([keyword_rank, density_rank, bm25_rank])
    channel_keyword = dict(keyword_rank)
    channel_density = dict(density_rank)
    channel_bm25 = dict(bm25_rank)

    ranked_paths = sorted(
        fused.keys(),
        key=lambda p: (
            fused[p],
            channel_bm25.get(p, 0.0),
            channel_density.get(p, 0.0),
            channel_keyword.get(p, 0.0),
            str(p),
        ),
        reverse=True,
    )

    results: list[dict] = []
    for path in ranked_paths[:top_k]:
        results.append(
            {
                "path": path,
                "score": fused[path],
                "rrf_score": fused[path],
                "channel_scores": {
                    "keyword": channel_keyword.get(path, 0.0),
                    "density": channel_density.get(path, 0.0),
                    "bm25": channel_bm25.get(path, 0.0),
                },
                "snippet": snippets.get(path, ""),
            }
        )

    return results
