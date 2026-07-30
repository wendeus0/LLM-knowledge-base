"""RED — `--rerank` tem de existir em `kb search`.

`search()` aceita `rerank_depth` desde a 021, e o bench mediu +42% de MRR com
ele (0,242 → 0,343). Mas só o bench chamava a função com o parâmetro: a CLI
nunca expôs a flag, então o ganho não alcançava nenhum comando de produção.

O instrumento media um caminho que o usuário não conseguia acionar.
"""

from typer.testing import CliRunner

from kb.cli import app

runner = CliRunner()


class TestSearchRerankFlag:
    def test_should_accept_rerank_flag(self, monkeypatch):
        monkeypatch.setattr("kb.search.search", lambda *a, **k: [])

        result = runner.invoke(app, ["search", "grafos", "--rerank", "20"])

        assert "No such option" not in result.output

    def test_should_forward_depth_to_search(self, monkeypatch):
        recebido = {}

        def fake_search(query, **kwargs):
            recebido.update(kwargs)
            return []

        monkeypatch.setattr("kb.search.search", fake_search)

        runner.invoke(app, ["search", "grafos", "--rerank", "20"])

        assert recebido.get("rerank_depth") == 20

    def test_should_default_to_no_rerank(self, monkeypatch):
        recebido = {}

        def fake_search(query, **kwargs):
            recebido.update(kwargs)
            return []

        monkeypatch.setattr("kb.search.search", fake_search)

        runner.invoke(app, ["search", "grafos"])

        assert not recebido.get("rerank_depth")
