"""Busca na wiki com ranking híbrido (keyword + BM25 + RRF)."""

from __future__ import annotations

import math
import re
import sys
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
    """Corpus da busca lexical — mesma convenção do índice semântico: `_*` e `.*` fora."""
    docs: list[tuple[Path, str, list[str]]] = []
    for md in WIKI_DIR.rglob("*.md"):
        if any(part.startswith(("_", ".")) for part in md.relative_to(WIKI_DIR).parts):
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


_semantic_warned = False


def _warn_semantic_degraded(reason: str) -> None:
    """Anuncia a degradação uma vez por execução, sem poluir stdout."""
    global _semantic_warned
    if _semantic_warned:
        return
    _semantic_warned = True
    print(
        f"aviso: canal semântico indisponível ({reason}) — resultados vêm só do lexical",
        file=sys.stderr,
    )


def _semantic_rank(query: str) -> list[tuple[Path, float]]:
    """Canal semântico da fusão; sem índice válido, retorna [] (fallback lexical)."""
    from kb.config import STATE_DIR
    from kb.embeddings import load_index, semantic_ranking

    index = load_index(STATE_DIR)
    if index is None:
        _warn_semantic_degraded("índice ausente ou de outro modelo; rode `kb index build`")
        return []
    ranking = semantic_ranking(query, index)
    if not ranking:
        _warn_semantic_degraded("servidor de embeddings não respondeu; veja `kb index status`")
    return ranking


def find_relevant(query: str, top_k: int = 5) -> list[Path]:
    """Retorna artigos mais relevantes para a query usando ranking híbrido."""
    results = search(query, top_k=top_k, mode="hybrid")
    return [item["path"] for item in results]


SEARCH_MODES = ("hybrid", "lexical", "keyword")


def search(query: str, top_k: int = 10, mode: str = "hybrid") -> list[dict]:
    """Retorna resultados com snippet para exibição no CLI.

    mode:
    - hybrid (default): RRF(keyword + density + bm25 + semântico quando há índice)
    - lexical: RRF(keyword + density + bm25), sem consultar o canal semântico
    - keyword: comportamento legado por contagem de termos
    """
    if mode not in SEARCH_MODES:
        raise ValueError(
            f"modo de busca desconhecido: {mode!r} (use um de {', '.join(SEARCH_MODES)})"
        )

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

    rankings = [keyword_rank, density_rank, bm25_rank]
    if mode == "hybrid":
        semantic_rank = _semantic_rank(query)
        if semantic_rank:
            rankings.append(semantic_rank)

    fused = _rrf_fuse(rankings)
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
