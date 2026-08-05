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


def _fingerprint(wiki_dir: Path) -> tuple:
    """Assinatura do corpus: identifica mudança sem reler o conteúdo.

    O `lru_cache` do índice era invalidado só por reinício do processo — artigo
    novo, editado ou apagado não aparecia até derrubar a API. `stat` de N
    arquivos custa ordens de grandeza menos que a leitura de N arquivos que o
    cálculo de backlinks fazia por requisição.
    """
    if not wiki_dir.is_dir():
        return ()
    entradas = []
    for path in wiki_dir.rglob("*.md"):
        if path.is_symlink():
            continue
        try:
            info = path.stat()
        except OSError:
            # O corpus é do usuário e `compile`/`heal` mexem nele em paralelo:
            # arquivo que some entre o rglob e o stat sai da assinatura em vez
            # de derrubar a requisição.
            continue
        entradas.append((path.relative_to(wiki_dir).as_posix(), info.st_mtime_ns, info.st_size))
    return tuple(sorted(entradas))


@lru_cache(maxsize=4)
def _build_index(wiki_dir: str, fingerprint: tuple) -> dict:
    """Índice de wikilinks mais o mapa de backlinks já invertido, por slug."""
    caminho = Path(wiki_dir)
    index = graph.build_link_index(caminho)
    backlinks: dict[str, set[str]] = {}
    for candidate in index["por_slug"].values():
        origem = rel_slug(candidate, caminho)
        try:
            content = candidate.read_text(encoding="utf-8", errors="replace")
        except OSError:
            # Mesma corrida do `_fingerprint`: o arquivo pode ter sumido entre a
            # varredura e a leitura. Ele fica fora dos backlinks desta versão do
            # índice, que a próxima requisição já reconstrói.
            continue
        for link in graph.extract_wikilinks(content):
            for alvo in graph.resolve_wikilink_all(link, caminho, index):
                backlinks.setdefault(rel_slug(alvo, caminho), set()).add(origem)
    return {**index, "backlinks": {slug: sorted(origens) for slug, origens in backlinks.items()}}


def _index_for(wiki_dir: Path) -> dict:
    return _build_index(str(wiki_dir), _fingerprint(wiki_dir))


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
    # `with_suffix` trocaria a extensão pelo que vem depois do último ponto do
    # slug: `ai/gpt-4.5` viraria `ai/gpt-4.md`.
    candidate = wiki_dir.joinpath(*parts[:-1], f"{parts[-1]}.md")
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
        "backlinks": index["backlinks"].get(rel_slug(candidate, wiki_dir), []),
    }
