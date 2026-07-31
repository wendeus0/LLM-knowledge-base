"""RED — feature 017: índice por chunk, com agregação por máximo.

Embedder falso e vetores trabalhados à mão: o que se testa aqui é a estrutura
do índice e a regra de agregação, não a qualidade do modelo.
"""

import json

from kb import embeddings


def _article(title: str, *sections: str) -> str:
    """Cada seção passa folgadamente do mínimo, para não ser agrupada."""
    body = "\n\n".join(f"## {name}\n" + f"{name.lower()} conteudo " * 40 for name in sections)
    return f"---\ntitle: {title}\n---\n\n{body}\n"


def _vault(tmp_path, monkeypatch, embedder=None):
    wiki = tmp_path / "wiki"
    state = tmp_path / "kb_state"
    wiki.mkdir()
    state.mkdir()
    calls = []

    def _fake_embed(texts, model=None, base_url=None):
        calls.extend(texts)
        return [[float(len(text) % 7), 1.0] for text in texts]

    monkeypatch.setattr(embeddings, "embed_texts", embedder or _fake_embed)
    return wiki, state, calls


class TestBuildIndexWithChunks:
    def test_should_store_one_vector_per_section(self, tmp_path, monkeypatch):
        wiki, state, _ = _vault(tmp_path, monkeypatch)
        (wiki / "artigo.md").write_text(
            _article("Artigo", "Alpha", "Bravo", "Charlie"), encoding="utf-8"
        )

        embeddings.build_index(wiki, state)

        payload = json.loads((state / "embeddings.json").read_text(encoding="utf-8"))
        assert payload["format"] == 2
        chunks = payload["articles"]["artigo.md"]["chunks"]
        assert len(chunks) == 3
        assert [c["heading"] for c in chunks] == ["Alpha", "Bravo", "Charlie"]
        assert all(c["vector"] for c in chunks)

    def test_should_not_reembed_unchanged_article(self, tmp_path, monkeypatch):
        wiki, state, calls = _vault(tmp_path, monkeypatch)
        (wiki / "artigo.md").write_text(_article("Artigo", "Alpha", "Bravo"), encoding="utf-8")

        embeddings.build_index(wiki, state)
        primeira = len(calls)
        embeddings.build_index(wiki, state)

        assert primeira > 0
        assert len(calls) == primeira

    def test_should_reembed_all_chunks_of_edited_article(self, tmp_path, monkeypatch):
        wiki, state, calls = _vault(tmp_path, monkeypatch)
        artigo = wiki / "artigo.md"
        artigo.write_text(_article("Artigo", "Alpha", "Bravo"), encoding="utf-8")
        embeddings.build_index(wiki, state)
        calls.clear()

        artigo.write_text(_article("Artigo", "Alpha", "Bravo", "Charlie"), encoding="utf-8")
        embeddings.build_index(wiki, state)

        assert len(calls) == 3

    def test_should_report_chunk_count_in_result(self, tmp_path, monkeypatch):
        wiki, state, _ = _vault(tmp_path, monkeypatch)
        (wiki / "a.md").write_text(_article("A", "Um", "Dois"), encoding="utf-8")

        report = embeddings.build_index(wiki, state)

        assert report["chunks"] == 2


class TestLoadIndexFormat:
    def test_should_reject_legacy_format(self, tmp_path, monkeypatch):
        _, state, _ = _vault(tmp_path, monkeypatch)
        monkeypatch.setenv("KB_EMBED_MODEL", "modelo-x")
        (state / "embeddings.json").write_text(
            json.dumps(
                {"model": "modelo-x", "dim": 2, "articles": {"a.md": {"hash": "h", "vector": [1.0, 0.0]}}}
            ),
            encoding="utf-8",
        )

        assert embeddings.load_index(state) is None


class TestSemanticRankingAggregation:
    def test_should_rank_article_by_its_best_chunk(self, tmp_path, monkeypatch):
        _, state, _ = _vault(tmp_path, monkeypatch)
        monkeypatch.setattr("kb.config.WIKI_DIR", tmp_path / "wiki")
        monkeypatch.setattr(
            embeddings, "embed_texts", lambda texts, model=None, base_url=None: [[1.0, 0.0]]
        )
        index = {
            "model": "m",
            "dim": 2,
            "articles": {
                "fraco.md": {"chunks": [{"heading": "x", "vector": [0.0, 1.0]}]},
                "forte.md": {
                    "chunks": [
                        {"heading": "irrelevante", "vector": [0.0, 1.0]},
                        {"heading": "no alvo", "vector": [1.0, 0.0]},
                    ]
                },
            },
        }

        ranking, _ = embeddings.semantic_ranking("consulta", index)

        assert ranking[0][0].name == "forte.md"
        assert ranking[0][1] > ranking[1][1]

    def test_should_not_favor_article_merely_for_having_more_chunks(self, tmp_path, monkeypatch):
        _, state, _ = _vault(tmp_path, monkeypatch)
        monkeypatch.setattr("kb.config.WIKI_DIR", tmp_path / "wiki")
        monkeypatch.setattr(
            embeddings, "embed_texts", lambda texts, model=None, base_url=None: [[1.0, 0.0]]
        )
        index = {
            "model": "m",
            "dim": 2,
            "articles": {
                "curto.md": {"chunks": [{"heading": "a", "vector": [1.0, 0.0]}]},
                "longo.md": {
                    "chunks": [{"heading": str(i), "vector": [0.5, 0.5]} for i in range(20)]
                },
            },
        }

        ranking, _ = embeddings.semantic_ranking("consulta", index)

        assert ranking[0][0].name == "curto.md"
