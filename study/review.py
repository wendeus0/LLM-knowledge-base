"""Agendamento FSRS e fila calculada de revisão."""

import json
from datetime import UTC, datetime

from fsrs import Card, Rating, Scheduler

from study.db import _connect_db, _ensure_schema, card_row


def review_card(card_id: int, rating: int, reviewed_at: datetime | None = None) -> dict:
    """Registra um rating FSRS 1:1 e persiste somente a data calculada."""
    if rating not in {1, 2, 3, 4}:
        raise ValueError("Rating de revisão precisa estar entre 1 e 4.")
    review_time = reviewed_at or datetime.now(UTC)
    with _connect_db() as conn:
        _ensure_schema(conn)
        # Ler o `fsrs_state` fora da transação que o reescreve perde a revisão
        # concorrente: as duas partem do mesmo estado e a última sobrescreve a
        # outra. `BEGIN IMMEDIATE` serializa a leitura junto da escrita.
        conn.isolation_level = None
        conn.execute("BEGIN IMMEDIATE")
        card = _card_state(conn, card_id)
        if card is None:
            raise LookupError("Cartão não encontrado.")
        if card["state"] != "aceito" or not card["fsrs_state"]:
            raise ValueError("Somente cartões aceitos podem ser revisados.")

        fsrs_card = Card.from_dict(json.loads(card["fsrs_state"]))
        next_card, _ = Scheduler(enable_fuzzing=False).review_card(
            fsrs_card, Rating(rating), review_datetime=review_time
        )
        due_at = next_card.due.isoformat()
        serialized = json.dumps(next_card.to_dict())
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


def _card_state(conn, card_id: int) -> dict | None:
    row = conn.execute(
        "SELECT state, fsrs_state FROM cards WHERE id = ?", (card_id,)
    ).fetchone()
    return None if row is None else {"state": row[0], "fsrs_state": row[1]}


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
    return [card_row(row) for row in rows]


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
    return card_row(row)


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
