"""RED — feature 018 RF-03: expansão alimenta só o canal semântico.

Os canais lexicais continuam com a pergunta original: eles funcionam por
casamento de termo, e diluí-los com vocabulário inventado pelo LLM degradaria
o que hoje acerta.
"""

from kb import search as search_module


def _seed(tmp_path, monkeypatch):
    wiki = tmp_path / "wiki"
    wiki.mkdir()
    (wiki / "grafos.md").write_text(
        "---\ntitle: Grafos\n---\n\ncaminho minimo em grafos ponderados\n", encoding="utf-8"
    )
    monkeypatch.setattr("kb.search.WIKI_DIR", wiki)
    monkeypatch.setattr(search_module, "_semantic_warned", False, raising=False)
    return wiki


class TestSearchExpansion:
    def test_should_send_expanded_query_only_to_semantic_channel(self, tmp_path, monkeypatch):
        _seed(tmp_path, monkeypatch)
        semantic_seen = []
        lexical_seen = []

        monkeypatch.setattr(
            search_module, "_semantic_rank", lambda q: semantic_seen.append(q) or []
        )
        original_build = search_module._build_rankings
        monkeypatch.setattr(
            search_module,
            "_build_rankings",
            lambda q: lexical_seen.append(q) or original_build(q),
        )
        monkeypatch.setattr(
            "kb.query_expansion.expand_query", lambda q, s: f"{q} DIJKSTRA"
        )

        search_module.search("trajeto barato", mode="hybrid", expand="terms")

        assert semantic_seen == ["trajeto barato DIJKSTRA"]
        assert lexical_seen == ["trajeto barato"]

    def test_should_not_expand_when_flag_absent(self, tmp_path, monkeypatch):
        _seed(tmp_path, monkeypatch)
        calls = []
        monkeypatch.setattr(search_module, "_semantic_rank", lambda q: calls.append(q) or [])
        monkeypatch.setattr(
            "kb.query_expansion.expand_query",
            lambda q, s: (_ for _ in ()).throw(AssertionError("não deveria expandir")),
        )

        search_module.search("trajeto barato", mode="hybrid")

        assert calls == ["trajeto barato"]

    def test_should_not_expand_in_lexical_mode(self, tmp_path, monkeypatch):
        _seed(tmp_path, monkeypatch)
        monkeypatch.setattr(
            "kb.query_expansion.expand_query",
            lambda q, s: (_ for _ in ()).throw(AssertionError("não deveria expandir")),
        )

        results = search_module.search("trajeto barato", mode="lexical", expand="terms")

        assert isinstance(results, list)
