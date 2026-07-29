"""RED — feature 012-semantic-retrieval (RF-01, RF-02, RF-03, RF-07, RF-08 + truncamento).

Seams: kb.embeddings (build_index, load_index, index_status, semantic_ranking);
embed_texts é a fronteira de rede (única coisa mockada).
Índice esperado em <state_dir>/embeddings.json com metadados de modelo/dimensão.
"""

import json

import pytest

from kb.embeddings import (
    build_index,
    index_status,
    load_index,
    semantic_ranking,
)


@pytest.fixture
def fake_embedder(monkeypatch):
    """Embedder determinístico por palavra-chave; registra os textos embedados."""
    calls: list[list[str]] = []

    def _embed(texts, model=None, base_url=None):
        calls.append(list(texts))
        vectors = []
        for text in texts:
            lowered = text.lower()
            if "resiliencia" in lowered or "resiliência" in lowered:
                vectors.append([1.0, 0.0])
            elif "culinaria" in lowered or "culinária" in lowered:
                vectors.append([0.0, 1.0])
            else:
                vectors.append([0.5, 0.5])
        return vectors

    monkeypatch.setattr("kb.embeddings.embed_texts", _embed)
    return calls


def _make_wiki(tmp_path):
    wiki = tmp_path / "wiki"
    state = tmp_path / "kb_state"
    wiki.mkdir()
    state.mkdir()
    (wiki / "circuit-breaker.md").write_text(
        "---\ntitle: Circuit Breaker\n---\n\nPadrão de resiliencia para falhas.\n", encoding="utf-8"
    )
    (wiki / "paella.md").write_text(
        "---\ntitle: Paella\n---\n\nReceita de culinaria espanhola.\n", encoding="utf-8"
    )
    return wiki, state


def test_should_build_index_with_one_vector_per_article(tmp_path, fake_embedder):
    # RED: falha até 012-semantic-retrieval ser implementada (RF-01)
    wiki, state = _make_wiki(tmp_path)
    report = build_index(wiki, state)
    assert report["indexed"] == 2
    index_file = state / "embeddings.json"
    assert index_file.exists()
    payload = json.loads(index_file.read_text(encoding="utf-8"))
    assert len(payload["articles"]) == 2


def test_should_reindex_only_changed_articles_when_rebuilding(tmp_path, fake_embedder):
    # RED: falha até 012-semantic-retrieval ser implementada (RF-02)
    wiki, state = _make_wiki(tmp_path)
    build_index(wiki, state)
    (wiki / "paella.md").write_text(
        "---\ntitle: Paella\n---\n\nReceita de culinaria valenciana atualizada.\n", encoding="utf-8"
    )
    (wiki / "bulkhead.md").write_text(
        "---\ntitle: Bulkhead\n---\n\nOutro padrão de resiliencia.\n", encoding="utf-8"
    )
    (wiki / "circuit-breaker.md").unlink()

    report = build_index(wiki, state)
    assert report["indexed"] == 2  # alterado + novo
    assert report["unchanged"] == 0
    assert report["removed"] == 1

    third = build_index(wiki, state)
    assert third["indexed"] == 0
    assert third["unchanged"] == 2
    # o embedder só recebeu textos na 1ª e 2ª rodadas
    assert len(fake_embedder) == 2


def test_should_report_coverage_and_stale_articles_in_status(tmp_path, fake_embedder):
    # RED: falha até 012-semantic-retrieval ser implementada (RF-03)
    wiki, state = _make_wiki(tmp_path)
    build_index(wiki, state)
    (wiki / "novo-artigo.md").write_text(
        "---\ntitle: Novo\n---\n\nAinda não indexado.\n", encoding="utf-8"
    )
    status = index_status(wiki, state)
    assert status["total"] == 3
    assert status["indexed"] == 2
    assert "novo-artigo.md" in str(status["stale"])


def test_should_resolve_model_and_endpoint_from_env(tmp_path, fake_embedder, monkeypatch):
    # RED: falha até 012-semantic-retrieval ser implementada (RF-07)
    monkeypatch.setenv("KB_EMBED_MODEL", "modelo-custom")
    wiki, state = _make_wiki(tmp_path)
    report = build_index(wiki, state)
    assert report["model"] == "modelo-custom"
    payload = json.loads((state / "embeddings.json").read_text(encoding="utf-8"))
    assert payload["model"] == "modelo-custom"


def test_should_ignore_index_when_model_diverges(tmp_path, fake_embedder, monkeypatch):
    # RED: falha até 012-semantic-retrieval ser implementada (RF-08)
    wiki, state = _make_wiki(tmp_path)
    monkeypatch.setenv("KB_EMBED_MODEL", "modelo-antigo")
    build_index(wiki, state)
    monkeypatch.setenv("KB_EMBED_MODEL", "modelo-novo")
    assert load_index(state) is None
    status = index_status(wiki, state)
    assert "rebuild" in status["note"].lower()


def test_should_rank_by_cosine_similarity_with_hand_worked_vectors(tmp_path, fake_embedder):
    # RED: falha até 012-semantic-retrieval ser implementada
    # Trabalhado à mão: query [1,0] vs doc [1,0] → cos=1.0; vs [0,1] → cos=0.0
    wiki, state = _make_wiki(tmp_path)
    build_index(wiki, state)
    index = load_index(state)
    assert index is not None
    ranking = semantic_ranking("padrão de resiliencia", index)
    assert ranking[0][0].name == "circuit-breaker.md"
    assert ranking[0][1] == pytest.approx(1.0)
    scores = dict((p.name, s) for p, s in ranking)
    assert scores["paella.md"] == pytest.approx(0.0)


def test_should_count_truncated_articles_when_body_exceeds_limit(tmp_path, fake_embedder):
    # RED: falha até 012-semantic-retrieval ser implementada (caso de erro: truncamento)
    wiki, state = _make_wiki(tmp_path)
    (wiki / "gigante.md").write_text(
        "---\ntitle: Gigante\n---\n\n" + ("resiliencia " * 5000), encoding="utf-8"
    )
    report = build_index(wiki, state, max_chars=1000)
    assert report["truncated"] == 1
    embedded_texts = [t for call in fake_embedder for t in call]
    assert all(len(t) <= 1000 for t in embedded_texts)
