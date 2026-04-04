"""Catálogo simples de jobs agendáveis do kb."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class JobSpec:
    name: str
    schedule: str
    description: str


JOBS = [
    JobSpec("compile", "0 9 * * *", "Compilar novos documentos de raw/ para wiki/ e atualizar o índice."),
    JobSpec("lint", "0 8 * * 0", "Auditar a wiki e relatar inconsistências."),
    JobSpec("review", "0 18 * * 5", "Executar heal amostrado para manutenção da wiki."),
]


def list_jobs() -> list[JobSpec]:
    return JOBS


def run_job(name: str) -> str:
    normalized = name.strip().lower()

    if normalized == "compile":
        from kb.compile import compile_file, discover_compile_targets, update_index

        targets = discover_compile_targets()
        for target in targets:
            compile_file(target)
        update_index()
        return f"Job compile executado ({len(targets)} alvo(s))."

    if normalized == "lint":
        from kb.lint import lint_wiki

        lint_wiki()
        return "Job lint executado."

    if normalized == "review":
        from kb.heal import heal

        processed = heal(3)
        return f"Job review executado ({len(processed)} item(ns) processado(s))."

    available = ", ".join(job.name for job in JOBS)
    raise ValueError(f"Job desconhecido: {name}. Disponíveis: {available}")
