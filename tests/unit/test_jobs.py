from unittest.mock import patch

from kb.jobs import list_jobs, run_job


def test_should_list_canonical_jobs():
    jobs = list_jobs()

    assert {job.name for job in jobs} == {"compile", "lint", "review", "metrics"}


def test_should_run_jobs_via_underlying_modules(tmp_raw_wiki):
    fake_result = type("CompileBatchResult", (), {"outputs": [], "failures": []})()

    with (
        patch("kb.compile.discover_compile_targets") as mock_targets,
        patch("kb.compile.compile_many") as mock_compile_many,
        patch("kb.lint.lint_wiki") as mock_lint,
        patch("kb.heal.heal") as mock_heal,
        patch("kb.analytics.gain.get_gain_summary") as mock_metrics,
    ):
        mock_targets.return_value = []
        mock_compile_many.return_value = fake_result
        mock_heal.return_value = []
        mock_metrics.return_value = {
            "total_runs": 2,
            "avg_savings_pct": 33.3,
            "recent": [],
        }

        assert "compile" in run_job("compile")
        mock_compile_many.assert_called_once_with([])

        mock_lint.return_value = "## Report\n- ok"
        lint_result = run_job("lint")
        assert "Job lint executado." in lint_result
        assert "## Report" in lint_result
        assert mock_lint.called

        assert "review" in run_job("review")
        assert mock_heal.called

        metrics_result = run_job("metrics")
        assert "Job metrics executado." in metrics_result
        assert "33.3" in metrics_result
