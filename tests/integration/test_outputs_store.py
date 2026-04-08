"""Testes RED de integração para outputs-store — comportamento de qa.answer_and_file.

Rastreabilidade SPEC:
  REQ-2: kb qa -f grava em outputs/ por padrão
  REQ-3: kb qa -f --to-wiki grava em wiki/
  REQ-6: git commit automático após write em outputs/
  REQ-7: --no-commit suprime o commit
"""

from unittest.mock import patch

from kb.qa import answer_and_file

MOCK_ANSWER = "Resposta gerada pelo LLM."
MOCK_ARTICLE = """---
title: XSS Explicado
topic: cybersecurity
tags: [xss, segurança]
source: qa
---

# XSS Explicado

Conteúdo sobre XSS.
"""


class TestAnswerAndFileOutputsStore:
    """Testa o comportamento de file-back com o novo store outputs/."""

    def test_should_write_to_outputs_dir_by_default_when_file_back_is_true(
        self, tmp_raw_wiki, tmp_path, monkeypatch
    ):
        """REQ-2: answer_and_file sem --to-wiki deve gravar em outputs/, não em wiki/."""
        # RED: falha até outputs-store ser implementada
        raw, wiki = tmp_raw_wiki
        outputs_dir = tmp_path / "outputs"
        monkeypatch.setattr("kb.config.OUTPUTS_DIR", outputs_dir)

        (wiki / "cybersecurity" / "xss.md").write_text("# XSS\nVulnerabilidade web.")

        with patch("kb.qa.chat") as mock_chat, patch("kb.qa.commit"):
            mock_chat.side_effect = [MOCK_ANSWER, MOCK_ARTICLE]
            _, out_path = answer_and_file("O que é XSS?", allow_sensitive=True)

        assert out_path is not None
        assert "outputs" in str(out_path), f"esperado outputs/, obtido: {out_path}"
        assert "wiki" not in str(out_path), f"não deveria escrever em wiki/: {out_path}"

    def test_should_write_to_wiki_dir_when_to_wiki_flag_is_set(
        self, tmp_raw_wiki, tmp_path, monkeypatch
    ):
        """REQ-3: answer_and_file com to_wiki=True deve gravar em wiki/ (comportamento anterior)."""
        # RED: falha até outputs-store ser implementada
        raw, wiki = tmp_raw_wiki
        outputs_dir = tmp_path / "outputs"
        monkeypatch.setattr("kb.config.OUTPUTS_DIR", outputs_dir)

        (wiki / "cybersecurity" / "xss.md").write_text("# XSS\nVulnerabilidade web.")

        with patch("kb.qa.chat") as mock_chat, patch("kb.qa.commit"):
            mock_chat.side_effect = [MOCK_ANSWER, MOCK_ARTICLE]
            _, out_path = answer_and_file(
                "O que é XSS?", allow_sensitive=True, to_wiki=True
            )

        assert out_path is not None
        assert str(wiki) in str(out_path), f"esperado wiki/, obtido: {out_path}"

    def test_should_commit_output_file_automatically(
        self, tmp_raw_wiki, tmp_path, monkeypatch
    ):
        """REQ-6: commit automático deve ocorrer após write em outputs/."""
        # RED: falha até outputs-store ser implementada
        raw, wiki = tmp_raw_wiki
        outputs_dir = tmp_path / "outputs"
        monkeypatch.setattr("kb.config.OUTPUTS_DIR", outputs_dir)

        (wiki / "ai" / "llm.md").write_text("# LLM\nModelos de linguagem.")

        with patch("kb.qa.chat") as mock_chat, patch("kb.qa.commit") as mock_commit:
            mock_chat.side_effect = [MOCK_ANSWER, MOCK_ARTICLE]
            answer_and_file("O que é um LLM?", allow_sensitive=True)

        assert mock_commit.called, "commit deveria ser chamado automaticamente"
        committed_path = mock_commit.call_args[0][1][0]
        assert "outputs" in str(committed_path)

    def test_should_suppress_commit_when_no_commit_is_true(
        self, tmp_raw_wiki, tmp_path, monkeypatch
    ):
        """REQ-7: no_commit=True deve suprimir o commit automático."""
        # RED: falha até outputs-store ser implementada
        raw, wiki = tmp_raw_wiki
        outputs_dir = tmp_path / "outputs"
        monkeypatch.setattr("kb.config.OUTPUTS_DIR", outputs_dir)

        (wiki / "ai" / "llm.md").write_text("# LLM\nModelos de linguagem.")

        with patch("kb.qa.chat") as mock_chat, patch("kb.qa.commit") as mock_commit:
            mock_chat.side_effect = [MOCK_ANSWER, MOCK_ARTICLE]
            answer_and_file("O que é um LLM?", allow_sensitive=True, no_commit=True)

        assert (
            not mock_commit.called
        ), "commit não deveria ser chamado quando no_commit=True"
