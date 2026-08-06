"""028 B6/B7 — contrato do `kb topics normalize|assign` (RF-06, RF-07, RF-08)."""

from typer.testing import CliRunner

from kb.cli import app

runner = CliRunner()


def _seed(tmp_path, monkeypatch):
    wiki = tmp_path / "wiki"
    wiki.mkdir()
    (wiki / "artigo-ddd.md").write_text(
        "---\ntitle: DDD\ntopic: ddd\ntags: []\nsource: a.md\n---\n\nCorpo.\n", encoding="utf-8"
    )
    (wiki / "sem-topic.md").write_text(
        "---\ntitle: Circuit Breaker\ntopic: general\ntags: []\nsource: b.md\n---\n\nEstabilidade em produção.\n",
        encoding="utf-8",
    )
    monkeypatch.setattr("kb.config.WIKI_DIR", wiki)
    monkeypatch.setattr("kb.config.TOPICS", ["algorithms", "operations", "software-architecture"])
    return wiki


def test_should_normalize_variants_only_with_apply(tmp_path, monkeypatch):
    wiki = _seed(tmp_path, monkeypatch)

    report = runner.invoke(app, ["topics", "normalize"])
    assert report.exit_code == 0
    assert "ddd → software-architecture" in report.output
    assert "topic: ddd" in (wiki / "artigo-ddd.md").read_text(encoding="utf-8")

    applied = runner.invoke(app, ["topics", "normalize", "--apply"])
    assert applied.exit_code == 0
    assert "topic: software-architecture" in (wiki / "artigo-ddd.md").read_text(encoding="utf-8")


def test_should_assign_via_llm_restricted_to_taxonomy(tmp_path, monkeypatch):
    wiki = _seed(tmp_path, monkeypatch)
    monkeypatch.setattr("kb.client.chat", lambda messages, **kw: "operations")

    report = runner.invoke(app, ["topics", "assign"])
    assert report.exit_code == 0
    assert "sem-topic.md" in report.output
    assert "operations" in report.output
    assert "topic: general" in (wiki / "sem-topic.md").read_text(encoding="utf-8")

    applied = runner.invoke(app, ["topics", "assign", "--apply"])
    assert applied.exit_code == 0
    assert "topic: operations" in (wiki / "sem-topic.md").read_text(encoding="utf-8")


def test_should_reject_llm_answer_outside_taxonomy(tmp_path, monkeypatch):
    wiki = _seed(tmp_path, monkeypatch)
    monkeypatch.setattr("kb.client.chat", lambda messages, **kw: "categoria-inventada")

    applied = runner.invoke(app, ["topics", "assign", "--apply"])

    assert applied.exit_code == 0
    assert "REJEITADO" in applied.output
    assert "topic: general" in (wiki / "sem-topic.md").read_text(encoding="utf-8")
