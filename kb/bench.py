"""Medição de retrieval contra golden set (feature 016-bench-golden-set).

O cálculo das métricas é puro e isolado do I/O: é a parte de que as decisões
de retrieval dependem, e ela não pode variar com disco ou servidor.

recall@k = proporção de casos válidos em que ao menos um artigo esperado
aparece no top-k. MRR usa o inverso da posição do primeiro acerto dentro do
corte (acerto fora do corte contribui zero, como em recall@k).
"""

import json
import random
import re
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
    source: str = "curated"


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


def aggregate_by_source(results: list[CaseResult], k: int = 5) -> dict:
    """Métricas separadas por população — casos curados e gerados medem coisas diferentes."""
    populations: dict[str, list[CaseResult]] = {}
    for result in results:
        populations.setdefault(result.source, []).append(result)
    return {source: aggregate(items, k=k) for source, items in populations.items()}


def _normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9 ]", " ", text.lower())


def is_trivial_question(title: str, question: str) -> bool:
    """Pergunta que repete o título mede casamento de string, não recuperação.

    Foi o defeito do seed original: recall de 0,860 que virou 0,420 quando as
    perguntas passaram a ser conceituais.
    """
    normalized_title = " ".join(_normalize(title).split())
    normalized_question = " ".join(_normalize(question).split())
    if not normalized_title:
        return False
    if normalized_title in normalized_question:
        return True

    title_words = {w for w in normalized_title.split() if len(w) > 3}
    if not title_words:
        return False
    question_words = set(normalized_question.split())
    return len(title_words & question_words) / len(title_words) >= 0.8


def sample_articles(
    pool: list[str], n: int, seed: int = 42, exclude: set[str] | None = None
) -> list[str]:
    """Amostra reprodutível, pulando o que já está coberto."""
    candidates = [item for item in pool if item not in (exclude or set())]
    rng = random.Random(seed)
    return rng.sample(candidates, min(n, len(candidates)))


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


_QUESTION_PROMPT = (
    "Você consulta uma base de conhecimento técnica em português. Leia o trecho de "
    "artigo e escreva UMA pergunta que levaria alguém a procurar por ele.\n"
    "Regras: use linguagem coloquial de quem NÃO conhece o jargão da área; NÃO use "
    "as palavras do título; descreva o problema ou a situação, não o conceito pelo "
    "nome. Máximo 15 palavras. Responda só a pergunta, sem aspas."
)


def generate_cases(
    wiki_dir: Path,
    n: int,
    seed: int = 42,
    existing: set[str] | None = None,
    on_case=None,
) -> list[dict]:
    """Um caso por artigo amostrado, com a pergunta escrita pelo LLM.

    Casos triviais (pergunta que repete o título) são descartados — foi o que
    inflou a medição do seed original.
    """
    from kb.client import chat
    from kb.embeddings import _iter_articles
    from kb.frontmatter import parse
    from kb.sampling import params

    articles = {Path(rel).stem: (rel, text) for rel, text in _iter_articles(wiki_dir)}
    chosen = sample_articles(sorted(articles), n, seed=seed, exclude=existing or set())

    cases: list[dict] = []
    for slug in chosen:
        _, text = articles[slug]
        meta, body = parse(text)
        title = str(meta.get("title") or slug.replace("-", " ")).strip()

        try:
            question = chat(
                messages=[
                    {"role": "system", "content": _QUESTION_PROMPT},
                    {"role": "user", "content": f"Título: {title}\n\n{body[:1500]}"},
                ],
                # Casos de avaliação precisam variar: aqui a diversidade é o objetivo.
                **params("diverse"),
            )
        except Exception:
            continue

        question = (question or "").strip().strip('"').splitlines()[0] if question else ""
        if not question or is_trivial_question(title, question):
            continue

        case = {"question": question, "expected": [slug], "source": "generated"}
        cases.append(case)
        if on_case:
            on_case(case)

    return cases


def write_golden(path: Path, cases: list[dict]) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"cases": cases}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def run_bench(
    mode: str = "hybrid",
    k: int = 5,
    expand: str | None = None,
    rerank_depth: int | None = None,
) -> dict | None:
    """Executa o golden set e devolve sumário + casos. None se não há golden set."""
    from kb.config import STATE_DIR, WIKI_DIR
    from kb.embeddings import _iter_articles
    from kb.search import search

    cases = load_golden(golden_path(STATE_DIR))
    if cases is None:
        return None

    known = {Path(relpath).stem for relpath, _ in _iter_articles(WIKI_DIR)}
    depth = max(k, 10)

    if rerank_depth:
        from kb.rerank import preflight, reset_stats

        preflight()
        reset_stats()

    semantic_active = False
    if mode == "hybrid":
        from kb.embeddings import load_index

        semantic_active = load_index(STATE_DIR) is not None

    results = []
    for case in cases:
        ranked = [
            Path(item["path"]).stem
            for item in search(
                case["question"],
                top_k=depth,
                mode=mode,
                expand=expand,
                rerank_depth=rerank_depth,
            )
        ]
        result = evaluate_case(
            ranked,
            case.get("expected", []),
            k=k,
            known_slugs=known,
            question=case.get("question", ""),
        )
        result.source = case.get("source", "curated")
        results.append(result)

    return {
        "mode": mode,
        "expand": expand,
        "corpus": len(known),
        "semantic_active": semantic_active,
        "summary": aggregate(results, k=k),
        "by_source": aggregate_by_source(results, k=k),
        "rerank_stats": _rerank_stats() if rerank_depth else None,
        "results": results,
    }


def _rerank_stats() -> dict:
    from kb.rerank import stats

    return stats()
