"""Ingestão de URLs: baixa HTML, converte para Markdown, salva em raw/."""

import ipaddress
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import kb.config as _config
from kb.git import commit

try:
    import requests
    import html2text as _html2text
except ImportError:  # pragma: no cover
    requests = None  # type: ignore[assignment]
    _html2text = None  # type: ignore[assignment]


class WebIngestError(Exception):
    pass


_BLOCKED_SCHEMES = {"file", "ftp", "data", "javascript"}

_BLOCKED_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
]


def _require_deps() -> None:
    if requests is None or _html2text is None:
        raise WebIngestError(
            "Dependências web não instaladas. Execute: pip install -e .[web]"
        )


def _validate_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise WebIngestError(
            f"Esquema não permitido: {parsed.scheme or 'vazio'}. Use http ou https."
        )
    if not parsed.hostname:
        raise WebIngestError("URL sem hostname.")
    try:
        import socket

        resolved = socket.getaddrinfo(
            parsed.hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM
        )
    except socket.gaierror as exc:
        raise WebIngestError(
            f"Não foi possível resolver hostname: {parsed.hostname}"
        ) from exc
    seen = set()
    for family, _, _, _, sockaddr in resolved:
        addr_str = sockaddr[0]
        if addr_str in seen:
            continue
        seen.add(addr_str)
        try:
            addr = ipaddress.ip_address(addr_str)
        except ValueError:
            continue
        for network in _BLOCKED_NETWORKS:
            if addr in network:
                raise WebIngestError(
                    f"URL aponta para endereço de rede interna ({addr}). Não permitido."
                )


def _extract_title(html: str) -> str | None:
    match = re.search(r"<title[^>]*>([^<]+)</title>", html, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None


def _slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")[:80]


def _yaml_quote(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _url_fallback_slug(url: str) -> str:
    clean = re.sub(r"^https?://", "", url)
    return _slugify(clean)[:40] or "page"


def ingest_url(url: str, no_commit: bool = True) -> Path:
    """Baixa URL, converte para Markdown e salva em raw/."""
    _require_deps()
    _validate_url(url)

    try:
        response = requests.get(
            url,
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        response.raise_for_status()
    except requests.Timeout as exc:
        raise WebIngestError(f"Timeout ao acessar {url}") from exc
    except requests.HTTPError as exc:
        raise WebIngestError(str(exc)) from exc
    except requests.RequestException as exc:
        raise WebIngestError(f"Erro de rede: {exc}") from exc

    html = response.text
    title = _extract_title(html) or ""

    slug = (_slugify(title) if title else "") or _url_fallback_slug(url)

    h = _html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = True
    h.body_width = 0
    markdown_body = h.handle(html)

    ingested_at = datetime.now(timezone.utc).isoformat()
    content = (
        f"---\n"
        f"title: {_yaml_quote(title or slug)}\n"
        f"source_url: {url}\n"
        f"ingested_at: {ingested_at}\n"
        f"---\n\n"
        f"{markdown_body}"
    )

    raw_dir = _config.RAW_DIR
    raw_dir.mkdir(parents=True, exist_ok=True)
    out = raw_dir / f"{slug}.md"
    out.write_text(content, encoding="utf-8")

    if not no_commit:
        commit(f"feat(raw): ingest url — {(title or url)[:50]}", [out])

    return out
