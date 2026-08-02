"""Leitura segura de artigos por `rel_slug`."""

import re
from functools import lru_cache
from pathlib import Path

from kb import config, graph
from kb.frontmatter import parse
from kb.search import rel_slug


class InvalidArticleSlug(ValueError):
    """Slug que não identifica um artigo da wiki."""


_SEGMENT = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


def _validate_slug(slug: str) -> list[str]:
    if not slug or slug.startswith("/") or "\\" in slug or slug.endswith(".md"):
        raise InvalidArticleSlug
    parts = slug.split("/")
    if any(part in {"", ".", ".."} or not _SEGMENT.fullmatch(part) for part in parts):
        raise InvalidArticleSlug
    return parts


@lru_cache(maxsize=16)
def _build_index(wiki_dir: str) -> dict:
    return graph.build_link_index(Path(wiki_dir))


def _index_for(wiki_dir: Path) -> dict:
    return _build_index(str(wiki_dir.resolve()))


def _backlinks(path: Path, wiki_dir: Path, index: dict) -> list[str]:
    linked_by: list[str] = []
    for candidate in index["por_slug"].values():
        content = candidate.read_text(encoding="utf-8", errors="replace")
        for link in graph.extract_wikilinks(content):
            if path in graph.resolve_wikilink_all(link, wiki_dir, index):
                linked_by.append(rel_slug(candidate, wiki_dir))
                break
    return sorted(linked_by)


def _wikilinks(content: str, wiki_dir: Path, index: dict) -> list[dict]:
    """Wikilinks do artigo já resolvidos, para o leitor navegar.

    Ambíguo devolve os dois alvos e a marca — a tela decide o que fazer, em vez
    de receber um dos dois sem saber que havia escolha.
    """
    saida = []
    for texto in graph.extract_wikilinks(content):
        alvos = graph.resolve_wikilink_all(texto, wiki_dir, index)
        saida.append(
            {
                "text": texto,
                "targets": [rel_slug(p, wiki_dir) for p in alvos],
                "ambiguous": len(alvos) > 1,
            }
        )
    return saida


def article_summary(path: Path, wiki_dir: Path) -> dict:
    """Título e topic de um artigo, para apresentar resultado de busca."""
    metadata, _ = parse(path.read_text(encoding="utf-8", errors="replace"))
    partes = path.relative_to(wiki_dir).parts
    return {
        "title": metadata.get("title") or path.stem,
        "topic": metadata.get("topic") or (partes[0] if len(partes) > 1 else "general"),
    }


SORTS = ("recent", "title")


def list_articles(topic: str | None = None, limit: int | None = None, sort: str = "recent") -> list[dict]:
    """Artigos da wiki para a home e para a sidebar.

    Derivados (`_summaries/`, `_sources/`, `_index.md`) ficam de fora pela mesma
    convenção `_*` que a busca já aplica.
    """
    if sort not in SORTS:
        raise ValueError(f"sort inválido: {sort}")
    wiki_dir = config.WIKI_DIR
    if not wiki_dir.exists():
        return []
    encontrados = []
    for path in wiki_dir.rglob("*.md"):
        if path.is_symlink() or any(
            part.startswith(("_", ".")) for part in path.relative_to(wiki_dir).parts
        ):
            continue
        resumo = article_summary(path, wiki_dir)
        if topic and resumo["topic"] != topic:
            continue
        encontrados.append(
            {"slug": rel_slug(path, wiki_dir), **resumo, "mtime": path.stat().st_mtime}
        )
    if sort == "title":
        encontrados.sort(key=lambda a: a["title"].lower())
    else:
        encontrados.sort(key=lambda a: a["mtime"], reverse=True)
    for item in encontrados:
        item.pop("mtime")
    return encontrados[:limit] if limit else encontrados


def get_article(slug: str) -> dict | None:
    """Devolve um artigo serializável, ou None quando não existe."""
    parts = _validate_slug(slug)
    wiki_dir = config.WIKI_DIR
    candidate = wiki_dir.joinpath(*parts).with_suffix(".md")
    try:
        candidate.resolve().relative_to(wiki_dir.resolve())
    except ValueError as exc:
        raise InvalidArticleSlug from exc
    if not candidate.is_file() or candidate.is_symlink():
        return None

    text = candidate.read_text(encoding="utf-8", errors="replace")
    metadata, content = parse(text)
    index = _index_for(wiki_dir)
    topic = metadata.get("topic") or (parts[0] if len(parts) > 1 else "general")
    tags = metadata.get("tags") or []
    return {
        "slug": rel_slug(candidate, wiki_dir),
        "title": metadata.get("title") or candidate.stem,
        "topic": topic,
        "tags": tags if isinstance(tags, list) else [],
        "source": metadata.get("source") or None,
        "content": content,
        "wikilinks": _wikilinks(content, wiki_dir, index),
        "backlinks": _backlinks(candidate, wiki_dir, index),
    }
