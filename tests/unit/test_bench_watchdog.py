"""RED — provider que morre no meio do lote não pode produzir número que parece válido.

`preflight()` cobre só o início. Em 2026-07-29 uma queda de energia derrubou o
túnel no meio de uma medição: 152 chamadas falharam, cada uma degradou
corretamente para a ordem original, e o resultado saiu idêntico à baseline —
18 minutos para medir nada. Em 2026-07-30 o mesmo padrão custou 65 de 152.
"""

import pytest

from kb.bench import BenchAbortedError, run_bench


@pytest.fixture
def golden_com_casos(tmp_wiki, monkeypatch):
    """Wiki mínima + golden de 10 casos, sem tocar o vault real."""
    from kb.bench import golden_path, write_golden
    from kb.config import STATE_DIR

    wiki = tmp_wiki
    for i in range(3):
        (wiki / "ai" / f"artigo-{i}.md").write_text(f"# Artigo {i}\n\nconteudo resiliencia {i}\n")

    cases = [{"question": f"pergunta {i} sobre resiliencia", "expected": [f"ai/artigo-{i % 3}"]} for i in range(10)]
    write_golden(golden_path(STATE_DIR), cases)
    return wiki


class TestProviderWatchdog:
    def test_should_abort_when_provider_fails_consecutively(
        self, golden_com_casos, monkeypatch
    ):
        """
        Dado um provider que passa a falhar a partir do 3º caso,
        Quando run_bench roda com rerank,
        Então aborta em vez de devolver número degradado silenciosamente
        """
        import kb.rerank as rerank_module

        monkeypatch.setattr(rerank_module, "preflight", lambda: None)

        chamadas = {"n": 0}

        def provider_que_morre(messages):
            chamadas["n"] += 1
            if chamadas["n"] > 2:
                raise RuntimeError("connection reset")
            return "1, 2"

        monkeypatch.setattr(rerank_module, "_call_llm", provider_que_morre)
        monkeypatch.setattr(rerank_module, "_read_cache", lambda: {})
        monkeypatch.setattr(rerank_module, "_write_cache", lambda cache: None)

        with pytest.raises(BenchAbortedError, match="provider"):
            run_bench(mode="lexical", k=5, rerank_depth=2)

    def test_should_name_how_many_cases_completed_on_abort(
        self, golden_com_casos, monkeypatch
    ):
        """
        Dado o abort do watchdog,
        Quando a exceção é lida,
        Então diz quantos casos rodaram — retomar exige saber onde parou
        """
        import kb.rerank as rerank_module

        monkeypatch.setattr(rerank_module, "preflight", lambda: None)
        monkeypatch.setattr(
            rerank_module,
            "_call_llm",
            lambda messages: (_ for _ in ()).throw(RuntimeError("morreu")),
        )
        monkeypatch.setattr(rerank_module, "_read_cache", lambda: {})
        monkeypatch.setattr(rerank_module, "_write_cache", lambda cache: None)

        with pytest.raises(BenchAbortedError) as exc:
            run_bench(mode="lexical", k=5, rerank_depth=2)

        assert "caso" in str(exc.value).lower()

    def test_should_not_abort_when_failures_are_isolated(
        self, golden_com_casos, monkeypatch
    ):
        """
        Dada uma falha isolada (blip de rede), não uma queda,
        Quando o provider volta a responder,
        Então o bench completa — watchdog não pode ser gatilho nervoso
        """
        import kb.rerank as rerank_module

        monkeypatch.setattr(rerank_module, "preflight", lambda: None)

        chamadas = {"n": 0}

        def provider_com_blip(messages):
            chamadas["n"] += 1
            if chamadas["n"] == 3:
                raise RuntimeError("blip")
            return "1, 2"

        monkeypatch.setattr(rerank_module, "_call_llm", provider_com_blip)
        monkeypatch.setattr(rerank_module, "_read_cache", lambda: {})
        monkeypatch.setattr(rerank_module, "_write_cache", lambda cache: None)

        report = run_bench(mode="lexical", k=5, rerank_depth=2)

        assert report is not None
        assert report["summary"]["total"] == 10

    def test_should_flag_report_when_any_call_failed(self, golden_com_casos, monkeypatch):
        """
        Dado que houve falha isolada durante o lote,
        Quando o relatório é lido,
        Então carrega marca de integridade — número com degradação parcial não
        pode ser lido como medição limpa
        """
        import kb.rerank as rerank_module

        monkeypatch.setattr(rerank_module, "preflight", lambda: None)

        chamadas = {"n": 0}

        def provider_com_blip(messages):
            chamadas["n"] += 1
            if chamadas["n"] == 3:
                raise RuntimeError("blip")
            return "1, 2"

        monkeypatch.setattr(rerank_module, "_call_llm", provider_com_blip)
        monkeypatch.setattr(rerank_module, "_read_cache", lambda: {})
        monkeypatch.setattr(rerank_module, "_write_cache", lambda cache: None)

        report = run_bench(mode="lexical", k=5, rerank_depth=2)

        assert report["degraded"] is True

    def test_should_mark_clean_run_as_not_degraded(self, golden_com_casos, monkeypatch):
        import kb.rerank as rerank_module

        monkeypatch.setattr(rerank_module, "preflight", lambda: None)
        monkeypatch.setattr(rerank_module, "_call_llm", lambda messages: "1, 2")
        monkeypatch.setattr(rerank_module, "_read_cache", lambda: {})
        monkeypatch.setattr(rerank_module, "_write_cache", lambda cache: None)

        report = run_bench(mode="lexical", k=5, rerank_depth=2)

        assert report["degraded"] is False

    def test_should_not_flag_degraded_without_rerank(self, golden_com_casos):
        """Sem rerank não há provider no caminho — a marca não se aplica."""
        report = run_bench(mode="lexical", k=5)

        assert report["degraded"] is False
