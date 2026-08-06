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
    from kb.config import DATA_DIR, RAW_DIR

    path = Path(source_path)
    if not path.is_absolute():
        return str(path)
    for base in (RAW_DIR, DATA_DIR):
        try:
            return str(path.resolve().relative_to(Path(base).resolve()))
        except ValueError:
            continue
    return str(path)


def _normalize_article_path(article_path: Path | str) -> str:
    from kb.config import WIKI_DIR

    path = Path(article_path)
    if not path.is_absolute():
        return str(path)
    try:
        return str(path.resolve().relative_to(Path(WIKI_DIR).resolve()))
    except ValueError:
        return str(path)


def entry_provenance(entry: dict) -> str:
    """Entradas legadas (compile/ingest) não carregam o campo — são `compile`."""
    return entry.get("provenance") or "compile"


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


def record_backfill(
    source_path: Path | str,
    article_path: Path | str,
    book: str | None,
    provenance: str,
) -> dict:
    """Materializa proveniência reconstruída (028 B1) — upsert pela fonte."""
    entries = load_manifest()
    entry = {
        "source": normalize_source_path(source_path),
        "kind": "raw",
        "status": "compiled",
        "article": _normalize_article_path(article_path),
        "book": book,
        "provenance": provenance,
    }
    entries = [
        item
        for item in entries
        if not (
            normalize_source_path(item.get("source", "")) == entry["source"]
            and (
                not item.get("article")
                or _normalize_article_path(item["article"]) == entry["article"]
            )
        )
    ]
    entries.append(entry)
    save_manifest(entries)
    return entry


def record_backfill_many(links) -> int:
    """Versão em lote do `record_backfill` — uma leitura e uma escrita.

    Upsert por (fonte, artigo): duas ligações vivas para a mesma fonte — o caso
    que o dedup precisa enxergar — coexistem em vez de a última engolir a
    anterior.
    """
    entries = load_manifest()
    novos = []
    chaves = set()
    for source_path, article_path, book, provenance in links:
        entry = {
            "source": normalize_source_path(source_path),
            "kind": "raw",
            "status": "compiled",
            "article": _normalize_article_path(article_path),
            "book": book,
            "provenance": provenance,
        }
        novos.append(entry)
        chaves.add((entry["source"], entry["article"]))
    mantidos = [
        item
        for item in entries
        if (
            normalize_source_path(item.get("source", "")),
            _normalize_article_path(item.get("article", "")) if item.get("article") else "",
        )
        not in chaves
    ]
    save_manifest(mantidos + novos)
    return len(novos)


def _entries_for_article(entries: list[dict], article_path: Path | str) -> list[dict]:
    alvo = _normalize_article_path(article_path)
    return [
        entry
        for entry in entries
        if entry.get("article") and _normalize_article_path(entry["article"]) == alvo
    ]


def mark_archived(article_path: Path | str) -> int:
    """Marca `status: archived` nas entradas do artigo; devolve quantas mudaram.

    Sem isto, arquivar um artigo deixa o guard de recompile apontando para um
    path inexistente em silêncio.
    """
    entries = load_manifest()
    atingidas = _entries_for_article(entries, article_path)
    for entry in atingidas:
        entry["status"] = "archived"
    if atingidas:
        save_manifest(entries)
    return len(atingidas)


def update_article_path(old_path: Path | str, new_path: Path | str) -> int:
    """Atualiza o path do artigo nas entradas correspondentes (move/reagrupamento)."""
    entries = load_manifest()
    atingidas = _entries_for_article(entries, old_path)
    for entry in atingidas:
        entry["article"] = _normalize_article_path(new_path)
    if atingidas:
        save_manifest(entries)
    return len(atingidas)


def find_compiled_entry(source_path: Path | str) -> dict | None:
    normalized_source = normalize_source_path(source_path)
    for entry in load_manifest():
        if entry.get("status") == "archived":
            # Entrada arquivada não pode guiar recompile: o path de artigo dela
            # não existe mais, e reusá-lo recriaria o que o dedup removeu.
            continue
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
