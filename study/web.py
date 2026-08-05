"""Aplicação FastAPI do leitor, separada da engine por HTTP local."""

import os
import sqlite3
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qs

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from kb.guardrails import SensitiveContentError
from kb.security import loopback_only_middleware, reject_cross_origin_writes_middleware
from study.cards import (
    accept_card,
    cards_for_article,
    discard_card,
    edit_card,
    generate_cards,
    get_card,
)
from study.highlights import (
    active_highlights,
    create_highlight,
    orphan_article,
    orphaned_highlights,
)
from study.notes import delete_note, get_note, save_note
from study.render import plain_text, render_markdown
from study.review import due_card, review_card, review_queue
from study.sources import buscar_fontes

_ROOT = Path(__file__).parent
templates = Jinja2Templates(directory=_ROOT / "templates")


def data_amigavel(valor: str) -> str:
    """Formata um ISO-8601 para leitura humana, preservando o que não for data."""
    if not valor:
        return ""
    try:
        momento = datetime.fromisoformat(valor)
    except ValueError:
        return valor
    return momento.astimezone().strftime("%d/%m/%Y às %H:%M")


templates.env.filters["data_amigavel"] = data_amigavel
app = FastAPI(title="study local reader")
app.mount("/static", StaticFiles(directory=_ROOT / "static"), name="static")
app.middleware("http")(reject_cross_origin_writes_middleware)
app.middleware("http")(loopback_only_middleware)


def api_request(method: str, path: str, **kwargs) -> dict:
    """Consulta a API local da engine sem importar módulos do kb."""
    base_url = os.getenv("KB_API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
    try:
        with httpx.Client(base_url=base_url, timeout=15.0, trust_env=False) as client:
            response = client.request(method, path, **kwargs)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        detail = exc.response.json().get("detail", "A API da knowledge base recusou a solicitação.")
        raise HTTPException(status_code=exc.response.status_code, detail=detail) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=503,
            detail="A API da knowledge base não está disponível.",
        ) from exc


def _render(request: Request, template_name: str, **context):
    return templates.TemplateResponse(request, template_name, context)


async def _form_value(request: Request, name: str) -> str:
    values = parse_qs((await request.body()).decode("utf-8"), keep_blank_values=True)
    return values.get(name, [""])[0]


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    """Exibe busca e os artigos mais recentes do corpus."""
    articles = api_request("GET", "/articles", params={"limit": 12})
    return _render(
        request,
        "home.html",
        articles=articles["results"],
        orphaned_highlights=orphaned_highlights(),
    )


@app.get("/a/{slug:path}", response_class=HTMLResponse)
def article(request: Request, slug: str):
    """Exibe um artigo e a trilha formada pelo tópico atual."""
    try:
        data = api_request("GET", f"/article/{slug}")
    except HTTPException as exc:
        if exc.status_code == 404:
            orphan_article(slug)
        raise
    sidebar = api_request("GET", "/articles", params={"topic": data["topic"]})
    highlights = active_highlights(slug, plain_text(data["content"], data["wikilinks"]))
    return _render(
        request,
        "article.html",
        article=data,
        article_html=render_markdown(data["content"], data["wikilinks"], highlights),
        sidebar=sidebar["results"],
        note=get_note(slug),
        cards=cards_for_article(slug),
        orphaned_highlights=orphaned_highlights(slug),
    )


@app.post("/buscar", response_class=HTMLResponse)
async def search(request: Request):
    """Renderiza a busca da engine como fragmento htmx."""
    query = (await _form_value(request, "q")).strip()
    results = {"results": []} if not query else await run_in_threadpool(
        api_request, "GET", "/search", params={"q": query, "top_k": 10}
    )
    return _render(request, "partials/search_results.html", query=query, results=results["results"])


@app.post("/perguntar", response_class=HTMLResponse)
async def ask(request: Request):
    """Renderiza a resposta e toda a informação de grounding da engine."""
    question = (await _form_value(request, "question")).strip()
    answer = {"answer": "", "grounding": {"claims": []}} if not question else await run_in_threadpool(
        api_request, "POST", "/qa", json={"question": question}
    )
    return _render(request, "partials/answer.html", answer=answer)


@app.post("/a/{slug:path}/note", response_class=HTMLResponse)
async def save_article_note(request: Request, slug: str):
    """Salva a nota do artigo e devolve o painel atualizado."""
    note = save_note(slug, await _form_value(request, "body"))
    return _render(request, "partials/note.html", slug=slug, note=note)


@app.delete("/a/{slug:path}/note", response_class=HTMLResponse)
def remove_article_note(request: Request, slug: str):
    """Remove a nota do artigo e devolve o painel vazio."""
    delete_note(slug)
    return _render(request, "partials/note.html", slug=slug, note=None)


@app.post("/a/{slug:path}/highlights", response_class=HTMLResponse)
async def save_article_highlight(request: Request, slug: str):
    """Salva um destaque textual selecionado no leitor."""
    quote = (await _form_value(request, "quote")).strip()
    if not quote:
        raise HTTPException(status_code=400, detail="Selecione um trecho para destacar.")
    create_highlight(
        slug,
        quote,
        await _form_value(request, "prefix"),
        await _form_value(request, "suffix"),
        await _form_value(request, "note"),
    )
    return _render(request, "partials/highlight_feedback.html")


@app.get("/fontes", response_class=HTMLResponse)
def sources(request: Request, termo: str = ""):
    """Exibe fontes locais encontradas para um wikilink sem artigo."""
    return _render(request, "partials/sources.html", sources=buscar_fontes(termo))


@app.post("/a/{slug:path}/cards/generate", response_class=HTMLResponse)
def generate_article_cards(request: Request, slug: str):
    """Gera cartões candidatos e mostra o grounding antes de qualquer aceitação."""
    article = api_request("GET", f"/article/{slug}")
    try:
        generate_cards(slug, article["content"])
    except SensitiveContentError as exc:
        raise HTTPException(status_code=409, detail="Conteúdo sensível requer autorização.") from exc
    # O painel inteiro é substituído: mostrar só o lote novo fazia os cartões já
    # curados sumirem da tela até o próximo reload.
    return _render(request, "partials/cards.html", slug=slug, cards=cards_for_article(slug))


@app.post("/cards/{card_id}/accept", response_class=HTMLResponse)
def accept_article_card(request: Request, card_id: int):
    """Aceita um candidato somente quando a verificação o ancorou."""
    try:
        card = accept_card(card_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return _render(
        request,
        "partials/cards.html",
        slug=card["slug"],
        cards=cards_for_article(card["slug"]),
        conquista="Card ancorado aceito — entrou na revisão",
    )


@app.post("/cards/{card_id}/edit", response_class=HTMLResponse)
async def edit_article_card(request: Request, card_id: int):
    """Edita e verifica de novo um cartão antes de deixá-lo em curadoria."""
    card = get_card(card_id)
    if card is None:
        raise HTTPException(status_code=404, detail="Cartão não encontrado.")
    article = await run_in_threadpool(api_request, "GET", f"/article/{card['slug']}")
    try:
        updated = edit_card(
            card_id,
            (await _form_value(request, "front")).strip(),
            (await _form_value(request, "back")).strip(),
            article["content"],
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return _render(
        request,
        "partials/cards.html",
        slug=updated["slug"],
        cards=cards_for_article(updated["slug"]),
    )


@app.post("/cards/{card_id}/discard", response_class=HTMLResponse)
def discard_article_card(request: Request, card_id: int):
    """Descarta um cartão da curadoria sem tocar no artigo compilado."""
    try:
        card = discard_card(card_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return _render(
        request,
        "partials/cards.html",
        slug=card["slug"],
        cards=cards_for_article(card["slug"]),
    )


@app.get("/revisar", response_class=HTMLResponse)
def review(request: Request):
    """Mostra o próximo cartão devido e a agenda derivada pelo FSRS."""
    return _render(request, "review.html", card=due_card(), queue=review_queue())


@app.post("/revisar/{card_id}", response_class=HTMLResponse)
async def submit_review(request: Request, card_id: int):
    """Registra um dos quatro ratings FSRS e recalcula a data devida."""
    try:
        review_card(card_id, int(await _form_value(request, "rating")))
    except (TypeError, ValueError, sqlite3.IntegrityError) as exc:
        raise HTTPException(status_code=400, detail="Rating de revisão inválido.") from exc
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    # O htmx troca `#review-body` por `outerHTML`: devolver a página inteira
    # aninhava um documento dentro do painel.
    return _render(request, "partials/review_body.html", card=due_card(), queue=review_queue())
