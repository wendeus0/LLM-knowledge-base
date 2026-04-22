import json
from pathlib import Path

import pytest

from kb.audit import list_events, record_event


def test_should_append_event_when_record_event_is_called(tmp_raw_wiki):
    # RED: falha até audit ser implementado
    record_event(
        event_type="claim_created",
        claim_id="clm_001",
        payload={"topic": "ai"},
        source="compile",
    )

    events = list_events()
    assert len(events) == 1
    assert events[0]["event_type"] == "claim_created"
    assert events[0]["claim_id"] == "clm_001"
    assert events[0]["source"] == "compile"
    assert "timestamp" in events[0]
    assert events[0]["schema_version"] == "1.0"


def test_should_preserve_previous_events_on_subsequent_records(tmp_raw_wiki):
    # RED: falha até audit ser implementado
    record_event(
        event_type="claim_created", claim_id="clm_001", payload={}, source="compile"
    )
    record_event(
        event_type="claim_superseded",
        claim_id="clm_001",
        payload={"new_id": "clm_002"},
        source="compile",
    )

    events = list_events()
    assert len(events) == 2
    assert events[1]["event_type"] == "claim_superseded"


def test_should_not_raise_when_audit_path_is_unwritable(
    tmp_raw_wiki, monkeypatch, capsys
):
    # RED: falha até audit ser implementado
    monkeypatch.setattr("kb.config.AUDIT_PATH", Path("/nonexistent/dir/events.jsonl"))

    record_event(
        event_type="claim_created",
        claim_id="clm_001",
        payload={},
        source="compile",
    )

    captured = capsys.readouterr()
    assert "warning" in captured.err.lower() or "audit" in captured.err.lower()
