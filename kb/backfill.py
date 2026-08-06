"""Reconstrução retroativa da proveniência artigo→fonte (feature 028, B2).

O frontmatter guarda só o basename da fonte (`source: 07-cap.md`); as fontes
vivem em `library/**`, `wiki/_sources/**` e `raw/**`. A cadeia de pareamento —
basename único → conteúdo idêntico → cosseno → `unresolved` — nunca inventa
proveniência: ambíguo sem desempate confiável fica `unresolved` e vira braço
humano no reagrupamento (029).
"""

import hashlib
import math
from dataclasses import dataclass
from pathlib import Path

COSINE_FLOOR = 0.75


@dataclass(frozen=True)
class ProposedLink:
    article: Path
    source: Path | None
    book: str | None
    provenance: str  # backfill-basename | backfill-content | backfill-cosine | unresolved
    score: float | None
    candidates: int


def _iter_source_files(data_dir: Path, wiki_dir: Path, raw_dir: Path):
    roots = [Path(data_dir) / "library", Path(wiki_dir) / "_sources", Path(raw_dir)]
    for root in roots:
        if not root.is_dir():
            continue
        for path in root.rglob("*.md"):
            if path.is_symlink() or path.name == "metadata.json":
                continue
            yield path


def _book_of(source: Path, data_dir: Path, wiki_dir: Path) -> str | None:
    """O diretório imediatamente acima do capítulo identifica o livro."""
    library = Path(data_dir) / "library"
    sources = Path(wiki_dir) / "_sources"
    for root in (library, sources):
        try:
            rel = source.relative_to(root)
        except ValueError:
            continue
        return rel.parent.name if len(rel.parts) > 1 else None
    return None


def _normalized_hash(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    normalized = " ".join(text.split()).casefold()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    norm = math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))
    return dot / norm if norm else 0.0


def _body(article: Path) -> str:
    from kb.frontmatter import parse

    _, body = parse(article.read_text(encoding="utf-8", errors="replace"))
    return body


_EMBED_MAX_CHARS = 8000
_TIE_EPSILON = 1e-9


def _resolve_ambiguous(
    article: Path,
    candidates: list[Path],
    embed_fn,
    article_vec: list[float] | None = None,
) -> tuple[Path | None, str, float | None]:
    hashes = {_normalized_hash(c) for c in candidates}
    if len(hashes) == 1:
        return sorted(candidates)[0], "backfill-content", None
    if embed_fn is None:
        return None, "unresolved", None
    # Truncamento no mesmo teto do índice: capítulo gigante não pode derrubar
    # o lote por limite de entrada do servidor de embeddings.
    candidatos_txt = [
        c.read_text(encoding="utf-8", errors="replace")[:_EMBED_MAX_CHARS]
        for c in candidates
    ]
    try:
        if article_vec is not None:
            # O vetor do artigo já existe no índice — só os candidatos embedam,
            # e o score fica comparável ao resto do sistema.
            candidato_vecs = embed_fn(candidatos_txt)
            artigo_vec = article_vec
        else:
            vetores = embed_fn([_body(article)[:_EMBED_MAX_CHARS]] + candidatos_txt)
            artigo_vec, candidato_vecs = vetores[0], vetores[1:]
    except Exception:
        return None, "unresolved", None
    pontuados = sorted(
        zip(candidates, (_cosine(artigo_vec, v) for v in candidato_vecs), strict=True),
        key=lambda item: item[1],
        reverse=True,
    )
    melhor, score = pontuados[0]
    if score < COSINE_FLOOR:
        return None, "unresolved", score
    if len(pontuados) > 1 and abs(score - pontuados[1][1]) <= _TIE_EPSILON:
        # Empate no topo: escolher por ordem de filesystem seria proveniência
        # arbitrária apresentada como fato.
        return None, "unresolved", score
    return melhor, "backfill-cosine", score


def backfill_links(
    wiki_dir: Path,
    data_dir: Path,
    raw_dir: Path,
    embed_fn=None,
    article_vectors: dict[Path, list[float]] | None = None,
) -> list[ProposedLink]:
    """Propõe a ligação artigo→fonte para cada artigo vivo da wiki."""
    from kb.frontmatter import parse

    by_basename: dict[str, list[Path]] = {}
    for source in _iter_source_files(data_dir, wiki_dir, raw_dir):
        by_basename.setdefault(source.name, []).append(source)

    links: list[ProposedLink] = []
    for article in sorted(Path(wiki_dir).rglob("*.md")):
        rel = article.relative_to(wiki_dir)
        if article.is_symlink() or any(part.startswith(("_", ".")) for part in rel.parts):
            continue
        try:
            meta, _ = parse(article.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            continue
        basename = (meta.get("source") or "").strip().strip("'\"")
        candidates = by_basename.get(basename, []) if basename else []
        if not candidates:
            links.append(ProposedLink(article, None, None, "unresolved", None, 0))
            continue
        if len(candidates) == 1:
            fonte = candidates[0]
            links.append(
                ProposedLink(
                    article, fonte, _book_of(fonte, data_dir, wiki_dir),
                    "backfill-basename", None, 1,
                )
            )
            continue
        fonte, provenance, score = _resolve_ambiguous(
            article,
            candidates,
            embed_fn,
            article_vec=(article_vectors or {}).get(article),
        )
        book = _book_of(fonte, data_dir, wiki_dir) if fonte else None
        links.append(ProposedLink(article, fonte, book, provenance, score, len(candidates)))
    return links
