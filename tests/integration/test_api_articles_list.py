"""Listagem de artigos — o leitor precisa dela para a home e para a sidebar.

Descoberto ao implementar a F2: `/search` exige `q` e `/stats` só dá métricas,
então não havia como montar "últimos artigos" nem "artigos deste topic" sem
furar a fronteira HTTP do ADR-0019.
"""

from fastapi.testclient import TestClient

from kb.api.app import app


def _client():
    return TestClient(app)


def _vault(tmp_path, monkeypatch):
    wiki = tmp_path / "wiki"
    (wiki / "cybersecurity").mkdir(parents=True)
    (wiki / "ai").mkdir(parents=True)
    (wiki / "_summaries").mkdir(parents=True)
    (wiki / "cybersecurity" / "dorks.md").write_text(
        "---\ntitle: Google Dorks\ntopic: cybersecurity\n---\ntexto\n", encoding="utf-8"
    )
    (wiki / "cybersecurity" / "xss.md").write_text(
        "---\ntitle: XSS\ntopic: cybersecurity\n---\ntexto\n", encoding="utf-8"
    )
    (wiki / "ai" / "osint.md").write_text(
        "---\ntitle: OSINT\ntopic: ai\n---\ntexto\n", encoding="utf-8"
    )
    (wiki / "_summaries" / "resumo.md").write_text("derivado\n", encoding="utf-8")
    (wiki / "_index.md").write_text("indice\n", encoding="utf-8")
    monkeypatch.setattr("kb.config.WIKI_DIR", wiki)
    monkeypatch.setattr("kb.search.WIKI_DIR", wiki)
    import kb.api.articles as mod

    mod._build_index.cache_clear()
    return wiki


def test_should_list_articles_with_slug_title_and_topic(tmp_path, monkeypatch):
    _vault(tmp_path, monkeypatch)

    corpo = _client().get("/articles").json()

    assert {a["slug"] for a in corpo["results"]} == {
        "cybersecurity/dorks",
        "cybersecurity/xss",
        "ai/osint",
    }
    assert all(a["title"] and a["topic"] for a in corpo["results"])


def test_should_exclude_derived_files_from_the_listing(tmp_path, monkeypatch):
    _vault(tmp_path, monkeypatch)

    slugs = {a["slug"] for a in _client().get("/articles").json()["results"]}

    assert not any(s.startswith("_") for s in slugs)


def test_should_filter_by_topic_for_the_sidebar(tmp_path, monkeypatch):
    _vault(tmp_path, monkeypatch)

    corpo = _client().get("/articles", params={"topic": "cybersecurity"}).json()

    assert {a["slug"] for a in corpo["results"]} == {"cybersecurity/dorks", "cybersecurity/xss"}


def test_should_honour_the_limit(tmp_path, monkeypatch):
    _vault(tmp_path, monkeypatch)

    assert len(_client().get("/articles", params={"limit": 2}).json()["results"]) == 2


def test_should_sort_by_recency_by_default(tmp_path, monkeypatch):
    wiki = _vault(tmp_path, monkeypatch)
    import os

    antigo = wiki / "ai" / "osint.md"
    os.utime(antigo, (1_000_000, 1_000_000))

    slugs = [a["slug"] for a in _client().get("/articles").json()["results"]]

    assert slugs[-1] == "ai/osint"


def test_should_sort_by_title_when_asked(tmp_path, monkeypatch):
    _vault(tmp_path, monkeypatch)

    titulos = [a["title"] for a in _client().get("/articles", params={"sort": "title"}).json()["results"]]

    assert titulos == sorted(titulos)


def test_should_reject_an_unknown_sort(tmp_path, monkeypatch):
    _vault(tmp_path, monkeypatch)

    assert _client().get("/articles", params={"sort": "aleatorio"}).status_code == 422
