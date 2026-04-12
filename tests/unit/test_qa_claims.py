from unittest.mock import patch

from kb.qa import answer


def test_answer_should_include_claim_confidence_context(tmp_raw_wiki):
    raw, wiki = tmp_raw_wiki
    (wiki / "ai" / "cache.md").write_text("# Cache\nRedis e performance.")

    with patch("kb.qa.chat") as mock_chat, patch("kb.qa.find_relevant_claims") as mock_claims:
        mock_claims.return_value = [
            {
                "id": "c-1",
                "text": "Projeto X usa Redis para cache.",
                "topic": "ai",
                "confidence": 0.82,
                "status": "active",
            }
        ]
        mock_chat.return_value = "Resposta baseada em contexto."

        response = answer("Qual cache usamos no projeto X?")

    assert response == "Resposta baseada em contexto."
    prompt = mock_chat.call_args.kwargs["messages"][1]["content"]
    assert "Claims relevantes" in prompt
    assert "confidence=0.82" in prompt
    assert "Projeto X usa Redis para cache." in prompt
