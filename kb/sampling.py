"""Perfis de sampling por tarefa (feature 022-perfis-de-sampling).

Nenhuma chamada ao LLM declarava amostragem: todas herdavam o default do
provider — 0,8 no Ollama. Na 021 isso rendeu 36 índices fora da faixa de 20
candidatos no rerank, e o resultado ficou abaixo de não reordenar.

Ordenar índices e inventar perguntas são tarefas opostas. Cada uma declara o
seu perfil aqui, em vez de herdar um número que serve mal às duas.

Somente `temperature` e `top_p`: são o que o protocolo OpenAI-compat aceita.
`top_k`, `min_p` e `repeat_penalty` só trafegam pela API nativa do runtime.
"""

import os

PROFILES: dict[str, dict] = {
    # Índices, classificação, extração: qualquer variação é erro.
    "deterministic": {"temperature": 0.0, "top_p": 1.0},
    # Analisar, responder, editar sem inventar.
    "analytical": {"temperature": 0.2, "top_p": 0.9},
    # Escrever prosa: precisa de alguma folga para não sair engessado.
    "generative": {"temperature": 0.6, "top_p": 0.95},
    # Gerar casos de avaliação: variedade é o objetivo.
    "diverse": {"temperature": 0.9, "top_p": 0.95},
}


def _override(profile: str) -> float | None:
    raw = os.getenv(f"KB_SAMPLING_{profile.upper()}_TEMP")
    if raw is None:
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def params(profile: str) -> dict:
    """Parâmetros de amostragem do perfil, prontos para repassar ao provider."""
    if profile not in PROFILES:
        raise ValueError(
            f"perfil de sampling desconhecido: {profile!r} "
            f"(use {', '.join(sorted(PROFILES))})"
        )

    resolved = dict(PROFILES[profile])
    override = _override(profile)
    if override is not None:
        resolved["temperature"] = override
    return resolved
