"""029 C1 — helper único da convenção `_*` e sua adoção (RF-01).

Sete pontos do engine ignoravam `_*`: o heal podia deletar summary HOJE, e um
`kb archive` pós-reagrupamento arrastaria `_chapters/` inteiro para archive/.
"""

from kb.fsutil import iter_articles


def _povoa(wiki):
    (wiki / "ai").mkdir(parents=True)
    (wiki / "ai" / "vivo.md").write_text("---\ntitle: V\ntopic: ai\n---\ncorpo", encoding="utf-8")
    (wiki / "raiz.md").write_text("---\ntitle: R\ntopic: general\n---\ncorpo", encoding="utf-8")
    (wiki / "_chapters" / "livro").mkdir(parents=True)
    (wiki / "_chapters" / "livro" / "cap.md").write_text("---\ntitle: C\n---\ncapítulo", encoding="utf-8")
    (wiki / "_summaries").mkdir()
    (wiki / "_summaries" / "vivo.md").write_text("resumo", encoding="utf-8")
    (wiki / "_index.md").write_text("---\ntitle: Index\n---\n", encoding="utf-8")
    (wiki / ".heal_backup").mkdir()
    (wiki / ".heal_backup" / "velho.md").write_text("backup", encoding="utf-8")
    return {wiki / "ai" / "vivo.md", wiki / "raiz.md"}


def test_should_yield_only_live_articles(tmp_path):
    wiki = tmp_path / "wiki"
    vivos = _povoa(wiki)

    assert set(iter_articles(wiki)) == vivos


def test_should_skip_symlinks(tmp_path):
    wiki = tmp_path / "wiki"
    vivos = _povoa(wiki)
    fora = tmp_path / "fora.md"
    fora.write_text("---\ntitle: F\n---\nfora", encoding="utf-8")
    (wiki / "link.md").symlink_to(fora)

    assert set(iter_articles(wiki)) == vivos


def test_should_return_empty_for_missing_wiki(tmp_path):
    assert list(iter_articles(tmp_path / "nao-existe")) == []


class TestAdocao:
    """Cada ex-furo passa a ignorar `_*` — provado módulo a módulo."""

    def test_heal_should_never_sample_underscore_files(self, tmp_path, monkeypatch):
        import kb.heal as heal

        wiki = tmp_path / "wiki"
        _povoa(wiki)
        monkeypatch.setattr(heal, "WIKI_DIR", wiki)
        sorteados = []
        monkeypatch.setattr(heal.random, "sample", lambda pop, k: sorteados.extend(pop) or [])

        heal.heal(50)

        assert sorteados, "amostra deveria ter candidatos"
        assert all("_" not in str(p.relative_to(wiki)).split("/")[0][:1] for p in sorteados)
        assert wiki / "_summaries" / "vivo.md" not in sorteados
        assert wiki / "_chapters" / "livro" / "cap.md" not in sorteados

    def test_archive_should_not_flag_chapters_as_orphans(self, tmp_path):
        from kb.archive import find_orphans

        wiki = tmp_path / "wiki"
        _povoa(wiki)

        orfaos = find_orphans(wiki)

        assert wiki / "_chapters" / "livro" / "cap.md" not in orfaos
        assert wiki / "_summaries" / "vivo.md" not in orfaos

    def test_archive_by_age_should_ignore_underscore_files(self, tmp_path):
        import os

        from kb.archive import find_by_age

        wiki = tmp_path / "wiki"
        _povoa(wiki)
        antigo = (1, 1)
        for p in wiki.rglob("*.md"):
            os.utime(p, antigo)

        velhos = find_by_age(wiki, days=1)

        assert wiki / "_chapters" / "livro" / "cap.md" not in velhos
        assert wiki / "ai" / "vivo.md" in velhos

    def test_update_index_should_not_list_chapters(self, tmp_path, monkeypatch):
        import kb.compile as compile_mod

        wiki = tmp_path / "wiki"
        _povoa(wiki)
        monkeypatch.setattr(compile_mod, "WIKI_DIR", wiki)

        compile_mod.update_index(no_commit=True)

        index = (wiki / "_index.md").read_text(encoding="utf-8")
        assert "vivo" in index
        assert "_chapters" not in index

    def test_stats_should_not_count_chapters(self, tmp_path):
        from kb.stats import _is_ignored_article

        wiki = tmp_path / "wiki"
        _povoa(wiki)

        assert _is_ignored_article(wiki / "_chapters" / "livro" / "cap.md", wiki) is True
        assert _is_ignored_article(wiki / "ai" / "vivo.md", wiki) is False

    def test_lint_should_not_use_chapters_as_wikilink_source(self, tmp_path):
        from kb.lint import find_ambiguous_wikilinks

        wiki = tmp_path / "wiki"
        _povoa(wiki)
        # dois alvos com mesmo stem tornam o link ambíguo; a ORIGEM está em _chapters
        (wiki / "ai" / "alvo.md").write_text("---\ntitle: A\n---\nx", encoding="utf-8")
        (wiki / "alvo.md").write_text("---\ntitle: A2\n---\nx", encoding="utf-8")
        (wiki / "_chapters" / "livro" / "citador.md").write_text(
            "---\ntitle: Cit\n---\nVeja [[alvo]].", encoding="utf-8"
        )

        achados = find_ambiguous_wikilinks(wiki)

        assert achados == []
