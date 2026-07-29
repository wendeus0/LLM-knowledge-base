"""Medição de retrieval contra golden set (feature 016-bench-golden-set).

O cálculo das métricas é puro e isolado do I/O: é a parte de que as decisões
de retrieval dependem, e ela não pode variar com disco ou servidor.

recall@k = proporção de casos válidos em que ao menos um artigo esperado
aparece no top-k. MRR usa o inverso da posição do primeiro acerto dentro do
corte (acerto fora do corte contribui zero, como em recall@k).
"""

import json
from dataclasses import dataclass, field
from pathlib import Path

GOLDEN_RELPATH = Path("bench") / "golden.json"


@dataclass
class CaseResult:
    question: str = ""
    expected: list[str] = field(default_factory=list)
    rank: int | None = None
    hit_at_k: bool = False
    invalid: bool = False


def evaluate_case(
    ranked_slugs: list[str],
    expected: list[str],
    k: int = 5,
    known_slugs: set[str] | None = None,
    question: str = "",
) -> CaseResult:
    """Posição do primeiro esperado no ranking; caso inválido não é falha de busca."""
    invalid = known_slugs is not None and not any(
        slug in known_slugs for slug in expected
    )

    rank = None
    for position, slug in enumerate(ranked_slugs, start=1):
        if slug in expected:
            rank = position
            break

    return CaseResult(
        question=question,
        expected=list(expected),
        rank=rank,
        hit_at_k=bool(not invalid and rank is not None and rank <= k),
        invalid=invalid,
    )


def aggregate(results: list[CaseResult], k: int = 5) -> dict:
    valid = [result for result in results if not result.invalid]
    total = len(valid)
    hits = sum(1 for result in valid if result.hit_at_k)
    reciprocal = sum(1.0 / result.rank for result in valid if result.hit_at_k and result.rank)

    return {
        "k": k,
        "total": total,
        "hits": hits,
        "invalid": len(results) - total,
        "recall_at_k": hits / total if total else 0.0,
        "mrr": reciprocal / total if total else 0.0,
    }


def golden_path(state_dir: Path) -> Path:
    return Path(state_dir) / GOLDEN_RELPATH


def load_golden(path: Path) -> list[dict] | None:
    path = Path(path)
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"golden set inválido em {path}: {exc}") from exc
    return payload.get("cases", [])


def seed_golden(wiki_dir: Path, limit: int | None = None) -> list[dict]:
    """Casos título→artigo: piso determinístico, sem LLM, para o operador curar."""
    from kb.embeddings import _iter_articles
    from kb.frontmatter import parse

    cases: list[dict] = []
    for relpath, text in _iter_articles(wiki_dir):
        slug = Path(relpath).stem
        meta, _ = parse(text)
        question = str(meta.get("title") or slug.replace("-", " ")).strip()
        cases.append({"question": question, "expected": [slug]})
        if limit and len(cases) >= limit:
            break
    return cases


def write_golden(path: Path, cases: list[dict]) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"cases": cases}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def run_bench(mode: str = "hybrid", k: int = 5) -> dict | None:
    """Executa o golden set e devolve sumário + casos. None se não há golden set."""
    from kb.config import STATE_DIR, WIKI_DIR
    from kb.embeddings import _iter_articles
    from kb.search import search

    cases = load_golden(golden_path(STATE_DIR))
    if cases is None:
        return None

    known = {Path(relpath).stem for relpath, _ in _iter_articles(WIKI_DIR)}
    depth = max(k, 10)

    semantic_active = False
    if mode == "hybrid":
        from kb.embeddings import load_index

        semantic_active = load_index(STATE_DIR) is not None

    results = []
    for case in cases:
        ranked = [
            Path(item["path"]).stem
            for item in search(case["question"], top_k=depth, mode=mode)
        ]
        results.append(
            evaluate_case(
                ranked,
                case.get("expected", []),
                k=k,
                known_slugs=known,
                question=case.get("question", ""),
            )
        )

    return {
        "mode": mode,
        "corpus": len(known),
        "semantic_active": semantic_active,
        "summary": aggregate(results, k=k),
        "results": results,
    }
