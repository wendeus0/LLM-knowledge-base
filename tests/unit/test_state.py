from kb.state import add_learning, load_knowledge, load_learnings, mark_compiled, record_ingest, upsert_knowledge


def test_should_record_ingest_entry(tmp_raw_wiki):
    raw, wiki = tmp_raw_wiki
    source = raw / "doc.md"
    source.write_text("# Doc")

    entry = record_ingest(source)

    assert entry["status"] == "ingested"


def test_should_upsert_knowledge_entry(tmp_raw_wiki):
    upsert_knowledge({"title": "XSS", "article": "wiki/xss.md", "summary_text": "Resumo 1"})
    upsert_knowledge({"title": "XSS", "article": "wiki/xss.md", "summary_text": "Resumo 2"})

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
    summary = wiki / "summaries" / "doc.md"
    summary.parent.mkdir(exist_ok=True)
    summary.write_text("# Summary")

    entry = mark_compiled(source, article, summary, "ai", "Doc")

    assert entry["status"] == "compiled"
    assert entry["article"].endswith("doc.md")
