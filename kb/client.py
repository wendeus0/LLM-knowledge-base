from kb.config import API_KEY, BASE_URL, MODEL

OPENCODE_GO_BASE_URL_FRAGMENT = "opencode.ai/zen/go"
OPENCODE_GO_ALLOWED_MODELS = {
    "kimi-k2.7-code",
    "kimi-k2.6",
    "kimi-k2.5",
    "minimax-m3",
    "minimax-m2.7",
    "minimax-m2.5",
    "glm-5.1",
    "glm-5",
    "deepseek-v4-pro",
    "deepseek-v4-flash",
    "qwen3.7-max",
    "qwen3.7-plus",
    "qwen3.6-plus",
    "qwen3.5-plus",
    "mimo-v2-pro",
    "mimo-v2-omni",
    "mimo-v2.5-pro",
    "mimo-v2.5",
    "hy3-preview",
}
RESOURCE_LIMIT_ERROR_MARKERS = (
    "error 1102",
    "worker exceeded resource limits",
    "worker_exceeded_resources",
)


def validate_provider_model_compatibility(base_url: str, model: str) -> None:
    normalized_base_url = base_url.strip().lower()
    normalized_model = model.strip().lower()

    if OPENCODE_GO_BASE_URL_FRAGMENT not in normalized_base_url:
        return

    if "/" in normalized_model:
        raise ValueError(
            "Modelo incompatível com OpenCode Go: use o nome simples do modelo, sem prefixos. "
            f"Exemplo válido: `kimi-k2.5`. Valor recebido: `{model}`"
        )

    if normalized_model not in OPENCODE_GO_ALLOWED_MODELS:
        allowed = ", ".join(sorted(OPENCODE_GO_ALLOWED_MODELS))
        raise ValueError(
            "Modelo não reconhecido para OpenCode Go. "
            f"Modelos validados neste projeto: {allowed}. Valor recebido: `{model}`"
        )


def is_provider_resource_limit_error(exc: Exception) -> bool:
    text = str(exc).lower()
    if any(marker in text for marker in RESOURCE_LIMIT_ERROR_MARKERS):
        return True

    body = getattr(exc, "body", None)
    if isinstance(body, dict):
        values = [
            str(body.get("error_code", "")).lower(),
            str(body.get("error_name", "")).lower(),
            str(body.get("detail", "")).lower(),
            str(body.get("title", "")).lower(),
        ]
        return any(any(marker in value for marker in RESOURCE_LIMIT_ERROR_MARKERS) for value in values)

    return False


def get_client():
    if not API_KEY:
        raise RuntimeError(
            "KB_API_KEY não está definida. Configure-a em .env ou como variável de ambiente."
        )

    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError(
            "Dependência opcional ausente: instale `openai` para usar compile/qa/heal/lint."
        ) from exc

    return OpenAI(api_key=API_KEY, base_url=BASE_URL)


def chat(messages: list[dict], model: str | None = None, **kwargs) -> str:
    resolved_model = model or MODEL
    validate_provider_model_compatibility(BASE_URL, resolved_model)

    client = get_client()
    response = client.chat.completions.create(
        model=resolved_model,
        messages=messages,
        **kwargs,
    )
    if not response.choices:
        raise RuntimeError("Provider retornou resposta vazia")
    content = response.choices[0].message.content
    if content is None or not content.strip():
        raise RuntimeError("Provider retornou resposta vazia")
    return content
