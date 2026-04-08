from typer.testing import CliRunner
from unittest.mock import patch

from kb.cli import app

runner = CliRunner()


def test_compile_cli_should_default_to_no_commit(tmp_path):
    source = tmp_path / "doc.md"
    source.write_text("# Doc\nConteúdo seguro.")

    with (
        patch("kb.cli.Path.cwd", return_value=tmp_path),
        patch("kb.cli.console.print"),
        patch("kb.compile.discover_compile_targets") as mock_targets,
        patch("kb.compile.compile_file") as mock_compile,
        patch("kb.compile.update_index") as mock_update_index,
    ):
        mock_targets.return_value = [source]
        mock_compile.return_value = tmp_path / "wiki" / "doc.md"

        result = runner.invoke(app, ["compile", "--workers", "1"])

    assert result.exit_code == 0
    assert mock_compile.call_args.kwargs["no_commit"] is True
    assert mock_update_index.call_args.kwargs["no_commit"] is True


def test_compile_cli_should_support_explicit_commit_flag(tmp_path):
    source = tmp_path / "doc.md"
    source.write_text("# Doc\nConteúdo seguro.")

    with (
        patch("kb.cli.Path.cwd", return_value=tmp_path),
        patch("kb.cli.console.print"),
        patch("kb.compile.discover_compile_targets") as mock_targets,
        patch("kb.compile.compile_file") as mock_compile,
        patch("kb.compile.update_index") as mock_update_index,
    ):
        mock_targets.return_value = [source]
        mock_compile.return_value = tmp_path / "wiki" / "doc.md"

        result = runner.invoke(app, ["compile", "--workers", "1", "--commit"])

    assert result.exit_code == 0
    assert mock_compile.call_args.kwargs["no_commit"] is False
    assert mock_update_index.call_args.kwargs["no_commit"] is False


def test_compile_cli_should_route_parallel_mode_to_compile_many(tmp_path):
    source = tmp_path / "doc.md"
    source.write_text("# Doc\nConteúdo seguro.")

    fake_result = type(
        "CompileBatchResult",
        (),
        {"outputs": [tmp_path / "wiki" / "doc.md"], "failures": []},
    )()

    with (
        patch("kb.cli.Path.cwd", return_value=tmp_path),
        patch("kb.cli.console.print"),
        patch("kb.compile.discover_compile_targets") as mock_targets,
        patch("kb.compile.compile_many") as mock_compile_many,
    ):
        mock_targets.return_value = [source]
        mock_compile_many.return_value = fake_result

        result = runner.invoke(app, ["compile", "--workers", "4"])

    assert result.exit_code == 0
    assert mock_compile_many.call_args.kwargs["workers"] == 4
    assert mock_compile_many.call_args.kwargs["no_commit"] is True


def test_qa_cli_should_support_allow_sensitive_and_no_commit_for_file_back(tmp_path):
    with (
        patch("kb.cli.console.print"),
        patch("kb.qa.answer_and_file") as mock_answer_and_file,
    ):
        mock_answer_and_file.return_value = (
            "Resposta.",
            tmp_path / "wiki" / "saved.md",
        )

        result = runner.invoke(
            app, ["qa", "pergunta", "--file-back", "--allow-sensitive", "--no-commit"]
        )

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


def test_import_book_cli_should_handle_sensitive_compile_with_confirmation(tmp_path):
    source = tmp_path / "book.epub"
    source.write_text("stub")
    output_dir = tmp_path / "raw" / "books" / "book"
    chapter = output_dir / "01-intro.md"

    with (
        patch("kb.cli.typer.confirm", return_value=True),
        patch("kb.book_import.import_epub") as mock_import,
        patch("kb.compile.compile_file") as mock_compile,
        patch("kb.compile.update_index") as mock_update_index,
    ):
        mock_import.return_value = ([chapter], output_dir / "metadata.json")
        from kb.guardrails import SensitiveContentError, SensitiveFinding

        mock_compile.side_effect = [
            SensitiveContentError(
                [SensitiveFinding(label="secret", sample="[redacted]")],
                "compile:01-intro.md",
            ),
            tmp_path / "wiki" / "intro.md",
        ]

        result = runner.invoke(
            app,
            [
                "import-book",
                str(source),
                "--output",
                str(output_dir),
                "--compile",
                "--workers",
                "1",
            ],
        )

    assert result.exit_code == 0
    assert mock_compile.call_count == 2
    assert mock_compile.call_args.kwargs["allow_sensitive"] is True
    assert mock_update_index.called
