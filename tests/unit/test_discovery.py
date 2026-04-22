"""Testes para kb/discovery.py: run loop, lock, seen-tracking."""

import json
from unittest.mock import MagicMock, patch

import pytest

from kb.config import STATE_DIR


@pytest.fixture(autouse=True)
def _isolate_state(tmp_path, monkeypatch):
    state_dir = tmp_path / "kb_state"
    state_dir.mkdir()
    monkeypatch.setattr("kb.discovery.STATE_DIR", state_dir)
    monkeypatch.setattr("kb.discovery.SEEN_URLS_PATH", state_dir / "discovery_seen_urls.json")
    monkeypatch.setattr("kb.config.STATE_DIR", state_dir)
    yield


def test_load_seen_urls_returns_empty_when_file_missing(tmp_path):
    from kb.discovery import _load_seen_urls

    assert _load_seen_urls() == set()


def test_load_seen_urls_reads_existing(tmp_path, monkeypatch):
    from kb.discovery import SEEN_URLS_PATH, _load_seen_urls

    payload = {"urls": ["https://a.com", "https://b.com"]}
    SEEN_URLS_PATH.write_text(json.dumps(payload))
    assert _load_seen_urls() == {"https://a.com", "https://b.com"}


def test_merge_and_save_seen_urls_atomic(tmp_path, monkeypatch):
    from kb.discovery import SEEN_URLS_PATH, _merge_and_save_seen_urls

    _merge_and_save_seen_urls({"https://x.com"})
    data = json.loads(SEEN_URLS_PATH.read_text())
    assert "https://x.com" in data["urls"]


def test_merge_and_save_seen_urls_merges_with_existing(tmp_path, monkeypatch):
    from kb.discovery import SEEN_URLS_PATH, _merge_and_save_seen_urls

    payload = {"urls": ["https://a.com"]}
    SEEN_URLS_PATH.write_text(json.dumps(payload))
    _merge_and_save_seen_urls({"https://b.com"})
    data = json.loads(SEEN_URLS_PATH.read_text())
    assert set(data["urls"]) == {"https://a.com", "https://b.com"}


def test_discover_arxiv_raises_without_requests(tmp_path, monkeypatch):
    import kb.discovery as mod

    original = mod.requests
    mod.requests = None
    try:
        with pytest.raises(RuntimeError, match="web"):
            mod.discover_arxiv("test")
    finally:
        mod.requests = original


def test_discover_articles_google_news_raises_without_requests(tmp_path, monkeypatch):
    import kb.discovery as mod

    original = mod.requests
    mod.requests = None
    try:
        with pytest.raises(RuntimeError, match="web"):
            mod.discover_articles_google_news("test")
    finally:
        mod.requests = original


@patch("kb.discovery.discover_arxiv")
@patch("kb.discovery.discover_articles_google_news")
@patch("kb.discovery.ingest_url")
def test_run_scheduled_skips_seen_urls(mock_ingest, mock_news, mock_arxiv, tmp_path, monkeypatch):
    from kb.discovery import DiscoveryItem, _merge_and_save_seen_urls, run_scheduled_discovery

    item = DiscoveryItem(title="Test", url="https://seen.com/paper", source="arxiv", published_at="2026-01-01")
    _merge_and_save_seen_urls({item.url})

    mock_arxiv.return_value = [item]
    mock_news.return_value = []

    result = run_scheduled_discovery(queries=["test"], max_per_source=1, compile_after_ingest=False)

    assert result["skipped_seen"] >= 1
    mock_ingest.assert_not_called()


@patch("kb.discovery.discover_arxiv")
@patch("kb.discovery.discover_articles_google_news")
@patch("kb.discovery.ingest_url")
def test_run_scheduled_ingests_new_urls(mock_ingest, mock_news, mock_arxiv, tmp_path, monkeypatch):
    from pathlib import Path
    from kb.discovery import DiscoveryItem, run_scheduled_discovery

    item = DiscoveryItem(title="New", url="https://new.com/paper", source="arxiv", published_at="2026-01-01")
    mock_arxiv.return_value = [item]
    mock_news.return_value = []
    mock_ingest.return_value = Path("/tmp/raw/new.md")

    result = run_scheduled_discovery(queries=["test"], max_per_source=1, compile_after_ingest=False)

    assert result["ingested"] >= 1
    mock_ingest.assert_called_once()


@patch("kb.discovery.discover_arxiv")
@patch("kb.discovery.discover_articles_google_news")
def test_run_scheduled_records_failures(mock_news, mock_arxiv, tmp_path, monkeypatch):
    from kb.discovery import run_scheduled_discovery

    mock_arxiv.__name__ = "discover_arxiv"
    mock_news.__name__ = "discover_articles_google_news"
    mock_arxiv.side_effect = RuntimeError("network error")
    mock_news.side_effect = RuntimeError("network error")

    result = run_scheduled_discovery(queries=["test"], max_per_source=1, compile_after_ingest=False)

    assert len(result["failures"]) >= 2


@patch("kb.discovery.discover_arxiv")
@patch("kb.discovery.discover_articles_google_news")
@patch("kb.discovery.ingest_url")
def test_run_scheduled_returns_summary(mock_ingest, mock_news, mock_arxiv, tmp_path, monkeypatch):
    from pathlib import Path
    from kb.discovery import DiscoveryItem, run_scheduled_discovery

    item = DiscoveryItem(title="Test", url="https://test.com/x", source="arxiv", published_at="2026-01-01")
    mock_arxiv.return_value = [item]
    mock_news.return_value = []
    mock_ingest.return_value = Path("/tmp/raw/test.md")

    result = run_scheduled_discovery(queries=["test"], max_per_source=1, compile_after_ingest=False)

    assert "queries" in result
    assert "discovered" in result
    assert "ingested" in result
    assert "compiled" in result
    assert "skipped_seen" in result
    assert "failures" in result
    assert "created_files" in result
