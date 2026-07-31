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


def _fake_semantic(path, heading="Seção Alvo", ordinal=0, content_hash=""):
    def fake(query, index):
        ranking = [(path, 0.9)]
        info = {path: {"heading": heading, "ordinal": ordinal, "hash": content_hash}}
        return ranking, info

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

        def fake_rerank(question, candidates, want=None):
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

        ranking, best_chunks = semantic_ranking("consulta", index)

        assert ranking[0][0].name == "a.md"
        assert best_chunks[ranking[0][0]]["heading"] == "no alvo"
        assert best_chunks[ranking[0][0]]["ordinal"] == 1

    def test_should_return_empty_pair_when_embed_fails(self, tmp_path, monkeypatch):
        """Falha de embed degrada para ([], {}) — fallback lexical sem quebra."""
        monkeypatch.setattr("kb.config.WIKI_DIR", tmp_path)

        def boom(texts, model=None, base_url=None):
            raise RuntimeError("servidor fora")

        monkeypatch.setattr("kb.embeddings.embed_texts", boom)
        index = {"articles": {"a.md": {"chunks": [{"heading": "h", "vector": [1.0, 0.0]}]}}}

        ranking, best_chunks = semantic_ranking("consulta", index)

        assert ranking == []
        assert best_chunks == {}


class TestExactChunkSnippet:
    def test_should_pick_second_homonym_section_when_its_chunk_wins(self, tmp_wiki, monkeypatch):
        """
        Dado um artigo com dois headings `Exemplos` idênticos,
        Quando o chunk vencedor é o segundo (hash confere, ordinal aponta),
        Então o snippet vem da segunda seção, não da primeira homônima
        """
        from kb.embeddings import _content_hash

        corpo_a = "Primeiro exemplo genérico de configuração. " * 8
        corpo_b = "O disjuntor semiaberto testa uma chamada por vez. " * 8
        artigo = (
            "---\ntitle: Guia\n---\n"
            f"## Exemplos\n\n{corpo_a}\n\n"
            f"## Meio\n\n{'Conteúdo intermediário da seção do meio. ' * 8}\n\n"
            f"## Exemplos\n\n{corpo_b}\n"
        )
        wiki = tmp_wiki
        path = wiki / "ai" / "guia.md"
        path.write_text(artigo)

        from kb.chunking import build_chunks
        from kb.embeddings import _DOCUMENT_PREFIX

        chunks = build_chunks("Guia", artigo, max_chars=8000 - len(_DOCUMENT_PREFIX))
        alvo = next(
            i for i, c in enumerate(chunks) if c["heading"] == "Exemplos" and "disjuntor" in c["text"]
        )

        monkeypatch.setattr("kb.embeddings.load_index", lambda state_dir: {"articles": {"x": 1}})
        monkeypatch.setattr(
            "kb.embeddings.semantic_ranking",
            _fake_semantic(path, heading="Exemplos", ordinal=alvo, content_hash=_content_hash(artigo)),
        )

        results = search("resiliencia distribuida", top_k=5, mode="hybrid")

        assert "disjuntor" in results[0]["snippet"]

    def test_should_fall_through_when_named_section_is_empty(self, tmp_wiki, monkeypatch):
        """
        Dado heading que aponta para uma seção vazia (heading colado no próximo),
        Quando o snippet é extraído pelo caminho stale,
        Então cai para a primeira seção com prosa — seção vazia reintroduzia
        o snippet vazio que este fix elimina (14 chunks no vault real)
        """
        artigo = (
            "---\ntitle: Guia\n---\n"
            "## Vazia\n\n"
            "## Conteudo\n\n"
            "Texto real que o cosseno casou.\n"
        )
        wiki = tmp_wiki
        path = wiki / "ai" / "vazia.md"
        path.write_text(artigo)

        monkeypatch.setattr("kb.embeddings.load_index", lambda state_dir: {"articles": {"x": 1}})
        monkeypatch.setattr("kb.embeddings.semantic_ranking", _fake_semantic(path, heading="Vazia"))

        results = search("resiliencia distribuida", top_k=5, mode="hybrid")

        assert results[0]["snippet"] == "Texto real que o cosseno casou."

    def test_should_skip_code_fence_when_section_starts_with_code(self, tmp_wiki, monkeypatch):
        """
        Dado que a seção vencedora começa com bloco de código,
        Quando o snippet é extraído,
        Então pula o fence e devolve a primeira linha de prosa
        """
        artigo = (
            "---\ntitle: Guia\n---\n"
            "## Seção Alvo\n\n"
            "```python\nprint('oi')\n```\n\n"
            "A prosa vem depois do bloco de código.\n"
        )
        wiki = tmp_wiki
        path = wiki / "ai" / "codigo.md"
        path.write_text(artigo)

        monkeypatch.setattr("kb.embeddings.load_index", lambda state_dir: {"articles": {"x": 1}})
        monkeypatch.setattr("kb.embeddings.semantic_ranking", _fake_semantic(path))

        results = search("resiliencia distribuida", top_k=5, mode="hybrid")

        assert results[0]["snippet"] == "A prosa vem depois do bloco de código."


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
