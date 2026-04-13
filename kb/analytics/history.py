"""Consultas históricas sobre tracking de comandos."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone

from kb.core.tracking import DB_PATH, _ensure_schema


def _parse_now(now: str | None) -> datetime:
    if now:
        parsed = datetime.fromisoformat(now)
    else:
        parsed = datetime.now(timezone.utc)

    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def get_history_summary(
    *,
    command: str | None = None,
    days: int = 7,
    now: str | None = None,
) -> dict:
    if not DB_PATH.exists():
        return {
            "window_days": int(days),
            "command_filter": command,
            "total_runs": 0,
            "failure_runs": 0,
            "avg_savings_pct": 0.0,
            "avg_duration_ms": 0.0,
            "by_command": {},
        }

    end = _parse_now(now)
    start = end - timedelta(days=int(days))
    start_bound = start.astimezone(timezone.utc).isoformat()
    end_bound = end.astimezone(timezone.utc).isoformat()

    where = "timestamp >= ? AND timestamp <= ?"
    params: list[object] = [start_bound, end_bound]
    if command:
        where += " AND command = ?"
        params.append(command)

    with sqlite3.connect(DB_PATH) as conn:
        _ensure_schema(conn)
        cur = conn.cursor()

        cur.execute(
            f"""
            SELECT
                COUNT(*),
                COALESCE(SUM(CASE WHEN exit_code != 0 THEN 1 ELSE 0 END), 0),
                COALESCE(AVG(savings_pct), 0),
                COALESCE(AVG(duration_ms), 0)
            FROM commands
            WHERE {where}
            """,
            params,
        )
        total_runs, failure_runs, avg_savings, avg_duration = cur.fetchone()

        cur.execute(
            f"""
            SELECT
                command,
                COALESCE(category, 'unknown'),
                COUNT(*),
                COALESCE(AVG(savings_pct), 0),
                COALESCE(AVG(duration_ms), 0),
                COALESCE(SUM(CASE WHEN exit_code != 0 THEN 1 ELSE 0 END), 0)
            FROM commands
            WHERE {where}
            GROUP BY command, COALESCE(category, 'unknown')
            ORDER BY COUNT(*) DESC, command ASC
            """,
            params,
        )
        by_command: dict[str, dict[str, object]] = {}
        for cmd, category, runs, savings, duration, fails in cur.fetchall():
            existing = by_command.get(cmd)
            if existing is None:
                by_command[cmd] = {
                    "category": category,
                    "runs": int(runs),
                    "avg_savings_pct": round(float(savings), 2),
                    "avg_duration_ms": round(float(duration), 2),
                    "failures": int(fails),
                }
                continue

            prev_runs = int(existing["runs"])
            merged_runs = prev_runs + int(runs)
            merged_savings = (
                float(existing["avg_savings_pct"]) * prev_runs
                + float(savings) * int(runs)
            ) / merged_runs
            merged_duration = (
                float(existing["avg_duration_ms"]) * prev_runs
                + float(duration) * int(runs)
            ) / merged_runs
            categories = {
                *(
                    cat.strip()
                    for cat in str(existing["category"]).split(",")
                    if cat.strip()
                ),
                category,
            }
            existing.update(
                {
                    "category": (
                        ", ".join(sorted(categories)) if categories else "unknown"
                    ),
                    "runs": merged_runs,
                    "avg_savings_pct": round(merged_savings, 2),
                    "avg_duration_ms": round(merged_duration, 2),
                    "failures": int(existing["failures"]) + int(fails),
                }
            )

    return {
        "window_days": int(days),
        "command_filter": command,
        "total_runs": int(total_runs),
        "failure_runs": int(failure_runs),
        "avg_savings_pct": round(float(avg_savings), 2),
        "avg_duration_ms": round(float(avg_duration), 2),
        "by_command": by_command,
    }
