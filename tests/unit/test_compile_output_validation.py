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
