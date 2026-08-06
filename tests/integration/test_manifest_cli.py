"""028 B2 — contrato do `kb manifest backfill` (RF-02, RF-08)."""

import json

from typer.testing import CliRunner

from kb.cli import app

runner = CliRunner()


def _seed(tmp_path, monkeypatch):
    data = tmp_path
    wiki = data / "wiki"
    raw = data / "raw"
    state = data / "kb_state"
    for d in (wiki, raw, state):
        d.mkdir()
    livro = data / "library" / "ai" / "livro-a"
    livro.mkdir(parents=True)
    (livro / "07-atencao.md").write_text("# Atenção\ncapítulo", encoding="utf-8")
    (wiki / "atencao.md").write_text(
        "---\ntitle: Atenção\ntopic: ai\ntags: []\nsource: 07-atencao.md\n---\n\nCorpo.\n",
        encoding="utf-8",
    )
    monkeypatch.setattr("kb.config.DATA_DIR", data)
    monkeypatch.setattr("kb.config.RAW_DIR", raw)
    monkeypatch.setattr("kb.config.WIKI_DIR", wiki)
    monkeypatch.setattr("kb.config.MANIFEST_PATH", state / "manifest.json")
    monkeypatch.setattr("kb.state.MANIFEST_PATH", state / "manifest.json")
    monkeypatch.setattr("kb.state.STATE_DIR", state)
    # sem servidor de embeddings nos testes
    monkeypatch.setattr("kb.embed_server.probe", lambda *a, **k: type("S", (), {"reachable": False})())
    return data, wiki, state


def test_should_only_report_without_apply(tmp_path, monkeypatch):
    data, wiki, state = _seed(tmp_path, monkeypatch)

    result = runner.invoke(app, ["manifest", "backfill"])

    assert result.exit_code == 0
    assert "backfill-basename" in result.output
    assert "atencao.md" in result.output
    assert not (state / "manifest.json").exists()


def test_should_materialize_links_with_apply(tmp_path, monkeypatch):
    data, wiki, state = _seed(tmp_path, monkeypatch)

    result = runner.invoke(app, ["manifest", "backfill", "--apply"])

    assert result.exit_code == 0
    entries = json.loads((state / "manifest.json").read_text(encoding="utf-8"))
    [entry] = entries
    assert entry["source"] == "library/ai/livro-a/07-atencao.md"
    assert entry["article"] == "atencao.md"
    assert entry["book"] == "livro-a"
    assert entry["provenance"] == "backfill-basename"


def test_should_not_materialize_unresolved_links(tmp_path, monkeypatch):
    data, wiki, state = _seed(tmp_path, monkeypatch)
    (wiki / "orfao.md").write_text(
        "---\ntitle: Órfão\ntopic: general\ntags: []\nsource: 99-nada.md\n---\n\nCorpo.\n",
        encoding="utf-8",
    )

    result = runner.invoke(app, ["manifest", "backfill", "--apply"])

    assert result.exit_code == 0
    entries = json.loads((state / "manifest.json").read_text(encoding="utf-8"))
    assert len(entries) == 1
    assert "unresolved" in result.output
