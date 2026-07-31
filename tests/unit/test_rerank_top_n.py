"""RED — pedir os N melhores é tarefa menor que ordenar 20.

A 022 provou que sampling determinístico corrige omissão mas não alucinação de
índice: o modelo ainda emite números fora da faixa quando precisa ordenar 20
candidatos. Selecionar os N mais relevantes é uma pergunta menor, e o que
sobra preserva a ordem original — que já vem do RRF, não é aleatória.
"""

from unittest.mock import patch

import pytest

from kb.rerank import _cache_key, rerank


@pytest.fixture(autouse=True)
def _sem_cache(monkeypatch):
    monkeypatch.setattr("kb.rerank._read_cache", lambda: {})
    monkeypatch.setattr("kb.rerank._write_cache", lambda cache: None)
    monkeypatch.setattr("kb.rerank.reset_stats", lambda: None)


def _candidatos(n):
    return [{"slug": f"ai/a{i}", "title": f"a{i}", "snippet": f"trecho {i}"} for i in range(n)]


class TestTopNPrompt:
    def test_should_ask_for_n_best_when_want_is_set(self):
        """
        Dado want=5 sobre 20 candidatos,
        Quando o prompt é montado,
        Então pede os 5 mais relevantes, não a ordenação dos 20
        """
        capturado = {}

        def fake_llm(messages):
            capturado["system"] = messages[0]["content"]
            return "1, 2, 3, 4, 5"

        with patch("kb.rerank._call_llm", side_effect=fake_llm):
            rerank("pergunta", _candidatos(20), want=5)

        assert "5" in capturado["system"]
        assert "mais relevantes" in capturado["system"].lower()

    def test_should_keep_ordering_prompt_without_want(self):
        """Sem `want`, o contrato antigo (ordenar tudo) é preservado."""
        capturado = {}

        def fake_llm(messages):
            capturado["system"] = messages[0]["content"]
            return "2, 1"

        with patch("kb.rerank._call_llm", side_effect=fake_llm):
            rerank("pergunta", _candidatos(2))

        assert "ordene" in capturado["system"].lower()


class TestTopNResult:
    def test_should_promote_selected_and_preserve_rest_in_original_order(self):
        """
        Dado que o modelo devolve 3 de 10,
        Quando o resultado é montado,
        Então os 3 vêm primeiro e os 7 restantes mantêm a ordem do RRF
        """
        with patch("kb.rerank._call_llm", return_value="7, 3, 9"):
            resultado = rerank("pergunta", _candidatos(10), want=3)

        slugs = [c["slug"] for c in resultado]
        assert slugs[:3] == ["ai/a6", "ai/a2", "ai/a8"]
        assert slugs[3:] == [
            "ai/a0", "ai/a1", "ai/a3", "ai/a4", "ai/a5", "ai/a7", "ai/a9",
        ]

    def test_should_ignore_indices_beyond_want(self):
        """
        Dado que o modelo devolve mais números do que foi pedido,
        Quando o resultado é montado,
        Então só os `want` primeiros são promovidos — pedir 3 e aceitar 10 de
        volta é a ordenação de 20 pela porta dos fundos
        """
        with patch("kb.rerank._call_llm", return_value="5, 4, 3, 2, 1"):
            resultado = rerank("pergunta", _candidatos(10), want=2)

        slugs = [c["slug"] for c in resultado]
        assert slugs[:2] == ["ai/a4", "ai/a3"]
        assert slugs[2] == "ai/a0"

    def test_should_never_lose_candidate(self):
        with patch("kb.rerank._call_llm", return_value="3"):
            resultado = rerank("pergunta", _candidatos(10), want=5)

        assert len(resultado) == 10
        assert {c["slug"] for c in resultado} == {f"ai/a{i}" for i in range(10)}

    def test_should_keep_original_order_when_answer_is_unparseable(self):
        with patch("kb.rerank._call_llm", return_value="não sei responder"):
            resultado = rerank("pergunta", _candidatos(5), want=3)

        assert [c["slug"] for c in resultado] == [f"ai/a{i}" for i in range(5)]


class TestTopNCache:
    def test_should_invalidate_cache_when_want_changes(self):
        """
        Dado o mesmo conjunto de candidatos com `want` diferente,
        Quando a chave de cache é calculada,
        Então difere — `want` muda a pergunta feita ao modelo
        """
        cands = _candidatos(5)

        assert _cache_key("q", cands, want=3) != _cache_key("q", cands, want=5)

    def test_should_keep_key_stable_for_same_want(self):
        cands = _candidatos(5)

        assert _cache_key("q", cands, want=3) == _cache_key("q", cands, want=3)
