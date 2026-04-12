"""Runner compartilhado inspirado no contrato de execução do RTK."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess
import time
from typing import Callable

from kb.core.tracking import track_command


FilterFn = Callable[[str], str]


@dataclass(frozen=True)
class CommandResult:
    command: str
    exit_code: int
    raw_output: str
    filtered_output: str
    duration_ms: int


def _safe_filter(filter_fn: FilterFn, output: str) -> tuple[str, bool]:
    try:
        return filter_fn(output), True
    except Exception:
        # Fail-safe igual ao RTK: nunca bloquear comando por falha de filtro.
        return output, False


def run_command(
    *,
    command: list[str],
    filter_fn: FilterFn,
    cwd: Path | None = None,
    track: bool = True,
) -> CommandResult:
    """Executa comando externo com fallback e tracking de economia.

    Contratos:
    - preserva exit code
    - se filtro falhar, retorna saída crua
    - registra raw x filtered para analytics
    """
    start = time.perf_counter()
    proc = subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
    )

    raw = (proc.stdout or "") + (proc.stderr or "")
    filtered, _ok = _safe_filter(filter_fn, raw)
    duration_ms = int((time.perf_counter() - start) * 1000)

    result = CommandResult(
        command=" ".join(command),
        exit_code=int(proc.returncode),
        raw_output=raw,
        filtered_output=filtered,
        duration_ms=duration_ms,
    )

    if track:
        track_command(
            command=result.command,
            project_path=Path.cwd(),
            exit_code=result.exit_code,
            raw_output=result.raw_output,
            filtered_output=result.filtered_output,
            duration_ms=result.duration_ms,
        )

    return result
