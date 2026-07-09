import pytest

from kb.templates_loader import resolve_template


def test_resolve_template_uses_engine_template_without_override(tmp_raw_wiki):
    assert "## Conceitos Relacionados" in resolve_template("article")


def test_resolve_template_uses_vault_override(tmp_raw_wiki):
    _raw, wiki = tmp_raw_wiki
    override = wiki.parent / "templates" / "article.md"
    override.parent.mkdir()
    override.write_text("# Template customizado\n", encoding="utf-8")

    assert resolve_template("article") == "# Template customizado\n"


def test_resolve_template_missing_name_mentions_name(tmp_raw_wiki):
    with pytest.raises(FileNotFoundError, match="inexistente"):
        resolve_template("inexistente")
