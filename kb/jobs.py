"""Catálogo simples de jobs agendáveis do kb."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Callable

from kb.core.tracking import track_command
from kb.discover import classify_job_command


class HealthGateError(RuntimeError):
    """Lançado quando um threshold de health é ultrapassado em run_job."""


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


def _run_decay_job() -> str:
    from kb.claims import apply_decay_cycle

    updated = apply_decay_cycle()
    return f"Job decay executado ({updated} claim(s) atualizado(s))."


def _run_contradiction_check_job() -> str:
    from kb.claims import run_contradiction_check

    report = run_contradiction_check()
    return (
        "Job contradiction-check executado "
        f"(disputed={report.get('disputed', 0)}, active={report.get('active', 0)})."
    )


def _run_index_refresh_job() -> str:
    from kb.compile import update_index

    update_index(no_commit=True)
    return "Job index-refresh executado."


def _run_health_job() -> str:
    from kb.analytics.health import render_health_summary

    return render_health_summary()


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
    "decay": JobDefinition(
        spec=JobSpec(
            name="decay",
            schedule="0 3 * * *",
            description="Aplicar decaimento de confiança e marcar claims stale.",
            category=classify_job_command("decay"),
        ),
        handler=_run_decay_job,
    ),
    "contradiction-check": JobDefinition(
        spec=JobSpec(
            name="contradiction-check",
            schedule="0 4 * * *",
            description="Detectar possíveis contradições e marcar claims como disputed.",
            category=classify_job_command("contradiction-check"),
        ),
        handler=_run_contradiction_check_job,
    ),
    "index-refresh": JobDefinition(
        spec=JobSpec(
            name="index-refresh",
            schedule="0 5 * * *",
            description="Regerar índice canônico da wiki (_index.md).",
            category=classify_job_command("index-refresh"),
        ),
        handler=_run_index_refresh_job,
    ),
    "health": JobDefinition(
        spec=JobSpec(
            name="health",
            schedule="30 5 * * *",
            description="Gerar relatório de saúde do estado (stale/disputed/confiança).",
            category=classify_job_command("health"),
        ),
        handler=_run_health_job,
    ),
}


def get_job_catalog() -> dict[str, JobSpec]:
    return {name: definition.spec for name, definition in _JOB_DEFINITIONS.items()}


def list_jobs() -> list[JobSpec]:
    return [definition.spec for definition in _JOB_DEFINITIONS.values()]


def get_jobs_list_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    health_extra = ""
    try:
        from kb.analytics.health import get_health_summary

        health = get_health_summary()
        health_extra = (
            f"stale={health.get('stale_pct', 0)}% | "
            f"disputed={health.get('disputed_pct', 0)}%"
        )
    except Exception:
        health_extra = "snapshot indisponível"

    for spec in list_jobs():
        extra = ""
        if spec.name == "health":
            extra = health_extra
        rows.append(
            {
                "name": spec.name,
                "schedule": spec.schedule,
                "description": spec.description,
                "extra": extra,
            }
        )
    return rows


def get_recommended_cron_chain() -> list[dict[str, str]]:
    return [
        {
            "name": "decay",
            "schedule": "0 3 * * *",
            "purpose": "Aplicar decaimento e marcar stale.",
        },
        {
            "name": "contradiction-check",
            "schedule": "10 3 * * *",
            "purpose": "Detectar conflitos e marcar disputed.",
        },
        {
            "name": "index-refresh",
            "schedule": "20 3 * * *",
            "purpose": "Regerar _index.md da wiki.",
        },
        {
            "name": "health",
            "schedule": "30 3 * * *",
            "purpose": "Emitir snapshot de saúde do estado.",
        },
    ]


def run_health_gate(
    stale_max_pct: float | None = None,
    disputed_max_pct: float | None = None,
) -> tuple[int, str]:
    from kb.analytics.health import evaluate_health_thresholds, get_health_summary

    summary = get_health_summary()
    ok, violations = evaluate_health_thresholds(
        summary,
        stale_max_pct=stale_max_pct,
        disputed_max_pct=disputed_max_pct,
    )
    if ok:
        return 0, "health gate OK"
    return 1, f"threshold_violation: {'; '.join(violations)}"


def build_operational_cron_lines(
    executable: str = "kb",
    stale_max_pct: float | None = None,
    disputed_max_pct: float | None = None,
) -> list[str]:
    commands: dict[str, str] = {
        "decay": f"{executable} jobs run decay",
        "contradiction-check": f"{executable} jobs run contradiction-check",
        "index-refresh": f"{executable} jobs run index-refresh",
        "health": f"{executable} jobs run health",
    }
    if stale_max_pct is not None:
        commands["health"] += f" --stale-max-pct {stale_max_pct}"
    if disputed_max_pct is not None:
        commands["health"] += f" --disputed-max-pct {disputed_max_pct}"

    lines: list[str] = []
    for item in get_recommended_cron_chain():
        lines.append(f"{item['schedule']} {commands[item['name']]}")
    return lines


def run_job(
    name: str,
    *,
    stale_max_pct: float | None = None,
    disputed_max_pct: float | None = None,
) -> str:
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

        if normalized == "health" and (
            stale_max_pct is not None or disputed_max_pct is not None
        ):
            from kb.analytics.health import (
                evaluate_health_thresholds,
                get_health_summary,
            )

            summary = get_health_summary()
            ok, violations = evaluate_health_thresholds(
                summary,
                stale_max_pct=stale_max_pct,
                disputed_max_pct=disputed_max_pct,
            )
            if not ok:
                exit_code = 1
                detail = "; ".join(violations)
                output = f"{output}\n- threshold_violation: {detail}"
                raise HealthGateError(output)

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
