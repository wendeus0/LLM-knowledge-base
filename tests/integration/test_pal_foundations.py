from unittest.mock import patch

from kb.compile import compile_file
from kb.guardrails import SensitiveContentError
from kb.jobs import run_job
from kb.state import load_knowledge, load_manifest


def test_should_compile_generate_summary_and_register_knowledge(tmp_raw_wiki):
    raw, wiki = tmp_raw_wiki
    raw_file = raw / "xss.md"
    raw_file.write_text("# XSS\nVulnerabilidade web com detalhes relevantes.")

    mock_response = """---
title: XSS
topic: cybersecurity
tags: [xss]
source: xss.md
---

# XSS

XSS é uma vulnerabilidade web que permite injetar scripts em páginas.
"""

    with patch("kb.compile.chat") as mock_chat, patch("kb.compile.commit"):
        mock_chat.return_value = mock_response
        article = compile_file(raw_file)

    summary = wiki / "summaries" / article.name
    assert article.exists()
    assert summary.exists()
    assert "Summary — XSS" in summary.read_text(encoding="utf-8")

    manifest = load_manifest()
    knowledge = load_knowledge()
    assert any(entry["status"] == "compiled" for entry in manifest)
    assert any(entry["title"] == "XSS" for entry in knowledge)


def test_should_block_sensitive_compile_before_provider_call(tmp_raw_wiki):
    raw, wiki = tmp_raw_wiki
    raw_file = raw / "secrets.md"
    raw_file.write_text("api_key=abc1234567890")

    with patch("kb.compile.chat") as mock_chat:
        try:
            compile_file(raw_file)
        except SensitiveContentError:
            assert not mock_chat.called
        else:
            raise AssertionError("Expected SensitiveContentError")


def test_should_run_compile_job_end_to_end(tmp_raw_wiki):
    raw, wiki = tmp_raw_wiki
    raw_file = raw / "ml.md"
    raw_file.write_text("# Machine Learning\nAprendizado de máquina.")

    mock_response = """---
title: Machine Learning
topic: ai
---

# Machine Learning

Machine learning é um subcampo da IA.
"""

    with patch("kb.compile.chat") as mock_chat, patch("kb.compile.commit"):
        mock_chat.return_value = mock_response
        result = run_job("compile")

    assert "Job compile executado" in result
    assert (wiki / "ai" / "machine-learning.md").exists()
    assert (wiki / "_index.md").exists()
