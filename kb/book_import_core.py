"""Núcleo compartilhado para importação/exportação de livros em Markdown."""

from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from pathlib import Path
from zipfile import BadZipFile, ZipFile

try:
    from defusedxml import ElementTree as SafeET
    from defusedxml.common import DefusedXmlException
except ImportError:  # pragma: no cover - fallback para ambientes mínimos de teste
    from xml.etree import ElementTree as SafeET

    class DefusedXmlException(Exception):
        pass


class BookConversionError(ValueError):
    """Erro genérico de conversão/importação de livros."""


class _MarkdownHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts: list[str] = []
        self.list_depth = 0
        self.skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self.skip_depth += 1
            return
        if self.skip_depth:
            return
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6", "p", "div", "section", "article", "blockquote"}:
            self.parts.append("\n\n")
        elif tag in {"ul", "ol"}:
            self.list_depth += 1
            self.parts.append("\n")
        elif tag == "li":
            indent = "  " * max(self.list_depth - 1, 0)
            self.parts.append(f"\n{indent}- ")
        elif tag in {"strong", "b"}:
            self.parts.append("**")
        elif tag in {"em", "i"}:
            self.parts.append("*")
        elif tag == "br":
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in {"script", "style"}:
            self.skip_depth = max(self.skip_depth - 1, 0)
            return
        if self.skip_depth:
            return
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6", "p", "div", "section", "article", "blockquote"}:
            self.parts.append("\n\n")
        elif tag in {"ul", "ol"}:
            self.list_depth = max(self.list_depth - 1, 0)
            self.parts.append("\n")
        elif tag in {"strong", "b"}:
            self.parts.append("**")
        elif tag in {"em", "i"}:
            self.parts.append("*")

    def handle_data(self, data):
        if self.skip_depth:
            return
        text = re.sub(r"\s+", " ", data)
        if text.strip():
            self.parts.append(text.strip())


class _TitleExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.current_tag: str | None = None
        self.buffer: list[str] = []
        self.candidates: dict[str, list[str]] = {"h1": [], "h2": [], "title": []}

    def handle_starttag(self, tag, attrs):
        if tag in self.candidates:
            self.current_tag = tag
            self.buffer = []

    def handle_endtag(self, tag):
        if self.current_tag == tag:
            text = " ".join(self.buffer).strip()
            if text:
                self.candidates[tag].append(text)
            self.current_tag = None
            self.buffer = []

    def handle_data(self, data):
        if self.current_tag:
            cleaned = re.sub(r"\s+", " ", data).strip()
            if cleaned:
                self.buffer.append(cleaned)


def slugify(value: str) -> str:
    normalized = value.lower()
    replacements = {"á": "a", "à": "a", "â": "a", "ã": "a", "ä": "a", "é": "e", "è": "e", "ê": "e", "ë": "e", "í": "i", "ì": "i", "î": "i", "ï": "i", "ó": "o", "ò": "o", "ô": "o", "õ": "o", "ö": "o", "ú": "u", "ù": "u", "û": "u", "ü": "u", "ç": "c"}
    for old, new in replacements.items():
        normalized = normalized.replace(old, new)
    normalized = re.sub(r"[^a-z0-9]+", "-", normalized)
    normalized = re.sub(r"-+", "-", normalized).strip("-")
    return normalized or "capitulo"


def build_chapter_filename(index: int, title: str) -> str:
    return f"{index:02d}-{slugify(title)}.md"


def html_to_markdown(html: str) -> str:
    parser = _MarkdownHTMLParser()
    parser.feed(html)
    parser.close()
    text = "".join(parser.parts)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\s+([.,;:!?])", r"\1", text)
    text = re.sub(r"\n[ \t]+", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def ensure_output_dir(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)


def _local_name(tag: str) -> str:
    return tag.split("}", 1)[-1]


def _safe_xml_fromstring(xml_bytes: bytes, error_cls: type[Exception], *, context: str) -> SafeET.Element:
    lowered = xml_bytes.lower()
    if b"<!doctype" in lowered or b"<!entity" in lowered:
        raise error_cls(f"EPUB inválido: XML inseguro ou malformado em {context}")
    try:
        return SafeET.fromstring(xml_bytes)
    except (DefusedXmlException, SafeET.ParseError) as exc:
        raise error_cls(f"EPUB inválido: XML inseguro ou malformado em {context}") from exc


def _find_rootfile_path(archive: ZipFile, error_cls: type[Exception]) -> str:
    try:
        container_xml = archive.read("META-INF/container.xml")
    except KeyError as exc:
        raise error_cls("EPUB inválido: container.xml ausente") from exc
    root = _safe_xml_fromstring(container_xml, error_cls, context="META-INF/container.xml")
    for element in root.iter():
        if _local_name(element.tag) == "rootfile":
            full_path = element.attrib.get("full-path")
            if full_path:
                return full_path
    raise error_cls("EPUB inválido: rootfile não encontrado")


def _resolve_href(base_path: str, href: str) -> str:
    return str((Path(base_path).parent / href).as_posix())


def _parse_package_document(archive: ZipFile, error_cls: type[Exception]) -> tuple[str, SafeET.Element]:
    rootfile_path = _find_rootfile_path(archive, error_cls)
    package_root = _safe_xml_fromstring(archive.read(rootfile_path), error_cls, context=rootfile_path)
    return rootfile_path, package_root


def _extract_metadata_from_package_root(package_root: SafeET.Element, fallback_title: str) -> dict:
    metadata = {"title": None, "author": None, "language": None}
    mapping = {"title": "title", "creator": "author", "language": "language"}
    for element in package_root.iter():
        target = mapping.get(_local_name(element.tag))
        if target and element.text and element.text.strip() and not metadata.get(target):
            metadata[target] = element.text.strip()
    metadata["title"] = metadata["title"] or fallback_title
    return metadata


def _extract_title(html: str, fallback: str) -> str:
    parser = _TitleExtractor()
    parser.feed(html)
    parser.close()
    for tag in ("h1", "h2", "title"):
        for candidate in parser.candidates[tag]:
            title = html_to_markdown(candidate).strip()
            if title:
                return title
    return fallback


def _normalize_book_path(path: str) -> str:
    return Path(path.split("#", 1)[0].split("?", 1)[0]).as_posix().lstrip("./")


def _parse_ncx_toc(archive: ZipFile, href: str) -> dict[str, str]:
    try:
        root = SafeET.fromstring(archive.read(href))
    except (KeyError, DefusedXmlException, SafeET.ParseError):
        return {}
    toc: dict[str, str] = {}
    for nav_point in root.iter():
        if _local_name(nav_point.tag) != "navPoint":
            continue
        label = None
        src = None
        for child in nav_point.iter():
            name = _local_name(child.tag)
            if name == "text" and child.text and child.text.strip() and label is None:
                label = child.text.strip()
            elif name == "content" and child.attrib.get("src"):
                src = child.attrib["src"]
        if src and label:
            toc.setdefault(_normalize_book_path(_resolve_href(href, src)), label)
    return toc


class _NavDocParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_nav = False
        self.in_link = False
        self.current_href: str | None = None
        self.current_text: list[str] = []
        self.links: list[tuple[str, str]] = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == "nav":
            nav_type = (attrs_dict.get("epub:type") or attrs_dict.get("type") or "").lower()
            if nav_type == "toc" or attrs_dict.get("role") == "doc-toc":
                self.in_nav = True
        elif self.in_nav and tag == "a":
            self.in_link = True
            self.current_href = attrs_dict.get("href")
            self.current_text = []

    def handle_endtag(self, tag):
        if tag == "nav" and self.in_nav:
            self.in_nav = False
        elif tag == "a" and self.in_link:
            text = " ".join(self.current_text).strip()
            if self.current_href and text:
                self.links.append((self.current_href, text))
            self.in_link = False
            self.current_href = None
            self.current_text = []

    def handle_data(self, data):
        if self.in_link:
            cleaned = re.sub(r"\s+", " ", data).strip()
            if cleaned:
                self.current_text.append(cleaned)


def _parse_nav_document_toc(archive: ZipFile, href: str) -> dict[str, str]:
    try:
        html = archive.read(href).decode("utf-8", errors="replace")
    except Exception:
        return {}
    parser = _NavDocParser()
    parser.feed(html)
    parser.close()
    toc: dict[str, str] = {}
    for link_href, label in parser.links:
        toc.setdefault(_normalize_book_path(_resolve_href(href, link_href)), label)
    return toc


def _build_toc_map(archive: ZipFile, rootfile_path: str, package_root: SafeET.Element) -> dict[str, str]:
    manifest: dict[str, dict[str, str]] = {}
    toc_id: str | None = package_root.attrib.get("toc")
    for element in package_root.iter():
        if _local_name(element.tag) != "item":
            continue
        item_id = element.attrib.get("id")
        href = element.attrib.get("href")
        if not item_id or not href:
            continue
        properties = element.attrib.get("properties", "")
        manifest[item_id] = {
            "href": _resolve_href(rootfile_path, href),
            "media_type": element.attrib.get("media-type", ""),
            "properties": properties,
        }
        if properties == "nav" or " nav " in f" {properties} ":
            toc_id = item_id
    if toc_id and toc_id in manifest:
        entry = manifest[toc_id]
        if "ncx" in entry["media_type"]:
            return _parse_ncx_toc(archive, entry["href"])
        if "html" in entry["media_type"] or "xhtml" in entry["media_type"]:
            return _parse_nav_document_toc(archive, entry["href"])
    for entry in manifest.values():
        if "ncx" in entry["media_type"]:
            toc_map = _parse_ncx_toc(archive, entry["href"])
            if toc_map:
                return toc_map
    return {}


def extract_book_metadata(source: Path, *, error_cls: type[Exception] = BookConversionError) -> dict:
    if not source.exists():
        raise error_cls(f"Arquivo de entrada não existe: {source}")
    suffix = source.suffix.lower()
    if suffix == ".epub":
        try:
            with ZipFile(source) as archive:
                _, package_root = _parse_package_document(archive, error_cls)
                return _extract_metadata_from_package_root(package_root, source.stem)
        except BadZipFile as exc:
            raise error_cls(f"EPUB inválido ou corrompido: {source.name}") from exc
    if suffix == ".pdf":
        return {"title": source.stem, "author": None, "language": None}
    raise error_cls("Formato não suportado. Use EPUB ou PDF textual")


def _extract_chapters_from_epub(source: Path, error_cls: type[Exception]) -> tuple[list[dict], dict]:
    try:
        with ZipFile(source) as archive:
            rootfile_path, package_root = _parse_package_document(archive, error_cls)
            book_metadata = _extract_metadata_from_package_root(package_root, source.stem)
            toc_map = _build_toc_map(archive, rootfile_path, package_root)
            manifest: dict[str, str] = {}
            spine: list[str] = []
            for element in package_root.iter():
                name = _local_name(element.tag)
                if name == "item":
                    item_id = element.attrib.get("id")
                    href = element.attrib.get("href")
                    media_type = element.attrib.get("media-type", "")
                    if item_id and href and ("html" in media_type or "xhtml" in media_type):
                        manifest[item_id] = _resolve_href(rootfile_path, href)
                elif name == "itemref":
                    idref = element.attrib.get("idref")
                    if idref:
                        spine.append(idref)
            chapters: list[dict] = []
            for chapter_index, idref in enumerate(spine, start=1):
                href = manifest.get(idref)
                if not href:
                    continue
                html = archive.read(href).decode("utf-8", errors="replace")
                fallback_title = toc_map.get(_normalize_book_path(href)) or Path(href).stem.replace("_", " ").replace("-", " ").strip() or f"Capítulo {chapter_index}"
                title = _extract_title(html, fallback_title)
                content = html_to_markdown(html)
                if not content:
                    continue
                chapters.append({"index": chapter_index, "title": title, "content": content})
    except BadZipFile as exc:
        raise error_cls(f"EPUB inválido ou corrompido: {source.name}") from exc
    return chapters, book_metadata


_PDF_TEXT_RE = re.compile(r"\((.*?)(?<!\\)\)\s*Tj", re.DOTALL)
_PDF_ARRAY_TEXT_RE = re.compile(r"\[(.*?)\]\s*TJ", re.DOTALL)
_PDF_STRING_RE = re.compile(r"\((.*?)(?<!\\)\)", re.DOTALL)
_PDF_HEADING_RE = re.compile(
    r"^(?:cap[ií]tulo|chapter|parte|part|section|se[cç][aã]o)\s+(?:[0-9]+|[ivxlcdm]+)\b(?:\s*[-–—:]?\s*.+)?$",
    re.IGNORECASE,
)


def _decode_pdf_literal(value: str) -> str:
    return value.replace(r"\n", "\n").replace(r"\r", "\n").replace(r"\t", " ").replace(r"\(", "(").replace(r"\)", ")").replace(r"\\", "\\")


def _normalize_pdf_text(text: str) -> str:
    normalized_lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines()]
    kept_lines: list[str] = []
    blank_streak = 0
    for line in normalized_lines:
        if not line:
            blank_streak += 1
            if blank_streak <= 1 and kept_lines:
                kept_lines.append("")
            continue
        blank_streak = 0
        kept_lines.append(line)
    return "\n".join(kept_lines).strip()


def _extract_text_from_pdf(source: Path, error_cls: type[Exception]) -> str:
    raw_bytes = source.read_bytes()
    if not raw_bytes.startswith(b"%PDF"):
        raise error_cls(f"PDF inválido ou corrompido: {source.name}")
    decoded = raw_bytes.decode("latin-1", errors="ignore")
    chunks = [_decode_pdf_literal(m.group(1)) for m in _PDF_TEXT_RE.finditer(decoded)]
    for match in _PDF_ARRAY_TEXT_RE.finditer(decoded):
        fragments = [_decode_pdf_literal(piece) for piece in _PDF_STRING_RE.findall(match.group(1))]
        if fragments:
            chunks.append(" ".join(fragments))
    text = _normalize_pdf_text("\n".join(chunks))
    if not text:
        raise error_cls("PDF sem texto extraível. O suporte inicial cobre apenas PDFs textuais, não scans/imagens")
    return text


def _is_pdf_heading_line(line: str) -> bool:
    return bool(_PDF_HEADING_RE.match(line.strip()))


def _build_pdf_chapters_from_lines(lines: list[str], source: Path) -> tuple[list[dict], str | None]:
    heading_indexes = [index for index, line in enumerate(lines) if _is_pdf_heading_line(line)]
    document_title = None

    if lines and (not heading_indexes or heading_indexes[0] > 0):
        document_title = lines[0][:120]

    if len(heading_indexes) >= 2:
        chapters: list[dict] = []
        for chapter_number, start_index in enumerate(heading_indexes, start=1):
            end_index = heading_indexes[chapter_number] if chapter_number < len(heading_indexes) else len(lines)
            title = lines[start_index].strip() or f"Capítulo {chapter_number}"
            body_lines = [line for line in lines[start_index + 1 : end_index] if line.strip()]
            content = "\n\n".join(body_lines).strip() or title
            chapters.append({"index": chapter_number, "title": title[:120], "content": content})
        return chapters, document_title

    return [], document_title


def _extract_chapters_from_pdf(source: Path, error_cls: type[Exception]) -> tuple[list[dict], dict]:
    text = _extract_text_from_pdf(source, error_cls)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    segmented_chapters, document_title = _build_pdf_chapters_from_lines(lines, source)
    if segmented_chapters:
        return segmented_chapters, {"title": document_title or source.stem, "author": None, "language": None}

    paragraphs = [part.strip() for part in re.split(r"\n\s*\n+", text) if part.strip()]
    title = paragraphs[0].splitlines()[0].strip() if paragraphs else source.stem
    title = (title or source.stem)[:120]
    content = text[len(title):].strip() if text.startswith(title) else text
    if not content:
        content = text
    return ([{"index": 1, "title": title, "content": content}], {"title": document_title or source.stem, "author": None, "language": None})


def write_chapters(chapters: list[dict], output_dir: Path, *, error_cls: type[Exception] = BookConversionError) -> list[Path]:
    if not chapters:
        raise error_cls("Nenhum capítulo foi detectado no documento")
    ensure_output_dir(output_dir)
    written_files: list[Path] = []
    for chapter in chapters:
        path = output_dir / build_chapter_filename(chapter["index"], chapter["title"])
        heading = f"# {chapter['title']}"
        body = chapter["content"].strip()
        if not body.startswith(heading):
            body = f"{heading}\n\n{body}"
        path.write_text(body.strip() + "\n", encoding="utf-8")
        written_files.append(path)
    return written_files


def write_metadata(source: Path, output_dir: Path, chapters: list[dict], written_files: list[Path], book_metadata: dict | None = None) -> Path:
    ensure_output_dir(output_dir)
    book_metadata = book_metadata or {}
    metadata_path = output_dir / "metadata.json"
    metadata_path.write_text(json.dumps({
        "source_file": source.name,
        "source_format": source.suffix.lower().lstrip("."),
        "book_title": book_metadata.get("title") or source.stem,
        "book_author": book_metadata.get("author"),
        "book_language": book_metadata.get("language"),
        "chapter_count": len(chapters),
        "chapters": [{"index": chapter["index"], "title": chapter["title"], "file": written_file.name} for chapter, written_file in zip(chapters, written_files, strict=False)],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return metadata_path


def convert_book(source: Path, output_dir: Path, *, error_cls: type[Exception] = BookConversionError, unsupported_message: str = "Formato não suportado. Use EPUB ou PDF textual") -> tuple[list[Path], Path]:
    if not source.exists():
        raise error_cls(f"Arquivo de entrada não existe: {source}")
    if source.suffix.lower() == ".epub":
        chapters, book_metadata = _extract_chapters_from_epub(source, error_cls)
    elif source.suffix.lower() == ".pdf":
        chapters, book_metadata = _extract_chapters_from_pdf(source, error_cls)
    else:
        raise error_cls(unsupported_message)
    written_files = write_chapters(chapters, output_dir, error_cls=error_cls)
    metadata_path = write_metadata(source, output_dir, chapters, written_files, book_metadata)
    return written_files, metadata_path
