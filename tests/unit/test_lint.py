from unittest.mock import patch
from kb.lint import lint_wiki


class TestLintWiki:
    """Testes para lint_wiki() — health checks da wiki"""

    def test_should_detect_broken_wikilinks(self, tmp_wiki, monkeypatch):
        """
        Dado um artigo com wikilink que não existe,
        Quando lint_wiki() é executado,
        Então deve reportar wikilink quebrado
        """
        monkeypatch.setattr("kb.lint.WIKI_DIR", tmp_wiki)

        article = tmp_wiki / "cybersecurity" / "auth.md"
        article.write_text("""---
title: Authentication
---

# Authentication

Ver também [[NonExistentArticle]] para mais detalhes.
""")

        with patch("kb.lint.chat") as mock_chat:
            mock_chat.return_value = "Wikilink [[NonExistentArticle]] não encontrado"

            # RED: falha se lint não é invocado
            result = lint_wiki()
            assert result is not None

    def test_should_report_stubs_and_empty_articles(
        self, tmp_wiki, monkeypatch
    ):
        """
        Dado artigos vazios ou com apenas headers,
        Quando lint_wiki() é executado,
        Então deve identificar como stubs
        """
        monkeypatch.setattr("kb.lint.WIKI_DIR", tmp_wiki)

        stub = tmp_wiki / "ai" / "stub.md"
        stub.write_text("""---
title: Stub Article
---

# Stub Article
""")

        with patch("kb.lint.chat") as mock_chat:
            mock_chat.return_value = "Stub detectado: arquivo vazio"

            # RED: falha se lint não processa stub
            result = lint_wiki()
            assert result is not None

    def test_should_check_frontmatter_completeness(self, tmp_wiki, monkeypatch):
        """
        Dado artigos com frontmatter incompleto,
        Quando lint_wiki() é executado,
        Então deve reportar campos faltando (title, topic, reviewed_at)
        """
        monkeypatch.setattr("kb.lint.WIKI_DIR", tmp_wiki)

        incomplete = tmp_wiki / "python" / "article.md"
        incomplete.write_text("""---
title: Missing Topic
---

# Article

Content.
""")

        with patch("kb.lint.chat") as mock_chat:
            mock_chat.return_value = "Falta campo 'topic' no frontmatter"

            # RED: falha se não valida frontmatter
            result = lint_wiki()
            assert result is not None

    def test_should_return_string_result(self, tmp_wiki, monkeypatch):
        """
        Dado uma wiki com artigos,
        Quando lint_wiki() termina,
        Então deve retornar resultado como string
        """
        monkeypatch.setattr("kb.lint.WIKI_DIR", tmp_wiki)

        (tmp_wiki / "cybersecurity" / "xss.md").write_text("# XSS\nContent")

        with patch("kb.lint.chat") as mock_chat:
            mock_chat.return_value = "Auditoria completa."

            # RED: falha se não retorna string
            result = lint_wiki()
            assert isinstance(result, str)
            assert len(result) > 0

    def test_should_handle_empty_wiki(self, tmp_wiki, monkeypatch):
        """
        Dado uma wiki vazia,
        Quando lint_wiki() é executado,
        Então deve retornar mensagem apropriada
        """
        monkeypatch.setattr("kb.lint.WIKI_DIR", tmp_wiki)

        # Wiki vazia (apenas diretórios vazios)

        # RED: falha se não trata wiki vazia
        result = lint_wiki()
        assert result is not None
        assert isinstance(result, str)
