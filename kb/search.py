"""Busca na wiki com ranking híbrido (keyword + BM25 + RRF)."""

from __future__ import annotations

import math
import sys
from pathlib import Path

from kb.config import WIKI_DIR
from kb.lexical_index import tokenize as _tokenize


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


class _Snippets:
    """Trecho de exibição por artigo, resolvido sob demanda.

    Com índice lexical o texto não está em memória, e extrair o trecho de todos
    os artigos que casaram exigiria reler o corpus — justamente o que o índice
    evita. Só os poucos resultados devolvidos leem o arquivo. Artigo fora do
    conjunto de casamentos devolve o default sem ler nada: o trecho casa por
    substring e traria trecho onde o ranking lexical não pontuou.
    """

    def __init__(self, terms: set[str], hits: set[Path], cache: dict[Path, str] | None = None):
        self._terms = terms
        self._hits = hits
        self._cache = cache if cache is not None else {}

    def get(self, path: Path, default: str = "") -> str:
        if path in self._cache:
            return self._cache[path]
        if path not in self._hits:
            return default
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return default
        self._cache[path] = _extract_snippet(text, self._terms)
        return self._cache[path]


def _corpus_docs(terms: set[str]) -> list[tuple[Path, int, dict[str, int], str | None]]:
    """(path, comprimento, frequência dos termos, texto) — do índice ou relendo a wiki.

    O texto vem None quando os números saíram do índice lexical; nesse caminho
    o trecho de exibição é resolvido depois, artigo a artigo.
    """
    from kb.config import STATE_DIR
    from kb.lexical_index import lexical_corpus

    indexed = lexical_corpus(WIKI_DIR, STATE_DIR)
    if indexed is not None:
        return [
            (
                WIKI_DIR / relpath,
                entry["length"],
                {term: entry["tf"].get(term, 0) for term in terms},
                None,
            )
            for relpath, entry in indexed.items()
        ]

    docs: list[tuple[Path, int, dict[str, int], str | None]] = []
    for path, text, tokens in _iter_docs():
        term_freq = {term: 0 for term in terms}
        for tok in tokens:
            if tok in term_freq:
                term_freq[tok] += 1
        docs.append((path, len(tokens), term_freq, text))
    return docs


def _build_rankings(query: str) -> tuple[list[tuple[Path, float]], list[tuple[Path, float]], list[tuple[Path, float]], _Snippets]:
    terms = {term for term in _tokenize(query) if len(term) > 1}
    if not terms:
        return [], [], [], _Snippets(terms, set())

    docs = _corpus_docs(terms)
    if not docs:
        return [], [], [], _Snippets(terms, set())

    lengths = {path: max(1, length) for path, length, _, _ in docs}
    avg_len = sum(lengths.values()) / len(lengths)

    # DF por termo para BM25
    df: dict[str, int] = {term: 0 for term in terms}
    for _, _, term_freq, _ in docs:
        for term in terms:
            if term_freq[term] > 0:
                df[term] += 1

    keyword_scores: list[tuple[Path, float]] = []
    density_scores: list[tuple[Path, float]] = []
    bm25_scores: list[tuple[Path, float]] = []
    hits: set[Path] = set()
    cache: dict[Path, str] = {}

    # BM25 params
    k1 = 1.5
    b = 0.75
    n_docs = len(docs)

    for path, _, term_freq, text in docs:
        tf_total = 0.0
        bm25 = 0.0

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

        hits.add(path)
        if text is not None:
            cache[path] = _extract_snippet(text, terms)
        keyword_scores.append((path, tf_total))
        density_scores.append((path, tf_total / lengths[path]))
        bm25_scores.append((path, bm25))

    keyword_scores.sort(key=lambda item: (item[1], -len(item[0].name), str(item[0])), reverse=True)
    density_scores.sort(key=lambda item: (item[1], -len(item[0].name), str(item[0])), reverse=True)
    bm25_scores.sort(key=lambda item: (item[1], -len(item[0].name), str(item[0])), reverse=True)

    return keyword_scores, density_scores, bm25_scores, _Snippets(terms, hits, cache)


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


def _semantic_rank(query: str) -> tuple[list[tuple[Path, float]], dict[Path, dict]]:
    """Canal semântico da fusão + chunk vencedor por artigo.

    Sem índice válido, retorna ([], {}) — fallback lexical. O chunk vencedor
    alimenta o snippet de candidato que só o canal semântico recuperou.
    """
    from kb.config import STATE_DIR
    from kb.embeddings import load_index, semantic_ranking

    index = load_index(STATE_DIR)
    if index is None:
        _warn_semantic_degraded("índice ausente ou de outro modelo; rode `kb index build`")
        return [], {}
    ranking, best_chunks = semantic_ranking(query, index)
    if not ranking:
        _warn_semantic_degraded("servidor de embeddings não respondeu; veja `kb index status`")
    return ranking, best_chunks


def _first_text_line(text: str) -> str:
    """Primeira linha de prosa: pula heading, fence, tabela e blockquote."""
    fence = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            fence = not fence
            continue
        if fence or not stripped or stripped.startswith(("#", ">", "|")):
            continue
        for marker in ("- ", "* ", "+ "):
            if stripped.startswith(marker):
                stripped = stripped[len(marker):].strip()
                break
        return stripped
    return ""


def _semantic_snippet(path: Path, info: dict) -> str:
    """Trecho do chunk que venceu no cosseno.

    Arquivo idêntico ao indexado (hash confere) → o mesmo chunking reproduz o
    chunk exato pelo ordinal — heading repetido e seção dividida não localizam.
    Índice stale cai para a seção homônima e depois para o primeiro trecho do
    corpo — snippet genérico ainda é melhor que o LLM julgar por slug.
    """
    from kb.chunking import build_chunks, split_sections

    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""

    if info.get("hash"):
        from kb.embeddings import _DOCUMENT_PREFIX, _content_hash

        if _content_hash(text) == info["hash"]:
            from kb.frontmatter import parse

            meta, _ = parse(text)
            title = str(meta.get("title") or path.stem).strip()
            chunks = build_chunks(title, text, max_chars=8000 - len(_DOCUMENT_PREFIX))
            ordinal = info.get("ordinal", -1)
            if 0 <= ordinal < len(chunks):
                # O texto do chunk começa pelo prefixo "título — heading"; pula-o.
                piece = chunks[ordinal]["text"].split("\n", 1)[-1]
                snippet = _first_text_line(piece)
                if snippet:
                    return snippet

    sections = split_sections(text)
    heading = info.get("heading", "")
    chosen = next((section for name, section in sections if name == heading), None)
    if chosen is not None:
        snippet = _first_text_line(chosen)
        if snippet:
            return snippet
    # Seção homônima vazia ou ausente: primeira seção com prosa de verdade —
    # sem isso, heading de seção vazia reintroduzia o snippet vazio original.
    for _, section in sections:
        snippet = _first_text_line(section)
        if snippet:
            return snippet
    return ""


def find_relevant(query: str, top_k: int = 5, rerank_depth: int | None = None) -> list[Path]:
    """Retorna artigos mais relevantes para a query usando ranking híbrido."""
    results = search(query, top_k=top_k, mode="hybrid", rerank_depth=rerank_depth)
    return [item["path"] for item in results]


SEARCH_MODES = ("hybrid", "lexical", "keyword")


def rel_slug(path: Path, wiki_dir: Path | None = None) -> str:
    """Identidade única do artigo: path relativo à wiki sem extensão.

    O stem sozinho colide — o vault tem 4 stems duplicados em topics
    diferentes, e dois no mesmo head faziam um sobrescrever o outro.
    Fora da wiki (ramo defensivo), o path completo mantém a unicidade.
    """
    try:
        return path.relative_to(wiki_dir or WIKI_DIR).with_suffix("").as_posix()
    except ValueError:
        return path.with_suffix("").as_posix()


def _apply_rerank(query: str, results: list[dict], depth: int) -> list[dict]:
    """Reordena os `depth` primeiros pelo julgamento do LLM, preservando o resto."""
    from kb.rerank import rerank as do_rerank

    head, tail = results[:depth], results[depth:]
    candidates = [
        {"slug": rel_slug(item["path"]), "title": rel_slug(item["path"]), "snippet": item.get("snippet", "")}
        for item in head
    ]
    by_slug = {rel_slug(item["path"]): item for item in head}
    reordered = [by_slug[c["slug"]] for c in do_rerank(query, candidates) if c["slug"] in by_slug]
    return reordered + tail


def search(
    query: str,
    top_k: int = 10,
    mode: str = "hybrid",
    expand: str | None = None,
    rerank_depth: int | None = None,
) -> list[dict]:
    """Retorna resultados com snippet para exibição no CLI.

    mode:
    - hybrid (default): RRF(keyword + density + bm25 + semântico quando há índice)
    - lexical: RRF(keyword + density + bm25), sem consultar o canal semântico
    - keyword: comportamento legado por contagem de termos

    expand: estratégia de expansão da query aplicada **apenas** ao canal
    semântico. Os lexicais funcionam por casamento de termo e seriam diluídos
    por vocabulário gerado.
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
    semantic_headings: dict[Path, dict] = {}
    if mode == "hybrid":
        semantic_query = query
        if expand:
            from kb.query_expansion import expand_query

            semantic_query = expand_query(query, expand)
        semantic_rank, semantic_headings = _semantic_rank(semantic_query)
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

    # Com rerank, é preciso buscar mais fundo do que se vai devolver.
    fetch = max(top_k, rerank_depth or 0)

    results: list[dict] = []
    for path in ranked_paths[:fetch]:
        snippet = snippets.get(path, "")
        if not snippet and path in semantic_headings:
            snippet = _semantic_snippet(path, semantic_headings[path])
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
                "snippet": snippet,
            }
        )

    if rerank_depth and len(results) > 1:
        results = _apply_rerank(query, results, rerank_depth)

    return results[:top_k]
