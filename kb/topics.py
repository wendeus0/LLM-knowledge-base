"""Normalização e atribuição de topics no frontmatter (feature 028, B6/B7).

O serializer de frontmatter não faz round-trip fiel, então toda escrita aqui é
regex in-place na linha `topic:` do bloco de frontmatter (padrão de
`heal._stamp_reviewed`), com escrita atômica — o resto do arquivo fica byte a
byte como estava.
"""

import re
from dataclasses import dataclass
from pathlib import Path

# Mapa fechado com o dono (2026-08-05): variante → canônico.
VARIANT_MAP: dict[str, str] = {
    "geral": "general",
    "architecture": "software-architecture",
    "software-design": "software-architecture",
    "ddd": "software-architecture",
    "domain-driven-design": "software-architecture",
    "hexagonal": "software-architecture",
    "event-driven-architecture": "software-architecture",
    "api": "software-architecture",
    "data-engineering": "data",
    "observability": "operations",
    "devops": "operations",
    "tensorflow": "ai",
    "mathematics": "algorithms",
}

_TOPIC_LINE = re.compile(r"^(topic:\s*)(.+?)\s*$", re.M)


@dataclass(frozen=True)
class TopicProposal:
    article: Path
    old: str
    new: str | None
    rejected: bool = False


def _frontmatter_span(text: str) -> tuple[int, int] | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return None
    return 0, end + len("\n---")


def _current_topic(text: str) -> tuple[str, tuple[int, int]] | None:
    span = _frontmatter_span(text)
    if span is None:
        return None
    match = _TOPIC_LINE.search(text, span[0], span[1])
    if match is None:
        return None
    return match.group(2).strip().strip("'\""), match.span(2)


def apply_topic(article: Path, new_topic: str) -> None:
    """Troca só o valor da linha `topic:` do frontmatter, atomicamente."""
    from kb.fsutil import atomic_write_text

    text = article.read_text(encoding="utf-8")
    atual = _current_topic(text)
    if atual is None:
        raise ValueError(f"artigo sem linha topic no frontmatter: {article}")
    _, (start, end) = atual
    atomic_write_text(article, text[:start] + new_topic + text[end:])


def _iter_articles(wiki_dir: Path):
    for path in sorted(Path(wiki_dir).rglob("*.md")):
        rel = path.relative_to(wiki_dir)
        if any(part.startswith(("_", ".")) for part in rel.parts):
            continue
        yield path


def normalize_variants(wiki_dir: Path) -> list[TopicProposal]:
    """Propostas determinísticas: topic no mapa de variantes → canônico."""
    propostas: list[TopicProposal] = []
    for article in _iter_articles(wiki_dir):
        atual = _current_topic(article.read_text(encoding="utf-8", errors="replace"))
        if atual is None:
            continue
        topic, _ = atual
        alvo = VARIANT_MAP.get(topic)
        if alvo and alvo != topic:
            propostas.append(TopicProposal(article=article, old=topic, new=alvo))
    return propostas


_ASSIGN_PROMPT = (
    "Classifique o artigo abaixo em exatamente um topic desta lista, respondendo "
    "somente com o topic, sem explicação: {taxonomia}.\n\n"
    "Arquivo: {nome}\nTítulo: {titulo}\n\nInício do artigo:\n{inicio}"
)


def propose_topics(articles, taxonomy: list[str], chat_fn) -> list[TopicProposal]:
    """Proposta de topic via LLM, com rejeição dura fora da taxonomia."""
    from kb.frontmatter import parse

    validos = {t.strip().casefold() for t in taxonomy}
    propostas: list[TopicProposal] = []
    for article in articles:
        text = article.read_text(encoding="utf-8", errors="replace")
        meta, body = parse(text)
        atual = (meta.get("topic") or "").strip().strip("'\"")
        prompt = _ASSIGN_PROMPT.format(
            taxonomia=", ".join(taxonomy),
            nome=article.name,
            titulo=(meta.get("title") or "").strip('"'),
            inicio=" ".join(body.split()[:180]),
        )
        try:
            resposta = chat_fn([{"role": "user", "content": prompt}], temperature=0)
        except Exception:
            propostas.append(TopicProposal(article=article, old=atual, new=None, rejected=True))
            continue
        proposto = (resposta or "").strip().strip(".").casefold()
        if proposto in validos:
            propostas.append(TopicProposal(article=article, old=atual, new=proposto))
        else:
            propostas.append(TopicProposal(article=article, old=atual, new=None, rejected=True))
    return propostas
