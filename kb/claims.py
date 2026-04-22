"""Lifecycle de claims: confiança, supersession e decaimento."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
import math
import re
import uuid
from pathlib import Path

from kb.audit import record_event
from kb.config import CLAIMS_PATH
from kb.state import ensure_state_dirs, normalize_source_path


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _to_iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat()


def _from_iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _read_claims() -> list[dict]:
    ensure_state_dirs()
    if not CLAIMS_PATH.exists():
        return []
    lines = CLAIMS_PATH.read_text(encoding="utf-8").splitlines()
    entries: list[dict] = []
    for line in lines:
        payload = line.strip()
        if not payload:
            continue
        entries.append(json.loads(payload))
    return entries


def _write_claims(entries: list[dict]) -> None:
    ensure_state_dirs()
    content = "\n".join(json.dumps(entry, ensure_ascii=False) for entry in entries)
    if content:
        content += "\n"
    CLAIMS_PATH.write_text(content, encoding="utf-8")


def list_claims() -> list[dict]:
    return _read_claims()


def _split_claims(summary_text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", summary_text.strip())
    claims = [part.strip() for part in parts if len(part.strip()) >= 20]
    return claims or ([summary_text.strip()] if summary_text.strip() else [])


def _base_confidence(text: str, topic: str) -> float:
    words = len(text.split())
    size_bonus = min(0.15, words / 200)
    topic_bonus = 0.05 if topic in {"ai", "python", "typescript", "cybersecurity"} else 0.0
    return min(0.95, 0.55 + size_bonus + topic_bonus)


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def record_compiled_claims(
    *,
    source_path: Path,
    article_path: Path,
    topic: str,
    summary_text: str,
) -> list[dict]:
    claims = _read_claims()
    now = _now()
    normalized_source = normalize_source_path(source_path)

    active_same_source = [
        item for item in claims if item.get("source") == normalized_source and item.get("status") == "active"
    ]

    new_claims: list[dict] = []
    for text in _split_claims(summary_text):
        claim_id = str(uuid.uuid4())
        base = round(_base_confidence(text, topic), 3)
        entry = {
            "schema_version": "1.0",
            "id": claim_id,
            "text": text,
            "topic": topic,
            "source": normalized_source,
            "article": str(article_path),
            "status": "active",
            "confidence": base,
            "initial_confidence": base,
            "evidence_count": 1,
            "created_at": _to_iso(now),
            "updated_at": _to_iso(now),
            "last_confirmed_at": _to_iso(now),
            "relationships": {
                "supersedes": None,
                "superseded_by": None,
                "contradicts": [],
            },
        }
        new_claims.append(entry)

    if new_claims and active_same_source:
        replacement = new_claims[0]["id"]
        for previous in active_same_source:
            previous["status"] = "superseded"
            previous["updated_at"] = _to_iso(now)
            previous.setdefault("relationships", {})["superseded_by"] = replacement
            record_event(
                event_type="claim_superseded",
                claim_id=previous["id"],
                payload={"new_claim_id": replacement},
                source="compile",
            )
        new_claims[0]["relationships"]["supersedes"] = active_same_source[0]["id"]

    claims.extend(new_claims)
    _write_claims(claims)

    for claim in new_claims:
        record_event(
            event_type="claim_created",
            claim_id=claim["id"],
            payload={"topic": topic, "source": str(normalized_source)},
            source="compile",
        )

    return new_claims


def _decayed_confidence(claim: dict, now: datetime) -> float:
    last_confirmed = _from_iso(claim.get("last_confirmed_at", claim.get("updated_at", _to_iso(now))))
    age_days = max(0.0, (now - last_confirmed).total_seconds() / 86400)
    half_life_days = 60 if claim.get("topic") in {"architecture", "decision"} else 30
    decay = math.exp(-(math.log(2) * age_days / half_life_days))
    evidence_boost = 1 + (0.07 * max(0, int(claim.get("evidence_count", 1)) - 1))
    base = float(claim.get("initial_confidence", claim.get("confidence", 0.5)))
    return _clamp(base * decay * evidence_boost)


def apply_decay_cycle(days_forward: int = 0) -> int:
    claims = _read_claims()
    if not claims:
        return 0

    now = _now() + timedelta(days=days_forward)
    updated = 0
    pending_events: list[tuple[str, str, dict, str]] = []
    for claim in claims:
        if claim.get("status") != "active":
            continue
        decayed = _decayed_confidence(claim, now)
        old = float(claim.get("confidence", 0.0))
        if abs(decayed - old) > 1e-6:
            claim["confidence"] = round(decayed, 3)
            claim["updated_at"] = _to_iso(now)
            updated += 1
        if decayed < 0.3:
            claim["status"] = "stale"
            claim["updated_at"] = _to_iso(now)
            pending_events.append((
                "claim_status_changed",
                claim["id"],
                {"old_status": "active", "new_status": "stale", "confidence": round(decayed, 3)},
                "decay",
            ))

    _write_claims(claims)
    for event_type, claim_id, payload, source in pending_events:
        record_event(event_type=event_type, claim_id=claim_id, payload=payload, source=source)
    return updated


def _simple_score(blob: str, terms: set[str]) -> int:
    return sum(blob.count(term) for term in terms)


def find_relevant_claims(question: str, top_k: int = 3) -> list[dict]:
    terms = {term for term in re.findall(r"\w+", question.lower()) if len(term) > 2}
    if not terms:
        return []

    scored: list[tuple[int, dict]] = []
    for claim in _read_claims():
        if claim.get("status") not in {"active", "stale"}:
            continue
        blob = f"{claim.get('text', '')} {claim.get('topic', '')} {claim.get('source', '')}".lower()
        score = _simple_score(blob, terms)
        if score > 0:
            scored.append((score, claim))

    scored.sort(key=lambda item: (item[0], item[1].get("confidence", 0)), reverse=True)
    return [claim for _, claim in scored[:top_k]]


def run_contradiction_check() -> dict[str, int]:
    """Heurística simples para marcar claims em potencial contradição.

    Regra v1: claims ativas do mesmo source+topic com confiança próxima e
    com sentenças iniciando por negação/oposição entram em `disputed`.
    """
    claims = _read_claims()
    updated = 0
    now = _to_iso(_now())
    pending_events: list[tuple[str, str, dict, str]] = []

    by_bucket: dict[tuple[str, str], list[dict]] = {}
    for claim in claims:
        if claim.get("status") != "active":
            continue
        key = (claim.get("source", ""), claim.get("topic", ""))
        by_bucket.setdefault(key, []).append(claim)

    def _is_negative(text: str) -> bool:
        lower = text.lower().strip()
        return lower.startswith(("não ", "nao ", "nunca ", "jamais ", "sem "))

    for bucket_claims in by_bucket.values():
        for idx, left in enumerate(bucket_claims):
            for right in bucket_claims[idx + 1 :]:
                left_neg = _is_negative(left.get("text", ""))
                right_neg = _is_negative(right.get("text", ""))
                if left_neg == right_neg:
                    continue

                c1 = float(left.get("confidence", 0.0))
                c2 = float(right.get("confidence", 0.0))
                if abs(c1 - c2) > 0.25:
                    continue

                for claim in (left, right):
                    if claim.get("status") != "disputed":
                        claim["status"] = "disputed"
                        claim["updated_at"] = now
                        pending_events.append((
                            "claim_status_changed",
                            claim["id"],
                            {"old_status": "active", "new_status": "disputed"},
                            "contradiction-check",
                        ))
                        updated += 1

    _write_claims(claims)
    for event_type, claim_id, payload, source in pending_events:
        record_event(event_type=event_type, claim_id=claim_id, payload=payload, source=source)

    disputed = sum(1 for c in claims if c.get("status") == "disputed")
    active = sum(1 for c in claims if c.get("status") == "active")
    return {"disputed": disputed, "active": active, "updated": updated}
