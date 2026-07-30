"""RED — preflight do rerank no bench.

Uma queda de energia derrubou o túnel para a VM no meio de uma medição: as 152
chamadas falharam, o rerank degradou para a ordem original (correto) e o bench
reportou 0,414 — idêntico à baseline. Dezoito minutos para produzir um número
que parecia válido e não media nada.

Provider morto tem de abortar antes do lote, não depois.
"""

import pytest

from kb import bench


def _seed(tmp_path, monkeypatch):
    wiki = tmp_path / "wiki"
    state = tmp_path / "kb_state"
    wiki.mkdir()
    (state / "bench").mkdir(parents=True)
    (wiki / "artigo.md").write_text("---\ntitle: Artigo\n---\n\ncorpo\n", encoding="utf-8")
    (state / "bench" / "golden.json").write_text(
        '{"cases": [{"question": "q", "expected": ["artigo"]}]}', encoding="utf-8"
    )
    monkeypatch.setattr("kb.config.WIKI_DIR", wiki)
    monkeypatch.setattr("kb.config.STATE_DIR", state)
    monkeypatch.setattr("kb.search.WIKI_DIR", wiki)
    return wiki, state


class TestRerankPreflight:
    def test_should_abort_when_rerank_provider_is_dead(self, tmp_path, monkeypatch):
        _seed(tmp_path, monkeypatch)

        def _dead(messages):
            raise RuntimeError("connection refused")

        monkeypatch.setattr("kb.rerank._call_llm", _dead)

        with pytest.raises(RuntimeError) as exc:
            bench.run_bench(mode="lexical", k=5, rerank_depth=20)

        assert "rerank" in str(exc.value).lower()

    def test_should_proceed_when_provider_answers(self, tmp_path, monkeypatch):
        _seed(tmp_path, monkeypatch)
        monkeypatch.setattr("kb.rerank._call_llm", lambda messages: "1, 2")

        report = bench.run_bench(mode="lexical", k=5, rerank_depth=20)

        assert report is not None

    def test_should_not_preflight_when_rerank_disabled(self, tmp_path, monkeypatch):
        _seed(tmp_path, monkeypatch)

        def _dead(messages):
            raise AssertionError("não deveria consultar o provider sem --rerank")

        monkeypatch.setattr("kb.rerank._call_llm", _dead)

        assert bench.run_bench(mode="lexical", k=5) is not None
