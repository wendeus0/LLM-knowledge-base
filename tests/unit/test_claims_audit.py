"""Testes de integração claims↔audit: eventos emitidos em cada transição."""

from kb.audit import list_events
from kb.claims import (
    apply_decay_cycle,
    list_claims,
    record_compiled_claims,
    run_contradiction_check,
)


def _make_claim(tmp_raw_wiki, topic="ai", summary="Projeto X usa Redis para cache."):
    raw, wiki = tmp_raw_wiki
    source = raw / "doc.md"
    source.write_text("# Doc")
    article = wiki / topic / "doc.md"
    article.parent.mkdir(parents=True, exist_ok=True)
    article.write_text("# Doc")
    return record_compiled_claims(
        source_path=source,
        article_path=article,
        topic=topic,
        summary_text=summary,
    )


def test_should_emit_claim_created_audit_event_on_record(tmp_raw_wiki):
    _make_claim(tmp_raw_wiki)
    events = list_events()
    created = [e for e in events if e["event_type"] == "claim_created"]
    assert len(created) >= 1
    assert created[0]["source"] == "compile"
    assert created[0]["schema_version"] == "1.0"


def test_should_emit_claim_superseded_audit_event(tmp_raw_wiki):
    _make_claim(tmp_raw_wiki, summary="Redis para cache.")
    _make_claim(tmp_raw_wiki, summary="Valkey para cache.")
    events = list_events()
    superseded = [e for e in events if e["event_type"] == "claim_superseded"]
    assert len(superseded) >= 1
    assert superseded[0]["payload"].get("new_claim_id") is not None


def test_should_emit_status_changed_when_decay_marks_stale(tmp_raw_wiki):
    _make_claim(tmp_raw_wiki, topic="bug", summary="Erro transitório Z raro.")
    apply_decay_cycle(days_forward=400)
    events = list_events()
    stale_events = [
        e
        for e in events
        if e["event_type"] == "claim_status_changed"
        and e["payload"].get("new_status") == "stale"
    ]
    assert len(stale_events) >= 1
    assert stale_events[0]["source"] == "decay"


def test_should_emit_status_changed_when_contradiction_marks_disputed(tmp_raw_wiki):
    import json
    from kb.config import CLAIMS_PATH

    raw, wiki = tmp_raw_wiki
    source = raw / "doc.md"
    article = wiki / "ai" / "doc.md"
    article.parent.mkdir(parents=True, exist_ok=True)

    record_compiled_claims(
        source_path=source,
        article_path=article,
        topic="ai",
        summary_text="O modelo suporta fine-tuning.",
    )
    record_compiled_claims(
        source_path=source,
        article_path=article,
        topic="ai",
        summary_text="Nunca use fine-tuning para este modelo.",
    )

    # A segunda chamada supersedeu a primeira; reativar a claim antiga
    # para que o contradiction check encontre ambas ativas com sentimento oposto.
    claims = list_claims()
    for claim in claims:
        if claim["status"] == "superseded":
            claim["status"] = "active"
    CLAIMS_PATH.write_text(
        "\n".join(json.dumps(c, ensure_ascii=False) for c in claims) + "\n",
        encoding="utf-8",
    )

    run_contradiction_check()
    events = list_events()
    disputed = [
        e
        for e in events
        if e["event_type"] == "claim_status_changed"
        and e["payload"].get("new_status") == "disputed"
    ]
    assert len(disputed) >= 1
    assert disputed[0]["source"] == "contradiction-check"


def test_new_claims_should_have_schema_version(tmp_raw_wiki):
    claims = _make_claim(tmp_raw_wiki)
    for claim in claims:
        assert claim.get("schema_version") == "1.0"


def test_read_claims_without_schema_version_fallback(tmp_raw_wiki):
    import json
    from kb.config import CLAIMS_PATH

    _ = tmp_raw_wiki
    old_claim = {
        "id": "old-001",
        "text": "Claim legado sem schema_version",
        "topic": "ai",
        "status": "active",
        "confidence": 0.7,
    }
    CLAIMS_PATH.write_text(json.dumps(old_claim) + "\n", encoding="utf-8")

    claims = list_claims()
    assert len(claims) == 1
    assert claims[0]["id"] == "old-001"
    assert claims[0].get("schema_version") is None
