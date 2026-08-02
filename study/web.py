"""Aplicação FastAPI do leitor, separada da engine por HTTP local."""

import os
from pathlib import Path
from urllib.parse import parse_qs

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from study.render import render_markdown
from study.sources import buscar_fontes

_ROOT = Path(__file__).parent
templates = Jinja2Templates(directory=_ROOT / "templates")
app = FastAPI(title="study local reader")
app.mount("/static", StaticFiles(directory=_ROOT / "static"), name="static")


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
    return _render(request, "home.html", articles=articles["results"])


@app.get("/a/{slug:path}", response_class=HTMLResponse)
def article(request: Request, slug: str):
    """Exibe um artigo e a trilha formada pelo tópico atual."""
    data = api_request("GET", f"/article/{slug}")
    sidebar = api_request("GET", "/articles", params={"topic": data["topic"]})
    return _render(
        request,
        "article.html",
        article=data,
        article_html=render_markdown(data["content"], data["wikilinks"]),
        sidebar=sidebar["results"],
    )


@app.post("/buscar", response_class=HTMLResponse)
async def search(request: Request):
    """Renderiza a busca da engine como fragmento htmx."""
    query = (await _form_value(request, "q")).strip()
    results = {"results": []} if not query else api_request(
        "GET", "/search", params={"q": query, "top_k": 10}
    )
    return _render(request, "partials/search_results.html", query=query, results=results["results"])


@app.post("/perguntar", response_class=HTMLResponse)
async def ask(request: Request):
    """Renderiza a resposta e toda a informação de grounding da engine."""
    question = (await _form_value(request, "question")).strip()
    answer = {"answer": "", "grounding": {"claims": []}} if not question else api_request(
        "POST", "/qa", json={"question": question}
    )
    return _render(request, "partials/answer.html", answer=answer)


@app.get("/fontes", response_class=HTMLResponse)
def sources(request: Request, termo: str = ""):
    """Exibe fontes locais encontradas para um wikilink sem artigo."""
    return _render(request, "partials/sources.html", sources=buscar_fontes(termo))
