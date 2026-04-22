"""Descoberta automatizada de artigos/papers e ingestão no kb."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote_plus
import xml.etree.ElementTree as ET

from kb.compile import compile_file
from kb.config import API_KEY, STATE_DIR
from kb.web_ingest import WebIngestError, ingest_url

try:
    import requests
except ImportError:  # pragma: no cover
    requests = None  # type: ignore[assignment]


SEEN_URLS_PATH = STATE_DIR / "discovery_seen_urls.json"
DEFAULT_QUERIES = [
    "llm agents",
    "retrieval augmented generation",
    "model evaluation",
]


@dataclass(frozen=True)
class DiscoveryItem:
    title: str
    url: str
    source: str
    published_at: str


def _require_requests() -> None:
    if requests is None:
        raise RuntimeError("Dependência ausente: instale kb com extra web (`pip install -e .[web]`).")


def _load_seen_urls() -> set[str]:
    if not SEEN_URLS_PATH.exists():
        return set()
    try:
        payload = json.loads(SEEN_URLS_PATH.read_text(encoding="utf-8"))
    except Exception:
        return set()
    urls = payload.get("urls", []) if isinstance(payload, dict) else []
    return {u for u in urls if isinstance(u, str)}


def _save_seen_urls(urls: set[str]) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "urls": sorted(urls),
    }
    SEEN_URLS_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def discover_arxiv(query: str, max_results: int = 3) -> list[DiscoveryItem]:
    _require_requests()
    endpoint = (
        "https://export.arxiv.org/api/query?"
        f"search_query=all:{quote_plus(query)}&start=0&max_results={max_results}&sortBy=submittedDate&sortOrder=descending"
    )
    response = requests.get(endpoint, timeout=20, headers={"User-Agent": "kb-discovery/1.0"})
    response.raise_for_status()

    root = ET.fromstring(response.text)
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    items: list[DiscoveryItem] = []
    for entry in root.findall("atom:entry", ns):
        title = _clean_text(entry.findtext("atom:title", default="", namespaces=ns))
        link = _clean_text(entry.findtext("atom:id", default="", namespaces=ns))
        published = _clean_text(entry.findtext("atom:published", default="", namespaces=ns))
        if not title or not link:
            continue
        items.append(
            DiscoveryItem(
                title=title,
                url=link,
                source="arxiv",
                published_at=published,
            )
        )
    return items


def discover_articles_google_news(query: str, max_results: int = 3) -> list[DiscoveryItem]:
    _require_requests()
    endpoint = (
        "https://news.google.com/rss/search?"
        f"q={quote_plus(query)}&hl=en-US&gl=US&ceid=US:en"
    )
    response = requests.get(endpoint, timeout=20, headers={"User-Agent": "kb-discovery/1.0"})
    response.raise_for_status()

    root = ET.fromstring(response.text)
    items: list[DiscoveryItem] = []
    for node in root.findall("./channel/item")[:max_results]:
        title = _clean_text(node.findtext("title", default=""))
        link = _clean_text(node.findtext("link", default=""))
        published = _clean_text(node.findtext("pubDate", default=""))
        if not title or not link:
            continue
        items.append(
            DiscoveryItem(
                title=title,
                url=link,
                source="google-news",
                published_at=published,
            )
        )
    return items


def run_scheduled_discovery(
    queries: list[str] | None = None,
    max_per_source: int = 2,
    compile_after_ingest: bool = True,
    allow_sensitive: bool = False,
    no_commit: bool = True,
) -> dict:
    queries = [q.strip() for q in (queries or DEFAULT_QUERIES) if q.strip()]
    seen = _load_seen_urls()

    discovered = 0
    ingested = 0
    compiled = 0
    skipped_seen = 0
    failures: list[str] = []
    created_files: list[str] = []

    for query in queries:
        for discover_fn in (discover_arxiv, discover_articles_google_news):
            try:
                items = discover_fn(query, max_results=max_per_source)
            except Exception as exc:
                failures.append(f"discover:{discover_fn.__name__}:{query}: {exc}")
                continue

            for item in items:
                discovered += 1
                if item.url in seen:
                    skipped_seen += 1
                    continue

                try:
                    raw_path = ingest_url(item.url, no_commit=no_commit)
                    ingested += 1
                    created_files.append(str(raw_path))
                except WebIngestError as exc:
                    failures.append(f"ingest:{item.url}: {exc}")
                    seen.add(item.url)
                    continue

                if compile_after_ingest and API_KEY:
                    try:
                        wiki_path = compile_file(
                            raw_path,
                            allow_sensitive=allow_sensitive,
                            no_commit=no_commit,
                        )
                        compiled += 1
                        created_files.append(str(wiki_path))
                    except Exception as exc:
                        failures.append(f"compile:{raw_path.name}: {exc}")

                seen.add(item.url)

    _save_seen_urls(seen)

    return {
        "queries": queries,
        "discovered": discovered,
        "ingested": ingested,
        "compiled": compiled,
        "skipped_seen": skipped_seen,
        "failures": failures,
        "created_files": created_files,
        "compiled_enabled": bool(API_KEY and compile_after_ingest),
        "seen_urls_path": str(SEEN_URLS_PATH),
    }
