import json
from zipfile import ZIP_DEFLATED, ZipFile


def _create_sample_epub(path):
    with ZipFile(path, "w", compression=ZIP_DEFLATED) as archive:
        archive.writestr("mimetype", "application/epub+zip")
        archive.writestr(
            "META-INF/container.xml",
            """<?xml version='1.0' encoding='utf-8'?>
<container version='1.0' xmlns='urn:oasis:names:tc:opendocument:xmlns:container'>
  <rootfiles>
    <rootfile full-path='OEBPS/content.opf' media-type='application/oebps-package+xml'/>
  </rootfiles>
</container>
""",
        )
        archive.writestr(
            "OEBPS/content.opf",
            """<?xml version='1.0' encoding='utf-8'?>
<package version='3.0' xmlns='http://www.idpf.org/2007/opf' xmlns:dc='http://purl.org/dc/elements/1.1/'>
  <metadata>
    <dc:title>Livro KB</dc:title>
    <dc:creator>Autora KB</dc:creator>
    <dc:language>pt-BR</dc:language>
  </metadata>
  <manifest>
    <item id='chap1' href='chapter1.xhtml' media-type='application/xhtml+xml'/>
    <item id='chap2' href='chapter2.xhtml' media-type='application/xhtml+xml'/>
  </manifest>
  <spine>
    <itemref idref='chap1'/>
    <itemref idref='chap2'/>
  </spine>
</package>
""",
        )
        archive.writestr(
            "OEBPS/chapter1.xhtml",
            "<html><body><h1>Introdução</h1><p>Primeiro <strong>capítulo</strong>.</p></body></html>",
        )
        archive.writestr(
            "OEBPS/chapter2.xhtml",
            "<html><body><h1>Capítulo 1</h1><p>Segundo capítulo.</p></body></html>",
        )


def test_should_export_epub_to_markdown_chapters_inside_output_directory(tmp_path):
    from kb.book_import import import_epub

    source = tmp_path / "livro.epub"
    output_dir = tmp_path / "raw" / "books" / "livro"
    _create_sample_epub(source)

    written_files, metadata_path = import_epub(source, output_dir)

    assert len(written_files) == 2
    assert written_files[0].name == "01-introducao.md"
    assert metadata_path.exists()


def test_should_generate_metadata_json_with_book_information_in_kb_import(tmp_path):
    from kb.book_import import import_epub

    source = tmp_path / "livro.epub"
    output_dir = tmp_path / "raw" / "books" / "livro"
    _create_sample_epub(source)

    _, metadata_path = import_epub(source, output_dir)
    payload = json.loads(metadata_path.read_text(encoding="utf-8"))

    assert payload["book_title"] == "Livro KB"
    assert payload["book_author"] == "Autora KB"
    assert payload["book_language"] == "pt-BR"


def test_should_raise_clear_error_when_epub_is_invalid(tmp_path):
    from kb.book_import import import_epub

    source = tmp_path / "quebrado.epub"
    source.write_text("not a zip", encoding="utf-8")

    try:
        import_epub(source, tmp_path / "raw" / "books" / "quebrado")
    except ValueError as exc:
        assert "epub" in str(exc).lower()
    else:
        raise AssertionError("Esperava ValueError para EPUB inválido")


def test_should_use_complex_toc_label_when_epub_chapter_has_no_h1(tmp_path):
    from kb.book_import import import_epub

    source = tmp_path / "toc-complexo.epub"
    output_dir = tmp_path / "raw" / "books" / "toc-complexo"

    with ZipFile(source, "w", compression=ZIP_DEFLATED) as archive:
        archive.writestr("mimetype", "application/epub+zip")
        archive.writestr(
            "META-INF/container.xml",
            """<?xml version='1.0' encoding='utf-8'?>
<container version='1.0' xmlns='urn:oasis:names:tc:opendocument:xmlns:container'>
  <rootfiles>
    <rootfile full-path='OEBPS/content.opf' media-type='application/oebps-package+xml'/>
  </rootfiles>
</container>
""",
        )
        archive.writestr(
            "OEBPS/content.opf",
            """<?xml version='1.0' encoding='utf-8'?>
<package version='3.0' xmlns='http://www.idpf.org/2007/opf' xmlns:dc='http://purl.org/dc/elements/1.1/'>
  <metadata><dc:title>Livro com TOC</dc:title></metadata>
  <manifest>
    <item id='nav' href='nav.xhtml' media-type='application/xhtml+xml' properties='nav'/>
    <item id='chap1' href='text/chapter1.xhtml' media-type='application/xhtml+xml'/>
  </manifest>
  <spine><itemref idref='chap1'/></spine>
</package>
""",
        )
        archive.writestr(
            "OEBPS/nav.xhtml",
            """<html><body>
<nav epub:type='toc'>
  <ol>
    <li><a href='text/chapter1.xhtml'>Parte I — Origem</a>
      <ol><li><a href='text/chapter1.xhtml#secao-a'>Seção A</a></li></ol>
    </li>
  </ol>
</nav>
</body></html>""",
        )
        archive.writestr(
            "OEBPS/text/chapter1.xhtml",
            "<html><body><section><p>Conteúdo sem heading principal.</p></section></body></html>",
        )

    written_files, _ = import_epub(source, output_dir)

    assert written_files[0].name == "01-parte-i-origem.md"
    assert written_files[0].read_text(encoding="utf-8").startswith("# Parte I — Origem")


def test_should_fallback_to_h2_and_ignore_dirty_xhtml_noise(tmp_path):
    from kb.book_import import import_epub

    source = tmp_path / "sujo.epub"
    output_dir = tmp_path / "raw" / "books" / "sujo"

    with ZipFile(source, "w", compression=ZIP_DEFLATED) as archive:
        archive.writestr("mimetype", "application/epub+zip")
        archive.writestr(
            "META-INF/container.xml",
            """<?xml version='1.0' encoding='utf-8'?>
<container version='1.0' xmlns='urn:oasis:names:tc:opendocument:xmlns:container'>
  <rootfiles>
    <rootfile full-path='OPS/content.opf' media-type='application/oebps-package+xml'/>
  </rootfiles>
</container>
""",
        )
        archive.writestr(
            "OPS/content.opf",
            """<?xml version='1.0' encoding='utf-8'?>
<package version='3.0' xmlns='http://www.idpf.org/2007/opf' xmlns:dc='http://purl.org/dc/elements/1.1/'>
  <metadata><dc:title>Livro Sujo</dc:title></metadata>
  <manifest><item id='chap1' href='chapter-01.xhtml' media-type='application/xhtml+xml'/></manifest>
  <spine><itemref idref='chap1'/></spine>
</package>
""",
        )
        archive.writestr(
            "OPS/chapter-01.xhtml",
            "<html><head><title>Título Ruim</title><style>.x{display:none}</style><script>boom()</script></head><body><div><h2>Capítulo Limpo</h2><p>Texto <strong>útil</strong>.</p></div></body></html>",
        )

    written_files, _ = import_epub(source, output_dir)
    content = written_files[0].read_text(encoding="utf-8")

    assert written_files[0].name == "01-capitulo-limpo.md"
    assert content.startswith("# Capítulo Limpo")
    assert "**útil**" in content
    assert "boom()" not in content
    assert "display:none" not in content


def test_should_support_initial_textual_pdf_import(tmp_path):
    from kb.book_import import import_epub

    source = tmp_path / "relatorio.pdf"
    output_dir = tmp_path / "raw" / "books" / "relatorio"
    source.write_bytes(
        b"%PDF-1.4\n"
        b"1 0 obj<</Length 72>>stream\n"
        b"BT\n/F1 12 Tf\n72 720 Td\n(Relatorio Mensal) Tj\n0 -24 Td\n(Primeira linha do PDF.) Tj\n0 -24 Td\n[(Item) 120 ( A)] TJ\nET\n"
        b"endstream\nendobj\n"
    )

    written_files, metadata_path = import_epub(source, output_dir)
    payload = json.loads(metadata_path.read_text(encoding="utf-8"))
    content = written_files[0].read_text(encoding="utf-8")

    assert len(written_files) == 1
    assert written_files[0].name == "01-relatorio-mensal.md"
    assert content.startswith("# Relatorio Mensal")
    assert "Primeira linha do PDF." in content
    assert "Item A" in content
    assert payload["source_format"] == "pdf"


def test_should_split_textual_pdf_into_multiple_chapters_when_heading_markers_are_present(tmp_path):
    from kb.book_import import import_epub

    source = tmp_path / "livro-fragmentado.pdf"
    output_dir = tmp_path / "raw" / "books" / "livro-fragmentado"
    source.write_bytes(
        b"%PDF-1.4\n"
        b"1 0 obj<</Length 180>>stream\n"
        b"BT\n/F1 12 Tf\n72 720 Td\n(Meu Livro) Tj\n"
        b"0 -24 Td\n(Capitulo 1 - Comeco) Tj\n"
        b"0 -24 Td\n(Primeiro paragrafo.) Tj\n"
        b"0 -24 Td\n(Capitulo 2 - Fim) Tj\n"
        b"0 -24 Td\n(Segundo paragrafo.) Tj\nET\n"
        b"endstream\nendobj\n"
    )

    written_files, metadata_path = import_epub(source, output_dir)
    payload = json.loads(metadata_path.read_text(encoding="utf-8"))

    assert len(written_files) == 2
    assert written_files[0].name == "01-capitulo-1-comeco.md"
    assert written_files[1].name == "02-capitulo-2-fim.md"
    assert written_files[0].read_text(encoding="utf-8").startswith("# Capitulo 1 - Comeco")
    assert "Primeiro paragrafo." in written_files[0].read_text(encoding="utf-8")
    assert "Segundo paragrafo." in written_files[1].read_text(encoding="utf-8")
    assert payload["chapter_count"] == 2
    assert payload["book_title"] == "Meu Livro"
