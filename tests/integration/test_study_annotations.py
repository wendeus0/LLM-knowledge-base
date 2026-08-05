from fastapi import HTTPException
from fastapi.testclient import TestClient


def _article_api(content_ref):
    def api_request(method, path, **kwargs):
        if path == "/article/ai/transformers":
            if content_ref["missing"]:
                raise HTTPException(status_code=404, detail="Artigo não encontrado.")
            return {
                "slug": "ai/transformers",
                "title": "Transformers",
                "topic": "ai",
                "tags": ["llm"],
                "content": content_ref["content"],
                "wikilinks": [],
                "backlinks": [],
            }
        if path == "/articles":
            return {"results": []}
        raise AssertionError(path)

    return api_request


def _isolated_vault(tmp_path, monkeypatch):
    from kb import config

    data_dir = tmp_path / "vault"
    wiki_dir = data_dir / "wiki"
    state_dir = data_dir / "kb_state"
    wiki_dir.mkdir(parents=True)
    state_dir.mkdir()
    monkeypatch.setattr(config, "DATA_DIR", data_dir)
    monkeypatch.setattr(config, "WIKI_DIR", wiki_dir)
    monkeypatch.setattr(config, "STATE_DIR", state_dir)
    return data_dir, wiki_dir, state_dir


def test_should_persist_note_changes_without_changing_the_compiled_article(tmp_path, monkeypatch):
    from study.web import app

    data_dir, wiki_dir, _ = _isolated_vault(tmp_path, monkeypatch)
    article_path = wiki_dir / "ai" / "transformers.md"
    article_path.parent.mkdir()
    article_path.write_text("# Transformers\n\nAtenção é tudo.", encoding="utf-8")
    before = article_path.read_bytes()
    content = {"content": "# Transformers\n\nAtenção é tudo.", "missing": False}
    monkeypatch.setattr("study.web.api_request", _article_api(content))
    client = TestClient(app)

    created = client.post("/a/ai/transformers/note", data={"body": "Rever atenção."})
    reopened_after_create = client.get("/a/ai/transformers")
    edited = client.post("/a/ai/transformers/note", data={"body": "Rever cabeças."})
    reopened_after_edit = client.get("/a/ai/transformers")
    removed = client.delete("/a/ai/transformers/note")
    reopened_after_delete = client.get("/a/ai/transformers")

    assert created.status_code == 200
    assert "Rever atenção." in created.text
    assert "Rever atenção." in reopened_after_create.text
    assert edited.status_code == 200
    assert "Rever cabeças." in edited.text
    assert "Rever cabeças." in reopened_after_edit.text
    assert removed.status_code == 200
    assert "Rever cabeças." not in removed.text
    assert "Rever cabeças." not in reopened_after_delete.text
    assert article_path.read_bytes() == before
    assert not (data_dir / "wiki" / "study.db").exists()
    assert not (data_dir / "kb_state" / "study.db").exists()


def test_should_reapply_a_highlight_when_reopening_its_article(tmp_path, monkeypatch):
    from study.web import app

    _isolated_vault(tmp_path, monkeypatch)
    content = {"content": "# Transformers\n\nAtenção é tudo.", "missing": False}
    monkeypatch.setattr("study.web.api_request", _article_api(content))
    client = TestClient(app)

    created = client.post(
        "/a/ai/transformers/highlights",
        data={"quote": "Atenção é tudo", "prefix": "Transformers\n\n", "suffix": ".", "note": ""},
    )
    reopened = client.get("/a/ai/transformers")

    assert created.status_code == 200
    assert reopened.status_code == 200
    assert '<mark class="highlight">Atenção é tudo</mark>' in reopened.text


def test_should_keep_highlight_as_orphan_when_its_text_disappears(tmp_path, monkeypatch):
    from study.web import app

    _isolated_vault(tmp_path, monkeypatch)
    content = {"content": "# Transformers\n\nAtenção é tudo.", "missing": False}
    monkeypatch.setattr("study.web.api_request", _article_api(content))
    client = TestClient(app)
    client.post(
        "/a/ai/transformers/highlights",
        data={"quote": "Atenção é tudo", "prefix": "Transformers\n\n", "suffix": ".", "note": ""},
    )
    content["content"] = "# Transformers\n\nO contexto mudou."

    reopened = client.get("/a/ai/transformers")

    assert reopened.status_code == 200
    assert '<mark class="highlight">' not in reopened.text
    assert "Destaques sem âncora" in reopened.text
    assert "Atenção é tudo" in reopened.text


def test_should_keep_highlight_as_orphan_when_its_article_disappears(tmp_path, monkeypatch):
    from study.web import app

    _isolated_vault(tmp_path, monkeypatch)
    content = {"content": "# Transformers\n\nAtenção é tudo.", "missing": False}
    monkeypatch.setattr("study.web.api_request", _article_api(content))
    client = TestClient(app)
    client.post(
        "/a/ai/transformers/highlights",
        data={"quote": "Atenção é tudo", "prefix": "Transformers\n\n", "suffix": ".", "note": ""},
    )
    content["missing"] = True

    missing_article = client.get("/a/ai/transformers")
    home = client.get("/")

    assert missing_article.status_code == 404
    assert home.status_code == 200
    assert "Destaques sem âncora" in home.text
    assert "Atenção é tudo" in home.text
    assert "ai/transformers" in home.text


def test_should_create_the_study_database_beside_the_vault_not_corpus_directories(tmp_path, monkeypatch):
    from study.web import app

    data_dir, wiki_dir, state_dir = _isolated_vault(tmp_path, monkeypatch)
    content = {"content": "# Transformers\n\nAtenção é tudo.", "missing": False}
    monkeypatch.setattr("study.web.api_request", _article_api(content))

    response = TestClient(app).post("/a/ai/transformers/note", data={"body": "Nota."})

    assert response.status_code == 200
    assert (data_dir / "study.db").is_file()
    assert not (wiki_dir / "study.db").exists()
    assert not (state_dir / "study.db").exists()
