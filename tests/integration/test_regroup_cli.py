"""029 C3 — contrato do `kb regroup scan|apply` (RF-03, RF-04, RF-06)."""

import json
import subprocess

from typer.testing import CliRunner

from kb.cli import app

runner = CliRunner()


def _seed(tmp_path, monkeypatch):
    data = tmp_path
    wiki = data / "wiki"
    state = data / "kb_state"
    (wiki / "algorithms").mkdir(parents=True)
    state.mkdir()
    (wiki / "algorithms" / "mergesort.md").write_text(
        "---\ntitle: Merge\ntopic: algorithms\n---\ncorpo", encoding="utf-8"
    )
    (wiki / "algorithms" / "solto.md").write_text(
        "---\ntitle: Solto\ntopic: algorithms\n---\ncorpo", encoding="utf-8"
    )
    summary = wiki / "_summaries" / "algorithms" / "mergesort.md"
    summary.parent.mkdir(parents=True)
    summary.write_text("resumo", encoding="utf-8")
    (state / "manifest.json").write_text(
        json.dumps(
            [{"source": "library/x/l/01.md", "article": "algorithms/mergesort.md",
              "status": "compiled", "book": "Livro A", "provenance": "backfill-basename"}]
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr("kb.config.DATA_DIR", data)
    monkeypatch.setattr("kb.config.WIKI_DIR", wiki)
    monkeypatch.setattr("kb.config.MANIFEST_PATH", state / "manifest.json")
    monkeypatch.setattr("kb.state.MANIFEST_PATH", state / "manifest.json")
    monkeypatch.setattr("kb.state.STATE_DIR", state)
    monkeypatch.setattr("kb.compile.WIKI_DIR", wiki)
    return data, wiki, state


def test_should_print_plan_without_moving_on_scan(tmp_path, monkeypatch):
    data, wiki, _ = _seed(tmp_path, monkeypatch)

    result = runner.invoke(app, ["regroup", "scan"])

    assert result.exit_code == 0
    assert "livro-a" in result.output
    assert "algorithms/mergesort.md → _chapters/livro-a/mergesort.md" in result.output
    assert "unresolved\talgorithms/solto.md" in result.output
    assert (wiki / "algorithms" / "mergesort.md").exists()


def test_should_move_book_update_manifest_and_commit(tmp_path, monkeypatch):
    data, wiki, state = _seed(tmp_path, monkeypatch)
    for cmd in (
        ["git", "init", "-q"],
        ["git", "config", "user.email", "kb@test"],
        ["git", "config", "user.name", "kb"],
        ["git", "add", "-A"],
        ["git", "commit", "-qm", "seed"],
    ):
        subprocess.run(cmd, cwd=tmp_path, check=True)

    result = runner.invoke(app, ["regroup", "apply", "--book", "livro-a", "--commit"])

    assert result.exit_code == 0
    assert not (wiki / "algorithms" / "mergesort.md").exists()
    assert (wiki / "_chapters" / "livro-a" / "mergesort.md").is_file()
    assert (wiki / "_summaries" / "_chapters" / "livro-a" / "mergesort.md").is_file()
    assert (wiki / "algorithms" / "solto.md").exists()  # unresolved fica
    [entry] = json.loads((state / "manifest.json").read_text(encoding="utf-8"))
    assert entry["article"] == "_chapters/livro-a/mergesort.md"
    index = (wiki / "_index.md").read_text(encoding="utf-8")
    assert "_chapters" not in index
    assert "solto" in index
    status = subprocess.run(
        ["git", "status", "--porcelain"], cwd=tmp_path, check=True, capture_output=True, text=True
    ).stdout
    sujos = [linha for linha in status.splitlines() if "_index.md" not in linha]
    assert sujos == [], f"move deve estar commitado; sobrou: {sujos}"


def test_should_reject_unknown_book(tmp_path, monkeypatch):
    _seed(tmp_path, monkeypatch)

    result = runner.invoke(app, ["regroup", "apply", "--book", "nao-existe"])

    assert result.exit_code == 2
