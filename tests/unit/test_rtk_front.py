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
            "recent": [],
        }

        output = run_job("metrics")

    assert "metrics" in output.lower()
    assert "3" in output


def test_cli_search_should_render_results():
    path = Path.cwd() / "wiki" / "article.md"
    fake_results = [
        {"path": path, "score": 10, "snippet": "snippet"},
    ]
    with (
        patch("kb.search.search") as mock_search,
        patch("kb.cli.console.print") as mock_print,
    ):
        mock_search.return_value = fake_results
        result = runner.invoke(app, ["search", "query"])

    assert result.exit_code == 0
    mock_search.assert_called_once_with("query")
    mock_print.assert_any_call("[bold]article[/] [dim](wiki/article.md)[/] score=10")
