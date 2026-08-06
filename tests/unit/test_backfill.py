"""028 B2 — reconstrução da proveniência artigo→fonte (RF-02).

Seam: kb.backfill (backfill_links, ProposedLink). Cadeia de pareamento:
basename único → conteúdo idêntico → cosseno (injetado) → unresolved.
"""

from kb.backfill import backfill_links


def _vault(tmp_path):
    data = tmp_path / "vault"
    wiki = data / "wiki"
    raw = data / "raw"
    wiki.mkdir(parents=True)
    raw.mkdir(parents=True)
    return data, wiki, raw


def _book(data, area, book, arquivos):
    d = data / "library" / area / book
    d.mkdir(parents=True)
    for nome, corpo in arquivos.items():
        (d / nome).write_text(corpo, encoding="utf-8")
    return d


def _artigo(wiki, rel, source, corpo="Corpo do artigo."):
    p = wiki / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(f"---\ntitle: T\ntopic: general\nsource: {source}\n---\n\n{corpo}\n", encoding="utf-8")
    return p


def test_should_link_article_by_unique_basename(tmp_path):
    data, wiki, raw = _vault(tmp_path)
    _book(data, "ai", "livro-a", {"07-atencao.md": "# Atenção\ntexto"})
    artigo = _artigo(wiki, "atencao.md", "07-atencao.md")

    [link] = backfill_links(wiki, data, raw)

    assert link.article == artigo
    assert link.source == data / "library" / "ai" / "livro-a" / "07-atencao.md"
    assert link.book == "livro-a"
    assert link.provenance == "backfill-basename"


def test_should_link_by_content_when_ambiguous_candidates_are_identical(tmp_path):
    data, wiki, raw = _vault(tmp_path)
    corpo = "# Capítulo\nmesmo conteúdo em dois lugares"
    _book(data, "ai", "livro-a", {"01-intro.md": corpo})
    _book(data, "python", "livro-b", {"01-intro.md": corpo})
    _artigo(wiki, "intro.md", "01-intro.md")

    [link] = backfill_links(wiki, data, raw)

    assert link.provenance == "backfill-content"
    assert link.source is not None


def test_should_resolve_ambiguity_by_cosine_when_contents_differ(tmp_path):
    data, wiki, raw = _vault(tmp_path)
    _book(data, "ai", "livro-a", {"02-cap.md": "redes neurais e atenção"})
    _book(data, "python", "livro-b", {"02-cap.md": "loops e list comprehensions"})
    artigo = _artigo(wiki, "cap.md", "02-cap.md", corpo="Artigo sobre atenção em redes neurais.")

    def embed(textos):
        return [[1.0, 0.0] if "atenção" in t or "neurais" in t else [0.0, 1.0] for t in textos]

    [link] = backfill_links(wiki, data, raw, embed_fn=embed)

    assert link.article == artigo
    assert link.provenance == "backfill-cosine"
    assert link.book == "livro-a"
    assert link.score is not None and link.score > 0.9


def test_should_mark_unresolved_when_cosine_is_below_the_floor(tmp_path):
    data, wiki, raw = _vault(tmp_path)
    _book(data, "ai", "livro-a", {"03-cap.md": "conteúdo alfa"})
    _book(data, "python", "livro-b", {"03-cap.md": "conteúdo beta"})
    _artigo(wiki, "cap.md", "03-cap.md", corpo="assunto totalmente ortogonal")

    def embed(textos):
        vetores = []
        for t in textos:
            if "ortogonal" in t:
                vetores.append([1.0, 0.0, 0.0])
            elif "alfa" in t:
                vetores.append([0.0, 1.0, 0.0])
            else:
                vetores.append([0.0, 0.0, 1.0])
        return vetores

    [link] = backfill_links(wiki, data, raw, embed_fn=embed)

    assert link.provenance == "unresolved"
    assert link.source is None


def test_should_mark_unresolved_without_embed_function(tmp_path):
    """Servidor de embeddings fora: ambíguo degrada para unresolved, nunca chuta."""
    data, wiki, raw = _vault(tmp_path)
    _book(data, "ai", "livro-a", {"04-cap.md": "um"})
    _book(data, "python", "livro-b", {"04-cap.md": "dois"})
    _artigo(wiki, "cap.md", "04-cap.md")

    [link] = backfill_links(wiki, data, raw)

    assert link.provenance == "unresolved"


def test_should_mark_unresolved_when_no_source_candidate_exists(tmp_path):
    data, wiki, raw = _vault(tmp_path)
    _artigo(wiki, "orfao.md", "99-inexistente.md")

    [link] = backfill_links(wiki, data, raw)

    assert link.provenance == "unresolved"
    assert link.candidates == 0


def test_should_search_wiki_sources_and_skip_underscore_articles(tmp_path):
    data, wiki, raw = _vault(tmp_path)
    fonte = wiki / "_sources" / "livro-c" / "05-cap.md"
    fonte.parent.mkdir(parents=True)
    fonte.write_text("fonte em _sources", encoding="utf-8")
    artigo = _artigo(wiki, "cap.md", "05-cap.md")
    _artigo(wiki, "_pipeline/nota.md", "05-cap.md")

    links = backfill_links(wiki, data, raw)

    assert [link.article for link in links] == [artigo]
    assert links[0].source == fonte
    assert links[0].book == "livro-c"


def test_should_mark_unresolved_when_top_cosines_tie(tmp_path):
    """Review PR #70 (cubic P2): empate no topo escolhia livro por ordem de
    filesystem — proveniência arbitrária apresentada como fato."""
    data, wiki, raw = _vault(tmp_path)
    _book(data, "ai", "livro-a", {"05-cap.md": "conteúdo A"})
    _book(data, "python", "livro-b", {"05-cap.md": "conteúdo B"})
    _artigo(wiki, "cap.md", "05-cap.md", corpo="artigo")

    def embed(textos):
        return [[1.0, 0.0]] + [[1.0, 0.0] for _ in textos[1:]]  # todos iguais

    [link] = backfill_links(wiki, data, raw, embed_fn=embed)

    assert link.provenance == "unresolved"


def test_should_skip_symlinked_articles(tmp_path):
    data, wiki, raw = _vault(tmp_path)
    real = tmp_path / "fora.md"
    real.write_text("---\ntitle: X\nsource: 01-x.md\n---\ncorpo", encoding="utf-8")
    (wiki / "link.md").symlink_to(real)

    assert backfill_links(wiki, data, raw) == []


def test_should_use_precomputed_article_vector_when_available(tmp_path):
    """Review PR #70 (cubic P1): o vetor do artigo já existe no índice; só os
    candidatos precisam de embedding."""
    data, wiki, raw = _vault(tmp_path)
    _book(data, "ai", "livro-a", {"06-cap.md": "texto sobre atenção"})
    _book(data, "python", "livro-b", {"06-cap.md": "texto sobre loops"})
    artigo = _artigo(wiki, "cap.md", "06-cap.md", corpo="qualquer corpo")

    def embed(textos):
        assert all("qualquer corpo" not in t for t in textos), "artigo não deve ser re-embedado"
        return [[1.0, 0.0] if "atenção" in t else [0.0, 1.0] for t in textos]

    [link] = backfill_links(
        wiki, data, raw, embed_fn=embed, article_vectors={artigo: [1.0, 0.0]}
    )

    assert link.provenance == "backfill-cosine"
    assert link.book == "livro-a"
