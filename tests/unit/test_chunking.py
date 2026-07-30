"""RED — feature 017: divisão de artigo em chunks por seção.

A divisão é pura de propósito: é o que decide o que o modelo enxerga, e
precisa ser verificável sem servidor nem disco.
"""

from kb import chunking


class TestSplitSections:
    def test_should_split_by_level_two_headings(self):
        text = "## Primeira\nconteudo um\n\n## Segunda\nconteudo dois\n"

        sections = chunking.split_sections(text)

        assert [heading for heading, _ in sections] == ["Primeira", "Segunda"]
        assert "conteudo um" in sections[0][1]

    def test_should_keep_preamble_as_its_own_section(self):
        text = "abertura do artigo\n\n## Primeira\nconteudo\n"

        sections = chunking.split_sections(text)

        assert sections[0][0] == ""
        assert "abertura do artigo" in sections[0][1]
        assert sections[1][0] == "Primeira"

    def test_should_keep_deeper_headings_inside_parent_section(self):
        text = "## Pai\nintro\n\n### Filho\ndetalhe\n"

        sections = chunking.split_sections(text)

        assert len(sections) == 1
        assert "### Filho" in sections[0][1]
        assert "detalhe" in sections[0][1]

    def test_should_return_single_section_when_no_headings(self):
        text = "somente corpo, sem heading nenhum"

        sections = chunking.split_sections(text)

        assert len(sections) == 1
        assert sections[0][0] == ""


class TestBuildChunks:
    def test_should_prefix_each_chunk_with_title_and_heading(self):
        text = "## Gotchas\ncuidado com isso\n" + "x" * 300

        chunks = chunking.build_chunks("Circuit Breaker", text)

        assert chunks[0]["heading"] == "Gotchas"
        assert "Circuit Breaker" in chunks[0]["text"]
        assert "Gotchas" in chunks[0]["text"]
        assert "cuidado com isso" in chunks[0]["text"]

    def test_should_merge_sections_below_minimum_size(self):
        text = "## A\ncurta\n\n## B\ntambem curta\n\n## C\n" + "y" * 400

        chunks = chunking.build_chunks("Titulo", text, min_chars=200)

        assert len(chunks) < 3
        merged = " ".join(chunk["text"] for chunk in chunks)
        assert "curta" in merged and "tambem curta" in merged

    def test_should_split_section_above_maximum_instead_of_truncating(self):
        text = "## Longa\n" + "z" * 5000

        chunks = chunking.build_chunks("Titulo", text, max_chars=1000)

        assert len(chunks) > 1
        recovered = "".join(chunk["text"] for chunk in chunks)
        assert recovered.count("z") == 5000

    def test_should_never_exceed_max_chars_per_chunk(self):
        text = "## Longa\n" + "z" * 5000

        chunks = chunking.build_chunks("Titulo", text, max_chars=1000)

        assert all(len(chunk["text"]) <= 1000 for chunk in chunks)

    def test_should_produce_one_chunk_for_article_without_headings(self):
        chunks = chunking.build_chunks("Titulo", "corpo simples e suficientemente longo" * 10)

        assert len(chunks) == 1
        assert "Titulo" in chunks[0]["text"]

    def test_should_ignore_frontmatter_when_chunking(self):
        text = "---\ntitle: X\ntags: [a]\n---\n\n## Secao\n" + "w" * 300

        chunks = chunking.build_chunks("X", text)

        assert all("tags:" not in chunk["text"] for chunk in chunks)
