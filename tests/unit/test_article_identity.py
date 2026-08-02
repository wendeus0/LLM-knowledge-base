"""Identidade de artigo — `rel_slug`, não `stem` (F0 da plataforma de estudos).

O vault tem 4 stems duplicados em topics diferentes. Resolver por `stem` faz
três coisas erradas: a resolução depende da ordem do `rglob` (que o sistema de
arquivos não garante), o lint não consegue reportar a ambiguidade, e o archive
trata dois artigos distintos como o mesmo — linkar um faz o outro parecer
linkado.
"""

from kb import archive, graph, lint
from kb.search import rel_slug


def _vault(tmp_path):
    wiki = tmp_path / "wiki"
    (wiki / "cybersecurity").mkdir(parents=True)
    (wiki / "ai").mkdir(parents=True)
    (wiki / "honeycomb.md").write_text("---\ntitle: Honeycomb\n---\n# Honeycomb raiz\n")
    (wiki / "cybersecurity" / "honeycomb.md").write_text(
        "---\ntitle: Honeycomb\n---\n# Honeycomb de segurança\n"
    )
    (wiki / "ai" / "transformers.md").write_text("---\ntitle: Transformers\n---\n# Transformers\n")
    return wiki


class TestResolucaoDeterministica:
    def test_should_resolve_the_same_article_on_every_call(self, tmp_path):
        wiki = _vault(tmp_path)

        resolvidos = {graph.resolve_wikilink("honeycomb", wiki) for _ in range(8)}

        assert len(resolvidos) == 1

    def test_should_resolve_an_explicit_topic_qualified_link(self, tmp_path):
        wiki = _vault(tmp_path)

        alvo = graph.resolve_wikilink("cybersecurity/honeycomb", wiki)

        assert alvo is not None
        assert rel_slug(alvo, wiki) == "cybersecurity/honeycomb"

    def test_should_still_resolve_an_unambiguous_bare_link(self, tmp_path):
        wiki = _vault(tmp_path)

        alvo = graph.resolve_wikilink("transformers", wiki)

        assert alvo is not None
        assert rel_slug(alvo, wiki) == "ai/transformers"

    def test_should_return_none_for_a_link_without_article(self, tmp_path):
        wiki = _vault(tmp_path)

        assert graph.resolve_wikilink("nao-existe", wiki) is None


class TestAmbiguidadeReportavel:
    def test_should_expose_every_candidate_of_an_ambiguous_link(self, tmp_path):
        wiki = _vault(tmp_path)

        candidatos = graph.resolve_wikilink_all("honeycomb", wiki)

        assert {rel_slug(p, wiki) for p in candidatos} == {"honeycomb", "cybersecurity/honeycomb"}

    def test_should_return_a_single_candidate_when_unambiguous(self, tmp_path):
        wiki = _vault(tmp_path)

        assert len(graph.resolve_wikilink_all("transformers", wiki)) == 1

    def test_should_order_candidates_deterministically(self, tmp_path):
        wiki = _vault(tmp_path)

        ordens = {
            tuple(rel_slug(p, wiki) for p in graph.resolve_wikilink_all("honeycomb", wiki))
            for _ in range(5)
        }

        assert len(ordens) == 1


class TestArchiveNaoColapsaHomonimos:
    def test_should_not_treat_a_namesake_as_linked(self, tmp_path):
        wiki = _vault(tmp_path)
        (wiki / "ai" / "transformers.md").write_text(
            "---\ntitle: Transformers\n---\nVeja [[cybersecurity/honeycomb]].\n"
        )

        orfaos = {rel_slug(p, wiki) for p in archive.find_orphans(wiki)}

        assert "cybersecurity/honeycomb" not in orfaos
        assert "honeycomb" in orfaos


class TestLintReportaAmbiguidade:
    def test_should_report_a_link_that_designates_more_than_one_article(
        self, tmp_path, monkeypatch
    ):
        wiki = _vault(tmp_path)
        (wiki / "ai" / "transformers.md").write_text(
            "---\ntitle: Transformers\n---\nVeja [[honeycomb]].\n"
        )
        monkeypatch.setattr("kb.lint.WIKI_DIR", wiki)

        ambiguos = lint.find_ambiguous_wikilinks(wiki)

        assert any("honeycomb" in item for item in ambiguos)

    def test_should_not_report_an_unambiguous_link(self, tmp_path):
        wiki = _vault(tmp_path)
        (wiki / "cybersecurity" / "honeycomb.md").write_text(
            "---\ntitle: Honeycomb\n---\nVeja [[transformers]].\n"
        )

        assert not any("transformers" in item for item in lint.find_ambiguous_wikilinks(wiki))

    def test_should_not_report_a_link_qualified_by_topic(self, tmp_path):
        wiki = _vault(tmp_path)
        (wiki / "ai" / "transformers.md").write_text(
            "---\ntitle: Transformers\n---\nVeja [[cybersecurity/honeycomb]].\n"
        )

        assert lint.find_ambiguous_wikilinks(wiki) == []


class TestDerivadosForaDoIndice:
    """`_summaries/`, `_sources/` e `_index.md` são derivados, não artigos.

    A convenção `_*` já os exclui do índice e da busca; incluí-los na
    resolução de wikilink fabricava ambiguidade — o vault real reportou 1.364
    falsos positivos, todos artigo contra o próprio resumo.
    """

    def test_should_not_offer_a_summary_as_a_wikilink_candidate(self, tmp_path):
        wiki = _vault(tmp_path)
        (wiki / "_summaries" / "ai").mkdir(parents=True)
        (wiki / "_summaries" / "ai" / "transformers.md").write_text("resumo\n")

        candidatos = graph.resolve_wikilink_all("transformers", wiki)

        assert [rel_slug(p, wiki) for p in candidatos] == ["ai/transformers"]

    def test_should_not_report_ambiguity_between_article_and_its_summary(self, tmp_path):
        wiki = _vault(tmp_path)
        (wiki / "_summaries" / "ai").mkdir(parents=True)
        (wiki / "_summaries" / "ai" / "transformers.md").write_text("resumo\n")
        (wiki / "cybersecurity" / "honeycomb.md").write_text(
            "---\ntitle: H\n---\nVeja [[transformers]].\n"
        )

        assert not any("transformers" in i for i in lint.find_ambiguous_wikilinks(wiki))

    def test_should_report_each_ambiguous_link_once_per_article(self, tmp_path):
        wiki = _vault(tmp_path)
        (wiki / "ai" / "transformers.md").write_text(
            "---\ntitle: T\n---\n[[honeycomb]] e [[honeycomb]] e [[Honeycomb]].\n"
        )

        achados = [i for i in lint.find_ambiguous_wikilinks(wiki) if "transformers.md" in i]

        assert len(achados) == 1
