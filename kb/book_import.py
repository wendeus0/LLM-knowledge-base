"""Importação de livros para capítulos em Markdown."""

from pathlib import Path

from kb.book_import_core import (
    BookConversionError,
    build_chapter_filename,
    clean_book_slug,
    convert_book,
    extract_book_metadata as _extract_book_metadata,
    html_to_markdown,
    slugify,
    write_chapters as _write_chapters,
    write_metadata as _write_metadata,
)


class BookImportError(BookConversionError):
    pass


def default_output_dir(source: Path) -> Path:
    from kb.config import RAW_DIR

    return RAW_DIR / "books" / clean_book_slug(source.stem)


def extract_book_metadata(source: Path) -> dict:
    return _extract_book_metadata(source, error_cls=BookImportError)


def import_epub(source: Path, output_dir: Path | None = None, *, use_ocr: bool = False, chunk_pages: int = 15) -> tuple[list[Path], Path]:
    target_dir = output_dir or default_output_dir(source)
    return convert_book(
        source,
        target_dir,
        error_cls=BookImportError,
        unsupported_message="A importação inicial suporta EPUB e PDF textual",
        use_ocr=use_ocr,
        chunk_pages=chunk_pages,
    )


__all__ = [
    "BookImportError",
    "build_chapter_filename",
    "clean_book_slug",
    "default_output_dir",
    "extract_book_metadata",
    "html_to_markdown",
    "import_epub",
    "slugify",
    "_write_chapters",
    "_write_metadata",
]
