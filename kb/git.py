"""Git helper — commit explícito para writes no corpus."""

import subprocess
import sys
from pathlib import Path

from kb.config import ROOT


def _run(*args: str) -> None:
    subprocess.run(["git", "-C", str(ROOT), *args], check=True, capture_output=True)


def _error_detail(exc):
    stderr = getattr(exc, "stderr", None)
    if isinstance(stderr, bytes):
        detail = stderr.decode("utf-8", errors="replace").strip()
    elif stderr:
        detail = str(stderr).strip()
    else:
        detail = str(exc).strip()
    return detail


def is_git_repo(root=ROOT) -> bool:
    """Retorna True quando root está dentro de um repositório git."""
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--is-inside-work-tree"],
            check=False,
            capture_output=True,
            text=True,
        )
        return result.returncode == 0 and result.stdout.strip() == "true"
    except Exception:
        return False


def commit(message: str, paths: list[Path], enabled: bool = True) -> bool:
    """Stage os paths e commita. Silencioso se não há mudanças."""
    if not enabled:
        return True
    try:
        rel = []
        for p in paths:
            try:
                rel.append(str(p.relative_to(ROOT)))
            except ValueError:
                continue
        if not rel:
            return True
        _run("add", *rel)
        result = subprocess.run(
            ["git", "-C", str(ROOT), "diff", "--cached", "--quiet"],
            capture_output=True,
        )
        if result.returncode != 0:  # há mudanças staged
            _run("commit", "-m", message)
        return True
    except Exception as exc:
        print(f"[kb] aviso: commit falhou: {_error_detail(exc)}", file=sys.stderr)
        return False
