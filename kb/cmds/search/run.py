"""Execução do comando search desacoplada da CLI."""

from __future__ import annotations

from pathlib import Path


def execute_search_command(query: str) -> list[str]:
    from kb.search import search as do_search

    lines: list[str] = []
    results = do_search(query)
    if not results:
        return ["[yellow]Nenhum resultado encontrado.[/]"]

    for r in results:
        rel = (
            r["path"].relative_to(Path.cwd())
            if r["path"].is_relative_to(Path.cwd())
            else r["path"]
        )
        lines.append(f"[bold]{r['path'].stem}[/] [dim]({rel})[/] score={r['score']}")
        if r["snippet"]:
            lines.append(f"  [dim]{r['snippet'][:120]}[/]")

    return lines
