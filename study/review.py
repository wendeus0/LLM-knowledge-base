"""Agendamento FSRS e fila calculada de revisão."""

import json
from datetime import UTC, datetime

from fsrs import Card, Rating, Scheduler

from study.cards import get_card
from study.db import _connect_db, _ensure_schema


def review_card(card_id: int, rating: int, reviewed_at: datetime | None = None) -> dict:
    """Registra um rating FSRS 1:1 e persiste somente a data calculada."""
    if rating not in {1, 2, 3, 4}:
        raise ValueError("Rating de revisão precisa estar entre 1 e 4.")
    card = get_card(card_id)
    if card is None:
        raise LookupError("Cartão não encontrado.")
    if card["state"] != "aceito" or not card["fsrs_state"]:
        raise ValueError("Somente cartões aceitos podem ser revisados.")

    review_time = reviewed_at or datetime.now(UTC)
    fsrs_card = Card.from_dict(json.loads(card["fsrs_state"]))
    next_card, _ = Scheduler(enable_fuzzing=False).review_card(
        fsrs_card, Rating(rating), review_datetime=review_time
    )
    due_at = next_card.due.isoformat()
    serialized = json.dumps(next_card.to_dict())
    with _connect_db() as conn:
        _ensure_schema(conn)
        conn.execute(
            """
            UPDATE cards
            SET fsrs_state = ?, due_at = ?, updated_at = ?
            WHERE id = ?
            """,
            (serialized, due_at, review_time.isoformat(), card_id),
        )
        cursor = conn.execute(
            """
            INSERT INTO reviews (card_id, rating, reviewed_at, due_at, stability, difficulty, fsrs_state)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                card_id,
                rating,
                review_time.isoformat(),
                due_at,
                next_card.stability,
                next_card.difficulty,
                serialized,
            ),
        )
        conn.commit()
    return get_review(cursor.lastrowid)


def get_review(review_id: int) -> dict | None:
    """Obtém o registro de uma revisão."""
    with _connect_db() as conn:
        _ensure_schema(conn)
        row = conn.execute(
            """
            SELECT id, card_id, rating, reviewed_at, due_at, stability, difficulty, fsrs_state
            FROM reviews WHERE id = ?
            """,
            (review_id,),
        ).fetchone()
    return _review_row(row)


def review_queue() -> list[dict]:
    """Lista cartões aceitos por data calculada, sem aceitar agenda manual."""
    with _connect_db() as conn:
        _ensure_schema(conn)
        rows = conn.execute(
            """
            SELECT id, slug, front, back, state, verdict, evidence, fsrs_state, due_at,
                   created_at, updated_at, accepted_at
            FROM cards
            WHERE state = 'aceito' AND due_at IS NOT NULL
            ORDER BY due_at, id
            """
        ).fetchall()
    return [_queue_row(row) for row in rows]


def due_card() -> dict | None:
    """Retorna o próximo cartão cuja data calculada já venceu."""
    now = datetime.now(UTC).isoformat()
    with _connect_db() as conn:
        _ensure_schema(conn)
        row = conn.execute(
            """
            SELECT id, slug, front, back, state, verdict, evidence, fsrs_state, due_at,
                   created_at, updated_at, accepted_at
            FROM cards
            WHERE state = 'aceito' AND due_at <= ?
            ORDER BY due_at, id LIMIT 1
            """,
            (now,),
        ).fetchone()
    return _queue_row(row)


def _review_row(row) -> dict | None:
    if row is None:
        return None
    return {
        "id": row[0],
        "card_id": row[1],
        "rating": row[2],
        "reviewed_at": row[3],
        "due_at": row[4],
        "stability": row[5],
        "difficulty": row[6],
        "fsrs_state": row[7],
    }


def _queue_row(row) -> dict | None:
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
