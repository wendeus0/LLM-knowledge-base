"""Guardas de segurança compartilhados pelas apps HTTP locais (kb/api e study)."""

import os
from urllib.parse import urlsplit

from starlette.requests import Request
from starlette.responses import JSONResponse

_LOOPBACK_HOSTS = {"127.0.0.1", "::1", "localhost"}
_UNSAFE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


def _remote_access_allowed() -> bool:
    return os.getenv("KB_ALLOW_REMOTE_ACCESS", "").strip().lower() in {"1", "true", "yes"}


async def loopback_only_middleware(request: Request, call_next):
    """Recusa requisições de fora do loopback, salvo opt-in explícito.

    A checagem é por conexão, não por bind: funciona mesmo se o servidor
    subir com --host 0.0.0.0, porque o IP de origem de um cliente remoto
    nunca é loopback.
    """
    client_host = request.client.host if request.client else None
    if not _remote_access_allowed() and client_host not in _LOOPBACK_HOSTS:
        return JSONResponse(status_code=403, content={"detail": "Acesso restrito a localhost."})
    return await call_next(request)


def _same_origin(candidate: str, request: Request) -> bool:
    """Compara origem declarada e origem da requisição.

    Cabeçalho malformado (porta fora de faixa, IPv6 truncado) faz `.port`
    levantar `ValueError`: sem o guard, a exceção escapava do middleware e
    devolvia 500 no lugar da recusa.
    """
    try:
        parsed = urlsplit(candidate)
        candidate_port = parsed.port or (443 if parsed.scheme == "https" else 80)
        candidate_host = parsed.hostname
        request_port = request.url.port or (443 if request.url.scheme == "https" else 80)
    except ValueError:
        return False
    # Origem é a tripla (esquema, host, porta): comparar só host e porta deixa
    # `https://host:80` passar por uma requisição `http://host:80`.
    return (
        parsed.scheme == request.url.scheme
        and candidate_host == request.url.hostname
        and candidate_port == request_port
    )


async def reject_cross_origin_writes_middleware(request: Request, call_next):
    """CSRF sem sessão/cookie: valida Origin/Referer em métodos que mutam estado.

    Ausência dos dois cabeçalhos não é bloqueada de propósito — um navegador
    não tem como forjar uma requisição cross-site sem enviar pelo menos um
    dos dois (Origin em toda requisição fetch/XHR/form não-GET, mesmo
    same-origin). A falta de ambos indica cliente não-navegador, fora do
    modelo de ameaça de CSRF.
    """
    if request.method in _UNSAFE_METHODS:
        source = request.headers.get("origin") or request.headers.get("referer")
        if source and not _same_origin(source, request):
            return JSONResponse(status_code=403, content={"detail": "Origem não autorizada."})
    return await call_next(request)
