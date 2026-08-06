"""029 C3 — plano de reagrupamento por livro (RF-03, RF-06).

Seam: kb.regroup (plan_regroup, RegroupPlan). O critério é a proveniência do
manifest; `unresolved` nunca é movido por inferência.
"""

from pathlib import Path

from kb.regroup import plan_regroup


def _wiki(tmp_path):
    wiki = tmp_path / "wiki"
    (wiki / "algorithms").mkdir(parents=True)
    return wiki


def _artigo(wiki, rel):
    p = wiki / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("---\ntitle: T\ntopic: x\n---\ncorpo", encoding="utf-8")
    return p


def test_should_group_articles_by_book_with_slugged_destinations(tmp_path):
    wiki = _wiki(tmp_path)
    a = _artigo(wiki, "algorithms/mergesort.md")
    b = _artigo(wiki, "algorithms/quicksort.md")
    entries = [
        {"source": "library/x/l/01.md", "article": "algorithms/mergesort.md", "status": "compiled",
         "book": "Introduction to Algorithms -- Cormen -- Anna's Archive"},
        {"source": "library/x/l/02.md", "article": "algorithms/quicksort.md", "status": "compiled",
         "book": "Introduction to Algorithms -- Cormen -- Anna's Archive"},
    ]

    plan = plan_regroup(wiki, entries)

    [(book_slug, moves)] = plan.groups.items()
    assert book_slug == "introduction-to-algorithms-cormen-anna-s-archive"
    assert (a, wiki / "_chapters" / book_slug / "mergesort.md") in moves
    assert (b, wiki / "_chapters" / book_slug / "quicksort.md") in moves


def test_should_list_articles_without_provenance_as_unresolved(tmp_path):
    wiki = _wiki(tmp_path)
    sem = _artigo(wiki, "algorithms/sem-proveniencia.md")
    com = _artigo(wiki, "algorithms/com.md")
    entries = [
        {"source": "library/x/l/01.md", "article": "algorithms/com.md", "status": "compiled", "book": "Livro"},
    ]

    plan = plan_regroup(wiki, entries)

    assert sem in plan.unresolved
    assert com not in plan.unresolved


def test_should_ignore_archived_entries_and_missing_files(tmp_path):
    wiki = _wiki(tmp_path)
    vivo = _artigo(wiki, "algorithms/vivo.md")
    entries = [
        {"source": "s1", "article": "algorithms/vivo.md", "status": "compiled", "book": "Livro A"},
        {"source": "s2", "article": "algorithms/arquivado.md", "status": "archived", "book": "Livro A"},
        {"source": "s3", "article": "algorithms/sumiu.md", "status": "compiled", "book": "Livro A"},
    ]

    plan = plan_regroup(wiki, entries)

    todos = [artigo for moves in plan.groups.values() for artigo, _ in moves]
    assert todos == [vivo]


def test_should_pair_summary_mirror_when_it_exists(tmp_path):
    wiki = _wiki(tmp_path)
    _artigo(wiki, "algorithms/com-resumo.md")
    summary = wiki / "_summaries" / "algorithms" / "com-resumo.md"
    summary.parent.mkdir(parents=True)
    summary.write_text("resumo", encoding="utf-8")
    entries = [
        {"source": "s1", "article": "algorithms/com-resumo.md", "status": "compiled", "book": "Livro A"},
    ]

    plan = plan_regroup(wiki, entries)

    [(book_slug, _)] = plan.groups.items()
    assert (summary, wiki / "_summaries" / "_chapters" / book_slug / "com-resumo.md") in plan.summary_moves[book_slug]


def test_should_group_entries_without_book_under_fallback(tmp_path):
    wiki = _wiki(tmp_path)
    _artigo(wiki, "algorithms/sem-livro.md")
    entries = [
        {"source": "raw/a.md", "article": "algorithms/sem-livro.md", "status": "compiled", "book": None},
    ]

    plan = plan_regroup(wiki, entries)

    assert Path(wiki / "algorithms" / "sem-livro.md") in plan.unresolved
