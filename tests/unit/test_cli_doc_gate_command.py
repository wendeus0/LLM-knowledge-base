from typer.testing import CliRunner

from kb.cli import app


runner = CliRunner()


def test_doc_gate_should_fail_when_code_changed_without_doc(monkeypatch):
    monkeypatch.setattr(
        "subprocess.run",
        lambda *args, **kwargs: type("Proc", (), {"stdout": "kb/cli.py\n", "returncode": 0})(),
    )

    result = runner.invoke(app, ["jobs", "doc-gate"])
    assert result.exit_code == 1
    assert "Mudança de código detectada" in result.stdout


def test_doc_gate_should_pass_when_code_changed_with_handoff(monkeypatch):
    monkeypatch.setattr(
        "subprocess.run",
        lambda *args, **kwargs: type(
            "Proc",
            (),
            {
                "stdout": "kb/cli.py\ndocs/handoffs/2026-04-12-2300.md\n",
                "returncode": 0,
            },
        )(),
    )

    result = runner.invoke(app, ["jobs", "doc-gate"])
    assert result.exit_code == 0
    assert "Mudança de código acompanhada" in result.stdout
