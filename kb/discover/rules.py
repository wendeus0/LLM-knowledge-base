"""Regras declarativas de classificação de comandos internos."""

from __future__ import annotations

INTERNAL_RULES: list[tuple[str, str]] = [
    ("ingest", "content"),
    ("import-book", "content"),
    ("compile", "pipeline"),
    ("qa", "qa"),
    ("search", "qa"),
    ("heal", "maintenance"),
    ("lint", "maintenance"),
    ("jobs", "operations"),
    ("discovery", "content"),
]
