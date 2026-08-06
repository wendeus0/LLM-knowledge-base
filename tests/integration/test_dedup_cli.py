"""028 B4/B5 — contrato do `kb dedup scan|apply` (RF-04, RF-05)."""

import json

from typer.testing import CliRunner

from kb.cli import app

runner = CliRunner()


def _seed(tmp_path, monkeypatch):
    data = tmp_path
    wiki = data / "wiki"
    raw = data / "raw"
    state = data / "kb_state"
    archive_dir = data / "archive"
    for d in (wiki, raw, state, archive_dir):
        d.mkdir()
    livro = data / "library" / "algorithms" / "livro-a"
    livro.mkdir(parents=True)
    (livro / "07-matrizes.md").write_text("# Matrizes\ncapítulo", encoding="utf-8")
    (wiki / "algorithms").mkdir()
    (wiki / "algorithms" / "decomposicoes.md").write_text(
        "---\ntitle: Decomposições\ntopic: algorithms\ntags: []\nsource: 07-matrizes.md\n---\n\nTexto principal sobre matrizes.\n",
        encoding="utf-8",
    )
    (wiki / "decomposicoes.md").write_text(
        "---\ntitle: Decomposições\ntopic: general\ntags: []\nsource: 07-matrizes.md\n---\n\nTexto duplicado sobre matrizes.\n",
        encoding="utf-8",
    )
    summary = wiki / "_summaries" / "decomposicoes.md"
    summary.parent.mkdir()
    summary.write_text("resumo do duplicado", encoding="utf-8")
    (state / "manifest.json").write_text(
        json.dumps(
            [
                {
                    "source": "library/algorithms/livro-a/07-matrizes.md",
                    "kind": "raw",
                    "status": "compiled",
                    "article": "decomposicoes.md",
                    "provenance": "backfill-basename",
                }
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr("kb.config.DATA_DIR", data)
    monkeypatch.setattr("kb.config.RAW_DIR", raw)
    monkeypatch.setattr("kb.config.WIKI_DIR", wiki)
    monkeypatch.setattr("kb.config.ARCHIVE_DIR", archive_dir)
    monkeypatch.setattr("kb.config.STATE_DIR", state)
    monkeypatch.setattr("kb.config.MANIFEST_PATH", state / "manifest.json")
    monkeypatch.setattr("kb.state.MANIFEST_PATH", state / "manifest.json")
    monkeypatch.setattr("kb.state.STATE_DIR", state)
    monkeypatch.setattr("kb.compile.WIKI_DIR", wiki)
    return data, wiki, state, archive_dir


def test_should_report_pairs_without_moving_anything_on_scan(tmp_path, monkeypatch):
    data, wiki, _, _ = _seed(tmp_path, monkeypatch)

    result = runner.invoke(app, ["dedup", "scan"])

    assert result.exit_code == 0
    assert "same-source" in result.output
    assert "fica: algorithms/decomposicoes.md" in result.output
    assert "sai: decomposicoes.md" in result.output
    assert (wiki / "decomposicoes.md").exists()


def test_should_archive_loser_with_summary_and_mark_manifest(tmp_path, monkeypatch):
    data, wiki, state, archive_dir = _seed(tmp_path, monkeypatch)

    result = runner.invoke(app, ["dedup", "apply"])

    assert result.exit_code == 0
    assert not (wiki / "decomposicoes.md").exists()
    assert (wiki / "algorithms" / "decomposicoes.md").exists()
    assert (archive_dir / "decomposicoes.md").is_file()
    assert (archive_dir / "_summaries" / "decomposicoes.md").is_file()
    [entry] = json.loads((state / "manifest.json").read_text(encoding="utf-8"))
    assert entry["status"] == "archived"
    index = (wiki / "_index.md").read_text(encoding="utf-8")
    assert "(`decomposicoes.md`)" not in index
    assert "algorithms/decomposicoes.md" in index
