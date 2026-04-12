"""Execução do comando lint desacoplada da CLI."""

from __future__ import annotations


def execute_lint_command(*, allow_sensitive: bool = False) -> str:
    from kb.lint import lint_wiki

    return lint_wiki(allow_sensitive=allow_sensitive)
