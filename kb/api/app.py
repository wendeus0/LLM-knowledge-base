"""API FastAPI local; execute apenas com host de loopback (127.0.0.1)."""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse

from kb import config, search, stats
from kb.api import articles
from kb.api.articles import InvalidArticleSlug, get_article
from kb.api.schemas import (
    ArticleResponse,
    HealthResponse,
    QaRequest,
    QaResponse,
    SearchResponse,
)
from kb.guardrails import SensitiveContentError

app = FastAPI(title="kb local API")


@app.exception_handler(SensitiveContentError)
def _sensitive_content_error(_request, _exc):
    return JSONResponse(
        status_code=409,
        content={"detail": "Conteúdo sensível bloqueado para processamento externo."},
    )


@app.get("/health", response_model=HealthResponse)
def health():
    """Informa a disponibilidade da aplicação."""
    return {"status": "ok"}


@app.get("/search", response_model=SearchResponse)
def search_articles(
    q: str = Query(min_length=1),
    top_k: int = Query(default=10, ge=1),
    rerank_depth: int | None = Query(default=None, ge=2),
):
    """Consulta a busca híbrida existente."""
    results = search.search(q, top_k=top_k, rerank_depth=rerank_depth)
    return {
        "results": [
            {
                **articles.article_summary(item["path"], config.WIKI_DIR),
                "slug": search.rel_slug(item["path"], config.WIKI_DIR),
                "score": item["score"],
                "snippet": item.get("snippet", ""),
            }
            for item in results
        ]
    }


@app.post("/qa", response_model=QaResponse)
def ask_question(request: QaRequest):
    """Responde com o contrato JSON do comando qa."""
    from kb.qa import answer_with_grounding

    result = answer_with_grounding(request.question)
    grounding = result.grounding
    return {
        "answer": result.answer,
        "grounding": {
            "status": grounding.status,
            "checked_claims": grounding.checked_claims,
            "unverified_due_to_limit": grounding.unverified_due_to_limit,
            "claims": [
                {
                    "claim": claim.claim,
                    "verdict": claim.verdict,
                    "evidence": claim.evidence,
                    "scores": claim.scores,
                }
                for claim in grounding.claims
            ],
        },
        "saved_path": None,
    }


@app.get("/article/{slug:path}", response_model=ArticleResponse)
def article(slug: str):
    """Lê artigo permitido identificado pelo rel_slug."""
    try:
        result = get_article(slug)
    except InvalidArticleSlug as exc:
        raise HTTPException(status_code=400, detail="Slug de artigo inválido.") from exc
    if result is None:
        raise HTTPException(status_code=404, detail="Artigo não encontrado.")
    return result


@app.get("/stats")
def get_stats():
    """Retorna métricas agregadas da engine."""
    return stats.collect_stats()
