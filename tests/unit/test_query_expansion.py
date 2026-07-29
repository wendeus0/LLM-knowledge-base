"""RED — feature 018: reescrever a pergunta no vocabulário do corpus.

`chat` é a única fronteira; nenhum teste toca rede. O que se verifica aqui é
o contrato: preservar a pergunta original, cachear, e nunca quebrar a busca.
"""

import json

import pytest

from kb import query_expansion


@pytest.fixture
def _state(tmp_path, monkeypatch):
    state = tmp_path / "kb_state"
    state.mkdir()
    monkeypatch.setattr("kb.config.STATE_DIR", state)
    monkeypatch.setenv("KB_MODEL", "modelo-teste")
    return state


class TestExpandQuery:
    def test_should_keep_original_terms_in_terms_strategy(self, _state, monkeypatch):
        monkeypatch.setattr(
            query_expansion, "chat", lambda messages: "grafos, caminho mínimo, Dijkstra"
        )

        expanded = query_expansion.expand_query("trajeto mais barato numa rede", "terms")

        assert "trajeto mais barato numa rede" in expanded
        assert "Dijkstra" in expanded

    def test_should_use_generated_passage_in_hyde_strategy(self, _state, monkeypatch):
        monkeypatch.setattr(
            query_expansion,
            "chat",
            lambda messages: "O algoritmo de Dijkstra encontra caminhos mínimos em grafos ponderados.",
        )

        expanded = query_expansion.expand_query("trajeto mais barato numa rede", "hyde")

        assert "Dijkstra" in expanded
        assert len(expanded) > len("trajeto mais barato numa rede")

    def test_should_fall_back_to_original_when_llm_fails(self, _state, monkeypatch, capsys):
        def _boom(messages):
            raise RuntimeError("provider fora")

        monkeypatch.setattr(query_expansion, "chat", _boom)

        expanded = query_expansion.expand_query("pergunta original", "terms")

        assert expanded == "pergunta original"
        assert "expans" in capsys.readouterr().err.lower()

    def test_should_fall_back_to_original_when_llm_returns_empty(self, _state, monkeypatch):
        monkeypatch.setattr(query_expansion, "chat", lambda messages: "   ")

        assert query_expansion.expand_query("pergunta original", "terms") == "pergunta original"

    def test_should_reject_unknown_strategy(self, _state):
        with pytest.raises(ValueError) as exc:
            query_expansion.expand_query("q", "inexistente")

        assert "inexistente" in str(exc.value)


class TestCache:
    def test_should_not_call_llm_twice_for_same_question(self, _state, monkeypatch):
        calls = []
        monkeypatch.setattr(
            query_expansion, "chat", lambda messages: calls.append(1) or "termo tecnico"
        )

        query_expansion.expand_query("mesma pergunta", "terms")
        query_expansion.expand_query("mesma pergunta", "terms")

        assert len(calls) == 1

    def test_should_persist_cache_between_processes(self, _state, monkeypatch):
        monkeypatch.setattr(query_expansion, "chat", lambda messages: "termo tecnico")
        query_expansion.expand_query("pergunta", "terms")

        payload = json.loads((_state / "query_expansion.json").read_text(encoding="utf-8"))

        assert payload

    def test_should_miss_cache_when_model_changes(self, _state, monkeypatch):
        calls = []
        monkeypatch.setattr(
            query_expansion, "chat", lambda messages: calls.append(1) or "termo"
        )

        query_expansion.expand_query("pergunta", "terms")
        monkeypatch.setenv("KB_MODEL", "outro-modelo")
        query_expansion.expand_query("pergunta", "terms")

        assert len(calls) == 2

    def test_should_miss_cache_when_strategy_changes(self, _state, monkeypatch):
        calls = []
        monkeypatch.setattr(
            query_expansion, "chat", lambda messages: calls.append(1) or "termo"
        )

        query_expansion.expand_query("pergunta", "terms")
        query_expansion.expand_query("pergunta", "hyde")

        assert len(calls) == 2

    def test_should_survive_corrupted_cache(self, _state, monkeypatch):
        (_state / "query_expansion.json").write_text("{ invalido", encoding="utf-8")
        monkeypatch.setattr(query_expansion, "chat", lambda messages: "termo")

        assert "termo" in query_expansion.expand_query("pergunta", "terms")
