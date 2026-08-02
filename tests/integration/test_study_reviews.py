from datetime import UTC, datetime

from fastapi.testclient import TestClient
from fsrs import Card, Rating, Scheduler


def _isolated_vault(tmp_path, monkeypatch):
    from kb import config

    data_dir = tmp_path / "vault"
    (data_dir / "wiki").mkdir(parents=True)
    monkeypatch.setattr(config, "DATA_DIR", data_dir)
    return data_dir


def test_should_schedule_the_next_review_with_fsrs_and_show_it_in_the_calendar(
    tmp_path, monkeypatch
):
    from study.cards import accept_card, create_card
    from study.review import review_card, review_queue

    _isolated_vault(tmp_path, monkeypatch)
    card = accept_card(create_card("ai/transformers", "Pergunta", "Resposta", "ancorada", "" )["id"])
    reviewed_at = datetime(2026, 8, 2, 12, 0, tzinfo=UTC)

    review = review_card(card["id"], 3, reviewed_at=reviewed_at)
    expected_due = Scheduler(enable_fuzzing=False).review_card(
        Card(), Rating.Good, review_datetime=reviewed_at
    )[0].due.isoformat()
    queue = review_queue()

    assert review["rating"] == 3
    assert review["due_at"] == expected_due
    assert any(item["id"] == card["id"] and item["due_at"] == expected_due for item in queue)


def test_should_not_offer_or_honor_a_manual_due_date(tmp_path, monkeypatch):
    from study.cards import accept_card, create_card, get_card
    from study.web import app

    _isolated_vault(tmp_path, monkeypatch)
    card = accept_card(create_card("ai/transformers", "Pergunta", "Resposta", "ancorada", "")["id"])

    response = TestClient(app).post(
        f"/revisar/{card['id']}", data={"rating": "3", "due_at": "2000-01-01T00:00:00+00:00"}
    )

    assert response.status_code == 200
    assert 'name="due_at"' not in response.text
    assert get_card(card["id"])["due_at"] != "2000-01-01T00:00:00+00:00"
