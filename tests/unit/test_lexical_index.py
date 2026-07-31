"""RED — índice lexical persistente (P2 de memory/next_steps.md).

Seams: kb.lexical_index (build_index, lexical_corpus). O índice vive em
<state_dir>/lexical.json, é incremental por hash de conteúdo e nunca pode
quebrar a busca: ausente, corrompido, de outra versão ou não-gravável, o
chamador cai para a leitura direta da wiki.
"""

import json

import pytest

from kb.lexical_index import INDEX_FILENAME, INDEX_FORMAT, build_index, lexical_corpus


@pytest.fixture
def auto_refresh_on(monkeypatch):
    """A suíte desliga o auto-refresh por default; estes testes o exercitam."""
    monkeypatch.delenv("KB_INDEX_AUTO_REFRESH", raising=False)


def _make_wiki(tmp_path):
    wiki = tmp_path / "wiki"
    state = tmp_path / "kb_state"
    wiki.mkdir()
    state.mkdir()
    (wiki / "xss.md").write_text("# XSS\n\nXSS é uma vulnerabilidade web comum.\n", encoding="utf-8")
    (wiki / "sqli.md").write_text("# SQLi\n\nInjeção de SQL em query dinâmica.\n", encoding="utf-8")
    (wiki / "_infra.md").write_text("# Infra\n\nArquivo de infraestrutura ignorado.\n", encoding="utf-8")
    return wiki, state


class TestBuildIndex:
    def test_should_write_index_file_in_state_dir(self, tmp_path):
        wiki, state = _make_wiki(tmp_path)

        build_index(wiki, state)

        payload = json.loads((state / INDEX_FILENAME).read_text(encoding="utf-8"))
        assert payload["format"] == INDEX_FORMAT
        assert set(payload["docs"]) == {"xss.md", "sqli.md"}

    def test_should_store_term_frequency_and_length(self, tmp_path):
        wiki, state = _make_wiki(tmp_path)

        build_index(wiki, state)

        entry = json.loads((state / INDEX_FILENAME).read_text(encoding="utf-8"))["docs"]["xss.md"]
        assert entry["tf"]["xss"] == 2
        assert entry["length"] == 7
        assert entry["hash"]

    def test_should_reuse_unchanged_entries_on_second_build(self, tmp_path):
        wiki, state = _make_wiki(tmp_path)
        build_index(wiki, state)

        report = build_index(wiki, state)

        assert report["indexed"] == 0
        assert report["unchanged"] == 2

    def test_should_reindex_only_the_changed_article(self, tmp_path):
        wiki, state = _make_wiki(tmp_path)
        build_index(wiki, state)
        (wiki / "xss.md").write_text("# XSS\n\nAgora fala de sanitização.\n", encoding="utf-8")

        report = build_index(wiki, state)

        assert report["indexed"] == 1
        assert report["unchanged"] == 1

    def test_should_drop_removed_article_from_index(self, tmp_path):
        wiki, state = _make_wiki(tmp_path)
        build_index(wiki, state)
        (wiki / "sqli.md").unlink()

        report = build_index(wiki, state)

        payload = json.loads((state / INDEX_FILENAME).read_text(encoding="utf-8"))
        assert report["removed"] == 1
        assert set(payload["docs"]) == {"xss.md"}

    def test_should_ignore_previous_index_of_other_format(self, tmp_path):
        wiki, state = _make_wiki(tmp_path)
        build_index(wiki, state)
        stale = json.loads((state / INDEX_FILENAME).read_text(encoding="utf-8"))
        stale["format"] = INDEX_FORMAT + 99
        (state / INDEX_FILENAME).write_text(json.dumps(stale), encoding="utf-8")

        report = build_index(wiki, state)

        assert report["indexed"] == 2
        assert report["unchanged"] == 0

    def test_should_reindex_everything_when_forced(self, tmp_path):
        wiki, state = _make_wiki(tmp_path)
        build_index(wiki, state)

        report = build_index(wiki, state, force=True)

        assert report["indexed"] == 2


class TestLexicalCorpus:
    def test_should_return_none_when_index_missing_and_auto_refresh_off(self, tmp_path, monkeypatch):
        wiki, state = _make_wiki(tmp_path)
        monkeypatch.setenv("KB_INDEX_AUTO_REFRESH", "0")

        assert lexical_corpus(wiki, state) is None
        assert not (state / INDEX_FILENAME).exists()

    def test_should_build_index_on_first_use_when_auto_refresh_on(self, tmp_path, auto_refresh_on):
        wiki, state = _make_wiki(tmp_path)

        docs = lexical_corpus(wiki, state)

        assert set(docs) == {"xss.md", "sqli.md"}
        assert (state / INDEX_FILENAME).exists()

    def test_should_return_none_when_index_is_corrupt_and_auto_refresh_off(self, tmp_path, monkeypatch):
        wiki, state = _make_wiki(tmp_path)
        (state / INDEX_FILENAME).write_text("{lixo", encoding="utf-8")
        monkeypatch.setenv("KB_INDEX_AUTO_REFRESH", "0")

        assert lexical_corpus(wiki, state) is None

    def test_should_rebuild_when_index_is_corrupt_and_auto_refresh_on(self, tmp_path, auto_refresh_on):
        wiki, state = _make_wiki(tmp_path)
        (state / INDEX_FILENAME).write_text("{lixo", encoding="utf-8")

        docs = lexical_corpus(wiki, state)

        assert set(docs) == {"xss.md", "sqli.md"}

    def test_should_refresh_stale_entry_when_article_changes(self, tmp_path, auto_refresh_on):
        wiki, state = _make_wiki(tmp_path)
        lexical_corpus(wiki, state)
        (wiki / "xss.md").write_text("# XSS\n\nsanitizacao sanitizacao sanitizacao\n", encoding="utf-8")

        docs = lexical_corpus(wiki, state)

        assert docs["xss.md"]["tf"]["sanitizacao"] == 3
        assert "vulnerabilidade" not in docs["xss.md"]["tf"]

    def test_should_return_none_for_stale_index_when_auto_refresh_off(self, tmp_path, monkeypatch):
        wiki, state = _make_wiki(tmp_path)
        monkeypatch.delenv("KB_INDEX_AUTO_REFRESH", raising=False)
        lexical_corpus(wiki, state)
        (wiki / "novo.md").write_text("# Novo\n\nartigo novo\n", encoding="utf-8")
        monkeypatch.setenv("KB_INDEX_AUTO_REFRESH", "0")

        assert lexical_corpus(wiki, state) is None

    def test_should_serve_corpus_even_when_state_dir_is_not_writable(self, tmp_path, auto_refresh_on):
        wiki, state = _make_wiki(tmp_path)
        state.chmod(0o500)
        try:
            docs = lexical_corpus(wiki, state)
        finally:
            state.chmod(0o700)

        assert set(docs) == {"xss.md", "sqli.md"}

    def test_should_ignore_index_of_other_format_when_auto_refresh_off(self, tmp_path, monkeypatch):
        wiki, state = _make_wiki(tmp_path)
        legacy = {"format": INDEX_FORMAT + 99, "docs": {"xss.md": {"length": 1, "tf": {"xss": 1}}}}
        (state / INDEX_FILENAME).write_text(json.dumps(legacy), encoding="utf-8")
        monkeypatch.setenv("KB_INDEX_AUTO_REFRESH", "0")

        assert lexical_corpus(wiki, state) is None
