"""RED — feature 015 (RF-01, RF-02, RF-05): índice acompanha compile e heal.

Sem rede: probe e embedder mockados; `build_index` real, exercitando a
incrementalidade por hash que a 012 já entrega.
"""

from pathlib import Path
from unittest.mock import patch

from kb.compile import compile_many
from kb.heal import heal


def _seed(tmp_path, monkeypatch):
    raw = tmp_path / "raw"
    wiki = tmp_path / "wiki"
    state = tmp_path / "kb_state"
    for directory in (raw, wiki, state):
        directory.mkdir()
    monkeypatch.setattr("kb.config.RAW_DIR", raw)
    monkeypatch.setattr("kb.config.WIKI_DIR", wiki)
    monkeypatch.setattr("kb.config.STATE_DIR", state)
    monkeypatch.setattr("kb.compile.RAW_DIR", raw)
    monkeypatch.setattr("kb.compile.WIKI_DIR", wiki)
    monkeypatch.setattr("kb.heal.WIKI_DIR", wiki)
    monkeypatch.setattr("kb.config.MANIFEST_PATH", state / "manifest.json")
    monkeypatch.setattr("kb.state.MANIFEST_PATH", state / "manifest.json")
    monkeypatch.setattr("kb.config.KNOWLEDGE_PATH", state / "knowledge.json")
    monkeypatch.setattr("kb.state.KNOWLEDGE_PATH", state / "knowledge.json")
    monkeypatch.setattr("kb.state.STATE_DIR", state)
    monkeypatch.setattr("kb.config.CLAIMS_PATH", state / "claims.jsonl")
    monkeypatch.setattr("kb.claims.CLAIMS_PATH", state / "claims.jsonl")
    monkeypatch.setattr("kb.config.AUDIT_PATH", state / "audit.jsonl")
    monkeypatch.setattr(
        "kb.embed_server._http_get_json", lambda url, timeout: {"data": [{"id": "m"}]}
    )
    monkeypatch.setattr(
        "kb.embeddings.embed_texts",
        lambda texts, model=None, base_url=None: [[1.0, 0.0] for _ in texts],
    )
    monkeypatch.delenv("KB_INDEX_AUTO_REFRESH", raising=False)
    return raw, wiki, state


def _indexed_paths(state: Path) -> set[str]:
    from kb.embeddings import load_index

    index = load_index(state)
    return set(index["articles"]) if index else set()


class TestCompileRefreshesIndex:
    def test_should_index_compiled_article_without_manual_build(
        self, tmp_path, monkeypatch
    ):
        raw, wiki, state = _seed(tmp_path, monkeypatch)
        (raw / "doc.md").write_text("# Doc\nConteúdo.", encoding="utf-8")

        with patch("kb.compile.chat") as mock_chat, patch("kb.compile.commit"):
            mock_chat.return_value = "---\ntitle: Artigo\ntopic: ai\n---\n\n# Artigo\n\nCorpo.\n"
            compile_many([raw / "doc.md"])

        assert any("artigo" in relpath for relpath in _indexed_paths(state))

    def test_should_not_touch_index_when_refresh_disabled(self, tmp_path, monkeypatch):
        raw, wiki, state = _seed(tmp_path, monkeypatch)
        (raw / "doc.md").write_text("# Doc\nConteúdo.", encoding="utf-8")

        with patch("kb.compile.chat") as mock_chat, patch("kb.compile.commit"):
            mock_chat.return_value = "---\ntitle: Artigo\ntopic: ai\n---\n\n# Artigo\n\nCorpo.\n"
            compile_many([raw / "doc.md"], index_refresh_enabled=False)

        assert _indexed_paths(state) == set()


class TestHealRefreshesIndex:
    def test_should_drop_deleted_stub_from_index(self, tmp_path, monkeypatch):
        _, wiki, state = _seed(tmp_path, monkeypatch)
        (wiki / "vivo.md").write_text(
            "---\ntitle: Vivo\n---\n\nConteúdo real e suficientemente longo.\n",
            encoding="utf-8",
        )
        stub = wiki / "stub.md"
        stub.write_text("---\ntitle: Stub\n---\n", encoding="utf-8")

        from kb.embeddings import build_index

        build_index(wiki, state)
        assert "stub.md" in _indexed_paths(state)

        with patch("kb.heal.chat") as mock_chat, patch("kb.heal.commit"):
            mock_chat.return_value = "NO_CHANGES"
            heal(n=10)

        assert "stub.md" not in _indexed_paths(state)
        assert "vivo.md" in _indexed_paths(state)
