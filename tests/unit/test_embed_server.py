"""Estado do servidor de embeddings: probe, disponibilidade de modelo e autostart.

Sem rede: `_http_get_json` e o runner de processo são as únicas fronteiras,
ambas monkeypatchadas — mesmo padrão que `embed_texts` já usa nos testes de 012.
"""

import pytest

from kb import embed_server


class TestProbe:
    def test_should_report_reachable_with_models_when_endpoint_answers(self, monkeypatch):
        monkeypatch.setattr(
            embed_server,
            "_http_get_json",
            lambda url, timeout: {"data": [{"id": "modelo-a"}, {"id": "modelo-b"}]},
        )

        state = embed_server.probe("http://localhost:1234/v1", timeout=1)

        assert state.reachable is True
        assert state.models == ["modelo-a", "modelo-b"]
        assert state.error is None

    def test_should_report_unreachable_with_cause_when_endpoint_refuses(self, monkeypatch):
        def _boom(url, timeout):
            raise OSError("connection refused")

        monkeypatch.setattr(embed_server, "_http_get_json", _boom)

        state = embed_server.probe("http://localhost:1234/v1", timeout=1)

        assert state.reachable is False
        assert state.models == []
        assert "connection refused" in state.error

    def test_should_keep_endpoint_in_state_for_error_messages(self, monkeypatch):
        monkeypatch.setattr(embed_server, "_http_get_json", lambda url, timeout: {"data": []})

        state = embed_server.probe("http://example:9999/v1", timeout=1)

        assert state.endpoint == "http://example:9999/v1"


class TestModelAvailable:
    def test_should_confirm_model_when_listed_by_server(self):
        state = embed_server.ServerState(
            reachable=True, models=["nomic-v2", "outro"], endpoint="x"
        )

        assert embed_server.model_available(state, "nomic-v2") is True

    def test_should_deny_model_when_not_listed(self):
        state = embed_server.ServerState(reachable=True, models=["outro"], endpoint="x")

        assert embed_server.model_available(state, "nomic-v2") is False

    def test_should_deny_model_when_server_unreachable(self):
        state = embed_server.ServerState(reachable=False, models=[], endpoint="x")

        assert embed_server.model_available(state, "nomic-v2") is False


class TestEnsureServer:
    def test_should_not_run_command_when_autostart_disabled(self, monkeypatch):
        calls = []
        monkeypatch.setattr(
            embed_server, "_http_get_json", lambda url, timeout: (_ for _ in ()).throw(OSError("down"))
        )
        monkeypatch.setattr(embed_server, "_run_command", lambda cmd, timeout: calls.append(cmd))

        state = embed_server.ensure_server(
            "http://localhost:1234/v1", autostart_enabled=False
        )

        assert state.reachable is False
        assert calls == []

    def test_should_run_command_once_when_autostart_enabled_and_server_down(self, monkeypatch):
        calls = []
        monkeypatch.setattr(
            embed_server, "_http_get_json", lambda url, timeout: (_ for _ in ()).throw(OSError("down"))
        )
        monkeypatch.setattr(embed_server, "_run_command", lambda cmd, timeout: calls.append(cmd))

        embed_server.ensure_server(
            "http://localhost:1234/v1",
            autostart_enabled=True,
            autostart_cmd="fake start",
            autostart_timeout=0,
        )

        assert len(calls) == 1

    def test_should_skip_autostart_when_server_already_reachable(self, monkeypatch):
        calls = []
        monkeypatch.setattr(
            embed_server, "_http_get_json", lambda url, timeout: {"data": [{"id": "m"}]}
        )
        monkeypatch.setattr(embed_server, "_run_command", lambda cmd, timeout: calls.append(cmd))

        state = embed_server.ensure_server(
            "http://localhost:1234/v1", autostart_enabled=True, autostart_cmd="fake start"
        )

        assert state.reachable is True
        assert calls == []

    def test_should_degrade_without_raising_when_autostart_binary_missing(self, monkeypatch):
        def _missing(cmd, timeout):
            raise FileNotFoundError("lms not found")

        monkeypatch.setattr(
            embed_server, "_http_get_json", lambda url, timeout: (_ for _ in ()).throw(OSError("down"))
        )
        monkeypatch.setattr(embed_server, "_run_command", _missing)

        state = embed_server.ensure_server(
            "http://localhost:1234/v1",
            autostart_enabled=True,
            autostart_cmd="lms server start",
            autostart_timeout=0,
        )

        assert state.reachable is False
        assert "lms not found" in state.error


class TestConfig:
    @pytest.mark.parametrize(
        "value,expected",
        [("1", True), ("true", True), ("0", False), ("", False), (None, False)],
    )
    def test_should_read_autostart_flag_from_env(self, monkeypatch, value, expected):
        if value is None:
            monkeypatch.delenv("KB_EMBED_AUTOSTART", raising=False)
        else:
            monkeypatch.setenv("KB_EMBED_AUTOSTART", value)

        assert embed_server.autostart_enabled() is expected
