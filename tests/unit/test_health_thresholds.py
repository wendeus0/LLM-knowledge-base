from kb.analytics.health import evaluate_health_thresholds


def test_health_thresholds_should_pass_when_within_limits():
    ok, violations = evaluate_health_thresholds(
        {"stale_pct": 10.0, "disputed_pct": 5.0},
        stale_max_pct=15.0,
        disputed_max_pct=8.0,
    )

    assert ok is True
    assert violations == []


def test_health_thresholds_should_fail_when_any_limit_exceeded():
    ok, violations = evaluate_health_thresholds(
        {"stale_pct": 22.5, "disputed_pct": 9.0},
        stale_max_pct=20.0,
        disputed_max_pct=8.0,
    )

    assert ok is False
    assert any("stale_pct" in item for item in violations)
    assert any("disputed_pct" in item for item in violations)
