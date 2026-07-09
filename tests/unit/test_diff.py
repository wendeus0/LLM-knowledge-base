import subprocess
from unittest.mock import Mock

from typer.testing import CliRunner

from kb.cli import app

runner = CliRunner()


def _git(root, *args):
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        text=True,
    )


def _init_repo(root):
    wiki = root / "wiki"
    wiki.mkdir()
    _git(root, "init")
    _git(root, "config", "user.email", "test@example.com")
    _git(root, "config", "user.name", "Test User")
    article = wiki / "article.md"
    article.write_text("# Artigo\n\nLinha original\n")
    _git(root, "add", "wiki/article.md")
    _git(root, "commit", "-m", "initial")
    return wiki, article


def _patch_config(monkeypatch, root, wiki):
    monkeypatch.setattr("kb.config.DATA_DIR", root)
    monkeypatch.setattr("kb.config.WIKI_DIR", wiki)


def test_diff_should_show_wiki_changes_since_last_commit(tmp_path, monkeypatch):
    wiki, article = _init_repo(tmp_path)
    _patch_config(monkeypatch, tmp_path, wiki)
    article.write_text("# Artigo\n\nLinha alterada\n")

    from kb.diff import wiki_diff

    output = wiki_diff()

    assert "diff --git a/wiki/article.md b/wiki/article.md" in output
    assert "-Linha original" in output
    assert "+Linha alterada" in output


def test_diff_default_should_include_staged_changes(tmp_path, monkeypatch):
    wiki, article = _init_repo(tmp_path)
    _patch_config(monkeypatch, tmp_path, wiki)
    article.write_text("# Artigo\n\nLinha staged\n")
    _git(tmp_path, "add", "wiki/article.md")

    from kb.diff import wiki_diff

    output = wiki_diff()

    assert "+Linha staged" in output


def test_diff_stat_should_show_summary(tmp_path, monkeypatch):
    wiki, article = _init_repo(tmp_path)
    _patch_config(monkeypatch, tmp_path, wiki)
    article.write_text("# Artigo\n\nLinha alterada\n")

    from kb.diff import wiki_diff

    output = wiki_diff(stat=True)

    assert "wiki/article.md" in output
    assert "1 file changed" in output


def test_diff_since_should_compare_against_ref(tmp_path, monkeypatch):
    wiki, article = _init_repo(tmp_path)
    _patch_config(monkeypatch, tmp_path, wiki)
    article.write_text("# Artigo\n\nLinha alterada\n")

    from kb.diff import wiki_diff

    output = wiki_diff(since="HEAD")

    assert "-Linha original" in output
    assert "+Linha alterada" in output


def test_render_diff_should_apply_rich_markup_by_line():
    from kb.diff import render_diff

    console = Mock()

    render_diff(
        "diff --git a/wiki/article.md b/wiki/article.md\n"
        "@@ -1 +1 @@\n"
        "-Linha original\n"
        "+Linha alterada\n",
        console,
    )

    calls = [call.args[0] for call in console.print.call_args_list]
    assert calls == [
        "[dim cyan]diff --git a/wiki/article.md b/wiki/article.md[/]",
        "[dim cyan]@@ -1 +1 @@[/]",
        "[red]-Linha original[/]",
        "[green]+Linha alterada[/]",
    ]


def test_diff_without_git_repo_should_fail_with_clear_message(tmp_path, monkeypatch):
    wiki = tmp_path / "wiki"
    wiki.mkdir()
    _patch_config(monkeypatch, tmp_path, wiki)

    result = runner.invoke(app, ["diff"])

    assert result.exit_code == 1
    assert "não é um repositório git" in result.output


def test_diff_without_changes_should_print_friendly_message(tmp_path, monkeypatch):
    wiki, _article = _init_repo(tmp_path)
    _patch_config(monkeypatch, tmp_path, wiki)

    result = runner.invoke(app, ["diff"])

    assert result.exit_code == 0
    assert "Sem alterações" in result.output
