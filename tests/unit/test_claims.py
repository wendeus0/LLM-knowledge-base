from kb.claims import apply_decay_cycle, list_claims, record_compiled_claims


def test_should_record_compiled_claim_as_active_with_confidence(tmp_raw_wiki):
    raw, wiki = tmp_raw_wiki
    source = raw / "doc.md"
    source.write_text("# Doc")
    article = wiki / "ai" / "doc.md"
    article.parent.mkdir(parents=True, exist_ok=True)
    article.write_text("# Doc")

    claims = record_compiled_claims(
        source_path=source,
        article_path=article,
        topic="ai",
        summary_text="Projeto X usa Redis para cache.",
    )

    assert len(claims) == 1
    claim = claims[0]
    assert claim["status"] == "active"
    assert claim["confidence"] > 0
    assert claim["evidence_count"] == 1


def test_should_supersede_previous_active_claim_from_same_source(tmp_raw_wiki):
    raw, wiki = tmp_raw_wiki
    source = raw / "doc.md"
    source.write_text("# Doc")
    article = wiki / "ai" / "doc.md"
    article.parent.mkdir(parents=True, exist_ok=True)
    article.write_text("# Doc")

    first = record_compiled_claims(
        source_path=source,
        article_path=article,
        topic="ai",
        summary_text="Projeto X usa Redis para cache.",
    )[0]

    second = record_compiled_claims(
        source_path=source,
        article_path=article,
        topic="ai",
        summary_text="Projeto X usa Valkey para cache.",
    )[0]

    claims = list_claims()
    first_latest = next(item for item in claims if item["id"] == first["id"])
    second_latest = next(item for item in claims if item["id"] == second["id"])

    assert first_latest["status"] == "superseded"
    assert first_latest["relationships"]["superseded_by"] == second_latest["id"]
    assert second_latest["relationships"]["supersedes"] == first_latest["id"]


def test_should_mark_old_low_confidence_claim_as_stale_on_decay_cycle(tmp_raw_wiki):
    raw, wiki = tmp_raw_wiki
    source = raw / "old.md"
    source.write_text("# Old")
    article = wiki / "ai" / "old.md"
    article.parent.mkdir(parents=True, exist_ok=True)
    article.write_text("# Old")

    claim = record_compiled_claims(
        source_path=source,
        article_path=article,
        topic="bug",
        summary_text="Erro transitório Z ocorre em condição rara.",
    )[0]

    updated_count = apply_decay_cycle(days_forward=400)

    claims = list_claims()
    latest = next(item for item in claims if item["id"] == claim["id"])

    assert updated_count >= 1
    assert latest["status"] in {"stale", "superseded"}
    assert latest["confidence"] < claim["confidence"]
