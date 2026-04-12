"""Tracking simples de execuções no estilo RTK (SQLite)."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from kb.config import STATE_DIR

DB_PATH = STATE_DIR / "tracking.db"


def _ensure_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS commands (
            id INTEGER PRIMARY KEY,
            timestamp TEXT NOT NULL,
            command TEXT NOT NULL,
            category TEXT NOT NULL DEFAULT 'unknown',
            exit_code INTEGER NOT NULL,
            input_chars INTEGER NOT NULL,
            output_chars INTEGER NOT NULL,
            saved_chars INTEGER NOT NULL,
            savings_pct REAL NOT NULL,
            duration_ms INTEGER NOT NULL,
            project_path TEXT NOT NULL
        )
        """
    )

    # Migração leve para bases antigas sem coluna de categoria.
    columns = {
        row[1] for row in conn.execute("PRAGMA table_info(commands)").fetchall()
    }
    if "category" not in columns:
        conn.execute(
            "ALTER TABLE commands ADD COLUMN category TEXT NOT NULL DEFAULT 'unknown'"
        )


def _count_tokens_estimate(text: str) -> int:
    # Mesmo princípio do RTK: aproximação simples por chars/4.
    return max(1, (len(text) + 3) // 4) if text else 0


def track_command(
    *,
    command: str,
    project_path: Path,
    exit_code: int,
    raw_output: str,
    filtered_output: str,
    duration_ms: int,
    category: str = "unknown",
) -> None:
    """Registra uma execução para analytics de economia."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)

    in_chars = len(raw_output)
    out_chars = len(filtered_output)
    saved = max(0, in_chars - out_chars)
    savings_pct = (saved / in_chars * 100.0) if in_chars > 0 else 0.0

    with sqlite3.connect(DB_PATH) as conn:
        _ensure_schema(conn)
        conn.execute(
            """
            INSERT INTO commands (
                timestamp, command, category, exit_code, input_chars, output_chars,
                saved_chars, savings_pct, duration_ms, project_path
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now(timezone.utc).isoformat(),
                command,
                category,
                int(exit_code),
                in_chars,
                out_chars,
                saved,
                round(savings_pct, 2),
                int(duration_ms),
                str(project_path),
            ),
        )
        conn.commit()


def get_gain_summary(limit: int = 20) -> dict:
    """Retorna resumo de ganho recente para futura CLI analytics."""
    if not DB_PATH.exists():
        return {
            "total_runs": 0,
            "avg_savings_pct": 0.0,
            "recent": [],
        }

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*), COALESCE(AVG(savings_pct),0) FROM commands")
        total_runs, avg_savings = cur.fetchone()

        cur.execute(
            """
            SELECT timestamp, command, category, savings_pct, exit_code, duration_ms
            FROM commands
            ORDER BY id DESC
            LIMIT ?
            """,
            (int(limit),),
        )
        recent = [
            {
                "timestamp": ts,
                "command": cmd,
                "category": category,
                "savings_pct": pct,
                "exit_code": code,
                "duration_ms": ms,
            }
            for ts, cmd, category, pct, code, ms in cur.fetchall()
        ]

    return {
        "total_runs": int(total_runs),
        "avg_savings_pct": round(float(avg_savings), 2),
        "recent": recent,
    }
