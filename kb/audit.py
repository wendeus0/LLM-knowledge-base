"""Trilha de auditoria append-only para mutações de claims."""

from __future__ import annotations

import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

import kb.config as _config


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _to_iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat()


def _ensure_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def record_event(*, event_type: str, claim_id: str, payload: dict, source: str) -> None:
    entry = {
        "schema_version": "1.0",
        "event_id": f"evt_{uuid.uuid4().hex}",
        "event_type": event_type,
        "claim_id": claim_id,
        "payload": payload,
        "source": source,
        "timestamp": _to_iso(_now()),
    }
    try:
        _ensure_dir(_config.AUDIT_PATH)
        with _config.AUDIT_PATH.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as exc:
        print(f"warning: falha ao escrever audit log: {exc}", file=sys.stderr)


def list_events() -> list[dict]:
    if not _config.AUDIT_PATH.exists():
        return []
    events: list[dict] = []
    for line in _config.AUDIT_PATH.read_text(encoding="utf-8").splitlines():
        payload = line.strip()
        if not payload:
            continue
        try:
            events.append(json.loads(payload))
        except json.JSONDecodeError:
            continue
    return events
