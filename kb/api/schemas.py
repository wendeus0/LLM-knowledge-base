"""Schemas serializáveis da API HTTP."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


class SearchResult(BaseModel):
    slug: str
    title: str
    topic: str
    score: float
    snippet: str


class SearchResponse(BaseModel):
    results: list[SearchResult]


class QaRequest(BaseModel):
    question: str


class GroundingClaim(BaseModel):
    claim: str
    verdict: str
    evidence: str
    scores: dict


class GroundingResponse(BaseModel):
    status: str
    checked_claims: int
    unverified_due_to_limit: int
    claims: list[GroundingClaim]


class QaResponse(BaseModel):
    answer: str
    grounding: GroundingResponse
    saved_path: None = None


class Wikilink(BaseModel):
    text: str
    targets: list[str]
    ambiguous: bool


class ArticleResponse(BaseModel):
    slug: str
    title: str
    topic: str
    tags: list[str]
    source: str | None = None
    content: str
    wikilinks: list[Wikilink]
    backlinks: list[str]
