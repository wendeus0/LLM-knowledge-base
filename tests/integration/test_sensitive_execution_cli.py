from typer.testing import CliRunner
from unittest.mock import patch

from kb.cli import app

runner = CliRunner()


def test_compile_cli_should_support_no_commit_flag(tmp_path):
    source = tmp_path / "doc.md"
    source.write_text("# Doc\nConteúdo seguro.")

    with patch("kb.cli.Path.cwd", return_value=tmp_path), patch("kb.cli.console.print"), patch("kb.compile.discover_compile_targets") as mock_targets, patch(
        "kb.compile.compile_file"
    ) as mock_compile, patch("kb.compile.update_index") as mock_update_index:
        mock_targets.return_value = [source]
        mock_compile.return_value = tmp_path / "wiki" / "doc.md"

        result = runner.invoke(app, ["compile", "--no-commit"])

    assert result.exit_code == 0
    assert mock_compile.call_args.kwargs["no_commit"] is True
    assert mock_update_index.call_args.kwargs["no_commit"] is True


def test_qa_cli_should_support_allow_sensitive_and_no_commit_for_file_back(tmp_path):
    with patch("kb.cli.console.print"), patch("kb.qa.answer_and_file") as mock_answer_and_file:
        mock_answer_and_file.return_value = ("Resposta.", tmp_path / "wiki" / "saved.md")

        result = runner.invoke(app, ["qa", "pergunta", "--file-back", "--allow-sensitive", "--no-commit"])

    assert result.exit_code == 0
    assert mock_answer_and_file.call_args.kwargs["allow_sensitive"] is True
    assert mock_answer_and_file.call_args.kwargs["no_commit"] is True


def test_heal_cli_should_support_no_commit_and_allow_sensitive():
    with patch("kb.cli.console.print"), patch("kb.heal.heal") as mock_heal:
        mock_heal.return_value = [{"file": "a.md", "action": "healed"}]

        result = runner.invoke(app, ["heal", "--allow-sensitive", "--no-commit"])

    assert result.exit_code == 0
    assert mock_heal.call_args.kwargs["allow_sensitive"] is True
    assert mock_heal.call_args.kwargs["no_commit"] is True
