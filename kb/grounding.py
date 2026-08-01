"""Verificação de ancoragem de afirmações contra o contexto (feature 023).

Esqueleto do ciclo RED (T-001): nomes e fronteiras existem, comportamento não.
`_http_get_json` e `_http_post_json` são as únicas fronteiras de efeito, para
que o contrato com o serviço NLI local seja testável sem rede.
"""

import json
import urllib.request
from dataclasses import dataclass, field


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


def probe(base_url: str, timeout: float = 1.5, api_key: str | None = None) -> ServerState:
    """Consulta /v1/models e devolve o estado observado do serviço NLI."""
    return ServerState()


def model_available(state: ServerState, model: str) -> bool:
    return False


def classify(
    pairs,
    model: str,
    base_url: str,
    timeout: float = 15.0,
    api_key: str | None = None,
) -> list[dict]:
    """Classifica pares premissa/hipótese, preservando a ordem de entrada."""
    return []
