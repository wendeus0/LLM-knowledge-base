"""Rerank do top-N por LLM (feature 020-rerank-llm).

O artigo certo costuma ser recuperado e mal ordenado: no golden de 152 casos,
recall@5 é 0,414 e recall@20 é 0,720. Cosseno e BM25 medem proximidade; quem
julga relevância de verdade é quem lê a pergunta e o trecho.

Toda a defesa está no parsing: o modelo devolve texto livre, e nenhuma resposta
malformada pode fazer um resultado desaparecer.
"""

import hashlib
import json
import os
import re
import sys
from pathlib import Path

from kb.client import chat
from kb.guardrails import new_sentinel, untrusted_policy, wrap_untrusted
from kb.sampling import params

CACHE_FILENAME = "rerank.json"
_SNIPPET_CHARS = 300

_PROMPT = (
    "Você seleciona artigos de uma base de conhecimento técnica. Dada uma pergunta e "
    "uma lista numerada de candidatos, ordene os números do mais relevante para o menos "
    "relevante. Responda APENAS com os números separados por vírgula, sem explicar."
)


_SEVERE_OMISSION_RATIO = 0.5

_STATS_TEMPLATE = {
    "calls": 0,
    "cache_hits": 0,
    "failed": 0,
    "unparseable": 0,
    "severe_omission": 0,
    "requested_total": 0,
    "returned_total": 0,
    "out_of_range_total": 0,
    "duplicates_total": 0,
}

_stats: dict[str, int] = dict(_STATS_TEMPLATE)


def reset_stats() -> None:
    global _stats
    _stats = dict(_STATS_TEMPLATE)


def stats() -> dict:
    """Diagnóstico das chamadas de rerank desta execução.

    O parsing descarta índice inválido e omitido em silêncio; sem estes números,
    um modelo que devolve 3 de 20 posições parece "rerank que não funcionou".
    """
    snapshot = dict(_stats)
    requested = snapshot["requested_total"]
    snapshot["coverage"] = (
        snapshot["returned_total"] / requested if requested else 0.0
    )
    return snapshot


def parse_order_with_stats(answer: str, size: int) -> tuple[list[int], dict]:
    """Índices 0-based válidos, mais o diagnóstico do que foi descartado."""
    seen: list[int] = []
    out_of_range = 0
    duplicates = 0

    for token in re.findall(r"\d+", answer or ""):
        position = int(token) - 1
        if not (0 <= position < size):
            out_of_range += 1
            continue
        if position in seen:
            duplicates += 1
            continue
        seen.append(position)

    return seen, {
        "requested": size,
        "returned": len(seen),
        "out_of_range": out_of_range,
        "duplicates": duplicates,
        "coverage": len(seen) / size if size else 0.0,
    }


def parse_order(answer: str, size: int) -> list[int]:
    """Números da resposta em índices 0-based, sem inválidos nem repetidos."""
    order, _ = parse_order_with_stats(answer, size)
    return order


def _cache_path() -> Path:
    import kb.config as config

    return Path(config.STATE_DIR) / CACHE_FILENAME


def rerank_model() -> str:
    """Modelo do rerank; cai para o modelo geral quando não há um dedicado."""
    return os.getenv("KB_RERANK_MODEL") or os.getenv("KB_MODEL", "")


def rerank_base_url() -> str:
    return os.getenv("KB_RERANK_BASE_URL") or os.getenv("KB_BASE_URL", "")


def _call_llm(messages: list[dict]) -> str:
    """Fronteira de rede do rerank — provider próprio quando configurado.

    Ordenar índices não admite variação: os dois caminhos usam o perfil
    determinístico. Com o default do provider (0,8 no Ollama), a 021 mediu 36
    índices fora da faixa de 20 candidatos.
    """
    sampling = params("deterministic")
    dedicated_url = os.getenv("KB_RERANK_BASE_URL")
    if not dedicated_url:
        return chat(messages=messages, model=rerank_model(), **sampling)

    from openai import OpenAI

    client = OpenAI(
        api_key=os.getenv("KB_RERANK_API_KEY", "ollama"), base_url=dedicated_url
    )
    response = client.chat.completions.create(
        model=rerank_model(), messages=messages, **sampling
    )
    return response.choices[0].message.content or ""


def preflight() -> None:
    """Confirma que o provider de rerank responde, antes de rodar um lote.

    Existe porque uma queda de energia derrubou o túnel no meio de uma medição:
    152 chamadas falharam, cada uma degradou corretamente para a ordem original,
    e o resultado final foi idêntico à baseline — 18 minutos para produzir um
    número que parecia válido e não media nada.
    """
    try:
        _call_llm([{"role": "user", "content": "Responda apenas: 1"}])
    except Exception as exc:
        raise RuntimeError(
            f"provider de rerank não respondeu ({rerank_base_url() or 'default'}, "
            f"modelo {rerank_model()}): {exc}. Corrija antes de rodar o lote — "
            "sem isso a medição degrada para a baseline sem avisar."
        ) from exc


def _cache_key(question: str, candidates: list[dict]) -> str:
    """Inclui modelo e sampling: os dois mudam a resposta, os dois invalidam."""
    model = rerank_model()
    sampling = json.dumps(params("deterministic"), sort_keys=True)
    slugs = "|".join(candidate.get("slug", "") for candidate in candidates)
    return hashlib.sha256(f"{model}|{sampling}|{question}|{slugs}".encode()).hexdigest()


def _read_cache() -> dict:
    path = _cache_path()
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _write_cache(cache: dict) -> None:
    path = _cache_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        path.write_text(json.dumps(cache), encoding="utf-8")
    except OSError:
        pass


def _apply_order(candidates: list[dict], order: list[int]) -> list[dict]:
    """Ordenados primeiro; omitidos preservam a ordem original no fim."""
    ordered = [candidates[position] for position in order]
    remaining = [c for index, c in enumerate(candidates) if index not in set(order)]
    return ordered + remaining


def rerank(question: str, candidates: list[dict]) -> list[dict]:
    if len(candidates) < 2:
        return candidates

    cache = _read_cache()
    key = _cache_key(question, candidates)
    if key in cache:
        _stats["cache_hits"] += 1
        return _apply_order(candidates, cache[key])

    listing = "\n".join(
        f"{index}. {c.get('title') or c.get('slug')} — {(c.get('snippet') or '')[:_SNIPPET_CHARS]}"
        for index, c in enumerate(candidates, start=1)
    )

    # Slug e snippet vêm de artigos da wiki — conteúdo de terceiro. O dano aqui
    # é menor (a resposta é parseada só para inteiros), mas um artigo envenenado
    # controlaria a ordenação do retrieval.
    sentinel = new_sentinel()
    try:
        answer = _call_llm(
            [
                {"role": "system", "content": _PROMPT + untrusted_policy(sentinel)},
                {
                    "role": "user",
                    "content": (
                        f"Pergunta: {question}\n\nCandidatos:\n"
                        f"{wrap_untrusted(listing, sentinel)}"
                    ),
                },
            ]
        )
    except Exception as exc:
        _stats["failed"] += 1
        print(f"aviso: rerank indisponível ({exc}) — mantendo a ordem original", file=sys.stderr)
        return candidates

    order, call_stats = parse_order_with_stats(answer or "", len(candidates))

    _stats["calls"] += 1
    _stats["requested_total"] += call_stats["requested"]
    _stats["returned_total"] += call_stats["returned"]
    _stats["out_of_range_total"] += call_stats["out_of_range"]
    _stats["duplicates_total"] += call_stats["duplicates"]
    if call_stats["coverage"] < _SEVERE_OMISSION_RATIO:
        _stats["severe_omission"] += 1

    if not order:
        _stats["unparseable"] += 1
        return candidates

    cache[key] = order
    _write_cache(cache)
    return _apply_order(candidates, order)
