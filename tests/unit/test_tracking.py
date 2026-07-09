import sqlite3
from contextlib import closing

from kb.core import tracking


def _use_tracking_db(tmp_path, monkeypatch):
    state_dir = tmp_path / "kb_state"
    db = state_dir / "tracking.db"
    monkeypatch.setattr(tracking, "STATE_DIR", state_dir)
    monkeypatch.setattr(tracking, "DB_PATH", db)
    monkeypatch.setattr(tracking._connect_db, "__defaults__", (db,))
    return db


def test_should_persist_command_row_when_track_command_is_called(tmp_path, monkeypatch):
    """
    Dado um banco de tracking temporario,
    Quando track_command registra uma execucao,
    Entao a linha deve ser persistida com metricas calculadas.
    """
    db = _use_tracking_db(tmp_path, monkeypatch)

    tracking.track_command(
        command="compile",
        project_path=tmp_path,
        exit_code=0,
        raw_output="abcdef",
        filtered_output="ab",
        duration_ms=123,
        category="pipeline",
    )

    with closing(sqlite3.connect(db)) as conn:
        row = conn.execute(
            """
            SELECT command, category, exit_code, input_chars, output_chars,
                   saved_chars, savings_pct, duration_ms, project_path
            FROM commands
            """
        ).fetchone()

    assert row == ("compile", "pipeline", 0, 6, 2, 4, 66.67, 123, str(tmp_path))


def test_should_keep_schema_when_initialized_twice(tmp_path, monkeypatch):
    """
    Dado um banco de tracking vazio,
    Quando a inicializacao de schema roda duas vezes,
    Entao a tabela commands deve continuar valida.
    """
    db = _use_tracking_db(tmp_path, monkeypatch)
    db.parent.mkdir(parents=True)

    with closing(sqlite3.connect(db)) as conn:
        tracking._ensure_schema(conn)
        tracking._ensure_schema(conn)
        columns = {
            row[1] for row in conn.execute("PRAGMA table_info(commands)").fetchall()
        }

    assert "command" in columns
    assert "category" in columns
    assert "project_path" in columns


def test_should_migrate_category_column_when_schema_is_legacy(tmp_path, monkeypatch):
    """
    Dado uma tabela commands sem coluna category,
    Quando a migracao leve de schema roda,
    Entao a coluna category deve ser adicionada com default unknown.
    """
    db = _use_tracking_db(tmp_path, monkeypatch)
    db.parent.mkdir(parents=True)

    with closing(sqlite3.connect(db)) as conn:
        conn.execute("""
            CREATE TABLE commands (
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
            """)
        conn.execute(
            """
            INSERT INTO commands (
                timestamp, command, exit_code, input_chars, output_chars,
                saved_chars, savings_pct, duration_ms, project_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            ("2026-01-01T00:00:00+00:00", "lint", 0, 10, 5, 5, 50.0, 20, "/repo"),
        )
        tracking._ensure_schema(conn)
        row = conn.execute("SELECT category FROM commands").fetchone()

    assert row == ("unknown",)
