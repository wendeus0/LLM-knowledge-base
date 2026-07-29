"""RED — feature 014 (RF-01, RF-02, RF-06 via CLI).

Seams: `kb index status` reportando servidor; `kb index build` com servidor fora.
Sem rede: `kb.embed_server._http_get_json` e `kb.embeddings.embed_texts` mockados.
"""

from typer.testing import CliRunner

from kb.cli import app

runner = CliRunner()


def _seed_vault(tmp_path, monkeypatch):
    wiki = tmp_path / "wiki"
    state = tmp_path / "kb_state"
    wiki.mkdir()
    state.mkdir()
    (wiki / "artigo.md").write_text(
        "---\ntitle: Artigo\ntopic: general\n---\n\nConteúdo.\n", encoding="utf-8"
    )
    monkeypatch.setattr("kb.config.WIKI_DIR", wiki)
    monkeypatch.setattr("kb.config.STATE_DIR", state)
    return wiki, state


def _server_up(models):
    return lambda url, timeout: {"data": [{"id": name} for name in models]}


def _server_down(url, timeout):
    raise OSError("connection refused")


class TestIndexStatusServerBlock:
    def test_should_report_endpoint_and_reachability_when_server_up(
        self, tmp_path, monkeypatch
    ):
        _seed_vault(tmp_path, monkeypatch)
        monkeypatch.setenv("KB_EMBED_MODEL", "modelo-x")
        monkeypatch.setattr(
            "kb.embed_server._http_get_json", _server_up(["modelo-x"])
        )

        result = runner.invoke(app, ["index", "status"])

        assert result.exit_code == 0
        assert "1234" in result.output or "servidor" in result.output.lower()
        assert "modelo-x" in result.output

    def test_should_report_unreachable_when_server_down(self, tmp_path, monkeypatch):
        _seed_vault(tmp_path, monkeypatch)
        monkeypatch.setattr("kb.embed_server._http_get_json", _server_down)

        result = runner.invoke(app, ["index", "status"])

        assert result.exit_code == 0
        assert "inacess" in result.output.lower()

    def test_should_distinguish_missing_model_from_unreachable_server(
        self, tmp_path, monkeypatch
    ):
        _seed_vault(tmp_path, monkeypatch)
        monkeypatch.setenv("KB_EMBED_MODEL", "ausente")
        monkeypatch.setattr(
            "kb.embed_server._http_get_json", _server_up(["outro-modelo"])
        )

        result = runner.invoke(app, ["index", "status"])

        assert result.exit_code == 0
        assert "inacess" not in result.output.lower()
        assert "AUSENTE" in result.output
        assert "outro-modelo" in result.output


class TestIndexBuildErrorMessage:
    def test_should_name_endpoint_and_command_when_server_unreachable(
        self, tmp_path, monkeypatch
    ):
        _seed_vault(tmp_path, monkeypatch)
        monkeypatch.setattr("kb.embed_server._http_get_json", _server_down)

        def _boom(texts, model=None, base_url=None):
            raise OSError("connection refused")

        monkeypatch.setattr("kb.embeddings.embed_texts", _boom)

        result = runner.invoke(app, ["index", "build"])

        assert result.exit_code == 1
        assert "1234" in result.output
        assert "ollama" not in result.output.lower()
