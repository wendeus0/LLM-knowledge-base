"""RED — feature 020: reordenar o top-N com julgamento do LLM.

O que precisa ser à prova de bala é o parsing: o modelo devolve texto, e uma
resposta malformada não pode fazer resultado sumir nem quebrar a busca.
"""

import pytest

from kb import rerank as rerank_module


@pytest.fixture
def _state(tmp_path, monkeypatch):
    state = tmp_path / "kb_state"
    state.mkdir()
    monkeypatch.setattr("kb.config.STATE_DIR", state)
    monkeypatch.setenv("KB_MODEL", "modelo-teste")
    return state


CANDIDATES = [
    {"slug": "alpha", "title": "Alpha", "snippet": "sobre alpha"},
    {"slug": "bravo", "title": "Bravo", "snippet": "sobre bravo"},
    {"slug": "charlie", "title": "Charlie", "snippet": "sobre charlie"},
]


class TestParseOrder:
    def test_should_parse_clean_list(self):
        assert rerank_module.parse_order("3, 1, 2", 3) == [2, 0, 1]

    def test_should_parse_list_with_noise(self):
        resposta = "Claro! A ordem mais relevante é: 2, 3 e depois 1."

        assert rerank_module.parse_order(resposta, 3) == [1, 2, 0]

    def test_should_drop_out_of_range_indexes(self):
        assert rerank_module.parse_order("1, 99, 2", 3) == [0, 1]

    def test_should_drop_duplicates_keeping_first(self):
        assert rerank_module.parse_order("2, 2, 1", 3) == [1, 0]

    def test_should_return_empty_for_unparseable_answer(self):
        assert rerank_module.parse_order("não sei responder", 3) == []


class TestRerank:
    def test_should_reorder_by_llm_judgement(self, _state, monkeypatch):
        monkeypatch.setattr(rerank_module, "_call_llm", lambda messages: "3, 1, 2")

        ordered = rerank_module.rerank("pergunta", CANDIDATES)

        assert [c["slug"] for c in ordered] == ["charlie", "alpha", "bravo"]

    def test_should_append_omitted_candidates_in_original_order(self, _state, monkeypatch):
        monkeypatch.setattr(rerank_module, "_call_llm", lambda messages: "3")

        ordered = rerank_module.rerank("pergunta", CANDIDATES)

        assert [c["slug"] for c in ordered] == ["charlie", "alpha", "bravo"]
        assert len(ordered) == 3

    def test_should_keep_original_order_when_llm_fails(self, _state, monkeypatch, capsys):
        def _boom(messages):
            raise RuntimeError("provider fora")

        monkeypatch.setattr(rerank_module, "_call_llm", _boom)

        ordered = rerank_module.rerank("pergunta", CANDIDATES)

        assert [c["slug"] for c in ordered] == ["alpha", "bravo", "charlie"]
        assert "rerank" in capsys.readouterr().err.lower()

    def test_should_keep_original_order_when_answer_unparseable(self, _state, monkeypatch):
        monkeypatch.setattr(rerank_module, "_call_llm", lambda messages: "sei lá")

        ordered = rerank_module.rerank("pergunta", CANDIDATES)

        assert [c["slug"] for c in ordered] == ["alpha", "bravo", "charlie"]

    def test_should_never_lose_a_candidate(self, _state, monkeypatch):
        monkeypatch.setattr(rerank_module, "_call_llm", lambda messages: "2")

        ordered = rerank_module.rerank("pergunta", CANDIDATES)

        assert {c["slug"] for c in ordered} == {"alpha", "bravo", "charlie"}

    def test_should_not_call_llm_twice_for_same_input(self, _state, monkeypatch):
        calls = []
        monkeypatch.setattr(
            rerank_module, "_call_llm", lambda messages: calls.append(1) or "1, 2, 3"
        )

        rerank_module.rerank("pergunta", CANDIDATES)
        rerank_module.rerank("pergunta", CANDIDATES)

        assert len(calls) == 1
