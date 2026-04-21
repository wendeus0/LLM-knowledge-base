from unittest.mock import patch
from kb.heal import heal, _is_stub, _stamp_reviewed


class TestIsStub:
    """Testes unitários para _is_stub()"""

    def test_should_detect_empty_text_as_stub(self):
        """
        Dado um texto vazio,
        Quando _is_stub() é executado,
        Então deve retornar True
        """
        # RED: falha se _is_stub não detecta texto vazio
        assert _is_stub("") is True

    def test_should_detect_headers_only_as_stub(self):
        """
        Dado um texto com apenas headers e sem conteúdo,
        Quando _is_stub() é executado,
        Então deve retornar True
        """
        # RED: falha se não detecta header-only como stub
        stub_text = """---
title: Empty Article
---

# Title

## Subtítulo
"""
        assert _is_stub(stub_text) is True

    def test_should_not_mark_content_as_stub(self):
        """
        Dado um texto com conteúdo substantivo,
        Quando _is_stub() é executado,
        Então deve retornar False
        """
        # RED: falha se marca artigo com conteúdo como stub
        content = """---
title: Article
---

# Article

Isto é conteúdo substantivo sobre um tópico.
Tem várias linhas e informação real.
Mais linhas de conteúdo.
"""
        assert _is_stub(content) is False


class TestStampReviewed:
    """Testes para _stamp_reviewed()"""

    def test_should_add_reviewed_at_when_missing(self):
        """
        Dado um artigo sem reviewed_at,
        Quando _stamp_reviewed() é chamado,
        Então deve adicionar reviewed_at
        """
        article = """---
title: Test
topic: ai
---

# Test
"""
        # RED: falha se não adiciona reviewed_at
        result = _stamp_reviewed(article)
        assert "reviewed_at:" in result

    def test_should_update_reviewed_at_when_present(self):
        """
        Dado um artigo com reviewed_at antigo,
        Quando _stamp_reviewed() é chamado,
        Então deve atualizar timestamp
        """
        article = """---
title: Test
reviewed_at: 2026-01-01
---

# Test
"""
        # RED: falha se não atualiza timestamp
        result = _stamp_reviewed(article)
        assert "reviewed_at:" in result
        assert "2026-01-01" not in result


class TestHeal:
    """Testes para heal()"""

    def test_should_process_articles(self, tmp_raw_wiki):
        """
        Dado uma wiki com artigos,
        Quando heal(n=1) é executado,
        Então deve processar artigos
        """
        raw, wiki = tmp_raw_wiki

        # Criar artigo
        (wiki / "python" / "article.md").write_text("""---
title: Article
---

# Article

Content.
""")

        with patch("kb.heal.chat") as mock_chat, patch("kb.heal.commit"):
            mock_chat.return_value = "Healed."

            # RED: falha se heal não processa
            result = heal(n=1)
            assert result is not None

    def test_should_commit_after_healing(self, tmp_raw_wiki):
        """
        Dado que heal() processou e fez mudanças,
        Quando termina,
        Então deve fazer commit
        """
        raw, wiki = tmp_raw_wiki

        # Criar artigo não-stub para ser processado
        (wiki / "ai" / "test.md").write_text("""---
title: Test
---

# Test

Conteúdo substantivo sobre teste.
""")

        with (
            patch("kb.heal.chat") as mock_chat,
            patch("kb.heal.commit") as mock_commit,
            patch("random.sample") as mock_sample,
        ):
            mock_chat.return_value = "Healed version of the article"
            article_path = wiki / "ai" / "test.md"
            mock_sample.return_value = [article_path]

            heal(n=1, no_commit=False)

            # RED: falha se commit não foi chamado após mudanças
            mock_commit.assert_called()

    def test_should_return_list_of_dicts(self, tmp_raw_wiki):
        """
        Dado heal() completo,
        Quando retorna,
        Então deve ser list[dict] com resultados
        """
        raw, wiki = tmp_raw_wiki

        (wiki / "typescript" / "test.md").write_text("# Test\nContent")

        with patch("kb.heal.chat") as mock_chat, patch("kb.heal.commit"):
            mock_chat.return_value = "OK"

            # RED: falha se não retorna list[dict]
            result = heal(n=1)
            assert isinstance(result, list)
