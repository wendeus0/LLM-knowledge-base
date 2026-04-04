from pathlib import Path
from unittest.mock import patch

from kb.compile import compile_file, update_index
from kb.guardrails import SensitiveContentError
from kb.heal import heal
from kb.qa import answer, answer_and_file


def test_compile_file_should_skip_commit_when_no_commit_is_enabled(tmp_raw_wiki):
    raw, wiki = tmp_raw_wiki
    raw_file = raw / "safe.md"
    raw_file.write_text("# Safe\nConteúdo seguro.")

    mock_response = """---
title: Safe
topic: ai
---

# Safe

Conteúdo compilado.
"""

    with patch("kb.compile.chat") as mock_chat, patch("kb.compile.commit") as mock_commit:
        mock_chat.return_value = mock_response

        result = compile_file(raw_file, no_commit=True)

        assert result.exists()
        mock_commit.assert_not_called()


def test_update_index_should_skip_commit_when_no_commit_is_enabled(tmp_raw_wiki):
    raw, wiki = tmp_raw_wiki
    (wiki / "ai" / "article.md").write_text("# Article")

    with patch("kb.compile.commit") as mock_commit:
        update_index(no_commit=True)

        assert (wiki / "_index.md").exists()
        mock_commit.assert_not_called()


def test_answer_should_allow_sensitive_when_explicit_flag_is_enabled(tmp_raw_wiki):
    raw, wiki = tmp_raw_wiki
    (wiki / "python" / "secret.md").write_text("# Secret\napi_key=abc1234567890")

    with patch("kb.qa.chat") as mock_chat:
        mock_chat.return_value = "Resposta controlada."

        result = answer("secret", allow_sensitive=True)

        assert result == "Resposta controlada."
        assert mock_chat.called


def test_answer_and_file_should_skip_commit_when_no_commit_is_enabled(tmp_raw_wiki):
    raw, wiki = tmp_raw_wiki
    (wiki / "ai" / "base.md").write_text("# Base\nConteúdo base.")

    with patch("kb.qa.chat") as mock_chat, patch("kb.qa.commit") as mock_commit:
        mock_chat.side_effect = ["Resposta breve.", """---
title: Filed Answer
topic: ai
---

# Filed Answer

Resposta arquivada.
"""]

        response, saved = answer_and_file("base", allow_sensitive=True, no_commit=True)

        assert response == "Resposta breve."
        assert isinstance(saved, Path)
        assert saved.exists()
        mock_commit.assert_not_called()


def test_heal_should_skip_commit_when_no_commit_is_enabled(tmp_raw_wiki):
    raw, wiki = tmp_raw_wiki
    article = wiki / "ai" / "test.md"
    article.write_text("""---
title: Test
---

# Test

Conteúdo substantivo para healing.
""")

    with patch("kb.heal.chat") as mock_chat, patch("kb.heal.commit") as mock_commit, patch("random.sample") as mock_sample:
        mock_chat.return_value = "Conteúdo ajustado."
        mock_sample.return_value = [article]

        log = heal(n=1, allow_sensitive=True, no_commit=True)

        assert log
        mock_commit.assert_not_called()
