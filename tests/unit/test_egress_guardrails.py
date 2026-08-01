"""RED — F-03: guardrail de egresso nos canais de embeddings e rerank."""

import sys
from types import SimpleNamespace

import pytest

from kb import embeddings, guardrails
from kb import rerank as rerank_module
from kb.guardrails import SensitiveContentError


@pytest.fixture
def fake_openai(monkeypatch):
    calls = []

    class OpenAI:
        def __init__(self, **kwargs):
            self.embeddings = self

        def create(self, **kwargs):
            calls.append(kwargs)
            return SimpleNamespace(
                data=[SimpleNamespace(embedding=[1.0, 0.0]) for _ in kwargs["input"]]
            )

    monkeypatch.setitem(sys.modules, "openai", SimpleNamespace(OpenAI=OpenAI))
    return calls


@pytest.fixture
def candidates():
    return [
        {"slug": "alpha", "title": "Alpha", "snippet": "conteúdo alpha"},
        {"slug": "bravo", "title": "Bravo", "snippet": "conteúdo bravo"},
    ]


@pytest.mark.parametrize("base_url", ["file:///tmp/embed", "ftp://provider.example/v1"])
def test_should_reject_non_http_schemes_before_embedding_request(fake_openai, base_url):
    # RED: falha até F-03 bloquear esquemas que não sejam HTTP(S).
    with pytest.raises(ValueError):
        embeddings.embed_texts(["conteúdo limpo"], base_url=base_url)

    assert fake_openai == []


@pytest.mark.parametrize("base_url", ["file:///tmp/rerank", "ftp://provider.example/v1"])
def test_should_reject_non_http_schemes_before_rerank_request(monkeypatch, candidates, base_url):
    # RED: falha até F-03 bloquear esquemas que não sejam HTTP(S).
    calls = []
    monkeypatch.setenv("KB_RERANK_BASE_URL", base_url)
    monkeypatch.setattr(
        rerank_module, "_call_llm", lambda messages: calls.append(messages) or "2, 1"
    )

    assert rerank_module.rerank("pergunta limpa", candidates) == candidates
    assert calls == []


def test_should_skip_sensitive_gate_for_loopback_endpoints(fake_openai, monkeypatch, candidates):
    # RED: falha até F-03 distinguir loopback de egresso remoto.
    def _unexpected(*args, **kwargs):
        raise AssertionError("loopback não deve passar pelo gate de sensível")

    monkeypatch.setattr(guardrails, "assert_safe_for_provider", _unexpected)
    monkeypatch.delenv("KB_EMBED_BASE_URL", raising=False)
    monkeypatch.setenv("KB_RERANK_BASE_URL", "http://localhost:8081/v1")
    monkeypatch.setattr(rerank_module, "_call_llm", lambda messages: "2, 1")

    assert embeddings.embed_texts(["password: local-only"]) == [[1.0, 0.0]]
    assert rerank_module.rerank("password: local-only", candidates) == list(reversed(candidates))


def test_should_raise_sensitive_content_error_for_remote_embeddings(fake_openai):
    # RED: falha até F-03 aplicar o gate ao payload enviado para embeddings remotos.
    with pytest.raises(SensitiveContentError) as error:
        embeddings.embed_texts(
            ["password: segredo"], base_url="https://embeddings.example/v1"
        )

    assert error.value.source == "embeddings"
    assert fake_openai == []


def test_should_keep_original_order_for_sensitive_remote_rerank(monkeypatch, candidates):
    # RED: falha até F-03 degradar rerank ao bloquear conteúdo sensível remoto.
    calls = []
    monkeypatch.setenv("KB_RERANK_BASE_URL", "https://rerank.example/v1")
    monkeypatch.setattr(
        rerank_module, "_call_llm", lambda messages: calls.append(messages) or "2, 1"
    )
    candidates[0]["snippet"] = "password: segredo"

    assert rerank_module.rerank("pergunta limpa", candidates) == candidates
    assert calls == []


def test_should_guard_clean_remote_payloads_and_warn_once(fake_openai, monkeypatch, capsys):
    # RED: falha até F-03 guardar payload remoto e avisar sobre opt-in ausente.
    seen = []

    def _safe(text, source, allow_sensitive=False):
        seen.append((text, source, allow_sensitive))

    monkeypatch.setattr(guardrails, "assert_safe_for_provider", _safe)
    monkeypatch.delenv("KB_EGRESS_REMOTE_OK", raising=False)

    embeddings.embed_texts(["primeiro payload"], base_url="https://embeddings.example/v1")
    embeddings.embed_texts(["segundo payload"], base_url="https://embeddings.example/v1")

    assert seen == [
        ("primeiro payload", "embeddings", False),
        ("segundo payload", "embeddings", False),
    ]
    assert capsys.readouterr().err.count("KB_EGRESS_REMOTE_OK") == 1


def test_should_keep_default_loopback_endpoints_silent(fake_openai, monkeypatch, capsys, candidates):
    # RED: falha até F-03 preservar os defaults locais sem aviso de egresso.
    monkeypatch.delenv("KB_EMBED_BASE_URL", raising=False)
    monkeypatch.delenv("KB_RERANK_BASE_URL", raising=False)
    monkeypatch.delenv("KB_BASE_URL", raising=False)
    monkeypatch.setattr("kb.config.BASE_URL", "http://localhost:8081/v1")
    calls = []
    monkeypatch.setattr(
        rerank_module, "_call_llm", lambda messages: calls.append(messages) or "2, 1"
    )

    embeddings.embed_texts(["conteúdo local"])
    assert rerank_module.rerank("pergunta local", candidates) == list(reversed(candidates))

    assert len(calls) == 1
    assert "KB_EGRESS_REMOTE_OK" not in capsys.readouterr().err
