"""RED — a busca sobre índice lexical tem de devolver exatamente o mesmo ranking.

O índice só troca a origem das frequências de termo (arquivo de estado em vez
de releitura da wiki). Ordem, scores e snippets ficam idênticos; sem índice o
comportamento é o de sempre; e nada é gravado fora do STATE_DIR isolado.
"""

import pytest

from kb.lexical_index import INDEX_FILENAME, build_index
from kb.search import _build_rankings, search

QUERIES = [
    "xss",
    "sql injection",
    "vulnerabilidade web",
    "python decorators",
    "cache redis",
    "autenticação",
    "modelo de ameaças",
    "injeção de sql em query",
    "redes neurais",
    "typescript generics",
    "termo inexistente 12345",
]


@pytest.fixture
def corpus(tmp_wiki):
    articles = {
        "cybersecurity/xss.md": "# XSS\n\nXSS é uma vulnerabilidade web comum.\n\n## Prevenção\n\nSanitizar entrada.\n",
        "cybersecurity/sqli.md": "# SQL Injection\n\nInjeção de SQL em query dinâmica é uma vulnerabilidade.\n",
        "cybersecurity/auth.md": "# Auth\n\nAutenticação e autorização em aplicações web.\n",
        "cybersecurity/threat-model.md": "# Threat Model\n\nModelo de ameaças descreve o atacante.\n",
        "python/decorators.md": "# Decorators\n\nPython decorators embrulham funções.\n",
        "python/cache.md": "# Cache\n\n" + ("texto " * 200) + "cache redis em python.\n",
        "ai/neural.md": "# Redes Neurais\n\nRedes neurais aprendem representações.\n",
        "typescript/generics.md": "# Generics\n\nTypescript generics parametrizam tipos.\n",
    }
    for relpath, text in articles.items():
        (tmp_wiki / relpath).write_text(text, encoding="utf-8")
    return tmp_wiki


def _snapshot(results):
    return [(str(item["path"]), item["score"], item["snippet"]) for item in results]


class TestParity:
    def test_should_return_identical_results_with_and_without_index(self, corpus, monkeypatch):
        from kb.config import STATE_DIR

        monkeypatch.setenv("KB_INDEX_AUTO_REFRESH", "0")
        without = {q: _snapshot(search(q, top_k=5, mode="lexical")) for q in QUERIES}

        build_index(corpus, STATE_DIR)
        with_index = {q: _snapshot(search(q, top_k=5, mode="lexical")) for q in QUERIES}

        assert with_index == without

    def test_should_return_identical_channel_scores_with_index(self, corpus, monkeypatch):
        from kb.config import STATE_DIR

        monkeypatch.setenv("KB_INDEX_AUTO_REFRESH", "0")
        without = [item["channel_scores"] for item in search("vulnerabilidade web", top_k=5)]

        build_index(corpus, STATE_DIR)
        with_index = [item["channel_scores"] for item in search("vulnerabilidade web", top_k=5)]

        assert with_index == without

    def test_should_keep_snippet_empty_for_article_without_term_match(self, corpus, monkeypatch):
        from kb.config import STATE_DIR

        (corpus / "python" / "sub.md").write_text("# Sub\n\nxsstest não casa o termo.\n", encoding="utf-8")
        build_index(corpus, STATE_DIR)
        monkeypatch.setenv("KB_INDEX_AUTO_REFRESH", "0")

        _, _, _, snippets = _build_rankings("xss")

        assert snippets.get(corpus / "python" / "sub.md", "") == ""


class TestIsolation:
    def test_should_not_write_index_when_auto_refresh_is_off(self, corpus, monkeypatch):
        from kb.config import STATE_DIR

        monkeypatch.setenv("KB_INDEX_AUTO_REFRESH", "0")

        search("xss", top_k=5, mode="lexical")

        assert not (STATE_DIR / INDEX_FILENAME).exists()

    def test_should_write_index_only_inside_isolated_state_dir(self, corpus, tmp_path, monkeypatch):
        from kb.config import STATE_DIR

        monkeypatch.delenv("KB_INDEX_AUTO_REFRESH", raising=False)

        search("xss", top_k=5, mode="lexical")

        assert str(STATE_DIR).startswith(str(tmp_path))
        assert (STATE_DIR / INDEX_FILENAME).exists()


class TestRefresh:
    def test_should_see_new_article_after_index_was_built(self, corpus, monkeypatch):
        from kb.config import STATE_DIR

        monkeypatch.delenv("KB_INDEX_AUTO_REFRESH", raising=False)
        build_index(corpus, STATE_DIR)
        (corpus / "cybersecurity" / "csrf.md").write_text("# CSRF\n\ncsrf forja requisições.\n", encoding="utf-8")

        results = search("csrf", top_k=5, mode="lexical")

        assert [item["path"].name for item in results] == ["csrf.md"]
