"""RED — feature 014 RF-05: degradação para lexical deixa de ser silenciosa.

O fallback continua sendo o comportamento (contrato da 012, RF-05); o que muda
é que ele passa a ser anunciado uma vez por execução, em stderr.
"""

from kb import search as search_module


def _seed(tmp_path, monkeypatch):
    wiki = tmp_path / "wiki"
    state = tmp_path / "kb_state"
    wiki.mkdir()
    state.mkdir()
    (wiki / "artigo.md").write_text(
        "---\ntitle: Artigo\n---\n\nConteúdo sobre resiliência.\n", encoding="utf-8"
    )
    monkeypatch.setattr("kb.search.WIKI_DIR", wiki)
    monkeypatch.setattr("kb.config.STATE_DIR", state)
    monkeypatch.setattr(search_module, "_semantic_warned", False, raising=False)
    return wiki, state


class TestDegradationWarning:
    def test_should_warn_on_stderr_when_semantic_index_absent(
        self, tmp_path, monkeypatch, capsys
    ):
        _seed(tmp_path, monkeypatch)

        results = search_module.search("resiliência")

        captured = capsys.readouterr()
        assert results, "busca lexical deve continuar funcionando"
        assert "semântic" in captured.err.lower()

    def test_should_warn_only_once_per_execution(self, tmp_path, monkeypatch, capsys):
        _seed(tmp_path, monkeypatch)

        search_module.search("resiliência")
        search_module.search("resiliência")

        captured = capsys.readouterr()
        assert captured.err.lower().count("semântic") == 1

    def test_should_not_warn_when_semantic_channel_available(
        self, tmp_path, monkeypatch, capsys
    ):
        wiki, _ = _seed(tmp_path, monkeypatch)
        monkeypatch.setattr(
            "kb.search._semantic_rank",
            lambda query: [(wiki / "artigo.md", 0.9)],
        )

        search_module.search("resiliência")

        captured = capsys.readouterr()
        assert captured.err == ""
