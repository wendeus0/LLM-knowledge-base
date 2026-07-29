"""RED — feature 012-semantic-retrieval (RF-01, RF-02, RF-03 via CLI; RF-04, RF-05, RF-06 no search; casos de erro).

Seams: CLI `kb index build|status`; `kb.search.search`/`find_relevant` com canal semântico.
Sem rede: kb.embeddings.embed_texts mockado com vetores controlados.
"""

import json

from typer.testing import CliRunner

from kb.cli import app

runner = CliRunner()


def _fake_embed(texts, model=None, base_url=None):
    vectors = []
    for text in texts:
        lowered = text.lower()
        if "resiliencia" in lowered or "automovel" in lowered or "automóvel" in lowered:
            vectors.append([1.0, 0.0])
        else:
            vectors.append([0.0, 1.0])
    return vectors


def _seed_vault(tmp_path, monkeypatch):
    wiki = tmp_path / "wiki"
    state = tmp_path / "kb_state"
    raw = tmp_path / "raw"
    wiki.mkdir()
    state.mkdir()
    raw.mkdir()
    # artigo sobre carros SEM a palavra "automovel" (zero overlap lexical com a query)
    (wiki / "carros.md").write_text(
        "---\ntitle: Carros\ntopic: general\ntags: []\n---\n\nManutenção de resiliencia veicular.\n",
        encoding="utf-8",
    )
    (wiki / "paella.md").write_text(
        "---\ntitle: Paella\ntopic: general\ntags: []\n---\n\nReceita de culinaria espanhola.\n",
        encoding="utf-8",
    )
    monkeypatch.setattr("kb.config.WIKI_DIR", wiki)
    monkeypatch.setattr("kb.config.STATE_DIR", state)
    monkeypatch.setattr("kb.config.RAW_DIR", raw)
    monkeypatch.setattr("kb.search.WIKI_DIR", wiki)
    monkeypatch.setattr("kb.embeddings.embed_texts", _fake_embed)
    return wiki, state


def test_should_build_index_via_cli_and_report_count(tmp_path, monkeypatch):
    # RED: falha até 012-semantic-retrieval ser implementada (RF-01)
    _, state = _seed_vault(tmp_path, monkeypatch)
    result = runner.invoke(app, ["index", "build"])
    assert result.exit_code == 0
    assert "2" in result.output
    assert (state / "embeddings.json").exists()


def test_should_report_zero_to_index_when_corpus_unchanged(tmp_path, monkeypatch):
    # RED: falha até 012-semantic-retrieval ser implementada (RF-02)
    _seed_vault(tmp_path, monkeypatch)
    first = runner.invoke(app, ["index", "build"])
    assert first.exit_code == 0
    second = runner.invoke(app, ["index", "build"])
    assert second.exit_code == 0
    assert "0" in second.output


def test_should_show_coverage_and_model_in_status(tmp_path, monkeypatch):
    # RED: falha até 012-semantic-retrieval ser implementada (RF-03)
    _seed_vault(tmp_path, monkeypatch)
    monkeypatch.setenv("KB_EMBED_MODEL", "nomic-teste")
    build = runner.invoke(app, ["index", "build"])
    assert build.exit_code == 0
    result = runner.invoke(app, ["index", "status"])
    assert result.exit_code == 0
    assert "2/2" in result.output
    assert "nomic-teste" in result.output


def test_should_find_semantically_related_article_without_lexical_overlap(tmp_path, monkeypatch):
    # RED: falha até 012-semantic-retrieval ser implementada (RF-04)
    _seed_vault(tmp_path, monkeypatch)
    runner.invoke(app, ["index", "build"])
    from kb.search import search

    results = search("automovel", top_k=5)
    names = [item["path"].name for item in results]
    assert "carros.md" in names  # zero overlap lexical; só o canal semântico encontra


def test_should_return_lexical_results_unchanged_when_index_absent(tmp_path, monkeypatch):
    # RED: falha até 012-semantic-retrieval ser implementada (RF-05)
    _seed_vault(tmp_path, monkeypatch)
    from kb.search import search

    results = search("culinaria espanhola", top_k=5)
    names = [item["path"].name for item in results]
    assert names == ["paella.md"]  # comportamento lexical atual, sem erro
    status = runner.invoke(app, ["index", "status"])
    assert status.exit_code == 0
    assert "índice" in status.output.lower() or "indice" in status.output.lower()


def test_should_expose_semantic_channel_to_qa_retrieval(tmp_path, monkeypatch):
    # RED: falha até 012-semantic-retrieval ser implementada (RF-06)
    _seed_vault(tmp_path, monkeypatch)
    runner.invoke(app, ["index", "build"])
    from kb.search import find_relevant

    paths = find_relevant("automovel", top_k=5)
    assert any(p.name == "carros.md" for p in paths)


def test_should_fail_clearly_and_keep_old_index_when_embedder_is_down(tmp_path, monkeypatch):
    # RED: falha até 012-semantic-retrieval ser implementada (caso de erro: Ollama fora)
    _, state = _seed_vault(tmp_path, monkeypatch)
    first = runner.invoke(app, ["index", "build"])
    assert first.exit_code == 0
    original = (state / "embeddings.json").read_text(encoding="utf-8")

    def _down(texts, model=None, base_url=None):
        raise ConnectionError("connection refused")

    monkeypatch.setattr("kb.embeddings.embed_texts", _down)
    (tmp_path / "wiki" / "novo.md").write_text(
        "---\ntitle: Novo\n---\n\nConteúdo novo de resiliencia.\n", encoding="utf-8"
    )
    result = runner.invoke(app, ["index", "build"])
    assert result.exit_code != 0
    assert "endpoint" in result.output.lower() or "ollama" in result.output.lower()
    assert (state / "embeddings.json").read_text(encoding="utf-8") == original


def test_should_degrade_to_lexical_when_index_is_corrupted(tmp_path, monkeypatch):
    # RED: falha até 012-semantic-retrieval ser implementada (caso de erro: índice corrompido)
    _, state = _seed_vault(tmp_path, monkeypatch)
    (state / "embeddings.json").write_text("{ nem json valido", encoding="utf-8")
    from kb.search import search

    results = search("culinaria espanhola", top_k=5)
    names = [item["path"].name for item in results]
    assert names == ["paella.md"]  # sem crash, resultado lexical
    status = runner.invoke(app, ["index", "status"])
    assert status.exit_code == 0
    assert "rebuild" in status.output.lower() or "corromp" in status.output.lower()


def test_should_index_metadata_record_model_dimension(tmp_path, monkeypatch):
    # RED: falha até 012-semantic-retrieval ser implementada (RF-08: metadados de integridade)
    _, state = _seed_vault(tmp_path, monkeypatch)
    runner.invoke(app, ["index", "build"])
    payload = json.loads((state / "embeddings.json").read_text(encoding="utf-8"))
    assert payload["dim"] == 2
    assert payload["model"]
