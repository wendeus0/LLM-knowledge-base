"""Destaques textuais persistidos pela plataforma de estudos."""

from datetime import UTC, datetime

from study.db import _connect_db, _ensure_schema


def create_highlight(
    slug: str, quote: str, prefix: str, suffix: str, note: str = ""
) -> dict:
    """Registra um destaque pela âncora textual selecionada."""
    now = datetime.now(UTC).isoformat()
    with _connect_db() as conn:
        _ensure_schema(conn)
        cursor = conn.execute(
            """
            INSERT INTO highlights (slug, quote, prefix, suffix, note, created_at, orphaned_at)
            VALUES (?, ?, ?, ?, ?, ?, NULL)
            """,
            (slug, quote, prefix, suffix, note, now),
        )
        conn.commit()
    return get_highlight(cursor.lastrowid)


def get_highlight(highlight_id: int) -> dict | None:
    """Obtém um destaque pelo identificador interno."""
    with _connect_db() as conn:
        _ensure_schema(conn)
        row = conn.execute(
            """
            SELECT id, slug, quote, prefix, suffix, note, created_at, orphaned_at
            FROM highlights WHERE id = ?
            """,
            (highlight_id,),
        ).fetchone()
    return _highlight_row(row)


def active_highlights(slug: str, content: str) -> list[dict]:
    """Localiza destaques ativos e torna órfãs as âncoras perdidas."""
    with _connect_db() as conn:
        _ensure_schema(conn)
        rows = conn.execute(
            """
            SELECT id, slug, quote, prefix, suffix, note, created_at, orphaned_at
            FROM highlights WHERE slug = ? AND orphaned_at IS NULL ORDER BY id
            """,
            (slug,),
        ).fetchall()
        active = []
        orphaned_at = datetime.now(UTC).isoformat()
        for row in rows:
            highlight = _highlight_row(row)
            start = _locate(content, highlight)
            if start is None:
                conn.execute(
                    "UPDATE highlights SET orphaned_at = ? WHERE id = ?",
                    (orphaned_at, highlight["id"]),
                )
                continue
            highlight["start"] = start
            active.append(highlight)
        conn.commit()
    return active


def orphan_article(slug: str) -> None:
    """Torna órfãos os destaques ativos de um artigo indisponível."""
    with _connect_db() as conn:
        _ensure_schema(conn)
        conn.execute(
            """
            UPDATE highlights SET orphaned_at = ?
            WHERE slug = ? AND orphaned_at IS NULL
            """,
            (datetime.now(UTC).isoformat(), slug),
        )
        conn.commit()


def orphaned_highlights(slug: str | None = None) -> list[dict]:
    """Lista destaques que perderam a âncora sem descartar o trabalho salvo."""
    query = """
        SELECT id, slug, quote, prefix, suffix, note, created_at, orphaned_at
        FROM highlights WHERE orphaned_at IS NOT NULL
    """
    parameters = ()
    if slug is not None:
        query += " AND slug = ?"
        parameters = (slug,)
    query += " ORDER BY orphaned_at DESC, id DESC"
    with _connect_db() as conn:
        _ensure_schema(conn)
        rows = conn.execute(query, parameters).fetchall()
    return [_highlight_row(row) for row in rows]


def _locate(content: str, highlight: dict) -> int | None:
    """Posição do destaque no texto do artigo, ou None quando perdeu a âncora.

    Sem a âncora completa, só reancora quando a citação aparece uma única vez:
    escolher a primeira de várias marca um trecho que o leitor não destacou.
    """
    anchor = f"{highlight['prefix']}{highlight['quote']}{highlight['suffix']}"
    anchor_start = content.find(anchor)
    if anchor_start != -1:
        return anchor_start + len(highlight["prefix"])
    quote = highlight["quote"]
    if not quote:
        return None
    primeira = content.find(quote)
    if primeira == -1 or content.find(quote, primeira + 1) != -1:
        return None
    return primeira


def _highlight_row(row) -> dict | None:
    if row is None:
        return None
    return {
        "id": row[0],
        "slug": row[1],
        "quote": row[2],
        "prefix": row[3],
        "suffix": row[4],
        "note": row[5],
        "created_at": row[6],
        "orphaned_at": row[7],
    }
