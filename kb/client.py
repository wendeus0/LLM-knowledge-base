from openai import OpenAI
from kb.config import API_KEY, BASE_URL, MODEL


def get_client() -> OpenAI:
    if not API_KEY:
        raise RuntimeError(
            "KB_API_KEY não configurada. Defina a variável de ambiente ou adicione ao .env."
        )
    return OpenAI(api_key=API_KEY, base_url=BASE_URL)


def chat(messages: list[dict], model: str = MODEL, **kwargs) -> str:
    client = get_client()
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        **kwargs,
    )
    return response.choices[0].message.content
