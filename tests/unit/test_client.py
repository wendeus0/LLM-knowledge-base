import pytest
from unittest.mock import Mock, patch

from kb.client import (
    validate_provider_model_compatibility,
    get_client,
    is_provider_resource_limit_error,
)


class TestIsProviderResourceLimitError:
    def test_should_return_true_for_error_1102_in_message(self):
        exc = Exception("API error 1102: worker exceeded resource limits")
        assert is_provider_resource_limit_error(exc) is True

    def test_should_return_true_for_worker_exceeded_resources_in_message(self):
        exc = Exception("worker_exceeded_resources")
        assert is_provider_resource_limit_error(exc) is True

    def test_should_return_false_for_non_resource_error(self):
        exc = Exception("Some other error")
        assert is_provider_resource_limit_error(exc) is False

    def test_should_check_error_code_in_body_dict(self):
        exc = Exception("API Error")
        exc.body = {"error_code": "error 1102"}
        assert is_provider_resource_limit_error(exc) is True

    def test_should_check_error_name_in_body_dict(self):
        exc = Exception("API Error")
        exc.body = {"error_name": "worker_exceeded_resources"}
        assert is_provider_resource_limit_error(exc) is True

    def test_should_check_detail_in_body_dict(self):
        exc = Exception("API Error")
        exc.body = {"detail": "worker exceeded resource limits"}
        assert is_provider_resource_limit_error(exc) is True

    def test_should_check_title_in_body_dict(self):
        exc = Exception("API Error")
        exc.body = {"title": "error 1102"}
        assert is_provider_resource_limit_error(exc) is True

    def test_should_return_false_when_body_has_no_matching_fields(self):
        exc = Exception("API Error")
        exc.body = {"message": "Something else"}
        assert is_provider_resource_limit_error(exc) is False

    def test_should_return_false_when_body_is_none(self):
        exc = Exception("API Error")
        exc.body = None
        assert is_provider_resource_limit_error(exc) is False

    def test_should_return_false_when_no_body_attribute(self):
        exc = Exception("API Error")
        assert is_provider_resource_limit_error(exc) is False


class TestGetClient:
    def test_should_raise_when_api_key_is_missing(self, monkeypatch):
        monkeypatch.setattr("kb.client.API_KEY", None)

        with pytest.raises(RuntimeError, match="KB_API_KEY"):
            get_client()

    def test_should_raise_when_api_key_is_empty_string(self, monkeypatch):
        monkeypatch.setattr("kb.client.API_KEY", "")

        with pytest.raises(RuntimeError, match="KB_API_KEY"):
            get_client()

    def test_should_raise_when_openai_import_fails(self, monkeypatch):
        monkeypatch.setattr("kb.client.API_KEY", "test-key")

        # Simulate ImportError when trying to import openai
        with patch(
            "builtins.__import__", side_effect=ImportError("No module named 'openai'")
        ):
            with pytest.raises(RuntimeError, match="openai"):
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

        assert (
            "modelo incompatível" in str(exc.value).lower()
            or "modelo não reconhecido" in str(exc.value).lower()
        )

    def test_should_skip_opencode_validation_for_other_base_urls(self):
        validate_provider_model_compatibility(
            base_url="http://localhost:11434/v1",
            model="qwen2.5-coder:7b",
        )


class TestChat:
    def test_should_call_chat_completions_with_correct_params(self, monkeypatch):
        monkeypatch.setattr("kb.client.API_KEY", "test-key")
        monkeypatch.setattr("kb.client.BASE_URL", "https://api.openai.com/v1")
        monkeypatch.setattr("kb.client.MODEL", "gpt-4")

        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Test response"))]
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response

        # OpenAI is imported inside get_client, so we need to patch it there
        with patch("kb.client.get_client", return_value=mock_client):
            from kb.client import chat

            result = chat([{"role": "user", "content": "Hello"}])

        assert result == "Test response"
        mock_client.chat.completions.create.assert_called_once_with(
            model="gpt-4",
            messages=[{"role": "user", "content": "Hello"}],
        )

    def test_should_use_provided_model_override(self, monkeypatch):
        monkeypatch.setattr("kb.client.API_KEY", "test-key")
        monkeypatch.setattr("kb.client.BASE_URL", "https://api.openai.com/v1")
        monkeypatch.setattr("kb.client.MODEL", "gpt-4")

        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Test response"))]
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response

        with patch("kb.client.get_client", return_value=mock_client):
            from kb.client import chat

            chat([{"role": "user", "content": "Hello"}], model="gpt-3.5")

        mock_client.chat.completions.create.assert_called_once_with(
            model="gpt-3.5",
            messages=[{"role": "user", "content": "Hello"}],
        )

    def test_should_pass_additional_kwargs_to_api(self, monkeypatch):
        monkeypatch.setattr("kb.client.API_KEY", "test-key")
        monkeypatch.setattr("kb.client.BASE_URL", "https://api.openai.com/v1")
        monkeypatch.setattr("kb.client.MODEL", "gpt-4")

        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Test"))]
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response

        with patch("kb.client.get_client", return_value=mock_client):
            from kb.client import chat

            chat(
                [{"role": "user", "content": "Hello"}], temperature=0.7, max_tokens=100
            )

        mock_client.chat.completions.create.assert_called_once_with(
            model="gpt-4",
            messages=[{"role": "user", "content": "Hello"}],
            temperature=0.7,
            max_tokens=100,
        )
