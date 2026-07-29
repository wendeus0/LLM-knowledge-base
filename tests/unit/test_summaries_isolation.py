"""Sumários vivem sob `_summaries/` para herdar a exclusão da convenção `_*`.

Sem isso, cada artigo compete com o resumo de si mesmo no ranking semântico
e no lexical — no vault real eram 1.022 sumários contra 1.037 artigos.
"""

from kb.compile import _summary_path
from kb.embeddings import _iter_articles
from kb.search import search


class TestSummariesIsolation:
    def test_should_store_summary_under_underscore_dir_when_article_compiled(
        self, tmp_raw_wiki
    ):
        _, wiki = tmp_raw_wiki
        article = wiki / "ai" / "artigo.md"
        article.write_text("# Artigo\n", encoding="utf-8")

        summary = _summary_path(article)

        assert summary.parent.relative_to(wiki).parts[0] == "_summaries"

    def test_should_exclude_summaries_from_index_when_scanning_wiki(self, tmp_raw_wiki):
        _, wiki = tmp_raw_wiki
        article = wiki / "ai" / "artigo.md"
        article.write_text("# Artigo sobre circuit breaker\n", encoding="utf-8")
        summary = _summary_path(article)
        summary.write_text("# Summary — Artigo\n", encoding="utf-8")

        indexed = [relpath for relpath, _ in _iter_articles(wiki)]

        assert "ai/artigo.md" in indexed
        assert str(summary.relative_to(wiki)) not in indexed

    def test_should_exclude_hidden_dirs_from_both_corpora(self, tmp_raw_wiki):
        _, wiki = tmp_raw_wiki
        (wiki / "ai" / "artigo.md").write_text(
            "---\ntitle: Artigo\n---\n\nresiliencia\n", encoding="utf-8"
        )
        for hidden in (".heal_backup", ".obsidian"):
            (wiki / hidden).mkdir(exist_ok=True)
            (wiki / hidden / "copia.md").write_text(
                "---\ntitle: Copia\n---\n\nresiliencia\n", encoding="utf-8"
            )

        indexed = [relpath for relpath, _ in _iter_articles(wiki)]
        found = [str(item["path"]) for item in search("resiliencia")]

        assert "ai/artigo.md" in indexed
        assert not any(relpath.startswith(".") for relpath in indexed)
        assert not any(".heal_backup" in path or ".obsidian" in path for path in found)

    def test_should_exclude_infra_dirs_from_lexical_search(self, tmp_raw_wiki):
        _, wiki = tmp_raw_wiki
        article = wiki / "ai" / "artigo.md"
        article.write_text("---\ntitle: Artigo\n---\n\nresiliencia\n", encoding="utf-8")
        summary = _summary_path(article)
        summary.write_text("---\ntitle: Resumo\n---\n\nresiliencia\n", encoding="utf-8")
        sources = wiki / "_sources"
        sources.mkdir(exist_ok=True)
        (sources / "fonte.md").write_text(
            "---\ntitle: Fonte\n---\n\nresiliencia\n", encoding="utf-8"
        )

        found = [str(item["path"]) for item in search("resiliencia")]

        assert any(str(article) == path for path in found)
        assert not any("_summaries" in path for path in found)
        assert not any("_sources" in path for path in found)
