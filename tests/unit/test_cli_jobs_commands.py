from typer.testing import CliRunner

from kb.cli import app


runner = CliRunner()


def test_jobs_list_should_show_operational_cron(monkeypatch):
    from kb import jobs as jobs_module

    monkeypatch.setattr(
        jobs_module,
        "get_jobs_list_rows",
        lambda: [
            {
                "name": "health",
                "schedule": "30 3 * * *",
                "description": "Health",
                "extra": "stale=10.0% | disputed=2.0%",
            }
        ],
    )
    monkeypatch.setattr(
        jobs_module,
        "get_recommended_cron_chain",
        lambda: [
            {
                "name": "health",
                "schedule": "30 3 * * *",
                "purpose": "Emitir snapshot",
            }
        ],
    )
    monkeypatch.setattr(
        jobs_module,
        "build_operational_cron_lines",
        lambda executable, stale_max_pct, disputed_max_pct: [
            "30 3 * * * kb jobs run health --stale-max-pct 20.0 --disputed-max-pct 8.0"
        ],
    )

    result = runner.invoke(app, ["jobs", "list"])
    assert result.exit_code == 0
    assert "Cron operacional sugerido" in result.stdout
    assert "kb jobs run health" in result.stdout


def test_jobs_gate_should_return_exit_1_on_violation(monkeypatch):
    from kb import jobs as jobs_module

    monkeypatch.setattr(
        jobs_module,
        "run_health_gate",
        lambda stale_max_pct, disputed_max_pct: (1, "threshold_violation: stale_pct=30"),
    )

    result = runner.invoke(app, ["jobs", "gate", "--stale-max-pct", "20"])
    assert result.exit_code == 1
    assert "threshold_violation" in result.stdout


def test_jobs_gate_should_return_exit_0_when_ok(monkeypatch):
    from kb import jobs as jobs_module

    monkeypatch.setattr(
        jobs_module,
        "run_health_gate",
        lambda stale_max_pct, disputed_max_pct: (0, "health gate OK"),
    )

    result = runner.invoke(app, ["jobs", "gate"])
    assert result.exit_code == 0
    assert "health gate OK" in result.stdout


def test_jobs_cron_should_print_copy_paste_block(monkeypatch):
    from kb import jobs as jobs_module

    monkeypatch.setattr(
        jobs_module,
        "build_operational_cron_lines",
        lambda executable, stale_max_pct, disputed_max_pct: [
            "0 3 * * * python -m kb.cli jobs run decay",
            "10 3 * * * python -m kb.cli jobs run contradiction-check",
        ],
    )

    result = runner.invoke(app, ["jobs", "cron"])
    assert result.exit_code == 0
    assert "python -m kb.cli jobs run decay" in result.stdout
    assert "python -m kb.cli jobs run contradiction-check" in result.stdout
