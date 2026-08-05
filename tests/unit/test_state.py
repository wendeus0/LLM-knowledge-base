from kb.state import (
    add_learning,
    find_compiled_entry,
    load_knowledge,
    load_learnings,
    mark_compiled,
    record_ingest,
    upsert_knowledge,
)


def test_should_record_ingest_entry(tmp_raw_wiki):
    raw, wiki = tmp_raw_wiki
    source = raw / "doc.md"
    source.write_text("# Doc")

    entry = record_ingest(source)

    assert entry["status"] == "ingested"


def test_should_upsert_knowledge_entry(tmp_raw_wiki):
    upsert_knowledge(
        {"title": "XSS", "article": "wiki/xss.md", "summary_text": "Resumo 1"}
    )
    upsert_knowledge(
        {"title": "XSS", "article": "wiki/xss.md", "summary_text": "Resumo 2"}
    )

    entries = load_knowledge()
    assert len(entries) == 1
    assert entries[0]["summary_text"] == "Resumo 2"


def test_should_add_learnings(tmp_raw_wiki):
    add_learning("retrieval", "Preferir wiki", source="qa")

    entries = load_learnings()
    assert len(entries) == 1
    assert entries[0]["source"] == "qa"


def test_should_mark_compiled_entry(tmp_raw_wiki):
    raw, wiki = tmp_raw_wiki
    source = raw / "doc.md"
    source.write_text("# Doc")
    article = wiki / "ai" / "doc.md"
    article.write_text("# Compiled")
    summary = wiki / "_summaries" / "ai" / "doc.md"
    summary.parent.mkdir(parents=True, exist_ok=True)
    summary.write_text("# Summary")

    entry = mark_compiled(source, article, summary, "ai", "Doc")

    assert entry["status"] == "compiled"
    assert entry["article"].endswith("doc.md")


def test_should_replace_ingested_entry_when_compiling_same_source_with_different_path_style(
    tmp_raw_wiki,
):
    raw, wiki = tmp_raw_wiki
    source = raw / "books" / "mml" / "01-intro.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Doc")
    article = wiki / "ai" / "intro.md"
    article.write_text("# Compiled")
    summary = wiki / "_summaries" / "ai" / "intro.md"
    summary.parent.mkdir(parents=True, exist_ok=True)
    summary.write_text("# Summary")

    record_ingest(source)
    mark_compiled(source.relative_to(raw), article, summary, "ai", "Intro")

    entry = find_compiled_entry(source)

    assert entry is not None
    assert entry["status"] == "compiled"
    assert entry["article"].endswith("intro.md")


def test_should_not_drop_entries_without_dedup_key(tmp_raw_wiki):
    upsert_knowledge({"summary_text": "Entry 1"})
    upsert_knowledge({"summary_text": "Entry 2"})

    entries = load_knowledge()
    assert len(entries) == 2


def test_should_find_compiled_entry_independently_of_source_path_style(tmp_raw_wiki):
    raw, wiki = tmp_raw_wiki
    nested = raw / "books" / "mml"
    nested.mkdir(parents=True)
    source = nested / "01-intro.md"
    source.write_text("# Doc")
    article = wiki / "ai" / "intro.md"
    article.write_text("# Compiled")
    summary = wiki / "_summaries" / "ai" / "intro.md"
    summary.parent.mkdir(parents=True, exist_ok=True)
    summary.write_text("# Summary")

    mark_compiled(source.relative_to(raw), article, summary, "ai", "Intro")

    entry = find_compiled_entry(source)

    assert entry is not None
    assert entry["article"].endswith("intro.md")


def test_should_upsert_knowledge_by_normalized_source(tmp_raw_wiki):
    raw, _ = tmp_raw_wiki
    source = raw / "books" / "mml" / "01-intro.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Doc")

    upsert_knowledge(
        {
            "source": str(source.relative_to(raw)),
            "article": "wiki/old.md",
            "summary_text": "Resumo 1",
        }
    )
    upsert_knowledge(
        {"source": str(source), "article": "wiki/new.md", "summary_text": "Resumo 2"}
    )

    entries = load_knowledge()
    assert len(entries) == 1
    assert entries[0]["article"] == "wiki/new.md"


class TestManifestV2:
    """028 B1: entradas ganham proveniência auditável e paths relativos, sem
    quebrar entradas legadas nem o guard de recompile."""

    def test_should_write_backfill_entry_with_relative_paths_and_provenance(
        self, tmp_raw_wiki, monkeypatch
    ):
        import kb.config
        from kb.state import load_manifest, record_backfill

        raw, wiki = tmp_raw_wiki
        data_dir = raw.parent
        monkeypatch.setattr(kb.config, "DATA_DIR", data_dir)
        library = data_dir / "library" / "software" / "livro-a"
        library.mkdir(parents=True)
        (library / "05-real.md").write_text("capítulo", encoding="utf-8")
        artigo = wiki / "ai" / "artigo.md"
        artigo.write_text("---\ntitle: A\n---\ncorpo", encoding="utf-8")

        entry = record_backfill(
            source_path=library / "05-real.md",
            article_path=artigo,
            book="livro-a",
            provenance="backfill-basename",
        )

        assert entry["source"] == "library/software/livro-a/05-real.md"
        assert entry["article"] == "ai/artigo.md"
        assert entry["book"] == "livro-a"
        assert entry["provenance"] == "backfill-basename"
        assert entry["status"] == "compiled"
        assert load_manifest()[-1] == entry

    def test_should_treat_legacy_entry_without_provenance_as_compile(self, tmp_raw_wiki):
        from kb.state import entry_provenance, load_manifest, save_manifest

        save_manifest([{"source": "a.md", "kind": "raw", "status": "compiled"}])

        assert entry_provenance(load_manifest()[0]) == "compile"

    def test_should_mark_entry_archived_when_its_article_is_archived(
        self, tmp_raw_wiki, monkeypatch
    ):
        import kb.config
        from kb.state import load_manifest, mark_archived, record_backfill

        raw, wiki = tmp_raw_wiki
        monkeypatch.setattr(kb.config, "DATA_DIR", raw.parent)
        artigo = wiki / "duplicata.md"
        artigo.write_text("---\ntitle: D\n---\ncorpo", encoding="utf-8")
        record_backfill(
            source_path=raw / "x.md", article_path=artigo, book=None, provenance="backfill-content"
        )

        alterados = mark_archived(artigo)

        assert alterados == 1
        entry = load_manifest()[-1]
        assert entry["status"] == "archived"

    def test_should_find_compiled_entry_for_backfilled_library_source(
        self, tmp_raw_wiki, monkeypatch
    ):
        """O guard de recompile precisa enxergar a entrada nova mesmo com a
        fonte fora de RAW_DIR."""
        import kb.config
        from kb.state import find_compiled_entry, record_backfill

        raw, wiki = tmp_raw_wiki
        data_dir = raw.parent
        monkeypatch.setattr(kb.config, "DATA_DIR", data_dir)
        library = data_dir / "library" / "ai" / "livro-b"
        library.mkdir(parents=True)
        fonte = library / "07-cap.md"
        fonte.write_text("capítulo", encoding="utf-8")
        artigo = wiki / "cap.md"
        artigo.write_text("---\ntitle: C\n---\ncorpo", encoding="utf-8")
        record_backfill(source_path=fonte, article_path=artigo, book="livro-b", provenance="backfill-basename")

        assert find_compiled_entry(fonte) is not None

    def test_should_update_article_path_when_article_moves(self, tmp_raw_wiki, monkeypatch):
        import kb.config
        from kb.state import load_manifest, record_backfill, update_article_path

        raw, wiki = tmp_raw_wiki
        monkeypatch.setattr(kb.config, "DATA_DIR", raw.parent)
        artigo = wiki / "antigo.md"
        artigo.write_text("---\ntitle: A\n---\ncorpo", encoding="utf-8")
        record_backfill(source_path=raw / "y.md", article_path=artigo, book=None, provenance="backfill-content")

        alterados = update_article_path(artigo, wiki / "_chapters" / "livro" / "antigo.md")

        assert alterados == 1
        assert load_manifest()[-1]["article"] == "_chapters/livro/antigo.md"
