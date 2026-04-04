import pytest
from pathlib import Path
from unittest.mock import patch
from kb.qa import answer, answer_and_file


class TestAnswer:
    """Testes unitários para answer()"""

    def test_should_search_wiki_and_return_response(self, tmp_raw_wiki):
        """
        Dado uma wiki com artigos e uma pergunta,
        Quando answer() é chamado,
        Então deve retornar uma resposta string
        """
        raw, wiki = tmp_raw_wiki

        # Criar artigo de teste
        (wiki / "cybersecurity" / "xss.md").write_text("# XSS\nVulnerabilidade web.")

        mock_search_result = [wiki / "cybersecurity" / "xss.md"]
        mock_llm_response = "XSS é uma vulnerabilidade de segurança web."

        with patch("kb.qa.find_relevant") as mock_search, patch(
            "kb.qa.chat"
        ) as mock_chat:
            mock_search.return_value = mock_search_result
            mock_chat.return_value = mock_llm_response

            result = answer("O que é XSS?")

            # RED: falha se não retorna resposta
            assert result is not None
            assert len(result) > 0
            assert isinstance(result, str)

    def test_should_call_search_with_question(self, tmp_raw_wiki):
        """
        Dado uma pergunta,
        Quando answer() executa,
        Então deve chamar search para encontrar artigos
        """
        raw, wiki = tmp_raw_wiki

        with patch("kb.qa.find_relevant") as mock_search, patch(
            "kb.qa.chat"
        ) as mock_chat:
            mock_search.return_value = []
            mock_chat.return_value = "Resposta genérica"

            answer("teste?")

            # RED: falha se search não foi chamado
            mock_search.assert_called()

    def test_should_handle_no_relevant_articles(self, tmp_raw_wiki):
        """
        Dado uma pergunta sem artigos relevantes,
        Quando answer() é chamado,
        Então deve retornar uma resposta mesmo assim
        """
        raw, wiki = tmp_raw_wiki

        with patch("kb.qa.find_relevant") as mock_search, patch(
            "kb.qa.chat"
        ) as mock_chat:
            mock_search.return_value = []
            mock_chat.return_value = "Não encontrei informações."

            result = answer("pergunta obscura?")

            # RED: falha se resultado é None
            assert result is not None


class TestAnswerAndFile:
    """Testes para answer_and_file() — file-back loop"""

    def test_should_answer_and_file_response(self, tmp_raw_wiki):
        """
        Dado uma pergunta,
        Quando answer_and_file() é executado,
        Então deve salvar a resposta como artigo
        """
        raw, wiki = tmp_raw_wiki

        with patch("kb.qa.find_relevant") as mock_search, patch(
            "kb.qa.chat"
        ) as mock_chat, patch("kb.qa.commit") as mock_commit:
            mock_search.return_value = []
            # Primeira chamada para answer(), segunda para gerar artigo
            answer_response = "Machine learning é..."
            article_response = """---
title: Machine Learning
topic: ai
---

# Machine Learning

Machine learning é um campo da IA.
"""
            mock_chat.side_effect = [answer_response, article_response]

            result = answer_and_file("O que é machine learning?")

            # RED: falha se não escreve arquivo
            assert mock_commit.called

    def test_should_return_tuple_with_answer_and_path(self, tmp_raw_wiki):
        """
        Dado uma resposta arquivada,
        Quando answer_and_file retorna,
        Então deve ser tuple(resposta, path)
        """
        raw, wiki = tmp_raw_wiki

        # Criar um artigo para que find_relevant retorne algo
        (wiki / "ai" / "test.md").write_text("# Test\nConteúdo.")

        with patch("kb.qa.chat") as mock_chat, patch(
            "kb.qa.commit"
        ) as mock_commit:
            answer_response = "Resposta breve."
            article_response = """---
title: Question Answer
topic: general
---

# Question Answer

A resposta em formato artigo.
"""
            mock_chat.side_effect = [answer_response, article_response]

            result = answer_and_file("test")

            # RED: falha se não retorna tuple
            assert isinstance(result, tuple)
            assert len(result) == 2
            assert result[0] == answer_response
            assert isinstance(result[1], Path)
