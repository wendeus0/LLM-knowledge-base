"""RED — feature 016: modos de busca precisam ser explícitos e verificáveis.

Sem um modo que desligue o canal semântico, não há como comparar "com" e "sem"
— e um modo desconhecido caindo em híbrido produz medição errada em silêncio.
"""

import pytest

from kb import search as search_module


def _seed(tmp_path, monkeypatch):
    wiki = tmp_path / "wiki"
    wiki.mkdir()
    (wiki / "alvo.md").write_text(
        "---\ntitle: Alvo\n---\n\nresiliencia de sistemas\n", encoding="utf-8"
    )
    (wiki / "outro.md").write_text(
        "---\ntitle: Outro\n---\n\nassunto distinto\n", encoding="utf-8"
    )
    monkeypatch.setattr("kb.search.WIKI_DIR", wiki)
    monkeypatch.setattr(search_module, "_semantic_warned", False, raising=False)
    return wiki


class TestSearchModes:
    def test_should_not_consult_semantic_channel_in_lexical_mode(
        self, tmp_path, monkeypatch
    ):
        _seed(tmp_path, monkeypatch)
        calls = []
        monkeypatch.setattr(
            search_module, "_semantic_rank", lambda query: calls.append(query) or []
        )

        search_module.search("resiliencia", mode="lexical")

        assert calls == []

    def test_should_consult_semantic_channel_in_hybrid_mode(self, tmp_path, monkeypatch):
        _seed(tmp_path, monkeypatch)
        calls = []
        monkeypatch.setattr(
            search_module, "_semantic_rank", lambda query: calls.append(query) or []
        )

        search_module.search("resiliencia", mode="hybrid")

        assert calls == ["resiliencia"]

    def test_should_reject_unknown_mode_instead_of_silently_using_hybrid(
        self, tmp_path, monkeypatch
    ):
        _seed(tmp_path, monkeypatch)

        with pytest.raises(ValueError) as exc:
            search_module.search("resiliencia", mode="modo-inexistente")

        assert "modo-inexistente" in str(exc.value)
