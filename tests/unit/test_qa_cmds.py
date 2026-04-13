from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from kb.cli import app
from kb.cmds.qa.run import execute_qa_command
from kb.guardrails import SensitiveContentError, SensitiveFinding

runner = CliRunner()


def test_execute_qa_command_should_call_answer_when_file_back_disabled():
    with patch("kb.qa.answer") as mock_answer:
        mock_answer.return_value = "Resposta"

        response, saved = execute_qa_command(
            question="Pergunta",
            file_back=False,
            to_wiki=False,
            allow_sensitive=False,
            no_commit=True,
            no_traverse=False,
            depth=1,
        )

    assert response == "Resposta"
    assert saved is None
    mock_answer.assert_called_once_with(
        "Pergunta", allow_sensitive=False, traverse=True, depth=1
    )


def test_execute_qa_command_should_call_answer_and_file_when_file_back_enabled():
    out = Path("/tmp/out.md")
    with patch("kb.qa.answer_and_file") as mock_file:
        mock_file.return_value = ("Resposta", out)

        response, saved = execute_qa_command(
            question="Pergunta",
            file_back=True,
            to_wiki=True,
            allow_sensitive=True,
            no_commit=True,
            no_traverse=True,
            depth=2,
        )

    assert response == "Resposta"
    assert saved == out
    mock_file.assert_called_once_with(
        "Pergunta",
        allow_sensitive=True,
        no_commit=True,
        to_wiki=True,
        traverse=False,
        depth=2,
    )


def test_cli_qa_should_render_markdown_from_cmd_layer():
    with (
        patch("kb.cli.console.print") as mock_print,
        patch("kb.cmds.qa.run.execute_qa_command") as mock_execute,
    ):
        mock_execute.return_value = ("# resposta", None)

        result = runner.invoke(app, ["qa", "pergunta teste", "--depth", "2"])

    assert result.exit_code == 0
    mock_execute.assert_called_once_with(
        question="pergunta teste",
        file_back=False,
        to_wiki=False,
        allow_sensitive=False,
        no_commit=True,
        no_traverse=False,
        depth=2,
    )
    assert mock_print.called


def test_cli_qa_should_retry_when_sensitive_confirmed():
    exc = SensitiveContentError(
        findings=[SensitiveFinding(label="secret", sample="[redacted]")],
        source="qa:test",
    )
    with (
        patch("kb.cli.console.print") as mock_print,
        patch("kb.cmds.qa.run.execute_qa_command") as mock_execute,
        patch("kb.cli.typer.confirm") as mock_confirm,
    ):
        mock_execute.side_effect = [exc, ("ok", None)]
        mock_confirm.return_value = True

        result = runner.invoke(app, ["qa", "pergunta"])

    assert result.exit_code == 0
    assert mock_execute.call_count == 2
    mock_execute.assert_any_call(
        question="pergunta",
        file_back=False,
        to_wiki=False,
        allow_sensitive=False,
        no_commit=True,
        no_traverse=False,
        depth=1,
    )
    mock_execute.assert_any_call(
        question="pergunta",
        file_back=False,
        to_wiki=False,
        allow_sensitive=True,
        no_commit=True,
        no_traverse=False,
        depth=1,
    )
    assert mock_print.called


def test_cli_qa_should_exit_when_sensitive_not_confirmed():
    exc = SensitiveContentError(
        findings=[SensitiveFinding(label="secret", sample="[redacted]")],
        source="qa:test",
    )
    with (
        patch("kb.cli.console.print") as mock_print,
        patch("kb.cmds.qa.run.execute_qa_command") as mock_execute,
        patch("kb.cli.typer.confirm") as mock_confirm,
    ):
        mock_execute.side_effect = exc
        mock_confirm.return_value = False

        result = runner.invoke(app, ["qa", "pergunta"])

    assert result.exit_code == 1
    mock_execute.assert_called_once()
    assert mock_print.called
