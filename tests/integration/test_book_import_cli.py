from zipfile import ZIP_DEFLATED, ZipFile
from unittest.mock import patch

from typer.testing import CliRunner

from kb.cli import app


runner = CliRunner()


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
            "<html><body><h1>Introdução</h1><p>Primeiro capítulo.</p></body></html>",
        )
        archive.writestr(
            "OEBPS/chapter2.xhtml",
            "<html><body><h1>Capítulo 1</h1><p>Segundo capítulo.</p></body></html>",
        )


def test_should_import_book_via_cli_and_create_chapter_files(tmp_path):
    source = tmp_path / "livro.epub"
    output_dir = tmp_path / "raw" / "books" / "livro"
    _create_sample_epub(source)

    result = runner.invoke(app, ["import-book", str(source), "--output", str(output_dir)])

    assert result.exit_code == 0
    assert (output_dir / "01-introducao.md").exists()
    assert (output_dir / "metadata.json").exists()


def test_should_report_generated_chapter_count_and_output_path_when_cli_import_succeeds(tmp_path):
    source = tmp_path / "livro.epub"
    output_dir = tmp_path / "raw" / "books" / "livro"
    _create_sample_epub(source)

    result = runner.invoke(app, ["import-book", str(source), "--output", str(output_dir)])

    assert result.exit_code == 0
    assert "2" in result.stdout
    assert str(output_dir) in result.stdout


def test_should_fail_with_clear_message_when_cli_receives_missing_file(tmp_path):
    source = tmp_path / "ausente.epub"
    output_dir = tmp_path / "raw" / "books" / "livro"

    result = runner.invoke(app, ["import-book", str(source), "--output", str(output_dir)])

    assert result.exit_code != 0
    assert "não existe" in result.stdout.lower() or "not found" in result.stdout.lower()


def test_should_compile_imported_chapters_to_wiki_when_flag_is_enabled(tmp_path):
    source = tmp_path / "livro.epub"
    output_dir = tmp_path / "raw" / "books" / "livro"
    _create_sample_epub(source)

    with patch("kb.compile.compile_file") as mock_compile_file, patch("kb.compile.update_index") as mock_update_index:
        mock_compile_file.side_effect = [tmp_path / "wiki" / "chapter-1.md", tmp_path / "wiki" / "chapter-2.md"]

        result = runner.invoke(app, ["import-book", str(source), "--output", str(output_dir), "--compile"])

    assert result.exit_code == 0
    assert mock_compile_file.call_count == 2
    mock_update_index.assert_called_once()
    assert "capítulos compilados" in result.stdout


def test_should_compile_nested_imported_book_chapters_when_running_compile_command(tmp_path, monkeypatch):
    raw_dir = tmp_path / "raw"
    nested = raw_dir / "books" / "livro"
    nested.mkdir(parents=True)
    (nested / "01-introducao.md").write_text("# Introdução", encoding="utf-8")
    (nested / "metadata.json").write_text("{}", encoding="utf-8")

    monkeypatch.setattr("kb.compile.RAW_DIR", raw_dir)

    with patch("kb.compile.compile_file") as mock_compile_file, patch("kb.compile.update_index") as mock_update_index:
        mock_compile_file.return_value = tmp_path / "wiki" / "introducao.md"
        result = runner.invoke(app, ["compile"])

    assert result.exit_code == 0
    mock_compile_file.assert_called_once()
    mock_update_index.assert_called_once()
