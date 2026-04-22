from pathlib import Path
from unittest.mock import patch

from kb.jobs import (
    HealthGateError,
    build_operational_cron_lines,
    get_jobs_list_rows,
    get_recommended_cron_chain,
    list_jobs,
    run_health_gate,
    run_job,
)


def test_should_list_canonical_jobs():
    jobs = list_jobs()

    assert {job.name for job in jobs} == {
        "compile",
        "lint",
        "review",
        "metrics",
        "decay",
        "contradiction-check",
        "index-refresh",
        "health",
        "discovery",
    }


def test_should_run_jobs_via_underlying_modules(tmp_raw_wiki):
    fake_result = type("CompileBatchResult", (), {"outputs": [], "failures": []})()

    with (
        patch("kb.compile.discover_compile_targets") as mock_targets,
        patch("kb.compile.compile_many") as mock_compile_many,
        patch("kb.cmds.lint.run.execute_lint_command") as mock_lint,
        patch("kb.heal.heal") as mock_heal,
        patch("kb.analytics.gain.get_gain_summary") as mock_metrics,
        patch("kb.claims.apply_decay_cycle") as mock_decay,
        patch("kb.claims.run_contradiction_check") as mock_contradiction,
        patch("kb.compile.update_index") as mock_index_refresh,
        patch("kb.analytics.health.render_health_summary") as mock_health,
        patch("kb.analytics.health.get_health_summary") as mock_health_data,
        patch("kb.discovery.run_scheduled_discovery") as mock_discovery,
    ):
        mock_targets.return_value = []
        mock_compile_many.return_value = fake_result
        mock_heal.return_value = []
        mock_decay.return_value = 4
        mock_contradiction.return_value = {"disputed": 2, "active": 1}
        mock_metrics.return_value = {
            "total_runs": 2,
            "avg_savings_pct": 33.3,
            "recent": [],
        }
        mock_health.return_value = "Job health executado.\n- stale_pct: 12.5"
        mock_health_data.return_value = {
            "stale_pct": 12.5,
            "disputed_pct": 8.0,
        }
        mock_discovery.return_value = {
            "discovered": 3,
            "ingested": 2,
            "compiled": 1,
            "skipped_seen": 1,
            "compiled_enabled": True,
            "seen_urls_path": "/tmp/discovery_seen_urls.json",
            "failures": [],
        }

        assert "compile" in run_job("compile")
        mock_compile_many.assert_called_once_with([])

        mock_lint.return_value = "## Report\n- ok"
        lint_result = run_job("lint")
        assert "Job lint executado." in lint_result
        assert "## Report" in lint_result
        assert mock_lint.called

        assert "review" in run_job("review")
        mock_heal.assert_called_once_with(3, no_commit=False)

        metrics_result = run_job("metrics")
        assert "Job metrics executado." in metrics_result
        assert "33.3" in metrics_result

        decay_result = run_job("decay")
        assert "Job decay executado" in decay_result
        assert "4" in decay_result

        contradiction_result = run_job("contradiction-check")
        assert "Job contradiction-check executado" in contradiction_result
        assert "2" in contradiction_result

        index_result = run_job("index-refresh")
        assert "Job index-refresh executado" in index_result
        assert mock_index_refresh.called

        health_result = run_job("health")
        assert "Job health executado" in health_result
        assert "stale_pct" in health_result

        discovery_result = run_job("discovery")
        assert "Job discovery executado" in discovery_result
        assert "discovered: 3" in discovery_result
        assert "ingested: 2" in discovery_result


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


def test_jobs_list_rows_should_include_health_snapshot():
    with patch("kb.analytics.health.get_health_summary") as mock_health_data:
        mock_health_data.return_value = {
            "stale_pct": 15.0,
            "disputed_pct": 4.5,
        }

        rows = get_jobs_list_rows()

    health_rows = [r for r in rows if r["name"] == "health"]
    assert health_rows
    assert "stale=15.0%" in health_rows[0]["extra"]
    assert "disputed=4.5%" in health_rows[0]["extra"]


def test_recommended_cron_chain_should_follow_fase3_sequence():
    chain = get_recommended_cron_chain()

    assert [item["name"] for item in chain] == [
        "discovery",
        "decay",
        "contradiction-check",
        "index-refresh",
        "health",
    ]


def test_run_job_health_should_fail_when_threshold_exceeded(tmp_raw_wiki):
    with (
        patch("kb.analytics.health.render_health_summary") as mock_health,
        patch("kb.analytics.health.get_health_summary") as mock_health_data,
    ):
        mock_health.return_value = "Job health executado.\n- stale_pct: 35.0"
        mock_health_data.return_value = {
            "stale_pct": 35.0,
            "disputed_pct": 2.0,
        }

        try:
            run_job("health", stale_max_pct=20.0)
            raise AssertionError("expected HealthGateError")
        except HealthGateError as exc:
            assert "threshold_violation" in str(exc)


def test_run_health_gate_should_return_nonzero_when_violated():
    with patch("kb.analytics.health.get_health_summary") as mock_health_data:
        mock_health_data.return_value = {
            "stale_pct": 31.0,
            "disputed_pct": 2.0,
        }

        code, message = run_health_gate(stale_max_pct=20.0)

    assert code == 1
    assert "threshold_violation" in message


def test_build_operational_cron_lines_should_include_staggered_chain():
    lines = build_operational_cron_lines(
        executable="kb",
        stale_max_pct=20.0,
        disputed_max_pct=8.0,
    )

    assert len(lines) == 5
    assert "jobs run discovery" in lines[0]
    assert "jobs run decay" in lines[1]
    assert "jobs run contradiction-check" in lines[2]
    assert "jobs run index-refresh" in lines[3]
    assert "jobs run health --stale-max-pct 20.0 --disputed-max-pct 8.0" in lines[4]
