"""Reagrupamento dos artigos de capítulo por livro (feature 029, C3).

O critério é a proveniência do manifest (ADR-0018: proveniência, não cosseno).
Artigo sem entrada viva com `book` é `unresolved` — permanece na wiki como
pendência humana e NUNCA é movido por inferência.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path


def _slug_book(book: str) -> str:
    from kb.book_import_core import slugify

    slug = slugify(book)
    slug = re.sub(r"-{2,}", "-", slug).strip("-")
    return slug or "livro-sem-nome"


@dataclass
class RegroupPlan:
    groups: dict[str, list[tuple[Path, Path]]] = field(default_factory=dict)
    summary_moves: dict[str, list[tuple[Path, Path]]] = field(default_factory=dict)
    unresolved: list[Path] = field(default_factory=list)
    book_names: dict[str, str] = field(default_factory=dict)


def plan_regroup(wiki_dir: Path, manifest_entries: list[dict]) -> RegroupPlan:
    """Plano de move `wiki/<...> → wiki/_chapters/<livro>/`, sem executar nada."""
    from kb.fsutil import iter_articles

    wiki_dir = Path(wiki_dir)
    plan = RegroupPlan()
    por_artigo: dict[Path, str] = {}
    for entry in manifest_entries:
        if entry.get("status") == "archived" or not entry.get("article"):
            continue
        book = entry.get("book")
        if not book:
            continue
        artigo = wiki_dir / entry["article"]
        if artigo.exists():
            por_artigo.setdefault(artigo, book)

    for artigo in iter_articles(wiki_dir):
        book = por_artigo.get(artigo)
        if book is None:
            plan.unresolved.append(artigo)
            continue
        slug = _slug_book(book)
        plan.book_names.setdefault(slug, book)
        destino = wiki_dir / "_chapters" / slug / artigo.name
        plan.groups.setdefault(slug, []).append((artigo, destino))
        summary = wiki_dir / "_summaries" / artigo.relative_to(wiki_dir)
        if summary.exists():
            plan.summary_moves.setdefault(slug, []).append(
                (summary, wiki_dir / "_summaries" / "_chapters" / slug / artigo.name)
            )
    return plan


def apply_book(wiki_dir: Path, plan: RegroupPlan, book_slug: str) -> list[dict]:
    """Move os artigos (e summaries) de um livro, atualizando o manifest.

    Reusa `move_to_archive` com raiz de contenção em `_chapters/` — mesma
    semântica de backup versionado, outra raiz.
    """
    from kb.archive import move_to_archive
    from kb.compile import update_index
    from kb.embeddings import refresh_embeddings_index
    from kb.state import update_article_path

    wiki_dir = Path(wiki_dir)
    moves = [
        {"source": origem, "dest": destino}
        for origem, destino in plan.groups.get(book_slug, [])
    ]
    log = move_to_archive(moves, wiki_dir / "_chapters")
    for entry in log:
        if entry["action"] == "moved":
            update_article_path(Path(entry["source"]), Path(entry["dest"]))
    summary_moves = [
        {"source": origem, "dest": destino}
        for origem, destino in plan.summary_moves.get(book_slug, [])
    ]
    if summary_moves:
        log += move_to_archive(summary_moves, wiki_dir / "_summaries" / "_chapters")
    if any(entry["action"] == "moved" for entry in log):
        update_index(no_commit=True)
        refresh_embeddings_index()
    return log
