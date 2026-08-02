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
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys = ON")
    return closing(conn)


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
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cards (
            id INTEGER PRIMARY KEY,
            slug TEXT NOT NULL,
            front TEXT NOT NULL,
            back TEXT NOT NULL,
            state TEXT NOT NULL CHECK (state IN ('curadoria', 'aceito', 'descartado')),
            verdict TEXT NOT NULL,
            evidence TEXT NOT NULL DEFAULT '',
            fsrs_state TEXT,
            due_at TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            accepted_at TEXT
        )
        """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            card_id INTEGER NOT NULL REFERENCES cards(id),
            rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 4),
            reviewed_at TEXT NOT NULL,
            due_at TEXT NOT NULL,
            stability REAL,
            difficulty REAL,
            fsrs_state TEXT NOT NULL
        )
        """)
    conn.execute("CREATE INDEX IF NOT EXISTS cards_by_slug ON cards(slug, state, due_at)")
    conn.execute("CREATE INDEX IF NOT EXISTS reviews_by_card ON reviews(card_id, reviewed_at)")
