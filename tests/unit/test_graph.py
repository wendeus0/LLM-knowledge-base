"""Testes RED para kb/graph.py — traversal de wikilinks.

Rastreabilidade SPEC:
  REQ-1: extract_wikilinks detecta [[link]], [[Link com espaço]], ignora markdown normal
  REQ-2: resolve_wikilink encontra arquivo em wiki/**/<link>.md; None se não existir
  REQ-3: load_frontmatter lê apenas bloco YAML sem corpo
  REQ-4: traverse para no budget de tokens
  REQ-5: traverse não visita arquivo duas vezes (sem ciclos)
  REQ-6: traverse respeita depth (depth=1 só segue links dos seed_files)
  REQ-7: traverse retorna apenas arquivos relevantes para a pergunta
"""

# RED: falha até wikilink-traversal ser implementada
from kb.graph import (
    extract_wikilinks,
    load_frontmatter,
    resolve_wikilink,
    traverse,
)  # noqa: E402


class TestExtractWikilinks:
    """Testa kb.graph.extract_wikilinks(content)."""

    def test_should_detect_simple_wikilink(self):
        """REQ-1: [[link]] deve ser detectado."""
        # RED: falha até wikilink-traversal ser implementada
        content = "Veja [[xss]] para mais detalhes."
        assert extract_wikilinks(content) == ["xss"]

    def test_should_detect_wikilink_with_spaces(self):
        """REQ-1: [[Link com espaço]] deve ser detectado."""
        # RED: falha até wikilink-traversal ser implementada
        content = "Relacionado com [[sql injection]] e [[csrf attack]]."
        links = extract_wikilinks(content)
        assert "sql injection" in links
        assert "csrf attack" in links

    def test_should_ignore_standard_markdown_links(self):
        """REQ-1: [texto](url) não deve ser detectado como wikilink."""
        # RED: falha até wikilink-traversal ser implementada
        content = "[Clique aqui](https://example.com) e veja [[xss]]."
        links = extract_wikilinks(content)
        assert links == ["xss"]
        assert "https://example.com" not in links

    def test_should_return_empty_list_when_no_wikilinks(self):
        """REQ-1: sem wikilinks retorna lista vazia."""
        # RED: falha até wikilink-traversal ser implementada
        content = "Texto sem nenhum link especial."
        assert extract_wikilinks(content) == []

    def test_should_deduplicate_wikilinks(self):
        """REQ-1: wikilinks duplicados devem aparecer uma única vez."""
        # RED: falha até wikilink-traversal ser implementada
        content = "[[xss]] é perigoso. Mais sobre [[xss]] aqui."
        links = extract_wikilinks(content)
        assert links.count("xss") == 1


class TestResolveWikilink:
    """Testa kb.graph.resolve_wikilink(link, wiki_dir)."""

    def test_should_resolve_existing_file(self, tmp_path):
        """REQ-2: resolve_wikilink deve retornar Path para arquivo existente."""
        # RED: falha até wikilink-traversal ser implementada
        wiki = tmp_path / "wiki"
        (wiki / "cybersecurity").mkdir(parents=True)
        xss_file = wiki / "cybersecurity" / "xss.md"
        xss_file.write_text("# XSS", encoding="utf-8")

        result = resolve_wikilink("xss", wiki)
        assert result == xss_file

    def test_should_return_none_when_file_not_found(self, tmp_path):
        """REQ-2: resolve_wikilink retorna None quando arquivo não existe."""
        # RED: falha até wikilink-traversal ser implementada
        wiki = tmp_path / "wiki"
        wiki.mkdir()

        result = resolve_wikilink("artigo-inexistente", wiki)
        assert result is None

    def test_should_resolve_case_insensitive_slug(self, tmp_path):
        """REQ-2: wikilink com espaços deve ser normalizado para slug do arquivo."""
        # RED: falha até wikilink-traversal ser implementada
        wiki = tmp_path / "wiki"
        (wiki / "cybersecurity").mkdir(parents=True)
        file = wiki / "cybersecurity" / "sql-injection.md"
        file.write_text("# SQL Injection", encoding="utf-8")

        result = resolve_wikilink("sql injection", wiki)
        assert result == file


class TestLoadFrontmatter:
    """Testa kb.graph.load_frontmatter(path)."""

    def test_should_parse_yaml_frontmatter(self, tmp_path):
        """REQ-3: load_frontmatter deve retornar dict com campos do YAML."""
        # RED: falha até wikilink-traversal ser implementada
        md = tmp_path / "article.md"
        md.write_text(
            "---\ntitle: XSS\ntopic: cybersecurity\ntags: [xss, web]\n---\n\n# XSS\n\nConteúdo.",
            encoding="utf-8",
        )

        fm = load_frontmatter(md)
        assert fm["title"] == "XSS"
        assert fm["topic"] == "cybersecurity"
        assert "xss" in fm["tags"]

    def test_should_return_empty_dict_when_no_frontmatter(self, tmp_path):
        """REQ-3: arquivo sem frontmatter retorna dict vazio."""
        # RED: falha até wikilink-traversal ser implementada
        md = tmp_path / "plain.md"
        md.write_text("# Título\n\nSem frontmatter.", encoding="utf-8")

        fm = load_frontmatter(md)
        assert fm == {}

    def test_should_not_include_body_content(self, tmp_path):
        """REQ-3: load_frontmatter não deve incluir conteúdo do corpo."""
        # RED: falha até wikilink-traversal ser implementada
        md = tmp_path / "article.md"
        md.write_text(
            "---\ntitle: XSS\n---\n\n# XSS\n\nEste é o corpo do artigo.",
            encoding="utf-8",
        )

        fm = load_frontmatter(md)
        assert "corpo do artigo" not in str(fm)


class TestTraverse:
    """Testa kb.graph.traverse(seed_files, question, depth, token_budget)."""

    def _make_wiki(self, tmp_path):
        wiki = tmp_path / "wiki" / "cybersecurity"
        wiki.mkdir(parents=True)
        return wiki

    def test_should_stop_when_token_budget_is_exhausted(self, tmp_path):
        """REQ-4: traverse não deve ultrapassar o budget de tokens."""
        # RED: falha até wikilink-traversal ser implementada
        wiki = self._make_wiki(tmp_path)
        seed = wiki / "xss.md"
        seed.write_text(
            "---\ntitle: XSS\ntags: [xss]\n---\n\n# XSS\n\nVeja [[csrf]].",
            encoding="utf-8",
        )
        linked = wiki / "csrf.md"
        linked.write_text(
            "---\ntitle: CSRF\ntags: [csrf, xss]\n---\n\n# CSRF\n\nConteúdo sobre csrf.\n"
            + ("y " * 500),
            encoding="utf-8",
        )

        result = traverse(
            seed_files=[seed],
            question="xss",
            wiki_dir=tmp_path / "wiki",
            depth=1,
            token_budget=100,  # seed ~12 tokens; csrf ~262 tokens — excede budget
        )

        # csrf não deve ser incluído — budget esgotado
        assert linked not in result

    def test_should_not_visit_file_twice(self, tmp_path):
        """REQ-5: ciclo A→B→A não deve duplicar B nem reintroduzir A no resultado."""
        wiki = self._make_wiki(tmp_path)

        file_a = wiki / "xss.md"
        file_a.write_text(
            "---\ntitle: XSS\ntags: [xss]\n---\n\n# XSS\n\nVeja [[csrf]].",
            encoding="utf-8",
        )
        file_b = wiki / "csrf.md"
        file_b.write_text(
            "---\ntitle: CSRF\ntags: [csrf, xss]\n---\n\n# CSRF\n\nVeja [[xss]].",
            encoding="utf-8",
        )

        result = traverse(
            seed_files=[file_a],
            question="xss csrf",
            wiki_dir=tmp_path / "wiki",
            depth=2,
            token_budget=8000,
        )

        # B deve aparecer exatamente uma vez — back-edge A←B não duplica
        assert result.count(file_b) == 1
        # A (seed) nunca deve ser adicionado ao resultado
        assert file_a not in result

    def test_should_respect_depth_1(self, tmp_path):
        """REQ-6: depth=1 não deve seguir links dos arquivos linkados."""
        # RED: falha até wikilink-traversal ser implementada
        wiki = self._make_wiki(tmp_path)

        seed = wiki / "xss.md"
        seed.write_text(
            "---\ntitle: XSS\ntags: [xss]\n---\n\n# XSS\n\nVeja [[csrf]].",
            encoding="utf-8",
        )
        level1 = wiki / "csrf.md"
        level1.write_text(
            "---\ntitle: CSRF\ntags: [csrf]\n---\n\n# CSRF\n\nVeja [[sqli]].",
            encoding="utf-8",
        )
        level2 = wiki / "sqli.md"
        level2.write_text(
            "---\ntitle: SQLi\ntags: [sqli, xss]\n---\n\n# SQLi\n\nConteúdo.",
            encoding="utf-8",
        )

        result = traverse(
            seed_files=[seed],
            question="csrf xss",
            wiki_dir=tmp_path / "wiki",
            depth=1,
            token_budget=8000,
        )

        # level2 não deve ser incluído com depth=1
        assert level2 not in result

    def test_should_include_relevant_linked_files(self, tmp_path):
        """REQ-7: arquivos linkados com frontmatter relevante devem ser incluídos."""
        # RED: falha até wikilink-traversal ser implementada
        wiki = self._make_wiki(tmp_path)

        seed = wiki / "xss.md"
        seed.write_text(
            "---\ntitle: XSS\ntags: [xss]\n---\n\n# XSS\n\nVeja [[csrf]].",
            encoding="utf-8",
        )
        linked = wiki / "csrf.md"
        linked.write_text(
            "---\ntitle: CSRF\ntags: [csrf, xss]\n---\n\n# CSRF\n\nConteúdo.",
            encoding="utf-8",
        )

        result = traverse(
            seed_files=[seed],
            question="csrf xss",
            wiki_dir=tmp_path / "wiki",
            depth=1,
            token_budget=8000,
        )

        assert linked in result
