"""RED — feature 021: provider dedicado para o rerank.

O rerank é a única etapa que precisa de saída estruturada longa, e é onde a
quantização do modelo pesa. Separar o provider permite trocar só ele — sem
tocar em compile, qa ou heal, que funcionam bem com o modelo atual.
"""

import pytest

from kb import rerank as rerank_module


@pytest.fixture
def _state(tmp_path, monkeypatch):
    state = tmp_path / "kb_state"
    state.mkdir()
    monkeypatch.setattr("kb.config.STATE_DIR", state)
    monkeypatch.setenv("KB_MODEL", "modelo-padrao")
    monkeypatch.delenv("KB_RERANK_MODEL", raising=False)
    monkeypatch.delenv("KB_RERANK_BASE_URL", raising=False)
    rerank_module.reset_stats()
    return state


class TestProviderResolution:
    def test_should_fall_back_to_default_model_when_unset(self, _state):
        assert rerank_module.rerank_model() == "modelo-padrao"

    def test_should_use_dedicated_model_when_set(self, _state, monkeypatch):
        monkeypatch.setenv("KB_RERANK_MODEL", "granite4:tiny-h")

        assert rerank_module.rerank_model() == "granite4:tiny-h"

    def test_should_use_dedicated_base_url_when_set(self, _state, monkeypatch):
        monkeypatch.setenv("KB_RERANK_BASE_URL", "http://localhost:11435/v1")

        assert rerank_module.rerank_base_url() == "http://localhost:11435/v1"


class TestCacheKeyIsolation:
    def test_should_miss_cache_when_sampling_changes(self, _state, monkeypatch):
        """Resposta depende da temperatura: mudá-la tem de invalidar o cache.

        Sem isso, medir o efeito de temperatura 0 reusaria respostas geradas a
        0,8 e a conclusão seria sobre o cache, não sobre o sampling.
        """
        calls = []
        monkeypatch.setattr(
            rerank_module, "_call_llm", lambda messages: calls.append(1) or "1, 2, 3"
        )
        candidates = [{"slug": f"a{i}", "title": f"A{i}", "snippet": "x"} for i in range(5)]

        rerank_module.rerank("q", candidates)
        monkeypatch.setenv("KB_SAMPLING_DETERMINISTIC_TEMP", "0.7")
        rerank_module.rerank("q", candidates)

        assert len(calls) == 2

    def test_should_miss_cache_when_rerank_model_changes(self, _state, monkeypatch):
        calls = []
        monkeypatch.setattr(
            rerank_module, "_call_llm", lambda messages: calls.append(1) or "1, 2, 3"
        )
        candidates = [{"slug": f"a{i}", "title": f"A{i}", "snippet": "x"} for i in range(5)]

        rerank_module.rerank("q", candidates)
        monkeypatch.setenv("KB_RERANK_MODEL", "outro-modelo")
        rerank_module.rerank("q", candidates)

        assert len(calls) == 2, "trocar o modelo de rerank precisa invalidar o cache"
