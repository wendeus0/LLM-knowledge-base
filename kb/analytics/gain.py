"""Renderização de resumo de ganhos (tracking)."""

from __future__ import annotations

from kb.analytics.history import get_history_summary
from kb.core.tracking import get_gain_summary


def render_gain_summary(limit: int = 10) -> str:
    data = get_gain_summary(limit=limit)
    history_7d = get_history_summary(days=7)

    lines = [
        "Job metrics executado.",
        f"- total_runs: {data['total_runs']}",
        f"- avg_savings_pct: {data['avg_savings_pct']}",
        f"- window_7d_runs: {history_7d['total_runs']}",
        f"- window_7d_failures: {history_7d['failure_runs']}",
        f"- window_7d_avg_duration_ms: {history_7d['avg_duration_ms']}",
    ]

    recent = data.get("recent", [])
    if recent:
        lines.append("- recent:")
        for item in recent:
            lines.append(
                f"  • {item['command']} | save={item['savings_pct']}% | exit={item['exit_code']} | {item['duration_ms']}ms"
            )

    by_command = history_7d.get("by_command", {})
    if by_command:
        lines.append("- by_command_7d:")
        for cmd, info in by_command.items():
            lines.append(
                f"  • {cmd}: runs={info['runs']} fails={info['failures']} avg_save={info['avg_savings_pct']}% avg_ms={info['avg_duration_ms']}"
            )

    return "\n".join(lines)
