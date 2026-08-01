"""Contrato HTTP do serviço NLI local (feature 023-claim-grounding, T-001).

Sem rede: `_http_get_json` e `_http_post_json` são as únicas fronteiras de
efeito, ambas monkeypatchadas — mesmo padrão que `embed_server` já usa.

O contrato entre `kb` e o serviço é uma das duas condições binárias de risco do
PLAN, então estes testes cobrem tanto o caminho feliz quanto cada forma de
payload malformado que o cliente precisa recusar sem derrubar o `qa`.
"""

import pytest

from kb import config, grounding


@pytest.fixture(autouse=True)
def _modelo_anunciado(monkeypatch):
    """O probe do modelo é gate de produção; nos testes ele parte de anunciado."""
    monkeypatch.setattr(grounding, "_probe_cache", True, raising=False)


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

    def test_should_not_promote_a_budget_below_one_group_of_three(self, monkeypatch):
        monkeypatch.setenv("KB_GROUNDING_MAX_PAIRS", "2")

        assert config.grounding_max_pairs() == 0

    def test_should_default_timeout_to_a_finite_number_of_seconds(self, monkeypatch):
        monkeypatch.delenv("KB_GROUNDING_TIMEOUT", raising=False)

        assert 0 < config.grounding_timeout() < 120


class TestWindows:
    def _contexto(self, n):
        return " ".join(f"Sentença número {i} do contexto." for i in range(1, n + 1))

    def test_should_group_twelve_sentences_per_window(self):
        janelas = grounding.context_windows(self._contexto(12))

        assert len(janelas) == 1
        assert janelas[0].count("Sentença número") == 12

    def test_should_advance_six_sentences_between_windows(self):
        janelas = grounding.context_windows(self._contexto(18))

        assert len(janelas) >= 2
        assert "Sentença número 1 do contexto." in janelas[0]
        assert "Sentença número 7 do contexto." in janelas[1]

    def test_should_overlap_consecutive_windows(self):
        janelas = grounding.context_windows(self._contexto(18))

        assert len(janelas) >= 2
        assert "Sentença número 12 do contexto." in janelas[0]
        assert "Sentença número 12 do contexto." in janelas[1]

    def test_should_keep_the_tail_sentences_in_the_last_window(self):
        janelas = grounding.context_windows(self._contexto(20))

        assert janelas
        assert "Sentença número 20 do contexto." in janelas[-1]

    def test_should_return_one_window_when_context_is_shorter_than_the_window(self):
        janelas = grounding.context_windows("Uma frase só. E outra.")

        assert len(janelas) == 1

    def test_should_return_no_windows_when_context_is_empty(self):
        assert grounding.context_windows("   ") == []


class TestVerdict:
    def _s(self, entailment, contradiction, neutral):
        return {"entailment": entailment, "contradiction": contradiction, "neutral": neutral}

    def test_should_return_ancorada_when_entailment_dominates(self):
        candidatas = [self._s(0.90, 0.03, 0.07), self._s(0.20, 0.10, 0.70)]

        assert grounding.verdict_from_scores(candidatas) == "ancorada"

    def test_should_return_contradita_when_contradiction_passes_the_threshold(self):
        candidatas = [self._s(0.02, 0.95, 0.03), self._s(0.10, 0.20, 0.70)]

        assert grounding.verdict_from_scores(candidatas) == "contradita"

    def test_should_return_sem_apoio_when_every_candidate_is_neutral(self):
        candidatas = [self._s(0.05, 0.05, 0.90), self._s(0.10, 0.10, 0.80)]

        assert grounding.verdict_from_scores(candidatas) == "sem apoio"

    def test_should_prefer_ancorada_when_one_candidate_entails_and_another_contradicts(self):
        candidatas = [self._s(0.92, 0.04, 0.04), self._s(0.05, 0.85, 0.10)]

        assert grounding.verdict_from_scores(candidatas) == "ancorada"

    def test_should_return_sem_apoio_when_contradiction_stays_below_the_threshold(self):
        candidatas = [self._s(0.30, 0.38, 0.32)]

        assert grounding.verdict_from_scores(candidatas) == "sem apoio"

    def test_should_return_sem_apoio_when_there_is_no_candidate(self):
        assert grounding.verdict_from_scores([]) == "sem apoio"


class TestNegation:
    """O caso didático: cosseno alto e contradição alta na mesma afirmação.

    Prova que o cosseno seleciona a premissa mas não decide o veredito. Medido no
    protótipo: "o circuit breaker NÃO abre" tem cosseno 0,786 e contradição 0,998.
    """

    def test_should_mark_negated_claim_as_contradita_despite_high_cosine(self, monkeypatch):
        contexto = (
            "Após falhas consecutivas, o circuit breaker abre e interrompe novas chamadas. "
            "Depois de um intervalo de recuperação, ele permite uma chamada de teste."
        )
        afirmacao = "O circuit breaker NÃO abre após falhas consecutivas e mantém as chamadas."

        monkeypatch.setattr(
            grounding, "_embed_texts", lambda textos: [[1.0, 0.0] for _ in textos]
        )
        monkeypatch.setattr(
            grounding,
            "classify",
            lambda pairs, model, base_url, timeout=15.0, api_key=None: [
                {"entailment": 0.001, "contradiction": 0.998, "neutral": 0.001} for _ in pairs
            ],
        )

        resultado = grounding.verify(afirmacao, contexto)

        assert resultado.claims
        assert resultado.claims[0].verdict == "contradita"

    def test_should_not_let_cosine_alone_produce_a_verdict(self, monkeypatch):
        monkeypatch.setattr(
            grounding, "_embed_texts", lambda textos: [[1.0, 0.0] for _ in textos]
        )
        chamou = {"nli": False}

        def _classify(pairs, model, base_url, timeout=15.0, api_key=None):
            chamou["nli"] = True
            return [{"entailment": 0.9, "contradiction": 0.05, "neutral": 0.05} for _ in pairs]

        monkeypatch.setattr(grounding, "classify", _classify)

        grounding.verify(
            "Uma afirmação suficientemente longa para ser elegível à verificação.",
            "Um contexto qualquer com conteúdo suficiente para gerar uma janela.",
        )

        assert chamou["nli"] is True


class TestBudgetLimit:
    def _preparar(self, monkeypatch, capturados):
        monkeypatch.setattr(
            grounding, "_embed_texts", lambda textos: [[1.0, 0.0] for _ in textos]
        )

        def _classify(pairs, model, base_url, timeout=15.0, api_key=None):
            capturados.append(len(pairs))
            return [{"entailment": 0.9, "contradiction": 0.05, "neutral": 0.05} for _ in pairs]

        monkeypatch.setattr(grounding, "classify", _classify)

    def _resposta(self, n):
        return " ".join(
            f"Esta é a afirmação número {i} e ela tem tamanho suficiente para ser elegível."
            for i in range(1, n + 1)
        )

    def test_should_verify_at_most_eight_claims_within_the_default_budget(self, monkeypatch):
        capturados = []
        self._preparar(monkeypatch, capturados)

        resultado = grounding.verify(self._resposta(9), "Contexto com conteúdo suficiente.")

        assert len(resultado.claims) == 8

    def test_should_report_the_claims_left_out_by_the_limit(self, monkeypatch):
        capturados = []
        self._preparar(monkeypatch, capturados)

        resultado = grounding.verify(self._resposta(9), "Contexto com conteúdo suficiente.")

        assert resultado.unverified_due_to_limit == 1

    def test_should_never_send_more_pairs_than_the_budget(self, monkeypatch):
        capturados = []
        self._preparar(monkeypatch, capturados)

        grounding.verify(self._resposta(9), "Contexto com conteúdo suficiente.")

        assert sum(capturados) <= 24

    def test_should_not_label_omitted_claims_as_sem_apoio(self, monkeypatch):
        capturados = []
        self._preparar(monkeypatch, capturados)

        resultado = grounding.verify(self._resposta(9), "Contexto com conteúdo suficiente.")

        assert all(c.verdict != "sem apoio" for c in resultado.claims)
        assert resultado.unverified_due_to_limit == 1

    def test_should_honour_a_reduced_budget_from_the_environment(self, monkeypatch):
        capturados = []
        self._preparar(monkeypatch, capturados)
        monkeypatch.setenv("KB_GROUNDING_MAX_PAIRS", "6")

        resultado = grounding.verify(self._resposta(5), "Contexto com conteúdo suficiente.")

        assert len(resultado.claims) == 2
        assert resultado.unverified_due_to_limit == 3

    def test_should_report_zero_unverified_when_every_claim_fits(self, monkeypatch):
        capturados = []
        self._preparar(monkeypatch, capturados)

        resultado = grounding.verify(self._resposta(3), "Contexto com conteúdo suficiente.")

        assert resultado.unverified_due_to_limit == 0
        assert len(resultado.claims) == 3

    def test_should_skip_when_the_context_has_no_window(self, monkeypatch):
        capturados = []
        self._preparar(monkeypatch, capturados)

        resultado = grounding.verify(self._resposta(2), "   ")

        assert resultado.status == "skipped"
        assert resultado.claims == []

    def test_should_skip_when_there_is_no_eligible_claim(self, monkeypatch):
        capturados = []
        self._preparar(monkeypatch, capturados)

        resultado = grounding.verify("Curto.", "Contexto com conteúdo suficiente.")

        assert resultado.status == "skipped"

    def test_should_degrade_when_the_service_is_unavailable(self, monkeypatch):
        monkeypatch.setattr(
            grounding, "_embed_texts", lambda textos: [[1.0, 0.0] for _ in textos]
        )

        def _boom(pairs, model, base_url, timeout=15.0, api_key=None):
            raise grounding.GroundingUnavailable("serviço fora do ar")

        monkeypatch.setattr(grounding, "classify", _boom)

        resultado = grounding.verify(self._resposta(2), "Contexto com conteúdo suficiente.")

        assert resultado.status == "degraded"
        assert resultado.claims == []


class TestVerdictEvidence:
    """A evidência mostrada precisa ser a que produziu o veredito.

    Um veredito `contradita` acompanhado das pontuações da candidata de maior
    entailment mostra ao usuário números que contradizem o próprio rótulo.
    """

    def test_should_pick_the_contradicting_candidate_as_evidence(self):
        candidatas = [
            ("janela neutra", {"entailment": 0.30, "contradiction": 0.20, "neutral": 0.50}),
            ("janela que contradiz", {"entailment": 0.10, "contradiction": 0.85, "neutral": 0.05}),
        ]

        indice = grounding.evidence_index([s for _, s in candidatas], "contradita")

        assert candidatas[indice][0] == "janela que contradiz"

    def test_should_pick_the_entailing_candidate_as_evidence_when_anchored(self):
        candidatas = [
            {"entailment": 0.20, "contradiction": 0.10, "neutral": 0.70},
            {"entailment": 0.92, "contradiction": 0.04, "neutral": 0.04},
        ]

        assert grounding.evidence_index(candidatas, "ancorada") == 1

    def test_should_return_zero_for_evidence_index_without_candidates(self):
        assert grounding.evidence_index([], "sem apoio") == 0


class TestVerdictSelection:
    def test_should_select_candidates_by_cosine_not_by_dot_product(self, monkeypatch):
        afirmacao = "Uma afirmação longa o suficiente para passar do mínimo de caracteres."
        janelas = {
            "Janela alfa com texto suficiente para virar uma sentença inteira.": [1.0, 0.0],
            "Janela beta com texto suficiente para virar uma sentença inteira.": [0.9, 0.1],
            "Janela gama com texto suficiente para virar uma sentença inteira.": [0.8, 0.2],
            "Janela delta com texto suficiente para virar uma sentença inteira.": [5.0, 10.0],
        }
        contexto = " ".join(janelas)

        monkeypatch.setattr(
            grounding,
            "_embed_texts",
            lambda textos: [janelas.get(t.strip(), [1.0, 0.0]) for t in textos],
        )
        vistos = []

        def _classify(pairs, model, base_url, timeout=15.0, api_key=None):
            vistos.extend(premise for premise, _ in pairs)
            return [{"entailment": 0.9, "contradiction": 0.05, "neutral": 0.05} for _ in pairs]

        monkeypatch.setattr(grounding, "classify", _classify)
        monkeypatch.setattr(grounding, "context_windows", lambda ctx, **kw: list(janelas))

        grounding.verify(afirmacao, contexto)

        assert not any("delta" in premissa for premissa in vistos)


class TestHttpContractHardening:
    """Achados do review adversarial (2026-08-01)."""

    def test_should_refuse_non_finite_probability(self, monkeypatch):
        monkeypatch.setattr(
            grounding,
            "_http_post_json",
            lambda url, payload, timeout, api_key: {
                "data": [{"entailment": float("nan"), "contradiction": 0.1, "neutral": 0.9}]
            },
        )

        with pytest.raises(grounding.GroundingUnavailable):
            grounding.classify([("p", "h")], model="m", base_url="http://localhost:1235/v1")

    def test_should_refuse_infinite_probability(self, monkeypatch):
        monkeypatch.setattr(
            grounding,
            "_http_post_json",
            lambda url, payload, timeout, api_key: {
                "data": [{"entailment": float("inf"), "contradiction": 0.1, "neutral": 0.9}]
            },
        )

        with pytest.raises(grounding.GroundingUnavailable):
            grounding.classify([("p", "h")], model="m", base_url="http://localhost:1235/v1")

    def test_should_refuse_a_redirect_that_would_leak_the_api_key(self):
        handler = grounding._NoRedirect()

        with pytest.raises(grounding.GroundingUnavailable):
            handler.redirect_request(
                None, None, 302, "Found", {}, "http://attacker.invalid/capture"
            )


class TestBudgetFloor:
    def test_should_round_max_pairs_down_without_promoting_below_one_group(self, monkeypatch):
        monkeypatch.setenv("KB_GROUNDING_MAX_PAIRS", "2")

        assert config.grounding_max_pairs() == 0

    def test_should_verify_nothing_when_the_budget_is_below_one_group(self, monkeypatch):
        monkeypatch.setattr(grounding, "_embed_texts", lambda t: [[1.0, 0.0] for _ in t])

        def _nao_deve_chamar(pairs, model, base_url, timeout=15.0, api_key=None):
            raise AssertionError("orçamento zero não deve chamar o serviço")

        monkeypatch.setattr(grounding, "classify", _nao_deve_chamar)

        resultado = grounding.verify(
            "Uma afirmação longa o suficiente para ser elegível à verificação.",
            "Contexto com conteúdo suficiente.",
            max_pairs=2,
        )

        assert resultado.claims == []
        assert resultado.unverified_due_to_limit == 1


class TestModelDiscovery:
    def test_should_degrade_when_the_model_is_not_announced(self, monkeypatch):
        monkeypatch.setattr(grounding, "_embed_texts", lambda t: [[1.0, 0.0] for _ in t])
        monkeypatch.setattr(
            grounding,
            "probe",
            lambda base_url, timeout=1.5, api_key=None: grounding.ServerState(
                reachable=True, models=["outro-modelo"], endpoint=base_url
            ),
        )
        monkeypatch.setattr(grounding, "_probe_cache", None, raising=False)

        def _nao_deve_chamar(pairs, model, base_url, timeout=15.0, api_key=None):
            raise AssertionError("modelo não anunciado não deve ser classificado")

        monkeypatch.setattr(grounding, "classify", _nao_deve_chamar)

        resultado = grounding.verify(
            "Uma afirmação longa o suficiente para ser elegível à verificação.",
            "Contexto com conteúdo suficiente.",
        )

        assert resultado.status == "degraded"


class TestClaimSegmentation:
    def test_should_split_markdown_list_items_without_terminal_punctuation(self):
        texto = (
            "- O cache expira depois de sessenta segundos de inatividade\n"
            "- O circuito abre depois de cinco falhas consecutivas seguidas"
        )

        assert len(grounding.split_claims(texto)) == 2

    def test_should_keep_splitting_regular_sentences(self):
        texto = (
            "O cache expira depois de sessenta segundos de inatividade. "
            "O circuito abre depois de cinco falhas consecutivas seguidas."
        )

        assert len(grounding.split_claims(texto)) == 2


class TestHttpContractEgress:
    """O guard de loopback não vale nada se o transporte contornar o host.

    Redirect e proxy são dois caminhos para o mesmo vazamento: a URL é loopback,
    mas o `Authorization` e o trecho de artigo saem para outro host.
    """

    def test_should_disable_proxies_that_would_route_the_request_elsewhere(self, monkeypatch):
        import urllib.request

        monkeypatch.setenv("http_proxy", "http://proxy.invalido:8080")
        monkeypatch.setenv("https_proxy", "http://proxy.invalido:8080")

        # build_opener com ProxyHandler({}) remove o handler da lista; o default
        # o inclui carregando http_proxy do ambiente.
        padrao = [
            h for h in urllib.request.build_opener().handlers
            if isinstance(h, urllib.request.ProxyHandler) and h.proxies
        ]
        nosso = [
            h for h in grounding._opener().handlers
            if isinstance(h, urllib.request.ProxyHandler) and h.proxies
        ]

        assert padrao, "o ambiente do teste precisa ter proxy configurado"
        assert not nosso

    @pytest.mark.parametrize(
        "base_url",
        ["file://localhost/etc/passwd", "ftp://localhost:1235/v1", "gopher://localhost/v1"],
    )
    def test_should_refuse_schemes_other_than_http(self, base_url):
        assert grounding._is_loopback(base_url) is False

    def test_should_accept_https_on_loopback(self):
        assert grounding._is_loopback("https://localhost:1235/v1") is True


class TestProbabilityRange:
    @pytest.mark.parametrize("valor", [1.5, -0.2, 42.0])
    def test_should_refuse_probability_outside_the_unit_interval(self, valor, monkeypatch):
        monkeypatch.setattr(
            grounding,
            "_http_post_json",
            lambda url, payload, timeout, api_key: {
                "data": [{"entailment": valor, "contradiction": 0.1, "neutral": 0.1}]
            },
        )

        with pytest.raises(grounding.GroundingUnavailable):
            grounding.classify([("p", "h")], model="m", base_url="http://localhost:1235/v1")


class TestGroundingDeadline:
    def test_should_stop_issuing_calls_after_the_overall_deadline(self, monkeypatch):
        monkeypatch.setattr(grounding, "_embed_texts", lambda t: [[1.0, 0.0] for _ in t])
        chamadas = []
        relogio = {"agora": 0.0}
        monkeypatch.setattr(grounding.time, "monotonic", lambda: relogio["agora"])

        def _lento(pairs, model, base_url, timeout=15.0, api_key=None):
            chamadas.append(len(pairs))
            relogio["agora"] += 30.0
            return [{"entailment": 0.9, "contradiction": 0.05, "neutral": 0.05} for _ in pairs]

        monkeypatch.setattr(grounding, "classify", _lento)

        resposta = " ".join(
            f"Esta é a afirmação número {i} com tamanho suficiente para ser elegível."
            for i in range(1, 7)
        )
        resultado = grounding.verify(resposta, "Contexto com conteúdo suficiente.")

        assert len(chamadas) < 6
        assert resultado.unverified_due_to_limit >= 1


class TestConfigTimeout:
    @pytest.mark.parametrize("valor", ["0", "-5", "0.0"])
    def test_should_fall_back_when_timeout_is_not_positive(self, valor, monkeypatch):
        monkeypatch.setenv("KB_GROUNDING_TIMEOUT", valor)

        assert config.grounding_timeout() == config.GROUNDING_TIMEOUT_DEFAULT
