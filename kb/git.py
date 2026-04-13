"""Git helper — commit explícito para writes no corpus."""

import subprocess
from pathlib import Path
from kb.config import ROOT


def _run(*args: str) -> None:
    subprocess.run(["git", "-C", str(ROOT), *args], check=True, capture_output=True)


def commit(message: str, paths: list[Path], enabled: bool = True) -> None:
    """Stage os paths e commita. Silencioso se não há mudanças."""
    if not enabled:
        return
    try:
        rel = [str(p.relative_to(ROOT)) for p in paths]
        _run("add", *rel)
        result = subprocess.run(
            ["git", "-C", str(ROOT), "diff", "--cached", "--quiet"],
            capture_output=True,
        )
        if result.returncode != 0:  # há mudanças staged
            _run("commit", "-m", message)
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass  # sem mudanças ou git não disponível — ignora
