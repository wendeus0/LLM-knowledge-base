import json
import sqlite3
from contextlib import closing
from datetime import datetime

from typer.testing import CliRunner

from kb.cli import app

runner = CliRunner()


def _write_claims(path, claims):
    path.write_text(
        "\n".join(json.dumps(claim, ensure_ascii=False) for claim in claims) + "\n",
        encoding="utf-8",
    )


def _seed_tracking_db(path):
    with closing(sqlite3.connect(path)) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS commands (
                id INTEGER PRIMARY KEY,
                timestamp TEXT NOT NULL,
                command TEXT NOT NULL,
                category TEXT NOT NULL DEFAULT 'unknown',
                exit_code INTEGER NOT NULL,
                input_chars INTEGER NOT NULL,
                output_chars INTEGER NOT NULL,
                saved_chars INTEGER NOT NULL,
                savings_pct REAL NOT NULL,
                duration_ms INTEGER NOT NULL,
                project_path TEXT NOT NULL
            )
            """)
        conn.executemany(
            """
            INSERT INTO commands (
                timestamp, command, category, exit_code, input_chars, output_chars,
                saved_chars, savings_pct, duration_ms, project_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    "2026-07-08T10:00:00+00:00",
                    "compile",
                    "compile",
                    0,
                    100,
                    90,
                    10,
                    10.0,
                    1200,
                    "/repo",
                ),
                (
                    "2026-07-08T11:00:00+00:00",
                    "lint",
                    "lint",
                    1,
                    50,
                    50,
                    0,
                    0.0,
                    800,
                    "/repo",
                ),
                (
                    "2026-06-01T10:00:00+00:00",
                    "qa",
                    "qa",
                    0,
                    10,
                    10,
                    0,
                    0.0,
                    100,
                    "/repo",
                ),
            ],
        )
        conn.commit()


def test_stats_cli_shows_claims_table_by_status(tmp_raw_wiki, tmp_path, monkeypatch):
    _, _ = tmp_raw_wiki
    claims_path = tmp_path / "kb_state" / "claims.jsonl"
    _write_claims(
        claims_path,
        [
            {"id": "c1", "status": "active", "confidence": 0.9},
            {"id": "c2", "status": "stale", "confidence": 0.3},
            {"id": "c3", "status": "disputed", "confidence": 0.6},
            {"id": "c4", "status": "superseded", "confidence": 0.8},
        ],
    )
    monkeypatch.setattr("kb.analytics.history.DB_PATH", tmp_path / "missing.db")

    result = runner.invoke(app, ["stats"])

    assert result.exit_code == 0
    assert "Claims por status" in result.output
    assert "active" in result.output
    assert "stale" in result.output
    assert "disputed" in result.output
    assert "superseded" in result.output
    assert "Avg confidence" in result.output
    assert "0.65" in result.output


def test_stats_cli_shows_history_metrics_for_last_7_days(
    tmp_raw_wiki, tmp_path, monkeypatch
):
    _, _ = tmp_raw_wiki
    db = tmp_path / "tracking.db"
    _seed_tracking_db(db)
    monkeypatch.setattr("kb.analytics.history.DB_PATH", db)
    monkeypatch.setattr(
        "kb.analytics.history._parse_now",
        lambda now: datetime.fromisoformat("2026-07-09T12:00:00+00:00"),
    )

    result = runner.invoke(app, ["stats"])

    assert result.exit_code == 0
    assert "History 7d" in result.output
    assert "Total runs" in result.output
    assert "Failures" in result.output
    assert "Avg duration" in result.output
    assert "2" in result.output
    assert "1" in result.output
    assert "1000.0" in result.output
    assert "savings" not in result.output.lower()


def test_stats_json_output_is_parseable(tmp_raw_wiki, tmp_path, monkeypatch):
    _, wiki = tmp_raw_wiki
    (wiki / "ai" / "agentes.md").write_text("# Agentes\n", encoding="utf-8")
    (wiki / "python" / "cli.md").write_text("# CLI\n", encoding="utf-8")
    (wiki / "_index.md").write_text("# Index\n", encoding="utf-8")
    (wiki / "summaries").mkdir(exist_ok=True)
    (wiki / "summaries" / "skip.md").write_text("# Skip\n", encoding="utf-8")
    (wiki / ".heal_backup").mkdir(exist_ok=True)
    (wiki / ".heal_backup" / "skip.md").write_text("# Skip\n", encoding="utf-8")
    monkeypatch.setattr("kb.analytics.history.DB_PATH", tmp_path / "missing.db")

    result = runner.invoke(app, ["stats", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["claims"]["total_claims"] == 0
    assert payload["history_7d"]["window_days"] == 7
    assert payload["articles"]["total"] == 2
    assert payload["articles"]["by_topic"] == {"ai": 1, "python": 1}


def test_stats_with_empty_vault_returns_zeros(tmp_raw_wiki, tmp_path, monkeypatch):
    _, _ = tmp_raw_wiki
    monkeypatch.setattr("kb.analytics.history.DB_PATH", tmp_path / "missing.db")

    result = runner.invoke(app, ["stats", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["claims"]["total_claims"] == 0
    assert payload["claims"]["active"] == 0
    assert payload["claims"]["stale"] == 0
    assert payload["history_7d"]["total_runs"] == 0
    assert payload["history_7d"]["failure_runs"] == 0
    assert payload["history_7d"]["avg_duration_ms"] == 0.0
    assert payload["articles"]["total"] == 0
    assert payload["articles"]["by_topic"] == {}


def test_stats_rich_total_pct_is_zero_when_vault_is_empty(
    tmp_raw_wiki, tmp_path, monkeypatch
):
    _, _ = tmp_raw_wiki
    monkeypatch.setattr("kb.analytics.history.DB_PATH", tmp_path / "missing.db")

    result = runner.invoke(app, ["stats"])

    assert result.exit_code == 0
    assert "100.0%" not in result.output
    assert "0.0%" in result.output
