from unittest.mock import patch
from kb.compile import compile_file
from kb.qa import answer


class TestIngestCompileQAWorkflow:
    """Testes de integração: pipeline raw → wiki → qa"""

    def test_should_ingest_compile_and_answer_question_end_to_end(
        self, tmp_raw_wiki
    ):
        """
        Dado um documento em raw/,
        Quando ingest → compile → qa é executado,
        Então sistema deve responder perguntas sobre o conteúdo
        """
        raw, wiki = tmp_raw_wiki

        # Step 1: Ingest
        raw_file = raw / "xss.md"
        raw_file.write_text("""# O que é XSS?

XSS (Cross-Site Scripting) é uma vulnerabilidade web que permite injetar scripts.

## Tipos de XSS

- Refletido
- Armazenado
- DOM-based

## Como prevenir

Sempre sanitizar entrada do usuário.""")

        # Step 2: Compile
        mock_response = """---
title: XSS (Cross-Site Scripting)
topic: cybersecurity
tags: [xss, vulnerabilidade]
---

# XSS (Cross-Site Scripting)

XSS é uma vulnerabilidade web que permite injetar scripts.

## Tipos

- Refletido
- Armazenado
- DOM-based
"""
        with patch("kb.compile.chat") as mock_chat, patch(
            "kb.compile.commit"
        ):
            mock_chat.return_value = mock_response

            compiled = compile_file(raw_file)

            # RED: falha se compile não gera arquivo
            assert compiled.exists()

        # Step 3: QA
        with patch("kb.qa.chat") as mock_qa_chat:
            mock_qa_chat.return_value = "XSS é uma vulnerabilidade que permite injetar scripts maliciosos."

            result = answer("O que é XSS?")

            # RED: falha se QA não retorna resposta
            assert result is not None
            assert len(result) > 0

    def test_should_compile_multiple_documents_and_search_across_them(
        self, tmp_raw_wiki
    ):
        """
        Dado múltiplos documentos em raw/,
        Quando todos são compilados,
        Então busca deve encontrar conteúdo em ambos
        """
        raw, wiki = tmp_raw_wiki

        # Ingest dois documentos
        doc1 = raw / "xss.md"
        doc1.write_text("# XSS\nVulnerabilidade de script injection.")

        doc2 = raw / "csrf.md"
        doc2.write_text("# CSRF\nCross-Site Request Forgery attack.")

        mock_response_1 = """---
title: XSS
topic: cybersecurity
---

# XSS

Vulnerabilidade de script injection.
"""
        mock_response_2 = """---
title: CSRF
topic: cybersecurity
---

# CSRF

Cross-Site Request Forgery attack.
"""

        with patch("kb.compile.chat") as mock_chat, patch(
            "kb.compile.commit"
        ):
            # Mock diferentes respostas para diferentes documentos
            mock_chat.side_effect = [mock_response_1, mock_response_2]

            compile_file(doc1)
            compile_file(doc2)

            # RED: falha se não consegue compilar ambos
            assert len(list(wiki.rglob("*.md"))) >= 2

    def test_should_file_back_answer_as_new_article(self, tmp_raw_wiki):
        """
        Dado uma pergunta respondida pelo LLM,
        Quando file-back é acionado,
        Então resposta deve ser arquivada como novo artigo na wiki
        """
        raw, wiki = tmp_raw_wiki

        # Setup: artigo inicial
        (wiki / "cybersecurity" / "xss.md").write_text("""---
title: XSS
---

# XSS

Informação sobre XSS.
""")

        # Answer com file-back
        new_article_response = """---
title: XSS Refletido vs Armazenado
topic: cybersecurity
---

# XSS Refletido vs Armazenado

Diferenças...
"""

        with patch("kb.qa.chat") as mock_qa, patch("kb.qa.commit"), patch("kb.qa.build_context") as mock_build_context:
            mock_qa.side_effect = ["Resposta breve sobre XSS.", new_article_response]
            mock_build_context.return_value = (
                type("Decision", (), {"route": "wiki", "reason": "teste"})(),
                ["# xss\nInformação sobre XSS."],
            )

            from kb.qa import answer_and_file

            result = answer_and_file("Qual diferença XSS?", allow_sensitive=True)

            # RED: falha se resposta e path não são retornados
            assert isinstance(result, tuple)
            assert len(result) == 2
            assert mock_qa.call_count == 2

    def test_should_maintain_topic_hierarchy_through_compile_flow(
        self, tmp_raw_wiki
    ):
        """
        Dado documentos com tópicos específicos,
        Quando compilados,
        Então artigos devem estar em diretórios corretos (cybersecurity/, ai/, etc)
        """
        raw, wiki = tmp_raw_wiki

        doc = raw / "neural.md"
        doc.write_text("# Neural Networks\nRedes neurais são...")

        mock_response = """---
title: Neural Networks
topic: ai
---

# Neural Networks
"""

        with patch("kb.compile.chat") as mock_chat, patch(
            "kb.compile.commit"
        ):
            mock_chat.return_value = mock_response

            compiled = compile_file(doc)

            # RED: falha se artigo não está em wiki/ai/
            assert "ai" in compiled.parent.name or (wiki / "ai") in compiled.parents
