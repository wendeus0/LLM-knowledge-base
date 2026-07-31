"""RED — colisão de `stem` não pode fazer artigo sumir do rerank nem da medição.

O vault real tem 4 stems duplicados em topics diferentes (`algebra-linear`,
`honeycomb`, `fundamentos-de-engenharia-de-dados`, `decomposicoes-de-matrizes`).
`_apply_rerank` chaveava por `path.stem`: dois candidatos no mesmo head → um
sobrescreve o outro no `by_slug` e desaparece do resultado. `run_bench`
comparava por stem, então um caso podia "acertar" o arquivo errado.
"""

from pathlib import Path

from kb.bench import (
    evaluate_case,
    generate_cases,
    sample_articles,
    seed_golden,
    slug_matches,
)
from kb.search import _apply_rerank


def _result(path, snippet="trecho"):
    return {"path": path, "score": 1.0, "snippet": snippet}


class TestApplyRerankStemCollision:
    def test_should_keep_both_articles_when_stems_collide(self, tmp_wiki, monkeypatch):
        """
        Dado dois candidatos com o mesmo stem em topics diferentes,
        Quando _apply_rerank reordena o head,
        Então nenhum dos dois pode desaparecer do resultado
        """
        wiki = tmp_wiki
        a = wiki / "ai" / "algebra-linear.md"
        b = wiki / "python" / "algebra-linear.md"
        a.write_text("# A\n")
        b.write_text("# B\n")

        monkeypatch.setattr("kb.rerank.rerank", lambda q, cands, want=None: list(reversed(cands)))

        results = _apply_rerank("algebra", [_result(a), _result(b)], depth=2)

        paths = [item["path"] for item in results]
        assert len(paths) == 2
        assert a in paths
        assert b in paths

    def test_should_send_unique_slugs_to_reranker(self, tmp_wiki, monkeypatch):
        """
        Dado candidatos com stems duplicados,
        Quando _apply_rerank monta a lista para o LLM,
        Então cada candidato tem slug único (o LLM distingue os dois)
        """
        wiki = tmp_wiki
        a = wiki / "ai" / "honeycomb.md"
        b = wiki / "cybersecurity" / "honeycomb.md"
        a.write_text("# A\n")
        b.write_text("# B\n")

        captured = {}

        def fake_rerank(question, candidates, want=None):
            captured["slugs"] = [c["slug"] for c in candidates]
            return candidates

        monkeypatch.setattr("kb.rerank.rerank", fake_rerank)

        _apply_rerank("honeycomb", [_result(a), _result(b)], depth=2)

        assert len(captured["slugs"]) == 2
        assert len(set(captured["slugs"])) == 2

    def test_should_keep_homonyms_even_for_paths_outside_wiki(self, tmp_wiki, monkeypatch):
        """
        Dado dois paths distintos fora de WIKI_DIR com o mesmo stem (defensivo),
        Quando _apply_rerank reordena,
        Então nenhum desaparece — a identidade de fallback também é única
        """
        a = Path("/tmp/topico-a/fora-da-wiki.md")
        b = Path("/tmp/topico-b/fora-da-wiki.md")

        monkeypatch.setattr("kb.rerank.rerank", lambda q, cands, want=None: list(reversed(cands)))

        results = _apply_rerank("x", [_result(a), _result(b)], depth=2)

        paths = [item["path"] for item in results]
        assert len(paths) == 2
        assert a in paths
        assert b in paths


class TestBenchSlugMatching:
    def test_should_match_expected_stem_against_relative_slug(self):
        """
        Dado golden com expected por stem (formato atual dos 152 casos),
        Quando o ranking vem como path relativo sem extensão,
        Então o stem continua casando (compatibilidade retroativa)
        """
        assert slug_matches("ai/algebra-linear", "algebra-linear")

    def test_should_match_exact_relative_path(self):
        """
        Dado expected com path relativo completo,
        Quando o ranking traz o mesmo path,
        Então casa por igualdade exata
        """
        assert slug_matches("ai/algebra-linear", "ai/algebra-linear")

    def test_should_not_match_same_stem_in_wrong_topic_when_expected_is_precise(self):
        """
        Dado expected com path relativo (caso futuro, desambiguado),
        Quando o ranking traz o homônimo do topic errado,
        Então NÃO casa — o bug era exatamente "acertar" o arquivo errado
        """
        assert not slug_matches("python/algebra-linear", "ai/algebra-linear")

    def test_evaluate_case_should_rank_by_relative_slug_with_stem_expected(self):
        ranked = ["python/decorators", "ai/algebra-linear", "cybersecurity/xss"]
        result = evaluate_case(
            ranked,
            expected=["algebra-linear"],
            k=5,
            known_slugs=set(ranked),
        )
        assert not result.invalid
        assert result.rank == 2
        assert result.hit_at_k

    def test_seed_golden_should_emit_distinct_expected_for_homonyms(self, tmp_wiki):
        """
        Dado dois artigos com o mesmo stem em topics diferentes,
        Quando seed_golden gera os casos,
        Então cada um recebe expected único (path relativo, não stem)
        """
        wiki = tmp_wiki
        (wiki / "ai" / "honeycomb.md").write_text("---\ntitle: A\n---\n# A\n")
        (wiki / "python" / "honeycomb.md").write_text("---\ntitle: B\n---\n# B\n")

        cases = seed_golden(wiki)

        expected = [slug for case in cases for slug in case["expected"]]
        assert sorted(expected) == ["ai/honeycomb", "python/honeycomb"]

    def test_evaluate_case_should_distinguish_homonyms_with_precise_expected(self):
        ranked = ["python/algebra-linear", "ai/algebra-linear"]
        result = evaluate_case(
            ranked,
            expected=["ai/algebra-linear"],
            k=1,
            known_slugs=set(ranked),
        )
        assert result.rank == 2
        assert not result.hit_at_k


class TestGoldenGenerationHomonyms:
    def test_generate_cases_should_sample_both_homonyms(self, tmp_wiki, monkeypatch):
        """
        Dado dois artigos com o mesmo stem em topics diferentes,
        Quando generate_cases amostra o corpus inteiro,
        Então os dois entram no pool com expected distinto
        (antes o dict chaveado por stem colapsava um no outro)
        """
        wiki = tmp_wiki
        (wiki / "ai" / "honeycomb.md").write_text("---\ntitle: Grades\n---\ncorpo A\n")
        (wiki / "python" / "honeycomb.md").write_text("---\ntitle: Colmeias\n---\ncorpo B\n")

        monkeypatch.setattr("kb.client.chat", lambda **kwargs: "para que serve isso na prática?")

        cases = generate_cases(wiki, n=2, seed=42)

        expected = sorted(slug for case in cases for slug in case["expected"])
        assert expected == ["ai/honeycomb", "python/honeycomb"]

    def test_sample_articles_should_exclude_all_homonyms_for_legacy_stem(self):
        """
        Dado golden legado cobrindo o stem `honeycomb`,
        Quando sample_articles monta o pool,
        Então ambos os homônimos saem — over-exclusion deliberada,
        melhor que gerar caso ambíguo
        """
        pool = ["ai/honeycomb", "python/honeycomb", "ai/outro"]
        chosen = sample_articles(pool, n=3, seed=42, exclude={"honeycomb"})
        assert chosen == ["ai/outro"]
