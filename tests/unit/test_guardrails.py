import pytest

from kb.guardrails import SensitiveContentError, assert_safe_for_provider, detect_sensitive_content


def test_should_detect_sensitive_patterns():
    findings = detect_sensitive_content("api_key=abc1234567890\npassword=secret")

    labels = {finding.label for finding in findings}
    assert "api_key" in labels
    assert "password" in labels


def test_should_raise_when_sensitive_content_is_sent():
    with pytest.raises(SensitiveContentError):
        assert_safe_for_provider("token=abcd1234", source="qa:test")


def test_should_allow_sensitive_when_explicitly_enabled():
    assert_safe_for_provider("secret=my-secret", source="qa:test", allow_sensitive=True)
