"""Consultas históricas sobre tracking de comandos."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

from kb.core.tracking import DB_PATH


def _parse_now(now: str | None) -> datetime:
    if now:
        return datetime.fromisoformat(now)
    return datetime.now(timezone.utc)


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

    where = "timestamp >= ? AND timestamp <= ?"
    params: list[object] = [start.isoformat(), end.isoformat()]
    if command:
        where += " AND command = ?"
        params.append(command)

    with sqlite3.connect(DB_PATH) as conn:
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
        by_command = {
            cmd: {
                "category": category,
                "runs": int(runs),
                "avg_savings_pct": round(float(savings), 2),
                "avg_duration_ms": round(float(duration), 2),
                "failures": int(fails),
            }
            for cmd, category, runs, savings, duration, fails in cur.fetchall()
        }

    return {
        "window_days": int(days),
        "command_filter": command,
        "total_runs": int(total_runs),
        "failure_runs": int(failure_runs),
        "avg_savings_pct": round(float(avg_savings), 2),
        "avg_duration_ms": round(float(avg_duration), 2),
        "by_command": by_command,
    }
