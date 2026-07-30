"""Estado do servidor de embeddings local (feature 014-embed-server-autostart).

Duas fronteiras de efeito, ambas isoláveis em teste: `_http_get_json` (rede) e
`_run_command` (processo). O resto é decisão pura sobre o estado observado.

Autostart é opt-in: o caminho padrão apenas observa e reporta, nunca inicia
processo. Sem servidor, o retrieval degrada para lexical — o que esta feature
acrescenta é tornar essa degradação visível.
"""

import json
import os
import subprocess
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field

DEFAULT_AUTOSTART_CMD = "lms server start"
DEFAULT_PROBE_TIMEOUT = 1.5
DEFAULT_AUTOSTART_TIMEOUT = 20.0
_POLL_INTERVAL = 0.5
_TRUTHY = ("1", "true", "yes", "on")


@dataclass
class ServerState:
    reachable: bool = False
    models: list[str] = field(default_factory=list)
    error: str | None = None
    endpoint: str = ""


def _http_get_json(url: str, timeout: float) -> dict:
    with urllib.request.urlopen(url, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def _run_command(cmd: str, timeout: float) -> None:
    subprocess.run(
        cmd.split(),
        check=True,
        capture_output=True,
        timeout=timeout if timeout > 0 else None,
    )


def probe(base_url: str, timeout: float = DEFAULT_PROBE_TIMEOUT) -> ServerState:
    """Consulta /v1/models e devolve o estado observado do endpoint."""
    url = f"{base_url.rstrip('/')}/models"
    try:
        payload = _http_get_json(url, timeout)
    except Exception as exc:
        return ServerState(reachable=False, error=str(exc), endpoint=base_url)
    models = [entry.get("id", "") for entry in payload.get("data", [])]
    return ServerState(reachable=True, models=models, endpoint=base_url)


def model_available(state: ServerState, model: str) -> bool:
    return state.reachable and model in state.models


def autostart_enabled() -> bool:
    return os.getenv("KB_EMBED_AUTOSTART", "").strip().lower() in _TRUTHY


def autostart_cmd() -> str:
    return os.getenv("KB_EMBED_AUTOSTART_CMD", DEFAULT_AUTOSTART_CMD)


def probe_timeout() -> float:
    return float(os.getenv("KB_EMBED_PROBE_TIMEOUT", DEFAULT_PROBE_TIMEOUT))


def autostart_timeout() -> float:
    return float(os.getenv("KB_EMBED_AUTOSTART_TIMEOUT", DEFAULT_AUTOSTART_TIMEOUT))


def ensure_server(
    base_url: str,
    autostart_enabled: bool = False,
    autostart_cmd: str = DEFAULT_AUTOSTART_CMD,
    autostart_timeout: float = DEFAULT_AUTOSTART_TIMEOUT,
    probe_timeout: float = DEFAULT_PROBE_TIMEOUT,
) -> ServerState:
    """Estado do servidor, subindo-o uma única vez quando autorizado."""
    state = probe(base_url, probe_timeout)
    if state.reachable or not autostart_enabled:
        return state

    try:
        _run_command(autostart_cmd, autostart_timeout)
    except Exception as exc:
        return ServerState(reachable=False, error=str(exc), endpoint=base_url)

    deadline = time.monotonic() + autostart_timeout
    while True:
        state = probe(base_url, probe_timeout)
        if state.reachable or time.monotonic() >= deadline:
            return state
        time.sleep(_POLL_INTERVAL)
