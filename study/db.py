"""Persistência SQLite do estado de estudo da plataforma."""

import sqlite3
from contextlib import closing
from pathlib import Path


def database_path() -> Path:
    """Retorna o banco da plataforma ao lado dos diretórios do vault."""
    from kb import config

    return config.DATA_DIR / "study.db"


def _connect_db(db_path: Path | None = None):
    path = db_path or database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    return closing(sqlite3.connect(path))


def _ensure_schema(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY,
            slug TEXT NOT NULL UNIQUE,
            body TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS highlights (
            id INTEGER PRIMARY KEY,
            slug TEXT NOT NULL,
            quote TEXT NOT NULL,
            prefix TEXT NOT NULL,
            suffix TEXT NOT NULL,
            note TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            orphaned_at TEXT
        )
        """)
    note_columns = {row[1] for row in conn.execute("PRAGMA table_info(notes)")}
    if "updated_at" not in note_columns:
        conn.execute("ALTER TABLE notes ADD COLUMN updated_at TEXT NOT NULL DEFAULT ''")
    highlight_columns = {
        row[1] for row in conn.execute("PRAGMA table_info(highlights)")
    }
    if "orphaned_at" not in highlight_columns:
        conn.execute("ALTER TABLE highlights ADD COLUMN orphaned_at TEXT")
