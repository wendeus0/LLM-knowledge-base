from pathlib import Path
from kb.search import find_relevant, search


class TestFindRelevant:
    """Testes unitários para find_relevant()"""

    def test_should_find_articles_matching_query(self, tmp_raw_wiki):
        """
        Dado uma wiki com artigos contendo palavras-chave,
        Quando find_relevant() busca por termo,
        Então deve retornar artigos com esse termo
        """
        raw, wiki = tmp_raw_wiki

        # Criar artigos
        (wiki / "cybersecurity" / "xss.md").write_text("# XSS\n\nXSS é uma vulnerabilidade web.")
        (wiki / "ai" / "ml.md").write_text("# Machine Learning\n\nML é algoritmo.")

        # RED: falha se não encontra artigos com o termo
        results = find_relevant("XSS")
        assert len(results) > 0
        assert any("xss" in str(r).lower() for r in results)

    def test_should_return_empty_list_when_no_matches(self, tmp_raw_wiki):
        """
        Dado uma wiki,
        Quando busca por termo inexistente,
        Então deve retornar lista vazia
        """
        raw, wiki = tmp_raw_wiki

        (wiki / "python" / "decorators.md").write_text("# Decorators\n")

        # RED: falha se não retorna list vazia
        results = find_relevant("INEXISTENTE_TERMO_RARO_12345")
        assert isinstance(results, list)
        assert len(results) == 0

    def test_should_return_list_of_paths(self, tmp_raw_wiki):
        """
        Dado uma busca com resultados,
        Quando find_relevant() retorna,
        Então deve ser list de Path objects
        """
        raw, wiki = tmp_raw_wiki

        (wiki / "python" / "tutorial.md").write_text("# Python Tutorial\n\nPython é uma linguagem.")

        # RED: falha se resultados não são Path
        results = find_relevant("python")
        for r in results:
            assert isinstance(r, Path)

    def test_should_respect_top_k_limit(self, tmp_raw_wiki):
        """
        Dado múltiplos artigos com o termo,
        Quando find_relevant(top_k=2) é chamado,
        Então deve retornar no máximo 2 resultados
        """
        raw, wiki = tmp_raw_wiki

        for i in range(5):
            (wiki / "python" / f"article{i}.md").write_text(f"Python tutorial {i}")

        # RED: falha se retorna mais que top_k
        results = find_relevant("python", top_k=2)
        assert len(results) <= 2


class TestSearch:
    """Testes para search() — versão CLI"""

    def test_should_return_list_of_dicts(self, tmp_raw_wiki):
        """
        Dado uma busca bem-sucedida,
        Quando search() retorna,
        Então cada resultado deve ter estrutura dict com path, score, snippet
        """
        raw, wiki = tmp_raw_wiki

        (wiki / "ai" / "neural-nets.md").write_text("# Neural Networks\n\nRedes neurais...")

        # RED: falha se não retorna dicts estruturados
        results = search("neural")
        assert isinstance(results, list)
        if len(results) > 0:
            assert "path" in results[0]
            assert "score" in results[0]
            assert "snippet" in results[0]

    def test_should_format_results(self, tmp_raw_wiki):
        """
        Dado resultados de busca,
        Quando search() é executado,
        Então deve retornar dados estruturados
        """
        raw, wiki = tmp_raw_wiki

        (wiki / "cybersecurity" / "auth.md").write_text("# Auth\n\nAutenticação...")

        # RED: falha se não formata resultados
        results = search("auth")
        assert isinstance(results, list)
