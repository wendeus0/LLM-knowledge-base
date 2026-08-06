"""Utilitários de filesystem."""

import os
import tempfile
from pathlib import Path


def iter_articles(wiki_dir):
    """Artigos vivos da wiki: exclui `_*`, `.*` e symlinks em qualquer nível.

    Mesma semântica de `graph._e_artigo`, centralizada — sete módulos aplicavam
    (ou esqueciam) a convenção cada um do seu jeito.
    """
    wiki_dir = Path(wiki_dir)
    if not wiki_dir.is_dir():
        return
    for path in sorted(wiki_dir.rglob("*.md")):
        if path.is_symlink():
            continue
        rel = path.relative_to(wiki_dir)
        if any(part.startswith(("_", ".")) for part in rel.parts):
            continue
        yield path


def atomic_write_text(path, text):
    """Grava texto em arquivo de forma atômica."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with open(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)
    except BaseException:
        Path(tmp_path).unlink(missing_ok=True)
        raise
