"""RED — feature 019: gerar casos de avaliação em escala.

O que precisa ser confiável é o descarte de caso trivial e a incrementalidade —
um golden que duplica artigos ou aceita pergunta igual ao título mede a coisa
errada, que foi o defeito do seed original.
"""

from kb import bench


class TestQuestionQuality:
    def test_should_reject_question_that_repeats_the_title(self):
        assert bench.is_trivial_question("Circuit Breaker", "circuit breaker") is True

    def test_should_reject_question_containing_full_title(self):
        assert (
            bench.is_trivial_question(
                "Falhas em Cascata", "o que são falhas em cascata em sistemas"
            )
            is True
        )

    def test_should_accept_conceptual_paraphrase(self):
        assert (
            bench.is_trivial_question(
                "Falhas em Cascata", "por que um problema pequeno derruba tudo"
            )
            is False
        )


class TestSampling:
    def test_should_be_deterministic_for_same_seed(self):
        pool = [f"artigo-{i}" for i in range(50)]

        first = bench.sample_articles(pool, 10, seed=7)
        second = bench.sample_articles(pool, 10, seed=7)

        assert first == second

    def test_should_differ_for_different_seed(self):
        pool = [f"artigo-{i}" for i in range(50)]

        assert bench.sample_articles(pool, 10, seed=1) != bench.sample_articles(pool, 10, seed=2)

    def test_should_exclude_already_covered_articles(self):
        pool = [f"artigo-{i}" for i in range(10)]
        covered = {f"artigo-{i}" for i in range(8)}

        sampled = bench.sample_articles(pool, 5, seed=1, exclude=covered)

        assert set(sampled).isdisjoint(covered)
        assert len(sampled) == 2


class TestPopulationMetrics:
    def test_should_split_summary_by_source(self):
        results = [
            bench.CaseResult(question="a", expected=["x"], rank=1, hit_at_k=True, source="curated"),
            bench.CaseResult(question="b", expected=["y"], rank=None, source="curated"),
            bench.CaseResult(question="c", expected=["z"], rank=1, hit_at_k=True, source="generated"),
        ]

        by_source = bench.aggregate_by_source(results, k=5)

        assert by_source["curated"]["total"] == 2
        assert by_source["curated"]["hits"] == 1
        assert by_source["generated"]["total"] == 1
        assert by_source["generated"]["recall_at_k"] == 1.0
