"""RED — feature 016 (RF-01, RF-03, RF-04, RF-06, RF-08) via CLI."""

import json

from typer.testing import CliRunner

from kb.cli import app

runner = CliRunner()


def _seed_vault(tmp_path, monkeypatch):
    wiki = tmp_path / "wiki"
    state = tmp_path / "kb_state"
    wiki.mkdir()
    state.mkdir()
    (wiki / "circuit-breaker.md").write_text(
        "---\ntitle: Circuit Breaker\n---\n\nInterrompe chamadas a servico em falha.\n",
        encoding="utf-8",
    )
    (wiki / "paella.md").write_text(
        "---\ntitle: Paella\n---\n\nReceita de culinaria espanhola.\n", encoding="utf-8"
    )
    monkeypatch.setattr("kb.config.WIKI_DIR", wiki)
    monkeypatch.setattr("kb.config.STATE_DIR", state)
    monkeypatch.setattr("kb.search.WIKI_DIR", wiki)
    return wiki, state


class TestBenchCommand:
    def test_should_teach_seed_when_golden_absent(self, tmp_path, monkeypatch):
        _seed_vault(tmp_path, monkeypatch)

        result = runner.invoke(app, ["bench"])

        assert result.exit_code == 1
        assert "--seed" in result.output

    def test_should_generate_golden_from_titles(self, tmp_path, monkeypatch):
        _, state = _seed_vault(tmp_path, monkeypatch)

        result = runner.invoke(app, ["bench", "--seed"])

        assert result.exit_code == 0
        payload = json.loads((state / "bench" / "golden.json").read_text(encoding="utf-8"))
        questions = {case["question"] for case in payload["cases"]}
        assert "Circuit Breaker" in questions
        assert {"circuit-breaker"} in [set(c["expected"]) for c in payload["cases"]]

    def test_should_report_recall_after_seeding(self, tmp_path, monkeypatch):
        _seed_vault(tmp_path, monkeypatch)
        runner.invoke(app, ["bench", "--seed"])

        result = runner.invoke(app, ["bench", "--mode", "lexical"])

        assert result.exit_code == 0
        assert "recall" in result.output.lower()

    def test_should_emit_parseable_json(self, tmp_path, monkeypatch):
        _seed_vault(tmp_path, monkeypatch)
        runner.invoke(app, ["bench", "--seed"])

        result = runner.invoke(app, ["bench", "--mode", "lexical", "--json"])

        payload = json.loads(result.output)
        assert payload["mode"] == "lexical"
        assert payload["summary"]["total"] == 2
        assert 0.0 <= payload["summary"]["recall_at_k"] <= 1.0
