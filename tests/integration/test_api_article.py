"""Contrato HTTP de leitura segura de artigos."""

from importlib import import_module

from fastapi.testclient import TestClient


def _client():
    try:
        app = import_module("kb.api.app").app
    except ModuleNotFoundError:
        app = None
    assert app is not None
    return TestClient(app)


def test_should_return_article_by_rel_slug_without_path_serialization(tmp_wiki):
    article = tmp_wiki / "ai" / "transformers.md"
    article.write_text(
        "---\ntitle: Transformers\ntopic: ai\ntags: [llm, attention]\nsource: raw/a.md\n---\n# Transformers\n\nConteúdo.\n",
        encoding="utf-8",
    )

    response = _client().get("/article/ai/transformers")

    assert response.status_code == 200
    assert response.json() == {
        "slug": "ai/transformers",
        "title": "Transformers",
        "topic": "ai",
        "tags": ["llm", "attention"],
        "source": "raw/a.md",
        "content": "# Transformers\n\nConteúdo.\n",
        "wikilinks": [],
        "backlinks": [],
    }


def test_should_reject_traversal_before_reading_outside_wiki(tmp_wiki):
    outside = tmp_wiki.parent / "secret.md"
    outside.write_text("segredo", encoding="utf-8")

    response = _client().get("/article/%2E%2E/secret")

    assert response.status_code == 400
    assert "secret" not in response.text


def test_should_not_expose_paths_for_missing_valid_article(tmp_wiki):
    response = _client().get("/article/ai/missing")

    assert response.status_code == 404
    assert str(tmp_wiki) not in response.text
