"""Execução do comando compile desacoplada da CLI."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from kb.compile import (
    CompileBatchResult,
    CompileFailure,
    compile_file,
    compile_many,
    discover_compile_targets,
    find_book_dirs,
    update_index as do_update_index,
)
from kb.guardrails import SensitiveContentError


@dataclass(frozen=True)
class CompileExecutionResult:
    exit_code: int
    message_lines: list[str]
    compiled_outputs: list[Path]
    failures: list[CompileFailure]
    targets: list[Path]
    book_dir_count: int = 0


def _resolve_targets(target: str | None) -> tuple[list[Path], int, list[str], int]:
    lines: list[str] = []
    if target is None:
        return discover_compile_targets(), 0, lines, 0

    path = Path(target)
    if path.exists():
        return discover_compile_targets(path), 0, lines, 0

    book_dirs = find_book_dirs(target)
    if not book_dirs:
        return [], 0, [f"[red]Nenhum livro encontrado para:[/] {target}"], 1

    targets: list[Path] = []
    for d in book_dirs:
        targets.extend(discover_compile_targets(d))

    lines.append(f"[dim]{len(book_dirs)} livro(s), {len(targets)} arquivo(s) a compilar[/]")
    return targets, len(book_dirs), lines, 0


def _effective_workers(targets: list[Path], workers: int | None) -> int:
    if workers is not None:
        return workers
    if len(targets) <= 3:
        return 1
    return min(len(targets), 4)


def execute_compile_command(
    *,
    target: str | None,
    update_index: bool,
    workers: int | None,
    allow_sensitive: bool,
    no_commit: bool,
    interactive_sensitive: bool,
    confirm_sensitive: Callable[[], bool] | None = None,
) -> CompileExecutionResult:
    targets, book_dir_count, lines, early_exit = _resolve_targets(target)
    if early_exit != 0:
        return CompileExecutionResult(
            exit_code=early_exit,
            message_lines=lines,
            compiled_outputs=[],
            failures=[],
            targets=[],
            book_dir_count=book_dir_count,
        )

    if not targets:
        return CompileExecutionResult(
            exit_code=0,
            message_lines=lines + ["[yellow]Nenhum arquivo em raw/[/]"],
            compiled_outputs=[],
            failures=[],
            targets=[],
            book_dir_count=book_dir_count,
        )

    effective_workers = _effective_workers(targets, workers)
    compiled_outputs: list[Path] = []
    failures: list[CompileFailure] = []

    if effective_workers == 1:
        for t in targets:
            try:
                out = compile_file(t, allow_sensitive=allow_sensitive, no_commit=no_commit)
            except SensitiveContentError as exc:
                if allow_sensitive:
                    out = compile_file(t, allow_sensitive=True, no_commit=no_commit)
                elif interactive_sensitive and confirm_sensitive and confirm_sensitive():
                    out = compile_file(t, allow_sensitive=True, no_commit=no_commit)
                else:
                    return CompileExecutionResult(
                        exit_code=1,
                        message_lines=lines,
                        compiled_outputs=compiled_outputs,
                        failures=[CompileFailure(raw_path=t, error=exc)],
                        targets=targets,
                        book_dir_count=book_dir_count,
                    )
            compiled_outputs.append(out)
    else:
        result: CompileBatchResult = compile_many(
            targets,
            workers=effective_workers,
            allow_sensitive=allow_sensitive,
            no_commit=no_commit,
            update_index_enabled=False,
        )
        compiled_outputs = result.outputs
        failures = result.failures

    if update_index and compiled_outputs:
        do_update_index(no_commit=no_commit)
        lines.append("[dim]Índice atualizado.[/]")

    if failures:
        lines.append(f"\n[bold red]Falhas: {len(failures)}/{len(targets)}[/]")
        for failure in failures:
            detail = str(failure.error) or type(failure.error).__name__
            lines.append(f"  [red]- {failure.raw_path.name}:[/] {detail}")
        exit_code = 1
    else:
        exit_code = 0

    return CompileExecutionResult(
        exit_code=exit_code,
        message_lines=lines,
        compiled_outputs=compiled_outputs,
        failures=failures,
        targets=targets,
        book_dir_count=book_dir_count,
    )
