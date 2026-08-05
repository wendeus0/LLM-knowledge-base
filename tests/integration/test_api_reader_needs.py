"""O que o leitor (F2) precisa da API e os testes da F1 não cobriram.

RF-06 exige navegar por wikilink; RF-02 identifica resultado por `rel_slug`, mas
uma lista de slugs não é apresentável — a tela mostra título.
"""

def _vault(tmp_path, monkeypatch):
    wiki = tmp_path / "wiki"
    (wiki / "cybersecurity").mkdir(parents=True)
    (wiki / "ai").mkdir(parents=True)
    (wiki / "cybersecurity" / "dorks.md").write_text(
        "---\ntitle: Google Dorks\ntopic: cybersecurity\ntags: [osint]\n---\n"
        "Veja [[OSINT]] e [[honeycomb]] e [[cybersecurity/honeycomb]].\n",
        encoding="utf-8",
    )
    (wiki / "ai" / "osint.md").write_text("---\ntitle: OSINT\ntopic: ai\n---\ntexto\n", encoding="utf-8")
    (wiki / "honeycomb.md").write_text("---\ntitle: Honeycomb raiz\n---\ntexto\n", encoding="utf-8")
    (wiki / "cybersecurity" / "honeycomb.md").write_text(
        "---\ntitle: Honeycomb seg\n---\ntexto\n", encoding="utf-8"
    )
    monkeypatch.setattr("kb.config.WIKI_DIR", wiki)
    monkeypatch.setattr("kb.search.WIKI_DIR", wiki)
    return wiki


class TestArticleExpoeWikilinks:
    def test_should_expose_wikilinks_so_the_reader_can_navigate(self, tmp_path, monkeypatch, api_client):
        _vault(tmp_path, monkeypatch)

        corpo = api_client.get("/article/cybersecurity/dorks").json()

        assert "wikilinks" in corpo
        assert [w["text"] for w in corpo["wikilinks"]] == [
            "OSINT",
            "honeycomb",
            "cybersecurity/honeycomb",
        ]

    def test_should_resolve_each_wikilink_to_a_slug(self, tmp_path, monkeypatch, api_client):
        _vault(tmp_path, monkeypatch)

        corpo = api_client.get("/article/cybersecurity/dorks").json()
        por_texto = {w["text"]: w for w in corpo["wikilinks"]}

        assert por_texto["OSINT"]["targets"] == ["ai/osint"]

    def test_should_flag_an_ambiguous_wikilink(self, tmp_path, monkeypatch, api_client):
        _vault(tmp_path, monkeypatch)

        por_texto = {
            w["text"]: w for w in api_client.get("/article/cybersecurity/dorks").json()["wikilinks"]
        }

        assert por_texto["honeycomb"]["ambiguous"] is True
        assert len(por_texto["honeycomb"]["targets"]) == 2
        assert por_texto["cybersecurity/honeycomb"]["ambiguous"] is False

    def test_should_report_a_wikilink_without_article_as_unresolved(self, tmp_path, monkeypatch, api_client):
        wiki = _vault(tmp_path, monkeypatch)
        (wiki / "cybersecurity" / "dorks.md").write_text(
            "---\ntitle: D\n---\nVeja [[nao-existe]].\n", encoding="utf-8"
        )

        alvo = api_client.get("/article/cybersecurity/dorks").json()["wikilinks"][0]

        assert alvo["targets"] == []
        assert alvo["ambiguous"] is False


class TestSearchApresentavel:
    def test_should_return_a_title_for_each_result(self, tmp_path, monkeypatch, api_client):
        _vault(tmp_path, monkeypatch)

        resultados = api_client.get("/search", params={"q": "dorks", "top_k": 3}).json()["results"]

        assert resultados
        assert all(r.get("title") for r in resultados)

    def test_should_return_the_topic_for_each_result(self, tmp_path, monkeypatch, api_client):
        _vault(tmp_path, monkeypatch)

        resultados = api_client.get("/search", params={"q": "dorks", "top_k": 3}).json()["results"]

        assert all(r.get("topic") for r in resultados)
