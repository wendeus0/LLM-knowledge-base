from unittest.mock import patch
from kb.compile import compile_file, discover_compile_targets, update_index


class TestCompileFile:
    """Testes unitários para compile_file()"""

    def test_should_read_raw_file_and_create_wiki_article(
        self, tmp_raw_wiki, sample_xss_md
    ):
        """
        Dado um arquivo raw válido com conteúdo,
        Quando compile_file() é chamado,
        Então deve gerar um arquivo .md na wiki
        """
        raw, wiki = tmp_raw_wiki
        raw_file = raw / "test.md"
        raw_file.write_text(sample_xss_md)

        # Mock LLM response
        mock_response = """---
title: XSS (Cross-Site Scripting)
topic: cybersecurity
tags: [xss, vulnerabilidade]
source: test.md
---

# XSS

Conteúdo compilado.
"""
        with patch("kb.compile.chat") as mock_chat, patch(
            "kb.compile.commit"
        ):
            mock_chat.return_value = mock_response

            result = compile_file(raw_file)

            # RED: falha até compile_file retornar Path do arquivo criado
            assert result is not None
            assert result.exists()
            assert "xss" in result.name.lower()

    def test_should_extract_topic_and_categorize_article(
        self, tmp_raw_wiki, sample_xss_md
    ):
        """
        Dado um documento sobre cybersecurity,
        Quando compile_file() categoriza o artigo,
        Então deve estar em wiki/cybersecurity/
        """
        raw, wiki = tmp_raw_wiki
        raw_file = raw / "security.md"
        raw_file.write_text(sample_xss_md)

        mock_response = """---
title: Test Article
topic: cybersecurity
---

# Test
"""
        with patch("kb.compile.chat") as mock_chat, patch(
            "kb.compile.commit"
        ):
            mock_chat.return_value = mock_response

            result = compile_file(raw_file)

            # RED: falha se arquivo não está em subdiretório de topic
            assert (wiki / "cybersecurity") in result.parents

    def test_should_include_frontmatter_in_compiled_article(
        self, tmp_raw_wiki, sample_xss_md
    ):
        """
        Dado um artigo compilado,
        Quando o arquivo é salvo,
        Então deve incluir YAML frontmatter com title, topic, tags
        """
        raw, wiki = tmp_raw_wiki
        raw_file = raw / "doc.md"
        raw_file.write_text(sample_xss_md)

        mock_response = """---
title: XSS
topic: cybersecurity
tags: [xss]
source: doc.md
reviewed_at: 2026-04-03
---

# XSS Article
"""
        with patch("kb.compile.chat") as mock_chat, patch(
            "kb.compile.commit"
        ):
            mock_chat.return_value = mock_response

            result = compile_file(raw_file)

            # RED: falha se não contém frontmatter válido
            content = result.read_text()
            assert "---" in content
            assert "title:" in content
            assert "topic:" in content

    def test_should_commit_to_git_after_compilation(
        self, tmp_raw_wiki, sample_xss_md
    ):
        """
        Dado um arquivo compilado com sucesso,
        Quando commit deve ser feito,
        Então git deve ter um novo commit
        """
        raw, wiki = tmp_raw_wiki
        raw_file = raw / "article.md"
        raw_file.write_text(sample_xss_md)

        mock_response = """---
title: Test
topic: ai
source: article.md
---

# Test
"""
        with patch("kb.compile.chat") as mock_chat, patch(
            "kb.compile.commit"
        ) as mock_commit:
            mock_chat.return_value = mock_response

            compile_file(raw_file)

            # RED: falha se commit não foi chamado
            mock_commit.assert_called()


class TestDiscoverCompileTargets:
    """Testes unitários para discovery de arquivos em raw/."""

    def test_should_discover_markdown_files_recursively_and_skip_metadata(self, tmp_raw_wiki):
        raw, wiki = tmp_raw_wiki
        (raw / "top.md").write_text("# Top")
        nested = raw / "books" / "livro"
        nested.mkdir(parents=True)
        (nested / "01-capitulo.md").write_text("# Capítulo 1")
        (nested / "metadata.json").write_text("{}")
        (nested / "cover.jpg").write_bytes(b"jpg")

        targets = discover_compile_targets(raw)

        assert raw / "top.md" in targets
        assert nested / "01-capitulo.md" in targets
        assert nested / "metadata.json" not in targets
        assert nested / "cover.jpg" not in targets


class TestUpdateIndex:
    """Testes unitários para update_index()"""

    def test_should_create_index_file(self, tmp_raw_wiki):
        """
        Dado uma wiki com artigos,
        Quando update_index() é executado,
        Então _index.md deve ser criado
        """
        raw, wiki = tmp_raw_wiki

        # Criar artigo de teste
        (wiki / "ai" / "article1.md").write_text("# Article 1\nContent")

        # RED: falha se _index.md não existe
        with patch("kb.compile.commit"):
            update_index()
        assert (wiki / "_index.md").exists()

    def test_should_include_articles_in_index(self, tmp_raw_wiki):
        """
        Dado artigos na wiki,
        Quando update_index() é executado,
        Então _index.md deve listar todos
        """
        raw, wiki = tmp_raw_wiki

        # Criar artigos
        (wiki / "ai" / "ml.md").write_text("# ML")
        (wiki / "cybersecurity" / "xss.md").write_text("# XSS")

        # RED: falha se index não contém referências
        with patch("kb.compile.commit"):
            update_index()
        index_content = (wiki / "_index.md").read_text()

        assert "ml" in index_content.lower() or "ML" in index_content
        assert "xss" in index_content.lower() or "XSS" in index_content

    def test_should_skip_index_file_itself(self, tmp_raw_wiki):
        """
        Dado que update_index já existe,
        Quando é reexecutado,
        Então não deve incluir _index.md no índice (evitar auto-referência)
        """
        raw, wiki = tmp_raw_wiki
        (wiki / "ai" / "test.md").write_text("# Test")

        with patch("kb.compile.commit"):
            update_index()
        # RED: falha se _index.md lista a si mesmo
        index_content = (wiki / "_index.md").read_text()
        assert "[[_index]]" not in index_content
