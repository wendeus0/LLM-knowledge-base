from typer.testing import CliRunner


def test_archive_cli_dry_run_shows_preview_table(tmp_path, monkeypatch):
    from kb.cli import app

    wiki = tmp_path / "wiki"
    wiki.mkdir()
    (wiki / "orphan.md").write_text("conteudo")

    monkeypatch.setattr("kb.config.WIKI_DIR", wiki)

    runner = CliRunner()
    result = runner.invoke(app, ["archive", "--dry-run"])
    assert result.exit_code == 0
    assert "orphan.md" in result.output
    assert (wiki / "orphan.md").exists()
