"""RED — feature 016: métricas de retrieval com valores trabalhados à mão.

O cálculo é puro de propósito: é a parte que precisa ser confiável, e ela não
deve depender de disco nem de servidor.
"""

import json

import pytest

from kb import bench


class TestEvaluateCase:
    def test_should_report_rank_one_when_expected_is_first(self):
        result = bench.evaluate_case(
            ranked_slugs=["circuit-breaker", "outro"], expected=["circuit-breaker"], k=5
        )

        assert result.rank == 1
        assert result.hit_at_k is True
        assert result.invalid is False

    def test_should_report_rank_at_cutoff_as_hit(self):
        ranked = ["a", "b", "c", "d", "alvo"]

        result = bench.evaluate_case(ranked_slugs=ranked, expected=["alvo"], k=5)

        assert result.rank == 5
        assert result.hit_at_k is True

    def test_should_not_count_hit_beyond_cutoff(self):
        ranked = ["a", "b", "c", "d", "e", "alvo"]

        result = bench.evaluate_case(ranked_slugs=ranked, expected=["alvo"], k=5)

        assert result.rank == 6
        assert result.hit_at_k is False

    def test_should_report_no_rank_when_expected_absent(self):
        result = bench.evaluate_case(ranked_slugs=["a", "b"], expected=["alvo"], k=5)

        assert result.rank is None
        assert result.hit_at_k is False

    def test_should_use_first_matching_expected_when_several(self):
        ranked = ["x", "segundo-esperado", "primeiro-esperado"]

        result = bench.evaluate_case(
            ranked_slugs=ranked,
            expected=["primeiro-esperado", "segundo-esperado"],
            k=5,
        )

        assert result.rank == 2

    def test_should_flag_case_as_invalid_when_expected_not_in_corpus(self):
        result = bench.evaluate_case(
            ranked_slugs=["a"],
            expected=["artigo-que-sumiu"],
            k=5,
            known_slugs={"a", "b"},
        )

        assert result.invalid is True
        assert result.hit_at_k is False


class TestAggregate:
    def test_should_compute_recall_and_mrr_over_valid_cases(self):
        results = [
            bench.evaluate_case(["alvo"], ["alvo"], k=5),
            bench.evaluate_case(["x", "alvo"], ["alvo"], k=5),
            bench.evaluate_case(["x", "y"], ["alvo"], k=5),
        ]

        summary = bench.aggregate(results, k=5)

        assert summary["total"] == 3
        assert summary["hits"] == 2
        assert summary["recall_at_k"] == pytest.approx(2 / 3)
        assert summary["mrr"] == pytest.approx((1.0 + 0.5 + 0.0) / 3)

    def test_should_exclude_invalid_cases_from_denominator(self):
        results = [
            bench.evaluate_case(["alvo"], ["alvo"], k=5, known_slugs={"alvo"}),
            bench.evaluate_case(["a"], ["sumiu"], k=5, known_slugs={"alvo", "a"}),
        ]

        summary = bench.aggregate(results, k=5)

        assert summary["total"] == 1
        assert summary["invalid"] == 1
        assert summary["recall_at_k"] == pytest.approx(1.0)

    def test_should_report_zero_without_dividing_by_zero_when_all_invalid(self):
        results = [bench.evaluate_case(["a"], ["sumiu"], k=5, known_slugs={"a"})]

        summary = bench.aggregate(results, k=5)

        assert summary["total"] == 0
        assert summary["recall_at_k"] == 0.0
        assert summary["mrr"] == 0.0


class TestLoadGolden:
    def test_should_load_cases_from_file(self, tmp_path):
        path = tmp_path / "golden.json"
        path.write_text(
            json.dumps({"cases": [{"question": "q", "expected": ["a"]}]}),
            encoding="utf-8",
        )

        cases = bench.load_golden(path)

        assert cases == [{"question": "q", "expected": ["a"]}]

    def test_should_return_none_when_file_absent(self, tmp_path):
        assert bench.load_golden(tmp_path / "ausente.json") is None

    def test_should_raise_with_path_when_json_invalid(self, tmp_path):
        path = tmp_path / "golden.json"
        path.write_text("{ nao é json", encoding="utf-8")

        with pytest.raises(ValueError) as exc:
            bench.load_golden(path)

        assert "golden.json" in str(exc.value)
