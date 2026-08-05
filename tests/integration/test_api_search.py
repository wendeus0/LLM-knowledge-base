"""Contrato HTTP da busca híbrida da engine."""

from pathlib import Path


def test_should_preserve_engine_order_and_use_rel_slugs(tmp_wiki, monkeypatch, api_client):
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

    response = api_client.get("/search", params={"q": "attention", "top_k": 2})

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
