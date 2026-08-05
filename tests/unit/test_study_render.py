from pathlib import Path


def test_should_render_a_resolved_wikilink_to_its_rel_slug():
    from study.render import render_markdown

    html = render_markdown(
        "Veja [[OSINT]].",
        [{"text": "OSINT", "targets": ["ai/osint"], "ambiguous": False}],
    )

    assert 'href="/a/ai/osint"' in html
    assert ">OSINT</a>" in html


def test_should_mark_an_ambiguous_wikilink_without_choosing_a_target():
    from study.render import render_markdown

    html = render_markdown(
        "Veja [[honeycomb]].",
        [
            {
                "text": "honeycomb",
                "targets": ["honeycomb", "cybersecurity/honeycomb"],
                "ambiguous": True,
            }
        ],
    )

    assert "wikilink--ambiguous" in html
    assert "ambíguo" in html
    assert "/a/honeycomb" not in html
    assert "/a/cybersecurity/honeycomb" not in html


def test_should_offer_a_source_hook_for_an_unresolved_wikilink():
    from study.render import render_markdown

    html = render_markdown(
        "Veja [[tema ausente]].",
        [{"text": "tema ausente", "targets": [], "ambiguous": False}],
    )

    # O gancho é a própria palavra, não um botão ao lado: um controle inline no
    # meio da frase separava a pontuação ("de OSINT [botão] , reconhecimento").
    assert "wikilink--missing" in html
    assert 'hx-get="/fontes?termo=tema+ausente"' in html
    assert "tema ausente</button>" in html
    assert "buscar fontes" in html  # segue anunciado, agora em title/aria-label


def test_should_classify_local_sources_without_reading_epub_content(tmp_path):
    from study.sources import buscar_fontes

    (tmp_path / "raw").mkdir()
    (tmp_path / "library").mkdir()
    (tmp_path / "wiki" / "_sources").mkdir(parents=True)
    (tmp_path / "raw" / "guia.md").write_text("Tema: Zero Trust", encoding="utf-8")
    (tmp_path / "library" / "zero-trust.epub").write_bytes(b"\x00tema")
    (tmp_path / "wiki" / "_sources" / "referencias.md").write_text(
        "Zero Trust em fontes", encoding="utf-8"
    )

    found = buscar_fontes("zero trust", data_dir=tmp_path)

    by_origin = {item["origin"]: item for item in found["origins"]}
    assert by_origin["raw"]["action"] == "Compilar diretamente"
    assert by_origin["library"]["action"] == "Importar livro antes"
    assert by_origin["sources"]["action"] == "Procurar artigo existente"
    assert all(item["matches"] for item in by_origin.values())
    assert isinstance(by_origin["library"]["matches"][0]["path"], str)
    assert not isinstance(by_origin["library"]["matches"][0]["path"], Path)


def test_should_drop_the_leading_h1_because_the_template_already_shows_the_title():
    """Todo artigo do kb começa com `# <título>`, e o template renderiza o
    title do frontmatter acima — sem isto, todo artigo mostra o nome duas vezes.
    """
    from study.render import render_markdown

    html = render_markdown("# Google Hacking\n\nTexto do corpo.\n", [])

    assert "<h1" not in html
    assert "Texto do corpo" in html


def test_should_keep_an_h1_that_is_not_the_first_block():
    from study.render import render_markdown

    html = render_markdown("Introdução.\n\n# Outro título\n\nMais texto.\n", [])

    assert "<h1" in html


def test_should_resolve_the_vault_from_kb_config_not_from_raw_env(monkeypatch, tmp_path):
    """`KB_DATA_DIR` vive no .env, que o `kb` carrega e o `study` não carregava.

    Lendo `os.getenv` cru, a busca caía em `Path.cwd()` — o repositório, sem
    `raw/` — e o gancho de fontes não achava nada em produção nenhuma.
    """
    import kb.config

    vault = tmp_path / "vault"
    (vault / "raw").mkdir(parents=True)
    (vault / "raw" / "xss-attack-explained.md").write_text("sobre XSS", encoding="utf-8")
    monkeypatch.delenv("KB_DATA_DIR", raising=False)
    monkeypatch.setattr(kb.config, "DATA_DIR", vault)

    from study.sources import buscar_fontes

    resultado = buscar_fontes("XSS")

    assert resultado["found"] is True
    raw = next(o for o in resultado["origins"] if o["origin"] == "raw")
    assert any("xss" in m.lower() for m in map(str, raw["matches"]))
