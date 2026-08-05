"""Notas persistidas por artigo da plataforma de estudos."""

from datetime import UTC, datetime

from study.db import _connect_db, _ensure_schema


def get_note(slug: str) -> dict | None:
    """Obtém a nota associada a um artigo."""
    with _connect_db() as conn:
        _ensure_schema(conn)
        row = conn.execute(
            "SELECT id, slug, body, created_at, updated_at FROM notes WHERE slug = ?",
            (slug,),
        ).fetchone()
    return _note_row(row)


def save_note(slug: str, body: str) -> dict:
    """Cria ou atualiza a única nota de um artigo."""
    now = datetime.now(UTC).isoformat()
    with _connect_db() as conn:
        _ensure_schema(conn)
        conn.execute(
            """
            INSERT INTO notes (slug, body, created_at, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(slug) DO UPDATE SET body = excluded.body, updated_at = excluded.updated_at
            """,
            (slug, body, now, now),
        )
        conn.commit()
    return get_note(slug)


def delete_note(slug: str) -> None:
    """Remove a nota associada a um artigo."""
    with _connect_db() as conn:
        _ensure_schema(conn)
        conn.execute("DELETE FROM notes WHERE slug = ?", (slug,))
        conn.commit()


def _note_row(row) -> dict | None:
    if row is None:
        return None
    return {
        "id": row[0],
        "slug": row[1],
        "body": row[2],
        "created_at": row[3],
        "updated_at": row[4],
    }
