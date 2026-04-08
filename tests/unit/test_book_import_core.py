import sys
import types
from zipfile import ZIP_DEFLATED, ZipFile

import pytest

from kb import book_import_core as core


def _write_zip(path, files):
    with ZipFile(path, "w", compression=ZIP_DEFLATED) as archive:
        for name, content in files.items():
            archive.writestr(name, content)


def _epub_container(rootfile_path="OPS/content.opf"):
    return f"""<?xml version='1.0' encoding='utf-8'?>
<container version='1.0' xmlns='urn:oasis:names:tc:opendocument:xmlns:container'>
  <rootfiles>
    <rootfile full-path='{rootfile_path}' media-type='application/oebps-package+xml'/>
  </rootfiles>
</container>
"""


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


def test_should_extract_epub_assets_with_deduplicated_names_and_image_map(tmp_path):
    source = tmp_path / "assets.epub"
    _write_zip(
        source,
        {
            "mimetype": "application/epub+zip",
            "META-INF/container.xml": _epub_container(),
            "OPS/content.opf": """<?xml version='1.0' encoding='utf-8'?>
<package xmlns='http://www.idpf.org/2007/opf'>
  <manifest>
    <item id='img1' href='images/cover.png' media-type='image/png'/>
    <item id='img2' href='art/cover.png' media-type='image/png'/>
    <item id='img3' href='missing/ghost.png' media-type='image/png'/>
    <item id='chap1' href='chapter1.xhtml' media-type='application/xhtml+xml'/>
  </manifest>
</package>
""",
            "OPS/images/cover.png": b"cover-1",
            "OPS/art/cover.png": b"cover-2",
            "OPS/chapter1.xhtml": "<html><body><p>Chapter</p></body></html>",
        },
    )

    with ZipFile(source) as archive:
        rootfile_path, package_root = core._parse_package_document(
            archive, core.BookConversionError
        )
        assets, image_map = core._extract_epub_assets(
            archive, rootfile_path, package_root
        )

    assert [asset["file"] for asset in assets] == [
        "images/cover.png",
        "images/cover-2.png",
    ]
    assert assets[0]["content"] == b"cover-1"
    assert assets[1]["content"] == b"cover-2"
    assert image_map["OPS/images/cover.png"] == "images/cover.png"
    assert image_map["cover.png"] == "images/cover-2.png"


def test_should_parse_ncx_tree_and_flatten_nested_entries(tmp_path):
    source = tmp_path / "toc.epub"
    _write_zip(
        source,
        {"toc.ncx": """<?xml version='1.0' encoding='utf-8'?>
<ncx xmlns='http://www.daisy.org/z3986/2005/ncx/'>
  <navMap>
    <navPoint>
      <navLabel><text>Part 1</text></navLabel>
      <content src='text/ch1.xhtml'/>
      <navPoint>
        <navLabel><text>Child A</text></navLabel>
        <content src='text/ch1.xhtml#child-a'/>
      </navPoint>
    </navPoint>
    <navPoint>
      <navLabel><text>Ignored</text></navLabel>
    </navPoint>
  </navMap>
</ncx>
"""},
    )

    invalid_nav_point = core.SafeET.fromstring(
        "<navPoint><content src='chapter.xhtml'/></navPoint>"
    )
    assert core._parse_ncx_navpoint(invalid_nav_point, "OPS/toc.ncx") is None

    with ZipFile(source) as archive:
        toc_tree = core._parse_ncx_toc_tree(archive, "toc.ncx")

    toc_map = core._flatten_toc_map(toc_tree)

    assert len(toc_tree) == 1
    assert toc_tree[0]["title"] == "Part 1"
    assert toc_tree[0]["children"][0]["anchor"] == "child-a"
    assert toc_map == {"text/ch1.xhtml": "Part 1"}


def test_should_parse_nav_document_tree_from_xml_and_html_fallback(tmp_path):
    source = tmp_path / "nav.epub"
    _write_zip(
        source,
        {
            "OPS/nav.xhtml": """<html xmlns='http://www.w3.org/1999/xhtml' xmlns:epub='http://www.idpf.org/2007/ops'>
  <body>
    <nav epub:type='toc'>
      <ol>
        <li>
          <span><a href='text/ch1.xhtml'>Chapter 1</a></span>
          <ol><li><a href='text/ch1.xhtml#sec-1'>Section 1</a></li></ol>
        </li>
      </ol>
    </nav>
  </body>
</html>""",
            "OPS/fallback-nav.xhtml": "<html><body><nav role='doc-toc'><a href='text/ch2.xhtml'>Chapter 2</a></nav>",
            "OPS/no-list.xhtml": """<html xmlns='http://www.w3.org/1999/xhtml' xmlns:epub='http://www.idpf.org/2007/ops'>
  <body><nav epub:type='toc'><p>No list here</p></nav></body>
</html>""",
        },
    )

    with ZipFile(source) as archive:
        xml_tree = core._parse_nav_document_toc_tree(archive, "OPS/nav.xhtml")
        fallback_tree = core._parse_nav_document_toc_tree(
            archive, "OPS/fallback-nav.xhtml"
        )
        empty_tree = core._parse_nav_document_toc_tree(archive, "OPS/no-list.xhtml")
        missing_tree = core._parse_nav_document_toc_tree(archive, "OPS/missing.xhtml")

    assert xml_tree[0]["title"] == "Chapter 1"
    assert xml_tree[0]["children"][0]["anchor"] == "sec-1"
    assert fallback_tree[0]["file_href"] == "OPS/text/ch2.xhtml"
    assert empty_tree == []
    assert missing_tree == []


def test_should_build_toc_data_from_nav_and_fallback_to_ncx(tmp_path):
    nav_source = tmp_path / "nav-first.epub"
    _write_zip(
        nav_source,
        {
            "mimetype": "application/epub+zip",
            "META-INF/container.xml": _epub_container(),
            "OPS/content.opf": """<?xml version='1.0' encoding='utf-8'?>
<package xmlns='http://www.idpf.org/2007/opf'>
  <manifest>
    <item id='nav' href='nav.xhtml' media-type='application/xhtml+xml' properties='nav'/>
    <item id='chap1' href='text/ch1.xhtml' media-type='application/xhtml+xml'/>
  </manifest>
</package>
""",
            "OPS/nav.xhtml": """<html xmlns='http://www.w3.org/1999/xhtml' xmlns:epub='http://www.idpf.org/2007/ops'>
  <body><nav epub:type='toc'><ol><li><a href='text/ch1.xhtml'>Nav chapter</a></li></ol></nav></body>
</html>""",
        },
    )
    ncx_source = tmp_path / "ncx-fallback.epub"
    _write_zip(
        ncx_source,
        {
            "mimetype": "application/epub+zip",
            "META-INF/container.xml": _epub_container(),
            "OPS/content.opf": """<?xml version='1.0' encoding='utf-8'?>
<package xmlns='http://www.idpf.org/2007/opf'>
  <manifest>
    <item id='nav' href='nav.xhtml' media-type='application/xhtml+xml' properties='nav'/>
    <item id='ncx' href='toc.ncx' media-type='application/x-dtbncx+xml'/>
    <item id='chap1' href='text/ch1.xhtml' media-type='application/xhtml+xml'/>
  </manifest>
</package>
""",
            "OPS/nav.xhtml": "<html><body><nav epub:type='toc'><p>broken",
            "OPS/toc.ncx": """<?xml version='1.0' encoding='utf-8'?>
<ncx xmlns='http://www.daisy.org/z3986/2005/ncx/'>
  <navMap><navPoint><navLabel><text>NCX chapter</text></navLabel><content src='text/ch1.xhtml'/></navPoint></navMap>
</ncx>
""",
        },
    )

    with ZipFile(nav_source) as archive:
        rootfile_path, package_root = core._parse_package_document(
            archive, core.BookConversionError
        )
        toc_tree, toc_map, toc_source = core._build_toc_data(
            archive, rootfile_path, package_root
        )

    assert toc_source == "nav"
    assert toc_tree[0]["title"] == "Nav chapter"
    assert toc_map == {"OPS/text/ch1.xhtml": "Nav chapter"}

    with ZipFile(ncx_source) as archive:
        rootfile_path, package_root = core._parse_package_document(
            archive, core.BookConversionError
        )
        toc_tree, toc_map, toc_source = core._build_toc_data(
            archive, rootfile_path, package_root
        )

    assert toc_source == "ncx"
    assert toc_tree[0]["title"] == "NCX chapter"
    assert toc_map == {"OPS/text/ch1.xhtml": "NCX chapter"}


@pytest.mark.parametrize(
    ("label", "manifest_block", "files", "expected_source", "expected_title"),
    [
        (
            "nav wins over ncx",
            """
  <manifest>
    <item id='nav' href='nav.xhtml' media-type='application/xhtml+xml' properties='nav'/>
    <item id='ncx' href='toc.ncx' media-type='application/x-dtbncx+xml'/>
    <item id='chap1' href='text/ch1.xhtml' media-type='application/xhtml+xml'/>
  </manifest>
""",
            {
                "OPS/nav.xhtml": """<html xmlns='http://www.w3.org/1999/xhtml' xmlns:epub='http://www.idpf.org/2007/ops'><body><nav epub:type='toc'><ol><li><a href='text/ch1.xhtml'>Nav wins</a></li></ol></nav></body></html>""",
                "OPS/toc.ncx": """<?xml version='1.0' encoding='utf-8'?><ncx xmlns='http://www.daisy.org/z3986/2005/ncx/'><navMap><navPoint><navLabel><text>NCX loses</text></navLabel><content src='text/ch1.xhtml'/></navPoint></navMap></ncx>""",
            },
            "nav",
            "Nav wins",
        ),
        (
            "ncx fallback when nav empty",
            """
  <manifest>
    <item id='nav' href='nav.xhtml' media-type='application/xhtml+xml' properties='nav'/>
    <item id='ncx' href='toc.ncx' media-type='application/x-dtbncx+xml'/>
    <item id='chap1' href='text/ch1.xhtml' media-type='application/xhtml+xml'/>
  </manifest>
""",
            {
                "OPS/nav.xhtml": """<html xmlns='http://www.w3.org/1999/xhtml' xmlns:epub='http://www.idpf.org/2007/ops'><body><nav epub:type='toc'><p>sem lista</p></nav></body></html>""",
                "OPS/toc.ncx": """<?xml version='1.0' encoding='utf-8'?><ncx xmlns='http://www.daisy.org/z3986/2005/ncx/'><navMap><navPoint><navLabel><text>NCX fallback</text></navLabel><content src='text/ch1.xhtml'/></navPoint></navMap></ncx>""",
            },
            "ncx",
            "NCX fallback",
        ),
        (
            "none when no toc survives",
            """
  <manifest>
    <item id='nav' href='nav.xhtml' media-type='application/xhtml+xml' properties='nav'/>
    <item id='chap1' href='text/ch1.xhtml' media-type='application/xhtml+xml'/>
  </manifest>
""",
            {
                "OPS/nav.xhtml": """<html xmlns='http://www.w3.org/1999/xhtml' xmlns:epub='http://www.idpf.org/2007/ops'><body><nav epub:type='toc'><p>sem lista</p></nav></body></html>"""
            },
            "none",
            None,
        ),
    ],
    ids=lambda case: case,
)
def test_should_follow_toc_source_contract_table(
    tmp_path, label, manifest_block, files, expected_source, expected_title
):
    source = tmp_path / f"{core.slugify(label)}.epub"
    payload = {
        "mimetype": "application/epub+zip",
        "META-INF/container.xml": _epub_container(),
        "OPS/content.opf": f"""<?xml version='1.0' encoding='utf-8'?>
<package xmlns='http://www.idpf.org/2007/opf'>
{manifest_block}
</package>
""",
        "OPS/text/ch1.xhtml": "<html><body><p>capitulo</p></body></html>",
    }
    payload.update(files)
    _write_zip(source, payload)

    with ZipFile(source) as archive:
        rootfile_path, package_root = core._parse_package_document(
            archive, core.BookConversionError
        )
        toc_tree, toc_map, toc_source = core._build_toc_data(
            archive, rootfile_path, package_root
        )

    assert toc_source == expected_source
    if expected_title is None:
        assert toc_tree == []
        assert toc_map == {}
    else:
        assert toc_tree[0]["title"] == expected_title
        assert list(toc_map.values()) == [expected_title]


@pytest.mark.parametrize(
    ("base_href", "src", "image_map", "expected"),
    [
        (
            "OPS/text/ch1.xhtml",
            "../images/cover.png",
            {
                "OPS/images/cover.png": "images/right.png",
                "cover.png": "images/wrong.png",
            },
            "images/right.png",
        ),
        (
            "OPS/text/ch1.xhtml",
            "cover.png",
            {
                "OPS/images/cover.png": "images/cover-a.png",
                "OPS/art/cover.png": "images/cover-b.png",
            },
            None,
        ),
        (
            None,
            "cover.png",
            {"OPS/images/cover.png": "images/cover.png"},
            "images/cover.png",
        ),
    ],
    ids=["full-path-before-basename", "ambiguous-basename", "unique-basename"],
)
def test_should_resolve_image_reference_by_contract(
    base_href, src, image_map, expected
):
    assert core._resolve_image_reference(base_href, src, image_map) == expected


def test_should_report_stable_rootfile_errors(tmp_path):
    missing_container = tmp_path / "missing-container.epub"
    _write_zip(missing_container, {"mimetype": "application/epub+zip"})

    with ZipFile(missing_container) as archive:
        with pytest.raises(
            core.BookConversionError, match="META-INF/container.xml ausente"
        ):
            core._find_rootfile_path(archive, core.BookConversionError)

    missing_rootfile = tmp_path / "missing-rootfile.epub"
    _write_zip(
        missing_rootfile,
        {
            "mimetype": "application/epub+zip",
            "META-INF/container.xml": """<?xml version='1.0' encoding='utf-8'?><container xmlns='urn:oasis:names:tc:opendocument:xmlns:container'><rootfiles><rootfile media-type='application/oebps-package+xml'/></rootfiles></container>""",
        },
    )

    with ZipFile(missing_rootfile) as archive:
        with pytest.raises(core.BookConversionError, match="rootfile não encontrado"):
            core._find_rootfile_path(archive, core.BookConversionError)


def test_should_extract_epub_metadata_or_raise_stable_epub_category(tmp_path):
    malformed = tmp_path / "malformed.epub"
    _write_zip(
        malformed,
        {
            "mimetype": "application/epub+zip",
            "META-INF/container.xml": _epub_container(),
            "OPS/content.opf": b"<package><metadata>",
        },
    )

    with pytest.raises(core.BookConversionError, match="XML inseguro ou malformado"):
        core.extract_book_metadata(malformed)

    broken_zip = tmp_path / "broken.epub"
    broken_zip.write_text("not a zip", encoding="utf-8")

    with pytest.raises(core.BookConversionError, match="EPUB inválido ou corrompido"):
        core.extract_book_metadata(broken_zip)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (
            "Livro Muito Grande Com Varias Palavras Para Preservar Limite Sem Cortar Termo No Meio Archive Copy 2024 Final Edition",
            "livro-muito-grande-com-varias-palavras-para-preservar",
        ),
        ("Título com ç ã é e símbolos !!!", "titulo-com-c-a-e-e-simbolos"),
        ("---", "capitulo"),
    ],
)
def test_should_normalize_slug_contract(raw, expected):
    target = core.clean_book_slug(raw) if raw != "---" else core.slugify(raw)
    assert target == expected
    assert len(target) <= 60


def test_should_convert_html_to_markdown_without_overfitting_layout():
    markdown = core.html_to_markdown("""
<article>
  <p>Intro <strong>forte</strong> e <em>clara</em>.</p>
  <script>boom()</script>
  <style>.x{display:none}</style>
  <ul><li>Primeiro</li><li>Segundo</li></ul>
</article>
""")

    assert "Intro **forte** e *clara*." in markdown
    assert "boom()" not in markdown
    assert "display:none" not in markdown
    assert markdown.index("Primeiro") < markdown.index("Segundo")
    assert "- Primeiro" in markdown
    assert "- Segundo" in markdown


def test_should_return_pdf_metadata_and_reject_missing_or_unsupported_sources(tmp_path):
    pdf_path = tmp_path / "book.pdf"
    pdf_path.write_bytes(b"%PDF-1.4")

    metadata = core.extract_book_metadata(pdf_path)

    assert metadata["title"] == "book"
    assert metadata["assets"] == []

    with pytest.raises(core.BookConversionError, match="não existe"):
        core.extract_book_metadata(tmp_path / "missing.epub")

    txt_path = tmp_path / "book.txt"
    txt_path.write_text("plain text", encoding="utf-8")

    with pytest.raises(core.BookConversionError, match="Formato não suportado"):
        core.extract_book_metadata(txt_path)


def test_should_merge_overflowing_pdf_toc_entries_into_chunked_chapters(
    tmp_path, monkeypatch
):
    source = tmp_path / "large.pdf"
    source.write_bytes(b"%PDF-1.4")
    pages = [f"Page {index}" for index in range(1, 25)]
    toc = [
        (1, "Part 1", 1),
        (1, "Part 2", 4),
        (1, "Part 3", 7),
        (1, "Part 4", 13),
        (1, "Part 5", 16),
        (1, "Part 6", 19),
    ]
    _mock_fitz(monkeypatch, toc=toc, pages=pages)

    chapters, metadata = core._extract_chapters_from_pdf(
        source, core.BookConversionError, chunk_pages=10
    )

    assert [chapter["title"] for chapter in chapters] == ["Part 1", "Part 4"]
    assert metadata["chapter_source"] == "toc_merged"
    assert "Page 1" in chapters[0]["content"]
    assert "Page 13" in chapters[1]["content"]


def test_should_write_assets_and_cover_text_and_pdf_error_helpers(
    tmp_path, monkeypatch
):
    assets_dir = tmp_path / "assets"
    written = core.write_assets(
        assets_dir,
        [{"file": "images/cover.png", "content": b"png-bytes"}],
    )

    assert written == [assets_dir / "images" / "cover.png"]
    assert written[0].read_bytes() == b"png-bytes"
    assert core._normalize_pdf_text("A\n\n\nB\n\t \nC") == "A\n\nB\n\nC"
    assert core._is_garbled("x" * 90 + "\x01" * 10) is True
    assert core._is_garbled("short text") is False

    source = tmp_path / "broken.pdf"
    source.write_bytes(b"%PDF-1.4")
    monkeypatch.setitem(
        sys.modules,
        "fitz",
        types.SimpleNamespace(
            open=lambda _: (_ for _ in ()).throw(RuntimeError("boom"))
        ),
    )

    with pytest.raises(core.BookConversionError, match="PDF inválido ou corrompido"):
        core._get_pdf_pages(source, core.BookConversionError)


def test_should_raise_ocr_and_garbled_errors_for_problematic_pdf_inputs(
    tmp_path, monkeypatch
):
    source = tmp_path / "ocr.pdf"
    source.write_bytes(b"%PDF-1.4")

    class FakeDoc:
        def get_toc(self):
            return []

        def __iter__(self):
            return iter([])

        def close(self):
            return None

    monkeypatch.setitem(
        sys.modules, "fitz", types.SimpleNamespace(open=lambda _: FakeDoc())
    )
    monkeypatch.setitem(
        sys.modules,
        "pdf2image",
        types.SimpleNamespace(
            convert_from_path=lambda _: (_ for _ in ()).throw(
                RuntimeError("ocr failed")
            )
        ),
    )
    monkeypatch.setitem(
        sys.modules,
        "pytesseract",
        types.SimpleNamespace(image_to_string=lambda image, lang: "unused"),
    )

    with pytest.raises(
        core.BookConversionError, match="Erro ao converter PDF para imagens"
    ):
        core._get_pdf_pages(source, core.BookConversionError, use_ocr=True)

    _mock_fitz(monkeypatch, toc=[], pages=["A" * 90 + "\x01" * 10])

    with pytest.raises(core.BookConversionError, match="encoding de fonte inválido"):
        core._get_pdf_pages(source, core.BookConversionError)
