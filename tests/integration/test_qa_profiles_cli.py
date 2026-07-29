"""RED — feature 013-context-budget (RF-04, RF-05 + validação de flag).

Seam: CLI `kb qa` com perfis (fast default, --deep, --top-k). O chat é a única
fronteira mockada; conta-se quantos documentos entram no contexto do prompt.
"""

from typer.testing import CliRunner

from kb.cli import app

runner = CliRunner()


def _seed(tmp_path, monkeypatch, captured):
    wiki = tmp_path / "wiki"
    state = tmp_path / "kb_state"
    raw = tmp_path / "raw"
    wiki.mkdir()
    state.mkdir()
    raw.mkdir()
    for i in range(6):
        (wiki / f"resiliencia-{i}.md").write_text(
            f"---\ntitle: Resiliencia {i}\n---\n\nArtigo {i} sobre resiliencia e falhas.\n",
            encoding="utf-8",
        )
    monkeypatch.setattr("kb.config.WIKI_DIR", wiki)
    monkeypatch.setattr("kb.config.RAW_DIR", raw)
    monkeypatch.setattr("kb.config.STATE_DIR", state)
    monkeypatch.setattr("kb.router.WIKI_DIR", wiki)
    monkeypatch.setattr("kb.router.RAW_DIR", raw)
    monkeypatch.setattr("kb.search.WIKI_DIR", wiki)

    def _fake_chat(messages, model=None, **kwargs):
        captured.append(messages[-1]["content"])
        return "resposta ok"

    monkeypatch.setattr("kb.qa.chat", _fake_chat)
    monkeypatch.setattr("kb.qa.find_relevant_claims", lambda *a, **k: [])
    monkeypatch.setattr("kb.qa.add_learning", lambda *a, **k: None)


def _doc_count(prompt: str) -> int:
    return prompt.count("# resiliencia-")


def test_should_use_fast_profile_with_three_docs_by_default(tmp_path, monkeypatch):
    # RED: falha até 013-context-budget ser implementada (RF-04)
    captured: list[str] = []
    _seed(tmp_path, monkeypatch, captured)
    result = runner.invoke(app, ["qa", "o que é resiliencia?"])
    assert result.exit_code == 0
    assert len(captured) == 1
    assert _doc_count(captured[0]) == 3


def test_should_use_deep_profile_with_five_docs_when_flag(tmp_path, monkeypatch):
    # RED: falha até 013-context-budget ser implementada (RF-04)
    captured: list[str] = []
    _seed(tmp_path, monkeypatch, captured)
    result = runner.invoke(app, ["qa", "o que é resiliencia?", "--deep"])
    assert result.exit_code == 0
    assert _doc_count(captured[0]) == 5


def test_should_override_top_k_with_flag(tmp_path, monkeypatch):
    # RED: falha até 013-context-budget ser implementada (RF-05)
    captured: list[str] = []
    _seed(tmp_path, monkeypatch, captured)
    result = runner.invoke(app, ["qa", "o que é resiliencia?", "--top-k", "2"])
    assert result.exit_code == 0
    assert _doc_count(captured[0]) == 2


def test_should_reject_non_positive_top_k(tmp_path, monkeypatch):
    # RED: falha até 013-context-budget ser implementada (caso de erro: --top-k 0)
    captured: list[str] = []
    _seed(tmp_path, monkeypatch, captured)
    valid = runner.invoke(app, ["qa", "o que é resiliencia?", "--top-k", "1"])
    assert valid.exit_code == 0  # flag existe e aceita valor válido
    invalid = runner.invoke(app, ["qa", "o que é resiliencia?", "--top-k", "0"])
    assert invalid.exit_code != 0
