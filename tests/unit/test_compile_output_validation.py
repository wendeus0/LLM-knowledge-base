from unittest.mock import patch

import pytest

from kb.compile import CompileArtifact, CompileOutputError, compile_to_artifact


class TestCompileOutputValidation:
    def test_should_raise_when_output_has_no_frontmatter(self, tmp_raw_wiki):
        raw, wiki = tmp_raw_wiki
        raw_file = raw / "no-frontmatter.md"
        raw_file.write_text("# Source\nConteúdo")

        with patch("kb.compile.chat") as mock_chat:
            mock_chat.return_value = "# Sem Frontmatter\n\nConteúdo compilado.\n"

            with pytest.raises(CompileOutputError) as exc:
                compile_to_artifact(raw_file)

        assert "no-frontmatter.md" in str(exc.value)

    def test_should_raise_when_title_is_missing(self, tmp_raw_wiki):
        raw, wiki = tmp_raw_wiki
        raw_file = raw / "missing-title.md"
        raw_file.write_text("# Source\nConteúdo")

        mock_response = """---
title:
topic: ai
---

# Missing Title

Conteúdo compilado.
"""
        with patch("kb.compile.chat") as mock_chat:
            mock_chat.return_value = mock_response

            with pytest.raises(CompileOutputError) as exc:
                compile_to_artifact(raw_file)

        assert "missing-title.md" in str(exc.value)

    def test_should_raise_when_body_is_empty_after_frontmatter(self, tmp_raw_wiki):
        raw, wiki = tmp_raw_wiki
        raw_file = raw / "empty-body.md"
        raw_file.write_text("# Source\nConteúdo")

        mock_response = """---
title: Empty Body
topic: ai
---

"""
        with patch("kb.compile.chat") as mock_chat:
            mock_chat.return_value = mock_response

            with pytest.raises(CompileOutputError) as exc:
                compile_to_artifact(raw_file)

        assert "empty-body.md" in str(exc.value)

    def test_should_strip_outer_fence_with_language_tag(self, tmp_raw_wiki):
        raw, wiki = tmp_raw_wiki
        raw_file = raw / "fenced.md"
        raw_file.write_text("# Source\nConteúdo")

        mock_response = """```markdown
---
title: Fenced Article
topic: ai
---

# Fenced Article

Conteúdo compilado.
```
"""
        with patch("kb.compile.chat") as mock_chat:
            mock_chat.return_value = mock_response

            artifact = compile_to_artifact(raw_file)

        assert artifact.compiled_markdown.startswith("---\n")
        assert artifact.compiled_markdown.endswith("Conteúdo compilado.\n")

    def test_should_preserve_inner_python_code_fence(self, tmp_raw_wiki):
        raw, wiki = tmp_raw_wiki
        raw_file = raw / "code.md"
        raw_file.write_text("# Source\nConteúdo")

        mock_response = """```md
---
title: Code Article
topic: python
---

# Code Article

```python
print("hello")
```

Conteúdo compilado.
```
"""
        with patch("kb.compile.chat") as mock_chat:
            mock_chat.return_value = mock_response

            artifact = compile_to_artifact(raw_file)

        assert '```python\nprint("hello")\n```' in artifact.compiled_markdown

    def test_should_return_artifact_when_output_is_valid(self, tmp_raw_wiki):
        raw, wiki = tmp_raw_wiki
        raw_file = raw / "valid.md"
        raw_file.write_text("# Source\nConteúdo")

        mock_response = """---
title: Valid Article
topic: ai
tags: [valid]
source: valid.md
---

# Valid Article

Conteúdo compilado.
"""
        with patch("kb.compile.chat") as mock_chat:
            mock_chat.return_value = mock_response

            artifact = compile_to_artifact(raw_file)

        assert artifact == CompileArtifact(
            raw_path=raw_file,
            source_name="valid.md",
            compiled_markdown=mock_response,
            topic="ai",
            title="Valid Article",
            summary_text="Conteúdo compilado.",
        )


class TestDeclaredSectionsAreNotEmpty:
    """Seção declarada e vazia é o artigo mentindo sobre o que contém.

    Origem: travessia do ticket 002 (docs/research/2026-07-30-politica-de-corpus).
    Medido no corpus real: 1.035 de 1.037 artigos têm `## Referências` sem um
    único item, e 14 têm `## Exemplos` vazia.
    """

    def test_should_raise_when_declared_section_has_no_content(self, tmp_raw_wiki):
        raw, wiki = tmp_raw_wiki
        raw_file = raw / "empty-section.md"
        raw_file.write_text("# Source\nConteúdo")

        mock_response = """---
title: Empty Section
topic: ai
---

# Empty Section

## Conceitos centrais

Conteúdo real aqui.

## Referências
"""
        with patch("kb.compile.chat") as mock_chat:
            mock_chat.return_value = mock_response

            with pytest.raises(CompileOutputError) as exc:
                compile_to_artifact(raw_file)

        assert "empty-section.md" in str(exc.value)
        assert "Referências" in str(exc.value)

    def test_should_raise_when_section_only_has_next_heading(self, tmp_raw_wiki):
        raw, wiki = tmp_raw_wiki
        raw_file = raw / "heading-only.md"
        raw_file.write_text("# Source\nConteúdo")

        mock_response = """---
title: Heading Only
topic: ai
---

# Heading Only

## Exemplos

## Limitações e trade-offs

Trade-off documentado.
"""
        with patch("kb.compile.chat") as mock_chat:
            mock_chat.return_value = mock_response

            with pytest.raises(CompileOutputError) as exc:
                compile_to_artifact(raw_file)

        assert "Exemplos" in str(exc.value)

    def test_should_accept_when_all_declared_sections_have_content(
        self, tmp_raw_wiki
    ):
        raw, wiki = tmp_raw_wiki
        raw_file = raw / "full.md"
        raw_file.write_text("# Source\nConteúdo")

        mock_response = """---
title: Full Article
topic: ai
---

# Full Article

## Conceitos centrais

Definição precisa.

## Referências

- Fonte original
"""
        with patch("kb.compile.chat") as mock_chat:
            mock_chat.return_value = mock_response

            artifact = compile_to_artifact(raw_file)

        assert artifact.title == "Full Article"


class TestTemplatePlaceholdersAreSubstituted:
    """Placeholder do template no output significa que o modelo copiou o molde."""

    def test_should_raise_when_body_keeps_template_placeholder(self, tmp_raw_wiki):
        raw, wiki = tmp_raw_wiki
        raw_file = raw / "placeholder.md"
        raw_file.write_text("# Source\nConteúdo")

        mock_response = """---
title: Placeholder Article
topic: ai
---

# Placeholder Article

## Conceitos centrais

<definições precisas; termos técnicos consolidados podem ficar em inglês>
"""
        with patch("kb.compile.chat") as mock_chat:
            mock_chat.return_value = mock_response

            with pytest.raises(CompileOutputError) as exc:
                compile_to_artifact(raw_file)

        assert "placeholder" in str(exc.value).lower()

    def test_should_not_flag_html_or_generics_as_placeholder(self, tmp_raw_wiki):
        raw, wiki = tmp_raw_wiki
        raw_file = raw / "generics.md"
        raw_file.write_text("# Source\nConteúdo")

        mock_response = """---
title: Generics Article
topic: typescript
---

# Generics Article

## Conceitos centrais

Use `Array<string>` para tipar listas, e `<div>` no JSX.
"""
        with patch("kb.compile.chat") as mock_chat:
            mock_chat.return_value = mock_response

            artifact = compile_to_artifact(raw_file)

        assert artifact.title == "Generics Article"


def test_should_compile_without_crash_when_topic_is_bracket_list(tmp_raw_wiki):
    raw, wiki = tmp_raw_wiki
    raw_file = raw / "bracket-topic.md"
    raw_file.write_text("# Source\nConteúdo")

    mock_response = """---
title: Bracket Topic
topic: [ai]
---

# Bracket Topic

Conteúdo compilado.
"""
    with patch("kb.compile.chat") as mock_chat:
        mock_chat.return_value = mock_response

        artifact = compile_to_artifact(raw_file)

    assert isinstance(artifact, CompileArtifact)
    assert artifact.topic == "ai"
