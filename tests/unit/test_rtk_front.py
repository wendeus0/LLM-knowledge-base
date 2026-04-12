from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from kb.cli import app
from kb.compile import update_index
from kb.jobs import run_job

runner = CliRunner()


def test_update_index_should_create_wiki_dir_when_missing(tmp_path, monkeypatch):
    missing_wiki = tmp_path / "wiki_missing"
    monkeypatch.setattr("kb.compile.WIKI_DIR", missing_wiki)

    update_index(no_commit=True)

    assert (missing_wiki / "_index.md").exists()


def test_jobs_run_metrics_should_return_tracking_summary(tmp_raw_wiki):
    with patch("kb.analytics.gain.get_gain_summary") as mock_summary:
        mock_summary.return_value = {
            "total_runs": 3,
            "avg_savings_pct": 42.5,
            "recent": [],
        }

        output = run_job("metrics")

    assert "metrics" in output.lower()
    assert "3" in output
    assert "42.5" in output


def test_cli_search_should_route_through_cmd_module():
    fake_results = [
        "[bold]article[/] [dim](wiki/article.md)[/] score=10",
        "  [dim]snippet[/]",
    ]
    with (
        patch("kb.cmds.search.run.execute_search_command") as mock_execute,
        patch("kb.cli.console.print") as mock_print,
    ):
        mock_execute.return_value = fake_results
        result = runner.invoke(app, ["search", "query"])

    assert result.exit_code == 0
    mock_execute.assert_called_once_with("query")
    mock_print.assert_any_call(fake_results[0])
