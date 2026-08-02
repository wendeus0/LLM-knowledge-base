from fastapi.testclient import TestClient


def test_should_render_article_sidebar_wikilinks_and_backlinks(monkeypatch):
    from study.web import app

    calls = []

    def api_request(method, path, **kwargs):
        calls.append((method, path, kwargs))
        if path == "/article/cybersecurity/dorks":
            return {
                "slug": "cybersecurity/dorks",
                "title": "Google Dorks",
                "topic": "cybersecurity",
                "tags": ["osint"],
                "content": "Veja [[OSINT]] e [[tema ausente]].",
                "wikilinks": [
                    {"text": "OSINT", "targets": ["ai/osint"], "ambiguous": False},
                    {"text": "tema ausente", "targets": [], "ambiguous": False},
                ],
                "backlinks": ["cybersecurity/pesquisa"],
            }
        if path == "/articles":
            return {
                "results": [
                    {
                        "slug": "cybersecurity/dorks",
                        "title": "Google Dorks",
                        "topic": "cybersecurity",
                    },
                    {
                        "slug": "cybersecurity/pesquisa",
                        "title": "Pesquisa",
                        "topic": "cybersecurity",
                    },
                ]
            }
        raise AssertionError(path)

    monkeypatch.setattr("study.web.api_request", api_request)

    response = TestClient(app).get("/a/cybersecurity/dorks")

    assert response.status_code == 200
    assert 'href="/a/ai/osint"' in response.text
    assert 'href="/a/cybersecurity/pesquisa"' in response.text
    assert "Google Dorks" in response.text
    assert "Progresso" in response.text
    assert ("GET", "/articles", {"params": {"topic": "cybersecurity"}}) in calls
