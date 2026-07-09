# OCR is out of scope due to system dependency.
import sys
import types

import pytest

from kb import book_import_pdf as pdf


class PDFTestError(Exception):
    pass


def _mock_fitz(monkeypatch, *, toc, pages):
    class FakePage:
        def __init__(self, text):
            self.text = text

        def get_text(self):
            return self.text

    class FakeDoc:
        def get_toc(self):
            return toc

        def __iter__(self):
            return iter([FakePage(text) for text in pages])

        def close(self):
            return None

    monkeypatch.setitem(
        sys.modules, "fitz", types.SimpleNamespace(open=lambda _: FakeDoc())
    )


def test_should_chunk_by_toc_when_pdf_outline_exists(tmp_path, monkeypatch):
    """
    Dado um PDF com outline de nivel 1,
    Quando os capitulos sao extraidos,
    Entao os chunks devem seguir os capitulos do outline.
    """
    source = tmp_path / "book.pdf"
    source.write_bytes(b"%PDF-1.4")
    pages = [f"Page {index} content" for index in range(1, 7)]
    toc = [
        (1, "Intro", 1),
        (2, "Ignored subsection", 2),
        (1, "Deep Dive", 4),
    ]
    _mock_fitz(monkeypatch, toc=toc, pages=pages)

    chapters, metadata = pdf._extract_chapters_from_pdf(source, PDFTestError)

    assert [chapter["title"] for chapter in chapters] == ["Intro", "Deep Dive"]
    assert chapters[0]["content"] == "Page 1 content\nPage 2 content\nPage 3 content"
    assert chapters[1]["content"] == "Page 4 content\nPage 5 content\nPage 6 content"
    assert metadata["chapter_source"] == "toc"
    assert metadata["toc_source"] == "pdf_outline"
    assert metadata["toc"] == [
        {"title": "Intro", "page": 1},
        {"title": "Deep Dive", "page": 4},
    ]


def test_should_chunk_by_page_blocks_when_pdf_outline_is_missing(tmp_path, monkeypatch):
    """
    Dado um PDF sem outline,
    Quando os capitulos sao extraidos,
    Entao os chunks devem ser blocos de paginas.
    """
    source = tmp_path / "book.pdf"
    source.write_bytes(b"%PDF-1.4")
    pages = [f"Page {index} content" for index in range(1, 8)]
    _mock_fitz(monkeypatch, toc=[], pages=pages)

    chapters, metadata = pdf._extract_chapters_from_pdf(
        source, PDFTestError, chunk_pages=3
    )

    assert [chapter["title"] for chapter in chapters] == [
        "Páginas 1–3",
        "Páginas 4–6",
        "Páginas 7–7",
    ]
    assert chapters[0]["content"] == "Page 1 content\nPage 2 content\nPage 3 content"
    assert chapters[2]["content"] == "Page 7 content"
    assert metadata["chapter_source"] == "page_chunks"
    assert metadata["toc"] == []


def test_should_derive_chapter_title_when_outline_entry_is_long(tmp_path, monkeypatch):
    """
    Dado um PDF com titulo longo no outline,
    Quando os capitulos sao extraidos,
    Entao o titulo do capitulo deve ser truncado de forma estavel.
    """
    source = tmp_path / "book.pdf"
    source.write_bytes(b"%PDF-1.4")
    long_title = "A" * 130
    _mock_fitz(
        monkeypatch,
        toc=[(1, long_title, 1), (1, "Second", 2)],
        pages=["First page", "Second page"],
    )

    chapters, metadata = pdf._extract_chapters_from_pdf(source, PDFTestError)

    assert chapters[0]["title"] == "A" * 120
    assert metadata["toc"][0] == {"title": "A" * 120, "page": 1}


def test_should_raise_error_when_pdf_is_corrupted(tmp_path, monkeypatch):
    """
    Dado um PDF corrompido,
    Quando a leitura de paginas falha,
    Entao deve levantar a classe de erro recebida pelo modulo.
    """
    source = tmp_path / "broken.pdf"
    source.write_bytes(b"%PDF-1.4")
    monkeypatch.setitem(
        sys.modules,
        "fitz",
        types.SimpleNamespace(
            open=lambda _: (_ for _ in ()).throw(RuntimeError("boom"))
        ),
    )

    with pytest.raises(PDFTestError, match="PDF inválido ou corrompido"):
        pdf._get_pdf_pages(source, PDFTestError)
