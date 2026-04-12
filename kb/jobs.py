"""Catálogo simples de jobs agendáveis do kb."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Callable

from kb.core.tracking import track_command
from kb.discover import classify_job_command


@dataclass(frozen=True)
class JobSpec:
    name: str
    schedule: str
    description: str
    category: str


@dataclass(frozen=True)
class JobDefinition:
    spec: JobSpec
    handler: Callable[[], str]


def _run_compile_job() -> str:
    from kb.compile import compile_many, discover_compile_targets

    targets = discover_compile_targets()
    result = compile_many(targets)
    return (
        f"Job compile executado ({len(result.outputs)} alvo(s) compilado(s), "
        f"{len(result.failures)} falha(s))."
    )


def _run_lint_job() -> str:
    from kb.cmds.lint.run import execute_lint_command

    report = execute_lint_command(allow_sensitive=False)
    return f"Job lint executado.\n\n{report}"


def _run_review_job() -> str:
    from kb.heal import heal

    processed = heal(3)
    return f"Job review executado ({len(processed)} item(ns) processado(s))."


def _run_metrics_job() -> str:
    from kb.analytics.gain import render_gain_summary

    return render_gain_summary(limit=10)


_JOB_DEFINITIONS: dict[str, JobDefinition] = {
    "compile": JobDefinition(
        spec=JobSpec(
            name="compile",
            schedule="0 9 * * *",
            description="Compilar novos documentos de raw/ para wiki/ e atualizar o índice.",
            category=classify_job_command("compile"),
        ),
        handler=_run_compile_job,
    ),
    "lint": JobDefinition(
        spec=JobSpec(
            name="lint",
            schedule="0 8 * * 0",
            description="Auditar a wiki e relatar inconsistências.",
            category=classify_job_command("lint"),
        ),
        handler=_run_lint_job,
    ),
    "review": JobDefinition(
        spec=JobSpec(
            name="review",
            schedule="0 18 * * 5",
            description="Executar heal amostrado para manutenção da wiki.",
            category=classify_job_command("review"),
        ),
        handler=_run_review_job,
    ),
    "metrics": JobDefinition(
        spec=JobSpec(
            name="metrics",
            schedule="0 21 * * *",
            description="Exibir resumo de economia do tracking (RTK-style).",
            category=classify_job_command("metrics"),
        ),
        handler=_run_metrics_job,
    ),
}


def get_job_catalog() -> dict[str, JobSpec]:
    return {name: definition.spec for name, definition in _JOB_DEFINITIONS.items()}


def list_jobs() -> list[JobSpec]:
    return [definition.spec for definition in _JOB_DEFINITIONS.values()]


def run_job(name: str) -> str:
    normalized = name.strip().lower()
    definition = _JOB_DEFINITIONS.get(normalized)
    if definition is None:
        available = ", ".join(sorted(_JOB_DEFINITIONS))
        raise ValueError(f"Job desconhecido: {name}. Disponíveis: {available}")

    start = perf_counter()
    output = ""
    exit_code = 0
    try:
        output = definition.handler()
        return output
    except Exception as exc:
        exit_code = 1
        output = str(exc) or type(exc).__name__
        raise
    finally:
        duration_ms = int((perf_counter() - start) * 1000)
        try:
            track_command(
                command=f"jobs run {normalized}",
                category=definition.spec.category,
                project_path=Path.cwd(),
                exit_code=exit_code,
                raw_output=output,
                filtered_output=output,
                duration_ms=duration_ms,
            )
        except Exception:
            # Tracking é best-effort e nunca deve mascarar o resultado real do job.
            pass
