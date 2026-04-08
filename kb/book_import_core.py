"""Núcleo compartilhado para importação/exportação de livros em Markdown."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote
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
    def __init__(self, *, image_map: dict[str, str] | None = None, base_href: str | None = None):
        super().__init__()
        self.parts: list[str] = []
        self.list_depth = 0
        self.skip_depth = 0
        self.image_map = image_map or {}
        self.base_href = base_href

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self.skip_depth += 1
            return
        if self.skip_depth:
            return
        attrs_dict = dict(attrs)
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
        elif tag == "img":
            src = (attrs_dict.get("src") or "").strip()
            resolved = _resolve_image_reference(self.base_href, src, self.image_map)
            if resolved:
                alt = re.sub(r"\s+", " ", attrs_dict.get("alt") or "imagem").strip() or "imagem"
                self.parts.append(f"\n\n![{alt}]({resolved})\n\n")

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


_CLEAN_SLUG_PATTERNS = [
    (re.compile(r'\b[a-f0-9]{32}\b', re.IGNORECASE), ''),
    (re.compile(r'\b97[89][\d -]{10,}'), ''),
    (re.compile(r'\(?(?:z-library[\w.]*|z-lib[\w.]*|1lib[\w.]*|libgen[\w.]*)[,\s]*\)?', re.IGNORECASE), ''),
    (re.compile(r"[\-–]\s*anna'?s?\s*archive", re.IGNORECASE), ''),
    (re.compile(r'--\s*\d+,?\s*\d{4}\s*--'), ' '),
    (re.compile(r'--\s*(?:O\'Reilly|Cambridge|Packt|Springer|Wiley|Manning|No\s*Starch|Apress|Addison)[^-]*(?:--|$)', re.IGNORECASE), ''),
    (re.compile(r'\s*--\s*'), ' '),
    (re.compile(r'\(\s*\)'), ''),
    (re.compile(r'\s+'), ' '),
]


def clean_book_slug(stem: str) -> str:
    result = stem
    for pattern, replacement in _CLEAN_SLUG_PATTERNS:
        result = pattern.sub(replacement, result)
    result = result.strip(' -_.,;')
    if len(result) > 60:
        truncated = result[:60]
        last_space = truncated.rfind(' ')
        result = truncated[:last_space] if last_space > 30 else truncated
    return slugify(result)


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


def _resolve_image_reference(base_href: str | None, src: str, image_map: dict[str, str]) -> str | None:
    if not src:
        return None
    normalized_src = _normalize_book_path(unquote(src))
    candidates = [normalized_src, Path(normalized_src).name]
    if base_href:
        resolved = _normalize_book_path(_resolve_href(base_href, unquote(src)))
        candidates.insert(0, resolved)
        candidates.insert(1, Path(resolved).name)
    for candidate in candidates:
        if candidate and candidate in image_map:
            return image_map[candidate]
    return None


def html_to_markdown(html: str, *, image_map: dict[str, str] | None = None, base_href: str | None = None) -> str:
    parser = _MarkdownHTMLParser(image_map=image_map, base_href=base_href)
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


def _text_or_none(element: SafeET.Element | None) -> str | None:
    if element is None:
        return None
    text = " ".join(part.strip() for part in element.itertext() if part and part.strip()).strip()
    return text or None


def _extract_metadata_from_package_root(package_root: SafeET.Element, fallback_title: str) -> dict:
    metadata = {
        "title": None,
        "author": None,
        "authors": [],
        "language": None,
        "description": None,
        "publisher": None,
        "date": None,
        "identifiers": [],
        "subjects": [],
    }
    scalar_mapping = {
        "title": "title",
        "language": "language",
        "description": "description",
        "publisher": "publisher",
        "date": "date",
    }
    list_mapping = {
        "creator": "authors",
        "identifier": "identifiers",
        "subject": "subjects",
    }
    for element in package_root.iter():
        local_name = _local_name(element.tag)
        text = _text_or_none(element)
        if not text:
            continue
        scalar_target = scalar_mapping.get(local_name)
        if scalar_target and not metadata.get(scalar_target):
            metadata[scalar_target] = text
            continue
        list_target = list_mapping.get(local_name)
        if list_target:
            target_list = metadata[list_target]
            if text not in target_list:
                target_list.append(text)
    metadata["title"] = metadata["title"] or fallback_title
    metadata["author"] = metadata["authors"][0] if metadata["authors"] else None
    return metadata


def _safe_asset_name(path: str) -> str:
    filename = Path(path).name or "asset"
    sanitized = re.sub(r"[^A-Za-z0-9._-]+", "-", filename).strip("-.")
    return sanitized or "asset"


def _extract_epub_assets(archive: ZipFile, rootfile_path: str, package_root: SafeET.Element) -> tuple[list[dict], dict[str, str]]:
    assets: list[dict] = []
    image_map: dict[str, str] = {}
    used_names: set[str] = set()
    for element in package_root.iter():
        if _local_name(element.tag) != "item":
            continue
        href = element.attrib.get("href")
        media_type = element.attrib.get("media-type", "")
        if not href or not media_type.startswith("image/"):
            continue
        resolved_href = _resolve_href(rootfile_path, href)
        try:
            content = archive.read(resolved_href)
        except KeyError:
            continue
        safe_name = _safe_asset_name(resolved_href)
        stem = Path(safe_name).stem or "asset"
        suffix = Path(safe_name).suffix
        counter = 1
        while safe_name in used_names:
            counter += 1
            safe_name = f"{stem}-{counter}{suffix}"
        used_names.add(safe_name)
        relative_path = f"images/{safe_name}"
        assets.append({
            "source_href": _normalize_book_path(resolved_href),
            "file": relative_path,
            "media_type": media_type,
            "content": content,
        })
        image_map[_normalize_book_path(resolved_href)] = relative_path
        image_map[Path(resolved_href).name] = relative_path
    return assets, image_map


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


def _toc_entry(title: str, href: str, *, children: list[dict] | None = None) -> dict:
    file_href = _normalize_book_path(href)
    anchor = href.split("#", 1)[1] if "#" in href else ""
    return {
        "title": title,
        "href": href,
        "file_href": file_href,
        "anchor": anchor,
        "children": children or [],
    }


def _flatten_toc_map(entries: list[dict]) -> dict[str, str]:
    toc_map: dict[str, str] = {}
    stack = list(entries)
    while stack:
        entry = stack.pop(0)
        title = (entry.get("title") or "").strip()
        file_href = _normalize_book_path(entry.get("file_href") or entry.get("href") or "")
        if title and file_href and file_href not in toc_map:
            toc_map[file_href] = title
        stack[0:0] = entry.get("children", [])
    return toc_map


def _parse_ncx_navpoint(nav_point: SafeET.Element, href: str) -> dict | None:
    label: str | None = None
    src: str | None = None
    children: list[dict] = []
    for child in list(nav_point):
        local_name = _local_name(child.tag)
        if local_name == "navLabel":
            label = _text_or_none(child) or label
        elif local_name == "content" and child.attrib.get("src"):
            src = _resolve_href(href, child.attrib["src"])
        elif local_name == "navPoint":
            parsed_child = _parse_ncx_navpoint(child, href)
            if parsed_child:
                children.append(parsed_child)
    if not label or not src:
        return None
    return _toc_entry(label, src, children=children)


def _parse_ncx_toc_tree(archive: ZipFile, href: str) -> list[dict]:
    try:
        root = _safe_xml_fromstring(archive.read(href), BookConversionError, context=href)
    except (KeyError, BookConversionError):
        return []
    nav_map = None
    for element in root.iter():
        if _local_name(element.tag) == "navMap":
            nav_map = element
            break
    if nav_map is None:
        return []
    entries: list[dict] = []
    for child in list(nav_map):
        if _local_name(child.tag) != "navPoint":
            continue
        parsed = _parse_ncx_navpoint(child, href)
        if parsed:
            entries.append(parsed)
    return entries


def _element_attr(element: SafeET.Element, *names: str) -> str | None:
    for key, value in element.attrib.items():
        if key in names or _local_name(key) in names:
            return value
    return None


def _find_nav_list_root(nav_element: SafeET.Element) -> SafeET.Element | None:
    for element in nav_element.iter():
        if _local_name(element.tag) in {"ol", "ul"}:
            return element
    return None


def _parse_nav_list(list_element: SafeET.Element, href: str) -> list[dict]:
    entries: list[dict] = []
    for child in list(list_element):
        if _local_name(child.tag) != "li":
            continue
        link = None
        nested_list = None
        for grandchild in list(child):
            grandchild_name = _local_name(grandchild.tag)
            if grandchild_name == "a" and link is None:
                link = grandchild
            elif grandchild_name in {"ol", "ul"} and nested_list is None:
                nested_list = grandchild
        if link is None:
            for descendant in child.iter():
                if _local_name(descendant.tag) == "a":
                    link = descendant
                    break
        if link is None:
            continue
        raw_href = (link.attrib.get("href") or "").strip()
        title = _text_or_none(link)
        if not raw_href or not title:
            continue
        children = _parse_nav_list(nested_list, href) if nested_list is not None else []
        entries.append(_toc_entry(title, _resolve_href(href, raw_href), children=children))
    return entries


def _parse_nav_document_toc_tree(archive: ZipFile, href: str) -> list[dict]:
    try:
        root = _safe_xml_fromstring(archive.read(href), BookConversionError, context=href)
    except BookConversionError:
        try:
            html = archive.read(href).decode("utf-8", errors="replace")
        except Exception:
            return []
        parser = _NavDocParser()
        parser.feed(html)
        parser.close()
        return [_toc_entry(label, _resolve_href(href, link_href)) for link_href, label in parser.links]
    except KeyError:
        return []

    nav_element = None
    for element in root.iter():
        if _local_name(element.tag) != "nav":
            continue
        nav_type = (_element_attr(element, "epub:type", "type") or "").lower()
        nav_role = (_element_attr(element, "role") or "").lower()
        if nav_type == "toc" or nav_role == "doc-toc":
            nav_element = element
            break
    if nav_element is None:
        return []
    list_root = _find_nav_list_root(nav_element)
    if list_root is None:
        return []
    return _parse_nav_list(list_root, href)


def _build_fallback_toc(chapters: list[dict]) -> list[dict]:
    return [_toc_entry(chapter["title"], chapter["source_href"]) for chapter in chapters if chapter.get("source_href")]


def _build_toc_data(archive: ZipFile, rootfile_path: str, package_root: SafeET.Element) -> tuple[list[dict], dict[str, str], str]:
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

    toc_tree: list[dict] = []
    toc_source = "none"
    if toc_id and toc_id in manifest:
        entry = manifest[toc_id]
        if "ncx" in entry["media_type"]:
            toc_tree = _parse_ncx_toc_tree(archive, entry["href"])
            toc_source = "ncx" if toc_tree else "none"
        elif "html" in entry["media_type"] or "xhtml" in entry["media_type"]:
            toc_tree = _parse_nav_document_toc_tree(archive, entry["href"])
            toc_source = "nav" if toc_tree else "none"

    if not toc_tree:
        for entry in manifest.values():
            if "ncx" not in entry["media_type"]:
                continue
            toc_tree = _parse_ncx_toc_tree(archive, entry["href"])
            if toc_tree:
                toc_source = "ncx"
                break

    if not toc_tree:
        for entry in manifest.values():
            if "html" not in entry["media_type"] and "xhtml" not in entry["media_type"]:
                continue
            if "nav" not in f" {entry['properties']} ":
                continue
            toc_tree = _parse_nav_document_toc_tree(archive, entry["href"])
            if toc_tree:
                toc_source = "nav"
                break

    return toc_tree, _flatten_toc_map(toc_tree), toc_source


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
        return {
            "title": source.stem,
            "author": None,
            "authors": [],
            "language": None,
            "description": None,
            "publisher": None,
            "date": None,
            "identifiers": [],
            "subjects": [],
            "assets": [],
        }
    raise error_cls("Formato não suportado. Use EPUB ou PDF textual")


def _extract_chapters_from_epub(source: Path, error_cls: type[Exception], *, include_images: bool = False) -> tuple[list[dict], dict]:
    try:
        with ZipFile(source) as archive:
            rootfile_path, package_root = _parse_package_document(archive, error_cls)
            book_metadata = _extract_metadata_from_package_root(package_root, source.stem)
            toc_tree, toc_map, toc_source = _build_toc_data(archive, rootfile_path, package_root)
            assets, image_map = _extract_epub_assets(archive, rootfile_path, package_root) if include_images else ([], {})
            manifest: dict[str, dict[str, str]] = {}
            spine: list[str] = []
            for element in package_root.iter():
                name = _local_name(element.tag)
                if name == "item":
                    item_id = element.attrib.get("id")
                    href = element.attrib.get("href")
                    media_type = element.attrib.get("media-type", "")
                    properties = element.attrib.get("properties", "")
                    if item_id and href and ("html" in media_type or "xhtml" in media_type) and "nav" not in f" {properties} ":
                        manifest[item_id] = {"href": _resolve_href(rootfile_path, href), "media_type": media_type}
                elif name == "itemref":
                    idref = element.attrib.get("idref")
                    if idref:
                        spine.append(idref)

            chapter_ids = [idref for idref in spine if idref in manifest]
            chapter_source = "spine"
            if not chapter_ids:
                chapter_ids = list(manifest.keys())
                chapter_source = "manifest_fallback"

            chapters: list[dict] = []
            for chapter_index, idref in enumerate(chapter_ids, start=1):
                manifest_entry = manifest.get(idref)
                if not manifest_entry:
                    continue
                href = manifest_entry["href"]
                html = archive.read(href).decode("utf-8", errors="replace")
                normalized_href = _normalize_book_path(href)
                fallback_title = toc_map.get(normalized_href) or Path(normalized_href).stem.replace("_", " ").replace("-", " ").strip() or f"Capítulo {chapter_index}"
                title = _extract_title(html, fallback_title)
                content = html_to_markdown(html, image_map=image_map, base_href=href)
                if not content:
                    continue
                chapters.append({
                    "index": chapter_index,
                    "title": title,
                    "content": content,
                    "source_href": normalized_href,
                })
    except BadZipFile as exc:
        raise error_cls(f"EPUB inválido ou corrompido: {source.name}") from exc

    if not chapters:
        return [], book_metadata

    if not toc_tree:
        toc_tree = _build_fallback_toc(chapters)
        toc_source = "spine_fallback"

    book_metadata.update({
        "toc": toc_tree,
        "toc_source": toc_source,
        "chapter_source": chapter_source,
        "assets": assets,
    })
    return chapters, book_metadata



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


def _is_garbled(text: str) -> bool:
    if len(text) < 50:
        return False
    ctrl = sum(1 for c in text if ord(c) < 32 and c not in '\n\r\t')
    return ctrl / len(text) > 0.05



_PDF_PAGES_PER_CHUNK = 15


def _get_pdf_pages(source: Path, error_cls: type[Exception], *, use_ocr: bool = False) -> tuple[list[str], list]:
    import fitz

    try:
        doc = fitz.open(str(source))
    except Exception as exc:
        raise error_cls(f"PDF inválido ou corrompido: {source.name} ({exc})")

    toc = doc.get_toc()  # [[level, title, page_1based], ...]

    if use_ocr:
        try:
            from pdf2image import convert_from_path
            import pytesseract
        except ImportError:
            raise error_cls("OCR requer dependências adicionais. Execute: pip install 'kb[ocr]'")
        try:
            images = convert_from_path(str(source))
        except Exception as exc:
            raise error_cls(f"Erro ao converter PDF para imagens: {exc}")
        pages = [pytesseract.image_to_string(img, lang="por+eng") for img in images]
        doc.close()
    else:
        pages = [page.get_text() for page in doc]
        doc.close()
        combined = _normalize_pdf_text("\n".join(pages))
        if not combined:
            raise error_cls("PDF sem texto extraível — arquivo pode ser scan. Tente: kb import-book --ocr")
        if _is_garbled(combined):
            raise error_cls("PDF com encoding de fonte inválido — texto corrompido. Tente: kb import-book --ocr")

    return pages, toc


def _build_metadata(source: Path, chapter_source: str) -> dict:
    return {
        "title": source.stem,
        "author": None,
        "authors": [],
        "language": None,
        "description": None,
        "publisher": None,
        "date": None,
        "identifiers": [],
        "subjects": [],
        "toc": [],
        "toc_source": "none",
        "chapter_source": chapter_source,
        "assets": [],
    }


def _extract_chapters_from_pdf(source: Path, error_cls: type[Exception], *, use_ocr: bool = False, chunk_pages: int = _PDF_PAGES_PER_CHUNK) -> tuple[list[dict], dict]:
    pages, toc = _get_pdf_pages(source, error_cls, use_ocr=use_ocr)

    max_toc_chapters = max(5, len(pages) // 8)

    top_level: list[tuple[str, int]] = []
    overflow_candidates: list[tuple[str, int]] = []

    for level in (1, 2):
        candidates = [(title, page - 1) for lvl, title, page in toc if lvl == level and title.strip()]
        enough = len(candidates) >= 5 or (len(candidates) >= 2 and len(pages) <= 30)
        not_too_many = len(candidates) <= max_toc_chapters
        if enough and not_too_many:
            top_level = candidates
            break
        if enough and not overflow_candidates:
            overflow_candidates = candidates

    if len(top_level) >= 2:
        chapters = []
        for i, (title, start_page) in enumerate(top_level):
            start_page = max(0, start_page)
            end_page = max(start_page + 1, top_level[i + 1][1] if i + 1 < len(top_level) else len(pages))
            content = _normalize_pdf_text("\n".join(pages[start_page:end_page]))
            if content:
                chapters.append({"index": len(chapters) + 1, "title": title[:120], "content": content})
        if chapters:
            return chapters, _build_metadata(source, "toc")

    if overflow_candidates:
        chapters = []
        i = 0
        while i < len(overflow_candidates):
            title, start = overflow_candidates[i]
            start = max(0, start)
            j = i + 1
            while j < len(overflow_candidates) and overflow_candidates[j][1] - start < chunk_pages:
                j += 1
            end = overflow_candidates[j][1] if j < len(overflow_candidates) else len(pages)
            content = _normalize_pdf_text("\n".join(pages[start:end]))
            if content:
                chapters.append({"index": len(chapters) + 1, "title": title[:120], "content": content})
            i = j
        if chapters:
            return chapters, _build_metadata(source, "toc_merged")

    chapters = []
    for i in range(0, len(pages), chunk_pages):
        chunk = pages[i:i + chunk_pages]
        content = _normalize_pdf_text("\n".join(chunk))
        if content:
            start = i + 1
            end = min(i + chunk_pages, len(pages))
            title = f"Páginas {start}–{end}"
            chapters.append({"index": len(chapters) + 1, "title": title, "content": content})

    if not chapters:
        raise error_cls("Nenhum conteúdo extraível encontrado no PDF")

    return chapters, _build_metadata(source, "page_chunks")


def write_assets(output_dir: Path, assets: list[dict]) -> list[Path]:
    ensure_output_dir(output_dir)
    written_assets: list[Path] = []
    for asset in assets:
        relative_path = Path(asset["file"])
        asset_path = output_dir / relative_path
        asset_path.parent.mkdir(parents=True, exist_ok=True)
        asset_path.write_bytes(asset["content"])
        written_assets.append(asset_path)
    return written_assets


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
    payload = {
        "source_file": source.name,
        "source_format": source.suffix.lower().lstrip("."),
        "processed_at": book_metadata.get("processed_at") or datetime.now(timezone.utc).isoformat(),
        "book_title": book_metadata.get("title") or source.stem,
        "book_author": book_metadata.get("author"),
        "book_authors": book_metadata.get("authors") or ([book_metadata["author"]] if book_metadata.get("author") else []),
        "book_language": book_metadata.get("language"),
        "book_description": book_metadata.get("description"),
        "book_publisher": book_metadata.get("publisher"),
        "book_date": book_metadata.get("date"),
        "book_identifiers": book_metadata.get("identifiers") or [],
        "book_subjects": book_metadata.get("subjects") or [],
        "chapter_count": len(chapters),
        "toc_source": book_metadata.get("toc_source") or "none",
        "chapter_source": book_metadata.get("chapter_source") or "unknown",
        "toc": book_metadata.get("toc") or [],
        "assets": [
            {
                "source_href": asset.get("source_href"),
                "file": asset.get("file"),
                "media_type": asset.get("media_type"),
            }
            for asset in (book_metadata.get("assets") or [])
        ],
        "chapters": [
            {
                "index": chapter["index"],
                "title": chapter["title"],
                "file": written_file.name,
                "source_href": chapter.get("source_href"),
            }
            for chapter, written_file in zip(chapters, written_files, strict=False)
        ],
    }
    metadata_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return metadata_path


def convert_book(source: Path, output_dir: Path, *, error_cls: type[Exception] = BookConversionError, unsupported_message: str = "Formato não suportado. Use EPUB ou PDF textual", include_images: bool = False, use_ocr: bool = False, chunk_pages: int = _PDF_PAGES_PER_CHUNK) -> tuple[list[Path], Path]:
    if not source.exists():
        raise error_cls(f"Arquivo de entrada não existe: {source}")
    if source.suffix.lower() == ".epub":
        chapters, book_metadata = _extract_chapters_from_epub(source, error_cls, include_images=include_images)
    elif source.suffix.lower() == ".pdf":
        chapters, book_metadata = _extract_chapters_from_pdf(source, error_cls, use_ocr=use_ocr, chunk_pages=chunk_pages)
    else:
        raise error_cls(unsupported_message)
    written_files = write_chapters(chapters, output_dir, error_cls=error_cls)
    write_assets(output_dir, book_metadata.get("assets") or [])
    metadata_path = write_metadata(source, output_dir, chapters, written_files, book_metadata)
    return written_files, metadata_path
