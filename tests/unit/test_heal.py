from unittest.mock import patch

from kb.heal import _is_stub, _stamp_reviewed, heal


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
            mock_chat.return_value = """---
title: Test
---

# Test

Conteúdo substantivo sobre teste com link para [[Python]].
"""
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

    def test_should_skip_invalid_output_without_frontmatter(self, tmp_raw_wiki):
        """
        Dado artigo com frontmatter,
        Quando LLM retorna markdown sem frontmatter,
        Então deve manter artigo intacto e logar skipped_invalid_output
        """
        raw, wiki = tmp_raw_wiki

        article_path = wiki / "ai" / "invalid.md"
        original = """---
title: Invalid
---

# Invalid

Conteúdo substantivo sobre teste com informação suficiente para não ser stub.
"""
        article_path.write_text(original)

        with (
            patch("kb.heal.chat") as mock_chat,
            patch("random.sample") as mock_sample,
        ):
            mock_chat.return_value = "# Invalid\n\nConteúdo sem frontmatter."
            mock_sample.return_value = [article_path]

            result = heal(n=1)

            assert article_path.read_text() == original
            assert result == [{"file": "invalid.md", "action": "skipped_invalid_output"}]

    def test_should_skip_collapsed_output(self, tmp_raw_wiki):
        """
        Dado artigo com conteúdo longo,
        Quando LLM retorna saída muito menor,
        Então deve manter artigo intacto e logar skipped_invalid_output
        """
        raw, wiki = tmp_raw_wiki

        article_path = wiki / "ai" / "collapse.md"
        original = """---
title: Collapse
---

# Collapse

Conteúdo substantivo sobre teste com informação suficiente para não ser stub.
Esta segunda frase aumenta o tamanho original para validar colapso de conteúdo.
Esta terceira frase mantém o artigo grande o suficiente para a heurística.
"""
        article_path.write_text(original)

        with (
            patch("kb.heal.chat") as mock_chat,
            patch("random.sample") as mock_sample,
        ):
            mock_chat.return_value = """---
title: Collapse
---

# Collapse
"""
            mock_sample.return_value = [article_path]

            result = heal(n=1)

            assert article_path.read_text() == original
            assert result == [{"file": "collapse.md", "action": "skipped_invalid_output"}]

    def test_should_backup_before_valid_heal_write(self, tmp_raw_wiki):
        """
        Dado saída válida do LLM,
        Quando heal escreve o artigo,
        Então deve criar backup em .heal_backup
        """
        raw, wiki = tmp_raw_wiki

        article_path = wiki / "ai" / "valid.md"
        original = """---
title: Valid
---

# Valid

Conteúdo substantivo sobre teste com informação suficiente para não ser stub.
"""
        article_path.write_text(original)

        response = """---
title: Valid
---

# Valid

Conteúdo substantivo sobre teste com informação suficiente para não ser stub e link para [[Python]].
"""

        with (
            patch("kb.heal.chat") as mock_chat,
            patch("random.sample") as mock_sample,
        ):
            mock_chat.return_value = response
            mock_sample.return_value = [article_path]

            result = heal(n=1)

            assert result == [{"file": "valid.md", "action": "healed"}]
            assert "[[Python]]" in article_path.read_text()
            backups = list((wiki / ".heal_backup").glob("valid.*.md"))
            assert len(backups) == 1
            assert backups[0].read_text() == original

    def test_should_backup_before_stub_delete(self, tmp_raw_wiki):
        """
        Dado stub na wiki,
        Quando heal deleta o stub,
        Então deve criar backup em .heal_backup
        """
        raw, wiki = tmp_raw_wiki

        stub_path = wiki / "ai" / "stub.md"
        original = """---
title: Stub
---

# Stub
"""
        stub_path.write_text(original)

        with patch("random.sample") as mock_sample:
            mock_sample.return_value = [stub_path]

            result = heal(n=1)

            assert result == [{"file": "stub.md", "action": "deleted_stub"}]
            assert not stub_path.exists()
            backups = list((wiki / ".heal_backup").glob("stub.*.md"))
            assert len(backups) == 1
            assert backups[0].read_text() == original

    def test_should_exclude_heal_backup_files_from_candidates(self, tmp_raw_wiki):
        """
        Dado arquivo dentro de .heal_backup,
        Quando heal coleta candidatos,
        Então backup não deve ser processado
        """
        raw, wiki = tmp_raw_wiki

        article_path = wiki / "ai" / "article.md"
        article_path.write_text("""---
title: Article
---

# Article

Conteúdo substantivo sobre teste com informação suficiente para não ser stub.
""")
        backup_dir = wiki / ".heal_backup"
        backup_dir.mkdir()
        backup_path = backup_dir / "article.20260709-120000.md"
        backup_path.write_text("""---
title: Backup
---

# Backup

Conteúdo substantivo de backup que nunca deve ser processado pelo heal.
""")

        def sample(candidates, count):
            assert backup_path not in candidates
            return [article_path]

        with (
            patch("kb.heal.chat") as mock_chat,
            patch("random.sample") as mock_sample,
        ):
            mock_chat.return_value = "NO_CHANGES"
            mock_sample.side_effect = sample

            result = heal(n=10)

            assert result == [{"file": "article.md", "action": "reviewed_no_changes"}]
