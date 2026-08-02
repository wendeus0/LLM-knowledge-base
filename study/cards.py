"""Geração e curadoria de flashcards ancorados no artigo de origem."""

import json
from datetime import UTC, datetime

from kb import client, grounding
from kb.guardrails import (
    assert_safe_for_provider,
    new_sentinel,
    untrusted_policy,
    wrap_untrusted,
)
from study.db import _connect_db, _ensure_schema

MAX_CARDS_PER_ARTICLE = 5


def generate_cards(slug: str, content: str) -> list[dict]:
    """Gera até cinco cartões em curadoria e registra o grounding de cada um."""
    assert_safe_for_provider(content, source=f"artigo {slug}")
    sentinel = new_sentinel()
    response = client.chat(
        [
            {
                "role": "system",
                "content": (
                    "Gere no máximo cinco flashcards curtos, autocontidos e úteis para "
                    "revisão. Responda somente com um array JSON de objetos `front` e `back`. "
                    "Cada `back` deve ser uma frase declarativa de 40 a 240 caracteres, "
                    "verificável somente contra o artigo."
                ),
            },
            {"role": "system", "content": untrusted_policy(sentinel)},
            {
                "role": "user",
                "content": f"Artigo {slug}:\n{wrap_untrusted(content, sentinel)}",
            },
        ],
        temperature=0.2,
    )
    cards = []
    for candidate in _candidates(response):
        verdict, evidence = _ground(candidate["front"], candidate["back"], content)
        cards.append(create_card(slug, candidate["front"], candidate["back"], verdict, evidence))
    return cards


def create_card(slug: str, front: str, back: str, verdict: str, evidence: str) -> dict:
    """Cria um cartão em curadoria, sem colocá-lo automaticamente em revisão."""
    now = _now()
    with _connect_db() as conn:
        _ensure_schema(conn)
        cursor = conn.execute(
            """
            INSERT INTO cards (slug, front, back, state, verdict, evidence, created_at, updated_at)
            VALUES (?, ?, ?, 'curadoria', ?, ?, ?, ?)
            """,
            (slug, front, back, verdict, evidence, now, now),
        )
        conn.commit()
    return get_card(cursor.lastrowid)


def get_card(card_id: int) -> dict | None:
    """Obtém um cartão pelo identificador interno."""
    with _connect_db() as conn:
        _ensure_schema(conn)
        row = conn.execute(
            """
            SELECT id, slug, front, back, state, verdict, evidence, fsrs_state, due_at,
                   created_at, updated_at, accepted_at
            FROM cards WHERE id = ?
            """,
            (card_id,),
        ).fetchone()
    return _card_row(row)


def cards_for_article(slug: str) -> list[dict]:
    """Lista os cartões do artigo, inclusive decisões de curadoria já tomadas."""
    with _connect_db() as conn:
        _ensure_schema(conn)
        rows = conn.execute(
            """
            SELECT id, slug, front, back, state, verdict, evidence, fsrs_state, due_at,
                   created_at, updated_at, accepted_at
            FROM cards WHERE slug = ? ORDER BY id DESC
            """,
            (slug,),
        ).fetchall()
    return [_card_row(row) for row in rows]


def accept_card(card_id: int) -> dict:
    """Aceita somente cartão cujo grounding foi literalmente ancorada."""
    card = get_card(card_id)
    if card is None:
        raise LookupError("Cartão não encontrado.")
    if card["state"] != "curadoria" or card["verdict"] != "ancorada":
        raise ValueError("Somente cartões ancorados em curadoria podem ser aceitos.")

    from fsrs import Card

    accepted_at = _now()
    fsrs_card = Card(card_id=card_id)
    with _connect_db() as conn:
        _ensure_schema(conn)
        conn.execute(
            """
            UPDATE cards
            SET state = 'aceito', fsrs_state = ?, due_at = ?, accepted_at = ?, updated_at = ?
            WHERE id = ?
            """,
            (json.dumps(fsrs_card.to_dict()), fsrs_card.due.isoformat(), accepted_at, accepted_at, card_id),
        )
        conn.commit()
    return get_card(card_id)


def edit_card(card_id: int, front: str, back: str, content: str) -> dict:
    """Edita um cartão e o devolve à curadoria com grounding recalculado."""
    card = get_card(card_id)
    if card is None:
        raise LookupError("Cartão não encontrado.")
    if card["state"] == "descartado":
        raise ValueError("Cartões descartados não podem ser editados.")
    verdict, evidence = _ground(front, back, content)
    now = _now()
    with _connect_db() as conn:
        _ensure_schema(conn)
        conn.execute(
            """
            UPDATE cards
            SET front = ?, back = ?, state = 'curadoria', verdict = ?, evidence = ?,
                fsrs_state = NULL, due_at = NULL, accepted_at = NULL, updated_at = ?
            WHERE id = ?
            """,
            (front, back, verdict, evidence, now, card_id),
        )
        conn.commit()
    return get_card(card_id)


def discard_card(card_id: int) -> dict:
    """Registra o descarte de um cartão sem alterar seu artigo de origem."""
    card = get_card(card_id)
    if card is None:
        raise LookupError("Cartão não encontrado.")
    if card["state"] != "curadoria":
        raise ValueError("Somente cartões em curadoria podem ser descartados.")
    with _connect_db() as conn:
        _ensure_schema(conn)
        conn.execute(
            "UPDATE cards SET state = 'descartado', updated_at = ? WHERE id = ?",
            (_now(), card_id),
        )
        conn.commit()
    return get_card(card_id)


def _candidates(response: str) -> list[dict]:
    payload = response.strip()
    if payload.startswith("```"):
        payload = payload.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
    try:
        parsed = json.loads(payload)
    except json.JSONDecodeError:
        return []
    if isinstance(parsed, dict):
        parsed = parsed.get("cards", [])
    if not isinstance(parsed, list):
        return []
    cards = []
    for candidate in parsed[:MAX_CARDS_PER_ARTICLE]:
        if not isinstance(candidate, dict):
            continue
        front = candidate.get("front")
        back = candidate.get("back")
        if isinstance(front, str) and isinstance(back, str) and front.strip() and back.strip():
            cards.append({"front": front.strip(), "back": back.strip()})
    return cards


def _ground(front: str, back: str, content: str) -> tuple[str, str]:
    try:
        result = grounding.verify(f"Pergunta: {front}\nResposta: {back}", content)
    except grounding.GroundingUnavailable:
        return "degraded", ""
    if result.status != "verified":
        return result.status, ""
    for claim in result.claims:
        if claim.verdict != "ancorada":
            return claim.verdict, claim.evidence
    if result.claims:
        return "ancorada", result.claims[0].evidence
    return "skipped", ""


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _card_row(row) -> dict | None:
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
