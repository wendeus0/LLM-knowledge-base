"""Verificação de ancoragem de afirmações contra o contexto (feature 023).

O cosseno seleciona a premissa e o NLI julga: similaridade não decide veredito.
`_http_get_json`, `_http_post_json` e `_embed_texts` são as únicas fronteiras de
efeito, para que o contrato com o serviço NLI local seja testável sem rede.
"""

import json
import math
import re
import time
import urllib.request
from collections.abc import Mapping
from dataclasses import dataclass, field

from kb.guardrails import is_loopback as _is_loopback


class GroundingUnavailable(Exception):
    """Serviço NLI indisponível ou resposta fora do contrato."""


@dataclass
class ServerState:
    reachable: bool = False
    models: list[str] = field(default_factory=list)
    error: str | None = None
    endpoint: str = ""


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise GroundingUnavailable(f"redirect recusado para {newurl}")


def _opener():
    return urllib.request.build_opener(urllib.request.ProxyHandler({}), _NoRedirect)


def _http_get_json(url: str, timeout: float, api_key: str | None = None) -> dict:
    request = urllib.request.Request(url)
    if api_key:
        request.add_header("Authorization", f"Bearer {api_key}")
    with _opener().open(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def _http_post_json(url: str, payload: dict, timeout: float, api_key: str | None = None) -> dict:
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=body, method="POST")
    request.add_header("Content-Type", "application/json")
    if api_key:
        request.add_header("Authorization", f"Bearer {api_key}")
    with _opener().open(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def probe(base_url: str, timeout: float = 1.5, api_key: str | None = None) -> ServerState:
    """Consulta /v1/models e devolve o estado observado do serviço NLI."""
    if not _is_loopback(base_url):
        return ServerState(reachable=False, error="endpoint NLI fora de loopback", endpoint=base_url)
    url = f"{base_url.rstrip('/')}/models"
    try:
        payload = _http_get_json(url, timeout, api_key)
        models = [entry["id"] for entry in payload["data"]]
    except Exception as exc:
        return ServerState(reachable=False, error=str(exc), endpoint=base_url)
    return ServerState(reachable=True, models=models, endpoint=base_url)


def model_available(state: ServerState, model: str) -> bool:
    return state.reachable and model in state.models


def classify(
    pairs,
    model: str,
    base_url: str,
    timeout: float = 15.0,
    api_key: str | None = None,
) -> list[dict]:
    """Classifica pares premissa/hipótese, preservando a ordem de entrada."""
    if not pairs:
        return []

    if not _is_loopback(base_url):
        raise GroundingUnavailable("endpoint NLI fora de loopback")

    payload = {
        "model": model,
        "pairs": [{"premise": premise, "hypothesis": hypothesis} for premise, hypothesis in pairs],
    }
    try:
        response = _http_post_json(
            f"{base_url.rstrip('/')}/nli", payload, timeout, api_key
        )
    except Exception as exc:
        raise GroundingUnavailable(str(exc)) from exc

    if not isinstance(response, Mapping) or "data" not in response:
        raise GroundingUnavailable("resposta NLI fora do contrato")
    data = response["data"]
    if not isinstance(data, list) or len(data) != len(pairs):
        raise GroundingUnavailable("resposta NLI fora do contrato")
    for entry in data:
        if not isinstance(entry, Mapping):
            raise GroundingUnavailable("resposta NLI fora do contrato")
        for probability in ("entailment", "contradiction", "neutral"):
            value = entry.get(probability)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise GroundingUnavailable("resposta NLI fora do contrato")
            if not math.isfinite(value) or not 0.0 <= value <= 1.0:
                raise GroundingUnavailable("resposta NLI fora do contrato")
    return data


SENTENCES_PER_WINDOW = 12
WINDOW_STEP = 6
CANDIDATES_PER_CLAIM = 3
CONTRADICTION_THRESHOLD = 0.5
MIN_CLAIM_CHARS = 40
DEADLINE_FACTOR = 2


@dataclass
class ClaimVerdict:
    claim: str
    verdict: str
    evidence: str = ""
    scores: dict = field(default_factory=dict)


@dataclass
class GroundingResult:
    status: str = "skipped"
    claims: list = field(default_factory=list)
    unverified_due_to_limit: int = 0

    @property
    def checked_claims(self) -> int:
        return len(self.claims)


def _embed_texts(texts):
    from kb.embeddings import embed_texts

    return embed_texts(texts)


def _split_units(text: str) -> list[str]:
    unidades = []
    for linha in text.splitlines():
        despido = re.sub(r"^\s*(?:[-*+]|\d+[.)])\s+", "", linha).strip()
        if despido:
            unidades.extend(re.split(r"(?<=[.!?])\s+", despido))
    return unidades


def split_claims(text: str, minimum: int = MIN_CLAIM_CHARS) -> list[str]:
    """Afirmações elegíveis do texto gerado."""
    return [
        unidade.strip()
        for unidade in _split_units(text)
        if len(unidade.strip()) >= minimum
    ]


def context_windows(
    context: str,
    per_window: int = SENTENCES_PER_WINDOW,
    step: int = WINDOW_STEP,
) -> list[str]:
    """Janelas deslizantes de sentenças usadas como premissa."""
    sentences = [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+", context.strip())
        if sentence.strip()
    ]
    if not sentences:
        return []
    if len(sentences) <= per_window:
        return [" ".join(sentences)]

    last_start = len(sentences) - per_window
    starts = list(range(0, last_start + 1, step))
    if starts[-1] != last_start:
        starts.append(last_start)
    return [" ".join(sentences[start:start + per_window]) for start in starts]


def verdict_from_scores(candidates) -> str:
    """Mapeia as pontuações das candidatas em um dos três vereditos (RT-04)."""
    if any(
        candidate["entailment"] > max(candidate["contradiction"], candidate["neutral"])
        for candidate in candidates
    ):
        return "ancorada"
    if any(candidate["contradiction"] > CONTRADICTION_THRESHOLD for candidate in candidates):
        return "contradita"
    return "sem apoio"


def evidence_index(scores, verdict: str) -> int:
    """Índice da candidata que produziu o veredito, para evidência coerente."""
    if not scores:
        return 0
    rotulo = "contradiction" if verdict == "contradita" else "entailment"
    return max(range(len(scores)), key=lambda index: scores[index][rotulo])


def _cosine(left, right) -> float:
    produto = sum(a * b for a, b in zip(left, right, strict=True))
    norma = (sum(a * a for a in left) ** 0.5) * (sum(b * b for b in right) ** 0.5)
    return produto / norma if norma else 0.0


_probe_cache = None


def _model_ready() -> bool:
    global _probe_cache
    from kb import config

    if _probe_cache is None:
        state = probe(
            config.grounding_base_url(),
            timeout=config.grounding_timeout(),
            api_key=config.grounding_api_key(),
        )
        _probe_cache = model_available(state, config.grounding_model())
    return _probe_cache


def verify(response: str, context: str, max_pairs: int | None = None) -> GroundingResult:
    """Verifica a ancoragem de cada afirmação elegível contra o contexto."""
    from kb import config

    claims = split_claims(response)
    windows = context_windows(context)
    if not claims or not windows:
        return GroundingResult()

    if max_pairs is None:
        max_pairs = config.grounding_max_pairs()
    checked = claims[:max(0, max_pairs) // CANDIDATES_PER_CLAIM]
    unverified_due_to_limit = len(claims) - len(checked)
    if not checked:
        return GroundingResult(status="verified", unverified_due_to_limit=unverified_due_to_limit)

    if not _model_ready():
        return GroundingResult(status="degraded")

    prazo = time.monotonic() + config.grounding_timeout() * DEADLINE_FACTOR
    try:
        claim_vectors = _embed_texts(checked)
        window_vectors = _embed_texts(windows)
        claim_verdicts = []
        for claim, claim_vector in zip(checked, claim_vectors, strict=True):
            if time.monotonic() >= prazo:
                unverified_due_to_limit += len(checked) - len(claim_verdicts)
                break
            candidates = sorted(
                zip(windows, window_vectors, strict=True),
                key=lambda item: _cosine(claim_vector, item[1]),
                reverse=True,
            )[:CANDIDATES_PER_CLAIM]
            scores = classify(
                [(window, claim) for window, _ in candidates],
                model=config.grounding_model(),
                base_url=config.grounding_base_url(),
                timeout=config.grounding_timeout(),
                api_key=config.grounding_api_key(),
            )
            verdict = verdict_from_scores(scores)
            best_index = evidence_index(scores, verdict)
            claim_verdicts.append(
                ClaimVerdict(
                    claim=claim,
                    verdict=verdict,
                    evidence=candidates[best_index][0],
                    scores=scores[best_index],
                )
            )
    except GroundingUnavailable:
        return GroundingResult(status="degraded")

    return GroundingResult(
        status="verified",
        claims=claim_verdicts,
        unverified_due_to_limit=unverified_due_to_limit,
    )
