"""Índice de embeddings por vault (feature 012-semantic-retrieval, ADR-0013 Fase 2).

Um vetor por artigo da wiki, gerado por modelo local (default: Nomic via Ollama,
endpoint OpenAI-compat). Índice em kb_state/embeddings.json, incremental por hash
de conteúdo. Sem índice válido, search/qa degradam para o retrieval lexical.
"""

import hashlib
import json
import math
import os
from pathlib import Path

INDEX_FILENAME = "embeddings.json"
DEFAULT_MODEL = "text-embedding-nomic-embed-text-v2-moe"
DEFAULT_BASE_URL = "http://localhost:1234/v1"


def _embed_model() -> str:
    return os.getenv("KB_EMBED_MODEL", DEFAULT_MODEL)


def _embed_base_url() -> str:
    return os.getenv("KB_EMBED_BASE_URL", DEFAULT_BASE_URL)


def embed_texts(texts: list[str], model: str | None = None, base_url: str | None = None) -> list[list[float]]:
    """Fronteira de rede: gera embeddings via endpoint OpenAI-compat (Ollama)."""
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError(
            "Dependência opcional ausente: instale `openai` para usar embeddings."
        ) from exc

    client = OpenAI(api_key=os.getenv("KB_EMBED_API_KEY", "ollama"), base_url=base_url or _embed_base_url())
    response = client.embeddings.create(model=model or _embed_model(), input=texts)
    return [item.embedding for item in response.data]


def _iter_articles(wiki_dir: Path) -> list[tuple[str, str]]:
    """(relpath, texto) dos artigos da wiki, ignorando infra `_*`."""
    articles: list[tuple[str, str]] = []
    for md in sorted(Path(wiki_dir).rglob("*.md")):
        relative = md.relative_to(wiki_dir)
        if any(part.startswith("_") for part in relative.parts):
            continue
        articles.append((str(relative), md.read_text(encoding="utf-8", errors="replace")))
    return articles


def _content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _read_index_file(state_dir: Path) -> dict | None:
    index_file = Path(state_dir) / INDEX_FILENAME
    if not index_file.exists():
        return None
    try:
        return json.loads(index_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def build_index(wiki_dir: Path, state_dir: Path, force: bool = False, max_chars: int = 8000) -> dict:
    from kb.fsutil import atomic_write_text

    model = _embed_model()
    articles = _iter_articles(wiki_dir)
    previous = _read_index_file(state_dir)
    reusable: dict[str, dict] = {}
    if previous and previous.get("model") == model and not force:
        reusable = previous.get("articles", {})

    to_embed: list[tuple[str, str]] = []
    kept: dict[str, dict] = {}
    truncated = 0
    for relpath, text in articles:
        digest = _content_hash(text)
        entry = reusable.get(relpath)
        if entry and entry.get("hash") == digest:
            kept[relpath] = entry
            continue
        payload_text = f"search_document: {text}"[:max_chars]
        if len(f"search_document: {text}") > max_chars:
            truncated += 1
        to_embed.append((relpath, payload_text))
        kept[relpath] = {"hash": digest}

    removed = len([relpath for relpath in reusable if relpath not in dict(articles)])

    if to_embed:
        try:
            vectors = embed_texts([text for _, text in to_embed])
        except Exception as exc:
            raise RuntimeError(
                f"Falha ao gerar embeddings (modelo {model}, endpoint {_embed_base_url()}): {exc}. "
                "Verifique se o Ollama está no ar (`ollama serve`) e o modelo instalado."
            ) from exc
        for (relpath, _), vector in zip(to_embed, vectors, strict=True):
            kept[relpath]["vector"] = vector

    dim = 0
    for entry in kept.values():
        vector = entry.get("vector")
        if vector:
            dim = len(vector)
            break

    payload = {"model": model, "dim": dim, "articles": kept}
    Path(state_dir).mkdir(parents=True, exist_ok=True)
    atomic_write_text(Path(state_dir) / INDEX_FILENAME, json.dumps(payload, ensure_ascii=False))

    return {
        "indexed": len(to_embed),
        "removed": removed,
        "unchanged": len(kept) - len(to_embed),
        "truncated": truncated,
        "model": model,
        "dim": dim,
    }


def load_index(state_dir: Path) -> dict | None:
    """Índice válido para o modelo configurado, ou None (fallback lexical)."""
    payload = _read_index_file(state_dir)
    if not payload or payload.get("model") != _embed_model():
        return None
    articles = {
        relpath: entry
        for relpath, entry in payload.get("articles", {}).items()
        if entry.get("vector")
    }
    if not articles:
        return None
    return {"model": payload["model"], "dim": payload.get("dim", 0), "articles": articles}


def index_status(wiki_dir: Path, state_dir: Path) -> dict:
    model = _embed_model()
    articles = _iter_articles(wiki_dir)
    payload = _read_index_file(state_dir)
    index_file = Path(state_dir) / INDEX_FILENAME

    note = ""
    indexed_entries: dict[str, dict] = {}
    if payload is None and index_file.exists():
        note = "índice corrompido — rode `kb index build` (rebuild)"
    elif payload is None:
        note = "nenhum índice — rode `kb index build`"
    elif payload.get("model") != model:
        note = f"índice gerado por outro modelo ({payload.get('model')}) — rode `kb index build` (rebuild)"
    else:
        indexed_entries = payload.get("articles", {})

    stale = [
        relpath
        for relpath, text in articles
        if indexed_entries.get(relpath, {}).get("hash") != _content_hash(text)
    ]
    return {
        "total": len(articles),
        "indexed": len(articles) - len(stale),
        "stale": stale,
        "model": model,
        "note": note,
    }


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def semantic_ranking(query: str, index: dict) -> list[tuple[Path, float]]:
    """Ranking (Path absoluto, similaridade) por cosseno; falha de embed degrada para []."""
    from kb.config import WIKI_DIR

    try:
        query_vector = embed_texts([f"search_query: {query}"])[0]
    except Exception:
        return []
    scored = [
        (Path(WIKI_DIR) / relpath, _cosine(query_vector, entry["vector"]))
        for relpath, entry in index["articles"].items()
    ]
    return sorted(scored, key=lambda item: item[1], reverse=True)
