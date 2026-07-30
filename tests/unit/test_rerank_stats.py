"""RED — instrumentação da omissão do rerank.

O parsing descarta índice fora de faixa, duplicado e omitido — tudo em silêncio.
Medido no vault real: só 18% das chamadas devolveram os 20 índices pedidos e 20%
devolveram 5 ou menos. Sem contador, essa degradação fica invisível e vira
"o rerank não funcionou".
"""

import pytest

from kb import rerank as rerank_module


@pytest.fixture
def _state(tmp_path, monkeypatch):
    state = tmp_path / "kb_state"
    state.mkdir()
    monkeypatch.setattr("kb.config.STATE_DIR", state)
    monkeypatch.setenv("KB_MODEL", "modelo-teste")
    rerank_module.reset_stats()
    return state


def _candidates(n):
    return [{"slug": f"a{i}", "title": f"A{i}", "snippet": "x"} for i in range(n)]


class TestParseOrderStats:
    def test_should_count_out_of_range_indexes(self):
        _, stats = rerank_module.parse_order_with_stats("1, 99, 2, 100", 3)

        assert stats["out_of_range"] == 2

    def test_should_count_duplicates(self):
        _, stats = rerank_module.parse_order_with_stats("1, 1, 2, 2", 3)

        assert stats["duplicates"] == 2

    def test_should_report_coverage_of_requested_candidates(self):
        _, stats = rerank_module.parse_order_with_stats("1, 2", 10)

        assert stats["requested"] == 10
        assert stats["returned"] == 2
        assert stats["coverage"] == pytest.approx(0.2)


class TestAccumulatedStats:
    def test_should_accumulate_across_calls(self, _state, monkeypatch):
        monkeypatch.setattr(rerank_module, "_call_llm", lambda messages: "1, 2, 3")

        rerank_module.rerank("q1", _candidates(20))
        rerank_module.rerank("q2", _candidates(20))

        stats = rerank_module.stats()
        assert stats["calls"] == 2
        assert stats["returned_total"] == 6
        assert stats["requested_total"] == 40

    def test_should_flag_severe_omission(self, _state, monkeypatch):
        monkeypatch.setattr(rerank_module, "_call_llm", lambda messages: "1, 2")

        rerank_module.rerank("q", _candidates(20))

        assert rerank_module.stats()["severe_omission"] == 1

    def test_should_not_flag_severe_omission_when_mostly_complete(self, _state, monkeypatch):
        monkeypatch.setattr(
            rerank_module, "_call_llm", lambda messages: ", ".join(str(i) for i in range(1, 20))
        )

        rerank_module.rerank("q", _candidates(20))

        assert rerank_module.stats()["severe_omission"] == 0

    def test_should_count_llm_failure(self, _state, monkeypatch):
        def _boom(messages):
            raise RuntimeError("fora")

        monkeypatch.setattr(rerank_module, "_call_llm", _boom)

        rerank_module.rerank("q", _candidates(20))

        assert rerank_module.stats()["failed"] == 1

    def test_should_count_unparseable_answer(self, _state, monkeypatch):
        monkeypatch.setattr(rerank_module, "_call_llm", lambda messages: "sei lá")

        rerank_module.rerank("q", _candidates(20))

        assert rerank_module.stats()["unparseable"] == 1

    def test_should_count_cache_hit_separately_from_call(self, _state, monkeypatch):
        monkeypatch.setattr(rerank_module, "_call_llm", lambda messages: "1, 2, 3")

        rerank_module.rerank("q", _candidates(20))
        rerank_module.rerank("q", _candidates(20))

        stats = rerank_module.stats()
        assert stats["calls"] == 1
        assert stats["cache_hits"] == 1

    def test_should_reset(self, _state, monkeypatch):
        monkeypatch.setattr(rerank_module, "_call_llm", lambda messages: "1")
        rerank_module.rerank("q", _candidates(20))

        rerank_module.reset_stats()

        assert rerank_module.stats()["calls"] == 0
