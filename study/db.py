"""Persistência SQLite do estado de estudo da plataforma."""

import sqlite3
from contextlib import closing
from pathlib import Path


def database_path() -> Path:
    """Retorna o banco da plataforma ao lado dos diretórios do vault.

    Fica em `DATA_DIR`, não em `kb_state/`: é dado de estudo do usuário, não
    estado derivado da engine. Sem `KB_DATA_DIR` configurado, `DATA_DIR` é a
    raiz do repositório — daí `study.db*` estar no `.gitignore`.
    """
    from kb import config

    return config.DATA_DIR / "study.db"


def _connect_db(db_path: Path | None = None):
    path = db_path or database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=30.0)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return closing(conn)


CARD_COLUMNS = """
    id, slug, front, back, state, verdict, evidence, fsrs_state, due_at,
    created_at, updated_at, accepted_at
"""


def card_row(row) -> dict | None:
    """Serializa uma linha de `cards` na ordem de `CARD_COLUMNS`."""
    if row is None:
        return None
    return {
        "id": row[0],
        "slug": row[1],
        "front": row[2],
        "back": row[3],
        "state": row[4],
        "verdict": row[5],
        "evidence": row[6],
        "fsrs_state": row[7],
        "due_at": row[8],
        "created_at": row[9],
        "updated_at": row[10],
        "accepted_at": row[11],
    }


def _add_column(conn: sqlite3.Connection, table: str, column: str, definition: str) -> None:
    """Adiciona coluna ausente tolerando outra conexão migrando ao mesmo tempo.

    Duas conexões leem o `PRAGMA table_info` antes de qualquer uma escrever, as
    duas concluem que falta a coluna e a segunda estoura `duplicate column name`
    — reproduzido com oito conexões simultâneas sobre um banco legado.
    """
    columns = {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}
    if column in columns:
        return
    try:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
    except sqlite3.OperationalError as exc:
        if "duplicate column name" not in str(exc):
            raise


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
    _add_column(conn, "notes", "updated_at", "TEXT NOT NULL DEFAULT ''")
    _add_column(conn, "highlights", "orphaned_at", "TEXT")
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
