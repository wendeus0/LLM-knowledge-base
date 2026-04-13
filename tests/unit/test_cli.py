from unittest.mock import Mock, patch

from typer.testing import CliRunner

from kb.cli import app

runner = CliRunner()


class TestIngestCommand:
    def test_should_ingest_local_file_without_commit_by_default(self, tmp_path):
        source = tmp_path / "source.md"
        source.write_text("# Content")

        with (
            patch("kb.config.RAW_DIR", tmp_path),
            patch("kb.cli.console.print") as mock_print,
            patch("kb.state.record_ingest") as mock_record,
            patch("kb.git.commit") as mock_commit,
        ):
            result = runner.invoke(app, ["ingest", str(source)])

        assert result.exit_code == 0
        assert (tmp_path / "source.md").exists()
        mock_record.assert_called_once()
        mock_commit.assert_not_called()
        # Check that the print call was made with the expected message format
        # (uses single f-string argument)
        adicionado_calls = [
            call
            for call in mock_print.call_args_list
            if call.args
            and "[green]Adicionado:[/]" in str(call.args[0])
            and "source.md" in str(call.args[0])
        ]
        assert (
            len(adicionado_calls) == 1
        ), f"Expected one 'Adicionado' call with source.md, got: {mock_print.call_args_list}"

    def test_should_ingest_with_explicit_commit_flag(self, tmp_path):
        source = tmp_path / "source.md"
        source.write_text("# Content")

        with (
            patch("kb.config.RAW_DIR", tmp_path),
            patch("kb.cli.console.print"),
            patch("kb.state.record_ingest"),
            patch("kb.git.commit") as mock_commit,
        ):
            result = runner.invoke(app, ["ingest", str(source), "--commit"])

        assert result.exit_code == 0
        mock_commit.assert_called_once()

    def test_should_ingest_url(self, tmp_path):
        with (
            patch("kb.config.RAW_DIR", tmp_path),
            patch("kb.cli.console.print") as mock_print,
            patch("kb.state.record_ingest") as mock_record,
            patch("kb.web_ingest.ingest_url") as mock_ingest,
        ):
            mock_ingest.return_value = tmp_path / "article.md"

            result = runner.invoke(app, ["ingest", "https://example.com/article"])

        assert result.exit_code == 0
        mock_ingest.assert_called_once()
        mock_record.assert_called_once()
        mock_print.assert_any_call("[dim]Baixando https://example.com/article...[/]")

    def test_should_handle_web_ingest_error(self, tmp_path):
        from kb.web_ingest import WebIngestError

        with (
            patch("kb.config.RAW_DIR", tmp_path),
            patch("kb.cli.console.print"),
            patch("kb.web_ingest.ingest_url") as mock_ingest,
        ):
            mock_ingest.side_effect = WebIngestError("Connection failed")

            result = runner.invoke(app, ["ingest", "https://example.com/bad"])

        assert result.exit_code == 1

    def test_should_compile_after_ingest_when_compile_flag(self, tmp_path):
        source = tmp_path / "source.md"
        source.write_text("# Content")

        with (
            patch("kb.config.RAW_DIR", tmp_path),
            patch("kb.cli.console.print"),
            patch("kb.state.record_ingest"),
            patch("kb.git.commit"),
            patch("kb.compile.compile_file") as mock_compile,
            patch("kb.compile.update_index") as mock_update,
        ):
            mock_compile.return_value = tmp_path / "wiki" / "source.md"

            result = runner.invoke(app, ["ingest", str(source), "--compile"])

        assert result.exit_code == 0
        mock_compile.assert_called_once()
        mock_update.assert_called_once()
        assert mock_compile.call_args.kwargs["no_commit"] is True
        assert mock_update.call_args.kwargs["no_commit"] is True


class TestSearchCommand:
    def test_should_search_and_display_results(self, tmp_path):
        with (
            patch("kb.cli.console.print") as mock_print,
            patch("kb.cmds.search.run.execute_search_command") as mock_execute,
        ):
            mock_execute.return_value = [
                f"[bold]article[/] [dim]({tmp_path / 'wiki' / 'article.md'})[/] score=10",
                "  [dim]This is a snippet of the content...[/]",
            ]

            result = runner.invoke(app, ["search", "query"])

        assert result.exit_code == 0
        mock_execute.assert_called_once_with("query")
        mock_print.assert_any_call(
            f"[bold]article[/] [dim]({tmp_path / 'wiki' / 'article.md'})[/] score=10"
        )

    def test_should_exit_when_no_results(self):
        with (
            patch("kb.cli.console.print") as mock_print,
            patch("kb.cmds.search.run.execute_search_command") as mock_execute,
        ):
            mock_execute.return_value = ["[yellow]Nenhum resultado encontrado.[/]"]

            result = runner.invoke(app, ["search", "unknown"])

        assert result.exit_code == 0  # typer.Exit() without code = 0
        mock_print.assert_any_call("[yellow]Nenhum resultado encontrado.[/]")


class TestJobsCommand:
    def test_should_list_available_jobs(self):
        with (
            patch("kb.cli.console.print") as mock_print,
            patch("kb.jobs.list_jobs") as mock_list,
        ):
            mock_job = Mock()
            mock_job.name = "compile"
            mock_job.schedule = "0 9 * * *"
            mock_job.description = "Compile raw files"
            mock_list.return_value = [mock_job]

            result = runner.invoke(app, ["jobs", "list"])

        assert result.exit_code == 0
        mock_list.assert_called_once()
        mock_print.assert_any_call(
            "[bold]compile[/] [dim](0 9 * * *)[/] — Compile raw files"
        )

    def test_should_run_job_by_name(self):
        with (
            patch("kb.cli.console.print") as mock_print,
            patch("kb.jobs.run_job") as mock_run,
        ):
            mock_run.return_value = "Job completed"

            result = runner.invoke(app, ["jobs", "run", "compile"])

        assert result.exit_code == 0
        mock_run.assert_called_once_with(
            "compile", stale_max_pct=None, disputed_max_pct=None
        )
        mock_print.assert_called_once_with("Job completed")


class TestCompileCommand:
    def test_should_exit_when_no_targets_found(self, tmp_path):
        with (
            patch("kb.cli.console.print") as mock_print,
            patch("kb.cmds.compile.run.discover_compile_targets") as mock_targets,
        ):
            mock_targets.return_value = []

            result = runner.invoke(app, ["compile", "--workers", "1"])

        assert result.exit_code == 0
        mock_print.assert_any_call("[yellow]Nenhum arquivo em raw/[/]")

    def test_should_exit_with_error_when_book_not_found(self):
        with (
            patch("kb.cli.console.print") as mock_print,
            patch("kb.cmds.compile.run.find_book_dirs") as mock_find,
        ):
            mock_find.return_value = []

            result = runner.invoke(app, ["compile", "NonExistentBook"])

        assert result.exit_code == 1
        mock_print.assert_any_call(
            "[red]Nenhum livro encontrado para:[/] NonExistentBook"
        )

    def test_should_compile_book_by_name(self, tmp_path):
        book_dir = tmp_path / "raw" / "books" / "mybook"
        book_dir.mkdir(parents=True)
        chapter = book_dir / "chapter.md"
        chapter.write_text("# Chapter")

        with (
            patch("kb.cli.Path.cwd", return_value=tmp_path),
            patch("kb.cli.console.print"),
            patch("kb.cmds.compile.run.find_book_dirs") as mock_find,
            patch("kb.cmds.compile.run.discover_compile_targets") as mock_targets,
            patch("kb.cmds.compile.run.compile_many") as mock_compile,
        ):
            mock_find.return_value = [book_dir]
            mock_targets.return_value = [chapter]

            fake_result = type(
                "CompileBatchResult",
                (),
                {"outputs": [tmp_path / "wiki" / "chapter.md"], "failures": []},
            )()
            mock_compile.return_value = fake_result

            result = runner.invoke(app, ["compile", "mybook", "--workers", "4"])

        assert result.exit_code == 0
        mock_find.assert_called_once_with("mybook")

    def test_should_report_failures_after_compile(self, tmp_path):
        source = tmp_path / "doc.md"
        source.write_text("# Doc")

        with (
            patch("kb.cli.Path.cwd", return_value=tmp_path),
            patch("kb.cli.console.print") as mock_print,
            patch("kb.cmds.compile.run.discover_compile_targets") as mock_targets,
            patch("kb.cmds.compile.run.compile_many") as mock_compile,
        ):
            mock_targets.return_value = [source]

            fake_failure = type(
                "CompileFailure",
                (),
                {"raw_path": source, "error": Exception("Parse error")},
            )()
            fake_result = type(
                "CompileBatchResult",
                (),
                {"outputs": [], "failures": [fake_failure]},
            )()
            mock_compile.return_value = fake_result

            result = runner.invoke(app, ["compile", "--workers", "4"])

        assert result.exit_code == 1
        mock_print.assert_any_call("\n[bold red]Falhas: 1/1[/]")

    def test_should_handle_sensitive_content_error_with_confirmation(self, tmp_path):
        from kb.guardrails import SensitiveContentError, SensitiveFinding

        source = tmp_path / "doc.md"
        source.write_text("# Doc")

        with (
            patch("kb.cli.Path.cwd", return_value=tmp_path),
            patch("kb.cli.console.print"),
            patch("kb.cli.typer.confirm") as mock_confirm,
            patch("kb.cmds.compile.run.discover_compile_targets") as mock_targets,
            patch("kb.cmds.compile.run.compile_file") as mock_compile,
            patch("kb.compile.update_index"),
        ):
            mock_targets.return_value = [source]
            mock_compile.side_effect = [
                SensitiveContentError(
                    [SensitiveFinding(label="secret", sample="[redacted]")],
                    "compile",
                ),
                tmp_path / "wiki" / "doc.md",
            ]
            mock_confirm.return_value = True

            result = runner.invoke(app, ["compile", "--workers", "1"])

        assert result.exit_code == 0
        assert mock_compile.call_count == 2

    def test_should_exit_when_sensitive_rejected(self, tmp_path):
        from kb.guardrails import SensitiveContentError, SensitiveFinding

        source = tmp_path / "doc.md"
        source.write_text("# Doc")

        with (
            patch("kb.cli.Path.cwd", return_value=tmp_path),
            patch("kb.cli.console.print"),
            patch("kb.cli.typer.confirm") as mock_confirm,
            patch("kb.cmds.compile.run.discover_compile_targets") as mock_targets,
            patch("kb.cmds.compile.run.compile_file") as mock_compile,
        ):
            mock_targets.return_value = [source]
            mock_compile.side_effect = SensitiveContentError(
                [SensitiveFinding(label="secret", sample="[redacted]")],
                "compile",
            )
            mock_confirm.return_value = False

            result = runner.invoke(app, ["compile", "--workers", "1"])

        assert result.exit_code == 1


class TestLintCommand:
    def test_should_run_lint_and_display_results(self):
        with (
            patch("kb.cli.console.print"),
            patch("kb.lint.lint_wiki") as mock_lint,
        ):
            mock_lint.return_value = "# Lint Report\n- 3 issues found"

            result = runner.invoke(app, ["lint"])

        assert result.exit_code == 0
        mock_lint.assert_called_once_with(allow_sensitive=False)

    def test_should_support_allow_sensitive_flag(self):
        with (
            patch("kb.cli.console.print"),
            patch("kb.lint.lint_wiki") as mock_lint,
        ):
            mock_lint.return_value = "# Lint Report"

            result = runner.invoke(app, ["lint", "--allow-sensitive"])

        assert result.exit_code == 0
        mock_lint.assert_called_once_with(allow_sensitive=True)

    def test_should_handle_sensitive_content_error_with_confirmation(self):
        from kb.guardrails import SensitiveContentError, SensitiveFinding

        with (
            patch("kb.cli.console.print"),
            patch("kb.lint.lint_wiki") as mock_lint,
            patch("kb.cli.typer.confirm") as mock_confirm,
        ):
            mock_lint.side_effect = [
                SensitiveContentError(
                    [SensitiveFinding(label="secret", sample="[redacted]")],
                    "lint",
                ),
                "# Lint Report After Confirmation",
            ]
            mock_confirm.return_value = True

            result = runner.invoke(app, ["lint"])

        assert result.exit_code == 0
        assert mock_lint.call_count == 2

    def test_should_exit_when_sensitive_rejected(self):
        from kb.guardrails import SensitiveContentError, SensitiveFinding

        with (
            patch("kb.cli.console.print"),
            patch("kb.lint.lint_wiki") as mock_lint,
            patch("kb.cli.typer.confirm") as mock_confirm,
        ):
            mock_lint.side_effect = SensitiveContentError(
                [SensitiveFinding(label="secret", sample="[redacted]")],
                "lint",
            )
            mock_confirm.return_value = False

            result = runner.invoke(app, ["lint"])

        assert result.exit_code == 1


class TestHealCommand:
    def test_should_run_heal_with_default_n(self):
        with (
            patch("kb.cli.console.print") as mock_print,
            patch("kb.heal.heal") as mock_heal,
        ):
            mock_heal.return_value = [
                {"file": "a.md", "action": "healed"},
                {"file": "b.md", "action": "reviewed_no_changes"},
            ]

            result = runner.invoke(app, ["heal"])

        assert result.exit_code == 0
        mock_heal.assert_called_once_with(10, allow_sensitive=False, no_commit=True)
        mock_print.assert_any_call("  [green]✓[/] a.md [dim](healed)[/]")
        mock_print.assert_any_call("  [dim]·[/] b.md [dim](reviewed_no_changes)[/]")

    def test_should_exit_when_wiki_empty(self):
        with (
            patch("kb.cli.console.print") as mock_print,
            patch("kb.heal.heal") as mock_heal,
        ):
            mock_heal.return_value = []

            result = runner.invoke(app, ["heal"])

        assert result.exit_code == 0
        mock_print.assert_any_call("[yellow]Wiki vazia.[/]")

    def test_should_use_custom_n_value(self):
        with (
            patch("kb.cli.console.print"),
            patch("kb.heal.heal") as mock_heal,
        ):
            mock_heal.return_value = [{"file": "a.md", "action": "healed"}]

            result = runner.invoke(app, ["heal", "--n", "5"])

        assert result.exit_code == 0
        mock_heal.assert_called_once_with(5, allow_sensitive=False, no_commit=True)

    def test_should_support_explicit_commit_flag(self):
        with (
            patch("kb.cli.console.print"),
            patch("kb.heal.heal") as mock_heal,
        ):
            mock_heal.return_value = [{"file": "a.md", "action": "healed"}]

            result = runner.invoke(app, ["heal", "--commit"])

        assert result.exit_code == 0
        mock_heal.assert_called_once_with(10, allow_sensitive=False, no_commit=False)

    def test_should_handle_sensitive_content_error_with_confirmation(self):
        from kb.guardrails import SensitiveContentError, SensitiveFinding

        with (
            patch("kb.cli.console.print"),
            patch("kb.heal.heal") as mock_heal,
            patch("kb.cli.typer.confirm") as mock_confirm,
        ):
            mock_heal.side_effect = [
                SensitiveContentError(
                    [SensitiveFinding(label="secret", sample="[redacted]")],
                    "heal",
                ),
                [{"file": "a.md", "action": "healed"}],
            ]
            mock_confirm.return_value = True

            result = runner.invoke(app, ["heal"])

        assert result.exit_code == 0
        assert mock_heal.call_count == 2

    def test_should_exit_when_sensitive_rejected(self):
        from kb.guardrails import SensitiveContentError, SensitiveFinding

        with (
            patch("kb.cli.console.print"),
            patch("kb.heal.heal") as mock_heal,
            patch("kb.cli.typer.confirm") as mock_confirm,
        ):
            mock_heal.side_effect = SensitiveContentError(
                [SensitiveFinding(label="secret", sample="[redacted]")],
                "heal",
            )
            mock_confirm.return_value = False

            result = runner.invoke(app, ["heal"])

        assert result.exit_code == 1


class TestQaCommand:
    def test_should_answer_without_file_back(self):
        with (
            patch("kb.cli.console.print"),
            patch("kb.cmds.qa.run.execute_qa_command") as mock_answer,
        ):
            mock_answer.return_value = ("This is the answer", None)

            result = runner.invoke(app, ["qa", "What is AI?"])

        assert result.exit_code == 0
        mock_answer.assert_called_once_with(
            question="What is AI?",
            file_back=False,
            to_wiki=False,
            allow_sensitive=False,
            no_commit=True,
            no_traverse=False,
            depth=1,
        )

    def test_should_handle_sensitive_content_error_with_confirmation(self):
        from kb.guardrails import SensitiveContentError, SensitiveFinding

        with (
            patch("kb.cli.console.print"),
            patch("kb.cmds.qa.run.execute_qa_command") as mock_answer,
            patch("kb.cli.typer.confirm") as mock_confirm,
        ):
            mock_answer.side_effect = [
                SensitiveContentError(
                    [SensitiveFinding(label="secret", sample="[redacted]")],
                    "qa",
                ),
                ("Answer after confirmation", None),
            ]
            mock_confirm.return_value = True

            result = runner.invoke(app, ["qa", "Question?"])

        assert result.exit_code == 0
        assert mock_answer.call_count == 2
        # Second call should have allow_sensitive=True
        assert mock_answer.call_args_list[1].kwargs["allow_sensitive"] is True
        assert mock_answer.call_args_list[1].kwargs["question"] == "Question?"

    def test_should_exit_when_sensitive_rejected(self):
        from kb.guardrails import SensitiveContentError, SensitiveFinding

        with (
            patch("kb.cli.console.print"),
            patch("kb.cmds.qa.run.execute_qa_command") as mock_answer,
            patch("kb.cli.typer.confirm") as mock_confirm,
        ):
            mock_answer.side_effect = SensitiveContentError(
                [SensitiveFinding(label="secret", sample="[redacted]")],
                "qa",
            )
            mock_confirm.return_value = False

            result = runner.invoke(app, ["qa", "Question?"])

        assert result.exit_code == 1

    def test_should_file_back_answer(self, tmp_path):
        with (
            patch("kb.cli.console.print") as mock_print,
            patch("kb.cmds.qa.run.execute_qa_command") as mock_answer_and_file,
        ):
            mock_answer_and_file.return_value = ("Answer text", tmp_path / "output.md")

            result = runner.invoke(
                app, ["qa", "Question?", "--file-back", "--no-commit"]
            )

        assert result.exit_code == 0
        mock_answer_and_file.assert_called_once_with(
            question="Question?",
            file_back=True,
            to_wiki=False,
            allow_sensitive=False,
            no_commit=True,
            no_traverse=False,
            depth=1,
        )
        mock_print.assert_any_call(
            f"\n[dim]Arquivado em:[/] [green]{tmp_path / 'output.md'}[/]"
        )

    def test_should_support_no_traverse_option(self):
        with (
            patch("kb.cli.console.print"),
            patch("kb.cmds.qa.run.execute_qa_command") as mock_answer,
        ):
            mock_answer.return_value = ("Answer", None)

            result = runner.invoke(app, ["qa", "Question?", "--no-traverse"])

        assert result.exit_code == 0
        mock_answer.assert_called_once_with(
            question="Question?",
            file_back=False,
            to_wiki=False,
            allow_sensitive=False,
            no_commit=True,
            no_traverse=True,
            depth=1,
        )

    def test_should_support_custom_depth(self):
        with (
            patch("kb.cli.console.print"),
            patch("kb.cmds.qa.run.execute_qa_command") as mock_answer,
        ):
            mock_answer.return_value = ("Answer", None)

            result = runner.invoke(app, ["qa", "Question?", "--depth", "3"])

        assert result.exit_code == 0
        mock_answer.assert_called_once_with(
            question="Question?",
            file_back=False,
            to_wiki=False,
            allow_sensitive=False,
            no_commit=True,
            no_traverse=False,
            depth=3,
        )

    def test_should_support_to_wiki_flag(self):
        with (
            patch("kb.cli.console.print"),
            patch("kb.cmds.qa.run.execute_qa_command") as mock_answer,
        ):
            mock_answer.return_value = ("Answer", None)

            result = runner.invoke(app, ["qa", "Q?", "--file-back", "--to-wiki"])

        assert result.exit_code == 0
        call_kwargs = mock_answer.call_args.kwargs
        assert call_kwargs["question"] == "Q?"
        assert call_kwargs["file_back"] is True
        assert call_kwargs["to_wiki"] is True
        assert call_kwargs["no_traverse"] is False


class TestImportBookCommand:
    def test_should_skip_existing_import_when_no_force(self, tmp_path):
        book_path = tmp_path / "book.epub"
        book_path.write_text("content")
        output_dir = tmp_path / "raw" / "books" / "book"
        output_dir.mkdir(parents=True)
        (output_dir / "existing.md").write_text("# Existing")

        with (
            patch("kb.cli.console.print") as mock_print,
            patch("kb.book_import.default_output_dir") as mock_default,
        ):
            mock_default.return_value = output_dir

            result = runner.invoke(app, ["import-book", str(book_path)])

        assert result.exit_code == 0
        # Verify a table was printed (skip case adds row to table, then table is printed)
        table_printed = any(
            call_args.args and hasattr(call_args.args[0], "rows")
            for call_args in mock_print.call_args_list
        )
        assert table_printed, "Expected table with skip status to be printed"

    def test_should_import_multiple_books(self, tmp_path):
        book1 = tmp_path / "book1.epub"
        book2 = tmp_path / "book2.epub"
        book1.write_text("content1")
        book2.write_text("content2")

        with (
            patch("kb.cli.console.print"),
            patch("kb.book_import.import_epub") as mock_import,
        ):
            mock_import.side_effect = [
                ([tmp_path / "ch1.md"], tmp_path / "meta1.json"),
                ([tmp_path / "ch2.md"], tmp_path / "meta2.json"),
            ]

            result = runner.invoke(app, ["import-book", str(book1), str(book2)])

        assert result.exit_code == 0
        assert mock_import.call_count == 2

    def test_should_force_reimport_when_force_flag(self, tmp_path):
        book_path = tmp_path / "book.epub"
        book_path.write_text("content")
        output_dir = tmp_path / "raw" / "books" / "book"
        output_dir.mkdir(parents=True)
        (output_dir / "existing.md").write_text("# Existing")

        with (
            patch("kb.cli.console.print"),
            patch("kb.book_import.import_epub") as mock_import,
        ):
            mock_import.return_value = (
                [output_dir / "new.md"],
                output_dir / "meta.json",
            )

            result = runner.invoke(app, ["import-book", str(book_path), "--force"])

        assert result.exit_code == 0
        mock_import.assert_called_once()

    def test_should_commit_imported_artifacts_when_commit_flag_is_set(self, tmp_path):
        book_path = tmp_path / "book.epub"
        book_path.write_text("content")
        output_dir = tmp_path / "raw" / "books" / "book"
        chapter = output_dir / "01-intro.md"
        metadata = output_dir / "metadata.json"

        with (
            patch("kb.cli.console.print"),
            patch("kb.book_import.import_epub") as mock_import,
            patch("kb.git.commit") as mock_commit,
        ):
            mock_import.return_value = ([chapter], metadata)

            result = runner.invoke(app, ["import-book", str(book_path), "--commit"])

        assert result.exit_code == 0
        mock_commit.assert_called_once()
        committed_paths = mock_commit.call_args.args[1]
        assert chapter in committed_paths
        assert metadata in committed_paths
