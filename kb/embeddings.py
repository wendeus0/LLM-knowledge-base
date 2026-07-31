"""Índice de embeddings por vault (feature 012-semantic-retrieval, ADR-0013 Fase 2).

Um vetor por artigo da wiki, gerado por modelo local servido em endpoint
OpenAI-compat (`KB_EMBED_BASE_URL`; default LM Studio em localhost:1234).
Índice em kb_state/embeddings.json, incremental por hash de conteúdo.
Sem índice válido, search/qa degradam para o retrieval lexical.
"""

import hashlib
import json
import math
import os
import sys
from pathlib import Path

INDEX_FILENAME = "embeddings.json"
INDEX_FORMAT = 2
_QUERY_PREFIX = "search_query: "
_DOCUMENT_PREFIX = "search_document: "
DEFAULT_MODEL = "text-embedding-nomic-embed-text-v2-moe"
DEFAULT_BASE_URL = "http://localhost:1234/v1"


def _embed_model() -> str:
    return os.getenv("KB_EMBED_MODEL", DEFAULT_MODEL)


def _embed_base_url() -> str:
    return os.getenv("KB_EMBED_BASE_URL", DEFAULT_BASE_URL)


def embed_texts(texts: list[str], model: str | None = None, base_url: str | None = None) -> list[list[float]]:
    """Fronteira de rede: gera embeddings via endpoint OpenAI-compat local."""
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
    """(relpath, texto) dos artigos da wiki, ignorando infra `_*` e ocultos `.*`."""
    articles: list[tuple[str, str]] = []
    for md in sorted(Path(wiki_dir).rglob("*.md")):
        relative = md.relative_to(wiki_dir)
        if any(part.startswith(("_", ".")) for part in relative.parts):
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
    from kb.chunking import build_chunks
    from kb.frontmatter import parse
    from kb.fsutil import atomic_write_text

    model = _embed_model()
    articles = _iter_articles(wiki_dir)
    previous = _read_index_file(state_dir)
    reusable: dict[str, dict] = {}
    if (
        previous
        and previous.get("model") == model
        and previous.get("format") == INDEX_FORMAT
        and not force
    ):
        reusable = previous.get("articles", {})

    to_embed: list[tuple[str, int, str]] = []
    kept: dict[str, dict] = {}
    for relpath, text in articles:
        digest = _content_hash(text)
        entry = reusable.get(relpath)
        if entry and entry.get("hash") == digest:
            kept[relpath] = entry
            continue

        meta, _ = parse(text)
        title = str(meta.get("title") or Path(relpath).stem).strip()
        chunks = build_chunks(title, text, max_chars=max_chars - len(_DOCUMENT_PREFIX))
        kept[relpath] = {
            "hash": digest,
            "chunks": [{"heading": chunk["heading"]} for chunk in chunks],
        }
        for ordinal, chunk in enumerate(chunks):
            to_embed.append((relpath, ordinal, _DOCUMENT_PREFIX + chunk["text"]))

    removed = len([relpath for relpath in reusable if relpath not in dict(articles)])

    if to_embed:
        try:
            vectors = embed_texts([text for _, _, text in to_embed])
        except Exception as exc:
            from kb.embed_server import autostart_cmd

            raise RuntimeError(
                f"Falha ao gerar embeddings (modelo {model}, endpoint {_embed_base_url()}): {exc}. "
                f"Suba o servidor com `{autostart_cmd()}`, ou ajuste KB_EMBED_BASE_URL/KB_EMBED_MODEL."
            ) from exc
        for (relpath, ordinal, _), vector in zip(to_embed, vectors, strict=True):
            kept[relpath]["chunks"][ordinal]["vector"] = vector

    dim = 0
    total_chunks = 0
    for entry in kept.values():
        chunks = entry.get("chunks", [])
        total_chunks += len(chunks)
        if not dim:
            for chunk in chunks:
                if chunk.get("vector"):
                    dim = len(chunk["vector"])
                    break

    payload = {"format": INDEX_FORMAT, "model": model, "dim": dim, "articles": kept}
    Path(state_dir).mkdir(parents=True, exist_ok=True)
    atomic_write_text(Path(state_dir) / INDEX_FILENAME, json.dumps(payload, ensure_ascii=False))

    reembedded_articles = len({relpath for relpath, _, _ in to_embed})
    return {
        "indexed": reembedded_articles,
        "chunks": total_chunks,
        "embedded_chunks": len(to_embed),
        "removed": removed,
        "unchanged": len(kept) - reembedded_articles,
        "truncated": 0,
        "model": model,
        "dim": dim,
    }


_AUTO_REFRESH_OFF = ("0", "false", "off", "no")


def refresh_embeddings_index(enabled: bool = True) -> dict | None:
    """Reindexa após escrita na wiki. Efeito colateral: nunca derruba o chamador.

    Devolve o relatório de `build_index` quando roda, ou None quando foi pulado
    (desabilitado, servidor fora, ou falha do build — sempre com aviso).
    """
    if not enabled:
        return None
    if os.getenv("KB_INDEX_AUTO_REFRESH", "1").strip().lower() in _AUTO_REFRESH_OFF:
        return None

    from kb.config import STATE_DIR, WIKI_DIR
    from kb.embed_server import probe, probe_timeout

    server = probe(_embed_base_url(), probe_timeout())
    if not server.reachable:
        print(
            f"aviso: índice de embeddings não atualizado — servidor inacessível em {server.endpoint}",
            file=sys.stderr,
        )
        return None

    try:
        report = build_index(WIKI_DIR, STATE_DIR)
    except Exception as exc:
        print(f"aviso: índice de embeddings não atualizado — {exc}", file=sys.stderr)
        return None

    if report.get("indexed") or report.get("removed"):
        print(
            f"índice de embeddings: {report['indexed']} indexado(s), "
            f"{report['removed']} removido(s)",
            file=sys.stderr,
        )
    return report


def load_index(state_dir: Path) -> dict | None:
    """Índice válido para o modelo configurado, ou None (fallback lexical)."""
    payload = _read_index_file(state_dir)
    if not payload or payload.get("model") != _embed_model():
        return None
    if payload.get("format") != INDEX_FORMAT:
        return None
    articles = {
        relpath: entry
        for relpath, entry in payload.get("articles", {}).items()
        if any(chunk.get("vector") for chunk in entry.get("chunks", []))
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
    chunks = sum(len(entry.get("chunks", [])) for entry in indexed_entries.values())
    indexed = len(articles) - len(stale)
    return {
        "total": len(articles),
        "indexed": indexed,
        "chunks": chunks,
        "chunks_per_article": round(chunks / indexed, 1) if indexed else 0.0,
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


def semantic_ranking(query: str, index: dict) -> tuple[list[tuple[Path, float]], dict[Path, dict]]:
    """Ranking por cosseno + chunk vencedor por artigo; falha de embed degrada para ([], {}).

    O chunk vencedor (`{path: {"heading", "ordinal", "hash"}}`) alimenta o
    snippet do rerank quando o candidato só existe no canal semântico. O
    ordinal aponta o chunk exato (heading repetido e seção dividida não bastam
    para localizar); o hash permite detectar índice stale na extração.
    """
    from kb.config import WIKI_DIR

    try:
        query_vector = embed_texts([_QUERY_PREFIX + query])[0]
    except Exception:
        return [], {}

    scored: list[tuple[Path, float]] = []
    best_chunks: dict[Path, dict] = {}
    for relpath, entry in index["articles"].items():
        best_score = None
        best_chunk: dict = {}
        for ordinal, chunk in enumerate(entry.get("chunks", [])):
            if not chunk.get("vector"):
                continue
            similarity = _cosine(query_vector, chunk["vector"])
            if best_score is None or similarity > best_score:
                best_score = similarity
                best_chunk = {
                    "heading": chunk.get("heading", ""),
                    "ordinal": ordinal,
                    "hash": entry.get("hash", ""),
                }
        if best_score is None:
            continue
        # Máximo, não soma: artigo longo não deve pontuar mais por ter mais seções.
        path = Path(WIKI_DIR) / relpath
        scored.append((path, best_score))
        best_chunks[path] = best_chunk

    ranking = sorted(scored, key=lambda item: item[1], reverse=True)
    return ranking, best_chunks
