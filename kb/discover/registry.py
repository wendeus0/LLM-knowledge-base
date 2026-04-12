"""Registry simples para classificação de comandos da CLI kb."""

from __future__ import annotations

from kb.discover.rules import INTERNAL_RULES

_RULE_MAP = {name: category for name, category in INTERNAL_RULES}


def classify_internal_command(command_name: str) -> str:
    """Classifica comando conhecido; retorna 'unknown' se não mapeado."""
    return _RULE_MAP.get(command_name.strip().lower(), "unknown")


def command_category(command_name: str) -> str:
    return classify_internal_command(command_name)


def classify_job_command(job_name: str) -> str:
    """Classifica jobs a partir do comando principal associado."""
    normalized = job_name.strip().lower()
    if normalized == "review":
        return command_category("heal")
    if normalized == "metrics":
        return command_category("jobs")
    return command_category(normalized)
