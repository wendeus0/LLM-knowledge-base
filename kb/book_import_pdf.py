from pathlib import Path


def _normalize_pdf_text(text: str) -> str:
    import re

    normalized_lines = []
    for line in text.splitlines():
        leading = re.match(r"[ \t]*", line).group(0)
        content = line[len(leading) :]
        normalized_content = re.sub(r"[ \t]+", " ", content).strip()
        normalized_lines.append(
            f"{leading}{normalized_content}" if normalized_content else ""
        )
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
    return "\n".join(kept_lines).strip("\n")


def _is_garbled(text: str) -> bool:
    if len(text) < 50:
        return False
    ctrl = sum(1 for c in text if ord(c) < 32 and c not in "\n\r\t")
    return ctrl / len(text) > 0.05


_PDF_PAGES_PER_CHUNK = 15


def _get_pdf_pages(
    source: Path, error_cls: type[Exception], *, use_ocr: bool = False
) -> tuple[list[str], list]:
    import fitz

    try:
        doc = fitz.open(str(source))
    except Exception as exc:
        raise error_cls(f"PDF inválido ou corrompido: {source.name} ({exc})")

    try:
        toc = doc.get_toc()

        if use_ocr:
            try:
                from pdf2image import convert_from_path
                import pytesseract
            except ImportError:
                raise error_cls(
                    "OCR requer dependências adicionais. Execute: pip install 'kb[ocr]'"
                )
            try:
                images = convert_from_path(str(source))
            except Exception as exc:
                raise error_cls(f"Erro ao converter PDF para imagens: {exc}")
            pages = [pytesseract.image_to_string(img, lang="por+eng") for img in images]
        else:
            pages = [page.get_text() for page in doc]
            combined = _normalize_pdf_text("\n".join(pages))
            if not combined:
                raise error_cls(
                    "PDF sem texto extraível — arquivo pode ser scan. Tente: kb import-book --ocr"
                )
            if _is_garbled(combined):
                raise error_cls(
                    "PDF com encoding de fonte inválido — texto corrompido. Tente: kb import-book --ocr"
                )

        return pages, toc
    finally:
        doc.close()


def _pdf_toc_entries(entries: list[tuple[str, int]]) -> list[dict]:
    return [
        {"title": title[:120], "page": max(1, page + 1)}
        for title, page in entries
        if title.strip()
    ]


def _build_pdf_metadata(
    source: Path,
    chapter_source: str,
    *,
    toc: list[dict] | None = None,
    toc_source: str = "none",
) -> dict:
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
        "toc": toc or [],
        "toc_source": toc_source,
        "chapter_source": chapter_source,
        "assets": [],
    }


def _extract_chapters_from_pdf(
    source: Path,
    error_cls: type[Exception],
    *,
    use_ocr: bool = False,
    chunk_pages: int = _PDF_PAGES_PER_CHUNK,
) -> tuple[list[dict], dict]:
    pages, toc = _get_pdf_pages(source, error_cls, use_ocr=use_ocr)

    max_toc_chapters = max(5, len(pages) // 8)
    top_level: list[tuple[str, int]] = []
    overflow_candidates: list[tuple[str, int]] = []
    toc = toc or []

    for level in (1, 2):
        candidates = [
            (title, page - 1)
            for lvl, title, page in toc
            if lvl == level and title.strip()
        ]
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
            end_page = max(
                start_page + 1,
                top_level[i + 1][1] if i + 1 < len(top_level) else len(pages),
            )
            content = _normalize_pdf_text("\n".join(pages[start_page:end_page]))
            if content:
                chapters.append(
                    {
                        "index": len(chapters) + 1,
                        "title": title[:120],
                        "content": content,
                    }
                )
        if chapters:
            return chapters, _build_pdf_metadata(
                source,
                "toc",
                toc=_pdf_toc_entries(top_level),
                toc_source="pdf_outline",
            )

    if overflow_candidates:
        chapters = []
        i = 0
        while i < len(overflow_candidates):
            title, start = overflow_candidates[i]
            start = max(0, start)
            j = i + 1
            while (
                j < len(overflow_candidates)
                and overflow_candidates[j][1] - start < chunk_pages
            ):
                j += 1
            end = (
                overflow_candidates[j][1]
                if j < len(overflow_candidates)
                else len(pages)
            )
            content = _normalize_pdf_text("\n".join(pages[start:end]))
            if content:
                chapters.append(
                    {
                        "index": len(chapters) + 1,
                        "title": title[:120],
                        "content": content,
                    }
                )
            i = j
        if chapters:
            return chapters, _build_pdf_metadata(
                source,
                "toc_merged",
                toc=_pdf_toc_entries(overflow_candidates),
                toc_source="pdf_outline",
            )

    chapters = []
    for i in range(0, len(pages), chunk_pages):
        chunk = pages[i : i + chunk_pages]
        content = _normalize_pdf_text("\n".join(chunk))
        if content:
            start = i + 1
            end = min(i + chunk_pages, len(pages))
            title = f"Páginas {start}–{end}"
            chapters.append(
                {"index": len(chapters) + 1, "title": title, "content": content}
            )

    if not chapters:
        raise error_cls("Nenhum conteúdo extraível encontrado no PDF")

    return chapters, _build_pdf_metadata(source, "page_chunks")
