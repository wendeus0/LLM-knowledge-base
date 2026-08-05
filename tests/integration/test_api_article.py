"""Contrato HTTP de leitura segura de artigos."""

from pathlib import Path


def test_should_return_article_by_rel_slug_without_path_serialization(tmp_wiki, api_client):
    article = tmp_wiki / "ai" / "transformers.md"
    article.write_text(
        "---\ntitle: Transformers\ntopic: ai\ntags: [llm, attention]\nsource: raw/a.md\n---\n# Transformers\n\nConteúdo.\n",
        encoding="utf-8",
    )

    response = api_client.get("/article/ai/transformers")

    assert response.status_code == 200
    assert response.json() == {
        "slug": "ai/transformers",
        "title": "Transformers",
        "topic": "ai",
        "tags": ["llm", "attention"],
        "source": "raw/a.md",
        "content": "# Transformers\n\nConteúdo.\n",
        "wikilinks": [],
        "backlinks": [],
    }


def test_should_reject_traversal_before_reading_outside_wiki(tmp_wiki, api_client):
    outside = tmp_wiki.parent / "secret.md"
    outside.write_text("segredo", encoding="utf-8")

    response = api_client.get("/article/%2E%2E/secret")

    assert response.status_code == 400
    assert "secret" not in response.text


def test_should_not_expose_paths_for_missing_valid_article(tmp_wiki, api_client):
    response = api_client.get("/article/ai/missing")

    assert response.status_code == 404
    assert str(tmp_wiki) not in response.text


def test_should_serve_an_article_whose_slug_contains_a_dot(tmp_wiki, api_client):
    (tmp_wiki / "ai" / "gpt-4.5.md").write_text(
        "---\ntitle: GPT-4.5\ntopic: ai\n---\nConteúdo.\n", encoding="utf-8"
    )

    response = api_client.get("/article/ai/gpt-4.5")

    assert response.status_code == 200
    assert response.json()["slug"] == "ai/gpt-4.5"
    assert response.json()["title"] == "GPT-4.5"


def test_should_reflect_a_new_backlink_without_restarting_the_process(tmp_wiki, api_client):
    (tmp_wiki / "ai" / "transformers.md").write_text(
        "---\ntitle: Transformers\ntopic: ai\n---\nConteúdo.\n", encoding="utf-8"
    )
    client = api_client

    antes = client.get("/article/ai/transformers").json()["backlinks"]
    (tmp_wiki / "ai" / "attention.md").write_text(
        "---\ntitle: Attention\ntopic: ai\n---\nVeja [[ai/transformers]].\n", encoding="utf-8"
    )
    depois = client.get("/article/ai/transformers").json()["backlinks"]

    assert antes == []
    assert depois == ["ai/attention"]


def test_should_serve_the_article_when_a_file_vanishes_while_the_corpus_is_scanned(
    tmp_wiki, monkeypatch, api_client
):
    """`compile`/`heal` mexem no corpus em paralelo: um arquivo que some entre o
    rglob e o stat não pode derrubar a requisição."""
    (tmp_wiki / "ai" / "transformers.md").write_text(
        "---\ntitle: Transformers\ntopic: ai\n---\nVeja [[ai/efemero]].\n", encoding="utf-8"
    )
    original_rglob = Path.rglob

    def _rglob_com_arquivo_ja_apagado(self, pattern, *args, **kwargs):
        # A varredura entrega um caminho que o `compile` apagou logo em seguida:
        # o `stat` da assinatura e o `read_text` do índice batem num arquivo que
        # não existe mais, com a semântica real do sistema de arquivos.
        yield from original_rglob(self, pattern, *args, **kwargs)
        yield self / "ai" / "efemero.md"

    monkeypatch.setattr(Path, "rglob", _rglob_com_arquivo_ja_apagado)

    response = api_client.get("/article/ai/transformers")

    assert response.status_code == 200
    assert response.json()["slug"] == "ai/transformers"


def test_should_not_reread_the_corpus_on_every_article_request(tmp_wiki, monkeypatch, api_client):
    for indice in range(12):
        (tmp_wiki / "ai" / f"artigo-{indice}.md").write_text(
            f"---\ntitle: Artigo {indice}\ntopic: ai\n---\nVeja [[ai/artigo-0]].\n", encoding="utf-8"
        )
    client = api_client
    client.get("/article/ai/artigo-0")

    leituras = []
    original = Path.read_text
    monkeypatch.setattr(
        Path, "read_text", lambda self, *args, **kwargs: (leituras.append(self), original(self, *args, **kwargs))[1]
    )
    client.get("/article/ai/artigo-1")

    assert len(leituras) == 1
