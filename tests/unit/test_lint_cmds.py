from unittest.mock import patch

from typer.testing import CliRunner

from kb.cli import app
from kb.guardrails import SensitiveContentError, SensitiveFinding

runner = CliRunner()


def test_cli_lint_should_render_markdown_report():
    with (
        patch("kb.cli.console.print") as mock_print,
        patch("kb.lint.lint_wiki") as mock_lint,
    ):
        mock_lint.return_value = "## Report\n- ok"
        result = runner.invoke(app, ["lint"])

    assert result.exit_code == 0
    mock_lint.assert_called_once_with(allow_sensitive=False)
    assert mock_print.called


def test_cli_lint_should_handle_sensitive_error_and_retry_when_confirmed():
    exc = SensitiveContentError(
        findings=[SensitiveFinding(label="secret", sample="toke…oken")],
        source="lint:wiki",
    )

    with (
        patch("kb.cli.console.print") as mock_print,
        patch("kb.lint.lint_wiki") as mock_lint,
        patch("kb.cli.typer.confirm") as mock_confirm,
    ):
        mock_lint.side_effect = [exc, "## Report after retry"]
        mock_confirm.return_value = True

        result = runner.invoke(app, ["lint"])

    assert result.exit_code == 0
    assert mock_lint.call_count == 2
    mock_lint.assert_any_call(allow_sensitive=False)
    mock_lint.assert_any_call(allow_sensitive=True)
    assert mock_print.called


def test_cli_lint_should_exit_when_sensitive_error_and_not_confirmed():
    exc = SensitiveContentError(
        findings=[SensitiveFinding(label="secret", sample="toke…oken")],
        source="lint:wiki",
    )

    with (
        patch("kb.cli.console.print") as mock_print,
        patch("kb.lint.lint_wiki") as mock_lint,
        patch("kb.cli.typer.confirm") as mock_confirm,
    ):
        mock_lint.side_effect = exc
        mock_confirm.return_value = False

        result = runner.invoke(app, ["lint"])

    assert result.exit_code == 1
    mock_lint.assert_called_once_with(allow_sensitive=False)
    assert mock_print.called
