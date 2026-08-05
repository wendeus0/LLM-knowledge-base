import re
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from fsrs import Scheduler


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
    queue = review_queue()

    # Data literal, não recalculada pelo mesmo `Scheduler` da implementação:
    # o oráculo antigo passaria mesmo se a agenda parasse de ser aplicada.
    # `fsrs` 6, primeiro passo de aprendizado com rating Bom: +10 minutos.
    assert review["rating"] == 3
    assert review["due_at"] == "2026-08-02T12:10:00+00:00"
    assert any(
        item["id"] == card["id"] and item["due_at"] == "2026-08-02T12:10:00+00:00"
        for item in queue
    )


def test_should_not_offer_or_honor_a_manual_due_date(tmp_path, monkeypatch):
    from study.cards import accept_card, create_card, get_card
    from study.web import app

    _isolated_vault(tmp_path, monkeypatch)
    card = accept_card(create_card("ai/transformers", "Pergunta", "Resposta", "ancorada", "")["id"])

    response = TestClient(app, client=("127.0.0.1", 51234)).post(
        f"/revisar/{card['id']}", data={"rating": "3", "due_at": "2000-01-01T00:00:00+00:00"}
    )

    assert response.status_code == 200
    assert 'name="due_at"' not in response.text
    assert get_card(card["id"])["due_at"] != "2000-01-01T00:00:00+00:00"


def test_should_answer_a_rating_with_the_panel_fragment_not_the_whole_page(tmp_path, monkeypatch):
    """`hx-swap="outerHTML"` sobre `#review-body` recebendo a página inteira
    aninhava um documento dentro do painel."""
    from study.cards import accept_card, create_card
    from study.web import app

    _isolated_vault(tmp_path, monkeypatch)
    card = accept_card(create_card("ai/transformers", "Pergunta", "Resposta", "ancorada", "")["id"])

    resposta = TestClient(app, client=("127.0.0.1", 51234)).post(
        f"/revisar/{card['id']}", data={"rating": "3"}
    )

    assert resposta.status_code == 200
    assert 'id="review-body"' in resposta.text
    assert "<!DOCTYPE" not in resposta.text
    assert "<html" not in resposta.text
    # A data devida aparece legível; o ISO fica no atributo `datetime`.
    assert re.search(r"\d{2}/\d{2}/\d{4} às \d{2}:\d{2}</time>", resposta.text)


def test_should_not_lose_a_review_when_two_of_them_race_over_the_same_card(
    tmp_path, monkeypatch
):
    from study import review as review_module
    from study.cards import accept_card, create_card

    _isolated_vault(tmp_path, monkeypatch)
    card = accept_card(create_card("ai/transformers", "Pergunta", "Resposta", "ancorada", "")["id"])

    class SchedulerLento(Scheduler):
        def review_card(self, *args, **kwargs):
            time.sleep(0.05)
            return super().review_card(*args, **kwargs)

    monkeypatch.setattr(review_module, "Scheduler", SchedulerLento)
    with ThreadPoolExecutor(max_workers=2) as pool:
        revisoes = [
            futuro.result()
            for futuro in [pool.submit(review_module.review_card, card["id"], 3) for _ in range(2)]
        ]

    assert len({revisao["fsrs_state"] for revisao in revisoes}) == 2
    assert review_module.review_queue()[0]["due_at"] == max(r["due_at"] for r in revisoes)


@pytest.mark.parametrize("rating", ["0", "5", "-1", "abc", ""])
def test_should_reject_the_review_when_the_rating_is_outside_the_fsrs_range(
    tmp_path, monkeypatch, rating
):
    from study.cards import accept_card, create_card, get_card
    from study.web import app

    _isolated_vault(tmp_path, monkeypatch)
    card = accept_card(create_card("ai/transformers", "Pergunta", "Resposta", "ancorada", "")["id"])
    before = get_card(card["id"])

    response = TestClient(app, client=("127.0.0.1", 51234)).post(
        f"/revisar/{card['id']}", data={"rating": rating}
    )

    assert response.status_code == 400
    after = get_card(card["id"])
    assert after["due_at"] == before["due_at"]
    assert after["fsrs_state"] == before["fsrs_state"]
