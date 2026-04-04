import pytest

from kb.client import validate_provider_model_compatibility, get_client


class TestGetClient:
    def test_should_raise_when_api_key_is_missing(self, monkeypatch):
        monkeypatch.setattr("kb.client.API_KEY", None)

        with pytest.raises(RuntimeError, match="KB_API_KEY"):
            get_client()

    def test_should_raise_when_api_key_is_empty_string(self, monkeypatch):
        monkeypatch.setattr("kb.client.API_KEY", "")

        with pytest.raises(RuntimeError, match="KB_API_KEY"):
            get_client()


class TestValidateProviderModelCompatibility:
    def test_should_allow_kimi_model_for_opencode_go(self):
        validate_provider_model_compatibility(
            base_url="https://opencode.ai/zen/go/v1",
            model="kimi-k2.5",
        )

    def test_should_reject_prefixed_model_name_for_opencode_go(self):
        with pytest.raises(ValueError) as exc:
            validate_provider_model_compatibility(
                base_url="https://opencode.ai/zen/go/v1",
                model="opencode-go/kimi-k2.5",
            )

        assert "OpenCode Go" in str(exc.value)
        assert "kimi-k2.5" in str(exc.value)

    def test_should_reject_unknown_model_name_for_opencode_go(self):
        with pytest.raises(ValueError) as exc:
            validate_provider_model_compatibility(
                base_url="https://opencode.ai/zen/go/v1",
                model="gpt-4o",
            )

        assert "modelo incompatível" in str(exc.value).lower() or "modelo não reconhecido" in str(exc.value).lower()

    def test_should_skip_opencode_validation_for_other_base_urls(self):
        validate_provider_model_compatibility(
            base_url="http://localhost:11434/v1",
            model="qwen2.5-coder:7b",
        )
