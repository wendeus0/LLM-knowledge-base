import math
import re
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path

from kb.analytics.health import get_health_summary

_WIKILINK_RE = re.compile(r"\[\[(.*?)\]\]")
_VERSIONED_RE = re.compile(r"\.v(\d+)\.\d{8}T\d{6}Z\.md$")


def _versioned_backup(dest: Path) -> None:
    prefix = dest.stem + ".v"
    max_ver = 0
    for sibling in dest.parent.iterdir():
        if not sibling.name.startswith(prefix):
            continue
        m = _VERSIONED_RE.search(sibling.name)
        if m:
            max_ver = max(max_ver, int(m.group(1)))
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_name = f"{dest.stem}.v{max_ver + 1}.{ts}.md"
    dest.rename(dest.parent / backup_name)


def _normalize_link(link: str) -> str:
    return re.sub(r"\s+", "-", link.strip().lower())


def find_orphans(wiki_dir: Path) -> list[Path]:
    """Retorna artigos sem backlinks na wiki."""
    if not wiki_dir.exists():
        return []
    backlink_sources = [p for p in wiki_dir.rglob("*.md") if not p.is_symlink()]
    all_md = [p for p in backlink_sources if p.name != "_index.md"]
    linked = set()
    for p in backlink_sources:
        current = _normalize_link(p.stem)
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for match in _WIKILINK_RE.finditer(text):
            target = _normalize_link(match.group(1))
            if target != current:
                linked.add(target)
    return [p for p in all_md if _normalize_link(p.stem) not in linked]


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
    if threshold_days <= 0:
        return []
    return find_by_age(wiki_dir, math.ceil(threshold_days))


def collect_candidates(
    wiki_dir: Path,
    *,
    stale: bool = False,
    older_than: int | None = None,
) -> list[dict]:
    """Coleta candidatos a archive segundo critérios ativos."""
    if not wiki_dir.is_dir() or not any(wiki_dir.iterdir()):
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
            threshold_days = summary.get("stale_days", 0.0)
        except (KeyError, TypeError, ValueError, OSError):
            threshold_days = 0.0
        if threshold_days > 0:
            for p in find_stale(wiki_dir, threshold_days):
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
    if not dry_run:
        archive_dir.mkdir(parents=True, exist_ok=True)
    for c in candidates:
        src: Path = c["source"]
        dest = c.get("dest")
        if dest is None:
            continue
        try:
            resolved_dest = dest.resolve()
            resolved_archive = archive_dir.resolve()
            if not (
                resolved_dest == resolved_archive
                or resolved_dest.is_relative_to(resolved_archive)
            ):
                log.append(
                    {
                        "source": str(src),
                        "dest": str(dest),
                        "action": "error",
                        "detail": "destino fora do diretório de archive",
                    }
                )
                continue
        except (OSError, ValueError) as exc:
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
            if dest.exists():
                _versioned_backup(dest)
            shutil.move(str(src), str(dest))
            log.append({"source": str(src), "dest": str(dest), "action": "moved"})
        except (OSError, ValueError) as exc:
            log.append(
                {
                    "source": str(src),
                    "dest": str(dest),
                    "action": "error",
                    "detail": str(exc),
                }
            )
    return log
