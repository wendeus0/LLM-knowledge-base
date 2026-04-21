from pathlib import Path
from unittest.mock import patch

from kb.guardrails import SensitiveContentError
from kb.qa import answer, answer_and_file


class TestAnswer:
    def test_should_route_question_and_return_response(self, tmp_raw_wiki):
        raw, wiki = tmp_raw_wiki
        (wiki / "cybersecurity" / "xss.md").write_text("# XSS\nVulnerabilidade web.")

        with patch("kb.qa.chat") as mock_chat:
            mock_chat.return_value = "XSS é uma vulnerabilidade de segurança web."

            result = answer("Explique XSS")

            assert result is not None
            assert len(result) > 0
            assert isinstance(result, str)
            assert mock_chat.called
            assert (
                "Fonte selecionada: wiki"
                in mock_chat.call_args.kwargs["messages"][1]["content"]
            )

    def test_should_route_raw_questions_to_raw_context(self, tmp_raw_wiki):
        raw, wiki = tmp_raw_wiki
        (raw / "fonte.md").write_text(
            "Documento bruto com detalhes originais do capítulo."
        )

        with patch("kb.qa.chat") as mock_chat:
            mock_chat.return_value = "Resumo do material bruto."

            answer("Mostre o texto original da fonte")

            prompt = mock_chat.call_args.kwargs["messages"][1]["content"]
            assert "Fonte selecionada: raw" in prompt
            assert "Documento bruto" in prompt

    def test_should_raise_guardrail_for_sensitive_context(self, tmp_raw_wiki):
        raw, wiki = tmp_raw_wiki
        (wiki / "python" / "secret.md").write_text("# Secret\napi_key=abc1234567890")

        with patch("kb.qa.chat"):
            try:
                answer("secret")
            except SensitiveContentError as exc:
                assert "qa:wiki" in str(exc)
            else:
                raise AssertionError("Expected SensitiveContentError")


class TestAnswerAndFile:
    def test_should_answer_and_file_response(self, tmp_raw_wiki):
        raw, wiki = tmp_raw_wiki
        (wiki / "ai" / "test.md").write_text("# Test\nConteúdo.")

        with patch("kb.qa.chat") as mock_chat, patch("kb.qa.commit") as mock_commit:
            answer_response = "Resposta breve."
            article_response = """---
title: Question Answer
topic: general
---

# Question Answer

A resposta em formato artigo.
"""
            mock_chat.side_effect = [answer_response, article_response]

            result = answer_and_file("test", allow_sensitive=True, no_commit=False)

            assert isinstance(result, tuple)
            assert len(result) == 2
            assert result[0] == answer_response
            assert isinstance(result[1], Path)
            assert mock_commit.called
