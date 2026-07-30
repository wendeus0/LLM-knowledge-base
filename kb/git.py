"""Git helper — commit explícito para writes no corpus.

O repositório alvo é o que **contém o arquivo**, não o do código. Antes isso
era resolvido contra `ROOT`, e com `KB_DATA_DIR` apontando para um vault fora
do repo — o setup recomendado pelo próprio `.env.example` — `relative_to(ROOT)`
levantava ValueError, o path era descartado e `commit()` devolvia True sem
fazer nada. `kb compile --commit` nunca versionou o vault, em silêncio.
"""

import subprocess
import sys
from collections import defaultdict
from pathlib import Path


def _error_detail(exc):
    stderr = getattr(exc, "stderr", None)
    if isinstance(stderr, bytes):
        detail = stderr.decode("utf-8", errors="replace").strip()
    elif stderr:
        detail = str(stderr).strip()
    else:
        detail = str(exc).strip()
    return detail


def is_git_repo(root) -> bool:
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


def repo_root_for(path: Path) -> Path | None:
    """Raiz do repositório que contém `path`, ou None se não houver."""
    anchor = path if path.is_dir() else path.parent
    try:
        result = subprocess.run(
            ["git", "-C", str(anchor), "rev-parse", "--show-toplevel"],
            check=False,
            capture_output=True,
            text=True,
        )
    except Exception:
        return None
    if result.returncode != 0:
        return None
    top = result.stdout.strip()
    return Path(top) if top else None


def _run(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


def _commit_in(repo: Path, message: str, relative_paths: list[str]) -> None:
    _run(repo, "add", *relative_paths)
    staged = subprocess.run(
        ["git", "-C", str(repo), "diff", "--cached", "--quiet"], capture_output=True
    )
    if staged.returncode != 0:  # há mudanças staged
        _run(repo, "commit", "-m", message)


def commit(message: str, paths: list[Path], enabled: bool = True) -> bool:
    """Stage e commita cada path no repositório que o contém.

    Paths de repositórios diferentes geram um commit em cada um. Path fora de
    qualquer repositório é avisado — não silenciado.
    """
    if not enabled:
        return True

    by_repo: dict[Path, list[str]] = defaultdict(list)
    orphans: list[Path] = []

    for path in paths:
        repo = repo_root_for(Path(path))
        if repo is None:
            orphans.append(Path(path))
            continue
        try:
            by_repo[repo].append(str(Path(path).resolve().relative_to(repo.resolve())))
        except ValueError:
            orphans.append(Path(path))

    if orphans:
        nomes = ", ".join(str(p) for p in orphans)
        print(
            f"[kb] aviso: commit ignorado — fora de repositório git: {nomes}. "
            "Rode `git init` no diretório do corpus para versionar.",
            file=sys.stderr,
        )

    ok = not orphans
    for repo, relative_paths in by_repo.items():
        try:
            _commit_in(repo, message, relative_paths)
        except Exception as exc:
            print(
                f"[kb] aviso: commit falhou em {repo}: {_error_detail(exc)}",
                file=sys.stderr,
            )
            ok = False

    return ok
