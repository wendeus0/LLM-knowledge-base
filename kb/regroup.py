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
    conflitantes: set[Path] = set()
    for entry in manifest_entries:
        if entry.get("status") == "archived" or not entry.get("article"):
            continue
        book = entry.get("book")
        if not book:
            continue
        artigo = wiki_dir / entry["article"]
        if not artigo.exists():
            continue
        if artigo in por_artigo and por_artigo[artigo] != book:
            # Duas entradas, dois livros: inferir um é chute — braço humano.
            conflitantes.add(artigo)
            continue
        por_artigo.setdefault(artigo, book)
    for artigo in conflitantes:
        por_artigo.pop(artigo, None)

    for artigo in iter_articles(wiki_dir):
        book = por_artigo.get(artigo)
        if book is None:
            plan.unresolved.append(artigo)
            continue
        slug = _slug_book(book)
        plan.book_names.setdefault(slug, book)
        destino = wiki_dir / "_chapters" / slug / artigo.name
        ocupados = {d for _, d in plan.groups.get(slug, [])}
        if destino in ocupados:
            # Basename colidiu dentro do livro: desambiguar pelo diretório de
            # origem — mover por cima criaria backup silencioso do primeiro.
            prefixo = "-".join(artigo.relative_to(wiki_dir).parts[:-1]) or "raiz"
            destino = wiki_dir / "_chapters" / slug / f"{prefixo}-{artigo.name}"
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
    # Preflight do lote inteiro antes de mover qualquer coisa: origem ausente
    # ou destino ocupado abortam o livro por completo — falha parcial é o modo
    # de erro caro (review PR #71).
    problemas = [
        m for m in moves
        if not m["source"].exists() or m["dest"].exists()
    ]
    if problemas:
        return [
            {"source": str(m["source"]), "dest": str(m["dest"]), "action": "error",
             "detail": "preflight: origem ausente ou destino ocupado"}
            for m in problemas
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
