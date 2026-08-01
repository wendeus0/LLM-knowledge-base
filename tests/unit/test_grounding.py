"""Contrato HTTP do serviço NLI local (feature 023-claim-grounding, T-001).

Sem rede: `_http_get_json` e `_http_post_json` são as únicas fronteiras de
efeito, ambas monkeypatchadas — mesmo padrão que `embed_server` já usa.

O contrato entre `kb` e o serviço é uma das duas condições binárias de risco do
PLAN, então estes testes cobrem tanto o caminho feliz quanto cada forma de
payload malformado que o cliente precisa recusar sem derrubar o `qa`.
"""

import pytest

from kb import config, grounding


class TestProbe:
    def test_should_report_reachable_with_models_when_service_answers(self, monkeypatch):
        monkeypatch.setattr(
            grounding,
            "_http_get_json",
            lambda url, timeout, api_key: {"data": [{"id": "mdeberta-xnli"}]},
        )

        state = grounding.probe("http://localhost:1235/v1", timeout=1)

        assert state.reachable is True
        assert state.models == ["mdeberta-xnli"]
        assert state.error is None

    def test_should_report_unreachable_with_cause_when_service_refuses(self, monkeypatch):
        def _boom(url, timeout, api_key):
            raise OSError("connection refused")

        monkeypatch.setattr(grounding, "_http_get_json", _boom)

        state = grounding.probe("http://localhost:1235/v1", timeout=1)

        assert state.reachable is False
        assert state.models == []
        assert "connection refused" in (state.error or "")

    def test_should_ask_the_models_path_of_the_configured_base_url(self, monkeypatch):
        visto = {}

        def _captura(url, timeout, api_key):
            visto["url"] = url
            return {"data": []}

        monkeypatch.setattr(grounding, "_http_get_json", _captura)

        grounding.probe("http://localhost:1235/v1/", timeout=1)

        assert visto.get("url") == "http://localhost:1235/v1/models"

    def test_should_keep_endpoint_in_state_for_error_messages(self, monkeypatch):
        monkeypatch.setattr(grounding, "_http_get_json", lambda url, timeout, api_key: {"data": []})

        state = grounding.probe("http://localhost:1235/v1", timeout=1)

        assert state.endpoint == "http://localhost:1235/v1"

    def test_should_confirm_model_when_announced_by_service(self):
        state = grounding.ServerState(reachable=True, models=["mdeberta-xnli"], endpoint="x")

        assert grounding.model_available(state, "mdeberta-xnli") is True

    def test_should_deny_model_when_not_announced(self):
        state = grounding.ServerState(reachable=True, models=["outro"], endpoint="x")

        assert grounding.model_available(state, "mdeberta-xnli") is False

    def test_should_deny_model_when_service_is_unreachable(self):
        state = grounding.ServerState(reachable=False, models=[], endpoint="x")

        assert grounding.model_available(state, "mdeberta-xnli") is False


class TestHttpContractRequest:
    def test_should_send_model_and_pairs_in_the_request_body(self, monkeypatch):
        visto = {}

        def _captura(url, payload, timeout, api_key):
            visto.update(url=url, payload=payload)
            return {"data": [{"entailment": 0.9, "contradiction": 0.05, "neutral": 0.05}]}

        monkeypatch.setattr(grounding, "_http_post_json", _captura)

        grounding.classify(
            [("premissa", "hipotese")],
            model="mdeberta-xnli",
            base_url="http://localhost:1235/v1",
            timeout=5,
        )

        assert visto.get("url") == "http://localhost:1235/v1/nli"
        assert visto.get("payload", {}).get("model") == "mdeberta-xnli"
        assert visto.get("payload", {}).get("pairs") == [
            {"premise": "premissa", "hypothesis": "hipotese"}
        ]

    def test_should_forward_the_configured_timeout_to_the_network_boundary(self, monkeypatch):
        visto = {}

        def _captura(url, payload, timeout, api_key):
            visto["timeout"] = timeout
            return {"data": [{"entailment": 0.9, "contradiction": 0.05, "neutral": 0.05}]}

        monkeypatch.setattr(grounding, "_http_post_json", _captura)

        grounding.classify(
            [("p", "h")], model="m", base_url="http://localhost:1235/v1", timeout=7.5
        )

        assert visto.get("timeout") == 7.5

    def test_should_forward_the_api_key_to_the_network_boundary(self, monkeypatch):
        visto = {}

        def _captura(url, payload, timeout, api_key):
            visto["api_key"] = api_key
            return {"data": [{"entailment": 0.9, "contradiction": 0.05, "neutral": 0.05}]}

        monkeypatch.setattr(grounding, "_http_post_json", _captura)

        grounding.classify(
            [("p", "h")],
            model="m",
            base_url="http://localhost:1235/v1",
            timeout=5,
            api_key="segredo",
        )

        assert visto.get("api_key") == "segredo"

    def test_should_not_call_the_service_when_there_are_no_pairs(self, monkeypatch):
        def _nao_deve_chamar(url, payload, timeout, api_key):
            raise AssertionError("classify não deve fazer requisição sem pares")

        monkeypatch.setattr(grounding, "_http_post_json", _nao_deve_chamar)

        assert grounding.classify([], model="m", base_url="http://localhost:1235/v1") == []


class TestHttpContractResponse:
    def test_should_return_probabilities_in_the_same_order_as_the_pairs(self, monkeypatch):
        monkeypatch.setattr(
            grounding,
            "_http_post_json",
            lambda url, payload, timeout, api_key: {
                "data": [
                    {"entailment": 0.90, "contradiction": 0.05, "neutral": 0.05},
                    {"entailment": 0.01, "contradiction": 0.98, "neutral": 0.01},
                ]
            },
        )

        resultado = grounding.classify(
            [("p1", "h1"), ("p2", "h2")], model="m", base_url="http://localhost:1235/v1"
        )

        assert [round(r["entailment"], 2) for r in resultado] == [0.90, 0.01]
        assert [round(r["contradiction"], 2) for r in resultado] == [0.05, 0.98]

    def test_should_refuse_response_whose_length_differs_from_the_pairs(self, monkeypatch):
        monkeypatch.setattr(
            grounding,
            "_http_post_json",
            lambda url, payload, timeout, api_key: {
                "data": [{"entailment": 0.9, "contradiction": 0.05, "neutral": 0.05}]
            },
        )

        with pytest.raises(grounding.GroundingUnavailable):
            grounding.classify(
                [("p1", "h1"), ("p2", "h2")], model="m", base_url="http://localhost:1235/v1"
            )

    def test_should_refuse_entry_missing_one_of_the_three_probabilities(self, monkeypatch):
        monkeypatch.setattr(
            grounding,
            "_http_post_json",
            lambda url, payload, timeout, api_key: {
                "data": [{"entailment": 0.9, "contradiction": 0.05}]
            },
        )

        with pytest.raises(grounding.GroundingUnavailable):
            grounding.classify([("p", "h")], model="m", base_url="http://localhost:1235/v1")

    def test_should_refuse_entry_whose_probability_is_not_a_number(self, monkeypatch):
        monkeypatch.setattr(
            grounding,
            "_http_post_json",
            lambda url, payload, timeout, api_key: {
                "data": [{"entailment": "alto", "contradiction": 0.05, "neutral": 0.05}]
            },
        )

        with pytest.raises(grounding.GroundingUnavailable):
            grounding.classify([("p", "h")], model="m", base_url="http://localhost:1235/v1")

    def test_should_refuse_payload_without_the_data_field(self, monkeypatch):
        monkeypatch.setattr(
            grounding,
            "_http_post_json",
            lambda url, payload, timeout, api_key: {"resultado": []},
        )

        with pytest.raises(grounding.GroundingUnavailable):
            grounding.classify([("p", "h")], model="m", base_url="http://localhost:1235/v1")

    def test_should_refuse_payload_that_is_not_a_mapping(self, monkeypatch):
        monkeypatch.setattr(
            grounding,
            "_http_post_json",
            lambda url, payload, timeout, api_key: ["nao", "e", "objeto"],
        )

        with pytest.raises(grounding.GroundingUnavailable):
            grounding.classify([("p", "h")], model="m", base_url="http://localhost:1235/v1")

    def test_should_raise_grounding_unavailable_when_transport_fails(self, monkeypatch):
        def _boom(url, payload, timeout, api_key):
            raise TimeoutError("timed out")

        monkeypatch.setattr(grounding, "_http_post_json", _boom)

        with pytest.raises(grounding.GroundingUnavailable) as exc:
            grounding.classify([("p", "h")], model="m", base_url="http://localhost:1235/v1")

        assert "timed out" in str(exc.value)


class TestHttpContractLoopback:
    """RT-02: o serviço é local; o cliente recusa endpoint fora de loopback.

    O `kb` já tem um achado P1 aberto (F-03) sobre canais de egresso cujo host
    vem de env sem validação. Este é um canal novo que manda trecho de artigo,
    então a fronteira nasce fechada.
    """

    @pytest.mark.parametrize(
        "base_url",
        [
            "http://localhost:1235/v1",
            "http://127.0.0.1:1235/v1",
            "http://[::1]:1235/v1",
        ],
    )
    def test_should_accept_loopback_endpoints(self, base_url, monkeypatch):
        monkeypatch.setattr(
            grounding,
            "_http_post_json",
            lambda url, payload, timeout, api_key: {
                "data": [{"entailment": 0.9, "contradiction": 0.05, "neutral": 0.05}]
            },
        )

        assert grounding.classify([("p", "h")], model="m", base_url=base_url)

    def test_should_refuse_probe_outside_loopback_without_leaking_the_api_key(self, monkeypatch):
        def _nao_deve_chamar(url, timeout, api_key):
            raise AssertionError("probe não deve alcançar host fora de loopback")

        monkeypatch.setattr(grounding, "_http_get_json", _nao_deve_chamar)

        state = grounding.probe("http://exemplo.invalido:1235/v1", timeout=1, api_key="segredo")

        assert state.reachable is False
        assert "loopback" in (state.error or "")

    @pytest.mark.parametrize(
        "base_url",
        [
            "http://exemplo.invalido:1235/v1",
            "http://10.0.0.5:1235/v1",
            "http://169.254.169.254/v1",
        ],
    )
    def test_should_refuse_endpoint_outside_loopback(self, base_url, monkeypatch):
        def _nao_deve_chamar(url, payload, timeout, api_key):
            raise AssertionError(f"não deveria alcançar a rede para {base_url}")

        monkeypatch.setattr(grounding, "_http_post_json", _nao_deve_chamar)

        with pytest.raises(grounding.GroundingUnavailable):
            grounding.classify([("p", "h")], model="m", base_url=base_url)


class TestHttpContractConfig:
    def test_should_default_base_url_to_loopback_port_1235(self, monkeypatch):
        monkeypatch.delenv("KB_GROUNDING_BASE_URL", raising=False)

        assert config.grounding_base_url() == "http://localhost:1235/v1"

    def test_should_read_base_url_from_environment(self, monkeypatch):
        monkeypatch.setenv("KB_GROUNDING_BASE_URL", "http://127.0.0.1:9999/v1")

        assert config.grounding_base_url() == "http://127.0.0.1:9999/v1"

    def test_should_default_model_to_the_measured_multilingual_nli(self, monkeypatch):
        monkeypatch.delenv("KB_GROUNDING_MODEL", raising=False)

        assert "mdeberta" in config.grounding_model().lower()

    def test_should_default_max_pairs_to_the_budget_of_24(self, monkeypatch):
        monkeypatch.delenv("KB_GROUNDING_MAX_PAIRS", raising=False)

        assert config.grounding_max_pairs() == 24

    def test_should_round_max_pairs_down_to_a_multiple_of_three(self, monkeypatch):
        monkeypatch.setenv("KB_GROUNDING_MAX_PAIRS", "26")

        assert config.grounding_max_pairs() == 24

    def test_should_fall_back_to_the_default_when_max_pairs_is_not_a_number(self, monkeypatch):
        monkeypatch.setenv("KB_GROUNDING_MAX_PAIRS", "muitos")

        assert config.grounding_max_pairs() == 24

    def test_should_floor_max_pairs_at_one_group_of_three(self, monkeypatch):
        monkeypatch.setenv("KB_GROUNDING_MAX_PAIRS", "2")

        assert config.grounding_max_pairs() == 3

    def test_should_default_timeout_to_a_finite_number_of_seconds(self, monkeypatch):
        monkeypatch.delenv("KB_GROUNDING_TIMEOUT", raising=False)

        assert 0 < config.grounding_timeout() < 120
