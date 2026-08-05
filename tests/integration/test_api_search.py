"""Contrato HTTP da busca híbrida da engine."""

from importlib import import_module
from pathlib import Path

from fastapi.testclient import TestClient


def _client():
    try:
        app = import_module("kb.api.app").app
    except ModuleNotFoundError:
        app = None
    assert app is not None
    return TestClient(app)


def test_should_preserve_engine_order_and_use_rel_slugs(tmp_wiki, monkeypatch):
    first = tmp_wiki / "ai" / "attention.md"
    second = tmp_wiki / "cybersecurity" / "attention.md"
    for path in (first, second):
        path.parent.mkdir(exist_ok=True)
        path.write_text("# Article\n", encoding="utf-8")

    engine_results = [
        {"path": first, "score": 0.8, "snippet": "primeiro"},
        {"path": second, "score": 0.4, "snippet": "segundo"},
    ]
    monkeypatch.setattr("kb.search.search", lambda *args, **kwargs: engine_results)

    response = _client().get("/search", params={"q": "attention", "top_k": 2})

    assert response.status_code == 200
    assert response.json() == {
        "results": [
            {"slug": "ai/attention", "title": "attention", "topic": "ai", "score": 0.8, "snippet": "primeiro"},
            {
                "slug": "cybersecurity/attention",
                "title": "attention",
                "topic": "cybersecurity",
                "score": 0.4,
                "snippet": "segundo",
            },
        ]
    }
    assert all(not isinstance(value, Path) for value in response.json()["results"])
