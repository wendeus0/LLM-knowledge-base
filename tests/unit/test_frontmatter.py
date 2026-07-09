from kb.frontmatter import has_frontmatter, parse, serialize


def test_should_parse_simple_keys_when_frontmatter_is_valid():
    text = """---
title: Test Article
topic: ai
source: test.md
---

# Test

Conteúdo.
"""

    meta, body = parse(text)

    assert meta == {
        "title": "Test Article",
        "topic": "ai",
        "source": "test.md",
    }
    assert body == "\n# Test\n\nConteúdo.\n"
    assert has_frontmatter(text) is True


def test_should_return_empty_meta_and_original_text_when_frontmatter_is_missing():
    text = "# Test\n\nConteúdo sem frontmatter.\n"

    meta, body = parse(text)

    assert meta == {}
    assert body == text
    assert has_frontmatter(text) is False


def test_should_preserve_colon_in_value_when_value_contains_colon():
    text = """---
title: Attention: is all you need
topic: ai
---

# Attention
"""

    meta, _ = parse(text)

    assert meta["title"] == "Attention: is all you need"


def test_should_trim_key_indent_when_key_has_leading_spaces():
    text = """---
  topic: ai
title: Test
---

# Test
"""

    meta, _ = parse(text)

    assert meta["topic"] == "ai"


def test_should_parse_tags_list_when_value_is_flat_bracket_list():
    text = """---
title: Test
tags: [a, b]
---

# Test
"""

    meta, _ = parse(text)

    assert meta["tags"] == ["a", "b"]


def test_should_return_empty_meta_and_original_text_when_frontmatter_is_unclosed():
    text = """---
title: Test
topic: ai

# Test
"""

    meta, body = parse(text)

    assert meta == {}
    assert body == text
    assert has_frontmatter(text) is False


def test_should_reconstruct_equivalent_document_when_parse_result_is_serialized():
    text = """---
title: Attention: is all you need
topic: ai
tags: [paper, transformer]
---

# Attention

Body.
"""

    meta, body = parse(text)
    reconstructed = serialize(meta, body)

    assert parse(reconstructed) == (meta, body)
    assert reconstructed == text


def test_should_keep_bracket_value_as_string_when_key_is_not_tags():
    text = """---
title: [Attention]
topic: [ai]
tags: [a, b]
---

# T
"""

    meta, _ = parse(text)

    assert meta["title"] == "[Attention]"
    assert meta["topic"] == "[ai]"
    assert meta["tags"] == ["a", "b"]
