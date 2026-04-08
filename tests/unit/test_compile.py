import threading
import time
from unittest.mock import patch
from kb.compile import (
    CompileArtifact,
    compile_many,
    compile_to_artifact,
    compile_file,
    discover_compile_targets,
    persist_artifact,
    update_index,
    _prepare_prompt_content,
)


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
        with patch("kb.compile.chat") as mock_chat, patch("kb.compile.commit"):
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
        with patch("kb.compile.chat") as mock_chat, patch("kb.compile.commit"):
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
        with patch("kb.compile.chat") as mock_chat, patch("kb.compile.commit"):
            mock_chat.return_value = mock_response

            result = compile_file(raw_file)

            # RED: falha se não contém frontmatter válido
            content = result.read_text()
            assert "---" in content
            assert "title:" in content
            assert "topic:" in content

    def test_should_commit_to_git_after_compilation(self, tmp_raw_wiki, sample_xss_md):
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
        with (
            patch("kb.compile.chat") as mock_chat,
            patch("kb.compile.commit") as mock_commit,
        ):
            mock_chat.return_value = mock_response

            compile_file(raw_file, no_commit=False)

            # RED: falha se commit não foi chamado
            mock_commit.assert_called()

    def test_should_not_commit_to_git_after_compilation_by_default(
        self, tmp_raw_wiki, sample_xss_md
    ):
        raw, wiki = tmp_raw_wiki
        raw_file = raw / "default-no-commit.md"
        raw_file.write_text(sample_xss_md)

        mock_response = """---
title: Default Safe
topic: ai
---

# Default Safe
"""

        with (
            patch("kb.compile.chat") as mock_chat,
            patch("kb.compile.commit") as mock_commit,
        ):
            mock_chat.return_value = mock_response

            compile_file(raw_file)

            mock_commit.assert_not_called()

    def test_should_store_summaries_with_topic_hierarchy(self, tmp_raw_wiki):
        raw, wiki = tmp_raw_wiki
        raw_file = raw / "article.md"
        raw_file.write_text("# Doc\nConteúdo")

        mock_response = """---
title: Same Slug
topic: cybersecurity
---

# Same Slug

Resumo compilado para security.
"""
        with patch("kb.compile.chat") as mock_chat, patch("kb.compile.commit"):
            mock_chat.return_value = mock_response
            compile_file(raw_file)

        assert (wiki / "summaries" / "cybersecurity" / "same-slug.md").exists()

    def test_should_reuse_existing_article_path_for_recompiled_source(
        self, tmp_raw_wiki
    ):
        raw, wiki = tmp_raw_wiki
        book_dir = raw / "books" / "mml"
        book_dir.mkdir(parents=True)
        raw_file = book_dir / "01-introduction.md"
        raw_file.write_text("# Chapter\nContent")

        first_response = """---
title: Introdução ao Machine Learning
topic: ai
source: 01-introduction.md
translated_by: ai
---

# Introdução ao Machine Learning

Conteúdo.
"""
        second_response = """---
title: Introdução ao Aprendizado de Máquina
topic: ai
source: 01-introduction.md
translated_by: ai
---

# Introdução ao Aprendizado de Máquina

Conteúdo atualizado.
"""

        with patch("kb.compile.chat") as mock_chat, patch("kb.compile.commit"):
            mock_chat.side_effect = [first_response, second_response]

            first_result = compile_file(raw_file.relative_to(raw), no_commit=True)
            second_result = compile_file(raw_file, no_commit=True)

        assert first_result == second_result
        assert second_result.name == "introducao-ao-machine-learning.md"
        assert "Aprendizado de Máquina" in second_result.read_text()


class TestCompilePromptPreparation:
    def test_should_remove_common_book_noise_from_prompt_content(self):
        content = """12\nDraft (2021-07-29) of “Mathematics for Machine Learning”. Feedback: https://mml-book.com.\nUseful line\nThis material is published by Cambridge University Press as Mathematics for Machine Learning by authors.\n\nAnother useful line\n"""

        prepared = _prepare_prompt_content(content, aggressive=True)

        assert "Draft (2021-07-29)" not in prepared
        assert "Cambridge University Press" not in prepared
        assert "Useful line" in prepared
        assert "Another useful line" in prepared

    def test_should_retry_with_preprocessed_prompt_after_provider_resource_limit_error(
        self, tmp_raw_wiki
    ):
        raw, wiki = tmp_raw_wiki
        raw_file = raw / "matrix-exercises.md"
        raw_file.write_text(
            "# Exercises\n123\nDraft (2021-07-29) of book. Feedback: https://mml-book.com.\nUseful exercise"
        )

        class FakeResourceLimitError(Exception):
            def __init__(self):
                super().__init__("Error 1102: Worker exceeded resource limits")
                self.body = {
                    "error_code": 1102,
                    "error_name": "worker_exceeded_resources",
                }

        mock_response = """---
title: Exercícios de Matrizes
topic: ai
---

# Exercícios de Matrizes

Conteúdo compilado.
"""

        with patch("kb.compile.chat") as mock_chat, patch("kb.compile.commit"):
            mock_chat.side_effect = [FakeResourceLimitError(), mock_response]

            artifact = compile_to_artifact(raw_file, allow_sensitive=False)

            assert artifact.title == "Exercícios de Matrizes"
            assert mock_chat.call_count == 2
            retry_prompt = mock_chat.call_args_list[1].kwargs["messages"][1]["content"]
            assert "Documento pré-processado" in retry_prompt
            assert "Draft (2021-07-29)" not in retry_prompt


class TestCompileArtifacts:
    def test_should_build_pure_artifact_without_persisting_files(self, tmp_raw_wiki):
        raw, wiki = tmp_raw_wiki
        raw_file = raw / "artifact.md"
        raw_file.write_text("# Artifact\nConteúdo")

        mock_response = """---
title: Artifact Title
topic: ai
---

# Artifact Title

Conteúdo compilado.
"""

        with patch("kb.compile.chat") as mock_chat, patch("kb.compile.commit"):
            mock_chat.return_value = mock_response

            artifact = compile_to_artifact(raw_file)

        assert artifact == CompileArtifact(
            raw_path=raw_file,
            source_name="artifact.md",
            compiled_markdown=mock_response,
            topic="ai",
            title="Artifact Title",
            summary_text="Conteúdo compilado.",
        )
        assert not (wiki / "ai" / "artifact-title.md").exists()
        assert not (wiki / "summaries" / "ai" / "artifact-title.md").exists()

    def test_should_persist_artifact_and_update_state(self, tmp_raw_wiki):
        raw, wiki = tmp_raw_wiki
        artifact = CompileArtifact(
            raw_path=raw / "persist.md",
            source_name="persist.md",
            compiled_markdown="""---
title: Persisted Article
topic: cybersecurity
---

# Persisted Article

Resumo persistido.
""",
            topic="cybersecurity",
            title="Persisted Article",
            summary_text="Resumo persistido.",
        )

        with patch("kb.compile.commit") as mock_commit:
            result = persist_artifact(artifact)

        assert result.exists()
        assert result == wiki / "cybersecurity" / "persisted-article.md"
        assert (wiki / "summaries" / "cybersecurity" / "persisted-article.md").exists()
        assert (
            "Persisted Article"
            in (
                wiki / "summaries" / "cybersecurity" / "persisted-article.md"
            ).read_text()
        )
        manifest = (raw.parent / "kb_state" / "manifest.json").read_text()
        knowledge = (raw.parent / "kb_state" / "knowledge.json").read_text()
        assert "Persisted Article" in manifest
        assert "Persisted Article" in knowledge
        mock_commit.assert_not_called()


class TestCompileMany:
    def test_should_compile_multiple_files_and_persist_in_stable_order(
        self, tmp_raw_wiki
    ):
        raw, wiki = tmp_raw_wiki
        first = raw / "b-second.md"
        second = raw / "a-first.md"
        first.write_text("# Second\nConteúdo")
        second.write_text("# First\nConteúdo")

        def fake_chat(*, messages):
            prompt = messages[1]["content"]
            if "b-second.md" in prompt:
                return """---
title: Second Article
topic: ai
---

# Second Article

Conteúdo do segundo arquivo.
"""
            return """---
title: First Article
topic: cybersecurity
---

# First Article

Conteúdo do primeiro arquivo.
"""

        result = None
        with (
            patch("kb.compile.chat", side_effect=fake_chat),
            patch("kb.compile.commit"),
            patch("kb.compile.update_index", wraps=update_index) as mock_update_index,
        ):
            result = compile_many([second, first], workers=2)

        assert [path.name for path in result.outputs] == [
            "first-article.md",
            "second-article.md",
        ]
        assert mock_update_index.call_count == 1
        manifest = (raw.parent / "kb_state" / "manifest.json").read_text()
        assert manifest.index("a-first.md") < manifest.index("b-second.md")
        assert (wiki / "_index.md").exists()

    def test_should_collect_partial_failures_without_aborting_batch(self, tmp_raw_wiki):
        raw, wiki = tmp_raw_wiki
        good = raw / "good.md"
        bad = raw / "bad.md"
        good.write_text("# Good\nConteúdo")
        bad.write_text("# Bad\nConteúdo")

        def fake_chat(*, messages):
            prompt = messages[1]["content"]
            if "bad.md" in prompt:
                raise RuntimeError("provider failed")
            return """---
title: Good Article
topic: ai
---

# Good Article

Conteúdo bom.
"""

        with (
            patch("kb.compile.chat", side_effect=fake_chat),
            patch("kb.compile.commit"),
        ):
            result = compile_many([good, bad], workers=2)

        assert [path.name for path in result.outputs] == ["good-article.md"]
        assert len(result.failures) == 1
        assert result.failures[0].raw_path == bad
        assert isinstance(result.failures[0].error, RuntimeError)
        assert (wiki / "ai" / "good-article.md").exists()
        assert (wiki / "_index.md").exists()

    def test_should_run_generation_concurrently_while_persisting_in_input_order(
        self, tmp_raw_wiki
    ):
        raw, wiki = tmp_raw_wiki
        targets = []
        for name in ["03-third.md", "01-first.md", "02-second.md"]:
            path = raw / name
            path.write_text(f"# {name}\nConteúdo")
            targets.append(path)

        active_calls = 0
        max_active_calls = 0
        lock = threading.Lock()

        def fake_chat(*, messages):
            nonlocal active_calls, max_active_calls
            prompt = messages[1]["content"]
            source_name = prompt.splitlines()[0].split(":", 1)[1].strip()
            title = source_name.replace(".md", "").replace("-", " ").title()
            with lock:
                active_calls += 1
                max_active_calls = max(max_active_calls, active_calls)
            time.sleep(0.03 if "03-third" in source_name else 0.01)
            with lock:
                active_calls -= 1
            return f"---\ntitle: {title}\ntopic: ai\n---\n\n# {title}\n\nConteúdo {source_name}.\n"

        with (
            patch("kb.compile.chat", side_effect=fake_chat),
            patch("kb.compile.commit"),
        ):
            result = compile_many(targets, workers=3)

        assert max_active_calls > 1
        assert [path.name for path in result.outputs] == [
            "03-third.md",
            "01-first.md",
            "02-second.md",
        ]
        manifest = (raw.parent / "kb_state" / "manifest.json").read_text()
        assert manifest.index("03-third.md") < manifest.index("01-first.md")
        assert manifest.index("01-first.md") < manifest.index("02-second.md")


class TestDiscoverCompileTargets:
    """Testes unitários para discovery de arquivos em raw/."""

    def test_should_discover_markdown_files_recursively_and_skip_metadata(
        self, tmp_raw_wiki
    ):
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
