import re
import shutil
import time
from pathlib import Path

from kb.analytics.health import get_health_summary

_WIKILINK_RE = re.compile(r"\[\[(.*?)\]\]")


def find_orphans(wiki_dir: Path) -> list[Path]:
    """Retorna artigos sem backlinks na wiki."""
    if not wiki_dir.exists():
        return []
    all_md = [p for p in wiki_dir.rglob("*.md") if not p.is_symlink()]
    linked = set()
    for p in all_md:
        text = p.read_text(encoding="utf-8")
        for match in _WIKILINK_RE.finditer(text):
            link = match.group(1).strip()
            linked.add(link)
    return [p for p in all_md if p.stem not in linked]


def find_by_age(wiki_dir: Path, days: int) -> list[Path]:
    """Retorna artigos com mtime anterior ao cutoff de dias."""
    if not wiki_dir.exists():
        return []
    cutoff = time.time() - (days * 86400)
    result = []
    for p in wiki_dir.rglob("*.md"):
        if p.is_symlink():
            continue
        try:
            if p.stat().st_mtime < cutoff:
                result.append(p)
        except OSError:
            continue
    return result


def find_stale(wiki_dir: Path, threshold_days: float) -> list[Path]:
    """Retorna artigos considerados stale usando threshold em dias."""
    return find_by_age(wiki_dir, int(threshold_days))


def collect_candidates(
    wiki_dir: Path,
    *,
    stale: bool = False,
    older_than: int | None = None,
) -> list[dict]:
    """Coleta candidatos a archive segundo critérios ativos."""
    if not wiki_dir.exists() or not any(wiki_dir.iterdir()):
        raise ValueError("wiki directory is empty or does not exist")
    if older_than is not None and older_than <= 0:
        raise ValueError("older_than must be a positive integer")

    candidates = []
    seen = set()

    if not stale and older_than is None:
        for p in find_orphans(wiki_dir):
            if p not in seen:
                seen.add(p)
                candidates.append({"source": p, "reason": "orphan", "dest": None})
        return candidates

    if older_than is not None:
        for p in find_by_age(wiki_dir, older_than):
            if p not in seen:
                seen.add(p)
                candidates.append({"source": p, "reason": "older-than", "dest": None})

    if stale:
        try:
            summary = get_health_summary()
            threshold = summary.get("stale_pct", 0.0)
        except Exception:
            threshold = 0.0
        for p in find_stale(wiki_dir, threshold):
            if p not in seen:
                seen.add(p)
                candidates.append({"source": p, "reason": "stale", "dest": None})

    return candidates


def move_to_archive(
    candidates: list[dict],
    archive_dir: Path,
    *,
    dry_run: bool = False,
) -> list[dict]:
    """Move candidatos para archive/. Retorna log da operação."""
    log = []
    archive_dir.mkdir(parents=True, exist_ok=True)
    for c in candidates:
        src: Path = c["source"]
        dest = c.get("dest")
        if dest is None:
            continue
        try:
            resolved_dest = dest.resolve()
            resolved_archive = archive_dir.resolve()
            if not str(resolved_dest).startswith(str(resolved_archive) + "/"):
                log.append(
                    {
                        "source": str(src),
                        "dest": str(dest),
                        "action": "error",
                        "detail": "destino fora do diretório de archive",
                    }
                )
                continue
        except Exception as exc:
            log.append(
                {
                    "source": str(src),
                    "dest": str(dest),
                    "action": "error",
                    "detail": str(exc),
                }
            )
            continue
        if dry_run:
            log.append({"source": str(src), "dest": str(dest), "action": "dry-run"})
            continue
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dest))
            log.append({"source": str(src), "dest": str(dest), "action": "moved"})
        except Exception as exc:
            log.append(
                {
                    "source": str(src),
                    "dest": str(dest),
                    "action": "error",
                    "detail": str(exc),
                }
            )
    return log
