import json

import pytest
from fastapi.testclient import TestClient


def _isolated_vault(tmp_path, monkeypatch):
    from kb import config

    data_dir = tmp_path / "vault"
    wiki_dir = data_dir / "wiki"
    wiki_dir.mkdir(parents=True)
    monkeypatch.setattr(config, "DATA_DIR", data_dir)
    monkeypatch.setattr(config, "WIKI_DIR", wiki_dir)
    return data_dir, wiki_dir


def _article_api(content):
    def api_request(method, path, **kwargs):
        if method == "GET" and path == "/article/ai/transformers":
            return {
                "slug": "ai/transformers",
                "title": "Transformers",
                "topic": "ai",
                "tags": [],
                "content": content,
                "wikilinks": [],
                "backlinks": [],
            }
        if method == "GET" and path == "/articles":
            return {"results": []}
        raise AssertionError((method, path, kwargs))

    return api_request


def _cards(*fronts):
    return json.dumps(
        [{"front": front, "back": "A atenção relaciona tokens."} for front in fronts]
    )


def _verified(verdict):
    from kb.grounding import ClaimVerdict, GroundingResult

    if verdict in {"degraded", "skipped"}:
        return GroundingResult(status=verdict)
    return GroundingResult(
        status="verified",
        claims=[
            ClaimVerdict(
                claim="A atenção relaciona tokens.",
                verdict=verdict,
                evidence="O mecanismo de atenção relaciona tokens.",
            )
        ],
    )


def test_should_accept_an_anchored_card_when_generated_from_an_article(tmp_path, monkeypatch):
    from study.cards import get_card
    from study.web import app

    _isolated_vault(tmp_path, monkeypatch)
    monkeypatch.setattr("study.web.api_request", _article_api("Atenção relaciona tokens."))
    monkeypatch.setattr("kb.client.chat", lambda *args, **kwargs: _cards("O que a atenção relaciona?"))
    monkeypatch.setattr("kb.grounding.verify", lambda *args: _verified("ancorada"))

    client = TestClient(app)
    generated = client.post("/a/ai/transformers/cards/generate")

    assert generated.status_code == 200
    assert "ancorada" in generated.text
    assert "Aceitar" in generated.text
    card_id = get_card(1)["id"]
    accepted = client.post(f"/cards/{card_id}/accept")

    assert accepted.status_code == 200
    assert get_card(card_id)["state"] == "aceito"


@pytest.mark.parametrize("verdict", ["contradita", "sem apoio", "degraded", "skipped"])
def test_should_block_acceptance_when_grounding_is_not_anchored(
    tmp_path, monkeypatch, verdict
):
    from study.cards import get_card
    from study.web import app

    _isolated_vault(tmp_path, monkeypatch)
    monkeypatch.setattr("study.web.api_request", _article_api("Atenção relaciona tokens."))
    monkeypatch.setattr("kb.client.chat", lambda *args, **kwargs: _cards("O que a atenção relaciona?"))
    monkeypatch.setattr("kb.grounding.verify", lambda *args: _verified(verdict))

    client = TestClient(app)
    generated = client.post("/a/ai/transformers/cards/generate")
    card_id = get_card(1)["id"]
    acceptance = client.post(f"/cards/{card_id}/accept")

    assert generated.status_code == 200
    assert verdict in generated.text
    assert "Aceitar" not in generated.text
    assert acceptance.status_code == 409
    assert get_card(card_id)["state"] == "curadoria"


def test_should_keep_card_in_curation_when_grounding_is_unavailable(tmp_path, monkeypatch):
    from kb.grounding import GroundingUnavailable
    from study.cards import get_card
    from study.web import app

    _isolated_vault(tmp_path, monkeypatch)
    monkeypatch.setattr("study.web.api_request", _article_api("Atenção relaciona tokens."))
    monkeypatch.setattr("kb.client.chat", lambda *args, **kwargs: _cards("O que a atenção relaciona?"))
    monkeypatch.setattr(
        "kb.grounding.verify",
        lambda *args: (_ for _ in ()).throw(GroundingUnavailable("NLI indisponível")),
    )

    response = TestClient(app).post("/a/ai/transformers/cards/generate")

    assert response.status_code == 200
    assert "Verificação indisponível" in response.text
    assert get_card(1)["state"] == "curadoria"


def test_should_keep_compiled_article_unchanged_when_curating_cards(tmp_path, monkeypatch):
    from study.cards import get_card
    from study.web import app

    _, wiki_dir = _isolated_vault(tmp_path, monkeypatch)
    article_path = wiki_dir / "ai" / "transformers.md"
    article_path.parent.mkdir()
    article_path.write_text("# Transformers\n\nAtenção relaciona tokens.", encoding="utf-8")
    before = article_path.read_bytes()
    monkeypatch.setattr("study.web.api_request", _article_api("Atenção relaciona tokens."))
    monkeypatch.setattr(
        "kb.client.chat",
        lambda *args, **kwargs: _cards("Card um?", "Card dois?", "Card três?"),
    )
    monkeypatch.setattr("kb.grounding.verify", lambda *args: _verified("ancorada"))

    client = TestClient(app)
    client.post("/a/ai/transformers/cards/generate")
    accepted = client.post("/cards/1/accept")
    edited = client.post("/cards/2/edit", data={"front": "Card editado?", "back": "Resposta editada."})
    discarded = client.post("/cards/3/discard")

    assert accepted.status_code == edited.status_code == discarded.status_code == 200
    assert get_card(1)["state"] == "aceito"
    assert get_card(2)["front"] == "Card editado?"
    assert get_card(3)["state"] == "descartado"
    assert article_path.read_bytes() == before
