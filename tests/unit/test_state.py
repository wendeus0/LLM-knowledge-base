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
    summary = wiki / "summaries" / "ai" / "doc.md"
    summary.parent.mkdir(parents=True, exist_ok=True)
    summary.write_text("# Summary")

    entry = mark_compiled(source, article, summary, "ai", "Doc")

    assert entry["status"] == "compiled"
    assert entry["article"].endswith("doc.md")


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
    summary = wiki / "summaries" / "ai" / "intro.md"
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
