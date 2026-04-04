import kb.client as _client
import pytest


def test_should_raise_clear_runtime_error_when_api_key_is_not_configured(monkeypatch):
    monkeypatch.setattr(_client, "API_KEY", None)

    with pytest.raises(RuntimeError, match="KB_API_KEY"):
        _client.get_client()
