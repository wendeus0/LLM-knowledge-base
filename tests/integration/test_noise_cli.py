"""RED — feature 011-corpus-noise-filter (RF-01, RF-02, RF-05, RF-06, RF-07 + casos de erro).

Seams: CLI `kb import-book` (default exclui ruído; `--keep-noise` preserva tudo),
CLI `kb noise scan|apply`, e contrato de metadata.json (`excluded_chapters`, `keep_noise`).
"""

import json
from zipfile import ZIP_DEFLATED, ZipFile

from typer.testing import CliRunner

from kb.cli import app

runner = CliRunner()

_CONTAINER = """<?xml version='1.0' encoding='utf-8'?>
<container version='1.0' xmlns='urn:oasis:names:tc:opendocument:xmlns:container'>
  <rootfiles>
    <rootfile full-path='OEBPS/content.opf' media-type='application/oebps-package+xml'/>
  </rootfiles>
</container>
"""


def _create_epub(path, chapters):
    """chapters: lista de (id, h1_ou_None, corpo)."""
    manifest = "\n".join(
        f"<item id='{cid}' href='{cid}.xhtml' media-type='application/xhtml+xml'/>"
        for cid, _, _ in chapters
    )
    spine = "\n".join(f"<itemref idref='{cid}'/>" for cid, _, _ in chapters)
    with ZipFile(path, "w", compression=ZIP_DEFLATED) as archive:
        archive.writestr("mimetype", "application/epub+zip")
        archive.writestr("META-INF/container.xml", _CONTAINER)
        archive.writestr(
            "OEBPS/content.opf",
            f"""<?xml version='1.0' encoding='utf-8'?>
<package version='3.0' xmlns='http://www.idpf.org/2007/opf' xmlns:dc='http://purl.org/dc/elements/1.1/'>
  <metadata>
    <dc:title>Livro Ruidoso</dc:title>
    <dc:creator>Autora KB</dc:creator>
    <dc:language>pt-BR</dc:language>
  </metadata>
  <manifest>{manifest}</manifest>
  <spine>{spine}</spine>
</package>
""",
        )
        for cid, h1, body in chapters:
            heading = f"<h1>{h1}</h1>" if h1 else ""
            archive.writestr(
                f"OEBPS/{cid}.xhtml",
                f"<html><body>{heading}<p>{body}</p></body></html>",
            )


_NOISY_CHAPTERS = [
    ("c1", "Elogios", "Melhor livro do ano, disse a crítica."),
    ("c2", "Prefácio", "Este prefácio explica como o livro nasceu."),
    ("c3", "Capítulo 1 — Fundamentos", "Conteúdo técnico real do livro."),
    ("c4", "Conclusão", "Síntese do argumento central do livro."),
    ("c5", "Agradecimentos", "Agradeço à minha família."),
    ("c6", "Posfácio", "Palavras finais do autor."),
]


def _import(tmp_path, extra_args=()):
    source = tmp_path / "livro.epub"
    output_dir = tmp_path / "raw" / "books" / "livro"
    _create_epub(source, _NOISY_CHAPTERS)
    result = runner.invoke(
        app, ["import-book", str(source), "--output", str(output_dir), *extra_args]
    )
    return result, output_dir


def _written_titles(output_dir):
    metadata = json.loads((output_dir / "metadata.json").read_text(encoding="utf-8"))
    return {chapter["title"] for chapter in metadata["chapters"]}, metadata


def test_should_exclude_noise_chapters_from_raw_when_importing(tmp_path):
    # RED: falha até 011-corpus-noise-filter ser implementada (RF-01)
    result, output_dir = _import(tmp_path)
    assert result.exit_code == 0
    titles, _ = _written_titles(output_dir)
    assert "Capítulo 1 — Fundamentos" in titles
    assert "Conclusão" in titles  # decisão A: conclusão é conteúdo
    assert "Prefácio" not in titles
    assert "Agradecimentos" not in titles
    assert "Elogios" not in titles
    assert "Posfácio" not in titles
    # relatório do que foi excluído aparece na saída
    assert "Prefácio" in result.output
    assert "Agradecimentos" in result.output


def test_should_record_excluded_chapters_in_metadata_json(tmp_path):
    # RED: falha até 011-corpus-noise-filter ser implementada (RF-01, trilha auditável)
    result, output_dir = _import(tmp_path)
    assert result.exit_code == 0
    _, metadata = _written_titles(output_dir)
    excluded = {entry["title"]: entry["category"] for entry in metadata["excluded_chapters"]}
    assert excluded == {
        "Elogios": "elogios",
        "Prefácio": "prefacio",
        "Agradecimentos": "agradecimentos",
        "Posfácio": "encerramento",
    }


def test_should_import_all_chapters_when_keep_noise_flag(tmp_path):
    # RED: falha até 011-corpus-noise-filter ser implementada (RF-02)
    result, output_dir = _import(tmp_path, extra_args=("--keep-noise",))
    assert result.exit_code == 0
    titles, metadata = _written_titles(output_dir)
    assert titles == {c[1] for c in _NOISY_CHAPTERS}
    assert metadata["keep_noise"] is True
    assert metadata["excluded_chapters"] == []


def test_should_exclude_nothing_and_warn_when_book_has_no_chapter_titles(tmp_path):
    # RED: falha até 011-corpus-noise-filter ser implementada (caso de erro: sem títulos)
    source = tmp_path / "sem-titulos.epub"
    output_dir = tmp_path / "raw" / "books" / "sem-titulos"
    _create_epub(
        source,
        [("c1", None, "Texto sem heading."), ("c2", None, "Mais texto sem heading.")],
    )
    result = runner.invoke(app, ["import-book", str(source), "--output", str(output_dir)])
    assert result.exit_code == 0
    metadata = json.loads((output_dir / "metadata.json").read_text(encoding="utf-8"))
    assert metadata["excluded_chapters"] == []
    assert len(metadata["chapters"]) == 2
    assert "classificar" in result.output.lower()  # warning de classificação impossível


def _seed_dirty_vault(tmp_path, monkeypatch):
    """Vault com livro contendo capítulo-ruído já importado + artigo wiki derivado."""
    raw = tmp_path / "raw"
    wiki = tmp_path / "wiki"
    archive_dir = tmp_path / "archive"
    book_dir = raw / "books" / "livro"
    book_dir.mkdir(parents=True)
    wiki.mkdir()
    archive_dir.mkdir()

    (book_dir / "001-prefacio.md").write_text("# Prefácio\n\nComo o livro nasceu.\n", encoding="utf-8")
    (book_dir / "002-capitulo-1.md").write_text("# Capítulo 1\n\nConteúdo real.\n", encoding="utf-8")
    (book_dir / "metadata.json").write_text(
        json.dumps(
            {
                "source_file": "livro.epub",
                "book_title": "Livro Ruidoso",
                "book_author": "Autora KB",
                "chapter_count": 2,
                "chapters": [
                    {"index": 1, "title": "Prefácio", "file": "001-prefacio.md", "source_href": "c1.xhtml"},
                    {"index": 2, "title": "Capítulo 1", "file": "002-capitulo-1.md", "source_href": "c2.xhtml"},
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (wiki / "prefacio-livro-ruidoso.md").write_text(
        "---\ntitle: Prefácio — Livro Ruidoso\ntopic: general\ntags: []\nsource: 001-prefacio.md\n---\n\nResumo do prefácio.\n",
        encoding="utf-8",
    )

    monkeypatch.setattr("kb.config.RAW_DIR", raw)
    monkeypatch.setattr("kb.config.WIKI_DIR", wiki)
    monkeypatch.setattr("kb.config.ARCHIVE_DIR", archive_dir)
    return raw, wiki, archive_dir


def test_should_list_noise_candidates_without_changes_when_scan(tmp_path, monkeypatch):
    # RED: falha até 011-corpus-noise-filter ser implementada (RF-05)
    raw, wiki, _ = _seed_dirty_vault(tmp_path, monkeypatch)
    result = runner.invoke(app, ["noise", "scan"])
    assert result.exit_code == 0
    assert "001-prefacio.md" in result.output
    assert "prefacio-livro-ruidoso.md" in result.output  # artigo wiki derivado, via rastro
    assert "002-capitulo-1.md" not in result.output
    # dry-run: nada mudou
    assert (raw / "books" / "livro" / "001-prefacio.md").exists()
    assert (wiki / "prefacio-livro-ruidoso.md").exists()


def test_should_move_candidates_to_archive_when_apply(tmp_path, monkeypatch):
    # RED: falha até 011-corpus-noise-filter ser implementada (RF-06: arquiva, nunca deleta)
    raw, wiki, archive_dir = _seed_dirty_vault(tmp_path, monkeypatch)
    result = runner.invoke(app, ["noise", "apply"])
    assert result.exit_code == 0
    assert not (raw / "books" / "livro" / "001-prefacio.md").exists()
    assert not (wiki / "prefacio-livro-ruidoso.md").exists()
    # conteúdo preservado no archive (nunca deletado)
    archived = list(archive_dir.rglob("*.md"))
    archived_texts = [p.read_text(encoding="utf-8") for p in archived]
    assert any("Como o livro nasceu." in text for text in archived_texts)
    assert any("Resumo do prefácio." in text for text in archived_texts)
    # conteúdo real intacto
    assert (raw / "books" / "livro" / "002-capitulo-1.md").exists()


def test_should_be_noop_when_apply_runs_on_clean_corpus(tmp_path, monkeypatch):
    # RED: falha até 011-corpus-noise-filter ser implementada (RF-07: idempotência)
    _seed_dirty_vault(tmp_path, monkeypatch)
    first = runner.invoke(app, ["noise", "apply"])
    assert first.exit_code == 0
    second = runner.invoke(app, ["noise", "apply"])
    assert second.exit_code == 0
    assert "0" in second.output  # relatório indica zero candidatos


def test_should_suffix_when_archive_name_conflicts(tmp_path, monkeypatch):
    # RED: falha até 011-corpus-noise-filter ser implementada (caso de erro: conflito de nome)
    _, _, archive_dir = _seed_dirty_vault(tmp_path, monkeypatch)
    conflicting = archive_dir / "001-prefacio.md"
    conflicting.write_text("conteudo pre-existente do archive", encoding="utf-8")
    result = runner.invoke(app, ["noise", "apply"])
    assert result.exit_code == 0
    assert conflicting.read_text(encoding="utf-8") == "conteudo pre-existente do archive"
    archived_texts = [p.read_text(encoding="utf-8") for p in archive_dir.rglob("*.md")]
    assert any("Como o livro nasceu." in text for text in archived_texts)


def test_should_resume_remaining_files_when_apply_partially_done(tmp_path, monkeypatch):
    # RED: falha até 011-corpus-noise-filter ser implementada (caso de erro: retomada pós-falha)
    raw, wiki, archive_dir = _seed_dirty_vault(tmp_path, monkeypatch)
    # simula apply interrompido: capítulo raw já movido, artigo wiki ainda não
    moved = archive_dir / "001-prefacio.md"
    original = raw / "books" / "livro" / "001-prefacio.md"
    moved.write_text(original.read_text(encoding="utf-8"), encoding="utf-8")
    original.unlink()
    result = runner.invoke(app, ["noise", "apply"])
    assert result.exit_code == 0
    assert not (wiki / "prefacio-livro-ruidoso.md").exists()
    archived_texts = [p.read_text(encoding="utf-8") for p in archive_dir.rglob("*.md")]
    assert any("Resumo do prefácio." in text for text in archived_texts)


def test_should_report_kept_chapter_with_noise_term_mid_title(tmp_path):
    # RED→GREEN na mesma sessão (RF-04: ambíguo mantido E listado como não classificado)
    source = tmp_path / "ambiguo.epub"
    output_dir = tmp_path / "raw" / "books" / "ambiguo"
    _create_epub(
        source,
        [
            ("c1", "O que os agradecimentos revelam", "Capítulo de conteúdo real."),
            ("c2", "Capítulo 2", "Mais conteúdo."),
        ],
    )
    result = runner.invoke(app, ["import-book", str(source), "--output", str(output_dir)])
    assert result.exit_code == 0
    metadata = json.loads((output_dir / "metadata.json").read_text(encoding="utf-8"))
    titles = {chapter["title"] for chapter in metadata["chapters"]}
    assert "O que os agradecimentos revelam" in titles  # mantido
    assert "não classificado" in result.output
    assert "O que os agradecimentos revelam" in result.output


def test_should_scan_wiki_article_by_frontmatter_title_without_metadata_trail(tmp_path, monkeypatch):
    # RED→GREEN: vault da era VM não tem raw/books/metadata.json — classifica pelo title
    raw = tmp_path / "raw"
    wiki = tmp_path / "wiki"
    archive_dir = tmp_path / "archive"
    raw.mkdir()
    wiki.mkdir()
    archive_dir.mkdir()
    (wiki / "prefacio-ao-ddd.md").write_text(
        "---\ntitle: \"Prefácio ao Domain-Driven Design\"\ntopic: general\ntags: []\nsource: 03-preface.md\n---\n\nResumo.\n",
        encoding="utf-8",
    )
    (wiki / "pagina-de-copyright.md").write_text(
        "---\ntitle: Página de copyright\ntopic: general\ntags: []\nsource: 02-copyright.md\n---\n\nMetadados.\n",
        encoding="utf-8",
    )
    (wiki / "agregados.md").write_text(
        "---\ntitle: Agregados (Aggregates)\ntopic: general\ntags: []\nsource: 10-aggregates.md\n---\n\nConteúdo real.\n",
        encoding="utf-8",
    )
    monkeypatch.setattr("kb.config.RAW_DIR", raw)
    monkeypatch.setattr("kb.config.WIKI_DIR", wiki)
    monkeypatch.setattr("kb.config.ARCHIVE_DIR", archive_dir)

    result = runner.invoke(app, ["noise", "scan"])
    assert result.exit_code == 0
    assert "prefacio-ao-ddd.md" in result.output
    assert "pagina-de-copyright.md" in result.output
    assert "agregados.md" not in result.output


def test_should_never_scan_underscore_infra_files(tmp_path, monkeypatch):
    # RED→GREEN: _index.md (title: Index) e _pipeline/ são infra da wiki, nunca candidatos
    raw = tmp_path / "raw"
    wiki = tmp_path / "wiki"
    archive_dir = tmp_path / "archive"
    raw.mkdir()
    wiki.mkdir()
    archive_dir.mkdir()
    (wiki / "_index.md").write_text("---\ntitle: Index\n---\n\n# Knowledge Base Index\n", encoding="utf-8")
    (wiki / "_pipeline").mkdir()
    (wiki / "_pipeline" / "prefacio-notas.md").write_text("---\ntitle: Prefácio\n---\n\nnota de pipeline\n", encoding="utf-8")
    (wiki / "prefacio-real.md").write_text("---\ntitle: Prefácio\ntopic: general\ntags: []\nsource: x.md\n---\n\nruído real\n", encoding="utf-8")
    monkeypatch.setattr("kb.config.RAW_DIR", raw)
    monkeypatch.setattr("kb.config.WIKI_DIR", wiki)
    monkeypatch.setattr("kb.config.ARCHIVE_DIR", archive_dir)

    result = runner.invoke(app, ["noise", "scan"])
    assert result.exit_code == 0
    assert "_index.md" not in result.output
    assert "prefacio-notas.md" not in result.output
    assert "prefacio-real.md" in result.output
