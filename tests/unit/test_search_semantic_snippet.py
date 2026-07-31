"""RED — candidato exclusivamente semântico não pode chegar ao reranker sem snippet.

`snippets` só era populado para docs com `tf_total > 0` (casamento lexical).
Um artigo recuperado apenas pelo canal de embeddings — a classe exata que o
canal existe para resgatar — chegava ao LLM como slug sem texto, e o rerank
julgava por nome de arquivo. Suspeita registrada: parte do teto de
`recall@5 = 0,467` era isto, não limite do modelo.
"""

from kb.embeddings import semantic_ranking
from kb.rerank import _cache_key
from kb.search import search

_ARTIGO = """---
title: Circuit Breaker
---
# Circuit Breaker

Introdução curta.

## Seção Alvo

O disjuntor interrompe chamadas quando a taxa de falha excede o limiar.

## Outra Seção

Conteúdo irrelevante para a query.
"""


def _fake_semantic(path, heading="Seção Alvo"):
    def fake(query, index, with_headings=False):
        ranking = [(path, 0.9)]
        return (ranking, {path: heading}) if with_headings else ranking

    return fake


def _semantic_only_setup(tmp_wiki, monkeypatch, heading="Seção Alvo"):
    """Artigo sem nenhum termo da query: só o canal semântico o encontra."""
    wiki = tmp_wiki
    path = wiki / "ai" / "circuit-breaker.md"
    path.write_text(_ARTIGO)

    monkeypatch.setattr("kb.embeddings.load_index", lambda state_dir: {"articles": {"x": 1}})
    monkeypatch.setattr("kb.embeddings.semantic_ranking", _fake_semantic(path, heading))
    return path


class TestSemanticOnlySnippet:
    def test_should_fill_snippet_from_winning_section(self, tmp_wiki, monkeypatch):
        """
        Dado um artigo recuperado apenas pelo canal semântico,
        Quando search() monta os resultados,
        Então o snippet vem da seção que venceu no cosseno
        """
        _semantic_only_setup(tmp_wiki, monkeypatch)

        results = search("resiliencia distribuida", top_k=5, mode="hybrid")

        assert len(results) == 1
        assert "disjuntor" in results[0]["snippet"]

    def test_should_send_semantic_snippet_to_reranker(self, tmp_wiki, monkeypatch):
        """
        Dado um candidato só-semântico no head do rerank,
        Quando _apply_rerank monta a lista para o LLM,
        Então o candidato carrega snippet não-vazio
        """
        _semantic_only_setup(tmp_wiki, monkeypatch)

        captured = {}

        def fake_rerank(question, candidates):
            captured["snippets"] = [c["snippet"] for c in candidates]
            return candidates

        monkeypatch.setattr("kb.rerank.rerank", fake_rerank)

        # segundo artigo com match lexical para o head ter 2 candidatos
        (tmp_wiki / "ai" / "resiliencia.md").write_text("# R\n\nresiliencia distribuida na prática.\n")

        search("resiliencia distribuida", top_k=5, mode="hybrid", rerank_depth=5)

        assert len(captured["snippets"]) == 2
        assert all(snippet for snippet in captured["snippets"])

    def test_should_fall_back_to_first_section_when_heading_unknown(self, tmp_wiki, monkeypatch):
        """
        Dado heading do índice que não existe mais no arquivo (índice stale),
        Quando search() extrai o snippet,
        Então cai para o primeiro trecho do corpo em vez de vazio
        """
        _semantic_only_setup(tmp_wiki, monkeypatch, heading="Seção Renomeada")

        results = search("resiliencia distribuida", top_k=5, mode="hybrid")

        assert results[0]["snippet"] != ""

    def test_should_keep_lexical_snippet_when_present(self, tmp_wiki, monkeypatch):
        """
        Dado um artigo com match lexical (snippet já populado),
        Quando o canal semântico também o traz,
        Então o snippet lexical é preservado
        """
        path = _semantic_only_setup(tmp_wiki, monkeypatch)
        path.write_text(_ARTIGO + "\nA resiliencia mora aqui.\n")

        results = search("resiliencia", top_k=5, mode="hybrid")

        assert "resiliencia" in results[0]["snippet"].lower()


class TestSemanticRankingHeadings:
    def test_should_return_heading_of_best_chunk(self, tmp_path, monkeypatch):
        """
        Dado um artigo com dois chunks,
        Quando semantic_ranking roda com with_headings=True,
        Então devolve o heading do chunk de maior cosseno
        """
        monkeypatch.setattr("kb.config.WIKI_DIR", tmp_path)
        monkeypatch.setattr(
            "kb.embeddings.embed_texts",
            lambda texts, model=None, base_url=None: [[1.0, 0.0]],
        )
        index = {
            "articles": {
                "a.md": {
                    "chunks": [
                        {"heading": "longe", "vector": [0.0, 1.0]},
                        {"heading": "no alvo", "vector": [1.0, 0.0]},
                    ]
                },
            },
        }

        ranking, headings = semantic_ranking("consulta", index, with_headings=True)

        assert ranking[0][0].name == "a.md"
        assert headings[ranking[0][0]] == "no alvo"

    def test_should_keep_legacy_return_without_headings(self, tmp_path, monkeypatch):
        """Contrato antigo preservado: sem a flag, retorna só o ranking."""
        monkeypatch.setattr("kb.config.WIKI_DIR", tmp_path)
        monkeypatch.setattr(
            "kb.embeddings.embed_texts",
            lambda texts, model=None, base_url=None: [[1.0, 0.0]],
        )
        index = {"articles": {"a.md": {"chunks": [{"heading": "h", "vector": [1.0, 0.0]}]}}}

        ranking = semantic_ranking("consulta", index)

        assert isinstance(ranking, list)
        assert ranking[0][0].name == "a.md"


class TestRerankCacheKeySnippets:
    def test_should_invalidate_cache_when_snippet_changes(self):
        """
        Dado dois conjuntos de candidatos iguais exceto pelo snippet,
        Quando _cache_key é calculado,
        Então as chaves diferem — o prompt inclui o snippet, o cache também deve
        (sem isso, consertar snippet vazio mediria cache velho em silêncio)
        """
        base = [{"slug": "ai/a", "snippet": "antes"}, {"slug": "ai/b", "snippet": "x"}]
        mudou = [{"slug": "ai/a", "snippet": "depois"}, {"slug": "ai/b", "snippet": "x"}]

        assert _cache_key("q", base) != _cache_key("q", mudou)

    def test_should_keep_same_key_for_same_candidates(self):
        a = [{"slug": "ai/a", "snippet": "s1"}]
        b = [{"slug": "ai/a", "snippet": "s1"}]
        assert _cache_key("q", a) == _cache_key("q", b)
