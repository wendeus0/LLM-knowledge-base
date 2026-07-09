"""Diff da wiki via git."""

import subprocess

from rich.markup import escape

from kb.git import is_git_repo


class DiffError(Exception):
    """Erro controlado ao calcular diff da wiki."""


def _paths():
    import kb.config as _config

    root = _config.DATA_DIR.expanduser()
    wiki_dir = _config.WIKI_DIR.expanduser()
    try:
        wiki_rel = wiki_dir.relative_to(root)
    except ValueError as exc:
        raise DiffError(f"wiki não está dentro de KB_DATA_DIR: {wiki_dir}") from exc
    return root, wiki_rel


def wiki_diff(stat=False, since=None):
    """Retorna o diff git da wiki em relação ao commit/ref informado."""
    root, wiki_rel = _paths()
    if not is_git_repo(root):
        raise DiffError(f"KB_DATA_DIR não é um repositório git: {root}")

    args = ["git", "-C", str(root), "diff"]
    if stat:
        args.append("--stat")
    args.append(since or "HEAD")
    args.extend(["--", str(wiki_rel)])

    result = subprocess.run(args, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "git diff falhou").strip()
        raise DiffError(detail)
    return result.stdout


def render_diff(output, console):
    """Imprime diff com cores simples por linha usando Rich."""
    for line in output.splitlines():
        safe = escape(line)
        if (
            line.startswith("@@")
            or line.startswith("diff ")
            or line.startswith("index ")
            or line.startswith("+++")
            or line.startswith("---")
        ):
            console.print(f"[dim cyan]{safe}[/]")
        elif line.startswith("+"):
            console.print(f"[green]{safe}[/]")
        elif line.startswith("-"):
            console.print(f"[red]{safe}[/]")
        else:
            console.print(safe)
