"""RED — feature 015: o índice acompanha as escritas, sem quebrar quem escreveu.

O refresh é efeito colateral de compile/heal/qa: pode ser pulado, nunca pode
derrubar o comando que o disparou.
"""

import pytest

from kb import embeddings


@pytest.fixture
def _no_build(monkeypatch):
    """Registra chamadas a build_index sem executá-lo."""
    calls = []

    def _fake_build(wiki_dir, state_dir, force=False, max_chars=8000):
        calls.append((wiki_dir, state_dir))
        return {"indexed": 2, "removed": 1, "unchanged": 5, "truncated": 0}

    monkeypatch.setattr(embeddings, "build_index", _fake_build)
    monkeypatch.setattr(
        "kb.embed_server._http_get_json", lambda url, timeout: {"data": [{"id": "m"}]}
    )
    monkeypatch.delenv("KB_INDEX_AUTO_REFRESH", raising=False)
    return calls


class TestRefreshEmbeddingsIndex:
    def test_should_build_and_return_report_when_enabled_and_server_up(self, _no_build):
        report = embeddings.refresh_embeddings_index(enabled=True)

        assert report is not None
        assert report["indexed"] == 2
        assert report["removed"] == 1
        assert len(_no_build) == 1

    def test_should_skip_when_disabled_by_argument(self, _no_build):
        report = embeddings.refresh_embeddings_index(enabled=False)

        assert report is None
        assert _no_build == []

    def test_should_skip_when_disabled_by_env(self, _no_build, monkeypatch):
        monkeypatch.setenv("KB_INDEX_AUTO_REFRESH", "0")

        report = embeddings.refresh_embeddings_index(enabled=True)

        assert report is None
        assert _no_build == []

    def test_should_skip_with_warning_when_server_unreachable(
        self, _no_build, monkeypatch, capsys
    ):
        def _down(url, timeout):
            raise OSError("connection refused")

        monkeypatch.setattr("kb.embed_server._http_get_json", _down)

        report = embeddings.refresh_embeddings_index(enabled=True)

        assert report is None
        assert _no_build == []
        assert "índice" in capsys.readouterr().err.lower()

    def test_should_swallow_build_failure_without_breaking_caller(
        self, monkeypatch, capsys
    ):
        def _boom(wiki_dir, state_dir, force=False, max_chars=8000):
            raise RuntimeError("falha ao gerar embeddings")

        monkeypatch.setattr(embeddings, "build_index", _boom)
        monkeypatch.setattr(
            "kb.embed_server._http_get_json", lambda url, timeout: {"data": [{"id": "m"}]}
        )
        monkeypatch.delenv("KB_INDEX_AUTO_REFRESH", raising=False)

        report = embeddings.refresh_embeddings_index(enabled=True)

        assert report is None
        assert "falha ao gerar embeddings" in capsys.readouterr().err
