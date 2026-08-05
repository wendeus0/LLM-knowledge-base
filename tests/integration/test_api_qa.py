"""Estabilidade do JSON de QA na fronteira HTTP."""

import json

from typer.testing import CliRunner

from kb import grounding
from kb.cli import app as cli_app

runner = CliRunner()


def _prepare(tmp_wiki, monkeypatch):
    article = tmp_wiki / "cybersecurity" / "circuit-breaker.md"
    article.write_text(
        "# Circuit breaker\nApós falhas consecutivas, o circuit breaker abre.\n",
        encoding="utf-8",
    )
    result = grounding.GroundingResult(
        status="verified",
        claims=[
            grounding.ClaimVerdict(
                claim="O circuit breaker abre após falhas consecutivas.",
                verdict="ancorada",
                evidence="Após falhas consecutivas, o circuit breaker abre.",
                scores={"entailment": 0.91, "contradiction": 0.04, "neutral": 0.05},
            )
        ],
    )
    monkeypatch.setattr("kb.qa.chat", lambda **kwargs: "Resposta ancorada.")
    monkeypatch.setattr("kb.grounding.verify", lambda *args, **kwargs: result)


def test_should_match_kb_qa_json_field_by_field_and_never_file_back(tmp_wiki, monkeypatch, api_client):
    _prepare(tmp_wiki, monkeypatch)
    question = "O que faz o circuit breaker?"

    cli_result = runner.invoke(cli_app, ["qa", question, "--json"])
    response = api_client.post("/qa", json={"question": question})

    assert cli_result.exit_code == 0
    assert response.status_code == 200
    cli_payload = json.loads(cli_result.stdout)
    api_payload = response.json()
    assert api_payload["answer"] == cli_payload["answer"]
    assert api_payload["grounding"] == cli_payload["grounding"]
    assert api_payload["saved_path"] is None
    assert set(api_payload) == {"answer", "grounding", "saved_path"}


def test_should_return_safe_conflict_for_sensitive_provider_content(tmp_wiki, api_client):
    article = tmp_wiki / "ai" / "sensitive.md"
    article.write_text(
        "Segredo do artigo: api_key: sk-123456789012345\n", encoding="utf-8"
    )

    response = api_client.post(
        "/qa", json={"question": "O que diz o segredo api_key: sk-123456789012345?"}
    )

    assert response.status_code == 409
    assert "sk-123456789012345" not in response.text
