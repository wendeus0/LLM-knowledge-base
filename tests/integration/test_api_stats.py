"""Contrato HTTP das métricas agregadas da wiki."""

def test_should_return_engine_aggregates_without_mutating_vault(tmp_wiki, monkeypatch, api_client):
    article = tmp_wiki / "python" / "typing.md"
    article.write_text("# Typing\n", encoding="utf-8")
    monkeypatch.setattr("kb.analytics.history.DB_PATH", tmp_wiki.parent / "tracking.db")
    before = article.read_text(encoding="utf-8")

    response = api_client.get("/stats")

    assert response.status_code == 200
    assert response.json()["articles"] == {"total": 1, "by_topic": {"python": 1}}
    assert set(response.json()) == {"claims", "history_7d", "articles"}
    assert article.read_text(encoding="utf-8") == before
