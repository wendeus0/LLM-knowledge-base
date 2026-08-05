"""Dedup de duplicatas de ingestão (feature 028, B4).

Duas chaves de candidatura, ambas sobre o mesmo documento-fonte:
- `same-source`: o backfill resolve dois artigos vivos para a mesma fonte;
- `near-identical`: cosseno ≥ 0,95 E razão textual normalizada ≥ 0,85.

Par temático — vizinho por cosseno mas com texto próprio — nunca entra: é
matéria do reagrupamento (ADR-0018 vetou "V5 isolado").
"""

from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path

COSINE_MIN = 0.95
TEXT_RATIO_MIN = 0.85


@dataclass(frozen=True)
class DuplicatePair:
    survivor: Path
    loser: Path
    reason: str  # same-source | near-identical
    source: Path | None
    cosine: float | None
    text_ratio: float | None


def _body(article: Path) -> str:
    from kb.frontmatter import parse

    _, body = parse(article.read_text(encoding="utf-8", errors="replace"))
    return body


def _normalized(article: Path) -> str:
    return " ".join(_body(article).split()).casefold()


def _text_ratio(a: Path, b: Path) -> float:
    return SequenceMatcher(None, _normalized(a), _normalized(b)).ratio()


def _tem_topic(article: Path, wiki_dir: Path) -> bool:
    return len(article.relative_to(wiki_dir).parts) > 1


def _survivor_first(a: Path, b: Path, wiki_dir: Path) -> tuple[Path, Path]:
    """Path com topic vence a raiz; empate decide por tamanho do corpo."""
    topic_a, topic_b = _tem_topic(a, wiki_dir), _tem_topic(b, wiki_dir)
    if topic_a != topic_b:
        return (a, b) if topic_a else (b, a)
    palavras_a, palavras_b = len(_body(a).split()), len(_body(b).split())
    return (a, b) if palavras_a >= palavras_b else (b, a)


def _cosine(u: list[float], v: list[float]) -> float:
    import math

    dot = sum(x * y for x, y in zip(u, v, strict=True))
    norm = math.sqrt(sum(x * x for x in u)) * math.sqrt(sum(y * y for y in v))
    return dot / norm if norm else 0.0


def review_candidates(
    wiki_dir: Path,
    data_dir: Path,
    raw_dir: Path,
    vectors: dict[Path, list[float]] | None = None,
) -> list[DuplicatePair]:
    """Pares semanticamente gêmeos que a dupla-chave NÃO propõe sozinha.

    Cosseno ≥ 0,95 com ratio textual < 0,85 é ambíguo por natureza: pode ser o
    mesmo documento vindo de duas URLs (prosa reescrita pelo compile — caso
    OWASP) ou par temático legítimo. A máquina lista; o humano decide.
    """
    if not vectors:
        return []
    ja_pareados: set[Path] = set()
    for pair in find_duplicates(wiki_dir, data_dir, raw_dir, vectors=vectors):
        ja_pareados.update({pair.survivor, pair.loser})
    revisao: list[DuplicatePair] = []
    artigos = sorted(vectors)
    for i, a in enumerate(artigos):
        for b in artigos[i + 1 :]:
            if a in ja_pareados or b in ja_pareados:
                continue
            cos = _cosine(vectors[a], vectors[b])
            if cos < COSINE_MIN:
                continue
            ratio = _text_ratio(a, b)
            if ratio >= TEXT_RATIO_MIN:
                continue
            survivor, loser = _survivor_first(a, b, wiki_dir)
            revisao.append(
                DuplicatePair(
                    survivor=survivor,
                    loser=loser,
                    reason="review",
                    source=None,
                    cosine=cos,
                    text_ratio=ratio,
                )
            )
    return revisao


def article_vectors_from_index(wiki_dir: Path, state_dir: Path) -> dict[Path, list[float]]:
    """Vetor médio L2-normalizado por artigo, a partir do índice existente.

    Mesma agregação de `scripts/measure_corpus_quality.py` — nada é re-embedado.
    """
    import math

    from kb.embeddings import load_index

    index = load_index(state_dir)
    if not index:
        return {}
    vetores: dict[Path, list[float]] = {}
    for relpath, entry in index["articles"].items():
        chunks = [c.get("vector") for c in entry.get("chunks", []) if c.get("vector")]
        if not chunks:
            continue
        dim = len(chunks[0])
        media = [sum(v[i] for v in chunks) / len(chunks) for i in range(dim)]
        norma = math.sqrt(sum(x * x for x in media))
        if not norma:
            continue
        artigo = Path(wiki_dir) / relpath
        if artigo.exists():
            vetores[artigo] = [x / norma for x in media]
    return vetores


def find_duplicates(
    wiki_dir: Path,
    data_dir: Path,
    raw_dir: Path,
    vectors: dict[Path, list[float]] | None = None,
) -> list[DuplicatePair]:
    """Pares de duplicata de ingestão entre artigos vivos, com o diff decidível.

    `vectors` (artigo → vetor médio L2) habilita a chave `near-identical`;
    sem ele, só a chave por fonte roda.
    """
    from kb.backfill import backfill_links

    pares: list[DuplicatePair] = []
    emparelhados: set[Path] = set()

    por_fonte: dict[Path, list] = {}
    for link in backfill_links(wiki_dir, data_dir, raw_dir):
        if link.source is not None:
            por_fonte.setdefault(link.source, []).append(link.article)
    for fonte, artigos in sorted(por_fonte.items()):
        if len(artigos) < 2:
            continue
        ordenados = sorted(artigos)
        survivor = ordenados[0]
        for other in ordenados[1:]:
            survivor, loser = _survivor_first(survivor, other, wiki_dir)
            pares.append(
                DuplicatePair(
                    survivor=survivor,
                    loser=loser,
                    reason="same-source",
                    source=fonte,
                    cosine=None,
                    text_ratio=_text_ratio(survivor, loser),
                )
            )
            emparelhados.update({survivor, loser})

    if vectors:
        artigos = sorted(vectors)
        for i, a in enumerate(artigos):
            for b in artigos[i + 1 :]:
                if a in emparelhados or b in emparelhados:
                    continue
                cos = _cosine(vectors[a], vectors[b])
                if cos < COSINE_MIN:
                    continue
                ratio = _text_ratio(a, b)
                if ratio < TEXT_RATIO_MIN:
                    continue
                survivor, loser = _survivor_first(a, b, wiki_dir)
                pares.append(
                    DuplicatePair(
                        survivor=survivor,
                        loser=loser,
                        reason="near-identical",
                        source=None,
                        cosine=cos,
                        text_ratio=ratio,
                    )
                )
                emparelhados.update({a, b})
    return pares
