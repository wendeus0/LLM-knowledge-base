"""Verificação de ancoragem de afirmações contra o contexto (feature 023).

Esqueleto do ciclo RED (T-001): nomes e fronteiras existem, comportamento não.
`_http_get_json` e `_http_post_json` são as únicas fronteiras de efeito, para
que o contrato com o serviço NLI local seja testável sem rede.
"""

import ipaddress
import json
import urllib.request
from collections.abc import Mapping
from dataclasses import dataclass, field
from urllib.parse import urlparse


class GroundingUnavailable(Exception):
    """Serviço NLI indisponível ou resposta fora do contrato."""


@dataclass
class ServerState:
    reachable: bool = False
    models: list[str] = field(default_factory=list)
    error: str | None = None
    endpoint: str = ""


def _http_get_json(url: str, timeout: float, api_key: str | None = None) -> dict:
    request = urllib.request.Request(url)
    if api_key:
        request.add_header("Authorization", f"Bearer {api_key}")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def _http_post_json(url: str, payload: dict, timeout: float, api_key: str | None = None) -> dict:
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=body, method="POST")
    request.add_header("Content-Type", "application/json")
    if api_key:
        request.add_header("Authorization", f"Bearer {api_key}")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def _is_loopback(base_url: str) -> bool:
    host = urlparse(base_url).hostname
    if host == "localhost":
        return True
    try:
        return bool(host) and ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


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
    return data
