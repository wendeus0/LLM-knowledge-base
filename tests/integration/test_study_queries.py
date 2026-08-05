from fastapi.testclient import TestClient


def test_should_render_search_results_from_the_engine_api(monkeypatch):
    from study.web import app

    def api_request(method, path, **kwargs):
        assert method == "GET"
        assert path == "/search"
        assert kwargs == {"params": {"q": "dorks", "top_k": 10}}
        return {
            "results": [
                {
                    "slug": "cybersecurity/dorks",
                    "title": "Google Dorks",
                    "topic": "cybersecurity",
                    "snippet": "Operadores de busca.",
                    "score": 0.9,
                }
            ]
        }

    monkeypatch.setattr("study.web.api_request", api_request)

    response = TestClient(app).post("/buscar", data={"q": "dorks"})

    assert response.status_code == 200
    assert 'href="/a/cybersecurity/dorks"' in response.text
    assert "Operadores de busca." in response.text


def test_should_preserve_grounding_block_when_rendering_an_answer(monkeypatch):
    from study.web import app

    def api_request(method, path, **kwargs):
        assert method == "POST"
        assert path == "/qa"
        assert kwargs == {"json": {"question": "O que são dorks?"}}
        return {
            "answer": "São operadores de busca.",
            "grounding": {
                "status": "degraded",
                "checked_claims": 1,
                "unverified_due_to_limit": 2,
                "claims": [
                    {
                        "claim": "Dorks são operadores.",
                        "verdict": "ancorada",
                        "evidence": "artigo",
                        "scores": {},
                    }
                ],
            },
            "saved_path": None,
        }

    monkeypatch.setattr("study.web.api_request", api_request)

    response = TestClient(app).post("/perguntar", data={"question": "O que são dorks?"})

    assert response.status_code == 200
    assert "São operadores de busca." in response.text
    assert "degraded" in response.text
    assert "2 afirmações sem verificação" in response.text
    assert "Dorks são operadores." in response.text
