from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from kb.cli import app
from kb.cmds.compile.run import execute_compile_command

runner = CliRunner()


def test_execute_compile_command_should_resolve_targets_by_book_name(tmp_path):
    book_dir = tmp_path / "raw" / "books" / "my-book"
    book_dir.mkdir(parents=True)
    chapter = book_dir / "chapter.md"
    chapter.write_text("# Chapter")

    with (
        patch("kb.cmds.compile.run.find_book_dirs") as mock_find,
        patch("kb.cmds.compile.run.discover_compile_targets") as mock_targets,
        patch("kb.cmds.compile.run.compile_many") as mock_many,
    ):
        mock_find.return_value = [book_dir]
        mock_targets.return_value = [chapter]
        fake_result = type("CompileBatchResult", (), {"outputs": [chapter], "failures": []})()
        mock_many.return_value = fake_result

        result = execute_compile_command(
            target="my-book",
            update_index=True,
            workers=4,
            allow_sensitive=False,
            no_commit=True,
            interactive_sensitive=False,
        )

    assert result.targets == [chapter]
    assert result.book_dir_count == 1
    assert result.exit_code == 0


def test_execute_compile_command_should_resolve_relative_path_to_absolute(
    tmp_path, monkeypatch
):
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    source = raw_dir / "artigo.md"
    source.write_text("# Artigo")
    monkeypatch.chdir(tmp_path)

    with (
        patch("kb.cmds.compile.run.find_book_dirs") as mock_find,
        patch("kb.cmds.compile.run.compile_file") as mock_compile,
    ):
        mock_compile.return_value = tmp_path / "wiki" / "artigo.md"

        result = execute_compile_command(
            target="raw/artigo.md",
            update_index=False,
            workers=1,
            allow_sensitive=False,
            no_commit=True,
            interactive_sensitive=False,
        )

    assert result.exit_code == 0
    assert result.targets == [source.resolve()]
    assert result.targets[0].is_absolute()
    assert not mock_find.called


def test_execute_compile_command_should_report_missing_file_for_path_like_target(
    tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)

    with patch("kb.cmds.compile.run.find_book_dirs") as mock_find:
        result = execute_compile_command(
            target="raw/inexistente.md",
            update_index=False,
            workers=1,
            allow_sensitive=False,
            no_commit=True,
            interactive_sensitive=False,
        )

    assert result.exit_code == 1
    assert not mock_find.called
    assert result.message_lines == [
        "[red]Arquivo não encontrado:[/] raw/inexistente.md"
    ]


def test_execute_compile_command_should_still_treat_plain_name_as_book(tmp_path):
    with patch("kb.cmds.compile.run.find_book_dirs") as mock_find:
        mock_find.return_value = []

        result = execute_compile_command(
            target="Build a Large Language Model",
            update_index=False,
            workers=1,
            allow_sensitive=False,
            no_commit=True,
            interactive_sensitive=False,
        )

    assert result.exit_code == 1
    mock_find.assert_called_once_with("Build a Large Language Model")
    assert result.message_lines == [
        "[red]Nenhum livro encontrado para:[/] Build a Large Language Model"
    ]


def test_cli_compile_should_route_through_cmd_layer():
    fake_out = Path("/tmp/wiki/out.md")
    fake_result = type(
        "CompileExecutionResult",
        (),
        {
            "exit_code": 0,
            "message_lines": ["[dim]ok[/]"],
            "compiled_outputs": [fake_out],
            "failures": [],
        },
    )()

    with (
        patch("kb.cli.console.print") as mock_print,
        patch("kb.cmds.compile.run.execute_compile_command") as mock_execute,
    ):
        mock_execute.return_value = fake_result
        result = runner.invoke(app, ["compile", "--workers", "1"])

    assert result.exit_code == 0
    assert mock_execute.call_count == 1
    kwargs = mock_execute.call_args.kwargs
    assert kwargs["target"] is None
    assert kwargs["update_index"] is True
    assert kwargs["workers"] == 1
    assert kwargs["allow_sensitive"] is False
    assert kwargs["no_commit"] is True
    assert kwargs["interactive_sensitive"] is True
    assert callable(kwargs["confirm_sensitive"])
    assert mock_print.called
