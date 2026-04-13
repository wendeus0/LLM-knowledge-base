from typer.testing import CliRunner

from kb.cli import app

runner = CliRunner()


def test_handoff_create_should_generate_file_and_print_path(monkeypatch, tmp_path):
    monkeypatch.setattr("kb.handoff.DATA_DIR", tmp_path)

    result = runner.invoke(
        app,
        [
            "handoff",
            "create",
            "--scope",
            "sessao de teste",
            "--summary",
            "resumo ok",
            "--next-steps",
            "continuar",
            "--evidence",
            "pytest -q",
            "--decisions",
            "adotar gate",
        ],
    )

    assert result.exit_code == 0
    assert "Handoff criado:" in result.stdout

    handoff_dir = tmp_path / "docs" / "handoffs"
    files = list(handoff_dir.glob("*.md"))
    assert len(files) == 1
    content = files[0].read_text(encoding="utf-8")
    assert "sessao de teste" in content
    assert "resumo ok" in content
