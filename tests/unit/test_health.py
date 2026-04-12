from kb.analytics.health import get_health_summary, render_health_summary


def test_health_summary_should_compute_state_percentages(tmp_raw_wiki):
    raw, wiki = tmp_raw_wiki
    state_dir = raw.parent / "kb_state"
    state_dir.mkdir(parents=True, exist_ok=True)

    (state_dir / "claims.jsonl").write_text(
        "\n".join(
            [
                '{"id":"c1","status":"active","confidence":0.9}',
                '{"id":"c2","status":"stale","confidence":0.2}',
                '{"id":"c3","status":"disputed","confidence":0.4}',
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    summary = get_health_summary()

    assert summary["total_claims"] == 3
    assert summary["stale_pct"] == 33.3
    assert summary["disputed_pct"] == 33.3
    assert summary["active_pct"] == 33.3


def test_health_render_should_return_human_readable_block(tmp_raw_wiki):
    raw, wiki = tmp_raw_wiki
    state_dir = raw.parent / "kb_state"
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / "claims.jsonl").write_text('{"id":"c1","status":"active","confidence":0.8}\n')

    report = render_health_summary()

    assert "Job health executado." in report
    assert "total_claims" in report
    assert "active_pct" in report
