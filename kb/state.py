"""Persistência leve para manifesto, knowledge e learnings."""

from __future__ import annotations

import json
import re
from pathlib import Path

from kb.config import KNOWLEDGE_PATH, LEARNINGS_PATH, MANIFEST_PATH, STATE_DIR

TEXT_SOURCE_EXTENSIONS = {".md", ".markdown", ".txt", ".rst"}


def ensure_state_dirs() -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)


def _read_json(path: Path, default):
    ensure_state_dirs()
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload) -> None:
    ensure_state_dirs()
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def normalize_source_path(source_path: Path | str) -> str:
    from kb.config import RAW_DIR

    path = Path(source_path)
    if not path.is_absolute():
        return str(path)
    try:
        return str(path.resolve().relative_to(RAW_DIR.resolve()))
    except ValueError:
        return str(path)


def load_manifest() -> list[dict]:
    return _read_json(MANIFEST_PATH, [])


def save_manifest(entries: list[dict]) -> None:
    _write_json(MANIFEST_PATH, entries)


def record_ingest(source_path: Path, kind: str = "raw") -> dict:
    entries = load_manifest()
    entry = {
        "source": normalize_source_path(source_path),
        "kind": kind,
        "status": "ingested",
    }
    entries = [
        item
        for item in entries
        if normalize_source_path(item.get("source", "")) != entry["source"]
    ]
    entries.append(entry)
    save_manifest(entries)
    return entry


def mark_compiled(
    source_path: Path, article_path: Path, summary_path: Path, topic: str, title: str
) -> dict:
    entries = load_manifest()
    compiled_entry = {
        "source": normalize_source_path(source_path),
        "kind": "raw",
        "status": "compiled",
        "article": str(article_path),
        "summary": str(summary_path),
        "topic": topic,
        "title": title,
    }
    entries = [
        item
        for item in entries
        if normalize_source_path(item.get("source", "")) != compiled_entry["source"]
    ]
    entries.append(compiled_entry)
    save_manifest(entries)
    return compiled_entry


def find_compiled_entry(source_path: Path | str) -> dict | None:
    normalized_source = normalize_source_path(source_path)
    for entry in load_manifest():
        if normalize_source_path(entry.get("source", "")) == normalized_source:
            return entry
    return None


def load_knowledge() -> list[dict]:
    return _read_json(KNOWLEDGE_PATH, [])


def save_knowledge(entries: list[dict]) -> None:
    _write_json(KNOWLEDGE_PATH, entries)


def upsert_knowledge(entry: dict) -> dict:
    entries = load_knowledge()
    source = entry.get("source")
    key = (
        normalize_source_path(source)
        if source is not None
        else entry.get("article") or entry.get("title")
    )

    if key is None:
        entries.append(entry)
        save_knowledge(entries)
        return entry

    filtered = []
    for item in entries:
        item_source = item.get("source")
        item_key = (
            normalize_source_path(item_source)
            if item_source is not None
            else item.get("article") or item.get("title")
        )
        if item_key != key:
            filtered.append(item)
    filtered.append(entry)
    save_knowledge(filtered)
    return entry


def load_learnings() -> list[dict]:
    return _read_json(LEARNINGS_PATH, [])


def save_learnings(entries: list[dict]) -> None:
    _write_json(LEARNINGS_PATH, entries)


def add_learning(kind: str, content: str, source: str = "system") -> dict:
    entries = load_learnings()
    entry = {"kind": kind, "content": content, "source": source}
    entries.append(entry)
    save_learnings(entries)
    return entry


def extract_summary(markdown: str, max_chars: int = 320) -> str:
    """Extrai um resumo curto do markdown compilado."""
    text = markdown
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            text = parts[2]

    lines = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        lines.append(line)

    summary = " ".join(lines)
    summary = re.sub(r"\s+", " ", summary).strip()
    if len(summary) <= max_chars:
        return summary
    return summary[: max_chars - 1].rstrip() + "…"


def search_structured_entries(
    entries: list[dict], query: str, top_k: int = 5
) -> list[dict]:
    terms = set(query.lower().split())
    scored: list[tuple[int, dict]] = []

    for entry in entries:
        blob = json.dumps(entry, ensure_ascii=False).lower()
        score = sum(blob.count(term) for term in terms)
        if score > 0:
            scored.append((score, entry))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [entry for _, entry in scored[:top_k]]


def discover_raw_sources(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file()
        and path.suffix.lower() in TEXT_SOURCE_EXTENSIONS
        and path.name != "metadata.json"
    )
