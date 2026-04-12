"""Relatório de saúde do estado de claims."""

from __future__ import annotations

from kb.claims import list_claims


def _pct(part: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return round((part / total) * 100, 1)


def get_health_summary() -> dict:
    claims = list_claims()
    total = len(claims)

    active = sum(1 for c in claims if c.get("status") == "active")
    stale = sum(1 for c in claims if c.get("status") == "stale")
    disputed = sum(1 for c in claims if c.get("status") == "disputed")
    superseded = sum(1 for c in claims if c.get("status") == "superseded")

    avg_confidence = round(
        sum(float(c.get("confidence", 0.0)) for c in claims) / total,
        3,
    ) if total else 0.0

    return {
        "total_claims": total,
        "active": active,
        "stale": stale,
        "disputed": disputed,
        "superseded": superseded,
        "active_pct": _pct(active, total),
        "stale_pct": _pct(stale, total),
        "disputed_pct": _pct(disputed, total),
        "superseded_pct": _pct(superseded, total),
        "avg_confidence": avg_confidence,
    }


def evaluate_health_thresholds(
    summary: dict,
    stale_max_pct: float | None = None,
    disputed_max_pct: float | None = None,
) -> tuple[bool, list[str]]:
    violations: list[str] = []
    if stale_max_pct is not None and float(summary.get("stale_pct", 0.0)) > float(stale_max_pct):
        violations.append(
            f"stale_pct={summary.get('stale_pct')} ultrapassou limite={stale_max_pct}"
        )
    if disputed_max_pct is not None and float(summary.get("disputed_pct", 0.0)) > float(disputed_max_pct):
        violations.append(
            f"disputed_pct={summary.get('disputed_pct')} ultrapassou limite={disputed_max_pct}"
        )
    return (len(violations) == 0), violations


def render_health_summary() -> str:
    data = get_health_summary()
    lines = [
        "Job health executado.",
        f"- total_claims: {data['total_claims']}",
        f"- active_pct: {data['active_pct']}",
        f"- stale_pct: {data['stale_pct']}",
        f"- disputed_pct: {data['disputed_pct']}",
        f"- superseded_pct: {data['superseded_pct']}",
        f"- avg_confidence: {data['avg_confidence']}",
    ]
    return "\n".join(lines)
