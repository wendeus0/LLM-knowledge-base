from __future__ import annotations

from dataclasses import dataclass
from fnmatch import fnmatch


CODE_PATTERNS = (
    "kb/*.py",
    "kb/**/*.py",
)

DOC_PATTERNS = (
    "docs/handoffs/*.md",
    "features/**/SPEC.md",
)


@dataclass(frozen=True)
class DocGateResult:
    ok: bool
    code_files: list[str]
    doc_files: list[str]
    reason: str


def _match_any(path: str, patterns: tuple[str, ...]) -> bool:
    return any(fnmatch(path, p) for p in patterns)


def evaluate_doc_gate(changed_files: list[str]) -> DocGateResult:
    normalized = sorted({f.strip() for f in changed_files if f and f.strip()})

    code_files = [f for f in normalized if _match_any(f, CODE_PATTERNS)]
    doc_files = [f for f in normalized if _match_any(f, DOC_PATTERNS)]

    if not code_files:
        return DocGateResult(
            ok=True,
            code_files=[],
            doc_files=doc_files,
            reason="Sem mudanças de código no diretório kb/.",
        )

    if doc_files:
        return DocGateResult(
            ok=True,
            code_files=code_files,
            doc_files=doc_files,
            reason="Mudança de código acompanhada por atualização de SPEC ou Handoff.",
        )

    return DocGateResult(
        ok=False,
        code_files=code_files,
        doc_files=[],
        reason=(
            "Mudança de código detectada sem atualização documental. "
            "Inclua ao menos um arquivo em docs/handoffs/*.md ou features/**/SPEC.md."
        ),
    )
