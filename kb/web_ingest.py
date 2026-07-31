"""Ingestão de URLs: baixa HTML, converte para Markdown, salva em raw/."""

import ipaddress
import re
import socket
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse, urlunparse

import kb.config as _config
from kb.git import commit

try:
    import html2text as _html2text
    import requests
except ImportError:  # pragma: no cover
    requests = None  # type: ignore[assignment]
    _html2text = None  # type: ignore[assignment]


class WebIngestError(Exception):
    pass


_ALLOWED_SCHEMES = {"http", "https"}

_BLOCKED_NETWORKS = [
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("100.64.0.0/10"),
    ipaddress.ip_network("198.18.0.0/15"),
    ipaddress.ip_network("224.0.0.0/4"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("::/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
    ipaddress.ip_network("ff00::/8"),
]


def _require_deps() -> None:
    if requests is None or _html2text is None:
        raise WebIngestError(
            "Dependências web não instaladas. Execute: pip install -e .[web]"
        )


def _resolve_and_validate(hostname: str) -> str:
    """Resolve hostname, validates IPs against blocked networks, returns first safe IP."""
    try:
        resolved = socket.getaddrinfo(
            hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM
        )
    except socket.gaierror as exc:
        raise WebIngestError(f"Não foi possível resolver hostname: {hostname}") from exc
    for _fam, _, _, _, sockaddr in resolved:
        addr_str = sockaddr[0]
        try:
            addr = ipaddress.ip_address(addr_str)
            if isinstance(addr, ipaddress.IPv6Address) and addr.ipv4_mapped:
                addr = addr.ipv4_mapped
        except ValueError:
            continue
        for network in _BLOCKED_NETWORKS:
            if addr in network:
                raise WebIngestError(
                    f"URL aponta para endereço de rede interna ({addr}). Não permitido."
                )
        return sockaddr[0]
    raise WebIngestError(f"Sem endereço validado para {hostname}")


def _follow_redirects(url: str, max_hops: int = 5) -> "requests.Response":
    """Follow redirects manually, pinning resolved IP to prevent DNS rebinding.

    This is a partial SSRF mitigation: the hostname is resolved once per hop
    and the connection is made directly to the resolved IP with the original
    Host header preserved. This eliminates the classic DNS rebinding attack
    window between validation and connection.
    """
    for _ in range(max_hops + 1):
        parsed = urlparse(url)
        if parsed.scheme not in _ALLOWED_SCHEMES:
            raise WebIngestError(
                f"Esquema não permitido: {parsed.scheme or 'vazio'}. Use http ou https."
            )
        if not parsed.hostname:
            raise WebIngestError("URL sem hostname.")
        resolved_ip = _resolve_and_validate(parsed.hostname)
        if parsed.scheme == "https":
            pinned_url = url
        elif parsed.hostname != resolved_ip:
            if ":" in resolved_ip and not resolved_ip.startswith("["):
                ip_for_url = f"[{resolved_ip}]"
            else:
                ip_for_url = resolved_ip
            netloc = ip_for_url
            if parsed.port:
                netloc = f"{ip_for_url}:{parsed.port}"
            pinned_url = urlunparse(parsed._replace(netloc=netloc))
        else:
            pinned_url = url
        host_header = parsed.hostname
        if parsed.port:
            host_header = f"{parsed.hostname}:{parsed.port}"
        response = requests.get(
            pinned_url,
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0", "Host": host_header},
            allow_redirects=False,
        )
        if response.status_code in (301, 302, 303, 307, 308):
            location = response.headers.get("Location")
            if not location:
                raise WebIngestError("Redirect sem header Location.")
            url = urljoin(url, location)
            continue
        response.raise_for_status()
        return response
    raise WebIngestError(f"Muitos redirects (>{max_hops}).")


_MIN_PROSE_CHARS = 200
_CHROME_BODY_CHARS = 400
# Piso baixo de propósito: item de menu é descartado pelo link-ratio, não pelo
# comprimento. Piso alto derrubava glossário, FAQ e tabela — conteúdo legítimo
# de linha curta — como se fossem navegação.
_MIN_LINE_CHARS = 15
_LINK_RATIO = 0.6

_MD_LINK_RE = re.compile(r"\[([^\]]*)\]\([^)]*\)")
_MD_MARKER_RE = re.compile(r"[#>*_`|~\[\]]+")

_SHELL_PAGE_RE = re.compile(
    r"requires?\s+javascript"
    r"|enable\s+javascript"
    r"|javascript\s+(?:is\s+)?(?:disabled|required|not\s+enabled)"
    r"|turn\s+on\s+javascript"
    r"|enable\s+cookies"
    r"|accept\s+(?:all\s+)?cookies"
    r"|cookie\s+(?:policy|consent)",
    re.IGNORECASE,
)


def _prose_text(markdown_body: str) -> str:
    """Extrai a prosa do markdown, descartando navegação e linhas repetidas."""
    kept: list[str] = []
    seen: set[str] = set()
    for raw_line in markdown_body.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        plain = " ".join(_MD_MARKER_RE.sub(" ", _MD_LINK_RE.sub(r"\1", line)).split())
        if len(plain) < _MIN_LINE_CHARS:
            continue
        link_texts = _MD_LINK_RE.findall(line)
        if link_texts and sum(len(t) for t in link_texts) >= _LINK_RATIO * len(plain):
            continue
        if plain in seen:
            continue
        seen.add(plain)
        kept.append(plain)
    return "\n".join(kept)


def _reject_empty_content(markdown_body: str, url: str) -> None:
    """Recusa páginas cujo markdown é só chrome de navegação ou aviso de JavaScript."""
    prose = _prose_text(markdown_body)
    if len(prose) >= _MIN_PROSE_CHARS:
        return
    body = " ".join(markdown_body.split())
    if len(body) < _CHROME_BODY_CHARS and not _SHELL_PAGE_RE.search(body):
        return
    raise WebIngestError(
        f"A página não rendeu conteúdo textual ({len(prose)} chars de prosa após "
        f"remover navegação) — provável página dinâmica que depende de JavaScript. "
        f"Abra {url} no navegador, salve a página renderizada como Markdown ou texto "
        f"e ingira o arquivo local."
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

    try:
        response = _follow_redirects(url)
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

    _reject_empty_content(markdown_body, url)

    ingested_at = datetime.now(UTC).isoformat()
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
