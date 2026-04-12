"""Renderização de resumo de ganhos (tracking)."""

from __future__ import annotations

from kb.core.tracking import get_gain_summary


def render_gain_summary(limit: int = 10) -> str:
    data = get_gain_summary(limit=limit)
    lines = [
        "Job metrics executado.",
        f"- total_runs: {data['total_runs']}",
        f"- avg_savings_pct: {data['avg_savings_pct']}",
    ]

    recent = data.get("recent", [])
    if recent:
        lines.append("- recent:")
        for item in recent:
            lines.append(
                f"  • {item['command']} | save={item['savings_pct']}% | exit={item['exit_code']} | {item['duration_ms']}ms"
            )

    return "\n".join(lines)
