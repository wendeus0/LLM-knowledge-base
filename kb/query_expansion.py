"""Expansão de query (feature 018-expansao-de-query).

Quem pergunta raramente conhece o termo que o artigo usa — é por isso que está
perguntando. A 017 mediu o custo disso: "trajeto mais barato entre dois pontos
de uma rede" não alcança um artigo sobre grafos.

Duas estratégias. `terms` acrescenta vocabulário técnico à pergunta, preservando
o original. `hyde` gera um trecho hipotético do artigo que responderia — a busca
passa a comparar documento com documento, não pergunta com documento.
"""

import hashlib
import json
import os
import sys
from pathlib import Path

from kb.client import chat

STRATEGIES = ("terms", "hyde")
CACHE_FILENAME = "query_expansion.json"
_MAX_TOKENS_HINT = "Responda em no máximo 30 palavras, sem preâmbulo."

_PROMPTS = {
    "terms": (
        "Você indexa uma base de conhecimento técnica em português. "
        "Dada uma pergunta em linguagem coloquial, liste os termos técnicos que um "
        "artigo sobre o assunto provavelmente usaria. Apenas os termos, separados por "
        f"vírgula, sem explicar. {_MAX_TOKENS_HINT}"
    ),
    "hyde": (
        "Você escreve verbetes de uma base de conhecimento técnica em português. "
        "Dada uma pergunta, escreva o primeiro parágrafo do verbete que a responderia, "
        f"usando o vocabulário técnico da área. {_MAX_TOKENS_HINT}"
    ),
}


def _cache_path() -> Path:
    import kb.config as config

    return Path(config.STATE_DIR) / CACHE_FILENAME


def _cache_key(query: str, strategy: str) -> str:
    model = os.getenv("KB_MODEL", "")
    return hashlib.sha256(f"{model}|{strategy}|{query}".encode()).hexdigest()


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
        path.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    except OSError:
        pass


def expand_query(query: str, strategy: str = "terms") -> str:
    """Pergunta reescrita no vocabulário provável do corpus.

    Nunca levanta por causa do provider: falha vira aviso e devolve a original,
    como toda degradação do projeto.
    """
    if strategy not in STRATEGIES:
        raise ValueError(
            f"estratégia de expansão desconhecida: {strategy!r} (use {', '.join(STRATEGIES)})"
        )

    cache = _read_cache()
    key = _cache_key(query, strategy)
    if key in cache:
        return cache[key]

    try:
        generated = chat(
            messages=[
                {"role": "system", "content": _PROMPTS[strategy]},
                {"role": "user", "content": query},
            ]
        )
    except Exception as exc:
        print(f"aviso: expansão de query indisponível ({exc}) — usando a pergunta original", file=sys.stderr)
        return query

    generated = (generated or "").strip()
    if not generated:
        return query

    expanded = f"{query}\n{generated}" if strategy == "terms" else generated

    cache[key] = expanded
    _write_cache(cache)
    return expanded
