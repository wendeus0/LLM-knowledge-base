import json
from unittest.mock import patch

from kb.compile import compile_to_artifact

VALID_RESPONSE = """---
title: Redes Neurais
topic: ai
tags: [deep-learning]
source: 02-cap.md
---

# Redes Neurais

Conteúdo compilado.
"""


def test_should_use_chapter_template_and_book_context_for_listed_book_chapter(
    tmp_raw_wiki,
):
    raw, wiki = tmp_raw_wiki
    book_dir = raw / "books" / "deep-learning"
    book_dir.mkdir(parents=True)
    raw_file = book_dir / "02-cap.md"
    raw_file.write_text("# Redes Neurais\nConteúdo")
    chapters = [
        {
            "index": index,
            "title": f"Capítulo {index}",
            "file": f"{index:02d}-cap.md",
            "source_href": f"chapter-{index}.xhtml",
        }
        for index in range(1, 13)
    ]
    chapters[1] = {
        "index": 2,
        "title": "Redes Neurais",
        "file": "02-cap.md",
        "source_href": "chapter-2.xhtml",
    }
    metadata = {
        "book_title": "Deep Learning",
        "book_author": "Ian Goodfellow",
        "chapter_count": 12,
        "chapters": chapters,
    }
    (book_dir / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False), encoding="utf-8"
    )

    with patch("kb.compile.chat", return_value=VALID_RESPONSE) as mock_chat:
        compile_to_artifact(raw_file)

    messages = mock_chat.call_args.kwargs["messages"]
    system_prompt = messages[0]["content"]
    user_prompt = messages[1]["content"]
    assert "capítulos vizinhos" in system_prompt
    assert "capítulo 2/12" in user_prompt
    assert "Deep Learning" in user_prompt


def test_should_use_article_template_for_common_raw_file_without_metadata(
    tmp_raw_wiki,
):
    raw, wiki = tmp_raw_wiki
    raw_file = raw / "article.md"
    raw_file.write_text("# Artigo\nConteúdo")

    with patch("kb.compile.chat", return_value=VALID_RESPONSE) as mock_chat:
        compile_to_artifact(raw_file)

    messages = mock_chat.call_args.kwargs["messages"]
    system_prompt = messages[0]["content"]
    user_prompt = messages[1]["content"]
    assert "## Referências" in system_prompt
    assert "capítulos vizinhos" not in system_prompt
    assert "Contexto: capítulo" not in user_prompt


def test_should_ignore_corrupted_book_metadata_and_use_article_template(tmp_raw_wiki):
    raw, wiki = tmp_raw_wiki
    book_dir = raw / "books" / "corrompido"
    book_dir.mkdir(parents=True)
    raw_file = book_dir / "01-cap.md"
    raw_file.write_text("# Capítulo\nConteúdo")
    (book_dir / "metadata.json").write_text("{invalid", encoding="utf-8")

    with patch("kb.compile.chat", return_value=VALID_RESPONSE) as mock_chat:
        compile_to_artifact(raw_file)

    messages = mock_chat.call_args.kwargs["messages"]
    system_prompt = messages[0]["content"]
    user_prompt = messages[1]["content"]
    assert "## Referências" in system_prompt
    assert "capítulos vizinhos" not in system_prompt
    assert "Contexto: capítulo" not in user_prompt


def test_should_use_article_template_when_book_metadata_does_not_list_chapter(
    tmp_raw_wiki,
):
    raw, wiki = tmp_raw_wiki
    book_dir = raw / "books" / "parcial"
    book_dir.mkdir(parents=True)
    raw_file = book_dir / "02-cap.md"
    raw_file.write_text("# Capítulo\nConteúdo")
    metadata = {
        "book_title": "Livro Parcial",
        "book_author": "Autora",
        "chapter_count": 1,
        "chapters": [
            {
                "index": 1,
                "title": "Outro Capítulo",
                "file": "01-cap.md",
                "source_href": "chapter-1.xhtml",
            }
        ],
    }
    (book_dir / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False), encoding="utf-8"
    )

    with patch("kb.compile.chat", return_value=VALID_RESPONSE) as mock_chat:
        compile_to_artifact(raw_file)

    messages = mock_chat.call_args.kwargs["messages"]
    system_prompt = messages[0]["content"]
    user_prompt = messages[1]["content"]
    assert "## Referências" in system_prompt
    assert "capítulos vizinhos" not in system_prompt
    assert "Contexto: capítulo" not in user_prompt
