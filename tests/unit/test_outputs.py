"""Testes RED para kb/outputs.py — store separado de respostas de QA.

Rastreabilidade SPEC:
  REQ-1: outputs/ criado automaticamente se não existir
  REQ-4: naming outputs/<topic>/<YYYY-MM-DD>-<slug>.md
  REQ-5: frontmatter com title, source_question, date, topic
"""

import re
from datetime import date
from unittest.mock import patch

# RED: falha até outputs-store ser implementada
from kb.outputs import write_output  # noqa: E402 — módulo não existe ainda


class TestWriteOutput:
    """Testa kb.outputs.write_output(question, answer, topic)."""

    def test_should_create_outputs_dir_when_it_does_not_exist(
        self, tmp_path, monkeypatch
    ):
        """REQ-1: outputs/ deve ser criado automaticamente na primeira escrita."""
        # RED: falha até outputs-store ser implementada
        outputs_dir = tmp_path / "outputs"
        assert not outputs_dir.exists()

        monkeypatch.setattr("kb.config.OUTPUTS_DIR", outputs_dir)

        with patch("kb.outputs.commit"):
            write_output("O que é XSS?", "XSS é uma vulnerabilidade.", "cybersecurity")

        assert outputs_dir.exists()

    def test_should_generate_correct_file_path_with_date_and_slug(
        self, tmp_path, monkeypatch
    ):
        """REQ-4: arquivo deve seguir padrão outputs/<topic>/<YYYY-MM-DD>-<slug>.md."""
        # RED: falha até outputs-store ser implementada
        outputs_dir = tmp_path / "outputs"
        monkeypatch.setattr("kb.config.OUTPUTS_DIR", outputs_dir)

        with patch("kb.outputs.commit"):
            _, out_path = write_output("O que é XSS?", "Resposta.", "cybersecurity")

        today = date.today().isoformat()
        assert out_path.parent == outputs_dir / "cybersecurity"
        assert out_path.name.startswith(today)
        assert out_path.suffix == ".md"

    def test_should_sanitize_question_into_valid_slug(self, tmp_path, monkeypatch):
        """REQ-4b: slug gerado a partir da pergunta deve conter apenas chars válidos."""
        # RED: falha até outputs-store ser implementada
        outputs_dir = tmp_path / "outputs"
        monkeypatch.setattr("kb.config.OUTPUTS_DIR", outputs_dir)

        with patch("kb.outputs.commit"):
            _, out_path = write_output(
                "Qual é a diferença entre XSS e CSRF? (segurança)",
                "Resposta.",
                "cybersecurity",
            )

        slug_part = out_path.stem.split("-", 3)[-1]  # remove YYYY-MM-DD prefix
        assert re.match(r"^[a-z0-9-]+$", slug_part), f"slug inválido: {slug_part}"

    def test_should_include_required_frontmatter_fields_in_output(
        self, tmp_path, monkeypatch
    ):
        """REQ-5: arquivo deve ter frontmatter com title, source_question, date, topic."""
        # RED: falha até outputs-store ser implementada
        outputs_dir = tmp_path / "outputs"
        monkeypatch.setattr("kb.config.OUTPUTS_DIR", outputs_dir)

        question = "O que é SQL injection?"
        with patch("kb.outputs.commit"):
            _, out_path = write_output(question, "SQL injection é...", "cybersecurity")

        content = out_path.read_text(encoding="utf-8")
        assert "title:" in content
        assert "source_question:" in content
        assert "date:" in content
        assert "topic:" in content
        assert question in content
