"""Registry simples para classificação de comandos da CLI kb."""

from __future__ import annotations

from kb.discover.rules import INTERNAL_RULES

_RULE_MAP = {name: category for name, category in INTERNAL_RULES}


def classify_internal_command(command_name: str) -> str:
    """Classifica comando conhecido; retorna 'unknown' se não mapeado."""
    return _RULE_MAP.get(command_name.strip().lower(), "unknown")


def command_category(command_name: str) -> str:
    return classify_internal_command(command_name)
