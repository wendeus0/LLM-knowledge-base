import pytest

from kb.templates_loader import resolve_template


def test_resolve_template_uses_engine_template_without_override(
    tmp_raw_wiki, monkeypatch
):
    _raw, wiki = tmp_raw_wiki
    monkeypatch.setattr("kb.config.DATA_DIR", wiki.parent)

    assert "## Conceitos Relacionados" in resolve_template("article")


def test_resolve_template_uses_vault_override(tmp_raw_wiki, monkeypatch):
    _raw, wiki = tmp_raw_wiki
    monkeypatch.setattr("kb.config.DATA_DIR", wiki.parent)
    override = wiki.parent / "templates" / "article.md"
    override.parent.mkdir()
    override.write_text("# Template customizado\n", encoding="utf-8")

    assert resolve_template("article") == "# Template customizado\n"


def test_resolve_template_derives_override_from_data_dir_not_wiki_dir(
    tmp_raw_wiki, monkeypatch, tmp_path
):
    _raw, wiki = tmp_raw_wiki
    vault = tmp_path / "vault"
    (vault / "templates").mkdir(parents=True)
    (vault / "templates" / "article.md").write_text(
        "# Override do vault\n", encoding="utf-8"
    )
    monkeypatch.setattr("kb.config.DATA_DIR", vault)

    assert resolve_template("article") == "# Override do vault\n"


def test_resolve_template_falls_back_when_override_is_directory(
    tmp_raw_wiki, monkeypatch
):
    _raw, wiki = tmp_raw_wiki
    monkeypatch.setattr("kb.config.DATA_DIR", wiki.parent)
    (wiki.parent / "templates" / "article.md").mkdir(parents=True)

    assert "## Conceitos Relacionados" in resolve_template("article")


def test_resolve_template_rejects_path_traversal_name(tmp_raw_wiki, monkeypatch):
    _raw, wiki = tmp_raw_wiki
    monkeypatch.setattr("kb.config.DATA_DIR", wiki.parent)

    with pytest.raises(ValueError, match="inválido"):
        resolve_template("../article")


def test_resolve_template_missing_name_mentions_name(tmp_raw_wiki, monkeypatch):
    _raw, wiki = tmp_raw_wiki
    monkeypatch.setattr("kb.config.DATA_DIR", wiki.parent)

    with pytest.raises(FileNotFoundError, match="inexistente"):
        resolve_template("inexistente")
