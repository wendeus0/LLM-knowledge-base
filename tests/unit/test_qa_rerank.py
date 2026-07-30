"""RED — o rerank tem de alcançar o `kb qa`, não só o bench.

O bench media +42% de MRR (0,242 -> 0,343) chamando `search(rerank_depth=20)`
direto. O caminho de produção — `qa -> build_context -> find_relevant -> search`
— nunca passou o parâmetro, então nenhuma pergunta se beneficiou do ganho.

O rerank vale justamente onde o `top_k` é pequeno: o perfil `fast` monta o
contexto com 3 artigos, e ordenar 20 candidatos para escolher esses 3 é o que
decide se a resposta cita o artigo certo.
"""

import pytest

from kb.config import RETRIEVAL_PROFILES, get_retrieval_profile


@pytest.fixture
def sem_override(monkeypatch):
    """O conftest desliga o rerank na suíte inteira; aqui o alvo é o default real."""
    monkeypatch.delenv("KB_RERANK_DEPTH", raising=False)


class TestRetrievalProfiles:
    @pytest.mark.parametrize("nome", sorted(RETRIEVAL_PROFILES))
    def test_should_declare_rerank_depth_in_every_profile(self, nome, sem_override):
        assert get_retrieval_profile(nome)["rerank_depth"] == 20

    def test_should_honor_env_override(self, monkeypatch):
        monkeypatch.setenv("KB_RERANK_DEPTH", "8")

        assert get_retrieval_profile("fast")["rerank_depth"] == 8

    def test_should_allow_disabling_via_env(self, monkeypatch):
        monkeypatch.setenv("KB_RERANK_DEPTH", "0")

        assert get_retrieval_profile("deep")["rerank_depth"] == 0


class TestFindRelevantForwarding:
    def test_should_forward_rerank_depth_to_search(self, monkeypatch):
        recebido = {}

        def fake_search(query, **kwargs):
            recebido.update(kwargs)
            return []

        monkeypatch.setattr("kb.search.search", fake_search)
        from kb.search import find_relevant

        find_relevant("grafos", top_k=3, rerank_depth=20)

        assert recebido["rerank_depth"] == 20
        assert recebido["top_k"] == 3

    def test_should_default_to_no_rerank(self, monkeypatch):
        recebido = {}
        monkeypatch.setattr("kb.search.search", lambda q, **kw: recebido.update(kw) or [])
        from kb.search import find_relevant

        find_relevant("grafos", top_k=3)

        assert not recebido.get("rerank_depth")


class TestBuildContextForwarding:
    def test_should_forward_rerank_depth_to_find_relevant(self, monkeypatch):
        recebido = {}
        monkeypatch.setattr(
            "kb.router.find_relevant", lambda q, **kw: recebido.update(kw) or []
        )
        from kb.router import build_context

        build_context("o que e circuit breaker", top_k=3, rerank_depth=20)

        assert recebido["rerank_depth"] == 20


class TestAnswerUsesProfile:
    def test_should_pass_profile_rerank_depth_to_build_context(self, monkeypatch):
        recebido = {}

        def fake_build_context(question, **kwargs):
            recebido.update(kwargs)
            return (None, [])

        monkeypatch.setattr("kb.qa.build_context", fake_build_context)
        monkeypatch.delenv("KB_RERANK_DEPTH", raising=False)
        from kb.qa import answer

        answer("pergunta", profile="fast")

        assert recebido["rerank_depth"] == 20

    def test_should_respect_explicit_override(self, monkeypatch):
        recebido = {}
        monkeypatch.setattr(
            "kb.qa.build_context",
            lambda q, **kw: recebido.update(kw) or (None, []),
        )
        from kb.qa import answer

        answer("pergunta", profile="deep", rerank_depth=0)

        assert recebido["rerank_depth"] == 0
