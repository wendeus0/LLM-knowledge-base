from pathlib import Path
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
        patch("kb.cmds.lint.run.execute_lint_command") as mock_lint,
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


def test_should_fail_with_explicit_error_for_unknown_job():
    try:
        run_job("unknown")
        raise AssertionError("expected ValueError")
    except ValueError as exc:
        message = str(exc)
        assert "Job desconhecido: unknown." in message
        assert "Disponíveis:" in message


def test_should_track_successful_job_execution(tmp_raw_wiki):
    with patch("kb.jobs.track_command") as mock_track:
        output = run_job("metrics")

    assert "Job metrics executado." in output
    assert mock_track.call_count == 1
    kwargs = mock_track.call_args.kwargs
    assert kwargs["command"] == "jobs run metrics"
    assert kwargs["exit_code"] == 0
    assert kwargs["category"] == "operations"
    assert kwargs["project_path"] == Path.cwd()


def test_should_track_failed_job_execution(tmp_raw_wiki):
    with (
        patch("kb.jobs._JOB_DEFINITIONS") as mock_defs,
        patch("kb.jobs.track_command") as mock_track,
    ):
        failing = type("JobDefinition", (), {})()
        failing.spec = type("JobSpec", (), {"category": "maintenance"})()

        def _boom():
            raise RuntimeError("kaboom")

        failing.handler = _boom
        mock_defs.get.side_effect = lambda name: failing if name == "broken" else None
        mock_defs.__iter__.return_value = iter(["broken"])

        try:
            run_job("broken")
            raise AssertionError("expected RuntimeError")
        except RuntimeError as exc:
            assert str(exc) == "kaboom"

    assert mock_track.call_count == 1
    kwargs = mock_track.call_args.kwargs
    assert kwargs["command"] == "jobs run broken"
    assert kwargs["exit_code"] == 1
    assert kwargs["raw_output"] == "kaboom"
    assert kwargs["category"] == "maintenance"


def test_should_not_mask_job_error_when_tracking_fails(tmp_raw_wiki):
    with (
        patch("kb.jobs._JOB_DEFINITIONS") as mock_defs,
        patch("kb.jobs.track_command", side_effect=RuntimeError("db down")),
    ):
        failing = type("JobDefinition", (), {})()
        failing.spec = type("JobSpec", (), {"category": "maintenance"})()

        def _boom():
            raise RuntimeError("kaboom")

        failing.handler = _boom
        mock_defs.get.side_effect = lambda name: failing if name == "broken" else None
        mock_defs.__iter__.return_value = iter(["broken"])

        try:
            run_job("broken")
            raise AssertionError("expected RuntimeError")
        except RuntimeError as exc:
            assert str(exc) == "kaboom"
