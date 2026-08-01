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


class TestAnswerAndFileGuards:
    def test_should_use_fallback_title_when_frontmatter_title_is_empty(
        self, tmp_raw_wiki
    ):
        """
        Dado artigo do LLM com title vazio no frontmatter,
        Quando answer_and_file arquiva na wiki,
        Então deve usar o fallback (pergunta) em vez de slug vazio
        """
        raw, wiki = tmp_raw_wiki
        (wiki / "ai" / "test.md").write_text("# Test\nConteúdo.")

        with patch("kb.qa.chat") as mock_chat, patch("kb.qa.commit"):
            article_response = """---
title:
topic: general
---

# Artigo

Corpo da resposta.
"""
            mock_chat.side_effect = ["Resposta breve.", article_response]

            _, out = answer_and_file(
                "test", allow_sensitive=True, no_commit=True, to_wiki=True
            )

        assert out.name != ".md"
        assert "test" in out.name


class TestQaGrounding:
    """Integração da verificação de ancoragem no fluxo do qa (T-004).

    A resposta nunca depende do serviço NLI: sem ele, o texto sai igual e o
    usuário recebe um aviso, uma vez por execução.
    """

    def _wiki(self, tmp_raw_wiki):
        raw, wiki = tmp_raw_wiki
        (wiki / "cybersecurity" / "xss.md").write_text(
            "# XSS\nVulnerabilidade web que injeta script na página renderizada."
        )
        return wiki

    def test_should_attach_grounding_to_the_structured_answer(self, tmp_raw_wiki, monkeypatch):
        from kb import grounding, qa

        self._wiki(tmp_raw_wiki)
        monkeypatch.setattr(
            grounding,
            "verify",
            lambda response, context, max_pairs=None: grounding.GroundingResult(
                status="verified",
                claims=[grounding.ClaimVerdict(claim="uma afirmação", verdict="ancorada")],
            ),
        )

        with patch("kb.qa.chat") as mock_chat:
            mock_chat.return_value = "XSS é uma vulnerabilidade de segurança web."

            resultado = qa.answer_with_grounding("Explique XSS")

        assert resultado.answer == "XSS é uma vulnerabilidade de segurança web."
        assert resultado.grounding.status == "verified"
        assert resultado.grounding.claims[0].verdict == "ancorada"

    def test_should_keep_the_answer_when_grounding_is_degraded(self, tmp_raw_wiki, monkeypatch):
        from kb import grounding, qa

        self._wiki(tmp_raw_wiki)
        monkeypatch.setattr(
            grounding,
            "verify",
            lambda response, context, max_pairs=None: grounding.GroundingResult(status="degraded"),
        )

        with patch("kb.qa.chat") as mock_chat:
            mock_chat.return_value = "XSS é uma vulnerabilidade de segurança web."

            resultado = qa.answer_with_grounding("Explique XSS")

        assert resultado.answer == "XSS é uma vulnerabilidade de segurança web."
        assert resultado.grounding.status == "degraded"

    def test_should_keep_the_answer_when_grounding_raises_unexpectedly(
        self, tmp_raw_wiki, monkeypatch, capsys
    ):
        from kb import grounding, qa

        self._wiki(tmp_raw_wiki)

        def _boom(response, context, max_pairs=None):
            raise grounding.GroundingUnavailable("serviço fora do ar")

        monkeypatch.setattr(grounding, "verify", _boom)

        with patch("kb.qa.chat") as mock_chat:
            mock_chat.return_value = "XSS é uma vulnerabilidade de segurança web."

            resultado = qa.answer_with_grounding("Explique XSS")

        assert resultado.answer == "XSS é uma vulnerabilidade de segurança web."
        assert resultado.grounding.status == "degraded"

    def test_should_warn_once_in_stderr_when_grounding_is_degraded(
        self, tmp_raw_wiki, monkeypatch, capsys
    ):
        from kb import grounding, qa

        self._wiki(tmp_raw_wiki)
        monkeypatch.setattr(
            grounding,
            "verify",
            lambda response, context, max_pairs=None: grounding.GroundingResult(status="degraded"),
        )
        monkeypatch.setattr(qa, "_grounding_warned", False, raising=False)

        with patch("kb.qa.chat") as mock_chat:
            mock_chat.return_value = "XSS é uma vulnerabilidade de segurança web."

            qa.answer_with_grounding("Explique XSS")
            qa.answer_with_grounding("Explique XSS de novo")

        erro = capsys.readouterr().err
        assert erro.lower().count("ancoragem") == 1

    def test_should_skip_grounding_entirely_when_disabled(self, tmp_raw_wiki, monkeypatch):
        from kb import grounding, qa

        self._wiki(tmp_raw_wiki)

        def _nao_deve_chamar(response, context, max_pairs=None):
            raise AssertionError("verify não deve ser chamado com grounding desligado")

        monkeypatch.setattr(grounding, "verify", _nao_deve_chamar)

        with patch("kb.qa.chat") as mock_chat:
            mock_chat.return_value = "XSS é uma vulnerabilidade de segurança web."

            resultado = qa.answer_with_grounding("Explique XSS", grounding_enabled=False)

        assert resultado.answer == "XSS é uma vulnerabilidade de segurança web."
        assert resultado.grounding.status == "skipped"

    def test_should_keep_answer_returning_plain_text_for_existing_callers(
        self, tmp_raw_wiki, monkeypatch
    ):
        from kb import grounding, qa

        self._wiki(tmp_raw_wiki)
        monkeypatch.setattr(
            grounding,
            "verify",
            lambda response, context, max_pairs=None: grounding.GroundingResult(status="verified"),
        )

        with patch("kb.qa.chat") as mock_chat:
            mock_chat.return_value = "XSS é uma vulnerabilidade de segurança web."

            resultado = qa.answer("Explique XSS")

        assert isinstance(resultado, str)
        assert resultado == "XSS é uma vulnerabilidade de segurança web."
