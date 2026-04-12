import sqlite3

from kb.analytics.history import get_history_summary


def _seed(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS commands (
            id INTEGER PRIMARY KEY,
            timestamp TEXT NOT NULL,
            command TEXT NOT NULL,
            exit_code INTEGER NOT NULL,
            input_chars INTEGER NOT NULL,
            output_chars INTEGER NOT NULL,
            saved_chars INTEGER NOT NULL,
            savings_pct REAL NOT NULL,
            duration_ms INTEGER NOT NULL,
            project_path TEXT NOT NULL
        )
        """
    )

    rows = [
        ("2026-04-10T10:00:00+00:00", "compile", 0, 100, 60, 40, 40.0, 1000, "/repo"),
        ("2026-04-10T11:00:00+00:00", "compile", 1, 80, 80, 0, 0.0, 800, "/repo"),
        ("2026-04-11T11:00:00+00:00", "lint", 0, 50, 25, 25, 50.0, 300, "/repo"),
        ("2026-04-11T12:00:00+00:00", "metrics", 0, 30, 30, 0, 0.0, 100, "/repo"),
    ]
    conn.executemany(
        """
        INSERT INTO commands (
            timestamp, command, exit_code, input_chars, output_chars,
            saved_chars, savings_pct, duration_ms, project_path
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )
    conn.commit()


def test_history_summary_should_filter_by_command(tmp_path, monkeypatch):
    db = tmp_path / "tracking.db"
    monkeypatch.setattr("kb.analytics.history.DB_PATH", db)

    with sqlite3.connect(db) as conn:
        _seed(conn)

    summary = get_history_summary(command="compile", days=30)

    assert summary["total_runs"] == 2
    assert summary["failure_runs"] == 1
    assert summary["avg_duration_ms"] == 900.0


def test_history_summary_should_apply_days_window(tmp_path, monkeypatch):
    db = tmp_path / "tracking.db"
    monkeypatch.setattr("kb.analytics.history.DB_PATH", db)

    with sqlite3.connect(db) as conn:
        _seed(conn)

    summary = get_history_summary(command=None, days=1, now="2026-04-11T12:30:00+00:00")

    assert summary["total_runs"] == 2
    assert summary["by_command"]["lint"]["runs"] == 1
    assert summary["by_command"]["metrics"]["runs"] == 1
