from kb.claims import run_contradiction_check, list_claims


def test_contradiction_check_should_mark_opposite_claims_as_disputed(tmp_raw_wiki):
    raw, wiki = tmp_raw_wiki
    state_dir = raw.parent / "kb_state"
    state_dir.mkdir(parents=True, exist_ok=True)

    (state_dir / "claims.jsonl").write_text(
        "\n".join(
            [
                '{"id":"c1","text":"Não usamos Redis para cache.","topic":"ai","source":"x.md","status":"active","confidence":0.7}',
                '{"id":"c2","text":"Usamos Redis para cache.","topic":"ai","source":"x.md","status":"active","confidence":0.68}',
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    report = run_contradiction_check()
    claims = {c["id"]: c for c in list_claims()}

    assert report["disputed"] == 2
    assert claims["c1"]["status"] == "disputed"
    assert claims["c2"]["status"] == "disputed"
