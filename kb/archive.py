import math
import re
import shutil
import time
from datetime import UTC, datetime
from pathlib import Path

from kb.analytics.health import get_health_summary

_WIKILINK_RE = re.compile(r"\[\[(.*?)\]\]")
_VERSIONED_RE = re.compile(r"\.v(\d+)\.\d{8}T\d{6}Z\.md$")


def _versioned_backup(dest: Path) -> Path:
    prefix = dest.stem + ".v"
    max_ver = 0
    for sibling in dest.parent.iterdir():
        if not sibling.name.startswith(prefix):
            continue
        m = _VERSIONED_RE.search(sibling.name)
        if m:
            max_ver = max(max_ver, int(m.group(1)))
    ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    backup_name = f"{dest.stem}.v{max_ver + 1}.{ts}.md"
    backup_path = dest.parent / backup_name
    dest.rename(backup_path)
    return backup_path


def _normalize_link(link: str) -> str:
    return re.sub(r"\s+", "-", link.strip().lower())


def find_orphans(wiki_dir: Path) -> list[Path]:
    """Retorna artigos sem backlinks na wiki.

    A identidade é o path relativo, não o stem: com stem, linkar
    `cybersecurity/honeycomb` fazia `honeycomb` da raiz parecer linkado e
    escapar do arquivamento. Wikilink ambíguo marca **todos** os candidatos —
    arquivar algo que talvez esteja linkado é o erro caro.
    """
    from kb.graph import build_link_index, resolve_wikilink_all

    if not wiki_dir.exists():
        return []
    from kb.fsutil import iter_articles

    backlink_sources = list(iter_articles(wiki_dir))
    all_md = backlink_sources

    def identidade(path: Path) -> str:
        return path.relative_to(wiki_dir).with_suffix("").as_posix()

    index = build_link_index(wiki_dir)
    linked = set()
    for p in backlink_sources:
        current = identidade(p)
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for match in _WIKILINK_RE.finditer(text):
            for alvo in resolve_wikilink_all(match.group(1), wiki_dir, index):
                chave = identidade(alvo)
                if chave != current:
                    linked.add(chave)
    return [p for p in all_md if identidade(p) not in linked]


def find_by_age(wiki_dir: Path, days: int) -> list[Path]:
    """Retorna artigos com mtime anterior ao cutoff de dias."""
    if not wiki_dir.exists():
        return []
    from kb.fsutil import iter_articles

    cutoff = time.time() - (days * 86400)
    result = []
    for p in iter_articles(wiki_dir):
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
            backup = None
            if dest.exists():
                if dest.is_dir():
                    raise ValueError(f"destino é um diretório: {dest}")
                backup = _versioned_backup(dest)
            shutil.move(str(src), str(dest))
            entry = {"source": str(src), "dest": str(dest), "action": "moved"}
            if backup is not None:
                entry["backup"] = str(backup)
            log.append(entry)
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
